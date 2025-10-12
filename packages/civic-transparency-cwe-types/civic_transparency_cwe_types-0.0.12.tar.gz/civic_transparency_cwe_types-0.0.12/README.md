# Civic Transparency CWE Types

[![Docs](https://img.shields.io/badge/docs-mkdocs--material-blue)](https://civic-interconnect.github.io/civic-transparency-py-cwe-types/)
[![PyPI](https://img.shields.io/pypi/v/civic-transparency-py-cwe-types.svg)](https://pypi.org/project/civic-transparency-py-cwe-types/)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue?logo=python)](#)
[![CI Status](https://github.com/civic-interconnect/civic-transparency-py-cwe-types/actions/workflows/ci.yml/badge.svg)](https://github.com/civic-interconnect/civic-transparency-py-cwe-types/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)

**Immutable, typed result objects for CWE, Standards, and Schema workflows.**

Provides strongly-typed Python models for Common Weakness Enumeration (CWE) analysis, standards framework mappings, and schema validation workflows.

## Features

- **Zero Dependencies** - Pure Python with no external requirements
- **Immutable Design** - Functional-style helpers return new instances
- **Type Safety** - Full static typing with `py.typed` marker
- **Composable** - Small building blocks for complex workflows
- **Memory Efficient** - Frozen dataclasses for better performance

## Installation

```bash
pip install civic-transparency-py-cwe-types
```

**Requirements:** Python 3.12+

## Quick Start

```python
from ci.transparency.cwe.types.cwe.results import CweLoadingResult, add_cwe

# Create immutable result objects
result = CweLoadingResult()
result = add_cwe(result, "CWE-79", {
    "id": "CWE-79",
    "name": "Cross-site Scripting",
    "category": "injection"
})

print(f"Loaded CWEs: {result.cwe_count}")
print(f"Has errors: {result.messages.has_errors}")
```

## What's Included

| Domain         | Purpose                               | Key Results                                                        |
| -------------- | ------------------------------------- | ------------------------------------------------------------------ |
| **CWE**        | Load, validate, analyze CWE data      | `CweLoadingResult`, `CweValidationResult`, `CweRelationshipResult` |
| **Standards**  | Framework loading & CWE mappings      | `StandardsLoadingResult`, `StandardsMappingResult`                 |
| **Schema**     | Generic schema operations             | `SchemaLoadingResult`, `SchemaValidationResult`                    |
| **CWE Schema** | Domain-specific CWE schema validation | `CweSchemaLoadingResult`, `CweSchemaValidationResult`              |

## Documentation

- **[Usage Guide](https://civic-interconnect.github.io/civic-transparency-py-cwe-types/usage/)** - Detailed examples and patterns
- **[API Reference](https://civic-interconnect.github.io/civic-transparency-py-cwe-types/api/)** - Complete module documentation
- **[Contributing](./CONTRIBUTING.md)** - Development guidelines

## Development

```bash
git clone https://github.com/civic-interconnect/civic-transparency-py-cwe-types
cd civic-transparency-py-cwe-types
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv sync --extra dev --extra docs
```

Run tests:

```bash
uv run pytest
uv run pyright src/
```

## Versioning

This specification follows semantic versioning.
See [CHANGELOG.md](./CHANGELOG.md) for version history.

## License

MIT © [Civic Interconnect](https://github.com/civic-interconnect)
