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

from dataclasses import dataclass
import json
import os
import re
import shlex
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any, Mapping, Sequence
from urllib import error as urlerror
from urllib import request as urlrequest
from urllib.parse import urlparse

try:
    import yaml  # type: ignore
except Exception as exc:  # pragma: no cover - dependency validated at runtime
    raise RuntimeError(
        "PyYAML is required for rebel_forge.device(); install with `pip install PyYAML`."
    ) from exc

from .credential_cache import cache_bundle as _cache_bundle, load_cached_bundle as _load_cached_bundle
from .env import load_local_env
from .remote import ensure_remote, RemoteError

_RUN_FLAG = "FORGE_REMOTE_ACTIVE"
_INSTANCE_ID_ENV = "FORGE_ACTIVE_INSTANCE_ID"
_CONFIG_SENTINEL = "FORGE_PROVISIONED"
_DEFAULT_PROFILE = "forge"
_DEFAULT_ENDPOINT = "api.nebius.cloud:443"
_DEFAULT_IMAGE = "computeimage-u00xn32tb5p5decbkv"  # Ubuntu 24.04 CUDA 12.0.2
_DEFAULTS_DIR = Path.home() / ".rebel-forge"
_STATE_FILE = _DEFAULTS_DIR / "provisioning.json"
_SESSION_PATH = _DEFAULTS_DIR / "session.json"
_LEGACY_CREDENTIAL_ENV = "REBEL_FORGE_ALLOW_LEGACY_CREDENTIALS"
_TRUE_VALUES = {"1", "true", "yes", "on"}

_PLATFORM_ALIASES: Mapping[str, str] = {
    "h100": "gpu-h100-sxm",
    "gpu-h100-sxm": "gpu-h100-sxm",
    "h200": "gpu-h200-sxm",
    "gpu-h200-sxm": "gpu-h200-sxm",
    "b200": "gpu-b200-sxm",
    "gpu-b200-sxm": "gpu-b200-sxm",
    "cpu": "cpu-d3",
    "cpu-d3": "cpu-d3",
}

_DEFAULT_CPU_PRESETS: Mapping[str, str] = {
    "cpu-d3": "8vcpu-32gb",
}

_DEFAULT_GPU_COUNTS: Mapping[str, int] = {
    "gpu-h100-sxm": 1,
    "gpu-h200-sxm": 1,
    "gpu-b200-sxm": 8,
}

_PLATFORM_FALLBACKS: Mapping[str, tuple[str, ...]] = {
    "gpu-h100-sxm": ("gpu-h100-sxm", "gpu-h200-sxm", "gpu-b200-sxm"),
}


@dataclass
class NebiusInstance:
    """Metadata for a provisioned Nebius compute instance."""

    instance_id: str
    name: str
    host: str
    username: str
    disk_id: str
    platform: str
    preset: str


class NebiusCLIError(RemoteError):
    """Raised when the Nebius CLI returns an error."""


class NebiusProvisioner:
    """Thin wrapper around the Nebius CLI to create/destroy compute instances."""

    def __init__(
        self,
        *,
        project_id: str,
        service_account_id: str,
        public_key_id: str,
        private_key_pem: str,
        profile: str = _DEFAULT_PROFILE,
        endpoint: str = _DEFAULT_ENDPOINT,
    ) -> None:
        self.project_id = project_id
        self.service_account_id = service_account_id
        self.public_key_id = public_key_id
        self.private_key_pem = private_key_pem.strip()
        self.profile = profile
        self.endpoint = endpoint
        self._preset_cache: dict[str, list[dict[str, Any]]] = {}
        self._ensure_profile()

    # ------------------------------------------------------------------ public API
    def provision_instance(
        self,
        *,
        name: str,
        platform: str,
        preset: str,
        boot_disk_gib: int,
        image_id: str,
        subnet_id: str,
        ssh_public_key: str,
        ssh_username: str = "ubuntu",
    ) -> NebiusInstance:
        disk = self._create_disk(
            name=f"{name}-boot",
            size_gib=boot_disk_gib,
            image_id=image_id,
        )
        try:
            instance = self._create_instance(
                name=name,
                platform=platform,
                preset=preset,
                disk_id=disk,
                subnet_id=subnet_id,
                ssh_public_key=ssh_public_key,
                ssh_username=ssh_username,
            )
        except Exception:
            # Attempt best-effort clean up of the disk if instance creation fails.
            try:
                self._delete_disk(disk)
            finally:
                raise
        return instance

    def release_instance(self, *, instance_id: str, boot_disk_id: str | None = None) -> None:
        """Delete the compute instance (and optionally its boot disk)."""

        self._run_cli(["compute", "instance", "delete", instance_id, "--async=false"])
        if boot_disk_id:
            self._delete_disk(boot_disk_id)

    def discover_subnet(self) -> str:
        """Fallback helper that picks the first subnet in the project."""

        out = self._run_cli(
            ["vpc", "subnet", "list", "--parent-id", self.project_id, "--format", "json"]
        )
        data = json.loads(out)
        items = data.get("items") or []
        if not items:
            raise NebiusCLIError(
                "No VPC subnets found. Set NEBIUS_SUBNET_ID in your environment to pick one."
            )
        return items[0]["metadata"]["id"]

    # ------------------------------------------------------------------ internals
    def _create_disk(self, *, name: str, size_gib: int, image_id: str) -> str:
        args = [
            "compute",
            "disk",
            "create",
            "--parent-id",
            self.project_id,
            "--name",
            name,
            "--type",
            "network_ssd",
            "--size-gibibytes",
            str(size_gib),
            "--source-image-id",
            image_id,
            "--async=false",
            "--format",
            "json",
        ]
        response = json.loads(self._run_cli(args))
        return response["metadata"]["id"]

    def _delete_disk(self, disk_id: str) -> None:
        self._run_cli(["compute", "disk", "delete", disk_id, "--async=false"])

    def _create_instance(
        self,
        *,
        name: str,
        platform: str,
        preset: str,
        disk_id: str,
        subnet_id: str,
        ssh_public_key: str,
        ssh_username: str,
    ) -> NebiusInstance:
        user_data = "\n".join(
            [
                "users:",
                f" - name: {ssh_username}",
                "   sudo: ALL=(ALL) NOPASSWD:ALL",
                "   shell: /bin/bash",
                "   ssh_authorized_keys:",
                f"    - {ssh_public_key.strip()}",
            ]
        )
        spec = {
            "metadata": {
                "parent_id": self.project_id,
                "name": name,
            },
            "spec": {
                "resources": {
                    "platform": platform,
                    "preset": preset,
                },
                "network_interfaces": [
                    {
                        "subnet_id": subnet_id,
                        "name": "eth0",
                        "ip_address": {},
                        "public_ip_address": {},
                    }
                ],
                "boot_disk": {
                    "attach_mode": "READ_WRITE",
                    "existing_disk": {"id": disk_id},
                    "device_id": "boot-disk",
                },
                "cloud_init_user_data": user_data,
            },
        }
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
            json.dump(spec, handle, indent=2)
            temp_path = Path(handle.name)
        try:
            response = json.loads(
                self._run_cli(
                    [
                        "compute",
                        "instance",
                        "create",
                        "--file",
                        str(temp_path),
                        "--async=false",
                        "--format",
                        "json",
                    ]
                )
            )
        finally:
            try:
                temp_path.unlink()
            except FileNotFoundError:
                pass
        host = _extract_public_ip(response)
        instance_id = response["metadata"]["id"]
        return NebiusInstance(
            instance_id=instance_id,
            name=name,
            host=host,
            username=ssh_username,
            disk_id=disk_id,
            platform=platform,
            preset=preset,
        )

    def _run_cli(self, args: Sequence[str]) -> str:
        command = ["nebius", "--profile", self.profile, *args]
        proc = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            raise NebiusCLIError(
                f"Nebius CLI failed ({proc.returncode}): {' '.join(shlex.quote(a) for a in command)}\n{proc.stderr.strip()}"
            )
        return proc.stdout.strip()

    def _ensure_profile(self) -> None:
        config_dir = Path.home() / ".nebius"
        config_dir.mkdir(parents=True, exist_ok=True)
        config_path = config_dir / "config.yaml"
        if config_path.exists():
            with config_path.open("r", encoding="utf-8") as handle:
                config = yaml.safe_load(handle) or {}
        else:
            config = {}
        profiles = config.setdefault("profiles", {})
        profile_cfg = profiles.setdefault(
            self.profile,
            {
                "endpoint": self.endpoint,
                "auth-type": "service account",
            },
        )
        profile_cfg["endpoint"] = self.endpoint
        profile_cfg["auth-type"] = "service account"
        profile_cfg["service-account-id"] = self.service_account_id
        profile_cfg["public-key-id"] = self.public_key_id
        key_path = config_dir / f"service-account-{self.service_account_id}.key"
        key_path.write_text(self.private_key_pem.strip() + "\n", encoding="utf-8")
        key_path.chmod(0o600)
        profile_cfg.pop("private-key", None)
        profile_cfg["private-key-file-path"] = str(key_path)
        config["default"] = self.profile
        with tempfile.NamedTemporaryFile("w", delete=False) as tmp:
            yaml.safe_dump(config, tmp, sort_keys=False)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, config_path)
        config_path.chmod(0o600)

    # ------------------------------------------------------------------ preset helpers
    def auto_preset(self, *, platform: str, gpu_count: int | None) -> str:
        if platform in _DEFAULT_CPU_PRESETS:
            return _DEFAULT_CPU_PRESETS[platform]

        if not platform.startswith("gpu-"):
            raise RemoteError(
                f"Preset not provided for platform '{platform}'. Pass preset='...' explicitly."
            )

        presets = self._platform_presets(platform)
        matches: list[tuple[int, str]] = []
        for item in presets:
            resources = item.get("resources") if isinstance(item, Mapping) else None
            if not isinstance(resources, Mapping):
                continue
            count = resources.get("gpu_count")
            name = item.get("name") if isinstance(item, Mapping) else None
            if isinstance(count, int) and isinstance(name, str):
                matches.append((count, name))
        if not matches:
            raise RemoteError(
                f"No GPU presets available for platform '{platform}'. Provide preset='...'."
            )
        if gpu_count is None:
            return matches[0][1]
        for count, name in matches:
            if count == gpu_count:
                return name
        counts = ", ".join(str(count) for count, _ in matches)
        raise RemoteError(
            f"GPU platform '{platform}' does not support {gpu_count} GPUs. "
            f"Available counts: {counts}. Pass preset='...' to override."
        )

    def _platform_presets(self, platform: str) -> list[dict[str, Any]]:
        cached = self._preset_cache.get(platform)
        if cached is not None:
            return cached
        try:
            response = self._run_cli(
                [
                    "compute",
                    "platform",
                    "get-by-name",
                    "--parent-id",
                    self.project_id,
                    "--name",
                    platform,
                    "--format",
                    "json",
                ]
            )
            data = json.loads(response or "{}")
        except json.JSONDecodeError as exc:
            raise NebiusCLIError(
                f"Unable to parse Nebius platform description for '{platform}'."
            ) from exc
        presets = data.get("spec", {}).get("presets")
        if not isinstance(presets, list):
            presets = []
        self._preset_cache[platform] = presets
        return presets

_CACHED_BUNDLE: dict[str, str] | None = None


def _resolve_credentials() -> dict[str, str]:
    global _CACHED_BUNDLE
    if _CACHED_BUNDLE is not None:
        return _CACHED_BUNDLE

    load_local_env()

    session_payload = _load_session_payload()
    if session_payload is None:
        raise RemoteError(
            "Rebel Forge CLI is not signed in. Run `rebel-forge` and complete the login flow before calling forge.device()."
        )

    bundle: dict[str, str] | None = None
    remote_error: RemoteError | None = None
    fetched: dict[str, str] | None = None
    if _allow_legacy_credentials():
        try:
            fetched = _fetch_remote_bundle()
        except RemoteError as error:
            remote_error = error
            fetched = None
        except Exception:
            fetched = None

    if fetched:
        _cache_bundle(fetched)
        bundle = fetched
    else:
        cached = _load_cached_bundle()
        if cached:
            bundle = cached

    if bundle is None:
        env_bundle = _environment_bundle()
        if env_bundle:
            _cache_bundle(env_bundle)
            bundle = env_bundle

    if bundle is None:
        if remote_error is not None:
            raise RemoteError(
                f"{remote_error}. Set NEBIUS_* variables in your environment or re-run `rebel-forge` to refresh the CLI link."
            ) from remote_error
        if not _allow_legacy_credentials():
            raise RemoteError(
                "Legacy Nebius credential fallback is disabled. Set REBEL_FORGE_ALLOW_LEGACY_CREDENTIALS=1 to opt into local credential usage."
            )
        raise RemoteError(
            "Nebius credentials are not configured. Re-run `rebel-forge` to refresh your session or set the NEBIUS_* variables."
        )

    _CACHED_BUNDLE = bundle
    return bundle


def _fetch_remote_bundle() -> dict[str, str] | None:
    session = _load_session_payload()
    if not session:
        return None
    token = _clean(session.get("token"))
    user_id = _clean(session.get("userId") or session.get("user_id"))
    if not token or not user_id:
        return None
    base = _clean(session.get("login_url")) or os.environ.get("REBEL_FORGE_PORTAL_URL")
    if not base:
        base = "http://localhost:3000"
    url = f"{base.rstrip('/')}/api/cli-auth/nebius"
    request = urlrequest.Request(
        url,
        headers={
            "Accept": "application/json",
            "X-CLI-Token": token,
            "X-CLI-User": user_id,
        },
    )
    try:
        with urlrequest.urlopen(request, timeout=30) as response:
            raw = response.read()
            data = json.loads(raw.decode("utf-8") if raw else "{}")
    except urlerror.HTTPError as error:
        if error.code == 403:
            raise RemoteError(
                "Rebel portal rejected the provisioning request. Re-run `rebel-forge` to refresh your CLI link."
            ) from error
        return None
    except (urlerror.URLError, TimeoutError, json.JSONDecodeError):
        return None

    if not isinstance(data, dict):
        return None
    if "error" in data:
        raise RemoteError(
            f"Rebel portal provisioning failed: {data.get('error') or 'unknown_error'}"
        )

    bundle: dict[str, str] = {}
    for key, value in data.items():
        if isinstance(value, str) and value.strip():
            bundle[key] = value.strip()
    return bundle or None


def _environment_bundle() -> dict[str, str] | None:
    project_id = _clean(os.environ.get("project_id") or os.environ.get("NEBIUS_PROJECT_ID"))
    service_account_id = _clean(
        os.environ.get("service_account_id") or os.environ.get("NEBIUS_SERVICE_ACCOUNT_ID")
    )
    authorized_key = _clean(
        os.environ.get("Authorized_key")
        or os.environ.get("AUTHORIZED_KEY")
        or os.environ.get("NEBIUS_AUTHORIZED_KEY_ID")
    )
    authorized_private_key = _normalize_multiline(
        os.environ.get("AUTHORIZED_KEY_PRIVATE") or os.environ.get("NEBIUS_AUTHORIZED_PRIVATE_KEY")
    )
    if not (project_id and service_account_id and authorized_key and authorized_private_key):
        return None
    bundle: dict[str, str] = {
        "projectId": project_id,
        "serviceAccountId": service_account_id,
        "authorizedKeyId": authorized_key,
        "authorizedPrivateKey": authorized_private_key,
    }
    optional = {
        "accessKeyId": os.environ.get("ACCESS_KEY_ID") or os.environ.get("NEBIUS_ACCESS_KEY_ID"),
        "accessSecret": os.environ.get("ACCESS_SECRET_KEY")
        or os.environ.get("NEBIUS_ACCESS_SECRET_ID")
        or os.environ.get("ACCESS_SECRET"),
        "sshPublicKey": _normalize_multiline(os.environ.get("ssh_key_public")),
        "sshPrivateKey": _normalize_multiline(os.environ.get("ssh_key_private")),
        "subnetId": os.environ.get("NEBIUS_SUBNET_ID"),
        "imageId": os.environ.get("NEBIUS_IMAGE_ID"),
        "endpoint": os.environ.get("NEBIUS_ENDPOINT"),
    }
    for key, value in optional.items():
        cleaned = _clean(value)
        if cleaned:
            bundle[key] = cleaned
    return bundle


def _normalize_multiline(value: str | None) -> str | None:
    if not value:
        return None
    return value.replace("\\r\\n", "\n").replace("\r\n", "\n").strip()


def _normalize_portal_base(value: str | None) -> str | None:
    if not value:
        return None
    candidate = value.strip()
    if not candidate:
        return None
    parsed = urlparse(candidate)
    if parsed.scheme and parsed.netloc:
        normalized = f"{parsed.scheme}://{parsed.netloc}"
        if parsed.path and parsed.path != "/":
            normalized = f"{normalized}{parsed.path.rstrip('/')}"
        return normalized
    if not parsed.scheme and parsed.path:
        candidate_with_scheme = f"https://{candidate}"
        parsed = urlparse(candidate_with_scheme)
        if parsed.scheme and parsed.netloc:
            normalized = f"{parsed.scheme}://{parsed.netloc}"
            if parsed.path and parsed.path != "/":
                normalized = f"{normalized}{parsed.path.rstrip('/')}"
            return normalized
    if parsed.scheme and not parsed.netloc and parsed.path:
        candidate_with_netloc = f"{parsed.scheme}://{parsed.path}"
        parsed = urlparse(candidate_with_netloc)
        if parsed.scheme and parsed.netloc:
            normalized = f"{parsed.scheme}://{parsed.netloc}"
            if parsed.path and parsed.path != "/":
                normalized = f"{normalized}{parsed.path.rstrip('/')}"
            return normalized
    return None


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


def _store_session_updates(session_payload: dict[str, Any], updates: Mapping[str, Any]) -> dict[str, Any]:
    merged = dict(session_payload)
    changed = False
    for key, value in updates.items():
        if value is None:
            continue
        normalized = value.strip() if isinstance(value, str) else value
        if isinstance(normalized, str):
            if not normalized:
                continue
        if merged.get(key) == normalized:
            continue
        merged[key] = normalized
        changed = True
    if not changed:
        return merged
    try:
        _SESSION_PATH.parent.mkdir(parents=True, exist_ok=True)
        _SESSION_PATH.write_text(json.dumps(merged, indent=2), encoding="utf-8")
    except Exception:
        return merged
    return merged


def _resolve_portal_base(session_payload: Mapping[str, Any]) -> tuple[str | None, dict[str, Any]]:
    updates: dict[str, Any] = {}
    candidates = [
        _clean(session_payload.get("login_url")),
        _clean(session_payload.get("loginUrl")),
        _clean(session_payload.get("portal_url")),
        _clean(session_payload.get("portalUrl")),
        _clean(os.environ.get("REBEL_FORGE_PORTAL_URL")),
    ]
    for candidate in candidates:
        normalized = _normalize_portal_base(candidate)
        if normalized:
            updates["login_url"] = normalized
            os.environ.setdefault("REBEL_FORGE_PORTAL_URL", normalized)
            updated_payload = _store_session_updates(dict(session_payload), updates)
            return normalized, updated_payload
    return None, dict(session_payload)


def _allow_legacy_credentials() -> bool:
    raw = os.environ.get(_LEGACY_CREDENTIAL_ENV)
    if raw is None:
        return False
    return raw.strip().lower() in _TRUE_VALUES


def _fetch_default_project_metadata(
    base: str, token: str | None, user_id: str | None
) -> dict[str, str] | None:
    normalized_base = _normalize_portal_base(base)
    if not normalized_base:
        return None
    url = f"{normalized_base.rstrip('/')}/api/nebius/project"
    headers = {
        "Accept": "application/json",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
        headers["X-CLI-Token"] = token
    if user_id:
        headers["X-CLI-User"] = user_id
    request = urlrequest.Request(url, headers=headers)
    try:
        with urlrequest.urlopen(request, timeout=15) as response:
            raw = response.read()
    except urlerror.HTTPError as error:
        # Treat server-side failures as non-fatal so we can fall back to the
        # handshake bundle or environment values.
        if error.code in (401, 403, 404, 500, 502, 503):
            return None
        return None
    except (urlerror.URLError, TimeoutError):
        return None
    except Exception:
        return None
    try:
        parsed = json.loads(raw.decode("utf-8") if raw else "{}")
    except json.JSONDecodeError:
        return None
    if not isinstance(parsed, dict):
        return None
    project_id = _clean(parsed.get("projectId"))
    if not project_id:
        return None
    metadata: dict[str, str] = {"projectId": project_id}
    endpoint = _clean(parsed.get("endpoint"))
    if endpoint:
        metadata["endpoint"] = endpoint
    default_image = _clean(parsed.get("defaultImageId"))
    if default_image:
        metadata["defaultImageId"] = default_image
    default_subnet = _clean(parsed.get("defaultSubnetId"))
    if default_subnet:
        metadata["defaultSubnetId"] = default_subnet
    return metadata


def _resolve_project_id(session_payload: dict[str, Any]) -> tuple[str | None, dict[str, Any]]:
    env_project = _clean(os.environ.get("project_id") or os.environ.get("NEBIUS_PROJECT_ID"))
    if env_project:
        return env_project, session_payload
    cached = _clean(session_payload.get("projectId") or session_payload.get("project_id"))
    if cached:
        os.environ.setdefault("project_id", cached)
        os.environ.setdefault("NEBIUS_PROJECT_ID", cached)
        return cached, session_payload
    base, session_payload = _resolve_portal_base(session_payload)
    if not base:
        return None, session_payload
    token = _clean(session_payload.get("token"))
    user_id = _clean(session_payload.get("userId") or session_payload.get("user_id"))
    if not (token or user_id):
        return None, session_payload
    metadata = _fetch_default_project_metadata(base, token, user_id)
    if not metadata:
        # Fall back to handshake bundle which may carry projectId defaults.
        handshake = _fetch_handshake_bundle(base, token or "", user_id or "")
        if handshake:
            candidate_project = _clean(handshake.get("projectId"))
            endpoint = _clean(handshake.get("endpoint"))
            default_image = _clean(handshake.get("imageId"))
            default_subnet = _clean(handshake.get("subnetId"))
            if candidate_project:
                os.environ.setdefault("project_id", candidate_project)
                os.environ.setdefault("NEBIUS_PROJECT_ID", candidate_project)
                if endpoint:
                    os.environ.setdefault("NEBIUS_ENDPOINT", endpoint)
                if default_image:
                    os.environ.setdefault("NEBIUS_IMAGE_ID", default_image)
                if default_subnet:
                    os.environ.setdefault("NEBIUS_SUBNET_ID", default_subnet)
                updated = _store_session_updates(
                    session_payload,
                    {
                        "projectId": candidate_project,
                        "endpoint": endpoint,
                        "defaultImageId": default_image,
                        "defaultSubnetId": default_subnet,
                    },
                )
                return candidate_project, updated
        return None, session_payload
    project_id = metadata["projectId"]
    os.environ.setdefault("project_id", project_id)
    os.environ.setdefault("NEBIUS_PROJECT_ID", project_id)
    endpoint = metadata.get("endpoint")
    if endpoint:
        os.environ.setdefault("NEBIUS_ENDPOINT", endpoint)
    default_image = metadata.get("defaultImageId")
    if default_image:
        os.environ.setdefault("NEBIUS_IMAGE_ID", default_image)
    default_subnet = metadata.get("defaultSubnetId")
    if default_subnet:
        os.environ.setdefault("NEBIUS_SUBNET_ID", default_subnet)
    session_payload = _store_session_updates(
        session_payload,
        {
            "projectId": project_id,
            "endpoint": endpoint,
            "defaultImageId": default_image,
            "defaultSubnetId": default_subnet,
        },
    )
    return project_id, session_payload


# --------------------------------------------------------------------------- API
def device(
    gpu_type: str,
    *positional_args: object,
    storage_gib: int | str | None = None,
    count: int | str | None = None,
    preset: str | None = None,
    image_id: str | None = None,
    subnet_id: str | None = None,
    instance_name: str | None = None,
) -> Any:
    """
    Provision a Nebius VM and return ``torch.device('cuda')`` once remote.
    The optional ``count`` argument selects how many GPUs the instance should expose.

    When invoked from the local environment the helper will:

    1. Fetch a provisioning bundle from the Rebel portal (or fall back to any
       locally configured `NEBIUS_*` variables) and configure the Nebius CLI.
    2. Create a boot disk from the configured image (defaults to
       ``ubuntu24.04-cuda12.0.2``) sized according to ``storage_gib``.
    3. Launch an instance with the requested GPU platform/count, resolving the
       appropriate Nebius preset automatically when ``preset`` is not provided.
    4. Update the ``NEBIUS_HOST`` environment variable so subsequent calls to
       :func:`ensure_remote` target the freshly created VM, then hand off
       execution by calling :func:`ensure_remote`.

    When the script re-executes on the remote VM the helper simply returns the
    standard ``torch.device('cuda')`` for use by training code.

    Examples
    --------
    ``forge.device("H100", "1", "512 GiB")`` provisions an NVIDIA H100 class VM
    with a 512 GiB boot disk, automatically falling back to H200/B200 capacity
    when H100 is unavailable. Existing calls such as
    ``forge.device("h200", 512, count=2)`` continue to work unchanged.
    """

    if os.environ.get(_RUN_FLAG) == "1":
        import torch

        return torch.device("cuda")

    parsed_storage = _parse_storage_gib(storage_gib)
    parsed_count = _parse_gpu_count(count)
    parsed_count, parsed_storage = _apply_positional_args(positional_args, parsed_count, parsed_storage)
    if parsed_storage is None:
        raise ValueError(
            "storage_gib is required. Provide it as the second or third positional argument "
            "or via storage_gib=..."
        )

    existing_host = _clean(os.environ.get("NEBIUS_HOST"))
    existing_user = _clean(os.environ.get("NEBIUS_USERNAME"))
    existing_private = _normalize_multiline(os.environ.get("NEBIUS_PRIVATE_KEY"))
    if existing_host and existing_user and existing_private:
        os.environ[_INSTANCE_ID_ENV] = os.environ.get(_INSTANCE_ID_ENV, "existing-instance")
        os.environ[_CONFIG_SENTINEL] = "1"
        state_payload = {
            "instance_id": os.environ[_INSTANCE_ID_ENV],
            "disk_id": None,
            "host": existing_host,
            "platform": os.environ.get("NEBIUS_PLATFORM", "unknown"),
            "preset": os.environ.get("NEBIUS_PRESET", ""),
            "created_at": int(time.time()),
        }
        _write_state(state_payload)
        _wait_for_ssh(host=existing_host, ssh_key=existing_private, username=existing_user)
        ensure_remote()
        import torch

        return torch.device("cuda")

    server_instance: dict[str, Any] | None = None
    server_error: RemoteError | None = None
    try:
        server_instance = _server_provision(
            gpu_type=gpu_type,
            gpu_count=parsed_count,
            storage_gib=parsed_storage,
            preset=preset,
            image_id=image_id,
            subnet_id=subnet_id,
            ttl_seconds=None,
        )
    except RemoteError as error:
        server_error = error
    if server_instance is not None:
        instance = server_instance["instance"]
        ssh_private_key = server_instance["ssh_private_key"]
        os.environ[_INSTANCE_ID_ENV] = instance["instanceId"]
        os.environ["NEBIUS_HOST"] = instance["host"]
        os.environ["NEBIUS_USERNAME"] = instance.get("username", "ubuntu")
        os.environ["NEBIUS_PRIVATE_KEY"] = ssh_private_key
        os.environ[_CONFIG_SENTINEL] = "1"
        if instance.get("platform"):
            os.environ.setdefault("NEBIUS_PLATFORM", instance["platform"])
        if instance.get("preset"):
            os.environ.setdefault("NEBIUS_PRESET", instance["preset"])
        state_payload: dict[str, Any] = {
            "instance_id": instance["instanceId"],
            "disk_id": instance.get("bootDiskId"),
            "host": instance["host"],
            "platform": instance.get("platform", gpu_type),
            "preset": instance.get("preset", ""),
            "created_at": int(time.time()),
        }
        if instance.get("gpuCount") is not None:
            state_payload["gpu_count"] = instance["gpuCount"]
        _write_state(state_payload)
        _wait_for_ssh(host=instance["host"], ssh_key=ssh_private_key, username=instance.get("username", "ubuntu"))
        ensure_remote()
        import torch

        return torch.device("cuda")

    if not _allow_legacy_credentials():
        if server_error is not None:
            raise server_error
        raise RemoteError(
            "Rebel provisioning service is unavailable and legacy Nebius credentials are disabled."
        )
    bundle = _resolve_credentials()
    project_id = bundle["projectId"]
    service_account_id = bundle["serviceAccountId"]
    public_key_id = bundle["authorizedKeyId"]
    private_key_pem = bundle["authorizedPrivateKey"]
    ssh_public_key = bundle.get("sshPublicKey") or _require_env(
        "ssh_key_public", "Provide the public SSH key via ssh_key_public."
    )
    ssh_private_key = bundle.get("sshPrivateKey") or _require_env(
        "ssh_key_private", "Provide the private SSH key via ssh_key_private."
    )

    _ensure_cli_on_path()

    normalized_type = gpu_type.strip().lower()
    requested_platform = _PLATFORM_ALIASES.get(normalized_type, normalized_type)
    candidates = _platform_candidates(requested_platform)

    provisioner = NebiusProvisioner(
        project_id=project_id,
        service_account_id=service_account_id,
        public_key_id=public_key_id,
        private_key_pem=private_key_pem,
        endpoint=bundle.get("endpoint", _DEFAULT_ENDPOINT),
    )

    selected_platform: str | None = None
    selected_preset: str | None = None
    resolved_count: int | None = None
    last_error: RemoteError | None = None
    for platform_candidate in candidates:
        candidate_count = _resolve_count_for_platform(platform_candidate, parsed_count)
        try:
            candidate_preset = preset or provisioner.auto_preset(
                platform=platform_candidate, gpu_count=candidate_count
            )
        except RemoteError as exc:
            last_error = exc
            continue
        selected_platform = platform_candidate
        selected_preset = preset or candidate_preset
        resolved_count = candidate_count
        break

    if selected_platform is None or selected_preset is None:
        if last_error is not None:
            raise last_error
        raise RemoteError(f"Unable to resolve Nebius platform for '{gpu_type}'.")

    image = image_id or bundle.get("imageId") or os.environ.get("NEBIUS_IMAGE_ID", _DEFAULT_IMAGE)
    subnet = subnet_id or bundle.get("subnetId") or os.environ.get("NEBIUS_SUBNET_ID")
    if not subnet:
        subnet = provisioner.discover_subnet()

    instance = provisioner.provision_instance(
        name=instance_name or _default_instance_name(),
        platform=selected_platform,
        preset=selected_preset,
        boot_disk_gib=parsed_storage,
        image_id=image,
        subnet_id=subnet,
        ssh_public_key=ssh_public_key,
    )
    state_payload: dict[str, Any] = {
        "instance_id": instance.instance_id,
        "disk_id": instance.disk_id,
        "host": instance.host,
        "platform": instance.platform,
        "preset": instance.preset,
        "created_at": int(time.time()),
    }
    if resolved_count is not None:
        state_payload["gpu_count"] = resolved_count
    _write_state(state_payload)
    os.environ[_INSTANCE_ID_ENV] = instance.instance_id
    os.environ["NEBIUS_HOST"] = instance.host
    os.environ["NEBIUS_USERNAME"] = instance.username
    os.environ.pop("NEBIUS_HOST_FINGERPRINT", None)
    os.environ["NEBIUS_PRIVATE_KEY"] = ssh_private_key
    os.environ[_CONFIG_SENTINEL] = "1"

    _wait_for_ssh(host=instance.host, ssh_key=ssh_private_key, username=instance.username)
    ensure_remote()
    # Execution never reaches here because ensure_remote raises SystemExit.
    import torch  # pragma: no cover - defensive fallback

    return torch.device("cuda")


# --------------------------------------------------------------------------- utils
def _ensure_cli_on_path() -> None:
    cli_dir = Path.home() / ".nebius" / "bin"
    if not cli_dir.is_dir():
        return
    path = os.environ.get("PATH", "")
    parts = path.split(os.pathsep) if path else []
    cli_str = str(cli_dir)
    if cli_str not in parts:
        os.environ["PATH"] = os.pathsep.join([cli_str, *parts]) if parts else cli_str


def _platform_candidates(platform: str) -> tuple[str, ...]:
    return _PLATFORM_FALLBACKS.get(platform, (platform,))


def _resolve_count_for_platform(platform: str, requested: int | None) -> int | None:
    if platform.startswith("gpu-"):
        count = requested if requested is not None else _DEFAULT_GPU_COUNTS.get(platform, 1)
        if count is None or count <= 0:
            raise ValueError("count must be a positive integer when requesting GPUs.")
        return count
    return None


def _apply_positional_args(
    args: Sequence[object], count: int | None, storage: int | None
) -> tuple[int | None, int | None]:
    if len(args) > 2:
        raise TypeError("device() accepts at most three positional arguments (gpu_type, [count], storage_gib).")
    if len(args) == 2:
        if count is not None:
            raise TypeError("GPU count provided both positionally and via keyword.")
        if storage is not None:
            raise TypeError("storage_gib provided both positionally and via keyword.")
        positional_count = _parse_gpu_count(args[0])
        positional_storage = _parse_storage_gib(args[1])
        if positional_storage is None:
            raise ValueError("storage_gib is required when provided positionally.")
        return positional_count, positional_storage
    if len(args) == 1:
        arg = args[0]
        if storage is None:
            positional_storage = _parse_storage_gib(arg)
            if positional_storage is None:
                raise ValueError("storage_gib is required when provided positionally.")
            return count, positional_storage
        if count is None:
            return _parse_gpu_count(arg), storage
        raise TypeError("device() received duplicate positional arguments.")
    return count, storage


def _parse_storage_gib(value: int | str | None) -> int | None:
    if value is None:
        return None
    result = _coerce_positive_int(value, "storage_gib")
    if result is None:
        return None
    return result


def _parse_gpu_count(value: int | str | None) -> int | None:
    if value is None:
        return None
    result = _coerce_positive_int(value, "GPU count")
    return result


def _coerce_positive_int(value: object, label: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        raise TypeError(f"{label} must be a positive integer.")
    if isinstance(value, int):
        if value <= 0:
            raise ValueError(f"{label} must be a positive integer.")
        return value
    if isinstance(value, float):
        if value <= 0 or not value.is_integer():
            raise ValueError(f"{label} must be a positive integer.")
        return int(value)
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None
        match = re.search(r"(\d+)", stripped)
        if not match:
            raise ValueError(f"Unable to parse {label} from '{value}'.")
        parsed = int(match.group(1))
        if parsed <= 0:
            raise ValueError(f"{label} must be a positive integer.")
        return parsed
    raise TypeError(f"{label} must be a positive integer.")


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


def _extract_public_ip(instance: Mapping[str, Any]) -> str:
    nets = instance.get("status", {}).get("network_interfaces") or []
    if not nets:
        raise RemoteError("Nebius instance does not expose any network interfaces.")
    public = nets[0].get("public_ip_address", {}).get("address")
    if not public:
        raise RemoteError("Nebius instance is missing a public IP address.")
    return public.split("/", 1)[0]


def _default_instance_name() -> str:
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    suffix = os.urandom(3).hex()
    return f"forge-instance-{timestamp}-{suffix}"


def _indent_private_key(private_key: str) -> str:
    stripped = private_key.strip().splitlines()
    return "\n".join(f"            {line}" for line in stripped)


def _require_env(key: str, message: str) -> str:
    value = os.environ.get(key)
    if not value:
        raise RemoteError(message)
    return value.strip()


def _fetch_handshake_bundle(base: str, token: str, user_id: str) -> dict[str, Any] | None:
    url = f"{base.rstrip('/')}/api/cli-auth/nebius"
    request = urlrequest.Request(
        url,
        headers={
            "X-CLI-Token": token,
            "X-CLI-User": user_id,
        },
    )
    try:
        with urlrequest.urlopen(request, timeout=30) as response:
            raw = response.read()
    except (urlerror.HTTPError, urlerror.URLError, TimeoutError):
        return None
    try:
        parsed = json.loads(raw.decode("utf-8") if raw else "{}")
    except json.JSONDecodeError:
        return None
    if not isinstance(parsed, dict):
        return None
    return parsed


def _bootstrap_server_credentials(
    base: str, token: str, user_id: str, handshake: Mapping[str, Any], project_id: str
) -> bool:
    service_account_id = _clean(handshake.get("serviceAccountId"))
    authorized_key_id = _clean(handshake.get("authorizedKeyId"))
    authorized_private_key = _normalize_multiline(handshake.get("authorizedPrivateKey"))
    if not (service_account_id and authorized_key_id and authorized_private_key):
        return False
    payload = json.dumps(
        {
            "projectId": project_id,
            "serviceAccountId": service_account_id,
            "authorizedKeyId": authorized_key_id,
            "authorizedPrivateKey": authorized_private_key,
            "endpoint": handshake.get("endpoint"),
            "defaultImageId": handshake.get("imageId"),
            "defaultSubnetId": handshake.get("subnetId"),
        }
    ).encode("utf-8")
    url = f"{base.rstrip('/')}/api/nebius/credentials"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        "X-CLI-Token": token,
        "X-CLI-User": user_id,
    }
    request = urlrequest.Request(url, data=payload, headers=headers)
    try:
        with urlrequest.urlopen(request, timeout=30):
            return True
    except urlerror.HTTPError as error:
        if error.code in (400, 401, 403):
            return False
        return False
    except (urlerror.URLError, TimeoutError):
        return False


def _server_provision(
    *,
    gpu_type: str,
    gpu_count: int | None,
    storage_gib: int,
    preset: str | None,
    image_id: str | None,
    subnet_id: str | None,
    ttl_seconds: int | None,
) -> dict[str, Any] | None:
    session_payload = _load_session_payload()
    allow_legacy = _allow_legacy_credentials()
    if not session_payload:
        raise RemoteError(
            "Rebel Forge CLI is not signed in. Run `rebel-forge` to link your account before provisioning GPUs."
        )
    token = _clean(session_payload.get("token"))
    base, session_payload = _resolve_portal_base(session_payload)
    user_id = _clean(session_payload.get("userId") or session_payload.get("user_id"))
    if not token or not base or not user_id:
        raise RemoteError(
            "Rebel Forge CLI session is incomplete. Re-run `rebel-forge` to refresh your CLI link."
        )
    project_id, session_payload = _resolve_project_id(session_payload)
    if not project_id:
        raise RemoteError(
            "Nebius credentials are not configured for this Rebel account. Contact your administrator to enable provisioning."
        )

    url = f"{base.rstrip('/')}/api/nebius/provision"
    payload: dict[str, Any] = {
        "projectId": project_id,
        "gpuType": gpu_type,
        "storageGiB": storage_gib,
    }
    if gpu_count is not None:
        payload["gpuCount"] = gpu_count
    if preset:
        payload["preset"] = preset
    if image_id:
        payload["imageId"] = image_id
    if subnet_id:
        payload["subnetId"] = subnet_id
    if ttl_seconds is not None:
        payload["ttlSeconds"] = ttl_seconds

    data = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        "X-CLI-Token": token,
        "X-CLI-User": user_id,
    }
    request = urlrequest.Request(url, data=data, headers=headers)
    try:
        with urlrequest.urlopen(request, timeout=120) as response:
            raw = response.read()
    except urlerror.HTTPError as error:
        if error.code == 404:
            # Seed credentials on the server from the CLI handshake, then retry once.
            handshake = _fetch_handshake_bundle(base, token, user_id)
            if handshake and _bootstrap_server_credentials(base, token, user_id, handshake, project_id):
                return _server_provision(
                    gpu_type=gpu_type,
                    gpu_count=gpu_count,
                    storage_gib=storage_gib,
                    preset=preset,
                    image_id=image_id,
                    subnet_id=subnet_id,
                    ttl_seconds=ttl_seconds,
                )
            raise RemoteError(
                "Nebius credentials are not configured for this Rebel account. "
                "Ask an admin to set them, or re-run `rebel-forge` so the portal can ingest your service-account keys."
            ) from error
        if error.code in (401, 403):
            raise RemoteError(
                "Rebel account is not authorized to provision Nebius resources. Re-run `rebel-forge` to refresh your session."
            ) from error
        detail = error.read().decode("utf-8", "ignore")
        raise RemoteError(
            f"Server-side Nebius provisioning failed ({error.code}): {detail or error.reason}"
        ) from error
    except (urlerror.URLError, TimeoutError) as error:
        host_hint = base or "unknown portal"
        raise RemoteError(
            f"Unable to reach the Rebel provisioning service at {host_hint}. "
            "Run `rebel-forge` to refresh your login or set REBEL_FORGE_PORTAL_URL if the portal address changed."
        ) from error

    try:
        parsed = json.loads(raw.decode("utf-8") if raw else "{}")
    except json.JSONDecodeError:
        raise RemoteError("Unexpected response from Rebel provisioning service.")
    instance = parsed.get("instance")
    ssh_key = parsed.get("sshPrivateKey")
    if not isinstance(instance, dict) or not isinstance(ssh_key, str):
        raise RemoteError("Provisioning response missing instance metadata.")
    return {
        "instance": instance,
        "ssh_private_key": ssh_key,
        "ssh_public_key": parsed.get("sshPublicKey"),
        "ssh_fingerprint": parsed.get("sshFingerprint"),
    }
