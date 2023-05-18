# Define variables
DOCKER_COMPOSE = docker-compose

build:
	$(DOCKER_COMPOSE) build

build-no-cache:
	$(DOCKER_COMPOSE) build --no-cache

up:
	$(DOCKER_COMPOSE) up

run: build up

run-no-cache: build-no-cache up
