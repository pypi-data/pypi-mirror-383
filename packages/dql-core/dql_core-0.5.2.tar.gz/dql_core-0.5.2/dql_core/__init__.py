"""dql-core: Framework-agnostic validation engine for Data Quality Language (DQL)."""

__version__ = "0.1.0"

# Core executor
from dql_core.executor import ValidationExecutor

# Expression evaluator (Story 2.3)
from dql_core.evaluator import ExpressionEvaluator

# Results
from dql_core.results import (
    ValidationResult,
    ExpectationResult,
    CleanerResult,
    ValidationRunResult,
)

# Exceptions
from dql_core.exceptions import (
    DQLCoreError,
    ValidationError,
    CleanerError,
    ExecutorError,
    AdapterError,
)

# Validators
from dql_core.validators import (
    Validator,
    ValidatorRegistry,
    default_registry,
    ToBeNullValidator,
    ToNotBeNullValidator,
    ToMatchPatternValidator,
    ToBeBetweenValidator,
    ToBeInValidator,
    ToBeUniqueValidator,
)

# Cleaners
from dql_core.cleaners import (
    Cleaner,
    CleanerExecutor,
    CleanerRegistry,
    default_cleaner_registry,
    register_cleaner,
    # String cleaners (Story 2.4)
    trim_whitespace,
    uppercase,
    lowercase,
    normalize_email,
    # Data type cleaners (Story 2.5)
    strip_non_numeric,
    normalize_phone,
    coalesce,
    format_date,
    # Custom cleaner framework (Story 2.6)
    cleaner,
    validate_cleaner_signature,
    is_cleaner_function,
    CleanerChain,
    discover_cleaners,
    register_cleaners_from_directory,
    # Transaction safety (Story 2.7)
    TransactionManager,
    DictTransactionManager,
    SafeCleanerExecutor,
    CleanerAuditLog,
    AuditLogger,
)

# Adapters
from dql_core.adapters import (
    ExternalAPIAdapter,
    APIAdapterFactory,
    default_adapter_factory,
    RateLimiter,
    retry_with_backoff,
)

__all__ = [
    "__version__",
    # Executor
    "ValidationExecutor",
    # Expression Evaluator
    "ExpressionEvaluator",
    # Results
    "ValidationResult",
    "ExpectationResult",
    "CleanerResult",
    "ValidationRunResult",
    # Exceptions
    "DQLCoreError",
    "ValidationError",
    "CleanerError",
    "ExecutorError",
    "AdapterError",
    # Validators
    "Validator",
    "ValidatorRegistry",
    "default_registry",
    "ToBeNullValidator",
    "ToNotBeNullValidator",
    "ToMatchPatternValidator",
    "ToBeBetweenValidator",
    "ToBeInValidator",
    "ToBeUniqueValidator",
    # Cleaners
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
    # Adapters
    "ExternalAPIAdapter",
    "APIAdapterFactory",
    "default_adapter_factory",
    "RateLimiter",
    "retry_with_backoff",
]
