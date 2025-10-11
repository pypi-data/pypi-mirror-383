"""Command-line entry point for rebel-forge."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import textwrap
import time
import webbrowser
from pathlib import Path
from typing import Any, Iterable, List, Optional
from urllib.parse import urlparse

from .env import load_local_env
from .onboarding import (
    ANSI_BLUE,
    ANSI_BOLD,
    ANSI_RESET,
    CTA_LINE,
    INFO_PARAGRAPH,
    HandshakeSession,
    ensure_onboarding,
    is_portal_alive,
    render_cta_line,
    render_logo,
    render_welcome_panel,
    resolve_login_url,
    start_handshake_session,
    update_cli_session,
    wait_for_handshake,
)

_PACKAGE_ROOT = Path(__file__).resolve().parent
_IGNORE_PATTERNS = shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo")
_DEFAULT_EXPORT_DIR = Path.home() / "rebel-forge"
_REMOTE_FLAG = "--remote"
_PORTAL_ENV = "REBEL_FORGE_PORTAL_DIR"
_STATE_DIR = Path.home() / ".rebel-forge"
_PORTAL_PID_FILE = _STATE_DIR / "portal-dev.pid"
_PORTAL_LOG_FILE = _STATE_DIR / "portal-dev.log"
_PORTAL_START_TIMEOUT = 60
_DEFAULT_PATH = "/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
_LOCAL_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0"}


_SUCCESS_MESSAGE = "🎉 Login successful. Press Enter to continue."


def _export_source(destination: str, *, force: bool = False, quiet: bool = False, skip_if_exists: bool = False) -> Path:
    dest_path = Path(destination).expanduser().resolve()
    if dest_path.exists():
        if skip_if_exists and not force:
            return dest_path
        if not force:
            raise SystemExit(
                f"Destination '{dest_path}' already exists. Pass --force to overwrite or use a different path."
            )
        shutil.rmtree(dest_path)
    shutil.copytree(_PACKAGE_ROOT, dest_path, ignore=_IGNORE_PATTERNS)
    if not quiet:
        print(f"Exported rebel-forge sources to {dest_path}")
    return dest_path


def _handle_source(argv: list[str]) -> None:
    parser = argparse.ArgumentParser(
        prog="rebel-forge source",
        description="Export the installed rebel-forge sources to a directory",
    )
    parser.add_argument(
        "--dest",
        default="rebel-forge-src",
        help="Destination directory for the exported sources (default: rebel-forge-src)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite the destination directory if it already exists.",
    )
    args = parser.parse_args(argv)
    _export_source(args.dest, force=args.force)


def _ensure_default_export() -> None:
    try:
        _export_source(str(_DEFAULT_EXPORT_DIR), skip_if_exists=True, quiet=True)
    except Exception:
        # Failing to export automatically should not block CLI usage.
        pass


def _activate_workspace(target: Path) -> None:
    if not target.exists():
        return
    try:
        os.chdir(target)
    except (NotADirectoryError, PermissionError):
        return


def _consume_remote_flag(argv: List[str]) -> tuple[list[str], bool]:
    cleaned: list[str] = []
    remote_requested = False
    for arg in argv:
        if arg == _REMOTE_FLAG:
            remote_requested = True
            continue
        if arg.startswith(f"{_REMOTE_FLAG}="):
            _, value = arg.split("=", 1)
            remote_requested = _coerce_bool(value)
            continue
        cleaned.append(arg)
    return cleaned, remote_requested


def _coerce_bool(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _maybe_enable_remote(argv: list[str]) -> list[str]:
    argv, flag_requested = _consume_remote_flag(argv)
    env_requested = _coerce_bool(os.environ.get("FORGE_REMOTE_AUTO"))
    if flag_requested or env_requested:
        from .remote import ensure_remote

        ensure_remote()
    return argv


def _load_cli_environment() -> None:
    try:
        load_local_env()
    except Exception as exc:
        print(f"Warning: unable to load environment values: {exc}")



def main() -> None:
    _load_cli_environment()
    _ensure_default_export()
    argv = sys.argv[1:]
    if argv and argv[0] == "source":
        _handle_source(argv[1:])
        return

    _activate_workspace(_DEFAULT_EXPORT_DIR)
    login_base = resolve_login_url()
    _ensure_portal_ready(login_base, _DEFAULT_EXPORT_DIR)
    session_payload = ensure_onboarding(workspace=_DEFAULT_EXPORT_DIR)

    if not argv:
        _handle_zero_arg(login_base, session_payload)
        return

    argv = _maybe_enable_remote(argv)
    sys.argv = [sys.argv[0], *argv]

    from .rebel_forge import main as forge_main

    forge_main()


def _handle_zero_arg(login_base: str, session_payload: Optional[dict[str, Any]]) -> None:
    if session_payload:
        _render_linked_banner(login_base, session_payload)
        _show_workspace_overview(_DEFAULT_EXPORT_DIR)
        return

    session = start_handshake_session(login_base=login_base)
    portal_ready = is_portal_alive(session.portal_url)
    _render_zero_arg_banner(session, portal_ready)
    _prompt_for_portal_launch(session)
    _wait_for_interactive_handshake(session)


def _render_linked_banner(login_base: str, session_payload: dict[str, Any]) -> None:
    print(render_welcome_panel())
    print(render_logo(force_color=True))
    print()
    account = _resolve_session_account(session_payload)
    verified = _format_timestamp(session_payload.get("last_verified"))
    workspace = _DEFAULT_EXPORT_DIR
    details = textwrap.dedent(
        f"""{INFO_PARAGRAPH}

Status    ▸ Linked to Rebel
Account   ▸ {account}
Verified  ▸ {verified}
Workspace ▸ {workspace}
Portal    ▸ {login_base}
"""
    )
    print(details)
    print("You are already signed in. Explore the workspace below or run `rebel-forge --help` for commands.\n")


def _resolve_session_account(session_payload: dict[str, Any]) -> str:
    profile = session_payload.get("profile")
    if isinstance(profile, dict):
        for key in ("display_name", "fullName", "full_name"):
            value = profile.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        first = profile.get("first_name") or profile.get("firstName")
        last = profile.get("last_name") or profile.get("lastName")
        names = [name.strip() for name in (first, last) if isinstance(name, str) and name.strip()]
        if names:
            return " ".join(names)
    for key in ("display_name", "first_name", "last_name"):
        value = session_payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    user_id = session_payload.get("userId") or session_payload.get("user_id")
    if isinstance(user_id, str) and user_id.strip():
        return user_id.strip()
    return "Rebel user"


def _format_timestamp(raw: Any) -> str:
    if isinstance(raw, (int, float)) and raw > 0:
        try:
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(raw))
        except (OverflowError, OSError, ValueError):
            pass
    return "unknown"


def _show_workspace_overview(workspace: Path, *, limit: int = 25) -> None:
    print(f"Workspace contents for {workspace}:")
    if not workspace.exists():
        print("  (workspace not initialized yet; run `rebel-forge source --force` to export the latest files)")
        return
    entries = sorted(
        workspace.iterdir(),
        key=lambda path: (not path.is_dir(), path.name.lower()),
    )
    if not entries:
        print("  (workspace is empty)")
        return
    to_show = entries[:limit]
    for entry in to_show:
        suffix = "/" if entry.is_dir() else ""
        print(f"  - {entry.name}{suffix}")
    remaining = len(entries) - len(to_show)
    if remaining > 0:
        print(f"  - ... {remaining} more entries (run `ls {workspace}` to view all)")


def _render_zero_arg_banner(session: HandshakeSession, portal_ready: bool) -> None:
    print(render_welcome_panel())
    print(render_logo(force_color=True))
    print()
    status = "Portal ready" if portal_ready else "Launch the Rebel portal"
    details = textwrap.dedent(
        f"""{INFO_PARAGRAPH}

Status   ▸ {status}
Token    ▸ {session.token}
Portal   ▸ {session.portal_url}
"""
    )
    print(details)
    print(render_cta_line())


def _prompt_for_portal_launch(session: HandshakeSession) -> None:
    while True:
        choice = input('› ').strip().lower()
        if choice in {'', 'open', 'login', 'sign', 'enter', '1'}:
            print('Opening the Rebel portal in your browser…')
            opened = webbrowser.open(session.portal_url, new=2, autoraise=True)
            if not opened:
                print('Unable to launch your default browser automatically. Open the URL shown above manually.')
            return
        if choice in {'skip', 's'}:
            print('Skipping portal launch. Run `rebel-forge` again when you are ready to sign in.')
            return
        print(render_cta_line())


def _celebrate_success(display_name: str | None = None) -> None:
    greeting = "Welcome to Rebel Forge!"
    if display_name:
        greeting = f"Welcome, {display_name} to Rebel Forge!"
    if not os.environ.get('NO_COLOR'):
        greeting = f"{ANSI_BLUE}{ANSI_BOLD}{greeting}{ANSI_RESET}"
    print(greeting)
    message = _SUCCESS_MESSAGE
    if not os.environ.get('NO_COLOR'):
        message = f"{ANSI_BLUE}{ANSI_BOLD}{message}{ANSI_RESET}"
    print(message)
    try:
        input()
    except (KeyboardInterrupt, EOFError):
        pass


def _wait_for_interactive_handshake(session: HandshakeSession) -> None:
    print('Waiting for Rebel to confirm the link… (Ctrl+C to cancel)')
    record = wait_for_handshake(session)
    if record:
        update_cli_session(session.login_base, record)
        session.handshake_path.unlink(missing_ok=True)
        display_name = record.display_name or record.first_name
        _celebrate_success(display_name)
    else:
        print('Timed out waiting for Rebel unlock. Rerun `rebel-forge` after signing in.')


def _ensure_portal_ready(login_base: str, workspace: Path) -> None:

    _cleanup_stale_portal()
    if not _login_is_local(login_base):
        return
    if is_portal_alive(login_base):
        return
    pid = _read_portal_pid()
    if pid and _pid_alive(pid):
        return
    portal_dir = _discover_portal_dir(workspace)
    if portal_dir is None:
        _print_portal_hint(login_base)
        return
    process = _spawn_portal_process(portal_dir, _extract_port(login_base))
    if process is None:
        _print_portal_hint(login_base)
        return
    deadline = time.time() + _PORTAL_START_TIMEOUT
    while time.time() < deadline:
        if is_portal_alive(login_base):
            return
        if process.poll() is not None:
            print(f"Portal dev server exited early (status {process.returncode}). See {_PORTAL_LOG_FILE} for details.")
            return
        time.sleep(1.0)
    print(f"Portal dev server did not become ready within {_PORTAL_START_TIMEOUT} seconds. See {_PORTAL_LOG_FILE} for logs.")


def _login_is_local(login_base: str) -> bool:
    parsed = urlparse(login_base)
    host = (parsed.hostname or "").lower()
    if host in _LOCAL_HOSTS:
        return True
    return host.endswith(".local")


def _extract_port(login_base: str) -> int:
    parsed = urlparse(login_base)
    if parsed.port:
        return parsed.port
    if parsed.scheme == "https":
        return 443
    return 3000


def _discover_portal_dir(workspace: Path) -> Optional[Path]:
    visited: set[Path] = set()
    for candidate in _candidate_portal_dirs(workspace):
        try:
            resolved = candidate.expanduser().resolve()
        except OSError:
            continue
        if resolved in visited:
            continue
        visited.add(resolved)
        if _looks_like_portal(resolved):
            return resolved
    return None


def _candidate_portal_dirs(workspace: Path) -> Iterable[Path]:
    env_value = os.environ.get(_PORTAL_ENV)
    if env_value:
        yield Path(env_value)
    seeds = [
        workspace,
        workspace.parent,
        Path.cwd(),
        _PACKAGE_ROOT.parent,
        _PACKAGE_ROOT.parent.parent,
        _PACKAGE_ROOT.parent.parent.parent,
        Path.home() / "rebel-frontend",
    ]
    suffixes = ("", "rebel-frontend", "frontend", "portal")
    for seed in seeds:
        if not seed:
            continue
        for suffix in suffixes:
            candidate = seed if suffix == "" else seed / suffix
            yield candidate


def _looks_like_portal(path: Path) -> bool:
    if "node_modules" in path.parts:
        return False
    package_json = path / "package.json"
    if not package_json.is_file():
        return False
    try:
        data = json.loads(package_json.read_text())
    except Exception:
        return False
    scripts = data.get("scripts")
    if isinstance(scripts, dict):
        dev_cmd = scripts.get("dev")
        if isinstance(dev_cmd, str) and "next" in dev_cmd.lower():
            return True
    if (path / "next.config.ts").is_file() or (path / "next.config.mjs").is_file() or (path / "next.config.js").is_file():
        return True
    return False


def _spawn_portal_process(portal_dir: Path, port: int) -> Optional[subprocess.Popen]:
    env = _portal_env(port)
    npm_path = shutil.which("npm", path=env.get("PATH"))
    if not npm_path:
        print("Unable to locate `npm`. Install Node.js or expose it via PATH to auto-start the portal.")
        return None
    command = [npm_path, "run", "dev", "--", "--port", str(port), "--hostname", "0.0.0.0"]
    creationflags = 0
    preexec_fn = None
    if os.name == "posix":
        preexec_fn = os.setsid
    elif os.name == "nt":
        creationflags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) | getattr(subprocess, "DETACHED_PROCESS", 0)
    _STATE_DIR.mkdir(parents=True, exist_ok=True)
    log_handle = open(_PORTAL_LOG_FILE, "ab", buffering=0)
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_handle.write(f"\n--- [{timestamp}] Starting rebel-forge portal in {portal_dir}\n".encode())
    process = subprocess.Popen(
        command,
        cwd=portal_dir,
        stdout=log_handle,
        stderr=subprocess.STDOUT,
        env=env,
        preexec_fn=preexec_fn,
        creationflags=creationflags,
        close_fds=True,
    )
    _PORTAL_PID_FILE.write_text(str(process.pid))
    log_handle.flush()
    log_handle.close()
    return process


def _portal_env(port: Optional[int] = None) -> dict[str, str]:
    env = os.environ.copy()
    current_path = env.get("PATH", "")
    env["PATH"] = _DEFAULT_PATH if not current_path else f"{_DEFAULT_PATH}:{current_path}"
    env.setdefault("BROWSER", "none")
    env.setdefault("NEXT_TELEMETRY_DISABLED", "1")
    if port is not None:
        env["PORT"] = str(port)
    else:
        env.setdefault("PORT", "3000")
    return env


def _read_portal_pid() -> Optional[int]:
    if not _PORTAL_PID_FILE.is_file():
        return None
    try:
        return int(_PORTAL_PID_FILE.read_text().strip())
    except Exception:
        return None


def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def _cleanup_stale_portal() -> None:
    pid = _read_portal_pid()
    if pid is None:
        return
    if _pid_alive(pid):
        return
    try:
        _PORTAL_PID_FILE.unlink(missing_ok=True)
    except OSError:
        pass


def _print_portal_hint(login_base: str) -> None:
    base = login_base.rstrip("/")
    message = f"""Unable to auto-start the Rebel Forge portal.
Set `{_PORTAL_ENV}` to your Next.js frontend directory or run `npm run dev` manually, then visit {base}.
"""
    print(textwrap.dedent(message))
    _cleanup_stale_portal()


if __name__ == "__main__":
    main()
