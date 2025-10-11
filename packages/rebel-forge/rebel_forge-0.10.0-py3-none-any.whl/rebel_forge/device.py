"""
Nebius infrastructure provisioning helpers exposed via ``forge.device``.

The entrypoint mirrors the familiar ``torch.device`` selection, but when
invoked from a local environment it will provision a Nebius VM based on the
requested GPU profile, prime SSH credentials, and hand execution off to that
remote instance via ``ensure_remote``. Once the script is running on the VM
the helper simply returns ``torch.device("cuda")`` for use by the training
code.
"""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any, Mapping
from urllib import error as urlerror
from urllib import request as urlrequest

from .remote import ensure_remote, RemoteError

_RUN_FLAG = "FORGE_REMOTE_ACTIVE"
_INSTANCE_ID_ENV = "FORGE_ACTIVE_INSTANCE_ID"
_CONFIG_SENTINEL = "FORGE_PROVISIONED"
_DEFAULTS_DIR = Path.home() / ".rebel-forge"
_STATE_FILE = _DEFAULTS_DIR / "provisioning.json"
_SESSION_PATH = _DEFAULTS_DIR / "session.json"

_PLATFORM_ALIASES: Mapping[str, str] = {
    "h200": "gpu-h200-sxm",
    "gpu-h200-sxm": "gpu-h200-sxm",
    "b200": "gpu-b200-sxm",
    "gpu-b200-sxm": "gpu-b200-sxm",
    "cpu": "cpu-d3",
    "cpu-d3": "cpu-d3",
}


class ProvisioningAuthError(RemoteError):
    """Raised when the short-lived provisioning token is invalid or expired."""


def _clean(value: object) -> str | None:
    if isinstance(value, str):
        candidate = value.strip()
        if candidate:
            return candidate
    return None


def _load_session_payload() -> dict[str, Any] | None:
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


def _persist_session_payload(payload: Mapping[str, Any]) -> None:
    _DEFAULTS_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", delete=False) as handle:
        json.dump(payload, handle, indent=2)
        temp_path = Path(handle.name)
    os.replace(temp_path, _SESSION_PATH)


def _ensure_provisioning_token(session: dict[str, Any], *, force_refresh: bool = False) -> str:
    now = time.time()
    token = _clean(session.get("provisioning_token"))
    expires_at = _coerce_timestamp(session.get("provisioning_expires_at"))
    if force_refresh or not token or expires_at is None or expires_at <= now + 15:
        refreshed = _request_provisioning_token(session)
        if not refreshed:
            raise RemoteError(
                "Unable to obtain a provisioning token from the Rebel Forge portal. Run `rebel-forge login` to re-authenticate."
            )
        token = refreshed["token"]
    if not token:
        raise RemoteError(
            "Provisioning token missing after refresh. Run `rebel-forge login` to re-authenticate."
        )
    return token


def _request_provisioning_token(session: dict[str, Any]) -> dict[str, Any] | None:
    token = _clean(session.get("token"))
    user_id = _clean(session.get("userId") or session.get("user_id"))
    if not token or not user_id:
        raise RemoteError(
            "Rebel Forge CLI session is missing authentication details. Run `rebel-forge login` to link your account."
        )

    base = _clean(session.get("login_url")) or os.environ.get("REBEL_FORGE_PORTAL_URL") or "http://localhost:3000"
    url = f"{base.rstrip('/')}/api/cli-auth/provisioning-token"

    request = urlrequest.Request(
        url,
        data=b"",
        headers={
            "Accept": "application/json",
            "X-CLI-Token": token,
            "X-CLI-User": user_id,
        },
        method="POST",
    )
    try:
        with urlrequest.urlopen(request, timeout=30) as response:
            raw = response.read()
            data = json.loads(raw.decode("utf-8") if raw else "{}")
    except urlerror.HTTPError as error:
        if error.code in {401, 403}:
            raise RemoteError(
                "Session expired or invalid. Run `rebel-forge login` to re-authenticate."
            ) from error
        raise RemoteError(
            f"Failed to obtain provisioning token (HTTP {error.code})."
        ) from error
    except (urlerror.URLError, TimeoutError) as error:
        raise RemoteError(f"Unable to reach the Rebel Forge portal: {error}") from error

    if not isinstance(data, dict):
        raise RemoteError("Rebel Forge portal returned an unexpected provisioning response.")

    new_token = _clean(data.get("token"))
    issued_at = _coerce_timestamp(data.get("issuedAt") or data.get("issued_at")) or time.time()
    expires_at = _coerce_timestamp(data.get("expiresAt") or data.get("expires_at"))
    if not new_token or expires_at is None:
        raise RemoteError("Provisioning token response was incomplete. Run `rebel-forge login` to refresh your session.")

    session["provisioning_token"] = new_token
    session["provisioning_issued_at"] = issued_at
    session["provisioning_expires_at"] = expires_at
    session["last_provisioning_refresh"] = time.time()
    _persist_session_payload(session)

    return {
        "token": new_token,
        "issued_at": issued_at,
        "expires_at": expires_at,
    }


def _coerce_timestamp(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return None
    return None


def prime_provisioning_token(force_refresh: bool = False) -> bool:
    """
    Ensure a valid provisioning token exists for the active CLI session.

    Returns True when a token is present (after refreshing if necessary).
    """

    session = _load_session_payload()
    if not session:
        return False
    try:
        _ensure_provisioning_token(session, force_refresh=force_refresh)
        return True
    except RemoteError:
        return False


def _provision_via_gateway(
    *,
    session: Mapping[str, Any],
    provisioning_token: str,
    gpu_type: str,
    storage_gib: int,
    count: int | None,
    preset: str | None,
    image_id: str | None,
    subnet_id: str | None,
    instance_name: str | None,
    cluster: str | None,
) -> dict[str, Any] | None:
    base = _clean(session.get("login_url")) or os.environ.get("REBEL_FORGE_PORTAL_URL") or "http://localhost:3000"
    url = f"{base.rstrip('/')}/api/forge/device"

    payload: dict[str, Any] = {
        "device": gpu_type,
        "storageGib": storage_gib,
    }
    if count is not None:
        payload["gpuCount"] = count
    if preset:
        payload["preset"] = preset
    if image_id:
        payload["imageId"] = image_id
    if subnet_id:
        payload["subnetId"] = subnet_id
    if instance_name:
        payload["instanceName"] = instance_name
    if cluster:
        payload["cluster"] = cluster

    metadata: dict[str, Any] = {}
    for key in ("session_id", "sessionId", "sessionId".lower()):
        value = session.get(key) if isinstance(session, Mapping) else None
        if isinstance(value, str) and value.strip():
            metadata["sessionId"] = value.strip()
            break
    device_id = session.get("device_id") if isinstance(session, Mapping) else None
    if isinstance(device_id, str) and device_id.strip():
        metadata["deviceId"] = session["device_id"].strip()
    if metadata:
        payload["metadata"] = metadata

    user_id = _clean(session.get("userId") if isinstance(session, Mapping) else None)
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {provisioning_token}",
    }
    if user_id:
        headers["X-CLI-User"] = user_id

    request = urlrequest.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urlrequest.urlopen(request, timeout=120) as response:
            raw = response.read()
            data = json.loads(raw.decode("utf-8") if raw else "{}")
    except urlerror.HTTPError as error:
        if error.code in {401, 403}:
            raise ProvisioningAuthError(
                "Rebel Forge portal rejected the provisioning token."
            ) from error
        if error.code == 404:
            return None
        if error.code >= 500:
            return None
        try:
            raw = error.read()
            data = json.loads(raw.decode("utf-8") if raw else "{}")
        except Exception:
            data = {}
    except (urlerror.URLError, TimeoutError):
        return None
    except Exception:
        return None

    if not isinstance(data, dict):
        return None
    if "error" in data:
        error_code = data.get("error")
        if error_code in {"token_mismatch", "provisioning_token_invalid"}:
            raise ProvisioningAuthError("Provisioning token mismatch between CLI and server.")
        if error_code in {"token_required", "user_required", "provisioning_token_required"}:
            raise ProvisioningAuthError("Provisioning rejected due to missing authentication headers.")
        return None

    return data


# --------------------------------------------------------------------------- API
def device(
    gpu_type: str,
    storage_gib: int,
    *,
    count: int | None = None,
    preset: str | None = None,
    image_id: str | None = None,
    subnet_id: str | None = None,
    instance_name: str | None = None,
    cluster: str | None = None,
) -> Any:
    """
    Provision a Nebius VM via the Rebel Forge service and return ``torch.device("cuda")`` once
    the script re-executes on the remote host.

    The optional ``count`` argument selects how many GPUs the instance should expose. All
    provisioning happens server-side using short-lived tokens exchanged during the CLI login
    flow, so provider credentials remain confined to the portal. When the instance is ready the
    helper re-runs the active script remotely and returns the standard ``torch.device("cuda")``.
    """

    if os.environ.get(_RUN_FLAG) == "1":
        import torch

        return torch.device("cuda")

    session = _load_session_payload()
    if not session:
        raise RemoteError(
            "Rebel Forge CLI is not signed in. Run `rebel-forge login` before calling forge.device()."
        )

    service_result: dict[str, Any] | None = None
    last_error: RemoteError | None = None

    for attempt in range(2):
        try:
            token = _ensure_provisioning_token(session, force_refresh=attempt == 1)
        except RemoteError as error:
            last_error = error
            break

        try:
            service_result = _provision_via_gateway(
                session=session,
                provisioning_token=token,
                gpu_type=gpu_type,
                storage_gib=storage_gib,
                count=count,
                preset=preset,
                image_id=image_id,
                subnet_id=subnet_id,
                instance_name=instance_name,
                cluster=cluster,
            )
        except ProvisioningAuthError as error:
            last_error = RemoteError(
                "Session expired or invalid. Run `rebel-forge login` to re-authenticate."
            )
            if attempt == 0:
                # Reload the session payload after refreshing the provisioning token.
                session = _load_session_payload() or session
                continue
            raise last_error from error
        except RemoteError:
            raise
        except Exception:
            service_result = None

        if service_result:
            break

        # Reload the session file in case another process refreshed it.
        session = _load_session_payload() or session

    if service_result:
        private_key = _clean(service_result.get("privateKey"))
        host = _clean(service_result.get("host"))
        username = _clean(service_result.get("username")) or "ubuntu"
        instance_id = _clean(service_result.get("instanceId"))
        disk_id = _clean(service_result.get("diskId"))
        platform = _clean(service_result.get("platform")) or _PLATFORM_ALIASES.get(gpu_type.lower(), gpu_type)
        resolved_preset = _clean(service_result.get("preset")) or preset or "unknown"
        cluster_label = _clean(service_result.get("cluster")) or cluster
        if not (private_key and host and instance_id):
            service_result = None
        else:
            state_payload: dict[str, Any] = {
                "instance_id": instance_id,
                "disk_id": disk_id,
                "host": host,
                "platform": platform,
                "preset": resolved_preset,
                "created_at": int(time.time()),
                "provisioner": "service",
            }
            gpu_count_value = service_result.get("gpuCount") or service_result.get("gpu_count") or count
            if isinstance(gpu_count_value, int) and gpu_count_value > 0:
                state_payload["gpu_count"] = gpu_count_value
            if cluster_label:
                state_payload["cluster"] = cluster_label
            _write_state(state_payload)
            os.environ[_INSTANCE_ID_ENV] = instance_id
            os.environ["NEBIUS_HOST"] = host
            os.environ["NEBIUS_USERNAME"] = username
            os.environ.pop("NEBIUS_HOST_FINGERPRINT", None)
            os.environ["NEBIUS_PRIVATE_KEY"] = private_key
            os.environ[_CONFIG_SENTINEL] = "1"
            _wait_for_ssh(host=host, ssh_key=private_key, username=username)
            ensure_remote()
            import torch  # pragma: no cover - defensive fallback

            return torch.device("cuda")

    if last_error is not None:
        raise last_error
    raise RemoteError(
        "Rebel Forge provisioning service is unavailable. Run `rebel-forge login` to refresh your session and retry."
    )


# --------------------------------------------------------------------------- utils
def _wait_for_ssh(*, host: str, ssh_key: str, username: str, timeout: int = 600) -> None:
    """Poll until the newly provisioned host accepts SSH connections."""

    with tempfile.NamedTemporaryFile("w", delete=False) as handle:
        handle.write(ssh_key.strip() + "\n")
        key_path = Path(handle.name)
    key_path.chmod(0o600)
    deadline = time.time() + timeout
    try:
        while time.time() < deadline:
            proc = subprocess.run(
                [
                    "ssh",
                    "-i",
                    str(key_path),
                    "-o",
                    "StrictHostKeyChecking=no",
                    "-o",
                    "BatchMode=yes",
                    f"{username}@{host}",
                    "true",
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
            if proc.returncode == 0:
                return
            time.sleep(5)
    finally:
        try:
            key_path.unlink()
        except FileNotFoundError:
            pass
    raise RemoteError(
        f"Timed out waiting for SSH connectivity to {host}. "
        "The instance may still be booting – check the Nebius console."
    )


def _write_state(payload: Mapping[str, Any]) -> None:
    _DEFAULTS_DIR.mkdir(parents=True, exist_ok=True)
    with _STATE_FILE.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
