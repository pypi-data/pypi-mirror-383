"""Environment helpers for Rebel Forge."""
from __future__ import annotations

from pathlib import Path
import os
from typing import Iterable

_ENV_BASENAME = ".env.local"
_ENV_FILE_ENV = "REBEL_FORGE_ENV_FILE"
_ENV_KEY_PREFIXES: tuple[str, ...] = ("NEBIUS_",)
_ENV_KEY_EXACT = {"PYPI_TOKEN"}
_PACKAGE_ROOT = Path(__file__).resolve().parent
_ENV_LOADED = False


def load_local_env(*, include: Iterable[str] | None = None) -> None:
    """Populate os.environ with safe keys from `.env.local` if present."""

    global _ENV_LOADED
    if _ENV_LOADED:
        return

    override = os.environ.get(_ENV_FILE_ENV)
    candidates: list[Path]
    if override:
        candidates = [Path(override).expanduser()]
    else:
        candidates = [
            Path.cwd() / _ENV_BASENAME,
            _PACKAGE_ROOT.parent / _ENV_BASENAME,
            _PACKAGE_ROOT.parent.parent / _ENV_BASENAME,
            Path.home() / _ENV_BASENAME,
        ]

    allowed_keys = set(include or ())
    for candidate in candidates:
        env_file = candidate.expanduser()
        if not env_file.is_file():
            continue
        try:
            _apply_env_file(env_file, allowed_keys)
        except Exception:
            # Loading environment values should never block execution.
            pass
        finally:
            _ENV_LOADED = True
            return
    _ENV_LOADED = True


def _apply_env_file(env_file: Path, allowed: set[str]) -> None:
    raw = env_file.read_text(encoding="utf-8")
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        if not _key_allowed(key, allowed):
            continue
        normalized = _normalize_value(value)
        os.environ.setdefault(key, normalized)


def _key_allowed(key: str, allowed: set[str]) -> bool:
    if key in allowed:
        return True
    if any(key.startswith(prefix) for prefix in _ENV_KEY_PREFIXES):
        return True
    return key in _ENV_KEY_EXACT


def _normalize_value(value: str) -> str:
    cleaned = value.strip()
    if (
        len(cleaned) >= 2
        and cleaned[0] == cleaned[-1]
        and cleaned[0] in {'"', "'"}
    ):
        cleaned = cleaned[1:-1]
    return cleaned

