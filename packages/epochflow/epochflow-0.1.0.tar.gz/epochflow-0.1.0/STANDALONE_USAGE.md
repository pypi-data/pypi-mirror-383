# EpochFlow Standalone Usage Guide

## Installation

```bash
# Once published to PyPI
pip install epochflow

# For now (local development)
pip install -e ./epochflow
```

## Quick Start

### 1. Prepare Your Transforms Metadata

EpochFlow needs transforms metadata to compile algorithms. You can provide this in two ways:

#### Option A: Direct Assignment
```python
from epochflow import set_transforms_list, compile_algorithm
import json

# Load your transforms metadata
with open("transforms.json") as f:
    transforms = json.load(f)

# Set it globally
set_transforms_list(transforms)

# Now you can compile
code = """
src = market_data_source(timeframe="1D")
ema_fast = ema(period=12)(src.close)
ema_slow = ema(period=26)(src.close)
"""

result = compile_algorithm(code)
print(result)
```

#### Option B: Custom Loader Function
```python
from epochflow import set_transforms_loader, compile_algorithm
import requests

# Define a loader that fetches from your API
def load_transforms():
    response = requests.get("https://api.example.com/transforms")
    return response.json()

# Set the loader
set_transforms_loader(load_transforms)

# Compile (will automatically call loader when needed)
result = compile_algorithm("src = market_data_source(timeframe='1D')")
```

### 2. Transforms Metadata Format

Your transforms metadata should be a list of dictionaries with this structure:

```json
[
  {
    "id": "market_data_source",
    "inputs": [],
    "outputs": [
      {"id": "open"},
      {"id": "high"},
      {"id": "low"},
      {"id": "close"},
      {"id": "volume"}
    ],
    "options": [
      {"id": "timeframe", "type": "string"}
    ],
    "requiresTimeFrame": true,
    "isCrossSectional": false,
    "atLeastOneInputRequired": false,
    "category": "DataSource"
  },
  {
    "id": "ema",
    "inputs": [{"id": "source"}],
    "outputs": [{"id": "result"}],
    "options": [
      {"id": "period", "type": "integer"}
    ],
    "requiresTimeFrame": false,
    "isCrossSectional": false,
    "atLeastOneInputRequired": true,
    "category": "MovingAverage"
  }
]
```

## API Reference

### Core Compilation

```python
from epochflow import compile_algorithm, AlgorithmCompiler

# Simple compilation (uses global transforms)
result = compile_algorithm(code)

# Advanced: Provide registry explicitly
from epochflow import build_transform_registry

transforms = [...]  # Your transforms
registry = build_transform_registry(transforms)
result = compile_algorithm(code, registry=registry)
```

### Transform Registry Management

```python
from epochflow import (
    set_transforms_list,
    set_transforms_loader,
    get_transforms_list,
    build_transform_registry,
)

# Set transforms directly
set_transforms_list(transforms_list)

# Set a loader function
set_transforms_loader(loader_function)

# Get current transforms
transforms = get_transforms_list()

# Build registry from transforms
registry = build_transform_registry(transforms)
```

### Syntax Rules (for LLM Agents)

```python
from epochflow import STRATEGY_BUILDER_RULE, QUANT_RESEARCHER_RULE

# Use in your LLM prompts
prompt = f"""
You are a trading strategy builder.

{STRATEGY_BUILDER_RULE}

User request: Build a moving average crossover strategy
"""
```

## Examples

### Example 1: Simple Moving Average

```python
from epochflow import set_transforms_list, compile_algorithm

# Minimal transforms for this example
transforms = [
    {
        "id": "market_data_source",
        "inputs": [],
        "outputs": [{"id": "c"}, {"id": "o"}, {"id": "h"}, {"id": "l"}, {"id": "v"}],
        "options": [{"id": "timeframe"}],
        "requiresTimeFrame": True,
        "isCrossSectional": False,
        "atLeastOneInputRequired": False,
    },
    {
        "id": "sma",
        "inputs": [{"id": "source"}],
        "outputs": [{"id": "result"}],
        "options": [{"id": "period"}],
        "requiresTimeFrame": False,
        "isCrossSectional": False,
        "atLeastOneInputRequired": True,
    }
]

set_transforms_list(transforms)

code = """
src = market_data_source(timeframe="1D")
sma_20 = sma(period=20)(src.c)
"""

result = compile_algorithm(code)
print(f"Compiled {len(result['nodes'])} nodes, {len(result['edges'])} edges")
```

### Example 2: Using with FastAPI

```python
from fastapi import FastAPI, HTTPException
from epochflow import set_transforms_loader, compile_algorithm
import httpx

app = FastAPI()

# Setup transforms loader
async def load_transforms():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/transforms")
        return response.json()

# Load on startup
@app.on_event("startup")
async def startup():
    transforms = await load_transforms()
    set_transforms_list(transforms)

@app.post("/compile")
async def compile_endpoint(code: str):
    try:
        result = compile_algorithm(code)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

## Troubleshooting

### ImportError: No transforms metadata available

**Problem:** You haven't provided transforms metadata.

**Solution:**
```python
from epochflow import set_transforms_list
transforms = [...]  # Load your transforms
set_transforms_list(transforms)
```

### RuntimeError: Transform registry unavailable

**Problem:** Registry couldn't be built (empty transforms list).

**Solution:** Ensure your transforms list is not empty and properly formatted.

### Compilation errors

**Problem:** Code uses components not in your transforms metadata.

**Solution:** Either add the missing components to your transforms, or fix the algorithm code.

## Migration from EpochAI

If you're already using EpochFlow within the EpochAI project, no changes are needed! The package automatically detects and uses `common.data_utils.doc.TRANSFORMS_LIST` when available.

## Support

- GitHub Issues: https://github.com/your-org/epochflow/issues
- Documentation: https://epochflow.readthedocs.io
