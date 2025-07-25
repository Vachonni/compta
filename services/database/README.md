# compta-pkg

Load Excel files into a SQLite database.

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
uv sync
```

## Running the FastAPI App

To start the FastAPI server and make it accessible from other devices on your local network, run the following command from the project root:

```bash
uv run uvicorn database_pkg.app:app --host 0.0.0.0 --port 8000 --reload
```

This will launch the API at `http://0.0.0.0:8000` on your machine. To access it from another device on the same WiFi network, use your computer's local IP address (e.g., `http://192.168.x.x:8000`).


### Find your local IP address

To find your computer's local IP address on macOS or Linux, run:

```bash
ipconfig getifaddr en0  # macOS (WiFi)
# or
hostname -I             # Linux
```

### Example: Fetch first two lines with curl

Assuming your API is running and you have a table called `transactions`, you can get the first two rows with:

```bash
curl -X POST http://<COMPUTER_IP OR COMPUTER_NAME.local>:8000/execute_sql \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT * FROM transactions LIMIT 2;"}'
```

## Port Number Convention by Environment

For clarity and to avoid conflicts, this project uses a port pattern based on the environment:

- **Local:** Port ending with `0`(e.g., `8000`)
- **Development:** Ports ending with `1` (e.g., `8001`)
- **Staging:** Ports ending with `5` (e.g., `8005`)
- **Production:** Ports ending with `9` (e.g., `8009`)

This convention helps quickly identify which environment is running based on the port number. 

## Running Tests

To run tests using uv, use:
```sh
uv run pytest
```

## Usage

See the package documentation and source code for usage details.
