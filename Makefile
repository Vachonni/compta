# Root Makefile for compta
# Proxy Makefile to run database service Makefile targets from the root

DATABASE_DIR=services/database


.PHONY: help database-run-app database-pytest database-docker-build-dev database-docker-run-dev database-docker-up-dev database-docker-run-staging
help:
	@echo "Root Makefile for compta:"
	@echo "  help                        Show this help message."
	@echo "  database-run-app            Run the FastAPI app for the database service."
	@echo "  database-pytest             Run tests for the database service."
	@echo "  database-docker-build-dev   Build the dev Docker image for the database service."
	@echo "  database-docker-run-dev     Run the dev Docker container for the database service."
	@echo "  database-docker-up-dev      Build and run the dev Docker container for the database service."
	@echo "  database-docker-run-staging Pull and run the staging Docker image for the database service."


database-run-app:
	$(MAKE) -C $(DATABASE_DIR) run-app

database-pytest:
	$(MAKE) -C $(DATABASE_DIR) pytest

database-docker-build-dev:
	$(MAKE) -C $(DATABASE_DIR) docker-build-dev

database-docker-run-dev:
	$(MAKE) -C $(DATABASE_DIR) docker-run-dev

database-docker-up-dev:
	$(MAKE) -C $(DATABASE_DIR) docker-up-dev

database-docker-run-staging:
	$(MAKE) -C $(DATABASE_DIR) docker-run-staging
