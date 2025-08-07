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
    deploy-docker-mbpnv/action.yml
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
