"""Generic string-keyed registry with alias support."""

from __future__ import annotations

from typing import Generic, TypeVar

T = TypeVar("T")

_SENTINEL = object()


class GenericRegistry(Generic[T]):
    """String-keyed registry with alias support and configurable duplicate handling."""

    def __init__(self) -> None:
        self._canonical: dict[str, T] = {}
        self._alias_to_canonical: dict[str, str] = {}
        self._canonical_to_aliases: dict[str, set[str]] = {}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _validate_on_duplicate(self, on_duplicate: str) -> None:
        if on_duplicate not in ("raise", "replace", "ignore"):
            raise ValueError(
                f"on_duplicate must be 'raise', 'replace', or 'ignore'; got {on_duplicate!r}"
            )

    def _resolve(self, key: str) -> str | None:
        """Return the canonical key for *key* (canonical or alias), or None."""
        if key in self._canonical:
            return key
        return self._alias_to_canonical.get(key)

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def register(self, key: str, value: T, on_duplicate: str = "raise") -> None:
        self._validate_on_duplicate(on_duplicate)
        if key in self._canonical:
            if on_duplicate == "raise":
                raise KeyError(f"Key {key!r} already exists")
            if on_duplicate == "ignore":
                return
            # replace: fall through to assignment
        self._canonical[key] = value
        self._canonical_to_aliases.setdefault(key, set())

    def register_alias(
        self, canonical_key: str, alias: str, on_duplicate: str = "raise"
    ) -> None:
        self._validate_on_duplicate(on_duplicate)
        if canonical_key not in self._canonical:
            raise KeyError(f"Canonical key {canonical_key!r} does not exist")
        if alias in self._canonical:
            raise ValueError(f"{alias!r} is already a canonical key")

        if alias in self._alias_to_canonical:
            if on_duplicate == "raise":
                raise KeyError(f"Alias {alias!r} already exists")
            if on_duplicate == "ignore":
                return
            # replace: remove from old canonical's alias set
            old_canonical = self._alias_to_canonical[alias]
            self._canonical_to_aliases[old_canonical].discard(alias)

        self._alias_to_canonical[alias] = canonical_key
        self._canonical_to_aliases.setdefault(canonical_key, set()).add(alias)

    def remove(self, key: str) -> None:
        if key in self._alias_to_canonical:
            raise ValueError(f"{key!r} is an alias; use remove_alias() to remove it")
        if key not in self._canonical:
            raise KeyError(f"Key {key!r} does not exist")
        for alias in list(self._canonical_to_aliases.get(key, set())):
            del self._alias_to_canonical[alias]
        del self._canonical_to_aliases[key]
        del self._canonical[key]

    def remove_alias(self, alias: str) -> None:
        if alias not in self._alias_to_canonical:
            raise KeyError(f"Alias {alias!r} does not exist")
        canonical = self._alias_to_canonical.pop(alias)
        self._canonical_to_aliases[canonical].discard(alias)

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def get(self, key: str, default: object = _SENTINEL) -> T:
        canonical = self._resolve(key)
        if canonical is None:
            if default is _SENTINEL:
                raise KeyError(key)
            return default  # type: ignore[return-value]
        return self._canonical[canonical]

    def contains(self, key: str) -> bool:
        return key in self._canonical or key in self._alias_to_canonical

    def canonical_keys(self) -> list[str]:
        return list(self._canonical)

    def all_keys(self) -> list[str]:
        return list(self._canonical) + list(self._alias_to_canonical)

    def aliases_of(self, canonical_key: str) -> list[str]:
        if canonical_key not in self._canonical:
            raise KeyError(f"Canonical key {canonical_key!r} does not exist")
        return list(self._canonical_to_aliases.get(canonical_key, set()))

    def values(self) -> list[T]:
        return list(self._canonical.values())

    def items(self) -> list[tuple[str, T]]:
        return list(self._canonical.items())

    def __len__(self) -> int:
        return len(self._canonical)

    def __contains__(self, key: object) -> bool:
        return isinstance(key, str) and self.contains(key)
