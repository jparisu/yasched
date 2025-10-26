"""
Custom exceptions for YAML reading and parsing.
"""


class YamlFormatError(ValueError):
    """Raised when YAML content has an incorrect format."""

    pass


class YamlKeyError(KeyError):
    """Raised when a required YAML key is not found."""

    pass


class YamlTypeError(TypeError):
    """Raised when a YAML value has an incorrect type."""

    pass
