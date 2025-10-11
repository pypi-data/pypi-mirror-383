# dql-parser

[![CI](https://github.com/dql-project/dql-parser/actions/workflows/ci.yml/badge.svg)](https://github.com/dql-project/dql-parser/actions)
[![PyPI](https://img.shields.io/pypi/v/dql-parser)](https://pypi.org/project/dql-parser/)
[![Python](https://img.shields.io/pypi/pyversions/dql-parser)](https://pypi.org/project/dql-parser/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Pure Python parser for Data Quality Language (DQL) - a human-readable language for defining data quality expectations.

**[Documentation](https://yourusername.github.io/dql-parser/)** | **[PyPI](https://pypi.org/project/dql-parser/)** | **[GitHub](https://github.com/dql-project/dql-parser)**

## Features

- 🚀 **Zero Dependencies** (except Lark parser)
- 🎯 **Framework-Agnostic** - No Django, Flask, or any framework required
- ⚡ **Fast** - Parses 100-line DQL files in <50ms
- 📝 **Clear Error Messages** - Line and column information for syntax errors
- 🐍 **Python 3.8+** - Supports Python 3.8 through 3.12

## Installation

```bash
pip install dql-parser
```

## Quick Start

```python
from dql_parser import DQLParser

# Parse DQL text
parser = DQLParser()
ast = parser.parse("""
FROM Customer
EXPECT column("email") to_not_be_null SEVERITY critical
EXPECT column("age") to_be_between(18, 120)
""")

# Access parsed expectations
for from_block in ast.from_blocks:
    print(f"Model: {from_block.model_name}")
    for expectation in from_block.expectations:
        print(f"  - {expectation.operator}")
```

## DQL Syntax Overview

DQL (Data Quality Language) is a declarative language for defining data quality rules:

```dql
FROM ModelName

EXPECT column("field_name") to_not_be_null SEVERITY critical
EXPECT column("email") to_match_pattern("[a-z]+@[a-z]+\\.[a-z]+")
EXPECT column("age") to_be_between(0, 150)
EXPECT column("status") to_be_in("active", "pending", "closed")
EXPECT column("id") to_be_unique
```

### Supported Operators

- `to_be_null` - Column must be NULL
- `to_not_be_null` - Column must not be NULL
- `to_match_pattern(regex)` - Column must match regex pattern
- `to_be_between(min, max)` - Column must be between min and max
- `to_be_in(value1, value2, ...)` - Column must be one of the values
- `to_be_unique` - Column must have unique values

### Severity Levels

- `critical` - Must pass for validation to succeed
- `warning` - Logged but doesn't fail validation
- `info` - Informational only

## API Reference

### `DQLParser`

Main parser class for DQL syntax.

```python
parser = DQLParser()
```

#### `parse(text: str) -> DQLFile`

Parse DQL text and return AST.

**Args:**
- `text`: DQL source text

**Returns:**
- `DQLFile`: Root AST node

**Raises:**
- `DQLSyntaxError`: If syntax is invalid

#### `parse_file(filepath: str) -> DQLFile`

Parse DQL file and return AST.

**Args:**
- `filepath`: Path to .dql file

**Returns:**
- `DQLFile`: Root AST node

**Raises:**
- `DQLSyntaxError`: If syntax is invalid
- `FileNotFoundError`: If file doesn't exist

### AST Nodes

The parser returns an Abstract Syntax Tree (AST) composed of dataclass nodes:

- `DQLFile` - Root node containing `from_blocks`
- `FromBlock` - Represents a FROM block with `model_name` and `expectations`
- `ExpectationNode` - Single expectation with `target`, `operator`, `severity`
- `ColumnTarget` - Column reference
- `RowTarget` - Row-level condition
- Operators: `ToBeNull`, `ToNotBeNull`, `ToMatchPattern`, `ToBeBetween`, `ToBeIn`, `ToBeUnique`

## Error Handling

DQL parser provides clear, actionable error messages:

```python
try:
    ast = parser.parse("EXPECT column('email') invalid_operator")
except DQLSyntaxError as e:
    print(e)
    # Output: Syntax error at line 1, column 30: unexpected token 'invalid_operator'
```

## Development

### Setup

```bash
# Clone repository
git clone https://github.com/dql-project/dql-parser.git
cd dql-parser

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=dql_parser --cov-report=html

# Run specific test file
pytest tests/test_valid_syntax.py
```

### Code Quality

```bash
# Format code
black dql_parser tests

# Lint code
flake8 dql_parser tests

# Type check
mypy dql_parser
```

## Documentation

**Full documentation:** https://yourusername.github.io/dql-parser/

- [Grammar Reference](https://yourusername.github.io/dql-parser/grammar-reference/) - Complete DQL syntax specification
- [AST Reference](https://yourusername.github.io/dql-parser/ast-reference/) - AST node documentation
- [Examples](https://yourusername.github.io/dql-parser/examples/) - Usage examples
- [API Reference](https://yourusername.github.io/dql-parser/api-reference/) - Complete API

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Related Projects

- **[dql-core](https://github.com/dql-project/dql-core)** - Framework-agnostic validation engine ([docs](https://yourusername.github.io/dql-core/))
- **[django-dqm](https://github.com/dql-project/django-dqm)** - Django integration with Admin dashboard ([docs](https://yourusername.github.io/django-dqm/))

## Package Selection

Not sure which package to use? See the **[Package Selection Guide](https://yourusername.github.io/django-dqm/package-selection/)**

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.
