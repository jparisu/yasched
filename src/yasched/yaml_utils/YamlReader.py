"""
YamlKey and YamlReader classes for versatile YAML parsing.
"""

from __future__ import annotations

from typing import Any

import yaml

from yasched.yaml_utils.exceptions import YamlFormatError, YamlKeyError, YamlTypeError


class YamlKey:
    """Represents a set of alternative keys for YAML lookups.

    Allows flexible key matching - any of the keys in the set can be used
    to access the same value.

    Example:
        >>> key = YamlKey({"name", "title", "label"})
        >>> key.keys
        {'name', 'title', 'label'}
    """

    __slots__ = ("keys",)

    def __init__(self, keys: set[str]) -> None:
        """Initialize a YamlKey with a set of alternative keys.

        Args:
            keys: Set of string keys that can be used interchangeably.

        Example:
            >>> YamlKey({"name", "title"})
            YamlKey({'name', 'title'})
        """
        self.keys = keys

    def __repr__(self) -> str:
        """Return an unambiguous representation."""
        return f"YamlKey({self.keys!r})"


class YamlReader:
    """A versatile YAML reader with flexible key lookup and type checking.

    Supports:
      * Multiple alternative keys for the same value
      * Type validation
      * Default values
      * Nested YAML access via get_child
      * YAML dumping

    Example:
        >>> yaml_content = "name: John\\nage: 30"
        >>> reader = YamlReader(yaml_content)
        >>> reader.get(YamlKey({"name"}))
        'John'
    """

    def __init__(self, yaml_content: str) -> None:
        """Initialize a YamlReader from YAML string content.

        Args:
            yaml_content: String containing YAML data.

        Raises:
            YamlFormatError: If the YAML content is invalid.

        Example:
            >>> YamlReader("key: value")
            YamlReader(...)
        """
        try:
            self._yaml = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            raise YamlFormatError(f"Invalid YAML content: {e}") from e

        if self._yaml is None:
            self._yaml = {}

    @classmethod
    def from_dict(cls, yaml_dict: dict[str, Any]) -> YamlReader:
        """Create a YamlReader from a dictionary.

        Args:
            yaml_dict: Dictionary to wrap.

        Returns:
            A new YamlReader instance.

        Example:
            >>> reader = YamlReader.from_dict({"key": "value"})
            >>> reader.get(YamlKey({"key"}))
            'value'
        """
        instance = cls.__new__(cls)
        instance._yaml = yaml_dict
        return instance

    def yaml(self, value: Any) -> YamlReader:
        """Set the internal YAML data directly.

        Args:
            value: Any value to set as the YAML data.

        Returns:
            self for method chaining.

        Example:
            >>> reader = YamlReader("")
            >>> reader.yaml({"key": "value"})
            YamlReader(...)
        """
        self._yaml = value
        return self

    def has(self, key: YamlKey) -> bool:
        """Check if any of the keys in YamlKey exists in the YAML data.

        Args:
            key: YamlKey containing alternative key names.

        Returns:
            True if any key exists, False otherwise.

        Example:
            >>> reader = YamlReader("name: John")
            >>> reader.has(YamlKey({"name"}))
            True
            >>> reader.has(YamlKey({"missing"}))
            False
        """
        if not isinstance(self._yaml, dict):
            return False

        for k in key.keys:
            if k in self._yaml:
                return True
        return False

    def get(
        self,
        key: YamlKey,
        default: Any = None,
        force_type: list[type] | None = None,
        throw: bool = True,
    ) -> Any:
        """Get a value from the YAML data using flexible key matching.

        Args:
            key: YamlKey containing alternative key names.
            default: Default value if key is not found. Defaults to None.
            force_type: List of acceptable types. If provided, validates the value type.
            throw: If True, raises exception when key is not found and no default.
                   If False, returns default value.

        Returns:
            The value associated with any of the keys, or default if not found.

        Raises:
            YamlKeyError: If key is not found and throw=True and no default.
            YamlTypeError: If value type doesn't match force_type.

        Example:
            >>> reader = YamlReader("name: John\\nage: 30")
            >>> reader.get(YamlKey({"name"}))
            'John'
            >>> reader.get(YamlKey({"missing"}), default="N/A")
            'N/A'
        """
        if not isinstance(self._yaml, dict):
            if throw and default is None:
                raise YamlKeyError(f"Cannot get key from non-dict YAML: {type(self._yaml)}")
            return default

        # Try each key in order
        value = None
        found = False
        for k in key.keys:
            if k in self._yaml:
                value = self._yaml[k]
                found = True
                break

        if not found:
            if throw and default is None:
                raise YamlKeyError(f"None of the keys {key.keys} found in YAML")
            return default

        # Type validation
        if force_type is not None:
            if not any(isinstance(value, t) for t in force_type):
                raise YamlTypeError(
                    f"Value for key {key.keys} has type {type(value).__name__}, "
                    f"expected one of {[t.__name__ for t in force_type]}"
                )

        return value

    def get_child(self, key: YamlKey, default: Any = None, throw: bool = True) -> YamlReader:
        """Get a nested YAML section as a new YamlReader.

        Args:
            key: YamlKey containing alternative key names.
            default: Default value if key is not found.
            throw: If True, raises exception when key is not found and no default.

        Returns:
            A new YamlReader wrapping the nested section.

        Raises:
            YamlKeyError: If key is not found and throw=True and no default.

        Example:
            >>> reader = YamlReader("person:\\n  name: John\\n  age: 30")
            >>> child = reader.get_child(YamlKey({"person"}))
            >>> child.get(YamlKey({"name"}))
            'John'
        """
        value = self.get(key, default=default, throw=throw)
        return YamlReader.from_dict(value if isinstance(value, dict) else {})

    def dump(self) -> str:
        """Dump the YAML data back to a string.

        Returns:
            YAML string representation of the data.

        Example:
            >>> reader = YamlReader("name: John")
            >>> 'name: John' in reader.dump()
            True
        """
        return yaml.dump(self._yaml, default_flow_style=False)

    def __repr__(self) -> str:
        """Return a representation of the YamlReader."""
        return f"YamlReader({self._yaml!r})"
