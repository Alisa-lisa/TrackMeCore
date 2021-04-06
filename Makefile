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

.PHONY: local-run
local-run:
	poetry run hypercorn -b 0.0.0.0:5000 -w 1 app:app 	

