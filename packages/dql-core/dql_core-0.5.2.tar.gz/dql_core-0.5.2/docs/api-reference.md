# API Reference

Complete API documentation for dql-core.

## ValidationExecutor

::: dql_core.ValidationExecutor

## Validators

::: dql_core.Validator
::: dql_core.ValidatorRegistry
::: dql_core.ToBeNullValidator
::: dql_core.ToNotBeNullValidator
::: dql_core.ToMatchPatternValidator
::: dql_core.ToBeBetweenValidator
::: dql_core.ToBeInValidator
::: dql_core.ToBeUniqueValidator

## Cleaners

::: dql_core.CleanerExecutor
::: dql_core.CleanerRegistry
::: dql_core.register_cleaner

## Results

::: dql_core.ValidationRunResult
::: dql_core.ExpectationResult
::: dql_core.ValidationResult
::: dql_core.CleanerResult

## Adapters

::: dql_core.APIAdapter
::: dql_core.APIAdapterFactory
::: dql_core.RateLimiter
::: dql_core.retry_with_backoff

## Exceptions

::: dql_core.DQLCoreError
::: dql_core.ValidatorNotFoundError
::: dql_core.CleanerNotFoundError
::: dql_core.AdapterNotFoundError
::: dql_core.ValidationExecutionError
