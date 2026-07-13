# SynthFHIR developer tasks. Run `make help` for the list.
.DEFAULT_GOAL := help
.PHONY: help install dev serve test lint typecheck check format docker docker-run clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

install: ## Install the package
	pip install -e .

dev: ## Install with development extras
	pip install -e ".[dev]"

serve: ## Run the API with auto-reload at http://localhost:8000
	uvicorn main:app --reload

test: ## Run the test suite
	pytest tests/ -v

lint: ## Run ruff
	ruff check .

typecheck: ## Run mypy
	mypy generators mappers api data validation main.py cli.py synthfhir.py

check: lint test ## Run lint and tests

format: ## Auto-fix lint issues
	ruff check --fix .

docker: ## Build the container image
	docker build -t synthfhir .

docker-run: ## Run the container on port 8000
	docker run --rm -p 8000:8000 synthfhir

clean: ## Remove caches and build artifacts
	rm -rf .ruff_cache .pytest_cache .mypy_cache *.egg-info build dist
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
