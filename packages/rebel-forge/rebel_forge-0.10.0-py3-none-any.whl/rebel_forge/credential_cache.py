"""Secure caching helpers for Nebius provisioning bundles.

The cache prefers the system keyring (when available) so credentials are stored
outside the project tree. We only fall back to an on-disk file when the keyring
backend cannot be reached; the file is written with 0600 permissions to limit
exposure.
"""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from threading import RLock
from typing import Mapping, Optional

_KEYRING_SERVICE = "rebel-forge"
_KEYRING_USER = "nebius-bundle"
_CACHE_DIR = Path.home() / ".rebel-forge"
_CACHE_PATH = _CACHE_DIR / "bundle.json"
_LOCK = RLock()
_MEMORY_CACHE: dict[str, str] | None = None

try:  # pragma: no cover - optional dependency
    import keyring  # type: ignore
    from keyring.errors import PasswordDeleteError  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    keyring = None  # type: ignore

    class PasswordDeleteError(Exception):
        """Fallback when keyring is unavailable."""


def cache_bundle(bundle: Mapping[str, str]) -> None:
    """Persist the Nebius credential bundle securely for reuse."""

    global _MEMORY_CACHE
    sanitized = {
        key: value
        for key, value in bundle.items()
        if isinstance(key, str) and isinstance(value, str) and value.strip()
    }
    if not sanitized:
        return

    with _LOCK:
        _MEMORY_CACHE = dict(sanitized)

    if keyring is not None:
        try:
            keyring.set_password(_KEYRING_SERVICE, _KEYRING_USER, json.dumps(sanitized))
            return
        except Exception:
            # Fall back to the file cache if keyring writes fail.
            pass

    _write_file_cache(sanitized)


def load_cached_bundle() -> dict[str, str] | None:
    """Return the cached bundle when present."""

    global _MEMORY_CACHE
    with _LOCK:
        if _MEMORY_CACHE is not None:
            return dict(_MEMORY_CACHE)

    bundle: dict[str, str] | None = None
    if keyring is not None:
        try:
            raw = keyring.get_password(_KEYRING_SERVICE, _KEYRING_USER)
        except Exception:
            raw = None
        if raw:
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, dict):
                    bundle = {
                        key: value
                        for key, value in parsed.items()
                        if isinstance(key, str) and isinstance(value, str)
                    }
            except json.JSONDecodeError:
                bundle = None

    if bundle is None:
        bundle = _read_file_cache()

    with _LOCK:
        if bundle is not None:
            _MEMORY_CACHE = dict(bundle)
    return dict(bundle) if bundle is not None else None


def clear_cached_bundle() -> None:
    """Remove any persisted credential bundle."""

    global _MEMORY_CACHE
    with _LOCK:
        _MEMORY_CACHE = None

    if keyring is not None:
        try:
            keyring.delete_password(_KEYRING_SERVICE, _KEYRING_USER)
        except PasswordDeleteError:
            pass
        except Exception:
            pass

    try:
        _CACHE_PATH.unlink()
    except FileNotFoundError:
        pass
    except OSError:
        pass


def _write_file_cache(bundle: Mapping[str, str]) -> None:
    temp_path: Optional[Path] = None
    try:
        _CACHE_DIR.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", delete=False, dir=str(_CACHE_DIR)
        ) as handle:
            json.dump(bundle, handle, indent=2)
            temp_path = Path(handle.name)
        os.replace(temp_path, _CACHE_PATH)
        _CACHE_PATH.chmod(0o600)
    except Exception:
        if temp_path is not None:
            try:
                temp_path.unlink()
            except Exception:
                pass


def _read_file_cache() -> dict[str, str] | None:
    try:
        raw = _CACHE_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    except OSError:
        return None
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(parsed, dict):
        return None
    return {
        key: value
        for key, value in parsed.items()
        if isinstance(key, str) and isinstance(value, str)
    }


__all__ = ["cache_bundle", "load_cached_bundle", "clear_cached_bundle"]
