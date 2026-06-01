"""Settings page — theme and read-only toggle."""

from __future__ import annotations

import reflex as rx

from yasched_web.state import AppState


def settings_page() -> rx.Component:
    return rx.box(
        rx.heading("Settings", size="6", margin_bottom="1.5rem"),
        rx.vstack(
            # Appearance
            rx.box(
                rx.text("Appearance", size="3", weight="bold", margin_bottom="0.75rem"),
                rx.hstack(
                    rx.text("Theme", size="2"),
                    rx.spacer(),
                    rx.radio_group(
                        ["light", "dark"],
                        value=AppState.theme,
                        on_change=AppState.set_theme,
                        direction="row",
                    ),
                    width="100%",
                    align="center",
                ),
                padding="1rem",
                border="1px solid var(--gray-4)",
                border_radius="8px",
                width="100%",
            ),
            # General
            rx.box(
                rx.text("General", size="3", weight="bold", margin_bottom="0.75rem"),
                rx.hstack(
                    rx.vstack(
                        rx.text("Read-only mode", size="2"),
                        rx.text(
                            "Disables all write operations across the app.",
                            size="1",
                            color="gray",
                        ),
                        spacing="0",
                        align="start",
                    ),
                    rx.spacer(),
                    rx.switch(
                        checked=AppState.read_only,
                        on_change=AppState.toggle_read_only,
                    ),
                    width="100%",
                    align="center",
                ),
                padding="1rem",
                border="1px solid var(--gray-4)",
                border_radius="8px",
                width="100%",
            ),
            spacing="4",
            width="100%",
            max_width="600px",
        ),
        padding="2rem",
    )
