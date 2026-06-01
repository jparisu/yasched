"""Environment-based configuration for the yasched API."""

from __future__ import annotations

import os
from pathlib import Path


class Config:
    db_path: Path = Path(os.environ.get("YASCHED_DB_PATH", "data/db.yaml"))
    cors_origins: list[str] = os.environ.get("YASCHED_CORS_ORIGINS", "http://localhost:5173").split(
        ","
    )
