import os
import sys
import tempfile
import unittest
from pathlib import Path

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

from rebel_forge import env as forge_env


class LoadEnvTest(unittest.TestCase):
    def setUp(self) -> None:
        self._original_env = os.environ.copy()
        forge_env._ENV_LOADED = False  # type: ignore[attr-defined]

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._original_env)
        forge_env._ENV_LOADED = False  # type: ignore[attr-defined]

    def test_load_env_file_applies_allowed_keys(self) -> None:
        with tempfile.NamedTemporaryFile("w", delete=False) as handle:
            handle.write(
                "NEBIUS_PROJECT_ID=project-test\n"
                "IGNORED_KEY=value\n"
                "PYPI_TOKEN=test-token\n"
            )
            path = handle.name
        os.environ["REBEL_FORGE_ENV_FILE"] = path
        os.environ.pop("NEBIUS_PROJECT_ID", None)
        os.environ.pop("PYPI_TOKEN", None)

        forge_env.load_local_env()

        self.assertEqual(os.environ.get("NEBIUS_PROJECT_ID"), "project-test")
        self.assertEqual(os.environ.get("PYPI_TOKEN"), "test-token")
        self.assertNotIn("IGNORED_KEY", os.environ)
        os.unlink(path)


if __name__ == "__main__":
    unittest.main()
