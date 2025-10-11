# RabbitMQ MCP Server
A [Model Context Protocol](https://www.anthropic.com/news/model-context-protocol) server implementation for RabbitMQ operation.

## Features

### Manage your RabbitMQ message brokers using AI agent
This MCP servers wraps admin APIs of a RabbitMQ broker as MCP tools.

### Supports streamable HTTP with FastMCP's `BearerAuthProvider`
You can start a remote RabbitMQ MCP server by configuring your own IdP and 3rd party authorization provider.

### Seamless integration with MCP clients
The package is available on PyPI, you can use uvx without having to fork and build the MCP server locally first.


## Installation

### PyPI

https://pypi.org/project/mcp-server-rabbitmq/

Use uvx directly in your MCP client config

```json
{
    "mcpServers": {
      "rabbitmq": {
        "command": "uvx",
        "args": [
            "amq-mcp-server-rabbitmq@latest",
            "--allow-mutative-tools"
        ]
      }
    }
}
```

### From source
1. Clone this repository.

```json
{
    "mcpServers": {
      "rabbitmq": {
        "command": "uv",
        "args": [
            "--directory",
            "/path/to/repo/mcp-server-rabbitmq",
            "run",
            "amq-mcp-server-rabbitmq",
            "--allow-mutative-tools"
        ]
      }
    }
}
```

### Configuration
`--allow-mutative-tools`: if specificy, it will enable tools that can mutate broker states. Default is false.

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/amazon-mq/mcp-server-rabbitmq.git
cd mcp-server-rabbitmq

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
pytest
```

### Code Quality

This project uses ruff for linting and formatting:

```bash
# Run linter
ruff check .

# Run formatter
ruff format .
```

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.
