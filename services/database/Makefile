
# Makefile for database-pkg.
# To run a make command, use `make <target>`...
# ...from any directory, use `make -C /Users/nicholas/Code/compta/database <target>`


# GitHub Container Registry path (without image name or tag)
GITHUB_REGISTRY=ghcr.io/$(shell echo $$(git config --get remote.origin.url) | sed -E 's#.*/([^/]+)/compta.*#\1#' | tr '[:upper:]' '[:lower:]')

.PHONY: helprun-app pytest docker-build-dev docker-run-dev docker-up-dev docker-run-staging

help:
	@echo "Available targets:"
	@echo "  run-app           Run the FastAPI app locally with uvicorn and reload."
	@echo "  pytest            Run tests using pytest."
	@echo "  docker-build-dev  Build the dev Docker image only (does not run)."
	@echo "  docker-run-dev    Run the dev Docker container (does not rebuild)."
	@echo "  docker-up-dev     Build and run the dev Docker container."
	@echo "  docker-run-staging  Pull and run the staging Docker image with .env.staging."

run-app:
	uv run uvicorn database_pkg.app:app --host 0.0.0.0 --port 8000 --reload

pytest:
	uv run pytest

docker-build-dev: 
	docker-compose --env-file .env.dev build compa-data-app
docker-run-dev: 
	docker-compose --env-file .env.dev up --no-build compa-data-app
	# Note: This will not rebuild the image, use `docker-build-dev` first if
docker-up-dev: 
	docker-compose --env-file .env.dev up --build

docker-run-staging: 
	docker pull $(GITHUB_REGISTRY)/compta-data-app:staging
	docker run --env-file .env.staging -p 8005:8000 -v /Users/nicholas/Databases:/app/DatabasesMount $(GITHUB_REGISTRY)/compta-data-app:staging


