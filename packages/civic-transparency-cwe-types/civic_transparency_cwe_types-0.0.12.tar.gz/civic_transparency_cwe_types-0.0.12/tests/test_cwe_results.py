# tests/test_cwe_results.py
# pyright: strict

"""Comprehensive tests for CWE result types and operations."""

from pathlib import Path


from ci.transparency.cwe.types.cwe.results import (
    CweDataDict,
    CweItemDict,
    CweLoadingResult,
    CweRelationshipResult,
    CweValidationResult,
    analyze_relationships,
    add_cwe,
    batch_validate_cwes,
    get_cwe_loading_summary,
    get_cwe_validation_summary,
    get_relationship_summary,
    track_invalid_file,
    track_skipped_cwe_file,
    validate_cwe,
    validate_cwe_field,
)


# ============================================================================
# CweLoadingResult Tests
# ============================================================================


class TestCweLoadingResult:
    """Test CweLoadingResult dataclass and operations."""

    def test_default_initialization(self) -> None:
        """Test result initializes with correct defaults."""
        result = CweLoadingResult()

        assert result.cwe_count == 0
        assert result.is_successful
        assert result.loaded_cwe_ids == []
        assert not result.messages.has_errors
        assert result.loading.loaded_count == 0

    def test_add_cwe_success(self) -> None:
        """Test successfully adding a CWE."""
        result = CweLoadingResult()
        cwe_data: CweItemDict = {
            "id": "CWE-79",
            "name": "Cross-site Scripting",
            "description": "XSS vulnerability",
            "category": "injection",
        }

        new_result = add_cwe(result, "CWE-79", cwe_data, file_path=Path("test.yaml"))

        # Verify immutability
        assert result.cwe_count == 0
        assert new_result.cwe_count == 1

        # Verify data
        assert "CWE-79" in new_result.cwes
        assert new_result.loading.loaded_count == 1
        assert new_result.files.processed_file_count == 1
        assert new_result.categories.category_stats["injection"] == 1
        assert new_result.messages.info_count == 1

    def test_add_cwe_duplicate_handling(self) -> None:
        """Test duplicate CWE handling."""
        result = CweLoadingResult()
        cwe_data: CweItemDict = {"id": "CWE-79", "name": "XSS", "category": "injection"}

        # Add first time
        result = add_cwe(result, "CWE-79", cwe_data)
        # Add duplicate
        result = add_cwe(result, "CWE-79", cwe_data, file_path=Path("dup.yaml"))

        assert result.cwe_count == 1  # Still only one
        assert result.duplicates.duplicate_count == 1
        assert result.messages.warning_count == 1
        assert result.loading.failed_count == 1

    def test_get_cwe(self) -> None:
        """Test getting CWE by ID."""
        result = CweLoadingResult()
        cwe_data: CweItemDict = {"id": "CWE-79", "name": "XSS"}
        result = add_cwe(result, "CWE-79", cwe_data)

        found = result.get_cwe("CWE-79")
        assert found is not None
        assert found.get("name") == "XSS"

        not_found = result.get_cwe("CWE-999")
        assert not_found is None

    def test_has_cwe(self) -> None:
        """Test checking if CWE exists."""
        result = CweLoadingResult()
        cwe_data: CweItemDict = {"id": "CWE-79", "name": "XSS"}
        result = add_cwe(result, "CWE-79", cwe_data)

        assert result.has_cwe("CWE-79")
        assert not result.has_cwe("CWE-999")

    def test_get_cwes_by_category(self) -> None:
        """Test filtering CWEs by category."""
        result = CweLoadingResult()
        result = add_cwe(result, "CWE-79", {"id": "CWE-79", "name": "XSS", "category": "injection"})
        result = add_cwe(
            result, "CWE-287", {"id": "CWE-287", "name": "Auth", "category": "authentication"}
        )

        injection_cwes = result.get_cwes_by_category("injection")
        assert len(injection_cwes) == 1
        assert "CWE-79" in injection_cwes

    def test_search_cwes(self) -> None:
        """Test searching CWEs by name or description."""
        result = CweLoadingResult()
        result = add_cwe(
            result,
            "CWE-79",
            {"id": "CWE-79", "name": "Cross-site Scripting", "description": "XSS vulnerability"},
        )
        result = add_cwe(
            result, "CWE-89", {"id": "CWE-89", "name": "SQL Injection", "description": "SQLi"}
        )

        # Search by name
        xss_results = result.search_cwes("scripting")
        assert len(xss_results) == 1
        assert "CWE-79" in xss_results

        # Search by description
        sql_results = result.search_cwes("sqli")
        assert len(sql_results) == 1
        assert "CWE-89" in sql_results

        # No results
        no_results = result.search_cwes("nonexistent")
        assert len(no_results) == 0

    def test_track_invalid_file(self) -> None:
        """Test tracking invalid files."""
        result = CweLoadingResult()

        new_result = track_invalid_file(result, Path("bad.yaml"), "malformed YAML")

        assert new_result.files.failed_file_count == 1
        assert new_result.loading.failed_count == 1
        assert new_result.messages.error_count == 1
        assert not new_result.is_successful

    def test_track_skipped_file(self) -> None:
        """Test tracking skipped files."""
        result = CweLoadingResult()

        new_result = track_skipped_cwe_file(result, Path("skip.yaml"), "already processed")

        assert new_result.files.skipped_file_count == 1
        assert new_result.messages.info_count == 1

    def test_loading_summary(self) -> None:
        """Test loading summary generation."""
        result = CweLoadingResult()
        result = add_cwe(result, "CWE-79", {"id": "CWE-79", "name": "XSS", "category": "injection"})
        result = track_invalid_file(result, Path("bad.yaml"), "error")

        summary = get_cwe_loading_summary(result)

        assert summary["cwes_loaded"] == 1
        assert summary["successful_loads"] == 1
        assert summary["failed_loads"] == 1
        assert "CWE-79" in summary["loaded_cwe_ids"]
        assert "injection" in summary["categories"]
        assert summary["most_common_category"] == "injection"


# ============================================================================
# CweValidationResult Tests
# ============================================================================


class TestCweValidationResult:
    """Test CweValidationResult dataclass and operations."""

    def test_default_initialization(self) -> None:
        """Test result initializes with correct defaults."""
        result = CweValidationResult()

        assert result.validated_count == 0
        assert result.is_successful
        assert result.validation_rate == 1.0
        assert result.field_error_count == 0
        assert not result.has_field_errors

    def test_validate_cwe_success(self) -> None:
        """Test successful CWE validation."""
        result = CweValidationResult()
        cwe_data: CweItemDict = {
            "id": "CWE-79",
            "name": "Cross-site Scripting",
            "description": "XSS vulnerability description that is long enough",
            "category": "injection",
        }

        new_result = validate_cwe(result, "CWE-79", cwe_data)

        assert new_result.validated_count == 1
        assert new_result.validation.passed_count == 1
        assert "CWE-79" in new_result.get_passed_cwes()
        assert "CWE-79" not in new_result.get_failed_cwes()

    def test_validate_cwe_missing_required_fields(self) -> None:
        """Test validation fails for missing required fields."""
        result = CweValidationResult()
        cwe_data: CweItemDict = {"id": "CWE-79"}  # Missing name, description

        new_result = validate_cwe(result, "CWE-79", cwe_data)

        assert new_result.validation.failed_count == 1
        assert "CWE-79" in new_result.get_failed_cwes()
        errors = new_result.get_validation_errors("CWE-79")
        assert len(errors) > 0

    def test_validate_cwe_invalid_id_format(self) -> None:
        """Test validation fails for invalid CWE ID format."""
        result = CweValidationResult()
        cwe_data: CweItemDict = {
            "id": "INVALID-79",
            "name": "Test",
            "description": "Test description",
        }

        new_result = validate_cwe(result, "INVALID-79", cwe_data)

        assert new_result.validation.failed_count == 1
        errors = new_result.get_validation_errors("INVALID-79")
        assert any("Invalid CWE ID format" in err for err in errors)

    def test_validate_cwe_short_name(self) -> None:
        """Test validation warns about short names."""
        result = CweValidationResult()
        cwe_data: CweItemDict = {"id": "CWE-79", "name": "XS", "description": "Short name test"}

        new_result = validate_cwe(result, "CWE-79", cwe_data)

        errors = new_result.get_validation_errors("CWE-79")
        assert any("name too short" in err.lower() for err in errors)

    def test_validate_cwe_invalid_category(self) -> None:
        """Test validation warns about invalid categories."""
        result = CweValidationResult()
        cwe_data: CweItemDict = {
            "id": "CWE-79",
            "name": "Test CWE",
            "description": "Test description",
            "category": "invalid_category_xyz",
        }

        new_result = validate_cwe(result, "CWE-79", cwe_data)

        errors = new_result.get_validation_errors("CWE-79")
        assert any("Invalid category" in err for err in errors)

    def test_validate_cwe_invalid_relationships(self) -> None:
        """Test validation of relationships."""
        result = CweValidationResult()
        cwe_data: CweItemDict = {
            "id": "CWE-79",
            "name": "Test",
            "description": "Test description",
            "relationships": [
                {"cwe_id": "INVALID-ID", "type": "parent"},  # Invalid ID format
                {"type": "child"},  # Missing cwe_id
            ],
        }

        new_result = validate_cwe(result, "CWE-79", cwe_data)

        errors = new_result.get_validation_errors("CWE-79")
        assert len(errors) >= 2  # At least 2 relationship errors

    def test_validate_cwe_field(self) -> None:
        """Test field-level validation."""
        result = CweValidationResult()

        # Valid field
        result = validate_cwe_field(result, "CWE-79", "name", "Valid Name", "required")
        assert result.validation.passed_count == 1

        # Invalid field - None value
        result = validate_cwe_field(result, "CWE-79", "description", None, "required")
        assert result.field_error_count == 1

        # Invalid field - empty string
        result = validate_cwe_field(result, "CWE-79", "category", "   ", "required")
        assert result.field_error_count == 2

        # Invalid CWE ID format
        result = validate_cwe_field(result, "CWE-79", "id", "INVALID", "format")
        assert result.field_error_count == 3

    def test_batch_validate_cwes(self) -> None:
        """Test batch validation."""
        result = CweValidationResult()
        cwe_dict: CweDataDict = {
            "CWE-79": {
                "id": "CWE-79",
                "name": "XSS",
                "description": "Cross-site scripting vulnerability",
            },
            "CWE-89": {
                "id": "CWE-89",
                "name": "SQL Injection",
                "description": "SQL injection vulnerability",
            },
        }

        new_result = batch_validate_cwes(result, cwe_dict)

        assert new_result.validated_count == 2
        assert new_result.messages.info_count >= 1  # Batch message

    def test_get_most_common_errors(self) -> None:
        """Test getting most common validation errors."""
        result = CweValidationResult()

        # Create multiple CWEs with same error
        for i in range(3):
            cwe_data: CweItemDict = {"id": f"CWE-{i}", "name": ""}  # Missing name
            result = validate_cwe(result, f"CWE-{i}", cwe_data)

        common_errors = result.get_most_common_errors(limit=3)
        assert len(common_errors) > 0
        # Most common error should appear multiple times
        assert common_errors[0][1] >= 3

    def test_get_error_summary(self) -> None:
        """Test comprehensive error summary."""
        result = CweValidationResult()
        cwe_data: CweItemDict = {"id": "INVALID", "name": ""}

        result = validate_cwe(result, "INVALID", cwe_data)

        summary = result.get_error_summary()
        assert summary["total_errors"] > 0
        assert summary["cwes_with_errors"] == 1
        assert "most_common_errors" in summary
        assert "severity_distribution" in summary

    def test_validation_rate(self) -> None:
        """Test validation rate calculation."""
        result = CweValidationResult()

        # Add 2 passing, 1 failing
        result = validate_cwe(
            result, "CWE-79", {"id": "CWE-79", "name": "XSS", "description": "XSS description"}
        )
        result = validate_cwe(
            result, "CWE-89", {"id": "CWE-89", "name": "SQLi", "description": "SQLi description"}
        )
        result = validate_cwe(result, "CWE-999", {"id": "INVALID", "name": ""})

        # 2/3 = 66.67%
        assert 0.6 < result.validation_rate < 0.7

    def test_validation_summary(self) -> None:
        """Test validation summary generation."""
        result = CweValidationResult()
        result = validate_cwe(
            result,
            "CWE-79",
            {"id": "CWE-79", "name": "XSS", "description": "Cross-site scripting vulnerability"},
        )

        summary = get_cwe_validation_summary(result)

        assert summary["cwes_validated"] == 1
        assert summary["validation_passed"] == 1
        assert "success_rate_percent" in summary
        assert "error_summary" in summary


# ============================================================================
# CweRelationshipResult Tests
# ============================================================================


class TestCweRelationshipResult:
    """Test CweRelationshipResult dataclass and operations."""

    def test_default_initialization(self) -> None:
        """Test result initializes with correct defaults."""
        result = CweRelationshipResult()

        assert result.circular_dependency_count == 0
        assert result.max_relationship_depth == 0
        assert result.is_successful
        assert not result.has_circular_dependencies

    def test_analyze_relationships_simple(self) -> None:
        """Test simple relationship analysis."""
        result = CweRelationshipResult()
        cwe_dict: CweDataDict = {
            "CWE-79": {
                "id": "CWE-79",
                "relationships": [{"cwe_id": "CWE-80", "type": "child"}],
            },
            "CWE-80": {"id": "CWE-80", "relationships": []},
        }

        new_result = analyze_relationships(result, cwe_dict)

        assert new_result.references.total_references_count == 1
        assert len(new_result.relationship_types) > 0
        assert new_result.relationship_types.get("child") == 1

    def test_analyze_relationships_circular(self) -> None:
        """Test circular dependency detection."""
        result = CweRelationshipResult()
        cwe_dict: CweDataDict = {
            "CWE-79": {"id": "CWE-79", "relationships": ["CWE-80"]},
            "CWE-80": {"id": "CWE-80", "relationships": ["CWE-79"]},  # Circular
        }

        new_result = analyze_relationships(result, cwe_dict)

        assert new_result.has_circular_dependencies
        assert new_result.circular_dependency_count >= 2
        assert new_result.messages.warning_count > 0

    def test_analyze_relationships_invalid_references(self) -> None:
        """Test detection of invalid references."""
        result = CweRelationshipResult()
        cwe_dict: CweDataDict = {
            "CWE-79": {
                "id": "CWE-79",
                "relationships": ["CWE-999"],  # Non-existent
            },
        }

        new_result = analyze_relationships(result, cwe_dict)

        assert new_result.references.invalid_reference_count > 0
        assert new_result.messages.error_count > 0

    def test_get_relationships(self) -> None:
        """Test getting relationships for a CWE."""
        result = CweRelationshipResult()
        cwe_dict: CweDataDict = {
            "CWE-79": {"id": "CWE-79", "relationships": ["CWE-80", "CWE-81"]},
            "CWE-80": {"id": "CWE-80"},
            "CWE-81": {"id": "CWE-81"},
        }

        result = analyze_relationships(result, cwe_dict)

        relationships = result.get_relationships("CWE-79")
        assert len(relationships) == 2
        assert "CWE-80" in relationships

    def test_get_relationship_depth(self) -> None:
        """Test getting relationship depth."""
        result = CweRelationshipResult()
        cwe_dict: CweDataDict = {
            "CWE-79": {"id": "CWE-79", "relationships": ["CWE-80"]},
            "CWE-80": {"id": "CWE-80", "relationships": ["CWE-81"]},
            "CWE-81": {"id": "CWE-81", "relationships": []},
        }

        result = analyze_relationships(result, cwe_dict)

        depth_79 = result.get_relationship_depth("CWE-79")
        assert depth_79 > 0

    def test_get_related_cwes(self) -> None:
        """Test getting related CWEs up to max depth."""
        result = CweRelationshipResult()
        cwe_dict: CweDataDict = {
            "CWE-79": {"id": "CWE-79", "relationships": ["CWE-80"]},
            "CWE-80": {"id": "CWE-80", "relationships": ["CWE-81"]},
            "CWE-81": {"id": "CWE-81", "relationships": []},
        }

        result = analyze_relationships(result, cwe_dict)

        # Depth 1: just direct children
        related_1 = result.get_related_cwes("CWE-79", max_depth=1)
        assert "CWE-80" in related_1

        # Depth 2: children and grandchildren
        related_2 = result.get_related_cwes("CWE-79", max_depth=2)
        assert "CWE-80" in related_2
        assert "CWE-81" in related_2

    def test_find_relationship_path(self) -> None:
        """Test finding shortest path between CWEs."""
        result = CweRelationshipResult()
        cwe_dict: CweDataDict = {
            "CWE-79": {"id": "CWE-79", "relationships": ["CWE-80"]},
            "CWE-80": {"id": "CWE-80", "relationships": ["CWE-81"]},
            "CWE-81": {"id": "CWE-81", "relationships": []},
        }

        result = analyze_relationships(result, cwe_dict)

        # Path exists
        path = result.find_relationship_path("CWE-79", "CWE-81")
        assert path is not None
        assert path[0] == "CWE-79"
        assert path[-1] == "CWE-81"

        # No path
        no_path = result.find_relationship_path("CWE-81", "CWE-79")
        assert no_path is None

        # Same node
        same = result.find_relationship_path("CWE-79", "CWE-79")
        assert same == ["CWE-79"]

    def test_get_relationship_statistics(self) -> None:
        """Test comprehensive relationship statistics."""
        result = CweRelationshipResult()
        cwe_dict: CweDataDict = {
            "CWE-79": {"id": "CWE-79", "relationships": ["CWE-80"]},
            "CWE-80": {"id": "CWE-80", "relationships": []},
            "CWE-81": {"id": "CWE-81", "relationships": []},  # Orphaned
        }

        result = analyze_relationships(result, cwe_dict)

        stats = result.get_relationship_statistics()

        assert stats["total_relationships"] == 1
        assert stats["connected_cwes"] == 1
        assert stats["orphaned_cwes"] >= 1
        assert "max_depth" in stats
        assert "avg_relationships_per_cwe" in stats

    def test_relationship_summary(self) -> None:
        """Test relationship summary generation."""
        result = CweRelationshipResult()
        cwe_dict: CweDataDict = {
            "CWE-79": {"id": "CWE-79", "relationships": ["CWE-80"]},
            "CWE-80": {"id": "CWE-80", "relationships": []},
        }

        result = analyze_relationships(result, cwe_dict)

        summary = get_relationship_summary(result)

        assert summary["total_relationships"] == 1
        assert "relationship_types" in summary
        assert "has_circular_dependencies" in summary
        assert "relationship_statistics" in summary


# ============================================================================
# Integration Tests
# ============================================================================


class TestIntegration:
    """Test integration between different result types."""

    def test_full_workflow(self) -> None:
        """Test complete workflow: load, validate, analyze."""
        # Load
        loading_result = CweLoadingResult()
        loading_result = add_cwe(
            loading_result,
            "CWE-79",
            {
                "id": "CWE-79",
                "name": "Cross-site Scripting",
                "description": "XSS vulnerability",
                "category": "injection",
                "relationships": ["CWE-80"],
            },
        )
        loading_result = add_cwe(
            loading_result,
            "CWE-80",
            {
                "id": "CWE-80",
                "name": "Basic XSS",
                "description": "Basic XSS",
                "category": "injection",
            },
        )

        assert loading_result.cwe_count == 2

        # Validate
        validation_result = CweValidationResult()
        validation_result = batch_validate_cwes(validation_result, loading_result.cwes)

        assert validation_result.validated_count == 2

        # Analyze relationships
        relationship_result = CweRelationshipResult()
        relationship_result = analyze_relationships(relationship_result, loading_result.cwes)

        assert relationship_result.references.total_references_count == 1

    def test_immutability_throughout_workflow(self) -> None:
        """Test that all operations maintain immutability."""
        original = CweLoadingResult()
        cwe_data: CweItemDict = {"id": "CWE-79", "name": "XSS"}

        modified = add_cwe(original, "CWE-79", cwe_data)

        # Original unchanged
        assert original.cwe_count == 0
        assert original.loading.loaded_count == 0

        # Modified has changes
        assert modified.cwe_count == 1
        assert modified.loading.loaded_count == 1
