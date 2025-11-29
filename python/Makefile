.PHONY: lint code-style type-check test format

PY_FILES=$(shell find . -type d -name '.venv' -prune -o -type f -name '*.py' -print | sed 's|^\./||')

lint:
	poetry run pylint $(PY_FILES)

code-style:
	poetry run isort --check-only --diff .
	poetry run black --check .

type-check:
	poetry run mypy --check-untyped-defs .
	poetry run pyright

test:
	poetry run python -m unittest discover -s tests -v

format:
	poetry run isort .
	poetry run black .
