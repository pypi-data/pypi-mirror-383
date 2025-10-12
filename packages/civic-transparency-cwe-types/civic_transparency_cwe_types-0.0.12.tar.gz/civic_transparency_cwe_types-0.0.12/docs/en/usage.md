# Usage Guide

This guide shows common patterns for using the **Civic Transparency CWE Types** library.

## Installation

```bash
pip install civic-transparency-py-cwe-types
```

## Core Concepts

### Immutability & Composition

Operations **return new dataclass instances**; originals are never modified.

```python
from pathlib import Path
from ci.transparency.cwe.types.cwe.results import CweLoadingResult, add_cwe

result = CweLoadingResult()
result2 = add_cwe(
    result,
    "CWE-79",
    {"id": "CWE-79", "name": "Cross-site Scripting", "category": "injection", "relationships": []},
    file_path=Path("cwe-79.yaml"),
)

assert result is not result2
print(result.cwe_count)   # 0
print(result2.cwe_count)  # 1
```

### Explicit Types, Strong Guarantees

Helper functions preserve concrete result types:

```python
from ci.transparency.cwe.types.cwe.results import CweLoadingResult, add_cwe

cwe_result = CweLoadingResult()
updated = add_cwe(cwe_result, "CWE-89", {"id": "CWE-89", "name": "SQL Injection"})
print(type(updated) is CweLoadingResult)  # True
```

## Base Building Blocks

The domain results compose a few base structures:

- `LoadingCounts` / `ValidationCounts` - tracked on results
- `MessageCollection` - `errors`, `warnings`, `infos` with convenience properties

Typically operate through domain helpers, but can also access them directly:

```python
from dataclasses import replace
from ci.transparency.cwe.types.base.counts import LoadingCounts
from ci.transparency.cwe.types.base.messages import MessageCollection

loading = LoadingCounts()
loading = replace(loading, loaded_count=loading.loaded_count + 1)

messages = MessageCollection()
messages = replace(messages, errors=messages.errors + ["Something went wrong"])
print(messages.has_errors)  # True
```

---

## CWE Domain

### Load CWE data

```python
from pathlib import Path
from ci.transparency.cwe.types.cwe.results import (
    CweLoadingResult, add_cwe, track_invalid_file, get_cwe_loading_summary
)

result = CweLoadingResult()

# Add one CWE
cwe79 = {
    "id": "CWE-79",
    "name": "Cross-site Scripting",
    "category": "injection",
    "relationships": [{"cwe_id": "CWE-80", "type": "child"}],
}
result = add_cwe(result, "CWE-79", cwe79, file_path=Path("cwe-79.yaml"))

# Track a failed file
result = track_invalid_file(result, Path("broken.yaml"), "Malformed YAML")

summary = get_cwe_loading_summary(result)
print(summary["cwes_loaded"], summary["failed_files"])
```

### Validate CWE records

```python
from ci.transparency.cwe.types.cwe.results import (
    CweValidationResult, validate_cwe, batch_validate_cwes, get_cwe_validation_summary
)

validation = CweValidationResult()

validation = validate_cwe(
    validation,
    "CWE-79",
    {"id": "CWE-79", "name": "XSS", "description": "Reflected XSS"}
)

# Batch
cwe_dict = {
    "CWE-79": {"id": "CWE-79", "name": "XSS"},
    "CWE-89": {"id": "CWE-89", "name": "SQL Injection"},
}
validation = batch_validate_cwes(validation, cwe_dict)

print(validation.validated_count)
print(validation.get_passed_cwes())
print(validation.get_failed_cwes())

summary = get_cwe_validation_summary(validation)
print(summary["success_rate_percent"])
```

### Analyze CWE relationships

```python
from ci.transparency.cwe.types.cwe.results import (
    CweRelationshipResult, analyze_relationships, get_relationship_summary
)

rels = CweRelationshipResult()

cwe_dict = {
    "CWE-79": {"id": "CWE-79", "relationships": [{"cwe_id": "CWE-80", "type": "child"}]},
    "CWE-80": {"id": "CWE-80", "relationships": [{"cwe_id": "CWE-79", "type": "parent"}]},
}

rels = analyze_relationships(rels, cwe_dict)

print(rels.references.total_references_count)   # total relationships
print(rels.circular_dependency_count)           # cycles detected
print(rels.references.orphaned_item_count)      # CWEs with no edges

summary = get_relationship_summary(rels)
print(summary["relationship_types"])
```

---

## Standards Domain

### Load standards

```python
from ci.transparency.cwe.types.standards.results import (
    StandardsLoadingResult, add_standard, get_standards_loading_summary
)

standards = StandardsLoadingResult()

nist = {
    "id": "NIST-SP-800-53",
    "name": "Security Controls",
    "framework": "NIST",
    "version": "Rev 5",
    "controls": [],
}
standards = add_standard(standards, "NIST-SP-800-53", nist)

print(standards.standards_count)
print(standards.frameworks.framework_count)

summary = get_standards_loading_summary(standards)
print(summary["frameworks"])
```

### Analyze standards mappings

```python
from ci.transparency.cwe.types.standards.results import (
    StandardsMappingResult, analyze_mappings, get_mapping_summary
)

mappings = StandardsMappingResult()

standards_dict = {
    "NIST-SP-800-53": {
        "id": "NIST-SP-800-53",
        "controls": [
            {"id": "AC-1", "mappings": [{"target_id": "CWE-79", "mapping_type": "cwe"}]},
        ],
    }
}

mappings = analyze_mappings(mappings, standards_dict)
print(mappings.total_mappings_count)
print(mappings.references.invalid_reference_count)

summary = get_mapping_summary(mappings)
print(summary["mapping_types"])
```

---

## CWE Schema (Domain-specific schema results)

### Load schemas & set metadata

```python
from pathlib import Path
from ci.transparency.cwe.types.cwe.schema.results import (
    CweSchemaLoadingResult,
    add_cwe_schema,
    set_schema_metadata,
    get_cwe_schema_loading_summary,
)

schemas = CweSchemaLoadingResult()
schemas = set_schema_metadata(schemas, schema_name="cwe", schema_version="1.0")

schema_item = {
    "schema_name": "cwe",
    "schema_version": "1.0",
    "schema_content": {"type": "object", "properties": {"id": {"type": "string"}}},
    "source_path": "cwe.schema.json",
}
schemas = add_cwe_schema(schemas, "cwe-1.0", schema_item, file_path=Path("cwe.schema.json"))

summary = get_cwe_schema_loading_summary(schemas)
print(summary["schema_name"], summary["file_types"])
```

### Build validation results

```python
from ci.transparency.cwe.types.cwe.schema.results import (
    create_successful_validation,
    create_failed_validation,
    add_validation_error,
    get_cwe_schema_validation_summary,
)

ok = create_successful_validation(
    schema_name="cwe",
    schema_version="1.0",
    cwe_id="CWE-79",
    field_path="id",
    info_message="ID matches pattern",
)

bad = create_failed_validation(
    schema_name="cwe",
    schema_version="1.0",
    cwe_id="CWE-79",
    field_path="id",
    error_messages=["Missing required: id"],
)

bad = add_validation_error(bad, "Unexpected field: foo")

print(ok.is_successful)   # True
print(bad.is_successful)  # False

print(get_cwe_schema_validation_summary(bad)["errors"])
```

---

## Tips

- Import from leaf modules:
  - `ci.transparency.cwe.types.cwe.results`
  - `ci.transparency.cwe.types.standards.results`
  - `ci.transparency.cwe.types.cwe.schema.results`
  - `ci.transparency.cwe.types.base.messages` / `base.counts` / `base.collections`
- All result types are **frozen dataclasses**; update via helper functions (which use `dataclasses.replace`).
- Summaries (`get_*_summary`) provide ready-to-serialize dictionaries for reporting/logging.

See the **API Reference** for module-by-module documentation.
