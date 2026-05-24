.PHONY: help up down build logs restart docker-up docker-down

help:
	@echo "Available targets:"
	@echo "  make up      - start the full app with Docker Compose"
	@echo "  make down    - stop Docker Compose services"
	@echo "  make build   - build Docker Compose services"
	@echo "  make logs    - show Docker Compose logs"
	@echo "  make restart - restart Docker Compose services"

up:
	docker compose up --build

down:
	docker compose down

build:
	docker compose build

logs:
	docker compose logs -f

restart: down up

docker-up: up

docker-down: down
