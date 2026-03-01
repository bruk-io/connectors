# connectors Development Guide

## Overview

Unofficial API connectors — both a CLI tool and a distributable SDK. The domain layer is the SDK core, usable as a standalone library (`from connectors.domain import ...`).

## Architecture

Three-layer clean architecture: `presentation -> domain <- infrastructure`

- **`connectors/domain/`** — SDK core. Pure business logic, types, and operations. This layer IS the distributable SDK — keep it dependency-free and importable without presentation or infrastructure.
- **`connectors/infrastructure/`** — API adapters for unofficial APIs. HTTP clients, scrapers, auth flows. Each connector gets its own module.
- **`connectors/presentation/`** — User interfaces.
  - `cli/` — Click CLI commands.

### Layer Rules

- Domain never imports presentation
- Presentation calls domain, never infrastructure directly
- Infrastructure wraps external systems with consistent interfaces
- Prefer pure functions over classes in domain layer
- Use TypedDict for type-safe dicts (type checking at dev time, dicts at runtime)

### Adding New Operations

1. **Domain types** (`domain/types.py`): Add TypedDict if new data shape needed
2. **Domain operations** (`domain/operations.py`): Add pure function with business logic
3. **Infrastructure** (`infrastructure/client.py`): Add external system call if needed
4. **CLI** (`presentation/cli/commands.py`): Add Click command
5. **Tests** (`tests/`): Add unit tests for domain operations

## Standard Project Interface

This project implements the **standard entrypoint interface** — a set of conventional commands that work the same locally and in Docker containers (via the containers plugin).

| Command | Local | Docker |
|---------|-------|--------|
| **test** | `uv run pytest` | `docker run <img>:ci test` |
| **lint** | `uv run ruff check .` | `docker run <img>:ci lint` |
| **check** | lint + test | `docker run <img>:ci check` |

## Commands

```bash
# Install dependencies
uv sync

# Run CLI
uv run connectors --help

# Run tests
uv run pytest

# Lint
uv run ruff check .

# Format
uv run ruff format .

# Type check
uv run mypy connectors/
```

### Pre-Commit Validation

**MUST verify all pass before committing:**
```bash
uv run pytest tests/ -v
uv run mypy connectors/
uv run ruff check .
uv run ruff format --check .
```

## Testing Strategy

Three test types with clear boundaries mapped to the architecture layers:

### Unit Tests
- **Scope:** Single function in `domain/operations.py` or `domain/types.py`
- **Dependencies:** ALL mocked/stubbed — no I/O, no network, no filesystem
- **Speed:** Milliseconds per test
- **Pattern:** Test pure functions with edge cases (empty inputs, None, boundary values)
- **Location:** `tests/test_operations.py`, `tests/test_<module>.py`

### Integration Tests
- **Scope:** Multiple components interacting (e.g., CLI handler → domain → mocked infrastructure)
- **Dependencies:** External systems (APIs, DB, filesystem) are MOCKED
- **Speed:** Seconds per test
- **Pattern:** Test workflows across layer boundaries with test doubles
- **Location:** `tests/test_integration_<feature>.py`

### E2E Tests
- **Scope:** Full system through public interface (CLI commands)
- **Dependencies:** Real external systems (requires setup)
- **Speed:** Seconds to minutes
- **Pattern:** Test critical user journeys, use unique test data, clean up after
- **Location:** `tests/test_e2e_<feature>.py`

### Test Rules
- **NEVER cheat:** Don't comment out failing tests, don't mock away the functionality being tested
- Test behavior, not implementation details
- Use dependency injection for testability
- Prefer pure functions (inherently testable)
- Domain layer tests should never need I/O mocks

## Code Standards

- **Python 3.14+** required
- **uv** for package management
- **Type hints mandatory** on all functions
- **Functional over OOP** — prefer pure functions in domain layer
- **Docstrings in imperative mode**: "Create an item" not "Creates an item"
- **ruff** for linting and formatting (line length: 100)
- **mypy** in strict mode
- **pytest** for testing

## Git Workflow

- Use conventional commits: `feat:`, `fix:`, `refactor:`, `test:`, `docs:`
- Co-author with Claude: `Co-Authored-By: Claude <model> <noreply@anthropic.com>`
