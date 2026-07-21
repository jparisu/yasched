"""Loading and resolution: turn a configuration into resolved, schedulable data.

``backending`` imports ``coring`` and ``utilizing``. It parses xyml documents
into a :class:`Database`, resolves inheritance/traits/merges into effective
values, and expands schedules into concrete occurrences.
"""

from yasched.backending.Database import Database
from yasched.backending.loading.DatabaseLoader import DatabaseLoader
from yasched.backending.loading.DatabaseSerializer import DatabaseSerializer
from yasched.backending.resolving.Resolver import Resolved, Resolver
from yasched.backending.scheduling.Occurrences import Occurrence, build_event_occurrences
from yasched.backending.validating.Validator import Issue, Severity, Validator, validate_database

__all__ = [
    "Database",
    "DatabaseLoader",
    "DatabaseSerializer",
    "Resolver",
    "Resolved",
    "Occurrence",
    "build_event_occurrences",
    "Validator",
    "Issue",
    "Severity",
    "validate_database",
]
