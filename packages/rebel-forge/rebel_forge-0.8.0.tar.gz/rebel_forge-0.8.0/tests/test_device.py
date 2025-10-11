import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
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


if __name__ == "__main__":
    unittest.main()
