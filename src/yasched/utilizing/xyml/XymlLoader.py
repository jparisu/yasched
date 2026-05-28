"""Extended-YAML loader: resolves directive keys by splicing in referenced files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from yasched.utilizing.xyml.XymlKeyBehavior import XymlKeyBehavior
from yasched.utilizing.xyml.XymlKeyRegistry import XymlKeyRegistry

# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class XymlError(ValueError):
    """Base class for all xyml errors."""


class XymlFileNotFoundError(XymlError):
    """A file referenced by a directive does not exist."""


class XymlCircularIncludeError(XymlError):
    """A file includes itself directly or transitively."""


class XymlDirectiveError(XymlError):
    """A directive key is used in an invalid way."""


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------


class XymlLoader:
    """Stateless utility that loads and resolves xyml documents.

    Public entry points: ``load(path)`` and ``loads(content, base_path)``.
    """

    @staticmethod
    def load(path: str | Path) -> Any:
        """Load and resolve the xyml document at *path*."""
        resolved = Path(path).resolve()
        if not resolved.exists():
            raise XymlFileNotFoundError(f"File not found: {resolved}")
        content = resolved.read_text(encoding="utf-8")
        node = yaml.safe_load(content)
        return XymlLoader._resolve(node, resolved.parent, frozenset())

    @staticmethod
    def loads(content: str, base_path: str | Path | None = None) -> Any:
        """Parse *content* as xyml. Relative paths resolve from *base_path*."""
        base = Path(base_path).resolve() if base_path is not None else Path.cwd()
        node = yaml.safe_load(content)
        return XymlLoader._resolve(node, base, frozenset())

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _resolve(node: Any, base_path: Path, stack: frozenset[Path]) -> Any:
        if isinstance(node, dict):
            return XymlLoader._resolve_mapping(node, base_path, stack)
        if isinstance(node, list):
            return [XymlLoader._resolve(item, base_path, stack) for item in node]
        return node

    @staticmethod
    def _resolve_mapping(node: dict[str, Any], base_path: Path, stack: frozenset[Path]) -> Any:
        registry = XymlKeyRegistry.get_instance()
        directives = {k: v for k, v in node.items() if registry.is_directive(k)}

        if len(directives) > 1:
            raise XymlDirectiveError(
                f"A mapping may contain at most one directive key; found: {sorted(directives)}"
            )

        if not directives:
            return {k: XymlLoader._resolve(v, base_path, stack) for k, v in node.items()}

        directive_key, file_value = next(iter(directives.items()))
        behavior = registry.get_behavior(directive_key)
        file_path = XymlLoader._resolve_path(str(file_value), base_path)

        if behavior is XymlKeyBehavior.REPLACE:
            if len(node) > 1:
                sibling_keys = [k for k in node if k != directive_key]
                raise XymlDirectiveError(
                    f"'{directive_key}' cannot have sibling keys; found: {sibling_keys}"
                )
            return XymlLoader._handle_replace(file_path, stack)

        if behavior is XymlKeyBehavior.EXTEND:
            return XymlLoader._handle_extend(node, file_path, directive_key, stack)

        raise XymlDirectiveError(f"Unknown behavior {behavior!r} for key '{directive_key}'")

    @staticmethod
    def _handle_replace(file_path: Path, stack: frozenset[Path]) -> Any:
        XymlLoader._check_file(file_path, stack)
        content = file_path.read_text(encoding="utf-8")
        node = yaml.safe_load(content)
        return XymlLoader._resolve(node, file_path.parent, stack | {file_path})

    @staticmethod
    def _handle_extend(
        current: dict[str, Any],
        file_path: Path,
        directive_key: str,
        stack: frozenset[Path],
    ) -> Any:
        XymlLoader._check_file(file_path, stack)
        content = file_path.read_text(encoding="utf-8")
        base_node = yaml.safe_load(content)
        base_resolved = XymlLoader._resolve(base_node, file_path.parent, stack | {file_path})
        siblings = {k: v for k, v in current.items() if k != directive_key}
        if not siblings:
            # No siblings: the directive is a pure include — return file content as-is.
            return base_resolved
        if not isinstance(base_resolved, dict):
            raise XymlDirectiveError(
                f"'{directive_key}' requires the referenced file to contain a mapping "
                f"when sibling keys are present; got {type(base_resolved).__name__}"
            )
        merged = {**base_resolved, **siblings}
        return {
            k: XymlLoader._resolve(v, file_path.parent, stack | {file_path})
            for k, v in merged.items()
        }

    @staticmethod
    def _check_file(file_path: Path, stack: frozenset[Path]) -> None:
        if not file_path.exists():
            raise XymlFileNotFoundError(f"File not found: {file_path}")
        if file_path in stack:
            raise XymlCircularIncludeError(
                f"Circular include detected: '{file_path}' is already on the include stack"
            )

    @staticmethod
    def _resolve_path(value: str, base_path: Path) -> Path:
        p = Path(value)
        if p.is_absolute():
            return p
        return (base_path / p).resolve()
