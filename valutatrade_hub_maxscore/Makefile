.PHONY: install project lint format build publish package-install

install:
	poetry install

project:
	poetry run project

lint:
	poetry run ruff check .
	poetry run ruff format --check .

format:
	poetry run ruff format .
	poetry run ruff check . --fix

build:
	poetry build

publish:
	poetry publish --dry-run

package-install: build
	python -m pip install --force-reinstall dist/*.whl
