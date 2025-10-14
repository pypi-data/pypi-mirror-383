# EpochFlow - Algorithm Graph Compiler

[![PyPI version](https://badge.fury.io/py/epochflow.svg)](https://badge.fury.io/py/epochflow)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**EpochFlow** is a compiler that transforms Python-like algorithm specifications into dataflow graph representations. It parses constrained Python syntax using AST compilation and generates node/edge graphs suitable for execution by dataflow runtime engines.

## Features

- 🐍 **Pure Python AST Parsing** - No custom grammar or parsers needed
- 🔄 **Automatic Type Casting** - Seamless Boolean ↔ Number conversions
- ⏰ **Timeframe Validation** - Built-in pandas offset validation
- 🔌 **Extensible Registry** - Plugin your own component metadata
- 🚀 **Zero Dependencies** - Only Python standard library required
- 🎯 **Type Safe** - Full type hints support
- 📦 **Standalone Package** - Use independently or with EpochAI

## Installation

```bash
pip install epochflow
```

### Optional Dependencies

```bash
# For timeframe validation
pip install epochflow[pandas]

# For development
pip install epochflow[dev]
```

## Quick Start

### Basic Usage

```python
from epochflow import compile_algorithm, set_transforms_list

# Define your component metadata
transforms = [
    {
        "id": "market_data_source",
        "inputs": [],
        "outputs": [{"id": "close"}, {"id": "volume"}],
        "options": [{"id": "timeframe"}],
        "requiresTimeFrame": True,
    },
    {
        "id": "sma",
        "inputs": [{"id": "source"}],
        "outputs": [{"id": "result"}],
        "options": [{"id": "period"}],
    }
]

# Set transforms metadata
set_transforms_list(transforms)

# Compile algorithm code
code = """
src = market_data_source(timeframe="1D")
sma_20 = sma(period=20)(src.close)
"""

result = compile_algorithm(code)
print(result)
# Output: {'nodes': [...], 'edges': [...]}
```

### Advanced Usage with Custom Loader

```python
from epochflow import set_transforms_loader, compile_algorithm
import requests

# Define a custom loader function
def load_transforms():
    response = requests.get("https://api.example.com/transforms")
    return response.json()

# Set the loader
set_transforms_loader(load_transforms)

# Compile (automatically loads transforms when needed)
result = compile_algorithm("src = market_data_source(timeframe='1H')")
```

## Syntax Overview

EpochFlow supports a constrained subset of Python:

### Variable Assignment
```python
src = market_data_source(timeframe="1D")
ema_fast = ema(period=12)(src.close)
```

### Operators
```python
# Arithmetic
result = a + b - c * d / e

# Comparison
condition = price > threshold

# Logical
signal = long_condition and not short_condition
```

### Lag Operator (Subscript)
```python
prev_close = src.close[1]  # Previous bar
```

### Ternary Expressions
```python
value = high_val if condition else low_val
```

### Tuple Unpacking
```python
upper, middle, lower = bollinger_bands(period=20)(src.close)
```

## API Reference

### Core Functions

#### `compile_algorithm(source, registry=None, transforms_list=None)`
Compiles algorithm code to node/edge graph.

**Parameters:**
- `source` (str): Algorithm code in EpochFlow syntax
- `registry` (dict, optional): Pre-built registry dictionary
- `transforms_list` (list, optional): Transform metadata for type checking

**Returns:** `dict` with `nodes` and `edges` keys

#### `set_transforms_list(transforms)`
Set transforms metadata directly.

**Parameters:**
- `transforms` (list): List of transform metadata dictionaries

#### `set_transforms_loader(loader)`
Set a custom loader function for transforms.

**Parameters:**
- `loader` (callable): Function that returns transform metadata list

#### `get_transforms_list()`
Get currently configured transforms metadata.

**Returns:** `list` or `None`

### Classes

#### `AlgorithmCompiler(registry, transforms_list=None)`
Low-level compiler class for advanced usage.

## Transform Metadata Format

Transforms metadata should be a list of dictionaries:

```python
{
    "id": "component_name",
    "inputs": [
        {"id": "input_name", "type": "Number"}
    ],
    "outputs": [
        {"id": "output_name", "type": "Decimal"}
    ],
    "options": [
        {"id": "parameter_name", "type": "integer"}
    ],
    "requiresTimeFrame": False,
    "isCrossSectional": False,
    "atLeastOneInputRequired": True,
    "category": "Indicators"
}
```

## Examples

See [STANDALONE_USAGE.md](STANDALONE_USAGE.md) for comprehensive examples including:
- Simple moving average crossover
- FastAPI integration
- Custom component metadata
- Error handling patterns

## Architecture

```
EpochFlow Components:
├── compiler/
│   └── ast_compiler.py    # AST parsing and graph generation
├── registry/
│   └── transform_registry.py  # Component metadata management
└── syntax/
    └── rules.py           # Syntax documentation for LLMs
```

**Design Philosophy:**
- Constrained Python syntax with direct AST compilation
- No custom grammar or structured parsers
- Optimized for LLM code generation
- Clean separation of parsing and validation

## Use Cases

- **Trading Strategies**: Compile algorithm specs for backtesting engines
- **Data Pipelines**: Transform declarative specs into execution graphs
- **Visual Programming**: Backend for node-based editors
- **Code Generation**: Target for LLM-generated algorithm code
- **Research Tools**: Analyze and validate quantitative strategies

## Integration with EpochAI

EpochFlow was extracted from the EpochAI project and maintains full backward compatibility. When used within EpochAI, it automatically detects and uses the parent project's transform metadata.

```python
# In EpochAI - works automatically
from epochflow import compile_algorithm
result = compile_algorithm(code)  # Uses EpochAI's metadata
```

## Development

```bash
# Clone the repository
git clone https://github.com/epochai/epochflow.git
cd epochflow

# Install in development mode
pip install -e .[dev]

# Run tests
pytest

# Format code
black .
ruff check --fix .
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=epochflow --cov-report=html

# Run specific test file
pytest epochflow/tests/test_py_algo_ast_compiler.py
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [GitHub README](https://github.com/epochai/epochflow#readme)
- **Issues**: [GitHub Issues](https://github.com/epochai/epochflow/issues)
- **Discussions**: [GitHub Discussions](https://github.com/epochai/epochflow/discussions)

## Changelog

See [CHANGELOG.md](https://github.com/epochai/epochflow/releases) for version history.

## Acknowledgments

EpochFlow is part of the EpochAI quantitative trading platform ecosystem.

---

Made with ❤️ by the EpochAI Team
