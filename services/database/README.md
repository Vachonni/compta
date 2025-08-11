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
To create a virtual environment and install dependencies for production:

```sh
uv sync
```

To install all dependencies including development dependencies (for testing, linting, etc.), use:

```sh
uv sync --dev
```

This will ensure your environment includes everything needed for both running and developing the project.

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

### Example: Upload a File with curl


To upload a file with the `/upload_file` endpoint, use the following command:

```bash
curl -X POST http://<COMPUTER_IP OR COMPUTER_NAME.local>:8000/upload_file \
  -F "owner=N" \
  -F "year=2025" \
  -F "month=8" \
  -F "bank=Revolut" \
  -F "file=@<COMPLETE PATH TO FILE>" \
  -F "overwrite=false"
```

Replace `<COMPUTER_IP OR COMPUTER_NAME.local>` and `<COMPLETE PATH TO FILE>` with your actual server address and the complete path to the file you want to upload. Adjust the form fields as needed for your use case.


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
