# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-10-09

### Added
- Initial release of dql-core
- Abstract `ValidationExecutor` class for framework-agnostic validation
- Abstract `Validator` base class with 6 built-in validators:
  - `ToBeNullValidator`
  - `ToNotBeNullValidator`
  - `ToMatchPatternValidator`
  - `ToBeBetweenValidator`
  - `ToBeInValidator`
  - `ToBeUniqueValidator`
- `ValidatorRegistry` for registering and looking up validators
- Abstract `CleanerExecutor` with transaction management template
- `CleanerRegistry` and `@register_cleaner` decorator
- Abstract `ExternalAPIAdapter` base class
- `APIAdapterFactory` for creating adapters
- Rate limiting and retry utilities for external APIs
- Result dataclasses: `ValidationResult`, `ExpectationResult`, `CleanerResult`, `ValidationRunResult`
- Exception hierarchy: `DQLCoreError`, `ValidationError`, `CleanerError`, `ExecutorError`, `AdapterError`
- Comprehensive test suite with >80% coverage
- Documentation guides for validators, cleaners, executors, and extensions
