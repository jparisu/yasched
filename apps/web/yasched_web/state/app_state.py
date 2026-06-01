"""Central application state for yasched_web."""

from __future__ import annotations

from pathlib import Path

import reflex as rx
from pydantic import BaseModel

from yasched.backending import (
    ConsistencyError,
    DatabaseInterface,
    DatabaseLoader,
    DatabaseManager,
)
from yasched.backending.Database import ResolvedTopic
from yasched.backending.loading.DatabaseParser import DatabaseParseError
from yasched.coring.Layout import (
    GradientBottomLeftBackground,
    GradientTopRightBackground,
    Layout,
    SolidBackground,
)

from .config import YaschedConfig, add_recent_file, load_config, save_config


class TopicData(BaseModel):
    """Serialisable snapshot of a resolved topic for use in Reflex state."""

    id: str
    name: str
    description: str
    tags: list[str]
    effective_tags: list[str]
    parent_ids: list[str]
    child_ids: list[str]
    # flattened layout fields (all empty strings if no layout)
    layout_id: str
    layout_bg_type: str       # "solid" | "gradient" | "none" | ""
    layout_bg_color: str      # hex string or ""
    layout_bg_colors: list[str]  # gradient stops as hex list
    layout_border_type: str
    layout_border_color: str
    layout_border_width: str
    layout_icon_type: str
    layout_icon_value: str


def _layout_to_fields(layout: Layout | None) -> dict:
    """Flatten a Layout into plain serialisable fields."""
    if layout is None:
        return dict(
            layout_id="",
            layout_bg_type="",
            layout_bg_color="",
            layout_bg_colors=[],
            layout_border_type="",
            layout_border_color="",
            layout_border_width="",
            layout_icon_type="",
            layout_icon_value="",
        )

    backgrounds = layout.backgrounds
    solid = next((b for b in backgrounds if isinstance(b, SolidBackground)), None)
    gradient_layers = [
        b for b in backgrounds if isinstance(b, (GradientTopRightBackground, GradientBottomLeftBackground))
    ]

    if solid:
        bg_type = "solid"
        bg_color = solid.color.to_hex()
        bg_colors: list[str] = []
    elif gradient_layers:
        bg_type = "gradient"
        bg_color = ""
        bg_colors = [b.color.to_hex() for b in gradient_layers]
    else:
        bg_type = ""
        bg_color = ""
        bg_colors = []

    border = layout.border
    icon = layout.icon
    return dict(
        layout_id=layout.id or "",
        layout_bg_type=bg_type,
        layout_bg_color=bg_color,
        layout_bg_colors=bg_colors,
        layout_border_type=border.type if border else "",
        layout_border_color=(border.color.to_hex() if border else ""),
        layout_border_width=border.width if border else "",
        layout_icon_type=icon.type if icon else "",
        layout_icon_value=icon.value if icon else "",
    )


def _resolved_topic_to_data(rt: ResolvedTopic) -> TopicData:
    return TopicData(
        id=rt.id,
        name=rt.name,
        description=rt.description or "",
        tags=list(rt.raw.tags),
        effective_tags=list(rt.effective_tags),
        parent_ids=[p.id for p in rt.parents],
        child_ids=[c.id for c in rt.children],
        **_layout_to_fields(rt.effective_layout),
    )


class AppState(rx.State):
    # ------------------------------------------------------------------ config
    theme: str = "light"
    read_only: bool = False
    recent_files: list[str] = []

    # ------------------------------------------------------------------ db
    db_path: str = ""
    db_errors: list[str] = []
    db_loaded: bool = False
    db_stats: dict[str, int] = {}

    # runtime-only (not serialisable by Reflex — held in backend var)
    _iface: DatabaseInterface | None = None

    # ------------------------------------------------------------------ topics
    topics_map: dict[str, TopicData] = {}
    root_topic_ids: list[str] = []

    # ------------------------------------------------------------------ modal
    modal_open: bool = False
    browser_dir: str = ""
    browser_dirs: list[str] = []
    browser_files: list[str] = []
    path_input: str = ""

    # ------------------------------------------------------------------ init
    def on_load(self) -> None:
        cfg: YaschedConfig = load_config()
        self.theme = cfg.theme
        self.read_only = cfg.read_only
        self.recent_files = cfg.recent_files

        if cfg.default_database:
            self.path_input = cfg.default_database
            self.modal_open = True
        else:
            self.modal_open = True

        self._refresh_browser(str(Path.cwd()))

    # ------------------------------------------------------------------ modal
    def open_modal(self) -> None:
        self.modal_open = True

    def close_modal(self) -> None:
        if self.db_loaded:
            self.modal_open = False

    # ------------------------------------------------------------------ browser
    def _refresh_browser(self, directory: str) -> None:
        p = Path(directory)
        try:
            entries = sorted(p.iterdir(), key=lambda e: (e.is_file(), e.name.lower()))
        except PermissionError:
            return
        self.browser_dir = str(p)
        self.browser_dirs = [
            str(e) for e in entries if e.is_dir() and not e.name.startswith(".")
        ]
        self.browser_files = [
            str(e) for e in entries if e.is_file() and e.suffix in (".yaml", ".yml")
        ]

    def navigate_browser_up(self) -> None:
        parent = str(Path(self.browser_dir).parent)
        self._refresh_browser(parent)

    def navigate_browser_into(self, directory: str) -> None:
        self._refresh_browser(directory)

    def select_file(self, filepath: str) -> None:
        self.path_input = filepath

    def set_path_input(self, value: str) -> None:
        self.path_input = value

    # ------------------------------------------------------------------ load
    def load_database(self) -> None:
        path = self.path_input.strip()
        if not path:
            return

        self._iface = None
        self.db_loaded = False
        self.db_errors = []
        self.db_stats = {}

        try:
            db = DatabaseLoader.load(path)
        except (DatabaseParseError, FileNotFoundError, Exception) as exc:
            self.db_errors = [str(exc)]
            return

        errors = DatabaseManager.validate(db)
        self.db_errors = [str(e) for e in errors]

        try:
            rdb = DatabaseManager.resolve(db)
            self._iface = DatabaseInterface(rdb)
            self.db_loaded = True
            self.db_path = path
            self.db_stats = {
                "layouts": len(rdb.layouts),
                "topics": len(rdb.topics),
                "events": len(rdb.events),
                "tasks": len(rdb.tasks),
            }
        except ConsistencyError as exc:
            if not self.db_errors:
                self.db_errors = [str(exc)]
            return

        # populate topic data
        self.topics_map = {
            tid: _resolved_topic_to_data(rt)
            for tid, rt in rdb.topics.items()
        }
        self.root_topic_ids = [t.id for t in rdb.root_topics]

        # persist to config
        cfg = load_config()
        cfg.default_database = path
        cfg = add_recent_file(cfg, path)
        self.recent_files = cfg.recent_files
        save_config(cfg)

        if not self.db_errors:
            self.modal_open = False

    # ------------------------------------------------------------------ settings
    def set_theme(self, value: str) -> None:
        self.theme = value
        cfg = load_config()
        cfg.theme = value
        save_config(cfg)

    def toggle_read_only(self, value: bool) -> None:
        self.read_only = value
        cfg = load_config()
        cfg.read_only = value
        save_config(cfg)
