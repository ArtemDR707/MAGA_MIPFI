.PHONY: install project lint build publish package-install

install:
	poetry install

project:
	poetry run project

lint:
	poetry run ruff check .
	poetry run ruff format --check .

build:
	poetry build

publish:
	poetry publish --build

package-install: build
	python -m pip install --force-reinstall dist/*.whl
