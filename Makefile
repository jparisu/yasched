.PHONY: venv install install-current ensure-git precommit lint format test docs build clean streamlit \
        install-api api kill-api install-web web

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
VENV_UVICORN := $(VENV)/bin/uvicorn

WEB_DIR := apps/web

DB_PATH ?= resources/basic_example/basic_example_main.yaml
API_HOST ?= 127.0.0.1
API_PORT ?= 8000

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

streamlit:
	pip install -e ".[frontend]" -q
	streamlit run apps/streamlit/yasched_streamlit.py

# ---------------------------------------------------------------------------
# API (FastAPI backend)
# ---------------------------------------------------------------------------

install-api: venv
	$(VENV_PIP) install -e ".[api]"

api: install-api
	-lsof -ti:$(API_PORT) | xargs kill -9 2>/dev/null; true
	YASCHED_DB_PATH=$(DB_PATH) $(VENV_UVICORN) apps.api.main:app \
		--host $(API_HOST) --port $(API_PORT) --reload

kill-api:
	-lsof -ti:$(API_PORT) | xargs kill -9 2>/dev/null; true

# ---------------------------------------------------------------------------
# Web frontend (React + Vite)
# ---------------------------------------------------------------------------

install-web:
	cd $(WEB_DIR) && npm install

web: install-web
	cd $(WEB_DIR) && npm run dev

clean:
	rm -rf build dist .coverage .pytest_cache .mypy_cache .ruff_cache site
