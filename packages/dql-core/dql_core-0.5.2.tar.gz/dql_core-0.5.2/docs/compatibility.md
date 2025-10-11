# Version Compatibility

## Package Compatibility Matrix

| dql-core | dql-parser | Python | Status |
|----------|------------|--------|--------|
| 0.1.0    | 0.1.0      | 3.8-3.12 | ✅ Stable |

## Dependencies

### Required

- `dql-parser>=0.1.0,<1.0.0` - DQL syntax parser

### Optional

- `requests>=2.28.0` - For external API adapters
- `tenacity>=8.0.0` - For retry logic

## Python Version Support

- **Python 3.8**: Minimum supported version
- **Python 3.9-3.12**: Fully supported and tested

## Framework Compatibility

dql-core is framework-agnostic and works with:

- **Django**: Any version (see django-dqm for integration)
- **Flask**: Any version
- **FastAPI**: Any version
- **SQLAlchemy**: 1.4+ and 2.0+
- **Peewee**: Any version
- **Pandas**: 1.0+

## Changelog

### 0.1.0 (2025-10-09)

- Initial release
- 6 built-in validators
- Abstract ValidationExecutor
- Cleaner framework
- External API adapter framework
