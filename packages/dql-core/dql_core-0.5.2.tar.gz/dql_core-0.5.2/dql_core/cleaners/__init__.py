"""Cleaner framework for DQL."""

from dql_core.cleaners.base import Cleaner, CleanerExecutor
from dql_core.cleaners.registry import CleanerRegistry, default_cleaner_registry
from dql_core.cleaners.decorators import register_cleaner, cleaner
from dql_core.cleaners.string_cleaners import (
    trim_whitespace,
    uppercase,
    lowercase,
    normalize_email,
)
from dql_core.cleaners.data_type_cleaners import (
    strip_non_numeric,
    normalize_phone,
    coalesce,
    format_date,
)
# Story 2.6: Custom cleaner framework
from dql_core.cleaners.validation import validate_cleaner_signature, is_cleaner_function
from dql_core.cleaners.chain import CleanerChain
from dql_core.cleaners.discovery import discover_cleaners, register_cleaners_from_directory
# Story 2.7: Transaction safety
from dql_core.cleaners.transaction import (
    TransactionManager,
    DictTransactionManager,
    SafeCleanerExecutor,
)
from dql_core.cleaners.audit import CleanerAuditLog, AuditLogger

__all__ = [
    "Cleaner",
    "CleanerExecutor",
    "CleanerRegistry",
    "default_cleaner_registry",
    "register_cleaner",
    # String cleaners (Story 2.4)
    "trim_whitespace",
    "uppercase",
    "lowercase",
    "normalize_email",
    # Data type cleaners (Story 2.5)
    "strip_non_numeric",
    "normalize_phone",
    "coalesce",
    "format_date",
    # Custom cleaner framework (Story 2.6)
    "cleaner",
    "validate_cleaner_signature",
    "is_cleaner_function",
    "CleanerChain",
    "discover_cleaners",
    "register_cleaners_from_directory",
    # Transaction safety (Story 2.7)
    "TransactionManager",
    "DictTransactionManager",
    "SafeCleanerExecutor",
    "CleanerAuditLog",
    "AuditLogger",
]
