.PHONY: install project lint build

install:
	poetry install

project:
	poetry run labyrinth

lint:
	poetry run ruff check .
	poetry run ruff format --check .

build:
	poetry build
