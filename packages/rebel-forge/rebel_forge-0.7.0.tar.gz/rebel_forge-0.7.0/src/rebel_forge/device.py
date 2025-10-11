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

try:
    import yaml  # type: ignore
except Exception as exc:  # pragma: no cover - dependency validated at runtime
    raise RuntimeError(
        "PyYAML is required for rebel_forge.device(); install with `pip install PyYAML`."
    ) from exc

from .remote import ensure_remote, RemoteError

_RUN_FLAG = "FORGE_REMOTE_ACTIVE"
_INSTANCE_ID_ENV = "FORGE_ACTIVE_INSTANCE_ID"
_CONFIG_SENTINEL = "FORGE_PROVISIONED"
_DEFAULT_PROFILE = "forge"
_DEFAULT_ENDPOINT = "api.nebius.cloud:443"
_DEFAULT_IMAGE = "computeimage-u00xn32tb5p5decbkv"  # Ubuntu 24.04 CUDA 12.0.2
_DEFAULTS_DIR = Path.home() / ".rebel-forge"
_STATE_FILE = _DEFAULTS_DIR / "provisioning.json"

_GPU_PLATFORM_ALIASES: Mapping[str, tuple[str, str]] = {
    "h200": ("gpu-h200-sxm", "1gpu-16vcpu-200gb"),
    "gpu-h200-sxm": ("gpu-h200-sxm", "1gpu-16vcpu-200gb"),
    "b200": ("gpu-b200-sxm", "8gpu-160vcpu-1792gb"),
    "gpu-b200-sxm": ("gpu-b200-sxm", "8gpu-160vcpu-1792gb"),
    "cpu": ("cpu-d3", "8vcpu-32gb"),
    "cpu-d3": ("cpu-d3", "8vcpu-32gb"),
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


# --------------------------------------------------------------------------- API
def device(
    gpu_type: str,
    storage_gib: int,
    *,
    preset: str | None = None,
    image_id: str | None = None,
    subnet_id: str | None = None,
    instance_name: str | None = None,
) -> Any:
    """
    Provision a Nebius VM and return ``torch.device('cuda')`` once remote.

    When invoked from the local environment the helper will:

    1. Ensure the Nebius CLI is configured using the service-account values
       loaded from the environment (``service_account_id``, ``Authorized_key``
       and ``AUTHORIZED_KEY_PRIVATE``).
    2. Create a boot disk from the configured image (defaults to
       ``ubuntu24.04-cuda12.0.2``) sized according to ``storage_gib``.
    3. Launch an instance with the requested GPU platform/preset inside the
       configured project/subnet.
    4. Update the ``NEBIUS_HOST`` environment variable so subsequent calls to
       :func:`ensure_remote` target the freshly created VM, then hand off
       execution by calling :func:`ensure_remote`.

    When the script re-executes on the remote VM the helper simply returns the
    standard ``torch.device('cuda')`` for use by training code.
    """

    if os.environ.get(_RUN_FLAG) == "1":
        import torch

        return torch.device("cuda")

    project_id = _require_env("project_id", "Project ID (project_id) is required.")
    service_account_id = _require_env(
        "service_account_id", "Service account id (service_account_id) is required."
    )
    public_key_id = _require_env(
        "Authorized_key", "Authorized key id (Authorized_key) is required."
    )
    private_key_pem = _require_env(
        "AUTHORIZED_KEY_PRIVATE",
        "Service-account private key (AUTHORIZED_KEY_PRIVATE) is required.",
    )
    ssh_public_key = _require_env(
        "ssh_key_public", "Provide the public SSH key via ssh_key_public."
    )
    ssh_private_key = _require_env(
        "ssh_key_private", "Provide the private SSH key via ssh_key_private."
    )

    platform, default_preset = _GPU_PLATFORM_ALIASES.get(
        gpu_type.lower(), (gpu_type, preset or "")
    )
    resolved_preset = preset or default_preset
    if not resolved_preset:
        raise ValueError(
            f"Preset not provided and no default found for GPU type '{gpu_type}'. "
            "Pass the Nebius preset explicitly (e.g. preset='1gpu-16vcpu-200gb')."
        )

    image = image_id or os.environ.get("NEBIUS_IMAGE_ID", _DEFAULT_IMAGE)

    provisioner = NebiusProvisioner(
        project_id=project_id,
        service_account_id=service_account_id,
        public_key_id=public_key_id,
        private_key_pem=private_key_pem,
    )
    subnet = subnet_id or os.environ.get("NEBIUS_SUBNET_ID")
    if not subnet:
        subnet = provisioner.discover_subnet()

    instance = provisioner.provision_instance(
        name=instance_name or _default_instance_name(),
        platform=platform,
        preset=resolved_preset,
        boot_disk_gib=storage_gib,
        image_id=image,
        subnet_id=subnet,
        ssh_public_key=ssh_public_key,
    )
    _write_state(
        {
            "instance_id": instance.instance_id,
            "disk_id": instance.disk_id,
            "host": instance.host,
            "platform": instance.platform,
            "preset": instance.preset,
            "created_at": int(time.time()),
        }
    )
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
