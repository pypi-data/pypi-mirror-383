"""Validators for DQL operators."""

from dql_core.validators.base import Validator
from dql_core.validators.registry import ValidatorRegistry, default_registry
from dql_core.validators.null_validators import ToBeNullValidator, ToNotBeNullValidator
from dql_core.validators.pattern_validators import ToMatchPatternValidator
from dql_core.validators.range_validators import ToBeBetweenValidator
from dql_core.validators.enum_validators import ToBeInValidator
from dql_core.validators.uniqueness_validators import ToBeUniqueValidator
# Story 2.1: Advanced operators
from dql_core.validators.length_validators import ToHaveLengthValidator
from dql_core.validators.comparison_validators import (
    ToBeGreaterThanValidator,
    ToBeLessThanValidator,
)
from dql_core.validators.custom_validators import ToSatisfyValidator
# Story 2.2: Foreign key validation
from dql_core.validators.reference_validators import ToReferenceValidator

__all__ = [
    "Validator",
    "ValidatorRegistry",
    "default_registry",
    "ToBeNullValidator",
    "ToNotBeNullValidator",
    "ToMatchPatternValidator",
    "ToBeBetweenValidator",
    "ToBeInValidator",
    "ToBeUniqueValidator",
    # Story 2.1
    "ToHaveLengthValidator",
    "ToBeGreaterThanValidator",
    "ToBeLessThanValidator",
    "ToSatisfyValidator",
    # Story 2.2
    "ToReferenceValidator",
]

# Register default validators
default_registry.register("to_be_null", ToBeNullValidator)
default_registry.register("to_not_be_null", ToNotBeNullValidator)
default_registry.register("to_match_pattern", ToMatchPatternValidator)
default_registry.register("to_be_between", ToBeBetweenValidator)
default_registry.register("to_be_in", ToBeInValidator)
default_registry.register("to_be_unique", ToBeUniqueValidator)
# Story 2.1: Advanced operators
default_registry.register("to_have_length", ToHaveLengthValidator)
default_registry.register("to_be_greater_than", ToBeGreaterThanValidator)
default_registry.register("to_be_less_than", ToBeLessThanValidator)
default_registry.register("to_satisfy", ToSatisfyValidator)
# Story 2.2: Foreign key validation
default_registry.register("to_reference", ToReferenceValidator)
