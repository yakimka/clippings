SHELL:=/usr/bin/env bash

RUN=docker compose run --rm --remove-orphans -it devtools

.PHONY: all
all: help

.PHONY: pre-commit
pre-commit:  ## Run pre-commit with args
	$(RUN) pre-commit $(args)

.PHONY: poetry
poetry:  ## Run poetry with args
	$(RUN) poetry $(args)

.PHONY: lint
lint:  ## Run flake8, mypy, other linters and verify formatting
	@make pre-commit args="run --all-files"; \
	RESULT1=$$?; \
	make mypy; \
	RESULT2=$$?; \
	exit $$((RESULT1 + RESULT2))

.PHONY: mypy
mypy:  ## Run mypy
	$(RUN) mypy $(args)

.PHONY: test
test:  ## Run tests
	$(RUN) pytest --cov=tests --cov=clippings $(args)
	$(RUN) pytest --dead-fixtures

.PHONY: test-record-vcr
test-record-vcr:  ## Run tests with VCR recording
	$(RUN) pytest -k vcr --record-mode=rewrite --block-network $(args)

.PHONY: package
package:  ## Run packages (dependencies) checks
	$(RUN) poetry check
	$(RUN) pip check

.PHONY: build-package
build-package:  ## Build package
	$(RUN) poetry build $(args)
	$(RUN) poetry export --format=requirements.txt --output=dist/requirements.txt

.PHONY: build-production-image
build-production-image:  ## Build production image
	build-package
	docker build -t clippings:prod .

.PHONY: checks
checks: lint package test  ## Run linting and tests

.PHONY: run-ci
run-ci:  ## Run CI locally
	$(RUN) ./ci.sh

.PHONY: clean
clean:  ## Clean up
	rm -rf dist
	rm -rf htmlcov
	rm -f .coverage coverage.xml

.PHONY: clean-all
clean-all:  ## Clean up all
	@make clean
	rm -rf .cache
	rm -rf .mypy_cache
	rm -rf .pytest_cache

.PHONY: bash
bash:  ## Run bash
	$(RUN) bash $(args)

.PHONY: run-command
run-command:  ## Run bash
	$(RUN) python -m clippings.cli $(args)

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
