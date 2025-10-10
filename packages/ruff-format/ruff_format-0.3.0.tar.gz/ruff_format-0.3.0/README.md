# ruff-format

A fast Python code formatter powered by [Ruff](https://github.com/astral-sh/ruff)'s formatting engine.

## Overview

`ruff-format` is a Python package that provides Python bindings to Ruff's Python formatter.

## Installation

```bash
pip install ruff-format
```

## Usage

```python
from ruff_format import format_string

code = """
def hello(  x,y,   z  ):
    print( x+y+z )
"""

formatted = format_string(code)
print(formatted)
```

## Development

### Prerequisites

- Rust (latest stable)
- Python 3.8+
- [maturin](https://github.com/PyO3/maturin)

### Building from source

```bash
# Install maturin
pip install maturin

# Build the package
maturin develop

# Or build a release version
maturin build --release
```

## License

MIT

## Links

- [Repository](https://github.com/reflex-dev/ruff-format)
- [Ruff](https://github.com/astral-sh/ruff)
