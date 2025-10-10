# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2025 The Linux Foundation
#
# Subprocess and git helper utilities with logging and error handling.
# - Strict typing
# - Centralized logging
# - Secret masking in logs
# - Optional retries with exponential backoff for transient errors

from __future__ import annotations

import logging
import os
import shlex
import subprocess
import time
from collections.abc import Callable
from collections.abc import Iterable
from collections.abc import Mapping
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from .utils import log_exception_conditionally


__all__ = [
    "CommandError",
    "CommandResult",
    "GitError",
    "enumerate_reviewer_emails",
    "git",
    "git_cherry_pick",
    "git_commit_amend",
    "git_commit_new",
    "git_config",
    "git_config_get",
    "git_config_get_all",
    "git_last_commit_trailers",
    "git_show",
    "mask_text",
    "run_cmd",
    "run_cmd_with_retries",
]

# Error message constants to comply with TRY003
_MSG_COMMIT_NO_MESSAGE = "Either message or message_file must be provided"


_LOGGER_NAME = "github2gerrit.git"
log = logging.getLogger(_LOGGER_NAME)
if not log.handlers:
    # Provide a minimal default if the app has not configured logging.
    level_name = os.getenv("G2G_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    fmt = (
        "%(asctime)s %(levelname)-8s %(name)s %(filename)s:%(lineno)d | "
        "%(message)s"
    )
    logging.basicConfig(level=level, format=fmt)


class CommandError(RuntimeError):
    """Raised when a subprocess command fails."""

    def __init__(
        self,
        message: str,
        *,
        cmd: Sequence[str] | None = None,
        returncode: int | None = None,
        stdout: str | None = None,
        stderr: str | None = None,
    ) -> None:
        super().__init__(message)
        self.cmd = list(cmd) if cmd is not None else None
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


class GitError(CommandError):
    """Raised when a git command fails."""


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    stdout: str
    stderr: str


def _to_str_opt(val: str | bytes | None) -> str | None:
    """Convert an optional bytes/str value to str safely."""
    if val is None:
        return None
    if isinstance(val, bytes):
        return val.decode("utf-8", errors="replace")
    return val


def mask_text(text: str, masks: Iterable[str]) -> str:
    """Replace each mask value in text with asterisks."""
    masked = text
    for token in masks:
        if not token:
            continue
        masked = masked.replace(token, "***")
    return masked


def _format_cmd_for_log(
    cmd: Sequence[str],
    masks: Iterable[str],
) -> str:
    quoted = [shlex.quote(x) for x in cmd]
    line = " ".join(quoted)
    return mask_text(line, masks)


def _merge_env(
    base: Mapping[str, str] | None,
    extra: Mapping[str, str] | None,
) -> dict[str, str]:
    if base is None:
        out: dict[str, str] = dict(os.environ)
    else:
        out = dict(base)
    if extra:
        out.update(extra)
    return out


def _is_transient_git_error(stderr: str) -> bool:
    """Heuristics for transient git/network errors suitable for retry."""
    s = stderr.lower()
    patterns = [
        "unable to access",
        "could not resolve host",
        "failed to connect",
        "connection timed out",
        "connection reset by peer",
        "early eof",
        "the remote end hung up unexpectedly",
        "http/2 stream",
        "transport endpoint is not connected",
        "network is unreachable",
        "temporary failure",
        "ssl: couldn't",
        "ssl: certificate",
    ]
    return any(pat in s for pat in patterns)


def _backoff_delay(attempt: int, base: float = 0.5, cap: float = 5.0) -> float:
    # Exponential backoff: base * 2^(attempt-1), capped
    delay: float = float(base * (2 ** max(0, attempt - 1)))
    return float(min(delay, cap))


def run_cmd(
    cmd: Sequence[str],
    *,
    cwd: Path | None = None,
    env: Mapping[str, str] | None = None,
    timeout: float | None = None,
    check: bool = True,
    masks: Iterable[str] | None = None,
    stdin_data: str | None = None,
) -> CommandResult:
    """Run a subprocess command and capture output.

    - Logs command line with secrets masked.
    - Returns stdout/stderr and return code.
    - Raises CommandError on failure when check=True.
    """
    masks = list(masks or [])
    env = env or non_interactive_env()
    env_full = _merge_env(None, env)

    log.debug("Executing: %s", _format_cmd_for_log(cmd, masks))
    try:
        proc = subprocess.run(  # noqa: S603
            list(cmd),
            cwd=str(cwd) if cwd else None,
            env=env_full,
            input=stdin_data,
            text=True,
            shell=False,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        msg = f"Command timed out: {cmd!r}"
        log_exception_conditionally(log, msg)
        # TimeoutExpired carries 'output' and 'stderr' attributes,
        # which may be bytes depending on invocation context.
        out = getattr(exc, "output", None)
        err = getattr(exc, "stderr", None)
        raise CommandError(
            msg,
            cmd=cmd,
            returncode=None,
            stdout=_to_str_opt(out),
            stderr=_to_str_opt(err),
        ) from exc
    except OSError as exc:
        msg = f"Failed to execute command: {cmd!r} ({exc})"
        log_exception_conditionally(log, msg)
        raise CommandError(msg, cmd=cmd) from exc

    result = CommandResult(
        returncode=proc.returncode,
        stdout=proc.stdout or "",
        stderr=proc.stderr or "",
    )

    if result.returncode != 0:
        log.debug(
            "Command failed (rc=%s): %s\nstdout: %s\nstderr: %s",
            result.returncode,
            _format_cmd_for_log(cmd, masks),
            mask_text(result.stdout, masks),
            mask_text(result.stderr, masks),
        )
        if check:
            raise CommandError(  # noqa: TRY003
                "Command failed",
                cmd=cmd,
                returncode=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
            )
    else:
        if result.stdout:
            log.debug("stdout: %s", mask_text(result.stdout, masks))
        if result.stderr:
            # Filter out git init default branch hints to keep logs clean
            stderr_lines = result.stderr.splitlines()
            filtered_lines = []
            skip_hint = False
            for line in stderr_lines:
                if (
                    "hint: Using '" in line
                    and "as the name for the initial branch" in line
                ):
                    skip_hint = True
                elif (skip_hint and line.startswith("hint:")) or (
                    skip_hint and not line.strip()
                ):
                    continue
                else:
                    skip_hint = False
                    filtered_lines.append(line)

            if filtered_lines:
                filtered_stderr = "\n".join(filtered_lines)
                log.debug("stderr: %s", mask_text(filtered_stderr, masks))

    return result


def non_interactive_env(include_git_ssh_command: bool = True) -> dict[str, str]:
    """Return a non-interactive SSH/Git environment to bypass local
    agents/keychains.

    Args:
        include_git_ssh_command: Whether to include a default GIT_SSH_COMMAND.
                                Set to False when the caller will provide their
                                own.

    Returns:
        Dictionary of environment variables for non-interactive operations.
    """
    # Import here to avoid circular imports
    from .ssh_common import build_non_interactive_ssh_env

    env = build_non_interactive_ssh_env()

    if include_git_ssh_command:
        from .ssh_common import build_git_ssh_command

        env["GIT_SSH_COMMAND"] = build_git_ssh_command()

    return env


def run_cmd_with_retries(
    cmd: Sequence[str],
    *,
    cwd: Path | None = None,
    env: Mapping[str, str] | None = None,
    timeout: float | None = None,
    check: bool = True,
    masks: Iterable[str] | None = None,
    stdin_data: str | None = None,
    retries: int = 2,
    retry_on: Callable[[CommandResult], bool] | None = None,
) -> CommandResult:
    """Run a command with basic exponential backoff retries on transient errors.

    The default retry predicate considers common transient git errors.
    """
    masks = list(masks or [])
    env = env or non_interactive_env()

    def _default_retry_on(res: CommandResult) -> bool:
        return res.returncode != 0 and _is_transient_git_error(res.stderr)

    predicate = retry_on or _default_retry_on
    attempt = 0

    while True:
        attempt += 1
        try:
            res = run_cmd(
                cmd,
                cwd=cwd,
                env=env,
                timeout=timeout,
                check=False,
                masks=masks,
                stdin_data=stdin_data,
            )
        except CommandError:  # noqa: TRY203
            # Non-exec or timeout errors are not retried here.
            raise

        if res.returncode == 0 or attempt > (retries + 1):
            if check and res.returncode != 0:
                raise CommandError(  # noqa: TRY003
                    "Command failed after retries",
                    cmd=cmd,
                    returncode=res.returncode,
                    stdout=res.stdout,
                    stderr=res.stderr,
                )
            return res

        if predicate(res):
            delay = _backoff_delay(attempt)
            log.warning(
                "Retrying (attempt %d) after transient error; delay %.1fs. "
                "cmd=%s",
                attempt,
                delay,
                " ".join(cmd) if isinstance(cmd, list) else str(cmd),
            )
            time.sleep(delay)
            continue

        # Non-transient failure; stop.
        if check:
            raise CommandError(  # noqa: TRY003
                "Command failed (non-retryable)",
                cmd=cmd,
                returncode=res.returncode,
                stdout=res.stdout,
                stderr=res.stderr,
            )
        return res


# ----------------------------
# Git helper functions
# ----------------------------


def git(
    args: Sequence[str],
    *,
    cwd: Path | None = None,
    env: Mapping[str, str] | None = None,
    timeout: float | None = None,
    check: bool = True,
    masks: Iterable[str] | None = None,
    retries: int = 2,
) -> CommandResult:
    """Run a git subcommand with retries on transient errors."""
    cmd = ["git", *args]
    return run_cmd_with_retries(
        cmd,
        cwd=cwd,
        env=env,
        timeout=timeout,
        check=check,
        masks=list(masks or []),
        retries=retries,
    )


def git_quiet(
    args: Sequence[str],
    *,
    cwd: Path | None = None,
    env: Mapping[str, str] | None = None,
    timeout: float | None = None,
) -> CommandResult:
    """Run a git subcommand quietly (no failure logging for expected)."""
    cmd = ["git", *args]
    try:
        return run_cmd(
            cmd,
            cwd=cwd,
            env=env or non_interactive_env(),
            timeout=timeout,
            check=False,
        )
    except Exception:
        return CommandResult(returncode=1, stdout="", stderr="")


def git_config(
    key: str,
    value: str,
    *,
    global_: bool = False,
    cwd: Path | None = None,
) -> None:
    args = ["config"]
    if global_:
        args.append("--global")
    args.extend([key, value])
    try:
        git(args, cwd=cwd)
    except CommandError as exc:
        # If we got an error about multiple values, try with --replace-all
        if exc.returncode == 5 and "multiple values" in (exc.stderr or ""):
            args = ["config"]
            if global_:
                args.append("--global")
            args.append("--replace-all")
            args.extend([key, value])
            try:
                git(args, cwd=cwd)
            except CommandError:
                # If replace-all also fails, raise the original error
                raise GitError(  # noqa: TRY003
                    f"git config failed for {key}",
                    cmd=exc.cmd,
                    returncode=exc.returncode,
                    stdout=exc.stdout,
                    stderr=exc.stderr,
                ) from exc
        else:
            raise GitError(  # noqa: TRY003
                f"git config failed for {key}",
                cmd=exc.cmd,
                returncode=exc.returncode,
                stdout=exc.stdout,
                stderr=exc.stderr,
            ) from exc


def git_cherry_pick(
    commit: str,
    *,
    cwd: Path | None = None,
    strategy_opts: Sequence[str] | None = None,
) -> None:
    args: list[str] = ["cherry-pick"]
    if strategy_opts:
        args.extend(strategy_opts)
    args.append(commit)
    try:
        git(args, cwd=cwd)
    except CommandError as exc:
        raise GitError(  # noqa: TRY003
            f"git cherry-pick {commit} failed",
            cmd=exc.cmd,
            returncode=exc.returncode,
            stdout=exc.stdout,
            stderr=exc.stderr,
        ) from exc


def git_commit_amend(
    *,
    cwd: Path | None = None,
    no_edit: bool = True,
    signoff: bool = True,
    author: str | None = None,
    message: str | None = None,
    message_file: Path | None = None,
) -> None:
    """Amend the current commit.

    If message is provided, it takes precedence over message_file.
    """
    # Write message to a temp file to avoid shell-escaping issues
    tmp_path: Path | None = None
    if message is not None:
        import tempfile as _tempfile

        with _tempfile.NamedTemporaryFile(
            "w", delete=False, encoding="utf-8"
        ) as _tf:
            _tf.write(message)
            _tf.flush()
            tmp_path = Path(_tf.name)
        message_file = tmp_path
        message = None

    # Determine whether to add -s; only suppress if message already has a
    # sign-off for current committer
    effective_signoff = bool(signoff)
    try:
        import os
        import re

        # Resolve committer email (prefer repo-local; fallback to global/env)
        committer_email = os.getenv("GIT_COMMITTER_EMAIL", "").strip()
        if not committer_email:
            try:
                res = run_cmd(["git", "config", "--get", "user.email"], cwd=cwd)
                committer_email = (res.stdout or "").strip()
            except Exception:
                committer_email = ""
        if not committer_email:
            try:
                ge = git_config_get("user.email", global_=True)
                if ge:
                    committer_email = ge.strip()
            except Exception:
                committer_email = ""

        def _has_committer_signoff(text: str) -> bool:
            for ln in text.splitlines():
                if ln.lower().startswith("signed-off-by:"):
                    m = re.search(r"<([^>]+)>", ln)
                    if (
                        m
                        and committer_email
                        and m.group(1).strip().lower()
                        == committer_email.lower()
                    ):
                        return True
            return False

        msg_text: str | None = None
        if message_file is not None:
            try:
                msg_text = Path(message_file).read_text(encoding="utf-8")
            except Exception:
                msg_text = None

        if msg_text is not None:
            if committer_email and _has_committer_signoff(msg_text):
                effective_signoff = False
        else:
            # No explicit message provided; check current commit body
            try:
                body = git_show("HEAD", cwd=cwd, fmt="%B")
                if committer_email and _has_committer_signoff(body):
                    effective_signoff = False
            except GitError:
                pass
    except Exception:
        # Best effort only; default to requested signoff
        effective_signoff = bool(signoff)

    args: list[str] = ["commit", "--amend"]
    if no_edit and not message and not message_file:
        args.append("--no-edit")
    if effective_signoff:
        args.append("-s")
    if author:
        args.extend(["--author", author])
    if message_file:
        args.extend(["-F", str(message_file)])

    try:
        git(args, cwd=cwd)
    except CommandError as exc:
        raise GitError(  # noqa: TRY003
            "git commit --amend failed",
            cmd=exc.cmd,
            returncode=exc.returncode,
            stdout=exc.stdout,
            stderr=exc.stderr,
        ) from exc
    finally:
        if tmp_path is not None:
            from contextlib import suppress

            with suppress(Exception):
                tmp_path.unlink(missing_ok=True)


def git_commit_new(
    *,
    cwd: Path | None = None,
    message: str | None = None,
    message_file: Path | None = None,
    signoff: bool = True,
    author: str | None = None,
    allow_empty: bool = False,
) -> None:
    """Create a new commit using message or message_file."""
    if not message and not message_file:
        raise ValueError(_MSG_COMMIT_NO_MESSAGE)

    # Write message to a temp file to avoid shell-escaping issues
    tmp_path: Path | None = None
    if message is not None:
        import tempfile as _tempfile

        with _tempfile.NamedTemporaryFile(
            "w", delete=False, encoding="utf-8"
        ) as _tf:
            _tf.write(message)
            _tf.flush()
            tmp_path = Path(_tf.name)
        message_file = tmp_path
        message = None

    # Determine whether to add -s; only suppress if message already has a
    # sign-off for current committer
    effective_signoff = bool(signoff)
    try:
        import os
        import re

        # Resolve committer email (prefer repo-local; fallback to global/env)
        committer_email = os.getenv("GIT_COMMITTER_EMAIL", "").strip()
        if not committer_email:
            try:
                res = run_cmd(["git", "config", "--get", "user.email"], cwd=cwd)
                committer_email = (res.stdout or "").strip()
            except Exception:
                committer_email = ""
        if not committer_email:
            try:
                ge = git_config_get("user.email", global_=True)
                if ge:
                    committer_email = ge.strip()
            except Exception:
                committer_email = ""

        def _has_committer_signoff(text: str) -> bool:
            for ln in text.splitlines():
                if ln.lower().startswith("signed-off-by:"):
                    m = re.search(r"<([^>]+)>", ln)
                    if (
                        m
                        and committer_email
                        and m.group(1).strip().lower()
                        == committer_email.lower()
                    ):
                        return True
            return False

        if message_file is not None:
            try:
                msg_text = Path(message_file).read_text(encoding="utf-8")
            except Exception:
                msg_text = None
            if msg_text and _has_committer_signoff(msg_text):
                effective_signoff = False
    except Exception:
        effective_signoff = bool(signoff)

    args: list[str] = ["commit"]
    if effective_signoff:
        args.append("-s")
    if author:
        args.extend(["--author", author])
    if allow_empty:
        args.append("--allow-empty")

    if message_file:
        args.extend(["-F", str(message_file)])

    try:
        git(args, cwd=cwd)
    except CommandError as exc:
        raise GitError(  # noqa: TRY003
            "git commit failed",
            cmd=exc.cmd,
            returncode=exc.returncode,
            stdout=exc.stdout,
            stderr=exc.stderr,
        ) from exc
    finally:
        if tmp_path is not None:
            from contextlib import suppress

            with suppress(Exception):
                tmp_path.unlink(missing_ok=True)


def git_show(
    rev: str,
    *,
    cwd: Path | None = None,
    fmt: str | None = None,
) -> str:
    """Show a commit content or its formatted output."""
    args: list[str] = ["show", rev]
    if fmt:
        args.extend([f"--format={fmt}", "-s"])
    try:
        res = git(args, cwd=cwd)
    except CommandError as exc:
        raise GitError(  # noqa: TRY003
            f"git show {rev} failed",
            cmd=exc.cmd,
            returncode=exc.returncode,
            stdout=exc.stdout,
            stderr=exc.stderr,
        ) from exc
    else:
        return res.stdout


def _parse_trailers(text: str) -> dict[str, list[str]]:
    """Parse trailers from a commit message footer only.

    Git trailers are key-value pairs that appear at the end of commit messages,
    separated from the body by a blank line. This function only parses trailers
    from the actual footer section to avoid false positives from the message
    body.
    """
    trailers: dict[str, list[str]] = {}
    lines = text.splitlines()

    # Find the start of the trailer block by working backwards
    # Trailers must be at the end, separated by a blank line from the body
    trailer_start = len(lines)
    in_trailer_block = True

    for i in range(len(lines) - 1, -1, -1):
        line = lines[i].strip()

        if not line and in_trailer_block:
            # Found blank line, trailers end here
            trailer_start = i + 1
            break
        elif not line:
            # Blank line in middle, not in trailer block anymore
            in_trailer_block = False
            trailer_start = len(lines)
        elif in_trailer_block and ":" in line:
            # Potential trailer line
            key, val = line.split(":", 1)
            k = key.strip()
            v = val.strip()
            if k and v and not k.startswith(" ") and not k.startswith("\t"):
                # Valid trailer format
                continue
            else:
                # Invalid trailer format, stop looking
                in_trailer_block = False
                trailer_start = len(lines)
        elif in_trailer_block:
            # Non-trailer line in what we thought was trailer block
            in_trailer_block = False
            trailer_start = len(lines)

    # Parse only the trailer section
    for i in range(trailer_start, len(lines)):
        line = lines[i].strip()
        if not line or ":" not in line:
            continue
        key, val = line.split(":", 1)
        k = key.strip()
        v = val.strip()
        if not k or not v or k.startswith((" ", "\t")):
            continue
        trailers.setdefault(k, []).append(v)

    return trailers


def git_last_commit_trailers(
    keys: Sequence[str] | None = None,
    *,
    cwd: Path | None = None,
) -> dict[str, list[str]]:
    """Return trailers for the last commit, optionally filtered by keys."""
    try:
        # Use pretty format to print only body for robust parsing.
        body = git_show("HEAD", cwd=cwd, fmt="%B")
        # Trailers are usually at the end, but we parse all lines.
        trailers = _parse_trailers(body)
        if keys is None:
            return trailers
        subset: dict[str, list[str]] = {}
        for k in keys:
            if k in trailers:
                subset[k] = trailers[k]
    except GitError:
        # If HEAD is unavailable (fresh repo), return empty.
        return {}
    else:
        return subset


def git_config_get(
    key: str,
    *,
    global_: bool = False,
) -> str | None:
    """Get a git config value (single) from local or global config."""
    args = ["config"]
    if global_:
        args.append("--global")
    args.extend(["--get", key])
    try:
        res = git_quiet(args, cwd=None)
        if res.returncode == 0:
            value = res.stdout.strip()
            return value if value else None
        else:
            return None
    except Exception:
        return None


def git_config_get_all(
    key: str,
    *,
    global_: bool = False,
) -> list[str]:
    """Get all git config values for a key (may return multiple lines)."""
    args = ["config"]
    if global_:
        args.append("--global")
    args.extend(["--get-all", key])
    try:
        res = git_quiet(args, cwd=None)
        if res.returncode == 0:
            values = [
                ln.strip() for ln in res.stdout.splitlines() if ln.strip()
            ]
            return values
        else:
            return []
    except Exception:
        return []


def enumerate_reviewer_emails() -> list[str]:
    """Return reviewer emails from local/global git config.

    Sources checked in order:
    - git config --get-all github2gerrit.reviewersEmail
    - git config --get-all g2g.reviewersEmail
    - git config --get-all reviewers.email
      (all may be comma-separated; values are split on commas)
    - git config user.email (local then global) as a fallback

    Returns:
      A de-duplicated list of emails (order preserved).
    """
    emails: list[str] = []

    def _add_email(e: str) -> None:
        v = e.strip()
        if v and v not in emails:
            emails.append(v)

    # Candidate keys that may hold reviewer emails
    candidate_keys = [
        "github2gerrit.reviewersEmail",
        "g2g.reviewersEmail",
        "reviewers.email",
    ]

    for key in candidate_keys:
        vals = git_config_get_all(key) + git_config_get_all(key, global_=True)
        for v in vals:
            # Support comma-separated lists within individual values
            for part in v.split(","):
                _add_email(part)

    # Fallback to user.email (local then global)
    user_email = git_config_get("user.email")
    if user_email:
        _add_email(user_email)
    ue_g = git_config_get("user.email", global_=True)
    if ue_g:
        _add_email(ue_g)

    return emails
