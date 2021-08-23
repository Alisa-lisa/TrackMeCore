.PHONY: local-setup
local-setup:
	poetry config virtualenvs.create true 
	poetry config virtualenvs.in-project false
	poetry install
	# poetry shell

.PHONY: lint
lint:
	poetry run black -l 120 .
	poetry run flake8 .
	poetry run mypy . 

.PHONY: test
test:
	poetry run pytest .


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
	poetry run hypercorn -b 0.0.0.0:5000 --access-logfile - -w 1 app:app --reload --debug


.PHONY: build
docker-run:
	docker build --rm -t trackme . 

.PHONY: run
run: 
	docker run --rm -p 5000:5000 --env-file .env --network="host" --name trackme-back trackme


.PHONY: docker-execute
docker-execute:
	make build
	make run

.PHONY: docker-migrate
docker-migrate:
	docker run --rm --env-file .env --network="host" --name tb trackme alembic upgrade head


generate-client:
	cd openapiclient && openapi-generator-cli generate -i openapi.json -g $(language) --ignore-file-override .
