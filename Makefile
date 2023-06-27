.SILENT:

## Migrations
.PHONY: migrate
migrate:
	poetry run python3 app/manage.py migrate

.PHONY: makemigrations
makemigrations:
	poetry run python3 app/manage.py makemigrations


## Backend
.PHONY: run
run:
	poetry run python3 app/manage.py runserver

.PHONY: createsuperuser
createsuperuser:
	poetry run python3 app/manage.py createsuperuser


## Bot
.PHONY: runbot
runbot:
	poetry run python3 app/runbot.py


## Poetry
.PHONY: install
install:
	poetry install
