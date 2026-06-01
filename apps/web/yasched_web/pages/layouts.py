"""Layouts page — placeholder."""
from __future__ import annotations
import reflex as rx

def layouts_page() -> rx.Component:
    return rx.box(
        rx.heading("Layouts", size="6", margin_bottom="0.5rem"),
        rx.text("Coming soon.", color="gray", size="2"),
        padding="2rem",
    )
