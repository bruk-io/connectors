# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Unofficial API connectors — both a CLI tool and a distributable SDK. The domain layer is the SDK core, usable as a standalone library (`from connectors.domain import ...`).

## Commands

```bash
uv sync                          # Install dependencies
uv run connectors --help         # Run CLI
uv run pytest                    # Run all tests
uv run pytest tests/test_foo.py  # Run one test file
uv run pytest -k test_name       # Run a single test by name
uv run mypy connectors/          # Type check
uv run ruff check .              # Lint
uv run ruff format .             # Format
```

### Pre-Commit Validation

**MUST verify all pass before committing:**
```bash
uv run pytest tests/ -v
uv run mypy connectors/
uv run ruff check .
uv run ruff format --check .
```

## Architecture

Three-layer clean architecture: `presentation -> domain <- infrastructure`

- **`connectors/domain/`** — SDK core. Pure business logic, types, and operations. Each connector gets its own subdirectory (`domain/<connector>/`). This layer IS the distributable SDK — keep it dependency-free and importable without presentation or infrastructure.
- **`connectors/infrastructure/`** — API adapters for unofficial APIs. HTTP clients, scrapers, auth flows. Each connector gets its own module.
- **`connectors/presentation/cli/`** — Click CLI commands. All commands live in `commands.py`.
- **`connectors/browser_auth/`** — Shared library for extracting cookies from local browsers (Arc by default) and creating authenticated `httpx` sessions. Used by infrastructure layer, not domain.

### Layer Rules

- Domain NEVER imports presentation or infrastructure
- Presentation calls domain, never infrastructure directly (except for infra-only commands like Google Keep's `list-notes`)
- Infrastructure wraps external systems with consistent interfaces
- Prefer pure functions over classes in domain layer
- Use TypedDict for type-safe dicts (type checking at dev time, dicts at runtime)

### Two Connector Patterns

**"Dumb client" (Serious Eats, Bon Appetit, NYT Cooking):** Domain only validates URLs. Infrastructure uses `fetch_authenticated` from `infrastructure/browser.py` to fetch raw HTML with Arc browser cookies. No custom infra module needed.

**Custom infra (ChefSteps, Google Keep):** Domain validates input + defines types. Infrastructure has a dedicated module (`infrastructure/chefsteps.py`, `infrastructure/google_keep.py`) with connector-specific API logic.

### Adding a New Connector

1. **Domain** — Create `domain/<connector>/` with `types.py`, `operations.py`, `__init__.py`. Operations are pure functions (URL validation, slug extraction, etc).
2. **Infrastructure** — Use `infrastructure/browser.py:fetch_authenticated` for dumb clients, or create `infrastructure/<connector>.py` for custom APIs.
3. **CLI** — Add a `@cli.group("<connector>")` with subcommands in `presentation/cli/commands.py`. Use lazy imports inside command functions.
4. **Tests** — Add `tests/test_<connector>.py` with unit tests for domain operations.

## Testing Strategy

Three test types mapped to architecture layers (detailed rules in `.claude/rules/`):

- **Unit** (`tests/test_<module>.py`): Single domain function, all deps mocked, milliseconds
- **Integration** (`tests/test_integration_<feature>.py`): Cross-layer workflows, external deps mocked
- **E2E** (`tests/test_e2e_<feature>.py`): Full CLI commands against real systems

**NEVER cheat:** Don't comment out failing tests, don't mock away the functionality being tested.

## Code Standards

- **Python 3.14+**, **uv** for package management
- **Type hints mandatory** on all functions
- **Functional over OOP** — prefer pure functions in domain layer
- **Docstrings in imperative mode**: "Create an item" not "Creates an item"
- **ruff** for linting and formatting (line length: 100)
- **mypy** in strict mode

## Git Workflow

- Conventional commits: `feat:`, `fix:`, `refactor:`, `test:`, `docs:`
- Co-author with Claude: `Co-Authored-By: Claude <model> <noreply@anthropic.com>`
