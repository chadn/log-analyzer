DEFAULT_GOAL := help

.PHONY: init deps lint format fix-format type test serve reqs check ci clean hooks

help: ## Show available targets
	@awk 'BEGIN {FS=":.*##"; printf "\nTargets:\n"} /^[a-zA-Z_-]+:.*##/ {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

init: ## Create venv and install dev dependencies
	uv venv .venv
	uv pip install -e ".[dev]"

deps: ## Reinstall dev dependencies (no new venv)
	uv pip install -e ".[dev]"

lint: ## Run lint checks
	uv run ruff check .

fix-lint: ## Fix lint issues
	uv run ruff check --fix .

format: ## Verify formatting
	uv run ruff format --check .

fix-format: ## Auto-fix formatting
	uv run ruff format .

type: ## Type-check with mypy
	uv run mypy .

test: ## Run tests (pass extra flags via ARGS='...')
	uv run pytest -q $(ARGS)

serve: ## Run app locally with hot reload, with APP_DEBUG env override
	APP_DEBUG=true uv run uvicorn access_log_analyzer.main:app --reload --port 8000

reqs: ## Generate requirements.txt from pyproject (legacy tools only)
	uv pip compile pyproject.toml -o requirements.txt

check: format lint type test ## Run all local checks

ci: check ## Run checks + coverage (CI gate)
	uv run coverage run -m pytest -q
	uv run coverage report --fail-under=85

clean: ## Remove caches and build artifacts
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage dist build
	find . -type d -name __pycache__ -exec rm -rf {} +

hooks: ## Install pre-commit hooks
	uv run pre-commit install