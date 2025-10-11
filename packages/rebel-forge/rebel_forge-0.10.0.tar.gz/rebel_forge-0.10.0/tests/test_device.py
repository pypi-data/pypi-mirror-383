import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

try:
    import torch  # type: ignore
except Exception:  # pragma: no cover - fallback shim when torch is unavailable
    torch = types.SimpleNamespace(device=lambda *_args, **_kwargs: "cpu")  # type: ignore


import importlib

device_mod = importlib.import_module("rebel_forge.device")
from rebel_forge.device import ProvisioningAuthError, RemoteError


class DeviceTokenFlowTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp_dir.cleanup)

        defaults_path = Path(self.tmp_dir.name)
        session_path = defaults_path / "session.json"
        state_path = defaults_path / "provisioning.json"

        self.patchers = [
            patch.object(device_mod, "_DEFAULTS_DIR", defaults_path),
            patch.object(device_mod, "_SESSION_PATH", session_path),
            patch.object(device_mod, "_STATE_FILE", state_path),
        ]
        for patcher in self.patchers:
            patcher.start()
            self.addCleanup(patcher.stop)

        # Avoid touching real SSH or remote execution during tests.
        self.wait_patch = patch.object(device_mod, "_wait_for_ssh", MagicMock())
        self.remote_patch = patch.object(device_mod, "ensure_remote", MagicMock())
        self.wait_patch.start()
        self.remote_patch.start()
        self.addCleanup(self.wait_patch.stop)
        self.addCleanup(self.remote_patch.stop)

    def _write_session(self, payload: dict[str, object]) -> None:
        device_mod._SESSION_PATH.parent.mkdir(parents=True, exist_ok=True)
        device_mod._SESSION_PATH.write_text(json.dumps(payload))

    def _read_session(self) -> dict[str, object]:
        if not device_mod._SESSION_PATH.exists():
            return {}
        return json.loads(device_mod._SESSION_PATH.read_text())

    def test_device_requires_login_when_session_missing(self) -> None:
        with self.assertRaises(RemoteError):
            device_mod.device("h200", storage_gib=256)

    def test_device_fetches_token_and_provisions(self) -> None:
        handshake = {
            "login_url": "http://localhost:3000",
            "token": "handshake-token",
            "userId": "user_123",
        }
        self._write_session(handshake)

        def mock_request_token(session: dict[str, object]) -> dict[str, object]:
            session["provisioning_token"] = "issued-token"
            session["provisioning_issued_at"] = 1000.0
            session["provisioning_expires_at"] = 2000.0
            device_mod._persist_session_payload(session)
            return {
                "token": "issued-token",
                "issued_at": 1000.0,
                "expires_at": 2000.0,
            }

        service_response = {
            "privateKey": "-----BEGIN PRIVATE KEY-----\n...",
            "host": "1.2.3.4",
            "username": "ubuntu",
            "instanceId": "instance-1",
            "diskId": "disk-1",
            "platform": "gpu-h200-sxm",
            "preset": "1gpu-16vcpu",
        }

        with patch.object(device_mod, "_request_provisioning_token", side_effect=mock_request_token) as request_mock:
            with patch.object(device_mod, "_provision_via_gateway", return_value=service_response) as provision_mock:
                result = device_mod.device("h200", storage_gib=256)

        self.assertEqual(result, torch.device("cuda"))  # type: ignore[arg-type]
        request_mock.assert_called_once()
        provision_mock.assert_called_once()

        persisted = self._read_session()
        self.assertEqual(persisted.get("provisioning_token"), "issued-token")

    def test_device_refreshes_token_after_auth_error(self) -> None:
        handshake = {
            "login_url": "http://localhost:3000",
            "token": "handshake-token",
            "userId": "user_123",
            "provisioning_token": "stale-token",
            "provisioning_expires_at": 0,
        }
        self._write_session(handshake)

        def refresh_token(session: dict[str, object]) -> dict[str, object]:
            session["provisioning_token"] = "fresh-token"
            session["provisioning_issued_at"] = 10_000.0
            session["provisioning_expires_at"] = 11_000.0
            device_mod._persist_session_payload(session)
            return {
                "token": "fresh-token",
                "issued_at": 10_000.0,
                "expires_at": 11_000.0,
            }

        service_response = {
            "privateKey": "-----BEGIN PRIVATE KEY-----\n...",
            "host": "1.2.3.4",
            "username": "ubuntu",
            "instanceId": "instance-2",
            "diskId": "disk-2",
            "platform": "gpu-h200-sxm",
            "preset": "1gpu-16vcpu",
        }

        provision_calls: list[str] = []

        def provision_side_effect(*_args, **_kwargs):
            provision_calls.append("called")
            if len(provision_calls) == 1:
                raise ProvisioningAuthError("expired")
            return service_response

        with patch.object(device_mod, "_request_provisioning_token", side_effect=refresh_token) as request_mock:
            with patch.object(device_mod, "_provision_via_gateway", side_effect=provision_side_effect) as provision_mock:
                result = device_mod.device("h200", storage_gib=256)

        self.assertEqual(result, torch.device("cuda"))  # type: ignore[arg-type]
        self.assertGreaterEqual(len(provision_calls), 2)
        self.assertGreaterEqual(request_mock.call_count, 1)
        self.assertGreaterEqual(provision_mock.call_count, 2)

    def test_prime_provisioning_token_handles_missing_session(self) -> None:
        self.assertFalse(device_mod.prime_provisioning_token())

        self._write_session({"login_url": "http://localhost:3000", "token": "handshake", "userId": "user"})

        with patch.object(device_mod, "_request_provisioning_token", return_value={"token": "cached", "expires_at": 9999}):
            self.assertTrue(device_mod.prime_provisioning_token(force_refresh=True))


if __name__ == "__main__":
    unittest.main()
