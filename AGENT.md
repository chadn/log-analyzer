# AI Agent Project Template Guide

This file provides project-level guidance to AI LLMs (Cursor, Claude Code, GitHub Copilot, etc.) when working with code in this repository.
The goal is guidance, recommending a solutioin when more than one common solution exists - no need to specify details if there's just one solution.
Everything here is a recommendation, should only deviate when good reason and user approves.

Also follow the user level guidelines in ~/.config/AGENT.md

# Project Overview

This is a simple project that enables user to add log files to logs/ folder, then run app `make serve`, and see key stats.

# General Project Preferences

## Documenation and markdown

-   All documentation should be created and updated in a way that is easy to maintain
-   Major Decisions should be documented in ADRs - https://adr.github.io/madr/examples.html
-  Evaluate each document against these criteria (in priority order):
   [1] Up to date - verify content matches current folders, files, and commands
   [2] Clear and well-organized - logical flow and structure
   [3] Follows best practices:
       - README.md in root directory
       - Decision records follow MADR template (keeping it concise)
   [4] Concise - apply "Less is More" philosophy, stay high-level
   [5] Cross-references - broken internal links between docs
   [6] Code examples - are they current and functional
   [7] Consistent - flag discrepancies for user clarification
   [8] Not overengineered - avoid excessive future plans/goals
   [9] Properly formatted - TOCs, links, bullets, bold/italics


## CI/CD

-   Create `.github/workflows/ci.yml` for GitHub Actions CI/CD.
-   **Strict gates**: CI must run and **fail** on: lint, type check, tests, coverage (<85%), and **security audit**.
-   **Cache uv + tests**: cache the uv directory and pytest cache keyed on `pyproject.toml` and `uv.lock` hashes.
    ```yaml
    - uses: actions/cache@v4
      with:
          path: |
              ~/.cache/uv
              .pytest_cache
          key: ${{ runner.os }}-uv-${{ hashFiles('pyproject.toml', 'uv.lock') }}
    ```
-   Run dependency audit in CI (`pip-audit` for Python, `npm audit` for Node).
-   Example CI steps (Python):
    ```yaml
    - uses: astral-sh/setup-uv@v3
    - run: uv venv .venv && uv pip install -e ".[dev]"
    - run: uv run ruff format --check . && uv run ruff check .
    - run: uv run mypy .
    - run: uv run coverage run -m pytest -q
    - run: uv run coverage report --fail-under=85
    - run: uv export | pip-audit -r -
    ```

## Release Automation

-   **Tags drive releases**: tagging `vX.Y.Z` triggers publishing (package/image) and changelog update.
-   Use **Conventional Commits** to auto-generate release notes and bump versions.
-   Use GitHub Actions to publish to PyPI / GHCR (or your registry).

## Config and Secrets

-   Use `.env.example` to document required settings with dummy values.
-   **Never commit `.env`**.
-   Load `.env` **only in local development**; not in CI or production.
-   In CI/prod, rely on injected env vars / secret managers.

## Versioning

-   Use **SemVer** with `CHANGELOG.md`.
-   Tag releases to align with semver and changelog.

## Testing

-   Every feature requires tests.
-   Unit tests should be **fast (<1s)**; add integration/E2E when relevant.
-   Apply the **testing pyramid**; mock external APIs in unit tests; prefer **testcontainers/pytest-docker** for integration.
-   Consider **property-based tests** (Hypothesis) for tricky logic.
-   Mirror application structure in `tests/`.

## Security

-   Never commit secrets or API keys.
-   Validate all user inputs on client and server.
-   Least-privilege access throughout.
-   Pre-commit hooks (lint, type, audit) and **secret scanning** (e.g., detect-secrets).
-   Pin dependencies with lockfiles (`uv.lock`, `package-lock.json`) and review drift in PRs.

## Logging & Errors

-   Use **structured logging** (JSON) and include correlation/request IDs.
-   Don’t swallow exceptions; log with context.

## Dependencies

-   Prefer stdlib; justify external packages.
-   Use stable versions; avoid short-lived dev releases.

## Troubleshooting

-   If a dependency misbehaves, confirm the **installed version** and read that version’s docs.

---

# Python Projects

## Python Environment & Dependencies

-   Use `uv` for environments and deps.
-   Configure all tools in **`pyproject.toml`** (Ruff, pytest, coverage, mypy, build).
    ```toml
    [project]
    dependencies = ["fastapi", "pydantic"]
    [project.optional-dependencies]
    dev = ["pytest", "mypy", "ruff", "coverage", "pre-commit"]
    ```
-   Commit `pyproject.toml` and `uv.lock`.
-   Only commit `requirements.txt` when legacy infra needs it (generate with `uv pip compile`, not `freeze`).
-   Create `.gitignore` based off of https://github.com/chadn/ai-chatbot-meetings/blob/main/.gitignore
-   For ASGI Runtime, use uvicorn in dev, and gunicorn in prod.
-   Pre-commit hooks: Use `ruff` + `detect-secrets` + `mypy` (not `black` + `flake8` + `isort`).

## Makefile

cross-platform (linux, windows) with `uv run`

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

## Python Typing and Linting

-   Use **Ruff** for lint + format (no separate Black needed).
-   **Docstrings**: Google style; enforce with Ruff `D` rules.
-   **Mypy “strict-ish”** for CI precision:
    ```toml
    [tool.mypy]
    python_version = "3.12"
    disallow_untyped_defs = true
    no_implicit_optional = true
    warn_unused_ignores = true
    ```
-   **Pyright** for editor feedback (fast, incremental).

## Python Testing

-   Use pytest.
-   Apply the testing pyramid: balance unit, integration, and end-to-end tests.
-   Structure tests to mirror application code.
-   Use pytest fixtures for data, test doubles, and setup.
-   Use pytest markers for categories (no need if entire test suite finishes in <1s).
-   Keep integration tests hermetic with `pytest-docker` or `testcontainers`.

## Python Config

-   Guidelines for data models:
    -   Use Pydantic at boundaries (config, request/response, parsing external data).
    -   Use `dataclasses` or `attrs` for plain in-memory models (lighter, faster).
    -   Use `msgspec` for hot (de)serialization paths where performance is critical.
-   Use `python-dotenv` for local dev only (never load `.env` files in CI/production).
-   Use Pydantic Settings v2 to unify env/config.

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

### Python Project Folders

```
repo-root/
├─ src/
│  └─ package_name/             # importable module
│     ├─ __init__.py
│     ├─ core/                  # domain/business logic (dataclasses/attrs)
│     ├─ adapters/              # IO edges: db, http clients, queues (Pydantic models ok)
│     ├─ api/                   # FastAPI routes, schemas, dependencies
│     ├─ services/              # orchestrations/use-cases (compose core + adapters)
│     ├─ settings.py            # Pydantic Settings v2 (env/config)
│     └─ cli.py                 # Typer/argparse entrypoint (optional)
├─ tests/
│  ├─ unit/                     # fast, isolated tests
│  ├─ integration/              # real services via testcontainers/pytest-docker
│  ├─ e2e/                      # optional end-to-end
│  └─ conftest.py               # shared fixtures
├─ scripts/                     # operational one-offs (migrations, data fixes, utilities)
├─ docs/
│  ├─ index.md                  # Quickstart (or keep in README if tiny)
│  └─ adr/                      # Architecture Decision Records (MADR template)
├─ .github/workflows/ci.yml     # CI pipeline
├─ Makefile                     # uv run … targets
├─ pyproject.toml               # single source of config (ruff/pytest/mypy/etc.)
├─ uv.lock                      # pinned deps (commit this)
├─ .env.example                 # doc-only; not loaded in CI/prod
├─ README.md                    # what it is, how to run, how to test
└─ .pre-commit-config.yaml      # ruff/mypy/pip-audit/detect-secrets
```

**Variants by project type**
A) Library-first repo (published package)

-   Drop api/ and services/ if not needed.
-   Add CHANGELOG.md, LICENSE, and CODEOWNERS.
-   Keep package_name/ with core/ and adapters/ (if any).
    Confidence: 90% (standard for libs; keep runtime deps minimal).

B) Service (FastAPI)

-   Keep api/ and services/.
-   Add package_name/db/ if you generate migrations (e.g., Alembic).
-   Containerize with a slim Dockerfile and uvicorn entrypoint.
    Confidence: 90% (clean boundary layering pays off quickly).

C) CLI-only tool

-   Keep package_name/cli.py and core/.
-   No api/; adapters/ only if IO-heavy.
    Confidence: 85% (smaller surface, faster to ship).

**Conventions inside folders (why & confidence)**

-   core/ → dataclasses/attrs, pure functions, business invariants; no Pydantic, no FastAPI.
    Confidence: 90% (keeps domain portable and testable).
-   adapters/ → Pydantic models for serialization, HTTP/DB clients, S3/GCS, caching, external APIs.
    Confidence: 90% (Pydantic-at-edges rule).
-   api/ → FastAPI routers grouped by domain (users.py, orders.py), schemas.py for request/response, deps.py for dependency providers.
    Confidence: 90% (common, readable pattern).
-   services/ → functions/classes that implement use-cases (e.g., create_order), orchestrating core and adapters; thin, testable.
    Confidence: 85% (clarifies “where the work happens”).
-   tests/ → mirror package layout (e.g., tests/unit/core/test\_\*.py), central conftest.py for fixtures, mark slow/integration tests.
    Confidence: 95% (maximizes clarity and speed).

## Project-Specific Notes

**[CUSTOMIZE THIS SECTION]**

Add project-specific patterns, libraries, or conventions that AI agents should follow.
