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


# Docker
# Запуск контейнера в проадкшене

.PHONY: compose-up
compose-up: ## Создает и запускает контейнер
	docker-compose -f docker/docker-compose.prod.yml up -d --build

.PHONY: compose-down
compose-down: ## Останавливает и удаляет контейнеры
	docker-compose -f docker/docker-compose.prod.yml down

.PHONY: compose-down-v
compose-down-v: ## Останавливает и удаляет контейнеры вместе с зависимостями
	docker-compose -f docker/docker-compose.prod.yml down -v

.PHONY: compose-stop
compose-stop: ## Останавливает контейнеры
	docker-compose -f docker/docker-compose.prod.yml stop

.PHONY: compose-start
compose-start: ## Запускает контейнеры
	docker-compose -f docker/docker-compose.prod.yml start

.PHONY: compose-logs
compose-logs: ## Просмотр логов
	docker-compose -f docker/docker-compose.prod.yml logs -f

.PHONY: compose-ps
compose-ps: ## Список всех контейнеров
	docker-compose -f docker/docker-compose.prod.yml ps -a

.PHONY: compose-collect-up
compose-collect-up: compose-up ## Полный запуск контейнеров
	 docker-compose -f docker/docker-compose.prod.yml exec web python3 manage.py collectstatic

.PHONY: compose-createsuperuser
compose-createsuperuser: ## Создание суперпользователя
	docker-compose -f docker/docker-compose.prod.yml exec web python3 manage.py createsuperuser

.PHONY: compose-exec
compose-exec:
	docker-compose -f docker/docker-compose.prod.yml exec web bash


.PHONY: gunicorn
gunicorn: ## Запуск проекта через gunicorn
	poetry run gunicorn --reload --bind $(HOST):$(PORT) --workers $(WORKERS) --log-level $(LEVEL) --chdir app/ config.wsgi:application

