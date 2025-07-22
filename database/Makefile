# Makefile for database-pkg
# To run a make command, use `make <target>`...
# ...from any directory, use `make -C /Users/nicholas/Code/compta/database <target>`

.PHONY: run-app pytest


run-app:
	uv run uvicorn database_pkg.app:app --host 0.0.0.0 --port 8000 --reload

pytest:
	uv run pytest
