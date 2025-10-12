# Civic Transparency CWE Types

**Immutable, typed result objects for CWE, Standards, and Schema workflows.**
This library provides a small set of frozen dataclasses and helpers for loading data, validation, relationship analysis, and machine-friendly summaries, with strict typing and zero runtime dependencies.

---

## Quick Install

```bash
pip install civic-transparency-py-cwe-types
```

Requirements: Python 3.12+ (no additional runtime dependencies, includes typing support)

---

## Design

- **Immutable by default** - all operations return new objects; originals never modified.
- **Composition-first** - domain results build on small base collections/counters/messages.
- **Strictly typed** - `py.typed` included; designed for strict type checkers.
- **Leaf-module imports** - no `__init__` re-exports; uses explicit dependency imports.

  Import from specific modules, e.g.:

  - `ci.transparency.cwe.types.cwe.results`
  - `ci.transparency.cwe.types.standards.results`
  - `ci.transparency.cwe.types.cwe.schema.results`

---

## Example

```python
from ci.transparency.cwe.types.cwe.results import CweLoadingResult, add_cwe

result = CweLoadingResult()
result = add_cwe(result, "CWE-79", {
    "id": "CWE-79",
    "name": "Cross-site Scripting",
    "category": "injection"
})

print(result.cwe_count)  # 1
```

---

## What's Included

| Domain         | Purpose                               | Key Results                                                        |
| -------------- | ------------------------------------- | ------------------------------------------------------------------ |
| **CWE**        | Load, validate, analyze CWE data      | `CweLoadingResult`, `CweValidationResult`, `CweRelationshipResult` |
| **Standards**  | Framework loading & CWE mappings      | `StandardsLoadingResult`, `StandardsMappingResult`                 |
| **Schema**     | Generic schema operations             | `SchemaLoadingResult`, `SchemaValidationResult`                    |
| **CWE Schema** | Domain-specific CWE schema validation | `CweSchemaLoadingResult`, `CweSchemaValidationResult`              |
| **Base**       | Shared building blocks                | `MessageCollection`, `LoadingCounts`, `ValidationCounts`           |

---

## Documentation

- **[Usage Guide](./usage.md)** - practical examples & patterns
- **API Reference** - auto-generated from docstrings (see sidebar)
- **[CHANGELOG](https://github.com/civic-interconnect/civic-transparency-py-cwe-types/blob/main/CHANGELOG.md)**
- **[CONTRIBUTING](https://github.com/civic-interconnect/civic-transparency-py-cwe-types/blob/main/CONTRIBUTING.md)**

---

## License

MIT © [Civic Interconnect](https://github.com/civic-interconnect)
