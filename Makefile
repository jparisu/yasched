.PHONY: venv install install-current ensure-git precommit lint format test docs build clean \
        test-all run serve demo web-build web install-web up up-demo down logs

VENV ?= .venv
PYTHON ?= python3
PRE_COMMIT_ARGS ?= --all-files
PRE_COMMIT_SKIP ?=
TEST_ARGS ?= tests -v
VENV_PYTHON := $(VENV)/bin/python
VENV_PIP := $(VENV)/bin/pip
VENV_PRE_COMMIT := $(VENV)/bin/pre-commit
VENV_RUFF := $(VENV)/bin/ruff
VENV_MYPY := $(VENV)/bin/mypy
VENV_PYTEST := $(VENV)/bin/pytest
VENV_MKDOCS := $(VENV)/bin/mkdocs
VENV_BUILD := $(VENV)/bin/python -m build
VENV_YASCHED := $(VENV)/bin/yasched

WEB_DIR := apps/web

# Agenda served by `make serve` (defaults to the personal agenda).
AGENDA ?= $(HOME)/.yasched/agenda.yaml
# Agenda served by `make demo` (the bundled comprehensive example).
DEMO_AGENDA := resources/teacher_example/teacher_main.yaml
HOST ?= 127.0.0.1
PORT ?= 8000

venv:
	$(PYTHON) -m venv $(VENV)

install: venv
	$(VENV_PYTHON) -m pip install --upgrade pip
	$(VENV_PIP) install -e ".[dev]"

install-current:
	python -m pip install --upgrade pip
	python -m pip install -e ".[dev]"

ensure-git:
	@if [ ! -d .git ]; then git init -q; fi

precommit: ensure-git
	SKIP=$(PRE_COMMIT_SKIP) $(VENV_PRE_COMMIT) run $(PRE_COMMIT_ARGS)

lint:
	$(VENV_RUFF) check src tests
	$(VENV_RUFF) format --diff --check src tests
	$(VENV_MYPY) src/yasched

format:
	$(VENV_RUFF) check --fix src tests
	$(VENV_RUFF) format src tests

test:
	$(VENV_PYTEST) $(TEST_ARGS)

docs:
	$(VENV_MKDOCS) build --strict

build:
	$(VENV_BUILD)

test-all: lint format test docs

# ---------------------------------------------------------------------------
# Run the app locally (fully offline). `make run` is the one-command path.
# ---------------------------------------------------------------------------

# Build + install + create-agenda-if-missing + serve, in one go.
run:
	./run.sh

# Serve your personal agenda (assumes deps installed and frontend built).
serve:
	$(VENV_YASCHED) serve --agenda "$(AGENDA)" --host $(HOST) --port $(PORT)

# Serve the bundled comprehensive example (great for a first look).
demo: web-build
	$(VENV_YASCHED) serve --agenda "$(DEMO_AGENDA)" --host $(HOST) --port $(PORT)

# ---------------------------------------------------------------------------
# Docker (easiest up/down). First `make up` builds the image (~1-2 min, needs
# network once); after that up/down take seconds.
# ---------------------------------------------------------------------------
DOCKER_COMPOSE ?= docker compose

# Start detached with an editable default agenda -> http://localhost:$(PORT)
up:
	$(DOCKER_COMPOSE) up -d --build
	@echo "yasched running at http://localhost:$(PORT)  —  stop it with 'make down'"

# Same, but serve the bundled comprehensive example (browse-only).
up-demo:
	YASCHED_AGENDA=/app/resources/teacher_example/teacher_main.yaml $(DOCKER_COMPOSE) up -d --build
	@echo "yasched (demo) at http://localhost:$(PORT)  —  stop it with 'make down'"

# Stop and remove the container + network.
down:
	$(DOCKER_COMPOSE) down

# Follow the container logs.
logs:
	$(DOCKER_COMPOSE) logs -f

# ---------------------------------------------------------------------------
# Web frontend (React + Vite)
# ---------------------------------------------------------------------------

install-web:
	cd $(WEB_DIR) && npm install

# Production build of the SPA (served by the API).
web-build: install-web
	cd $(WEB_DIR) && npm run build

# Dev server with hot reload (proxies /api to the running `yasched serve`).
web: install-web
	cd $(WEB_DIR) && npm run dev

clean:
	rm -rf build dist .coverage .pytest_cache .mypy_cache .ruff_cache site apps/web/dist
