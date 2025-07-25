# compta

A repository for managing accounting-related code and resources.

## Project Structure

```
compta/
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
          config.py
          excel_to_sqlite.py
          utils.py
      tests/
        test_app.py
  shared/
    __init__.py
    config/
      __init__.py
      settings.py
  .github/
  .gitignore
  README.md
```

## Description
- **database/**: Contains the database service, source code, and tests.
- **shared/**: Shared modules and configuration used across the project.

---

Feel free to update this README as the project evolves.
