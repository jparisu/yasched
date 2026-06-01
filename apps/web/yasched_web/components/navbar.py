"""Top navigation bar."""

from __future__ import annotations

import reflex as rx

from yasched_web.state import AppState


def _db_status_badge() -> rx.Component:
    return rx.cond(
        AppState.db_loaded,
        rx.cond(
            AppState.db_errors.length() > 0,
            rx.tooltip(
                rx.badge(
                    rx.icon("triangle-alert", size=13),
                    " ",
                    AppState.db_errors.length(),
                    " error(s)",
                    color_scheme="yellow",
                    variant="soft",
                ),
                content="Database loaded with validation errors — click Open DB to see details",
            ),
            rx.tooltip(
                rx.badge(
                    rx.icon("check-circle", size=13),
                    " Loaded",
                    color_scheme="green",
                    variant="soft",
                ),
                content=AppState.db_path,
            ),
        ),
        rx.tooltip(
            rx.badge(
                rx.icon("circle-x", size=13),
                " No database",
                color_scheme="gray",
                variant="soft",
            ),
            content="No database loaded — click Open DB to select a file",
        ),
    )


def _db_stats() -> rx.Component:
    return rx.cond(
        AppState.db_loaded,
        rx.hstack(
            rx.text(
                rx.icon("layout-grid", size=12),
                " ",
                AppState.db_stats["layouts"],
                size="1",
                color="gray",
            ),
            rx.text(
                rx.icon("folder", size=12),
                " ",
                AppState.db_stats["topics"],
                size="1",
                color="gray",
            ),
            rx.text(
                rx.icon("calendar", size=12),
                " ",
                AppState.db_stats["events"],
                size="1",
                color="gray",
            ),
            rx.text(
                rx.icon("check-square", size=12),
                " ",
                AppState.db_stats["tasks"],
                size="1",
                color="gray",
            ),
            spacing="3",
        ),
        rx.fragment(),
    )


def _read_only_indicator() -> rx.Component:
    return rx.cond(
        AppState.read_only,
        rx.tooltip(
            rx.badge(
                rx.icon("lock", size=13),
                " Read-only",
                color_scheme="orange",
                variant="soft",
            ),
            content="Read-only mode is ON — all write operations are disabled. Change this in Settings.",
        ),
        rx.fragment(),
    )


def navbar() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.hstack(
                rx.icon("calendar-days", size=22, color="var(--accent-9)"),
                rx.heading("yasched", size="4"),
                spacing="2",
                align="center",
            ),
            rx.spacer(),
            _db_stats(),
            _db_status_badge(),
            _read_only_indicator(),
            rx.tooltip(
                rx.button(
                    rx.icon("database", size=15),
                    " Open DB",
                    on_click=AppState.open_modal,
                    variant="soft",
                    size="2",
                ),
                content="Open or reload a YAML schedule database",
            ),
            spacing="3",
            align="center",
            width="100%",
        ),
        padding="0 1.5rem",
        height="56px",
        border_bottom="1px solid var(--gray-4)",
        background="var(--color-background)",
        position="sticky",
        top="0",
        z_index="100",
        display="flex",
        align_items="center",
    )
