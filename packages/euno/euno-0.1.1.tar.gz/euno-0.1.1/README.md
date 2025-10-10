# Euno SDK

Euno's CLI library to programmatically interact with Euno instance

## Installation

```bash
pip install euno-sdk
```

## Quick Start

### As a Library

```python
from euno import hello_world

# Use the hello_world function
message = hello_world("Euno")
print(message)  # Output: Hello, Euno! Welcome to the Euno SDK!
```

### As a CLI Tool

```bash
# Hello world command
euno hello-world --name Euno

# Show version
euno version

# Show help
euno --help
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/euno-ai/euno-sdk.git
cd euno-sdk

# Install development dependencies
pip install -r requirements-dev.txt

# Install the package in development mode
pip install -e .
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black euno tests
```

### Type Checking

```bash
mypy euno
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for your changes
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.