"""Interactive onboarding banner for the rebel-forge CLI."""
from __future__ import annotations

import json
import os
import textwrap
import time
import uuid
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional
from urllib import request
from urllib.error import HTTPError, URLError

ANSI_BLUE = "\u001b[38;5;39m"
ANSI_RED = "\u001b[38;5;196m"
ANSI_ACCENT = ANSI_BLUE
ANSI_BOLD = "\u001b[1m"
ANSI_RESET = "\u001b[0m"

ASCII_LOGO = r"""
██████╗ ███████╗██████╗ ███████╗██╗         ███████╗ ██████╗ ██████╗  ██████╗ ███████╗
██╔══██╗██╔════╝██╔══██╗██╔════╝██║         ██╔════╝██╔═══██╗██╔══██╗██╔════╝ ██╔════╝
██████╔╝█████╗  ██████╔╝█████╗  ██║  █████╗ █████╗  ██║   ██║██████╔╝██║  ███╗█████╗  
██╔══██╗██╔══╝  ██╔══██╗██╔══╝  ██║  ╚════╝ ██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔══╝  
██║  ██║███████╗██║  ██║███████╗███████╗    ██║     ╚██████╔╝██║  ██║╚██████╔╝███████╗
╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝    ╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝
"""

WELCOME_PANEL = r"""
╭──────────────────────────────────────────────────────────────────────────────╮
│ * Welcome to the Rebel Forge research preview!                              │
╰──────────────────────────────────────────────────────────────────────────────╯
"""

INFO_PARAGRAPH = (
    "Rebel Forge is billed based on Nebius usage through your Rebel account.\n"
    "Pricing may evolve as we move towards general availability."
)

CTA_LINE = "Press Enter to sign in to your Rebel account…"


@dataclass(init=False)
class HandshakeSession:
    """Lightweight record describing a CLI unlock session."""

    login_base: str
    token: str
    handshake_path: Path
    portal_url: str

    def __init__(
        self,
        *,
        login_base: str | None = None,
        token: str,
        handshake_path: Path,
        portal_url: str,
        **legacy_kwargs,
    ) -> None:
        base = login_base or legacy_kwargs.pop("base", None)
        if legacy_kwargs:
            unexpected = ", ".join(sorted(legacy_kwargs))
            raise TypeError(f"Unexpected arguments for HandshakeSession: {unexpected}")
        if base is None:
            raise TypeError("login_base is required")
        self.login_base = base
        self.token = token
        self.handshake_path = handshake_path
        self.portal_url = portal_url


@dataclass(frozen=True)
class HandshakeRecord:
    """Details returned from the portal handshake."""

    token: str
    user_id: str
    unlocked_at: float
    display_name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    session_template: str | None = None
    session_id: str | None = None


_MARKER_DIR = Path.home() / ".rebel-forge"
_MARKER_PATH = _MARKER_DIR / "onboarding.done"
_SESSION_PATH = _MARKER_DIR / "session.json"
_STATUS_ENDPOINT = "/api/cli-auth/status"
_HANDSHAKE_PREFIX = "cli-handshake-"
_DEFAULT_LOGIN_URL = "http://localhost:3000"
_SKIP_ENV = "REBEL_FORGE_SKIP_ONBOARDING"
_AUTO_UNLOCK_ENV = "REBEL_FORGE_AUTO_UNLOCK"
_AUTO_HANDSHAKE_USER_ENV = "REBEL_FORGE_HANDSHAKE_USER"
_AUTO_HANDSHAKE_NAME_ENV = "REBEL_FORGE_HANDSHAKE_NAME"
_TRUE_VALUES = {"1", "true", "yes", "on"}
_CLEAR_CMDS = ("clear", "cls")
_POLL_ATTEMPTS = 240
_POLL_DELAY_SECONDS = 1.0
_SESSION_VERIFY_TIMEOUT = 5.0
_DEFAULT_HANDSHAKE_USER = "cli-user"


def start_handshake_session(*, login_base: str | None = None) -> HandshakeSession:
    base = (login_base or resolve_login_url()).rstrip("/")
    token = uuid.uuid4().hex
    handshake_path = _MARKER_DIR / f"{_HANDSHAKE_PREFIX}{token}"
    portal_url = f"{base}/cli?token={token}"
    handshake_path.unlink(missing_ok=True)
    return HandshakeSession(login_base=base, token=token, handshake_path=handshake_path, portal_url=portal_url)


def wait_for_handshake(session: HandshakeSession) -> Optional[HandshakeRecord]:
    return _await_handshake(session.portal_url, session.handshake_path, session.token)


def ensure_onboarding(*, workspace: Path) -> Optional[dict[str, Any]]:
    """Guide the user through Rebel account login and return the active session payload when linked."""

    if _should_skip():
        return None

    login_base = resolve_login_url().rstrip("/")
    existing_session = _load_session()

    if existing_session and _session_active(existing_session, login_base):
        _ensure_marker(login_base)
        return existing_session

    if existing_session:
        print("Rebel authentication expired. Please sign in again to unlock the CLI.\n")
        _clear_session_state()

    session = start_handshake_session(login_base=login_base)

    if _auto_unlock_enabled():
        _render_banner(session.portal_url, workspace)
        _launch_login(session.portal_url)
        record = wait_for_handshake(session)
        session.handshake_path.unlink(missing_ok=True)
        if record:
            _record_session(session.login_base, record)
            return _load_session()
        return None

    while True:
        _render_banner(session.portal_url, workspace)
        choice = input("Press Enter to open the Rebel portal, 's' to skip, or 'quit' to exit: ").strip().lower()
        if choice in {"", "login", "sign", "sign in", "signin", "log in", "1"}:
            _launch_login(session.portal_url)
            record = wait_for_handshake(session)
            if record:
                _record_session(session.login_base, record)
                session.handshake_path.unlink(missing_ok=True)
                return _load_session()
            print("Still waiting for confirmation from the browser. Select Link CLI again after signing in.")
            continue
        if choice in {"skip", "s"}:
            if _confirm_skip():
                session.handshake_path.unlink(missing_ok=True)
                return None
            continue
        if choice in {"quit", "q", "exit"}:
            raise SystemExit("Aborted before completing Rebel Forge onboarding.")
        print("Unrecognized option. Press Enter to Log In, type 's' to skip, or 'quit' to exit.")


def update_cli_session(login_base: str, handshake: HandshakeRecord) -> None:
    """Refresh the persisted CLI session after a new portal handshake."""
    _record_session(login_base.rstrip("/"), handshake, quiet=True)


def _should_skip() -> bool:
    return _coerce_bool(os.environ.get(_SKIP_ENV))


def _auto_unlock_enabled() -> bool:
    return _coerce_bool(os.environ.get(_AUTO_UNLOCK_ENV))


def resolve_login_url() -> str:
    for key in ("REBEL_FORGE_LOGIN_URL", "REBEL_FORGE_FRONTEND_URL", "NEXT_PUBLIC_SITE_URL"):
        raw = os.environ.get(key)
        if raw:
            return raw.rstrip("/")
    return _DEFAULT_LOGIN_URL


def _render_banner(portal_url: str, workspace: Path) -> None:
    _clear_screen()
    print(render_welcome_panel())
    print(render_logo())
    print()
    body = textwrap.dedent(
        f"""{INFO_PARAGRAPH}

Workspace ▸ {workspace}
Portal    ▸ {portal_url}
"""
    )
    print(body)
    print(render_cta_line())
    print()


def _clear_screen() -> None:
    if _coerce_bool(os.environ.get("REBEL_FORGE_DISABLE_CLEAR")):
        return
    for cmd in _CLEAR_CMDS:
        if os.system(cmd + " > /dev/null 2>&1") == 0:
            return


def _launch_login(portal_url: str) -> None:
    print(f"Opening {portal_url} in your browser…")
    webbrowser.open(portal_url, new=2, autoraise=True)


def _load_session() -> Optional[dict[str, Any]]:
    try:
        raw = _SESSION_PATH.read_text()
    except FileNotFoundError:
        return None
    except OSError:
        return None
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict):
        return None
    return payload


def _write_session_payload(payload: dict[str, Any]) -> None:
    _MARKER_DIR.mkdir(parents=True, exist_ok=True)
    _SESSION_PATH.write_text(json.dumps(payload, indent=2))


def _ensure_marker(login_base: str) -> None:
    if _MARKER_PATH.exists():
        return
    _MARKER_DIR.mkdir(parents=True, exist_ok=True)
    payload = {"login_url": login_base, "completed_at": time.time()}
    _MARKER_PATH.write_text(json.dumps(payload, indent=2))


def _clear_session_state() -> None:
    for path in (_SESSION_PATH, _MARKER_PATH):
        try:
            path.unlink()
        except FileNotFoundError:
            continue


def _record_session(login_base: str, handshake: HandshakeRecord, *, quiet: bool = False) -> None:
    session_payload = {
        "login_url": login_base,
        "userId": handshake.user_id,
        "token": handshake.token,
        "linked_at": handshake.unlocked_at,
        "last_verified": time.time(),
    }
    if handshake.session_template:
        session_payload["session_template"] = handshake.session_template
    if handshake.session_id:
        session_payload["session_id"] = handshake.session_id
    profile: dict[str, str] = {}
    if handshake.display_name:
        session_payload["display_name"] = handshake.display_name
        profile["display_name"] = handshake.display_name
    if handshake.first_name:
        session_payload["first_name"] = handshake.first_name
        profile["first_name"] = handshake.first_name
    if handshake.last_name:
        session_payload["last_name"] = handshake.last_name
        profile["last_name"] = handshake.last_name
    if profile:
        session_payload["profile"] = profile
    _write_session_payload(session_payload)
    _ensure_marker(login_base)
    if not quiet:
        greeting = "Onboarding complete. Welcome to Rebel Forge!"
        if handshake.display_name:
            greeting = f"Onboarding complete. Welcome, {handshake.display_name}!"
        print(f"{greeting}\n")


def _session_active(session_payload: dict[str, Any], login_base: str) -> bool:
    user_id = session_payload.get("userId") or session_payload.get("user_id")
    if not isinstance(user_id, str) or not user_id.strip():
        return False
    base = login_base.rstrip("/")
    url = f"{base}{_STATUS_ENDPOINT}?userId={user_id}"
    request_obj = request.Request(url, headers={"Accept": "application/json"})
    try:
        with request.urlopen(request_obj, timeout=_SESSION_VERIFY_TIMEOUT) as response:
            raw = response.read()
            data = json.loads(raw.decode("utf-8") if raw else "{}")
    except HTTPError as error:
        if error.code in {401, 403, 404}:
            return False
        print(f"[rebel-forge] Warning: CLI status endpoint returned {error.code}; assuming session still active.")
        return True
    except (URLError, TimeoutError, OSError) as error:
        print(f"[rebel-forge] Warning: Unable to reach CLI status endpoint ({error}); assuming session still active.")
        return True
    except Exception as error:  # pragma: no cover - defensive
        print(f"[rebel-forge] Warning: CLI status probe failed ({error}); assuming session still active.")
        return True
    active = bool(data.get("active"))
    if active:
        session_payload["login_url"] = base
        session_payload["last_verified"] = time.time()
        _write_session_payload(session_payload)
    return active


def _await_handshake(portal_url: str, handshake_path: Path, token: str) -> Optional[HandshakeRecord]:
    print("Waiting for the CLI unlock signal from the browser…")
    if _auto_unlock_enabled():
        _write_handshake(handshake_path, token)
        return _load_handshake_payload(handshake_path, token)
    for attempt in range(1, _POLL_ATTEMPTS + 1):
        if handshake_path.exists():
            return _load_handshake_payload(handshake_path, token)
        if attempt == 1 or attempt % 20 == 0:
            if not is_portal_alive(portal_url):
                print("The portal is not responding yet. Ensure `npm run dev` is active.")
            else:
                print("Portal responding. Complete the Rebel sign-in and wait for the automatic unlock.")
        time.sleep(_POLL_DELAY_SECONDS)
    return None


def _load_handshake_payload(handshake_path: Path, token: str) -> Optional[HandshakeRecord]:
    try:
        payload = json.loads(handshake_path.read_text())
    except (OSError, json.JSONDecodeError):
        return None
    user_raw = payload.get("userId")
    if not isinstance(user_raw, str) or not user_raw.strip():
        return None
    unlocked_raw = payload.get("unlockedAt", time.time())
    try:
        unlocked_at = float(unlocked_raw)
    except (TypeError, ValueError):
        unlocked_at = time.time()
    def _clean(value: object) -> str | None:
        if isinstance(value, str):
            candidate = value.strip()
            if candidate:
                return candidate
        return None

    raw_profile = payload.get("profile")
    profile = raw_profile if isinstance(raw_profile, dict) else {}
    first_name = _clean(
        profile.get("firstName")
        or profile.get("first_name")
        or payload.get("firstName")
        or payload.get("first_name")
    )
    last_name = _clean(
        profile.get("lastName")
        or profile.get("last_name")
        or payload.get("lastName")
        or payload.get("last_name")
    )
    display_name = _clean(
        profile.get("fullName")
        or profile.get("full_name")
        or profile.get("displayName")
        or payload.get("fullName")
        or payload.get("full_name")
        or payload.get("displayName")
    )
    if not display_name:
        combined = " ".join(part for part in (first_name, last_name) if part)
        display_name = combined.strip() if combined else None

    session_template = _clean(payload.get("sessionTemplate") or payload.get("session_template"))
    session_id = _clean(payload.get("sessionId") or payload.get("session_id"))

    return HandshakeRecord(
        token=token,
        user_id=user_raw.strip(),
        unlocked_at=unlocked_at,
        display_name=display_name,
        first_name=first_name,
        last_name=last_name,
        session_template=session_template,
        session_id=session_id,
    )


def is_portal_alive(portal_url: str) -> bool:
    base = portal_url.split("?", 1)[0]
    try:
        with request.urlopen(base, timeout=1.5) as response:
            return 200 <= response.status < 500
    except Exception:
        return False


def _write_handshake(handshake_path: Path, token: str) -> None:
    handshake_path.parent.mkdir(parents=True, exist_ok=True)
    profile: dict[str, str] = {}
    auto_name = os.environ.get(_AUTO_HANDSHAKE_NAME_ENV)
    if isinstance(auto_name, str) and auto_name.strip():
        profile["fullName"] = auto_name.strip()
    payload: dict[str, object] = {
        "token": token,
        "userId": os.environ.get(_AUTO_HANDSHAKE_USER_ENV, _DEFAULT_HANDSHAKE_USER),
        "unlockedAt": time.time(),
    }
    if profile:
        payload["profile"] = profile
    handshake_path.write_text(json.dumps(payload, indent=2))


def _confirm_skip() -> bool:
    answer = input("Skip onboarding for this session? [y/N]: ").strip().lower()
    return answer.startswith("y")


def _coerce_bool(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() in _TRUE_VALUES


def _colorize_block(block: str, color: str, *, bold: bool = False) -> str:
    if os.environ.get("NO_COLOR"):
        return block
    prefix = color + (ANSI_BOLD if bold else "")
    suffix = ANSI_RESET
    return "\n".join(f"{prefix}{line}{suffix}" for line in block.splitlines())


def render_welcome_panel() -> str:
    return _colorize_block(WELCOME_PANEL.strip("\n"), ANSI_ACCENT, bold=True)


def render_cta_line() -> str:
    line = CTA_LINE
    if os.environ.get("NO_COLOR"):
        return line
    return f"{ANSI_BLUE}{ANSI_BOLD}{line}{ANSI_RESET}"


def render_logo(*, force_color: bool = False) -> str:
    art = ASCII_LOGO.strip("\n")
    if force_color or not os.environ.get("NO_COLOR"):
        return _colorize_block(art, ANSI_RED, bold=True)
    return art


__all__ = [
    "ensure_onboarding",
    "resolve_login_url",
    "is_portal_alive",
    "render_logo",
    "render_welcome_panel",
    "render_cta_line",
    "INFO_PARAGRAPH",
    "CTA_LINE",
    "ASCII_LOGO",
    "ANSI_ACCENT",
    "ANSI_BLUE",
    "ANSI_BOLD",
    "ANSI_RED",
    "ANSI_RESET",
    "HandshakeSession",
    "HandshakeRecord",
    "start_handshake_session",
    "wait_for_handshake",
    "update_cli_session",
]
