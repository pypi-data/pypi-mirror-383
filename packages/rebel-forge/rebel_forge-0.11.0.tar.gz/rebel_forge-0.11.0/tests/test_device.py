import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

try:
    import torch  # type: ignore
except Exception:  # pragma: no cover - fallback for test environment
    import types

    torch_module = types.ModuleType("torch")
    utils_module = types.ModuleType("torch.utils")
    data_module = types.ModuleType("torch.utils.data")
    setattr(data_module, "DataLoader", object)
    setattr(data_module, "TensorDataset", object)
    setattr(utils_module, "data", data_module)
    setattr(torch_module, "utils", utils_module)
    setattr(torch_module, "device", lambda *_args, **_kwargs: "cpu")
    sys.modules["torch"] = torch_module
    sys.modules["torch.utils"] = utils_module
    sys.modules["torch.utils.data"] = data_module
else:  # pragma: no cover
    import types
    try:
        import torch.utils.data as torch_utils_data  # type: ignore
    except Exception:
        torch_utils_data = types.SimpleNamespace()
        sys.modules["torch.utils.data"] = torch_utils_data  # type: ignore[assignment]

    if not hasattr(torch, "device"):
        torch.device = lambda *_args, **_kwargs: "cpu"  # type: ignore[attr-defined]
    if not hasattr(torch, "utils"):
        torch.utils = types.SimpleNamespace()  # type: ignore[attr-defined]
    if not hasattr(torch.utils, "data"):
        torch.utils.data = torch_utils_data  # type: ignore[attr-defined]
    if not hasattr(torch_utils_data, "DataLoader"):
        torch_utils_data.DataLoader = object  # type: ignore[attr-defined]
    if not hasattr(torch_utils_data, "TensorDataset"):
        torch_utils_data.TensorDataset = object  # type: ignore[attr-defined]


import importlib

device_mod = importlib.import_module("rebel_forge.device")
from rebel_forge.device import NebiusProvisioner, RemoteError


GPU_PLATFORM_RESPONSE = {
    "spec": {
        "presets": [
            {"name": "1gpu-16vcpu-200gb", "resources": {"gpu_count": 1}},
            {"name": "8gpu-128vcpu-1600gb", "resources": {"gpu_count": 8}},
        ]
    }
}


class AutoPresetTest(unittest.TestCase):
    def test_auto_preset_selects_gpu_count(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_home, patch.dict(
            os.environ, {"HOME": tmp_home}, clear=False
        ):
            provisioner = NebiusProvisioner(
                project_id="project-test",
                service_account_id="sa-test",
                public_key_id="pub-test",
                private_key_pem="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----",
                profile="test-profile",
                endpoint="api.nebius.cloud:443",
            )
            with patch.object(
                provisioner,
                "_run_cli",
                return_value=json.dumps(GPU_PLATFORM_RESPONSE),
            ):
                preset = provisioner.auto_preset(platform="gpu-h200-sxm", gpu_count=8)
        self.assertEqual(preset, "8gpu-128vcpu-1600gb")

    def test_auto_preset_rejects_unknown_count(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_home, patch.dict(
            os.environ, {"HOME": tmp_home}, clear=False
        ):
            provisioner = NebiusProvisioner(
                project_id="project-test",
                service_account_id="sa-test",
                public_key_id="pub-test",
                private_key_pem="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----",
                profile="test-profile",
                endpoint="api.nebius.cloud:443",
            )
            with patch.object(
                provisioner,
                "_run_cli",
                return_value=json.dumps(GPU_PLATFORM_RESPONSE),
            ):
                with self.assertRaises(RemoteError):
                    provisioner.auto_preset(platform="gpu-h200-sxm", gpu_count=4)

    def test_auto_preset_cpu_defaults_without_cli(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_home, patch.dict(
            os.environ, {"HOME": tmp_home}, clear=False
        ):
            provisioner = NebiusProvisioner(
                project_id="project-test",
                service_account_id="sa-test",
                public_key_id="pub-test",
                private_key_pem="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----",
                profile="test-profile",
                endpoint="api.nebius.cloud:443",
            )
            with patch.object(provisioner, "_run_cli", MagicMock()) as mock_cli:
                preset = provisioner.auto_preset(platform="cpu-d3", gpu_count=None)
        self.assertEqual(preset, "8vcpu-32gb")
        mock_cli.assert_not_called()

    def test_device_raises_when_remote_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_home, patch.dict(
            os.environ, {"HOME": tmp_home}, clear=False
        ):
            with patch.object(device_mod, "_server_provision", side_effect=RemoteError("service down")):
                with self.assertRaises(RemoteError):
                    device_mod.device("H100", "512")

class ServiceProvisionTests(unittest.TestCase):
    def test_server_provision_posts_to_service_endpoint(self) -> None:
        payloads = {}

        class _Resp:
            def __init__(self, body: dict[str, Any]):
                self._body = json.dumps(body).encode("utf-8")

            def read(self) -> bytes:
                return self._body

            def __enter__(self) -> "_Resp":
                return self

            def __exit__(self, *_args: object) -> bool:
                return False

        def fake_urlopen(request_obj, timeout=0):
            payloads["url"] = request_obj.full_url
            payloads["headers"] = dict(request_obj.headers)
            payloads["body"] = json.loads(request_obj.data.decode("utf-8"))
            return _Resp(
                {
                    "instance": {
                        "instanceId": "inst-1",
                        "host": "198.51.100.10",
                        "username": "ubuntu",
                        "bootDiskId": "disk-1",
                        "platform": "gpu-h100-sxm",
                        "preset": "preset-h100",
                        "gpuCount": 1,
                    },
                    "sshPrivateKey": "-----BEGIN OPENSSH PRIVATE KEY-----\\n...\n-----END OPENSSH PRIVATE KEY-----",
                    "sshPublicKey": "ssh-rsa AAAA",
                    "sshFingerprint": "fp:123",
                }
            )

        with patch.object(device_mod._service, "service_base_url", return_value="https://forge.example.com"), patch.object(
            device_mod._service, "service_token", return_value="service-token"
        ), patch.object(device_mod._service, "service_project_id", return_value="project-service"), patch.object(
            device_mod.urlrequest, "urlopen", side_effect=fake_urlopen
        ):
            response = device_mod._server_provision(
                gpu_type="H100",
                gpu_count=1,
                storage_gib=512,
                preset=None,
                image_id=None,
                subnet_id=None,
                ttl_seconds=None,
            )

        self.assertIsNotNone(response)
        self.assertEqual(payloads["url"], "https://forge.example.com/api/nebius/provision")
        self.assertEqual(payloads["headers"]["X-Service-Token"], "service-token")
        self.assertEqual(payloads["body"]["projectId"], "project-service")
        self.assertEqual(payloads["body"]["gpuType"], "H100")


if __name__ == "__main__":
    unittest.main()
