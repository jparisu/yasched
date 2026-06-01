"""Database picker modal (Group A)."""

from __future__ import annotations

import reflex as rx

from yasched_web.state import AppState

# ── shared row style ─────────────────────────────────────────────────────────

_ROW_STYLE = {
    "display": "flex",
    "align_items": "center",
    "gap": "6px",
    "padding": "3px 6px",
    "border_radius": "4px",
    "cursor": "pointer",
    "width": "100%",
    "user_select": "none",
    "_hover": {"background": "var(--accent-3)"},
}


def _browser_row(icon: str, label: str, on_click: rx.EventSpec, color: str = "inherit") -> rx.Component:
    return rx.box(
        rx.icon(icon, size=14, color=color, flex_shrink="0"),
        rx.text(label, size="1", color=color, overflow="hidden", text_overflow="ellipsis", white_space="nowrap"),
        on_click=on_click,
        **_ROW_STYLE,
    )


# ── file browser ─────────────────────────────────────────────────────────────

def _file_browser() -> rx.Component:
    return rx.box(
        rx.vstack(
            # current path breadcrumb
            rx.hstack(
                rx.icon("folder-open", size=12, color="var(--accent-9)"),
                rx.text(
                    AppState.browser_dir,
                    size="1",
                    color="var(--gray-10)",
                    overflow="hidden",
                    text_overflow="ellipsis",
                    white_space="nowrap",
                    flex="1",
                ),
                spacing="1",
                align="center",
                width="100%",
                padding_bottom="4px",
                border_bottom="1px solid var(--gray-4)",
            ),
            # parent directory
            _browser_row(
                "arrow-up",
                "..",
                on_click=AppState.navigate_browser_up,
                color="var(--gray-9)",
            ),
            # subdirectories
            rx.foreach(
                AppState.browser_dirs,
                lambda d: _browser_row(
                    "folder",
                    d.split("/")[-1],
                    on_click=AppState.navigate_browser_into(d),
                    color="#e09000",
                ),
            ),
            # yaml files
            rx.foreach(
                AppState.browser_files,
                lambda f: rx.box(
                    rx.icon("file-text", size=14, color="var(--accent-9)", flex_shrink="0"),
                    rx.text(
                        f.split("/")[-1],
                        size="1",
                        overflow="hidden",
                        text_overflow="ellipsis",
                        white_space="nowrap",
                        color=rx.cond(AppState.path_input == f, "var(--accent-9)", "inherit"),
                        font_weight=rx.cond(AppState.path_input == f, "600", "400"),
                    ),
                    on_click=AppState.select_file(f),
                    **{**_ROW_STYLE, "background": rx.cond(AppState.path_input == f, "var(--accent-3)", "transparent")},
                ),
            ),
            spacing="0",
            align="start",
            width="100%",
        ),
        height="200px",
        overflow_y="auto",
        border="1px solid var(--gray-5)",
        border_radius="6px",
        padding="6px",
        background="var(--gray-1)",
        font_family="monospace",
    )


# ── recent files ─────────────────────────────────────────────────────────────

def _recent_files() -> rx.Component:
    return rx.cond(
        AppState.recent_files.length() > 0,
        rx.vstack(
            rx.text("Recent files", size="1", weight="medium", color="var(--gray-10)"),
            rx.box(
                rx.foreach(
                    AppState.recent_files,
                    lambda f: rx.tooltip(
                        _browser_row(
                            "clock",
                            f.split("/")[-1],
                            on_click=AppState.select_file(f),
                            color="var(--gray-11)",
                        ),
                        content=f,
                    ),
                ),
                width="100%",
                border="1px solid var(--gray-4)",
                border_radius="6px",
                padding="4px",
                max_height="120px",
                overflow_y="auto",
            ),
            spacing="1",
            align="start",
            width="100%",
        ),
        rx.fragment(),
    )


# ── error list ────────────────────────────────────────────────────────────────

def _error_list() -> rx.Component:
    return rx.cond(
        AppState.db_errors.length() > 0,
        rx.vstack(
            rx.foreach(
                AppState.db_errors,
                lambda e: rx.callout(
                    e,
                    icon="triangle-alert",
                    color="red",
                    size="1",
                ),
            ),
            width="100%",
            spacing="1",
        ),
        rx.fragment(),
    )


# ── modal ─────────────────────────────────────────────────────────────────────

def db_modal() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Open Database"),
            rx.dialog.description(
                "Select a YAML schedule file to load.",
                size="2",
                color="var(--gray-10)",
            ),
            rx.vstack(
                # path input + browse refresh
                rx.hstack(
                    rx.tooltip(
                        rx.box(
                            rx.input(
                                placeholder="path/to/schedule.yaml",
                                value=AppState.path_input,
                                on_change=AppState.set_path_input,
                                width="100%",
                                size="2",
                            ),
                            flex="1",
                        ),
                        content="Type a full file path or pick one from the browser below",
                    ),
                    rx.tooltip(
                        rx.button(
                            rx.icon("refresh-cw", size=15),
                            on_click=AppState.navigate_browser_into(AppState.browser_dir),
                            variant="soft",
                            size="2",
                        ),
                        content="Refresh current directory listing",
                    ),
                    spacing="2",
                    width="100%",
                ),
                _file_browser(),
                _recent_files(),
                _error_list(),
                # action buttons
                rx.hstack(
                    rx.tooltip(
                        rx.button(
                            rx.icon("database", size=15),
                            " Load",
                            on_click=AppState.load_database,
                            size="2",
                        ),
                        content="Parse and load the selected YAML file into the app",
                    ),
                    rx.cond(
                        AppState.db_loaded,
                        rx.dialog.close(
                            rx.tooltip(
                                rx.button(
                                    "Cancel",
                                    on_click=AppState.close_modal,
                                    variant="soft",
                                    color_scheme="gray",
                                    size="2",
                                ),
                                content="Close this dialog and keep the current database",
                            ),
                        ),
                        rx.fragment(),
                    ),
                    spacing="2",
                    justify="end",
                    width="100%",
                ),
                spacing="3",
                width="100%",
            ),
            max_width="520px",
        ),
        open=AppState.modal_open,
    )
