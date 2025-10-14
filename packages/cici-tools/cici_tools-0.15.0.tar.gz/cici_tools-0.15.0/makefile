# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

VENV ?= venv
PYTHON ?= $(VENV)/bin/python3
PYTHON_VERSION ?= 3.11
MANAGE ?= $(PYTHON) ./manage.py

.PHONY: all
all: setup

.PHONY: setup
setup: $(VENV)/requirements.txt

requirements.txt: pyproject.toml | $(VENV)
	uv pip compile --python-version $(PYTHON_VERSION) --upgrade -o requirements.txt pyproject.toml

$(VENV)/requirements.txt: requirements.txt | $(VENV)
	VIRTUAL_ENV=$(VENV) uv pip install -r requirements.txt
	cp -f requirements.txt $(VENV)/requirements.txt

$(VENV):
	uv venv $(VENV)

.PHONY: clean
clean:
	find -name __pycache__ -type d -exec rm -rf '{}' \;
	find -name \*.pyc -type f -exec rm -f '{}' \;

.PHONY: distclean
distclean:
	rm -rf $(VENV)

.PHONY: editable
editable:
	VIRTUAL_ENV=$(VENV) uv pip install -e .

.PHONY: schema
schema:
	$(VENV)/bin/cici schema | $(PYTHON) ./scripts/gen-api-doc.py -p cici.config. -t "cici config file format" -d 'This page is a reference for cici config file syntax. For a tutorial, see the [Getting started](getting-started.md) section of the site' - > docs/config-file.md
	npx prettier -w docs/config-file.md
