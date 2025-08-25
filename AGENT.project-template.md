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

-   Consider creating `.github/workflows/ci.yml` for GitHub actions CI/CD
    -   CI must run lint, type check, tests, coverage
-   Config and secrets: Keep a `.env.example` and load only in dev.
-   Versioning: semver + CHANGELOG.md
-   Always add tests for new functionality
-   Mock external dependencies appropriately
-   Security
    -   Never commit secrets or API keys to repository
    -   Use environment variables for sensitive data
    -   Validate all user inputs on both client and server
    -   Follow principle of least privilege

## Python Projects

-   Environment and dependencies
    -   Use uv to manage environments & dependencies
    -   Prefer one pyproject.toml to configure everything (Ruff, pytest, coverage, mypy, build). ex:

```
[project]
dependencies = ["fastapi", "pydantic"]

[project.optional-dependencies]
dev = ["pytest", "mypy", "ruff", "coverage", "pre-commit"]
```

-   use Makefile to make it easier. Uses `uv run xxx` to run on linux or windows, and in CI. Ex:

```
DEFAULT_GOAL := help

.PHONY: init deps lint format type test check ci

help: ## Show available targets
   @awk 'BEGIN {FS:=":.*##"; printf "\nTargets:\n"} /^[a-zA-Z_-]+:.*##/ {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)


init: ## Create venv and install dev dependencies
   uv venv .venv
   uv pip install -e ".[dev]"

deps: ## Reinstall dev dependencies (no new venv)
   uv pip install -e ".[dev]"

lint:
   uv run ruff check .

format: ## Verify formatting
	uv run ruff format --check .

fix-format: ## Auto-fix formatting
	uv run ruff format .

type:
   uv run mypy .

test: ## Run tests (pass extra flags via ARGS='...')
   uv run pytest -q $(ARGS)

serve: ## Run app locally with hot reload, with APP_DEBUG env overide
	APP_DEBUG=true uv run uvicorn package_name.api:app --reload --port 8000

reqs: ## Generate requirements.txt from pyproject - use only for legacy tools when needed
   uv pip compile pyproject.toml -o requirements.txt

check: format lint type test

ci: check
   uv run coverage run -m pytest -q
   uv run coverage report --fail-under=85

clean: ## Remove caches and build artifacts
   rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage dist build
```

-   commmit pyproject.toml and uv.lock, only commit requirements.txt if infrastructure requires it.
-   Typing and Linting
    -   use [Ruff](https://github.com/astral-sh/ruff) for formatting AND linting code
    -   Ruff enforces most of PEP8 + formatting, no need to run Black separately.
    -   Use docstrings in Google style, enforced by Ruff D rules.
    -   Optional: pydantic for runtime validation where API/IO boundaries exist.
    -   use pyright for basic or simple projects, OR use mypy + plugins for CI, advanced, or larger projects (FastAPI/Pydantic/SQLAlchemy heavily) or for CI precision
-   use pytest for testing code
    -   Leverage the testing pyramid to effectively balance unit, integration, and end-to-end tests.
    -   Structure your tests to mirror application code and separate them cleanly in dedicated folders.
    -   Maximize Pytest’s flexibility to organize fixtures, manage test data, and control scope with conftest.py.
    -   use pytest fixtures to provide data, test doubles, or state setup to tests
    -   use pytest markers to categorize tests if need be (not needed if only a small number of tests that can execute in <1sec)
    -   Keep integration tests hermetic with pytest-docker or testcontainers when services are needed.
    -   All new code must have at least one unit test; integration/E2E if relevant.
-   default to using pydantic, but consider alternatives https://developer-service.blog/beyond-pydantic-7-game-changing-libraries-for-python-data-handling/
    -   Use pydantic at boundaries (config, request/response, parsing external data), not inside your app’s core/domain.
    -   Prefer dataclasses or attrs for plain in-memory models (lighter, faster, fewer imports).
    -   For hot (de)serialization paths needing speed, consider msgspec.
-   Security: `uv export | pip-audit -r -` for dependency CVEs
    -   Enable pre-commit hooks (ruff, mypy, pip-audit) to catch issues before commit.
    -   Detect-secrets or similar to scan for accidental secrets.
-   Docs
    -   small projects may need no docs, README only is enough; pdoc/MkDocs optional.
    -   Suggest ADRs for architecture decisions (lightweight, Markdown, numbered).
    -   For basic API docs, use pdoc → Minimal, auto-generated API docs from code/docstrings with near-zero config. Great for libraries and internal packages when you just want “read the code, but nicer”.
    -   For advanced docs, use MkDocs Material → Team docs sites, hand-written guides + API refs, pretty theme, navigation, search, versioned docs, plugins. Great for product-y repos and onboarding.
-   code style
    -   4 spaces indentation
    -   88 character line limit (Black standard)
    -   Type hints required
    -   Follow PEP 8

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
