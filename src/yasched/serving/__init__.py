"""Serving layer: FastAPI app, view DTOs, and the ``yasched`` CLI.

Everything here is local-only: the API binds to localhost by default and makes
no outbound network calls.
"""

from yasched.serving.cli import main

__all__ = ["main"]
