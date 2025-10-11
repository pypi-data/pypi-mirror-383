# iCost App MCP Server

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A Model Context Protocol (MCP) server for iCost application integration, providing seamless communication between AI models and the iCost cost management system.

## Features

- 🚀 **Fast and Reliable**: Built with FastAPI and modern Python async/await patterns
- 🔧 **Extensible**: Modular architecture for easy customization and extension
- 📊 **Cost Management Integration**: Direct integration with iCost application APIs
- 🛡️ **Type Safe**: Full type hints and Pydantic models for data validation
- 🧪 **Well Tested**: Comprehensive test suite with pytest
- 📚 **Well Documented**: Complete API documentation and usage examples

## Installation

### From PyPI (when published)

```bash
pip install icost-app-mcp-server
```

### From Source

```bash
git clone https://github.com/yourusername/icost-app-mcp-server.git
cd icost-app-mcp-server
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/yourusername/icost-app-mcp-server.git
cd icost-app-mcp-server
pip install -e ".[dev]"
```

## Quick Start

### Basic Usage

```python
from icost_app_mcp_server import MCPServer

# Initialize the server
server = MCPServer()

# Start the server
server.start()
```

### Configuration

```python
from icost_app_mcp_server import MCPServer

# Custom configuration
config = {
    "host": "localhost",
    "port": 8080,
    "debug": True
}

server = MCPServer(config)
server.start()
```

## Project Structure

```
icost-app-mcp-server/
├── src/
│   └── icost_app_mcp_server/
│       ├── __init__.py
│       ├── server.py
│       └── ...
├── tests/
│   ├── __init__.py
│   ├── test_server.py
│   └── ...
├── docs/
├── examples/
├── scripts/
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── README.md
└── LICENSE
```

## Development

### Setting up Development Environment

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/icost-app-mcp-server.git
   cd icost-app-mcp-server
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**:
   ```bash
   pip install -r requirements-dev.txt
   ```

4. **Install pre-commit hooks**:
   ```bash
   pre-commit install
   ```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=icost_app_mcp_server

# Run specific test file
pytest tests/test_server.py
```

### Code Formatting and Linting

```bash
# Format code with black
black src/ tests/

# Sort imports with isort
isort src/ tests/

# Lint with flake8
flake8 src/ tests/

# Type checking with mypy
mypy src/
```

### Building Documentation

```bash
cd docs/
make html
```

## API Reference

### MCPServer

The main server class for handling MCP protocol communications.

#### Methods

- `__init__(config: Optional[Dict[str, Any]] = None)`: Initialize the server
- `start()`: Start the MCP server
- `stop()`: Stop the MCP server

## Configuration

The server can be configured using a dictionary passed to the constructor:

```python
config = {
    "host": "localhost",        # Server host
    "port": 8080,              # Server port
    "debug": False,            # Debug mode
    "log_level": "INFO",       # Logging level
}
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for your changes
5. Ensure all tests pass (`pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes and version history.

## Support

- 📧 Email: your.email@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/icost-app-mcp-server/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/yourusername/icost-app-mcp-server/discussions)

## Acknowledgments

- Thanks to the MCP protocol developers
- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Inspired by modern Python development practices