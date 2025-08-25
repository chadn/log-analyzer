# AI Agent Project Template Guide

This file provides project-level guidance to AI LLMs (Cursor, Claude Code, GitHub Copilot, etc.) when working with code in this repository.

This template is designed to work with both Node.js/TypeScript and Python projects. Customize the sections below for your specific project needs.

## Setup Instructions

**REMOVE THIS SECTION** after customizing for your project.

Based on community best practices from https://ampcode.com/AGENT.md

Create symbolic links for AI tool compatibility:

```bash
cp ~/.config/AGENT.project-template.md AGENT.md
ln -s AGENT.md CLAUDE.md
ln -s AGENT.md .cursorrules
ln -s ../../AGENT.md .github/instructions/[name].instructions.md  # Github Copilot
```

## Project Overview

**[CUSTOMIZE THIS SECTION]**

Brief description of project purpose, architecture, and key technologies. Reference README.md for complete details.

If node project, below delete Python Projects  
If python, below delete Node Projects

## General Project Preferences

Use the following for python projects, node projects (javascript or typescript), etc.

### CI/CD

-   Create `.github/workflows/ci.yml` for GitHub Actions CI/CD.
-   CI must run: lint, type check, tests, coverage.
-   CI must fail if coverage < 85% (default; adjust as needed).
-   Cache dependencies in CI to speed up builds.
-   Run dependency audit in CI (`pip-audit` for Python, `npm audit` for Node).

### Config and Secrets

-   Use `.env.example` to document required settings with dummy values.
-   Never commit `.env`.
-   Load `.env` **only in local development**, never in CI or production.
-   In CI/prod, rely on injected environment variables.

### Versioning

-   Semantic versioning with `CHANGELOG.md`.
-   Use Conventional Commits or similar to automate changelog if possible.
-   Tag releases in git to align with semver and changelog entries.

### Testing

-   Always add tests for new functionality.
-   All new code must include at least one **fast (<1s) unit test**; add integration/E2E tests if relevant.
-   Apply the testing pyramid: balance unit, integration, and end-to-end tests.
-   Mock external dependencies appropriately: stub/mocks for APIs, containers for heavier services.
-   Consider property-based testing for critical logic.
-   Structure tests to mirror application code and keep them in dedicated folders.

### Security

-   Never commit secrets or API keys.
-   Use environment variables for sensitive data.
-   Validate all user inputs on both client and server.
-   Follow the principle of least privilege.
-   Enable pre-commit hooks to catch issues before commit (lint, type checks, audit).
-   Use secret-scanning (e.g., detect-secrets).
-   Dependencies must be pinned in lockfiles (`uv.lock`, `package-lock.json`, etc.); review drift in PRs.

### Logging and Errors

-   Use structured logging (JSON or equivalent).
-   Never swallow exceptions; always log with context.

### Dependencies

-   Avoid unnecessary dependencies; prefer stdlib / core libraries first.
-   Justify adding external packages.

## Python Projects

### Python Environment and Dependencies

-   Use `uv` to manage environments and dependencies.
-   Prefer a single `pyproject.toml` to configure everything (Ruff, pytest, coverage, mypy, build).

```toml
[project]
dependencies = ["fastapi", "pydantic"]

[project.optional-dependencies]
dev = ["pytest", "mypy", "ruff", "coverage", "pre-commit"]
```

-   Commit `pyproject.toml` and `uv.lock`.
-   Only commit `requirements.txt` if infrastructure requires it (generate with `uv pip compile`, not `uv pip freeze`).

### Python Makefile

Use a Makefile for common workflows. All commands run via `uv run` for cross-platform safety (Linux/Windows/CI).

```make
DEFAULT_GOAL := help

.PHONY: init deps lint format fix-format type test serve reqs check ci clean hooks

help: ## Show available targets
	@awk 'BEGIN {FS:=":.*##"; printf "\nTargets:\n"} /^[a-zA-Z_-]+:.*##/ {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

init: ## Create venv and install dev dependencies
	uv venv .venv
	uv pip install -e ".[dev]"

deps: ## Reinstall dev dependencies (no new venv)
	uv pip install -e ".[dev]"

lint: ## Run lint checks
	uv run ruff check .

format: ## Verify formatting
	uv run ruff format --check .

fix-format: ## Auto-fix formatting
	uv run ruff format .

type: ## Type-check with mypy
	uv run mypy .

test: ## Run tests (pass extra flags via ARGS='...')
	uv run pytest -q $(ARGS)

serve: ## Run app locally with hot reload, with APP_DEBUG env overide
	APP_DEBUG=true uv run uvicorn package_name.api:app --reload --port 8000

reqs: ## Generate requirements.txt from pyproject (legacy tools only)
	uv pip compile pyproject.toml -o requirements.txt

check: format lint type test ## Run all local checks

ci: check ## Run checks + coverage (CI gate)
	uv run coverage run -m pytest -q
	uv run coverage report --fail-under=85

clean: ## Remove caches and build artifacts
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage dist build

hooks: ## Install pre-commit hooks
	uv run pre-commit install
```

### Python Typing and Linting

-   Use [Ruff](https://github.com/astral-sh/ruff) for linting **and** formatting.
-   Ruff enforces most of PEP8 + formatting; no need to run Black separately.
-   Use Google-style docstrings; enforce with Ruff `D` rules.
-   Pyright → editor feedback (fast, incremental).
-   Mypy (+ plugins) → CI precision, especially for larger projects or where Pydantic/SQLAlchemy integration matters.
-   Optional: Pydantic for runtime validation where API/IO boundaries exist.

### Python Testing

-   Use pytest.
-   Apply the testing pyramid: balance unit, integration, and end-to-end tests.
-   Structure tests to mirror application code.
-   Use pytest fixtures for data, test doubles, and setup.
-   Use pytest markers for categories (no need if entire test suite finishes in <1s).
-   Keep integration tests hermetic with `pytest-docker` or `testcontainers`.

### Python Config

-   Use `python-dotenv` for local dev.
-   Use Pydantic Settings v2 to unify env/config.
-   Guidelines for data models:
    -   Use Pydantic at boundaries (config, request/response, parsing external data).
    -   Use `dataclasses` or `attrs` for plain in-memory models (lighter, faster).
    -   Use `msgspec` for hot (de)serialization paths where performance is critical.

### Python Docs

-   Small projects → README only may be enough.
-   For team projects, always include a **Quickstart** in README or `docs/`.
-   Use ADRs (Architecture Decision Records) for major design choices (lightweight, Markdown, numbered, e.g. MADR template).
-   Basic API docs → `pdoc` (auto-generated from docstrings).
-   Advanced docs → MkDocs Material (team sites, guides, versioned docs, search).

### Python Code Style

-   4 spaces indentation.
-   88 character line limit (Black standard).
-   Type hints required.
-   Follow PEP 8.
-   Enforce via Ruff and CI.

## Node Projects

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run lint         # Run linter
npm test             # Run tests
```

### Code style for TypeScript/JavaScript

-   2 spaces indentation
-   120 character line limit
-   Single quotes, no semicolons, trailing commas
-   Use TypeScript strict mode
-   NEVER use `@ts-ignore` without strong justification
-   Use JSDoc docstrings for documenting TypeScript definitions, not `//` comments
-   Imports: Use consistent-type-imports
-   Prefer functional programming patterns
-   Use TypeScript interfaces for public APIs

### Testing

-   **Node.js**: Use Vitest(preferred) or Jest for unit tests; Playwright for E2E

## Project-Specific Notes

**[CUSTOMIZE THIS SECTION]**

Add project-specific patterns, libraries, or conventions that AI agents should follow.
