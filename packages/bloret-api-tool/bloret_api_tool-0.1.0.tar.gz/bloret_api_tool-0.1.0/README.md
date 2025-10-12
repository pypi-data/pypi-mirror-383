# Bloret Launcher API Tool

A Python library for interacting with Bloret Launcher API. This library can be used both as a module that you can import in your Python applications and as a command-line tool using the `BLAPI` command.

## Installation

```bash
pip install bloret-api-tool
```

Or install from source:

```bash
pip install .
```

## Usage

### As a Library

```python
from bloret_api_tool import Client, request_api

# Using the Client class
client = Client(base_url="https://api.bloret.com", token="your-token")
response = client.request("GET", "/v1/games")

# Using the convenience function
response = request_api("GET", "/v1/games", token="your-token")
```

### As a Command-Line Tool

After installation, you can use the `BLAPI` command:

```bash
# Make a GET request
BLAPI get /v1/games

# Make a POST request with data
BLAPI post /v1/games --data '{"name": "New Game"}'

# Specify a custom base URL and token
BLAPI --base-url https://api.bloret.com --token your-token get /v1/games

# Save output to a file
BLAPI get /v1/games --output games.json
```

## Commands

- `get` - Make a GET request to an endpoint
- `post` - Make a POST request to an endpoint
- `put` - Make a PUT request to an endpoint
- `delete` - Make a DELETE request to an endpoint

## Options

- `--base-url` - Base URL for the API (default: https://api.bloret.com)
- `--token` - Authorization token for API requests
- `--output`, `-o` - Output file (default: stdout)

## Development

To install the package in development mode:

```bash
pip install -e .
```

To run tests:

```bash
pytest
```

## License

MIT