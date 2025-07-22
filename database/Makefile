# Makefile for compta-pkg

.PHONY: run test

run:
	uv run uvicorn database_pkg.app:app --host 0.0.0.0 --port 8000 --reload

test:
	uv run pytest
