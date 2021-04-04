.PHONY: local-setup
local-setup:
	poetry config virtualenvs.create true --local
	poetry config virtualenvs.path ./venv/
	poetry install
	poetry shell


migrate:
	poetry run alembic revision --autogenerate -m $(message)

.PHONY: db-up
db-up:
	poetry run alembic upgrade head

.PHONY: db-down
db-down:
	poetry run alembic downgrade -1

