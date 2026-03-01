# End-to-End (E2E) Tests

## Definition
Test the entire system through its public interface with real external dependencies.

**Boundaries:**
- Real environment with real external dependencies
- Entry point: through CLI commands or public API — not internal functions
- Slowest tests (seconds to minutes), run less frequently

## Where They Live

`tests/test_e2e_<feature>.py`

## What to Test

Test the **complete system** as users experience it:

```python
import subprocess


def test_cli_greet_produces_output() -> None:
    """Test the CLI works end-to-end."""
    result = subprocess.run(
        ["uv", "run", "connectors", "greet", "World"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Hello, World!" in result.stdout


def test_cli_status_returns_valid_json() -> None:
    """Test status command returns parseable JSON."""
    result = subprocess.run(
        ["uv", "run", "connectors", "status"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    import json
    data = json.loads(result.stdout)
    assert "name" in data
    assert "version" in data
```

## Purpose

E2E tests validate that:
- The installed package runs correctly
- CLI commands produce expected output
- Configuration is loaded correctly
- All dependencies are wired together

## Writing Testable Code

### Make Operations Idempotent Where Possible
```python
# ✅ Idempotent — safe to retry in tests
def update_config(key: str, value: str) -> Config:
    """Set a config value — same result if called twice."""
    ...

# ❌ Non-idempotent — hard to test reliably
def increment_counter(key: str) -> int:
    """Each call changes state — retries cause problems."""
    ...
```

### Use Unique Test Data
```python
from uuid import uuid4

def test_create_resource() -> None:
    unique_name = f"test-{uuid4().hex[:8]}"
    # Create with unique name to avoid conflicts
    # Clean up after test
```

## Best Practices

- Test critical user journeys end-to-end
- Use unique test data (UUIDs, timestamps) to avoid conflicts
- Clean up test data after tests run
- Focus on happy paths and critical error scenarios
- Verify infrastructure/deployment, not business logic details
- Keep E2E tests focused — don't test every edge case here

## Anti-Patterns

- Testing business logic details (that's unit/integration)
- Not cleaning up test data
- Testing through internal functions instead of public interface
- Too many E2E tests (slow and expensive)
- Flaky tests that fail intermittently due to timing
