from pathlib import Path

from ci.transparency.cwe.types.schema.results import (
    SchemaLoadingResult,
    SchemaValidationResult,
    SchemaDocumentDict,
    add_schema,
    track_invalid_schema_file,
    track_skipped_schema_file,
    validate_schema_document,
    record_schema_validation,
    get_schema_loading_summary,
    get_schema_validation_summary,
)


def make_doc(schema_id: str = "core", name: str = "Core", version: str = "1.0") -> SchemaDocumentDict:
    return {
        "id": schema_id,
        "name": name,
        "version": version,
        "content": {"$schema": "https://json-schema.org/draft/2020-12/schema"},
        "source_path": f"{schema_id}.json",
    }


def test_add_schema_success():
    res = SchemaLoadingResult()
    doc = make_doc("s1", "Schema One")
    res2 = add_schema(res, "s1", doc)

    assert res.schema_count == 0  # original unchanged (immutability)
    assert res2.schema_count == 1
    assert "s1" in res2.schemas
    assert res2.loading.loaded_count == 1
    assert res2.loading.failed_count == 0
    # info message recorded
    assert any("Loaded schema s1" in m for m in res2.messages.infos)


def test_add_schema_duplicate_records_warning_and_failed():
    res = SchemaLoadingResult()
    doc = make_doc("s1", "Schema One")
    res = add_schema(res, "s1", doc)

    # Duplicate with file path should increment failed + track duplicate
    dup_path = Path("dup.json")
    res2 = add_schema(res, "s1", doc, file_path=dup_path)

    assert res2.loading.loaded_count == 1
    assert res2.loading.failed_count == 1
    assert "s1" in res2.duplicates.duplicate_ids
    assert dup_path in res2.duplicates.duplicate_ids["s1"]
    assert any("Duplicate schema ID" in w for w in res2.messages.warnings)


def test_track_invalid_and_skipped_files():
    res = SchemaLoadingResult()
    res = track_invalid_schema_file(res, Path("bad.json"), "parse error")
    res = track_skipped_schema_file(res, Path("skip.json"), "filtered")

    assert res.files.failed_file_count == 1
    assert res.files.skipped_file_count == 1
    assert res.loading.failed_count == 1
    assert any("Invalid schema file" in e for e in res.messages.errors)
    assert any("Skipped schema file" in i for i in res.messages.infos)


def test_record_schema_validation_adapter_messages_and_counts():
    vres = SchemaValidationResult()

    vres = record_schema_validation(
        vres,
        "ext1",
        ok=False,
        errors=["E1", "E2"],
        warnings=["W1"],
        infos=["I1"],
    )

    assert vres.validation_results["ext1"] is False
    assert vres.validation.failed_count == 1
    assert any(": E1" in e for e in vres.messages.errors)
    assert any(": W1" in w for w in vres.messages.warnings)
    assert any(": I1" in i for i in vres.messages.infos)
    # details captured
    assert "ext1" in vres.validation_details
    assert set(vres.validation_details["ext1"]) >= {"E1", "E2"}


def test_loading_and_validation_summaries_shape_and_values():
    lres = SchemaLoadingResult()
    lres = add_schema(lres, "s1", make_doc("s1"))
    lres = track_skipped_schema_file(lres, Path("a.json"), "skip")
    lsum = get_schema_loading_summary(lres)

    assert lsum["schemas_loaded"] == 1
    assert lsum["successful_loads"] == 1
    assert lsum["skipped_files"] == 1
    assert "loaded_schema_ids" in lsum

    vres = SchemaValidationResult()
    vres = validate_schema_document(vres, "ok", make_doc("ok"))
    vsum = get_schema_validation_summary(vres)

    assert vsum["schemas_validated"] == 1
    assert vsum["validation_passed"] == 1
    assert vsum["validation_failed"] == 0
