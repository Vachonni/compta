# Makefile for database-pkg.
# To run a make command, use `make <target>`...
# ...from any directory, use `make -C /Users/nicholas/Code/compta/database <target>`


# !!!!!!! WARNING !!!!!!! USING ENVIRONMENT VARIABLES FROM .env.dev FILE !!!!!!! WARNING !!!!!!!
include .env.dev
# !!!!!!! WARNING !!!!!!! USING ENVIRONMENT VARIABLES FROM .env.dev FILE !!!!!!! WARNING !!!!!!!


.PHONY: run-app pytest docker-build docker-run print-vars


run-app:
	uv run uvicorn database_pkg.app:app --host 0.0.0.0 --port 8000 --reload

pytest:
	uv run pytest

docker-build: # Run in development mode
	docker build \
	  --build-arg DATABASES_DIR=$(DATABASES_DIR) \
	  --build-arg ENVIRONMENT=$(ENVIRONMENT) \
	  -t compta-data-app:latest .
docker-run: # Run in development mode
	docker run -p 8001:8000 \
	  -v /Users/nicholas/Databases:/app/DatabasesMount \
	  -e DATABASES_DIR=$(DATABASES_DIR) \
	  -e ENVIRONMENT=$(ENVIRONMENT) \
	  compta-data-app:latest

print-vars:
	@echo "DATABASES_DIR=$(DATABASES_DIR)"
	@echo "ENVIRONMENT=$(ENVIRONMENT)"
