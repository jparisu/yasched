"""Process-wide singleton color registry."""

from __future__ import annotations

from yasched.utilizing.coloring.ColorRegistry import ColorRegistry
from yasched.utilizing.structuring.GenericSingleton import GenericSingleton


class SingletonColorRegistry(ColorRegistry, GenericSingleton):
    """Exactly one ColorRegistry instance per process, accessible via get_instance()."""
