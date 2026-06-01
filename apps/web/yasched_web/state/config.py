"""Read/write ~/.yasched/config.yaml — server-side persistent configuration."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path

import yaml

_CONFIG_PATH = Path.home() / ".yasched" / "config.yaml"


@dataclass
class YaschedConfig:
    default_database: str = ""
    theme: str = "light"
    read_only: bool = False
    recent_files: list[str] = field(default_factory=list)
    show_deadlines: bool = True
    upcoming_days: int = 7
    grid_start_hour: int = 7
    grid_end_hour: int = 22
    grid_granularity_minutes: int = 60
    kanban_noise: int = 20
    alert_muted: dict[str, bool] = field(default_factory=dict)
    alert_dismissed: dict[str, list[str]] = field(default_factory=dict)


def load_config() -> YaschedConfig:
    if not _CONFIG_PATH.exists():
        return YaschedConfig()
    try:
        raw = yaml.safe_load(_CONFIG_PATH.read_text()) or {}
        return YaschedConfig(
            default_database=raw.get("default_database", ""),
            theme=raw.get("theme", "light"),
            read_only=raw.get("read_only", False),
            recent_files=raw.get("recent_files", []),
            show_deadlines=raw.get("show_deadlines", True),
            upcoming_days=raw.get("upcoming_days", 7),
            grid_start_hour=raw.get("grid_start_hour", 7),
            grid_end_hour=raw.get("grid_end_hour", 22),
            grid_granularity_minutes=raw.get("grid_granularity_minutes", 60),
            kanban_noise=raw.get("kanban_noise", 20),
            alert_muted=raw.get("alert_muted", {}),
            alert_dismissed=raw.get("alert_dismissed", {}),
        )
    except Exception:
        return YaschedConfig()


def save_config(cfg: YaschedConfig) -> None:
    _CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    _CONFIG_PATH.write_text(yaml.dump(asdict(cfg), default_flow_style=False))


def add_recent_file(cfg: YaschedConfig, path: str, max_entries: int = 10) -> YaschedConfig:
    recent = [p for p in cfg.recent_files if p != path]
    recent.insert(0, path)
    return YaschedConfig(**{**asdict(cfg), "recent_files": recent[:max_entries]})
