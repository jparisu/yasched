"""Loading, resolution, and generation for the v4 element model.

``backending`` imports ``coring`` and ``utilizing``. It parses (x)yml documents
into a :class:`Database`, resolves the inheritance model into effective values,
generates auto-elements (schedules/deadlines/reminders), and validates.
"""

from yasched.backending.Database import ALL_TOPIC_ID, Database
from yasched.backending.generating.Generator import Generator
from yasched.backending.loading.ElementLoader import DatabaseLoadError, ElementLoader
from yasched.backending.loading.ElementSerializer import ElementSerializer
from yasched.backending.resolving.Resolver import ResolvedElement, Resolver
from yasched.backending.validating.Validator import Issue, Severity, Validator, validate_database

__all__ = [
    "Database",
    "ALL_TOPIC_ID",
    "ElementLoader",
    "DatabaseLoadError",
    "ElementSerializer",
    "Resolver",
    "ResolvedElement",
    "Generator",
    "Validator",
    "Issue",
    "Severity",
    "validate_database",
]
