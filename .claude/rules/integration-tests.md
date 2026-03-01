# Integration Tests

## Definition
Test how multiple components/modules within the codebase work together.

**Boundaries:**
- Multiple modules/components interacting
- External dependencies (DB, APIs, filesystem) are MOCKED
- Tests your architecture and component design
- Faster than E2E, slower than unit tests (seconds)

## Where They Live

`tests/test_integration_<feature>.py`

## What to Test

Test the **seams between layers** in the three-layer architecture:

- **presentation → domain**: CLI commands or MCP tools calling domain operations
- **domain → infrastructure**: Domain operations calling infrastructure (with mocked externals)

```python
# Test CLI handler → domain integration (mock infrastructure)
from unittest.mock import patch
from click.testing import CliRunner

from connectors.presentation.cli.commands import cli


def test_status_command_outputs_json() -> None:
    """Test CLI status command integrates with domain operations."""
    runner = CliRunner()
    result = runner.invoke(cli, ["status"])
    assert result.exit_code == 0
    assert "connectors" in result.output


@patch("connectors.infrastructure.client.get")
def test_domain_uses_infrastructure(mock_get) -> None:
    """Test domain calls infrastructure correctly."""
    mock_get.return_value = {"resource": "test", "data": {"key": "value"}}
    # Call domain function that uses infrastructure
    # Verify the interaction between layers
```

## Architecture Mapping

| Integration Test | Layers Tested | What's Mocked |
|-----------------|---------------|---------------|
| CLI → domain | presentation + domain | infrastructure |
| domain → infrastructure | domain + infrastructure | external systems |

## Writing Testable Code

### Define Clear Layer Interfaces
```python
# ✅ Clear interface between layers
# infrastructure/client.py
def get(resource: str) -> dict:
    """Fetch from external system."""
    ...

# domain/operations.py
from connectors.infrastructure import client

def get_resource(name: str) -> Resource:
    raw = client.get(name)
    return transform(raw)

# Integration test: real domain + mocked infrastructure
```

### Use Dependency Injection
```python
# ✅ Dependencies injected, easy to swap for testing
def process(data: dict, fetcher: Callable[[str], dict]) -> Result:
    raw = fetcher(data["id"])
    return Result(**raw)

# Test with mock fetcher
def test_process_transforms_data() -> None:
    mock_fetcher = lambda id: {"name": "test", "status": "ok"}
    result = process({"id": "123"}, mock_fetcher)
    assert result.name == "test"
```

## Best Practices

- Test workflows across component boundaries
- Mock external services at the boundary (use test doubles)
- Focus on testing the "seams" between modules
- Test error propagation across components
- Verify contracts between components are honored

## Anti-Patterns

- Testing with real databases/APIs (that's E2E)
- Testing too many components at once (unclear what broke)
- Duplicating unit test coverage
- Not testing error conditions between components
