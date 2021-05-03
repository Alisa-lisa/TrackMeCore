.PHONY: local-setup
local-setup:
	poetry config virtualenvs.create true 
	poetry config virtualenvs.in-project false
	poetry install
	poetry shell

.PHONY: lint
lint:
	poetry run black -l 120 .
	poetry run flake8 .
	poetry run mypy . 


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

