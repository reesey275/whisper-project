# Whisper Project - Professional Development Commands
# =======================================================

.PHONY: help test test-fast test-slow test-all bench lint security clean setup docs potato-check potato-report potato-violations

# Default target
help:  ## Show this help message
	@echo "Whisper Transcription Project - Development Commands"
	@echo "=================================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Testing Commands
test-fast:  ## Run fast unit tests only (no slow/integration)
	python -m pytest -m "not slow and not integration" --tb=short

test:  ## Run all tests except slow integration tests
	python -m pytest -m "not slow" --tb=short

test-slow:  ## Run only slow and integration tests
	python -m pytest -m "slow or integration" --tb=line

test-all:  ## Run complete test suite including slow tests
	python -m pytest --tb=short

test-property:  ## Run property-based tests only
	python -m pytest -m "property" --tb=short

# Performance & Benchmarking
bench:  ## Run performance benchmarks and save results
	python -m pytest -k benchmark --benchmark-save=latest --benchmark-sort=mean

bench-compare:  ## Compare current benchmarks with previous run
	python -m pytest -k benchmark --benchmark-compare=latest --benchmark-compare-fail=mean:10%

# Code Quality
lint:  ## Run all linting and formatting checks
	@echo "🔍 Running black formatter check..."
	black --check .
	@echo "🔍 Running isort import check..."
	isort --check-only .
	@echo "🔍 Running flake8 linting..."
	flake8 .
	@echo "🔍 Running mypy type checking..."
	mypy .

format:  ## Auto-format code with black and isort
	@echo "🎨 Formatting code with black..."
	black .
	@echo "🎨 Sorting imports with isort..."
	isort .

# Security & Safety
security:  ## Run security and vulnerability checks
	@echo "🔒 Running bandit security analysis..."
	bandit -r . -ll
	@echo "🔒 Running safety vulnerability check..."
	safety check
	@echo "🔒 Checking for secrets in git history..."
	@if command -v gitleaks >/dev/null; then gitleaks detect --verbose; else echo "⚠️ gitleaks not installed"; fi

# Environment Setup
setup:  ## Set up development environment
	@echo "🚀 Setting up development environment..."
	pip install -e .
	pip install -r requirements-dev.txt
	pre-commit install

clean:  ## Clean up generated files and caches
	@echo "🧹 Cleaning up..."
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf coverage_html/
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	rm -rf __pycache__/
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .benchmarks/
	rm -rf output/

# Documentation
docs:  ## Generate and view documentation
	@echo "📚 Generating documentation..."
	@echo "Coverage report: file://$(PWD)/coverage_html/index.html"
	@echo "Benchmark results: .benchmarks/latest.json"

# Docker Commands
docker-build:  ## Build Docker image for transcription
	docker build -t whisper-transcribe -f docker/Dockerfile .

docker-test:  ## Run tests in Docker environment
	docker run --rm -v $(PWD):/workspace whisper-transcribe make test

# CI/CD Helpers
ci-lint:  ## Run linting checks for CI (fail-fast)
	black --check --diff .
	isort --check-only --diff .
	flake8 .
	mypy . --strict

ci-security:  ## Run security checks for CI
	bandit -r . -f json -o bandit-report.json
	safety check --json --output safety-report.json

ci-test:  ## Run test suite optimized for CI
	python -m pytest -x --tb=short --durations=10

# Development Workflow
dev-check:  ## Run full development checks (lint + test + security)
	$(MAKE) lint
	$(MAKE) test
	$(MAKE) security
	@echo "✅ All checks passed! Ready for commit."

# Performance Profiling
profile:  ## Profile test performance
	python -m pytest --tb=no --durations=20 -q

# Environment Setup - Professional Reproducibility
.PHONY: venv
venv:  ## Create isolated virtual environment
	@echo "🚀 Creating professional virtual environment..."
	python -m venv .venv
	@echo "📦 Activating and upgrading pip..."
	. .venv/bin/activate && python -m pip install -U pip
	@echo "✅ Virtual environment ready at .venv/"
	@echo "🔧 Run: source .venv/bin/activate"

# Contract Validation
.PHONY: test-contracts
test-contracts:  ## Run tests that validate behavior contracts
	@echo "📋 Validating function behavior contracts..."
	python -m pytest -k "contract or essential_edge_cases" -v --tb=short
	@echo "✅ Behavior contracts validated"

# Quick Status
status:  ## Show project status and metrics
	@echo "📊 Whisper Project Status"
	@echo "========================"
	@echo "Tests: $$(python -m pytest --collect-only -q | grep -c test)"
	@echo "Coverage: $$(python -m pytest --cov=. --cov-report=term | grep TOTAL | awk '{print $$4}')"
	@echo "Lines of Code: $$(find . -name '*.py' -not -path './tests/*' | xargs wc -l | tail -1 | awk '{print $$1}')"
	@echo "Test Lines: $$(find ./tests -name '*.py' | xargs wc -l | tail -1 | awk '{print $$1}')"
	@echo "Coverage Gate: 40% (realistic baseline, will ratchet up)"
	@echo "Behavior Contracts: ✅ Documented in FUNCTION_CONTRACTS.md"

# Enhanced Potato Policy Commands 🥔
potato-check:  ## Run Enhanced Potato Policy security check
	@echo "🥔 Running Enhanced Potato Policy security check..."
	@./scripts/enhanced_potato_check.sh --verbose

potato-report:  ## Generate Enhanced Potato Policy audit report
	@echo "🥔 Generating Enhanced Potato Policy audit report..."
	@./scripts/generate_potato_report.sh true

potato-violations:  ## Check and report Enhanced Potato Policy violations
	@echo "🥔 Checking and reporting policy violations..."
	@./scripts/potato_violation_reporter.sh
