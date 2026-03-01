# Unit Tests

## Definition
Test a single function/module in complete isolation.

**Boundaries:**
- All external dependencies mocked/stubbed
- No I/O: no network, no file system, no database, no environment variables
- Speed: milliseconds per test
- Scope: one function/class, testing logic and edge cases

## Where They Live

`tests/test_<module>.py` — e.g., `tests/test_operations.py`

## What to Test

Primary target: **`connectors/domain/`** — pure functions, TypedDict types, business logic.

Domain functions are inherently unit-testable because they have no I/O dependencies.

```python
# connectors/domain/operations.py — pure, no I/O
def calculate_total(items: list[Item]) -> float:
    return sum(item["price"] * item["quantity"] for item in items)

# tests/test_operations.py
def test_calculate_total_empty() -> None:
    assert calculate_total([]) == 0.0

def test_calculate_total_single_item() -> None:
    items = [Item(price=10.0, quantity=2)]
    assert calculate_total(items) == 20.0
```

## Writing Testable Code

### Prefer Pure Functions
```python
# domain/operations.py — easy to unit test
def validate_input(data: str) -> bool:
    return len(data) > 0 and len(data) <= 100

# ❌ Hard to unit test — has side effects
def save_and_validate(data: str) -> None:
    if validate_input(data):
        db.save(data)  # Side effect
```

### Use Dependency Injection
```python
# ✅ Dependencies passed in, easy to mock
def process(data: dict, client: Client) -> Result:
    raw = client.fetch(data["id"])
    return transform(raw)

# ❌ Hard to test — implicit dependency
def process(data: dict) -> Result:
    raw = global_client.fetch(data["id"])
    return transform(raw)
```

### Avoid Global State
```python
# ✅ State passed explicitly
def add_item(cart: list[Item], item: Item) -> list[Item]:
    return cart + [item]

# ❌ Global state makes tests interfere with each other
CART: list[Item] = []
def add_item(item: Item) -> None:
    CART.append(item)
```

## Best Practices

- Test behavior, not implementation details
- One assertion per test (when possible)
- Use descriptive test names: `test_greet_with_empty_name_returns_default`
- Test edge cases: empty inputs, None, zero, negative numbers, boundary values
- Don't test framework code — test YOUR logic

## Anti-Patterns

- Testing private methods directly
- Brittle tests that break when refactoring
- Tests that require specific execution order
- Using real datetime/random — mock these
