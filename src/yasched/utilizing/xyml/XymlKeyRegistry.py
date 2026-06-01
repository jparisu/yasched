"""Singleton registry mapping directive key strings to XymlKeyBehavior."""

from __future__ import annotations

from yasched.utilizing.structuring.GenericRegistry import GenericRegistry
from yasched.utilizing.structuring.GenericSingleton import GenericSingleton
from yasched.utilizing.xyml.XymlKeyBehavior import XymlKeyBehavior


class XymlKeyRegistry(GenericRegistry[XymlKeyBehavior], GenericSingleton):
    """Process-wide singleton that maps directive key names to their behaviour.

    Pre-registered keys:
      ``__file__``  →  REPLACE
      ``__ext__``   →  EXTEND
    """

    def __init__(self) -> None:
        GenericRegistry.__init__(self)
        self.register("__file__", XymlKeyBehavior.REPLACE)
        self.register("__ext__", XymlKeyBehavior.EXTEND)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def register_key(
        self,
        key: str,
        behavior: XymlKeyBehavior,
        on_duplicate: str = "raise",
    ) -> None:
        """Register *key* with the given *behavior*.

        Raises ``TypeError`` if *behavior* is not a ``XymlKeyBehavior``.
        """
        if not isinstance(behavior, XymlKeyBehavior):
            raise TypeError(f"behavior must be a XymlKeyBehavior instance, got {type(behavior)!r}")
        self.register(key, behavior, on_duplicate=on_duplicate)

    def get_behavior(self, key: str) -> XymlKeyBehavior | None:
        """Return the behavior for *key*, or ``None`` if not a directive."""
        return self.get(key, None)

    def is_directive(self, key: str) -> bool:
        """Return ``True`` if *key* is a registered directive."""
        return self.get_behavior(key) is not None
