# compta

A repository for managing accounting-related code and resources.

## Project Structure

```
Makefile
README.md
scripts/
  health-check.sh
  test-sql.sh
services/
  database/
    docker-compose.yml
    Dockerfile
    Makefile
    pyproject.toml
    README.md
    uv.lock
    src/
      database_pkg/
        __init__.py
        app.py
        excel_to_sqlite.py
        utils.py
        config/
          __init__.py
          logs.py
          schemas.py
          settings.py
    tests/
      test_app.py
      test_settings.py
shared/
  __init__.py
  config/
    __init__.py
    logging_config.py
    settings.py
.github/
  actions/
    build-to-ghcr/action.yml
    deploy-docker-local/action.yml
    python-build-test/action.yml
  workflows/
    build-and-deploy.yml
    ci-cd-database.yml
.gitignore
```


## Databases Structure

```
Databases/
  compta/
    blob/
      dev/
        Legacy/
          REVOLUT AVRIL 2025.xlsx
        raw/
          2025/
      prod/
        raw/
          2025/
    SQL/
      prod.db
      dev.db
```

## Description
- **database/**: Contains the database service, source code, and tests.
- **shared/**: Shared modules and configuration used across the project.

---

Feel free to update this README as the project evolves.

## Self-hosted GitHub Actions Runner (macOS)

This project deploys containers to a local machine using a self-hosted GitHub Actions runner.

For setup, follow GitHub’s official guide: https://docs.github.com/en/actions/hosting-your-own-runners/adding-self-hosted-runners

Notes for this repo:
- Install the runner under `~/actions-runner` (matches the Makefile target).
- Docker Desktop must be running (the deploy steps use `docker`).
- Workflows run on `runs-on: self-hosted` (default labels are fine).

Run the runner from the repo root:

```bash
make run-runner
```

Required GitHub Environment variables (Settings → Environments) for `staging` and `prod`:
- `APP_ENV` (e.g., `staging` or `prod`)
- `LOCAL_DATABASES_DIR` (host path on your Mac, e.g., `/Users/<you>/Databases/compta`)
- `DOCKER_DATABASES_DIR` (container path, e.g., `/data`)

These are used to mount `${LOCAL_DATABASES_DIR}:${DOCKER_DATABASES_DIR}` during deployment.

Trigger: push to `staging` or `main` (see `.github/workflows/ci-cd-database.yml`). Ports: staging `8005:8000`, production `8009:8000`.
