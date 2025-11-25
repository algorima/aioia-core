.PHONY: lint code-style type-check test format

PY_FILES=$(shell find aioia_core -type f -name '*.py' -print)

lint:
	poetry run pylint $(PY_FILES)

code-style:
	poetry run isort --check-only --diff aioia_core
	poetry run black --check aioia_core

type-check:
	poetry run mypy --check-untyped-defs aioia_core
	poetry run pyright

test:
	poetry run python -m unittest discover -s tests -v

format:
	poetry run isort aioia_core
	poetry run black aioia_core
