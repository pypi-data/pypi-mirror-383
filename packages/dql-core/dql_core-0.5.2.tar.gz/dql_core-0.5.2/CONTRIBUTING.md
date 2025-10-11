# Contributing to dql-core

Thank you for your interest in contributing to dql-core!

## Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/dql/dql-core.git
   cd dql-core
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies:**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Install pre-commit hooks:**
   ```bash
   pip install pre-commit
   pre-commit install
   ```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=dql_core --cov-report=html

# Run specific test file
pytest tests/test_validators/test_null_validators.py -v
```

## Code Quality

```bash
# Format code with Black
black dql_core tests

# Lint with Flake8
flake8 dql_core tests

# Type check with mypy
mypy dql_core
```

## Project Structure

```
dql-core/
├── dql_core/           # Core package
│   ├── validators/     # Validator implementations
│   ├── cleaners/       # Cleaner framework
│   ├── adapters/       # External API adapters
│   ├── executor.py     # Abstract executor
│   ├── results.py      # Result dataclasses
│   └── exceptions.py   # Exception hierarchy
├── tests/              # Test suite
└── docs/               # Documentation
```

## Pull Request Process

1. Create a feature branch from `main`
2. Make your changes with tests
3. Ensure all tests pass and coverage is maintained
4. Update documentation if needed
5. Submit a pull request with a clear description

## Code Style

- Follow PEP 8 (enforced by Black and Flake8)
- Line length: 100 characters
- Use type hints for all public APIs
- Write docstrings for all public classes and methods

## Testing Guidelines

- Write unit tests for all new functionality
- Maintain test coverage >80%
- Use pytest fixtures for reusable test setup
- Mock external dependencies

## Questions?

Open an issue on GitHub if you have questions or need clarification.
