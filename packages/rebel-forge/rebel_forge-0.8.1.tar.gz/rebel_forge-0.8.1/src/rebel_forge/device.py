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

_PLATFORM_ALIASES: Mapping[str, str] = {
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
    "gpu-h200-sxm": 1,
    "gpu-b200-sxm": 8,
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
        profile_cfg["private-key"] = _indent_private_key(self.private_key_pem)
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

    bundle = None
    remote_error: RemoteError | None = None
    try:
        bundle = _fetch_remote_bundle()
    except RemoteError as error:
        remote_error = error
    except Exception:
        bundle = None

    if bundle is None:
        bundle = _environment_bundle()

    if bundle is None:
        if remote_error is not None:
            raise RemoteError(
                f"{remote_error}. Set NEBIUS_* variables in your environment or re-run `rebel-forge` to refresh the CLI link."
            ) from remote_error
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
    """

    if os.environ.get(_RUN_FLAG) == "1":
        import torch

        return torch.device("cuda")

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

    platform = _PLATFORM_ALIASES.get(gpu_type.lower(), gpu_type)

    resolved_count: int | None = count
    if platform.startswith("gpu-"):
        if resolved_count is None:
            resolved_count = _DEFAULT_GPU_COUNTS.get(platform, 1)
        if resolved_count is None or resolved_count <= 0:
            raise ValueError("count must be a positive integer when requesting GPUs.")
    else:
        resolved_count = None

    image = image_id or bundle.get("imageId") or os.environ.get("NEBIUS_IMAGE_ID", _DEFAULT_IMAGE)

    provisioner = NebiusProvisioner(
        project_id=project_id,
        service_account_id=service_account_id,
        public_key_id=public_key_id,
        private_key_pem=private_key_pem,
        endpoint=bundle.get("endpoint", _DEFAULT_ENDPOINT),
    )
    subnet = subnet_id or bundle.get("subnetId") or os.environ.get("NEBIUS_SUBNET_ID")
    if not subnet:
        subnet = provisioner.discover_subnet()

    resolved_preset = preset or provisioner.auto_preset(platform=platform, gpu_count=resolved_count)

    instance = provisioner.provision_instance(
        name=instance_name or _default_instance_name(),
        platform=platform,
        preset=resolved_preset,
        boot_disk_gib=storage_gib,
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
