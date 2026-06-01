"""yasched web app — main entry point."""

from __future__ import annotations

import reflex as rx

from yasched_web.components import db_modal, navbar, sidebar
from yasched_web.pages import (
    analytics_page,
    calendar_page,
    dashboard_page,
    graph_page,
    layouts_page,
    schedule_page,
    settings_page,
    tasks_page,
    topics_page,
)
from yasched_web.state import AppState


def _layout(content: rx.Component) -> rx.Component:
    return rx.theme(
        rx.vstack(
            navbar(),
            rx.hstack(
                sidebar(),
                rx.box(content, flex="1", overflow_y="auto"),
                spacing="0",
                align="start",
                width="100%",
                min_height="calc(100vh - 56px)",
            ),
            spacing="0",
            width="100%",
        ),
        db_modal(),
        appearance=AppState.theme,
        accent_color="violet",
        style={"font_family": "Inter, system-ui, sans-serif"},
    )


@rx.page(route="/", on_load=AppState.on_load)
def index() -> rx.Component:
    return _layout(dashboard_page())


@rx.page(route="/tasks")
def tasks() -> rx.Component:
    return _layout(tasks_page())


@rx.page(route="/calendar")
def calendar() -> rx.Component:
    return _layout(calendar_page())


@rx.page(route="/schedule")
def schedule() -> rx.Component:
    return _layout(schedule_page())


@rx.page(route="/topics")
def topics() -> rx.Component:
    return _layout(topics_page())


@rx.page(route="/layouts")
def layouts() -> rx.Component:
    return _layout(layouts_page())


@rx.page(route="/analytics")
def analytics() -> rx.Component:
    return _layout(analytics_page())


@rx.page(route="/graph")
def graph() -> rx.Component:
    return _layout(graph_page())


@rx.page(route="/settings")
def settings() -> rx.Component:
    return _layout(settings_page())


app = rx.App(
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap",
    ],
)
