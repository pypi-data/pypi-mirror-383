"""
Core implementation for pylogsentinel.

The program is designed to be executed periodically (e.g. via cron every
minute). It maintains lightweight state files tracking how far into each
monitored log file it has already processed (byte offset and line number).
Only newly appended content is scanned on each invocation, bounded by a
configurable max_block_size to avoid unbounded processing time.

Key features:
- INI configuration (see pylogsentinel.conf.example).
- Dynamic or static log file discovery (command or explicit paths).
- Regex rule matching with per-rule actions, default fallback action.
- Lock file to prevent concurrent execution using same state directory.
- Safe state persistence per log inode (coping with rotation/truncation).
- Environment variable expansion for action shell commands.
- Optional dry-run mode for testing (no commands executed).

Only Python standard library modules are used.
"""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Iterator, Sequence
from types import TracebackType

import configparser
import os
import re
import subprocess
import sys
import time


DEFAULT_CONFIG_PATH = "pylogsentinel.conf"
LOCK_FILENAME = "LOCK"
DEFAULT_MAX_BLOCK_SIZE = 10 * 1024 * 1024  # 10 MiB
CONTEXT_RADIUS = 2  # lines before and after a match to include in CONTEXT


class ConfigError(Exception):
    """Raised for configuration problems."""


@dataclass
class Action:
    action_id: str
    cmd: str


@dataclass
class Rule:
    rule_id: str
    pattern: str
    description: str
    action_id: str  # may reference "default"
    compiled: re.Pattern[str]


@dataclass
class MatchEvent:
    rule: Rule
    file_path: str
    line_number: int
    context: str
    matched_text: str


def parse_size(value: str) -> int:
    """
    Parse a human-friendly size string into bytes.
    Supports plain integers or integers suffixed by K, M, G (binary multiples).
    """
    v = value.strip()
    if not v:
        raise ValueError("Empty size value")
    multiplier = 1
    if v[-1] in "KkMmGg":
        unit = v[-1].upper()
        num = v[:-1]
        try:
            base = int(num)
        except ValueError as e:
            raise ValueError(f"Invalid numeric portion in size: {value!r}") from e
        if unit == "K":
            multiplier = 1024
        elif unit == "M":
            multiplier = 1024**2
        elif unit == "G":
            multiplier = 1024**3
        return base * multiplier
    try:
        return int(v)
    except ValueError as e:
        raise ValueError(f"Invalid size value: {value!r}") from e


_FLAG_MAP = {
    "i": re.IGNORECASE,  # only supported flag
}


def _compile_pattern(raw: str) -> tuple[str, re.Pattern[str]]:
    """
    Compile a pattern of the required form: /pattern/flags

    Allowed flag: i (IGNORECASE) only. Any other flag is rejected.

    Raises:
        ConfigError if the pattern does not conform.
    """
    text = raw.strip()
    if not (len(text) >= 2 and text.startswith("/") and text.rfind("/") > 0):
        raise ConfigError(f"Pattern must be in /pattern/flags form (got {raw!r})")
    last = text.rfind("/")
    body = text[1:last]
    flags_part = text[(last + 1) :]
    if body == "":
        raise ConfigError("Empty pattern body is not allowed")
    flags = 0
    for ch in flags_part:
        if ch not in _FLAG_MAP:
            raise ConfigError(f"Unsupported regex flag {ch!r} in pattern {raw!r}")
        flags |= _FLAG_MAP[ch]
    try:
        compiled = re.compile(body, flags)
    except re.error as e:
        raise ConfigError(f"Invalid regex {body!r}: {e}") from e
    normalized = f"/{body}/{flags_part}"
    return normalized, compiled


def load_config(
    path: str,
) -> tuple[list[str], dict[str, Rule], dict[str, Action], int, str]:
    """
    Load and validate configuration.

    Returns:
        (log_paths (may contain directories),
         rules mapping,
         actions mapping,
         max_block_size,
         state_dir)
    """
    parser = configparser.ConfigParser(interpolation=None)
    with open(path, "r", encoding="utf-8") as fh:
        parser.read_file(fh)

    if not parser.has_section("system"):
        raise ConfigError("Missing [system] section")
    state_dir = parser.get("system", "state_dir", fallback=None)
    max_block_size_str = parser.get("system", "max_block_size", fallback="10M")
    if not state_dir:
        raise ConfigError("Missing required option: system.state_dir")
    state_dir = os.path.expanduser(os.path.expandvars(state_dir))
    try:
        max_block_size = parse_size(max_block_size_str)
    except ValueError as e:
        raise ConfigError(f"Invalid max_block_size: {e}") from e
    if max_block_size <= 0:
        raise ConfigError("max_block_size must be positive")

    # Logs section
    if not parser.has_section("logs"):
        raise ConfigError("Missing [logs] section")
    log_cmd = parser.get("logs", "cmd", fallback=None)
    log_paths_raw = parser.get("logs", "paths", fallback=None)
    if log_cmd and log_paths_raw:
        raise ConfigError("Specify only one of [logs].cmd or [logs].paths")
    if not log_cmd and not log_paths_raw:
        raise ConfigError("Must specify one of [logs].cmd or [logs].paths")

    log_paths: list[str]
    if log_paths_raw:
        log_paths = [
            os.path.expanduser(os.path.expandvars(p))
            for p in log_paths_raw.split()
            if p
        ]
    else:
        # Run discovery command (log_cmd validated above)
        assert log_cmd is not None and log_cmd.strip(), (
            "internal: log_cmd unexpectedly None/empty"
        )
        try:
            proc = subprocess.run(
                log_cmd,  # type: ignore[arg-type]  # narrowed by assert for type checkers
                shell=True,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        except OSError as e:
            raise ConfigError(f"Failed to run logs cmd: {e}") from e
        if proc.returncode != 0:
            raise ConfigError(
                f"Log discovery command failed ({proc.returncode}): {log_cmd}\n{proc.stderr}"
            )
        log_paths = [
            os.path.expanduser(os.path.expandvars(line.strip()))
            for line in proc.stdout.splitlines()
            if line.strip()
        ]

    # Parse actions
    actions: dict[str, Action] = {}
    for section in parser.sections():
        if section.startswith("action."):
            action_id = section[len("action.") :]
            cmd = parser.get(section, "cmd", fallback=None)
            if not cmd:
                raise ConfigError(f"Missing cmd in [{section}]")
            actions[action_id] = Action(action_id=action_id, cmd=cmd)

    if "default" not in actions:
        raise ConfigError("Missing [action.default] section (mandatory default action)")

    # Parse rules
    rules: dict[str, Rule] = {}
    for section in parser.sections():
        if section.startswith("rule."):
            rule_id = section[len("rule.") :]
            description = parser.get(
                section, "description", fallback="(no description)"
            )
            pattern_raw = parser.get(section, "pattern", fallback=None)
            if not pattern_raw:
                raise ConfigError(f"Missing pattern in [{section}]")
            action_id = parser.get(section, "action", fallback="default")
            if action_id not in actions:
                raise ConfigError(
                    f"Rule {rule_id!r} references unknown action {action_id!r}"
                )
            normalized, compiled = _compile_pattern(pattern_raw)
            rules[rule_id] = Rule(
                rule_id=rule_id,
                pattern=normalized,
                description=description,
                action_id=action_id,
                compiled=compiled,
            )

    if not rules:
        raise ConfigError("No rules defined (need at least one [rule.*] section)")

    return log_paths, rules, actions, max_block_size, state_dir


class LockFile:
    """
    Simple lock file using atomic O_CREAT | O_EXCL semantics.

    Ensures only one running process per state directory.
    """

    state_dir: str
    path: str
    _fd: int | None

    def __init__(self, state_dir: str, filename: str = LOCK_FILENAME) -> None:
        self.state_dir = state_dir
        self.path = os.path.join(state_dir, filename)
        self._fd: int | None = None

    def acquire(self) -> None:
        try:
            self._fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            os.write(
                self._fd,
                f"pid={os.getpid()} time={int(time.time())}\n".encode("utf-8"),
            )
        except FileExistsError:
            raise SystemExit(
                f"ERROR: Lock file exists: {self.path}\n"
                "If no other process is running, delete it manually."
            )
        except OSError as e:
            raise SystemExit(f"ERROR: Unable to create lock file {self.path}: {e}")

    def release(self) -> None:
        if self._fd is not None:
            try:
                os.close(self._fd)
            except OSError:
                pass
            self._fd = None
        try:
            os.unlink(self.path)
        except FileNotFoundError:
            pass
        except OSError as e:
            print(
                f"WARNING: Failed to remove lock file {self.path}: {e}", file=sys.stderr
            )

    def __enter__(self) -> "LockFile":
        self.acquire()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.release()


class StateManager:
    """
    Manage per-inode state files.

    Format per file:
        <byte_offset> <line_number>

    If file is truncated (size < stored offset) we reset to 0,0.
    """

    state_dir: str

    def __init__(self, state_dir: str) -> None:
        self.state_dir = state_dir

    def _path_for_inode(self, inode: int) -> str:
        return os.path.join(self.state_dir, str(inode))

    def load(self, inode: int) -> tuple[int, int]:
        path = self._path_for_inode(inode)
        try:
            with open(path, "r", encoding="utf-8") as fh:
                content = fh.read().strip()
        except FileNotFoundError:
            return 0, 0
        except OSError as e:
            print(f"WARNING: Failed reading state file {path}: {e}", file=sys.stderr)
            return 0, 0
        if not content:
            return 0, 0
        parts = content.split()
        if len(parts) != 2:
            print(f"WARNING: Malformed state file {path}: {content!r}", file=sys.stderr)
            return 0, 0
        try:
            byte_offset = int(parts[0])
            line_number = int(parts[1])
        except ValueError:
            print(
                f"WARNING: Non-integer state file {path}: {content!r}", file=sys.stderr
            )
            return 0, 0
        return byte_offset, line_number

    def save(self, inode: int, byte_offset: int, line_number: int) -> None:
        path = self._path_for_inode(inode)
        tmp_path = f"{path}.tmp"
        data = f"{byte_offset} {line_number}\n"
        try:
            with open(tmp_path, "w", encoding="utf-8") as fh:
                fh.write(data)
            os.replace(tmp_path, path)
        except OSError as e:
            print(
                f"WARNING: Failed writing state file {path}: {e}",
                file=sys.stderr,
            )
            try:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
            except OSError:
                pass


def discover_files(paths: list[str]) -> Iterator[str]:
    """
    Expand a list of paths which may include directories.
    For directories: recursively traverse and yield ONLY files that the system
    'file' command reports as some form of text (case-insensitive substring
    'text' in its output). User-specified explicit file paths are yielded
    regardless of type (user responsibility).

    Fallback behavior:
      - If invoking 'file' fails (missing command or error exit), the file is
        treated as text (permissive fallback).
      - Only regular files are yielded.

    NOTE: This introduces a subprocess per file encountered under directories;
    if performance becomes a concern, consider constraining directory breadth
    or switching to explicit file paths.
    """

    def _is_text(path: str) -> bool:
        try:
            proc = subprocess.run(
                ["file", "-b", path],  # type: ignore[arg-type]  # pyright: acceptable sequence of str
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )
            if proc.returncode != 0:
                return True  # permissive fallback
            desc = proc.stdout.lower()
            return "text" in desc
        except Exception:
            return True  # permissive fallback on unexpected errors

    for p in paths:
        if not p:
            continue
        if os.path.isfile(p):
            # Explicit file path: yield directly
            yield p
        elif os.path.isdir(p):
            for root, _, files in os.walk(p):
                for name in files:
                    full = os.path.join(root, name)
                    if os.path.isfile(full) and _is_text(full):
                        yield full
        else:
            continue


def read_new_lines(
    file_path: str,
    start_offset: int,
    start_line_number: int,
    max_block_size: int,
) -> tuple[list[str], int, int]:
    """
    Read up to max_block_size newly appended bytes from file.

    Returns:
        (new_lines (decoded with replacement errors),
         new_byte_offset,
         new_last_line_number)

    new_last_line_number is the absolute line number of the final line read.
    """
    lines: list[str] = []
    try:
        with open(file_path, "rb") as fh:
            fh.seek(0, os.SEEK_END)
            file_size = fh.tell()
            if file_size < start_offset:
                # Truncated
                start_offset = 0
                start_line_number = 0
            fh.seek(start_offset)
            bytes_read = 0
            while bytes_read < max_block_size:
                line_bytes = fh.readline()
                if not line_bytes:
                    break
                bytes_read += len(line_bytes)
                if bytes_read > max_block_size:
                    # Do not include this partial line; rewind to before line.
                    bytes_read -= len(line_bytes)
                    break
                try:
                    decoded = line_bytes.decode("utf-8", errors="replace")
                except Exception:
                    decoded = line_bytes.decode("latin1", errors="replace")
                lines.append(decoded)
            new_offset = start_offset + bytes_read
    except FileNotFoundError:
        return [], start_offset, start_line_number
    except PermissionError:
        print(f"WARNING: Permission denied: {file_path}", file=sys.stderr)
        return [], start_offset, start_line_number
    except OSError as e:
        print(f"WARNING: Failed reading {file_path}: {e}", file=sys.stderr)
        return [], start_offset, start_line_number

    if not lines:
        return [], start_offset, start_line_number

    new_last_line_number = start_line_number + len(lines)
    return lines, new_offset, new_last_line_number


def generate_matches(
    file_path: str,
    lines: list[str],
    initial_line_number: int,
    rules: dict[str, Rule],
    context_radius: int = CONTEXT_RADIUS,
) -> Iterator[MatchEvent]:
    """
    Iterate over lines and yield MatchEvent objects for each rule match.
    """
    total_lines = len(lines)
    for idx, line in enumerate(lines):
        absolute_line_number = initial_line_number + idx + 1
        for rule in rules.values():
            m = rule.compiled.search(line)
            if not m:
                continue
            # Build context
            start_ctx = max(0, idx - context_radius)
            end_ctx = min(total_lines, idx + context_radius + 1)
            context = "".join(lines[start_ctx:end_ctx])
            yield MatchEvent(
                rule=rule,
                file_path=file_path,
                line_number=absolute_line_number,
                context=context,
                matched_text=m.group(0),
            )


def execute_action(
    action: Action,
    event: MatchEvent,
    dry_run: bool = False,
    env_overrides: dict[str, str] | None = None,
) -> int:
    """
    Execute an action shell command with appropriate environment.

    Returns the process exit code (0 on dry-run).
    """
    env = os.environ.copy()
    env.update(
        {
            "RULE_ID": event.rule.rule_id,
            "RULE_PATTERN": event.rule.pattern,
            "RULE_DESCRIPTION": event.rule.description,
            "FILE": event.file_path,
            "LINE": str(event.line_number),
            "CONTEXT": event.context,
        }
    )
    if env_overrides:
        env.update(env_overrides)

    if dry_run:
        print(
            f"[dry-run] Would execute action {action.action_id!r} for rule "
            f"{event.rule.rule_id!r} on {event.file_path}:{event.line_number}\n"
            f"Command: {action.cmd}\n",
            file=sys.stderr,
        )
        return 0

    try:
        proc = subprocess.run(  # type: ignore
            action.cmd,
            shell=True,
            env=env,
            text=True,
        )
        if proc.returncode != 0:
            print(
                f"WARNING: Action {action.action_id} exited with {proc.returncode}",
                file=sys.stderr,
            )
        return proc.returncode
    except OSError as e:
        print(
            f"ERROR: Failed executing action {action.action_id}: {e}",
            file=sys.stderr,
        )
        return 1


class Sentinel:
    """
    Encapsulates a configured sentinel run.
    """

    log_paths: list[str]
    rules: dict[str, Rule]
    actions: dict[str, Action]
    max_block_size: int
    state_dir: str
    dry_run: bool
    state_manager: "StateManager"

    def __init__(
        self,
        log_paths: list[str],
        rules: dict[str, Rule],
        actions: dict[str, Action],
        max_block_size: int,
        state_dir: str,
        dry_run: bool = False,
    ) -> None:
        self.log_paths = log_paths
        self.rules = rules
        self.actions = actions
        self.max_block_size = max_block_size
        self.state_dir = state_dir
        self.dry_run = dry_run
        self.state_manager = StateManager(state_dir)

    def ensure_state_dir(self) -> None:
        try:
            os.makedirs(self.state_dir, exist_ok=True)
        except OSError as e:
            # Explicit error output before failing; re-raise original exception
            print(
                f"ERROR: Failed to create state_dir '{self.state_dir}': {e}",
                file=sys.stderr,
            )
            raise

    def process_file(self, file_path: str) -> None:
        try:
            st = os.stat(file_path)
        except FileNotFoundError:
            return
        except PermissionError:
            print(f"WARNING: Permission denied: {file_path}", file=sys.stderr)
            return
        except OSError as e:
            print(f"WARNING: Cannot stat {file_path}: {e}", file=sys.stderr)
            return

        inode = st.st_ino
        prev_offset, prev_line_no = self.state_manager.load(inode)

        lines, new_offset, new_last_line_no = read_new_lines(
            file_path, prev_offset, prev_line_no, self.max_block_size
        )
        if not lines:
            # No new content OR failed to read
            return

        for event in generate_matches(
            file_path, lines, prev_line_no, self.rules, CONTEXT_RADIUS
        ):
            action = self.actions.get(event.rule.action_id) or self.actions["default"]
            execute_action(action, event, dry_run=self.dry_run)

        self.state_manager.save(inode, new_offset, new_last_line_no)

    def run(self) -> int:
        """
        Run a single monitoring pass.

        Returns process exit code (0 success).
        """
        self.ensure_state_dir()

        with LockFile(self.state_dir):
            files = list(discover_files(self.log_paths))
            if not files:
                print("INFO: No files to process", file=sys.stderr)
                return 0
            for path in files:
                if self.dry_run:
                    print(f"[dry-run] Scanning {path}", file=sys.stderr)
                self.process_file(path)
        return 0


def parse_args(argv: Sequence[str]) -> tuple[str, bool]:
    """
    Very small argument parser (avoid argparse for minimal footprint).

    Supported:
        -c/--config PATH
        --dry-run
        -h/--help
    """
    config_path = DEFAULT_CONFIG_PATH
    dry_run = False
    it = iter(enumerate(argv))
    for _, arg in it:
        if arg in ("-h", "--help"):
            print(
                "Usage: pylogsentinel [-c CONFIG] [--dry-run]\n"
                "Environment variables may be referenced in action commands.\n",
                file=sys.stderr,
            )
            raise SystemExit(0)
        elif arg in ("-c", "--config"):
            try:
                _, value = next(it)
            except StopIteration:
                raise SystemExit("ERROR: -c/--config requires a value")
            config_path = value
        elif arg == "--dry-run":
            dry_run = True
        else:
            # Unrecognized argument
            raise SystemExit(f"ERROR: Unrecognized argument: {arg}")
    return config_path, dry_run


def main(argv: Sequence[str] | None = None) -> int:
    """
    CLI entry point.
    """
    if argv is None:
        argv = sys.argv[1:]
    try:
        config_path, dry_run = parse_args(list(argv))
        # If the provided (or default) config path does not exist, attempt standard locations.
        if not os.path.isfile(config_path):
            for cand in (
                os.path.expanduser("~/.pylogsentinel.conf"),
                os.path.expanduser("~/.config/pylogsentinel.conf"),
                "/etc/pylogsentinel.conf",
                "/usr/local/etc/pylogsentinel.conf",
                config_path,  # fallback original (may still not exist)
            ):
                if os.path.isfile(cand):
                    config_path = cand
                    break
        (
            log_paths,
            rules,
            actions,
            max_block_size,
            state_dir,
        ) = load_config(config_path)
        sentinel = Sentinel(
            log_paths=log_paths,
            rules=rules,
            actions=actions,
            max_block_size=max_block_size,
            state_dir=state_dir,
            dry_run=dry_run,
        )
        if dry_run:
            print(f"[dry-run] Using config: {config_path}", file=sys.stderr)
            print(f"[dry-run] Log path entries: {len(log_paths)}", file=sys.stderr)
            print(
                f"[dry-run] Rules: {', '.join(sorted(rules.keys()))}", file=sys.stderr
            )
            print(
                f"[dry-run] Actions: {', '.join(sorted(actions.keys()))}",
                file=sys.stderr,
            )
        return sentinel.run()
    except ConfigError as e:
        print(f"CONFIG ERROR: {e}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("Interrupted", file=sys.stderr)
        return 130
    except SystemExit as e:
        return int(e.code) if isinstance(e.code, int) else 1
    except Exception as e:
        print(f"UNHANDLED ERROR: {e.__class__.__name__}: {e}", file=sys.stderr)
        raise


if __name__ == "__main__":
    sys.exit(main())
