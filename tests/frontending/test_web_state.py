"""Unit tests for pure-Python state logic in yasched_web.

These tests cover the parts of the state layer that don't require a running
Reflex app: config I/O, data-conversion helpers, and recent-file management.
"""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("reflex", reason="reflex not installed; run: pip install -e '.[frontend]'")

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------


def test_load_config_missing_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """load_config returns defaults when the config file does not exist."""
    monkeypatch.setattr(
        "yasched_web.state.config._CONFIG_PATH",
        tmp_path / "nonexistent.yaml",
    )
    from yasched_web.state.config import YaschedConfig, load_config

    cfg = load_config()
    assert isinstance(cfg, YaschedConfig)
    assert cfg.theme == "light"
    assert cfg.read_only is False
    assert cfg.recent_files == []


def test_save_and_load_config_roundtrip(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config_path = tmp_path / ".yasched" / "config.yaml"
    monkeypatch.setattr("yasched_web.state.config._CONFIG_PATH", config_path)

    from yasched_web.state.config import YaschedConfig, load_config, save_config

    cfg = YaschedConfig(
        theme="dark",
        read_only=True,
        recent_files=["/a/b.yaml", "/c/d.yaml"],
        default_database="/a/b.yaml",
    )
    save_config(cfg)
    assert config_path.exists()

    loaded = load_config()
    assert loaded.theme == "dark"
    assert loaded.read_only is True
    assert loaded.recent_files == ["/a/b.yaml", "/c/d.yaml"]
    assert loaded.default_database == "/a/b.yaml"


def test_load_config_partial_yaml(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """load_config fills in defaults for missing keys."""
    config_path = tmp_path / "config.yaml"
    config_path.write_text("theme: dark\n")
    monkeypatch.setattr("yasched_web.state.config._CONFIG_PATH", config_path)

    from yasched_web.state.config import load_config

    cfg = load_config()
    assert cfg.theme == "dark"
    assert cfg.read_only is False  # default


def test_load_config_corrupt_yaml(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """load_config returns defaults when the YAML is unparseable."""
    config_path = tmp_path / "config.yaml"
    config_path.write_text(": : : invalid yaml {{{\n")
    monkeypatch.setattr("yasched_web.state.config._CONFIG_PATH", config_path)

    from yasched_web.state.config import load_config

    cfg = load_config()
    assert cfg.theme == "light"


def test_add_recent_file_prepends() -> None:
    from yasched_web.state.config import YaschedConfig, add_recent_file

    cfg = YaschedConfig(recent_files=["/old/a.yaml", "/old/b.yaml"])
    updated = add_recent_file(cfg, "/new/c.yaml")
    assert updated.recent_files[0] == "/new/c.yaml"


def test_add_recent_file_deduplicates() -> None:
    from yasched_web.state.config import YaschedConfig, add_recent_file

    cfg = YaschedConfig(recent_files=["/a.yaml", "/b.yaml"])
    updated = add_recent_file(cfg, "/a.yaml")
    assert updated.recent_files.count("/a.yaml") == 1
    assert updated.recent_files[0] == "/a.yaml"


def test_add_recent_file_enforces_max(tmp_path: Path) -> None:
    from yasched_web.state.config import YaschedConfig, add_recent_file

    existing = [f"/{i}.yaml" for i in range(10)]
    cfg = YaschedConfig(recent_files=existing)
    updated = add_recent_file(cfg, "/new.yaml", max_entries=10)
    assert len(updated.recent_files) == 10
    assert updated.recent_files[0] == "/new.yaml"


# ---------------------------------------------------------------------------
# _layout_to_fields
# ---------------------------------------------------------------------------


def test_layout_to_fields_none() -> None:
    from yasched_web.state.app_state import _layout_to_fields

    result = _layout_to_fields(None)
    assert result["layout_id"] == ""
    assert result["layout_bg_type"] == ""
    assert result["layout_bg_colors"] == []
    assert result["layout_border_type"] == ""
    assert result["layout_icon_type"] == ""


def test_layout_to_fields_id_only() -> None:
    from yasched.coring.Layout import Layout

    from yasched_web.state.app_state import _layout_to_fields

    layout = Layout(id="blue_theme")
    result = _layout_to_fields(layout)
    assert result["layout_id"] == "blue_theme"
    assert result["layout_bg_type"] == ""
    assert result["layout_bg_color"] == ""
    assert result["layout_bg_colors"] == []
    assert result["layout_border_type"] == ""
    assert result["layout_icon_type"] == ""


def test_layout_to_fields_solid_background() -> None:
    from yasched.coring.Layout import Layout, SolidBackground
    from yasched.utilizing.coloring.Color import Color

    from yasched_web.state.app_state import _layout_to_fields

    color = Color(r=1.0, g=0.0, b=0.0)
    layout = Layout(id="red", backgrounds=[SolidBackground(color=color)])
    result = _layout_to_fields(layout)
    assert result["layout_bg_type"] == "solid"
    assert result["layout_bg_color"] == color.to_hex()
    assert result["layout_bg_colors"] == []


def test_layout_to_fields_gradient_background() -> None:
    from yasched.coring.Layout import (
        GradientBottomLeftBackground,
        GradientTopRightBackground,
        Layout,
    )
    from yasched.utilizing.coloring.Color import Color

    from yasched_web.state.app_state import _layout_to_fields

    c1 = Color(r=1.0, g=0.0, b=0.0)
    c2 = Color(r=0.0, g=0.0, b=1.0)
    layout = Layout(
        id="grad",
        backgrounds=[GradientTopRightBackground(color=c1), GradientBottomLeftBackground(color=c2)],
    )
    result = _layout_to_fields(layout)
    assert result["layout_bg_type"] == "gradient"
    assert result["layout_bg_color"] == ""
    assert len(result["layout_bg_colors"]) == 2
