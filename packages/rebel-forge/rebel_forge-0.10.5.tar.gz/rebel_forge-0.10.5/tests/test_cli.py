import importlib
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

try:
    import torch  # type: ignore
except Exception:
    torch = types.ModuleType("torch")
    torch.device = lambda *_args, **_kwargs: "cpu"  # type: ignore[attr-defined]
    utils_module = types.ModuleType("torch.utils")
    data_module = types.ModuleType("torch.utils.data")
    utils_module.data = data_module  # type: ignore[attr-defined]
    sys.modules["torch"] = torch
    sys.modules["torch.utils"] = utils_module
    sys.modules["torch.utils.data"] = data_module
else:  # pragma: no cover - align torch shims with device tests
    if not hasattr(torch, "device"):
        torch.device = lambda *_args, **_kwargs: "cpu"  # type: ignore[attr-defined]
    if not hasattr(torch, "utils"):
        torch.utils = types.SimpleNamespace()  # type: ignore[attr-defined]
    if not hasattr(torch.utils, "data"):
        torch.utils.data = types.SimpleNamespace()  # type: ignore[attr-defined]


class LogoutCommandTest(unittest.TestCase):
    def test_logout_clears_state_without_portal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_home:
            temp_home = Path(tmp_home)
            with patch("pathlib.Path.home", return_value=temp_home):
                for module in (
                    "rebel_forge.cli",
                    "rebel_forge.onboarding",
                    "rebel_forge.credential_cache",
                ):
                    sys.modules.pop(module, None)
                cli = importlib.import_module("rebel_forge.cli")
                importlib.import_module("rebel_forge.onboarding")
                cache = importlib.import_module("rebel_forge.credential_cache")
                cache.keyring = None  # type: ignore[attr-defined]

                marker_dir = temp_home / ".rebel-forge"
                marker_dir.mkdir(parents=True, exist_ok=True)
                session_path = marker_dir / "session.json"
                marker_path = marker_dir / "onboarding.done"
                bundle_path = marker_dir / "bundle.json"
                handshake_path = marker_dir / "cli-handshake-testtoken"
                session_path.write_text("{}")
                marker_path.write_text("{}")
                bundle_path.write_text("{}")
                handshake_path.write_text("{}")
                cache._MEMORY_CACHE = {"foo": "bar"}  # type: ignore[attr-defined]

                original_argv = sys.argv
                sys.argv = ["rebel-forge", "logout"]
                try:
                    with patch.object(cli, "_load_cli_environment") as mock_load, patch.object(
                        cli, "_ensure_default_export"
                    ) as mock_export, patch.object(cli, "_ensure_portal_ready") as mock_portal:
                        with self.assertRaises(SystemExit) as exit_info:
                            cli.main()
                finally:
                    sys.argv = original_argv

                mock_load.assert_not_called()
                mock_export.assert_not_called()
                mock_portal.assert_not_called()
                self.assertEqual(exit_info.exception.code, 0)
                self.assertFalse(session_path.exists())
                self.assertFalse(marker_path.exists())
                self.assertFalse(bundle_path.exists())
                self.assertFalse(handshake_path.exists())
                self.assertIsNone(cache.load_cached_bundle())


if __name__ == "__main__":
    unittest.main()
