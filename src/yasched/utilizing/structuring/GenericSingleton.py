"""Mixin that enforces a single instance per subclass."""

from __future__ import annotations

import threading
from typing import ClassVar, Self


class GenericSingleton:
    """Mixin base class that enforces exactly one instance per subclass.

    Uses double-checked locking with an RLock so that subclasses whose
    __new__ calls super().__new__() do not deadlock when get_instance()
    drives the first construction.
    """

    _instance: ClassVar[Self | None] = None
    _lock: ClassVar[threading.RLock]

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        cls._instance = None
        cls._lock = threading.RLock()

    def __new__(cls, *args: object, **kwargs: object) -> Self:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = object.__new__(cls)
        assert cls._instance is not None
        return cls._instance

    @classmethod
    def get_instance(cls) -> Self:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls()  # triggers __new__ (and subclass __init__) exactly once
        assert cls._instance is not None
        return cls._instance

    @classmethod
    def _reset_instance(cls) -> None:
        with cls._lock:
            cls._instance = None
