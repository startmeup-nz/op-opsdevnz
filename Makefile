.PHONY: install lint test typecheck build check

install:
	pip install -e .[dev]

lint:
	ruff check src tests

typecheck:
	mypy src

test:
	pytest --color=yes --durations=10

check: lint typecheck test

build:
	python -m build
