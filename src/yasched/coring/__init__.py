"""Core domain data holders for the unified element model.

Plain data holders parsed from the configuration. They do not resolve
references, apply inheritance, or generate auto-elements — that is
``backending``'s job. ``coring`` imports ``utilizing`` only.
"""

from yasched.coring.AttributeDefinition import (
    NON_INHERITING,
    AttributeDefinition,
    ValueType,
    builtin_definitions,
)
from yasched.coring.Connection import Connection
from yasched.coring.Element import Element
from yasched.coring.ElementType import ElementType
from yasched.coring.Layout import Background, Border, Format, Icon, Layout, Pin

__all__ = [
    "ElementType",
    "Element",
    "Connection",
    "AttributeDefinition",
    "ValueType",
    "builtin_definitions",
    "NON_INHERITING",
    "Layout",
    "Background",
    "Border",
    "Icon",
    "Pin",
    "Format",
]
