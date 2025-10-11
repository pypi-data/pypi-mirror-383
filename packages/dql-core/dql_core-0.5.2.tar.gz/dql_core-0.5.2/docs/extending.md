# Extending dql-core

External API adapters, rate limiting, and retry patterns.

## APIAdapter

Abstract base class for calling external APIs during validation.

```python
from dql_core import APIAdapter

class MyAPIAdapter(APIAdapter):
    def call(self, **kwargs) -> dict:
        """Call external API."""
        import requests
        response = requests.post(
            "https://api.example.com/validate",
            json=kwargs
        )
        return response.json()
```

## APIAdapterFactory

Register and create adapters:

```python
from dql_core import APIAdapterFactory

factory = APIAdapterFactory()
factory.register("email_validator", EmailValidatorAdapter)
factory.register("address_checker", AddressCheckerAdapter)

# Create adapter
adapter = factory.create("email_validator")
result = adapter.call(email="test@example.com")
```

## Rate Limiting

Prevent API rate limit violations:

```python
from dql_core import RateLimiter

limiter = RateLimiter(calls_per_second=10)

for record in records:
    limiter.acquire()  # Blocks if rate exceeded
    result = api.call(data=record)
```

## Retry Logic

Exponential backoff for transient failures:

```python
from dql_core import retry_with_backoff

@retry_with_backoff(max_retries=3, base_delay=1.0, max_delay=10.0)
def call_api(data):
    return requests.post("https://api.example.com", json=data)
```

## Complete Example

```python
from dql_core import APIAdapter, APIAdapterFactory, RateLimiter, retry_with_backoff
import requests

class EmailValidatorAdapter(APIAdapter):
    def __init__(self):
        self.rate_limiter = RateLimiter(calls_per_second=5)

    @retry_with_backoff(max_retries=3)
    def call(self, **kwargs) -> dict:
        self.rate_limiter.acquire()

        response = requests.post(
            "https://api.emailvalidation.com/check",
            json=kwargs
        )
        return response.json()

# Register
factory = APIAdapterFactory()
factory.register("email_validator", EmailValidatorAdapter)

# Use in validator
class ExternalEmailValidator(Validator):
    def __init__(self, factory):
        self.adapter = factory.create("email_validator")

    def validate(self, records, expectation, executor):
        for record in records:
            email = executor.get_field_value(record, "email")
            result = self.adapter.call(email=email)
            if not result["valid"]:
                # Mark as failed
                pass
```

## Next Steps

- **[API Reference](api-reference.md)** - Complete API documentation
