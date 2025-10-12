"""Service provisioning defaults for rebel_forge."""
from __future__ import annotations

import os
from typing import Final

DEFAULT_SERVICE_BASE_URL: Final[str] = "https://tidy-hound-232.convex.cloud"
DEFAULT_SERVICE_TOKEN: Final[str] = "forge-service-token-py"
DEFAULT_PROJECT_ID: Final[str] = "project-u00w2p27pr00nd0qmqfwg4"


def service_base_url() -> str:
    return os.environ.get("REBEL_FORGE_SERVICE_BASE_URL", DEFAULT_SERVICE_BASE_URL)


def service_token() -> str:
    return os.environ.get("REBEL_FORGE_SERVICE_TOKEN", DEFAULT_SERVICE_TOKEN)


def service_project_id() -> str:
    return os.environ.get("REBEL_FORGE_SERVICE_PROJECT_ID", DEFAULT_PROJECT_ID)
