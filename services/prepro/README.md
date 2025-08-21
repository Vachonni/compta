# prepro

Processing data. From extracted reports to standardized transactions table.

## Installation

### uv
This project uses [uv](https://github.com/astral-sh/uv) for fast Python dependency management.

If you don't have uv installed, on Linux/macOS, run:
```sh
curl -Ls https://astral.sh/uv/install.sh | bash
```
More info at:
[https://github.com/astral-sh/uv#installation](https://github.com/astral-sh/uv#installation)

### virtual environment
To create a virtual environment and install all dependencies:

```sh
uv sync --dev
```

For production, use:

```sh
uv sync
```




## Port Number Convention by Environment

For clarity and to avoid conflicts, this project uses a port pattern based on the environment:

- **Development:** Ports ending with `1` (e.g., `8001`)
- **Staging:** Ports ending with `5` (e.g., `8005`)
- **Production:** Ports ending with `9` (e.g., `8009`)

This convention helps quickly identify which environment is running based on the port number. 

## Running Tests

To run tests using uv, use:
```sh
uv run pytest
```
