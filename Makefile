# Makefile for WiFi Profile Extractor
# Professional automation for development and deployment tasks

.PHONY: help install install-dev test lint format security clean build docs serve run all check pre-commit docker-build docker-run

# Default target
.DEFAULT_GOAL := help

# Colors for output
RED=\033[0;31m
GREEN=\033[0;32m
YELLOW=\033[1;33m
BLUE=\033[0;34m
PURPLE=\033[0;35m
CYAN=\033[0;36m
WHITE=\033[1;37m
NC=\033[0m # No Color

# Python and environment settings
PYTHON := python
PIP := pip
VENV := venv
SRC_DIR := src
TEST_DIR := tests
DOCS_DIR := docs

# Check if virtual environment exists
VENV_EXISTS := $(shell test -d $(VENV) && echo yes || echo no)

# Project metadata
PROJECT_NAME := wifi-profile-extractor
VERSION := $(shell $(PYTHON) -c "import sys; sys.path.insert(0, '$(SRC_DIR)'); from config.settings import app_config; print(app_config.APP_VERSION)")

help: ## Show this help message
	@echo "$(CYAN)WiFi Profile Extractor - Development Commands$(NC)"
	@echo "$(CYAN)=============================================$(NC)"
	@echo ""
	@echo "$(WHITE)Available commands:$(NC)"
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ { printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(WHITE)Project Info:$(NC)"
	@echo "  $(BLUE)Name:$(NC)    $(PROJECT_NAME)"
	@echo "  $(BLUE)Version:$(NC) $(VERSION)"
	@echo "  $(BLUE)Python:$(NC)  $(shell $(PYTHON) --version)"
	@echo ""

check-python: ## Check Python version compatibility
	@echo "$(BLUE)Checking Python version...$(NC)"
	@$(PYTHON) -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" || \
		(echo "$(RED)Error: Python 3.8+ required$(NC)" && exit 1)
	@echo "$(GREEN)✓ Python version OK$(NC)"

check-venv: ## Check if virtual environment exists
ifeq ($(VENV_EXISTS),no)
	@echo "$(YELLOW)⚠ Virtual environment not found. Creating...$(NC)"
	@$(PYTHON) -m venv $(VENV)
	@echo "$(GREEN)✓ Virtual environment created$(NC)"
	@echo "$(CYAN)Activate with: $(VENV)/Scripts/activate (Windows) or source $(VENV)/bin/activate (Linux/Mac)$(NC)"
endif

install: check-python check-venv ## Install production dependencies
	@echo "$(BLUE)Installing production dependencies...$(NC)"
	@$(PYTHON) -m pip install --upgrade pip
	@$(PYTHON) -m pip install -r requirements.txt
	@$(PYTHON) -m pip install -e .
	@echo "$(GREEN)✓ Production dependencies installed$(NC)"

install-dev: check-python check-venv ## Install development dependencies
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	@$(PYTHON) -m pip install --upgrade pip
	@$(PYTHON) -m pip install -r requirements-dev.txt
	@$(PYTHON) -m pip install -e .
	@echo "$(GREEN)✓ Development dependencies installed$(NC)"

install-hooks: install-dev ## Install pre-commit hooks
	@echo "$(BLUE)Installing pre-commit hooks...$(NC)"
	@$(PYTHON) -m pre_commit install --install-hooks
	@$(PYTHON) -m pre_commit install --hook-type commit-msg
	@echo "$(GREEN)✓ Pre-commit hooks installed$(NC)"

test: ## Run test suite
	@echo "$(BLUE)Running test suite...$(NC)"
	@$(PYTHON) -m pytest $(TEST_DIR)/ -v --tb=short --cov=$(SRC_DIR) --cov-report=html --cov-report=term-missing
	@echo "$(GREEN)✓ Tests completed$(NC)"
	@echo "$(CYAN)Coverage report: htmlcov/index.html$(NC)"

test-quick: ## Run tests without coverage
	@echo "$(BLUE)Running quick tests...$(NC)"
	@$(PYTHON) -m pytest $(TEST_DIR)/ -v --tb=short
	@echo "$(GREEN)✓ Quick tests completed$(NC)"

lint: ## Run code linting
	@echo "$(BLUE)Running code quality checks...$(NC)"
	@echo "$(PURPLE)→ Black formatting check...$(NC)"
	@$(PYTHON) -m black --check --diff $(SRC_DIR)/ $(TEST_DIR)/
	@echo "$(PURPLE)→ Import sorting check...$(NC)"
	@$(PYTHON) -m isort --check-only --diff $(SRC_DIR)/ $(TEST_DIR)/
	@echo "$(PURPLE)→ Flake8 linting...$(NC)"
	@$(PYTHON) -m flake8 $(SRC_DIR)/ $(TEST_DIR)/
	@echo "$(PURPLE)→ MyPy type checking...$(NC)"
	@$(PYTHON) -m mypy $(SRC_DIR)/ --ignore-missing-imports
	@echo "$(GREEN)✓ All linting checks passed$(NC)"

format: ## Format code with Black and isort
	@echo "$(BLUE)Formatting code...$(NC)"
	@$(PYTHON) -m black $(SRC_DIR)/ $(TEST_DIR)/
	@$(PYTHON) -m isort $(SRC_DIR)/ $(TEST_DIR)/
	@echo "$(GREEN)✓ Code formatted$(NC)"

security: ## Run security checks
	@echo "$(BLUE)Running security checks...$(NC)"
	@echo "$(PURPLE)→ Bandit security scan...$(NC)"
	@$(PYTHON) -m bandit -r $(SRC_DIR)/ -f json -o bandit-report.json || true
	@echo "$(PURPLE)→ Safety dependency check...$(NC)"
	@$(PYTHON) -m safety check || true
	@echo "$(GREEN)✓ Security checks completed$(NC)"

clean: ## Clean build artifacts and cache
	@echo "$(BLUE)Cleaning project...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf build/ dist/ htmlcov/ .coverage bandit-report.json safety-report.json 2>/dev/null || true
	@echo "$(GREEN)✓ Project cleaned$(NC)"

build: clean ## Build package for distribution
	@echo "$(BLUE)Building package...$(NC)"
	@$(PYTHON) -m build
	@$(PYTHON) -m twine check dist/*
	@echo "$(GREEN)✓ Package built successfully$(NC)"
	@echo "$(CYAN)Package files: $(shell ls -1 dist/)$(NC)"

docs: ## Build documentation
	@echo "$(BLUE)Building documentation...$(NC)"
	@if [ ! -f mkdocs.yml ]; then \
		echo "site_name: WiFi Profile Extractor" > mkdocs.yml; \
		echo "theme:" >> mkdocs.yml; \
		echo "  name: material" >> mkdocs.yml; \
		echo "nav:" >> mkdocs.yml; \
		echo "  - Home: README.md" >> mkdocs.yml; \
		echo "  - API: docs/API.md" >> mkdocs.yml; \
		echo "  - Security: docs/SECURITY.md" >> mkdocs.yml; \
		echo "  - Contributing: docs/CONTRIBUTING.md" >> mkdocs.yml; \
	fi
	@$(PYTHON) -m mkdocs build
	@echo "$(GREEN)✓ Documentation built$(NC)"
	@echo "$(CYAN)Documentation: site/index.html$(NC)"

serve-docs: docs ## Serve documentation locally
	@echo "$(BLUE)Serving documentation at http://127.0.0.1:8000$(NC)"
	@$(PYTHON) -m mkdocs serve

run: ## Run Streamlit application
	@echo "$(BLUE)Starting WiFi Profile Extractor...$(NC)"
	@echo "$(CYAN)Application will open at http://localhost:8501$(NC)"
	@$(PYTHON) -m streamlit run $(SRC_DIR)/app.py

serve: run ## Alias for run command

dev-setup: install-dev install-hooks ## Complete development environment setup
	@echo "$(GREEN)✓ Development environment setup complete!$(NC)"
	@echo ""
	@echo "$(WHITE)Next steps:$(NC)"
	@echo "  1. $(CYAN)make test$(NC)     - Run the test suite"
	@echo "  2. $(CYAN)make run$(NC)      - Start the application"
	@echo "  3. $(CYAN)make lint$(NC)     - Check code quality"
	@echo ""

all: format lint test security ## Run all checks (format, lint, test, security)
	@echo "$(GREEN)✓ All checks completed successfully!$(NC)"

check: lint test ## Run linting and tests
	@echo "$(GREEN)✓ Code quality checks completed$(NC)"

pre-commit: format lint test-quick ## Run pre-commit checks
	@echo "$(GREEN)✓ Pre-commit checks completed$(NC)"

# Docker commands
docker-build: ## Build Docker image
	@echo "$(BLUE)Building Docker image...$(NC)"
	@docker build -t $(PROJECT_NAME):$(VERSION) .
	@docker tag $(PROJECT_NAME):$(VERSION) $(PROJECT_NAME):latest
	@echo "$(GREEN)✓ Docker image built: $(PROJECT_NAME):$(VERSION)$(NC)"

docker-run: ## Run application in Docker container
	@echo "$(BLUE)Running Docker container...$(NC)"
	@echo "$(CYAN)Application will be available at http://localhost:8501$(NC)"
	@docker run -p 8501:8501 --rm -it $(PROJECT_NAME):latest

docker-clean: ## Clean Docker images and containers
	@echo "$(BLUE)Cleaning Docker resources...$(NC)"
	@docker rmi $(PROJECT_NAME):latest $(PROJECT_NAME):$(VERSION) 2>/dev/null || true
	@echo "$(GREEN)✓ Docker resources cleaned$(NC)"

# Release commands
version: ## Show current version
	@echo "$(CYAN)Current version: $(VERSION)$(NC)"

# Development helpers
watch-test: ## Watch files and run tests on changes
	@echo "$(BLUE)Watching for changes... (Ctrl+C to stop)$(NC)"
	@$(PYTHON) -m pytest_watch $(TEST_DIR)/ -- -v --tb=short

profile: ## Profile application performance
	@echo "$(BLUE)Profiling application...$(NC)"
	@$(PYTHON) -m cProfile -o profile.prof $(SRC_DIR)/app.py
	@echo "$(GREEN)✓ Profile saved to profile.prof$(NC)"

# Utility commands
deps-update: ## Update dependencies to latest versions
	@echo "$(BLUE)Updating dependencies...$(NC)"
	@$(PYTHON) -m pip install --upgrade pip
	@$(PYTHON) -m pip list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1 | xargs -n1 pip install -U || true
	@echo "$(GREEN)✓ Dependencies updated$(NC)"

deps-check: ## Check for dependency vulnerabilities
	@echo "$(BLUE)Checking dependencies for vulnerabilities...$(NC)"
	@$(PYTHON) -m safety check
	@echo "$(GREEN)✓ Dependencies checked$(NC)"

size: ## Show project size statistics
	@echo "$(BLUE)Project size statistics:$(NC)"
	@echo "$(CYAN)Source code:$(NC)"
	@find $(SRC_DIR) -name "*.py" | xargs wc -l | tail -1 || echo "0 total"
	@echo "$(CYAN)Test code:$(NC)"
	@find $(TEST_DIR) -name "*.py" | xargs wc -l | tail -1 || echo "0 total"
	@echo "$(CYAN)Documentation:$(NC)"
	@find $(DOCS_DIR) -name "*.md" | xargs wc -l | tail -1 || echo "0 total"

info: ## Show project information
	@echo "$(CYAN)WiFi Profile Extractor - Project Information$(NC)"
	@echo "$(CYAN)===========================================$(NC)"
	@echo ""
	@echo "$(WHITE)Project Details:$(NC)"
	@echo "  $(BLUE)Name:$(NC)         $(PROJECT_NAME)"
	@echo "  $(BLUE)Version:$(NC)      $(VERSION)"
	@echo "  $(BLUE)Python:$(NC)       $(shell $(PYTHON) --version)"
	@echo "  $(BLUE)Platform:$(NC)     $(shell $(PYTHON) -c "import platform; print(platform.platform())")"
	@echo ""
	@echo "$(WHITE)Environment:$(NC)"
	@echo "  $(BLUE)Virtual Env:$(NC)  $(if $(filter yes,$(VENV_EXISTS)),✓ Active,✗ Not found)"
	@echo "  $(BLUE)Git Branch:$(NC)   $(shell git branch --show-current 2>/dev/null || echo 'Not a git repo')"
	@echo "  $(BLUE)Git Status:$(NC)   $(shell git status --porcelain 2>/dev/null | wc -l | awk '{print ($$1 == 0) ? "Clean" : $$1 " changes"}')"
	@echo ""
	@echo "$(WHITE)Quick Commands:$(NC)"
	@echo "  $(GREEN)make dev-setup$(NC)  - Set up development environment"
	@echo "  $(GREEN)make test$(NC)       - Run test suite"
	@echo "  $(GREEN)make run$(NC)        - Start application"
	@echo "  $(GREEN)make all$(NC)        - Run all checks"
	@echo ""

# Dockerfile
---
# Dockerfile
FROM python:3.8-slim-bullseye

# Set metadata
LABEL maintainer="WiFi Profile Extractor Team"
LABEL description="Professional WiFi Profile Extractor for Windows"
LABEL version="1.0.0"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Create app user for security
RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 --gid 1001 appuser

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt requirements-dev.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY setup.py pyproject.toml ./
COPY README.md LICENSE CHANGELOG.md ./

# Install the application
RUN pip install -e .

# Create necessary directories
RUN mkdir -p /app/logs /app/exports && \
    chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Expose port
EXPOSE 8501

# Set default command
CMD ["streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=0.0.0.0"]

# .dockerignore
---
# .dockerignore
# Build artifacts
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDE files
.vscode/
.idea/
*.swp
*.swo
*~

# OS files
.DS_Store
Thumbs.db

# Git
.git/
.gitignore

# Documentation build
site/
docs/_build/

# Test and coverage
.pytest_cache/
.coverage
htmlcov/
.tox/
.nox/

# Security reports
bandit-report.json
safety-report.json

# Logs
logs/
*.log

# Temporary files
tmp/
temp/
*.tmp

# Development scripts
scripts/
examples/
tests/

# CI/CD
.github/
.pre-commit-config.yaml

# Documentation
docs/
*.md
!README.md

# Configuration files that shouldn't be in container
.env
.env.local
.env.production

# docker-compose.yml (for development)
---
version: '3.8'

services:
  wifi-extractor:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: wifi-profile-extractor
    ports:
      - "8501:8501"
    environment:
      - STREAMLIT_SERVER_HEADLESS=true
      - STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
    volumes:
      - ./exports:/app/exports  # Mount exports directory
      - ./logs:/app/logs        # Mount logs directory
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Development service with hot reload
  wifi-extractor-dev:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: wifi-profile-extractor-dev
    ports:
      - "8502:8501"
    environment:
      - STREAMLIT_SERVER_HEADLESS=true
      - STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
      - DEBUG=true
    volumes:
      - .:/app                  # Mount entire project for development
      - /app/venv               # Exclude virtual environment
    restart: "no"
    profiles:
      - dev
    command: ["streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.runOnSave=true"]