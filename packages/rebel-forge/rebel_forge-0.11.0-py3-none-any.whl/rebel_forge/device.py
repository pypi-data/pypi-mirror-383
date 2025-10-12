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

try:
    import yaml  # type: ignore
except Exception as exc:  # pragma: no cover - dependency validated at runtime
    raise RuntimeError(
        "PyYAML is required for rebel_forge.device(); install with `pip install PyYAML`."
    ) from exc

from . import _service
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

def _normalize_multiline(value: str | None) -> str | None:
    if not value:
        return None
    return value.replace("\\r\\n", "\n").replace("\r\n", "\n").strip()


def _clean(value: object) -> str | None:
    if isinstance(value, str):
        candidate = value.strip()
        if candidate:
            return candidate
    return None




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

    When invoked locally the helper will:

    1. Submit a provisioning request to the Rebel Forge service, which in turn
       uses shared Nebius credentials stored on the backend.
    2. Wait for the provisioned host to accept SSH connections before handing
       execution off to :func:`ensure_remote`.

    When the script re-executes on the remote VM the helper simply returns the
    standard ``torch.device('cuda')`` for use by training code.
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

    if server_error is not None:
        raise server_error

    raise RemoteError("Rebel provisioning service is unavailable. Try again later or contact Rebel support.")


# --------------------------------------------------------------------------- utils
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
    base = _service.service_base_url().rstrip("/")
    token = _service.service_token()
    if not token:
        raise RemoteError("Rebel Forge service token is not configured.")

    url = f"{base}/api/nebius/provision"
    payload: dict[str, Any] = {
        "projectId": _service.service_project_id(),
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
        "X-Service-Token": token,
    }
    request = urlrequest.Request(url, data=data, headers=headers)
    try:
        with urlrequest.urlopen(request, timeout=120) as response:
            raw = response.read()
    except urlerror.HTTPError as error:
        detail = ""
        try:
            detail = error.read().decode("utf-8", "ignore")
        except Exception:
            detail = error.reason
        if error.code in (401, 403):
            raise RemoteError("Rebel service token rejected by provisioning backend.") from error
        detail = error.read().decode("utf-8", "ignore")
        raise RemoteError(
            f"Service-side Nebius provisioning failed ({error.code}): {detail or error.reason}"
        ) from error
    except (urlerror.URLError, TimeoutError) as error:
        raise RemoteError(f"Unable to reach the Rebel provisioning service at {base}.") from error

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
