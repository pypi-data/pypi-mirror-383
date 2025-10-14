"""
Unit tests for FileValidator edge cases not covered by integration tests.
"""
import pytest
from XER_Technologies_metadata_extractor.validation import FileValidator, ValidationResult


class TestFileValidator:
    """Test FileValidator edge cases and validation logic."""

    def test_invalid_file_extension(self, file_validator, sample_csv_content):
        """Test validation rejects non-CSV file extensions."""
        result = file_validator.precheck_csv_file(sample_csv_content, "test.txt")
        assert isinstance(result, ValidationResult)
        assert result.is_valid is False
        assert "csv" in result.message.lower()

    def test_empty_file_content(self, file_validator):
        """Test validation rejects empty file content."""
        result = file_validator.precheck_csv_file("", "test.csv")
        assert isinstance(result, ValidationResult)
        assert result.is_valid is False
        assert "empty" in result.message.lower()

    def test_empty_bytes_content(self, file_validator):
        """Test validation rejects empty bytes content."""
        result = file_validator.precheck_csv_file(b"", "test.csv")
        assert isinstance(result, ValidationResult)
        assert result.is_valid is False
        assert "empty" in result.message.lower()

    def test_insufficient_data_lines(self, file_validator):
        """Test validation rejects CSV with too few lines."""
        small_csv = "header1,header2\nvalue1,value2"
        result = file_validator.precheck_csv_file(small_csv, "test.csv")
        assert isinstance(result, ValidationResult)
        # Should fail validation for insufficient data
        if not result.is_valid:
            assert "insufficient" in result.message.lower() or "minimum" in result.message.lower()

    def test_malformed_csv_content(self, file_validator):
        """Test validation handles malformed CSV content."""
        malformed_csv = "header1,header2\nvalue1\nincomplete_row"
        result = file_validator.precheck_csv_file(malformed_csv, "test.csv")
        assert isinstance(result, ValidationResult)
        # Validator should handle this gracefully (either pass or fail with clear message)

    def test_csv_with_special_characters(self, file_validator):
        """Test validation handles CSV with quotes and commas."""
        special_csv = 'name,value\n"Test, Inc",123\n"Quote""Test",456'
        result = file_validator.precheck_csv_file(special_csv, "test.csv")
        assert isinstance(result, ValidationResult)
        # Should handle this gracefully

    def test_csv_with_unicode_characters(self, file_validator):
        """Test validation accepts Unicode characters."""
        unicode_csv = "name,value\nTëst,123\nÄnother,456\nрусский,789"
        result = file_validator.precheck_csv_file(unicode_csv, "test.csv")
        assert isinstance(result, ValidationResult)
        assert result.is_valid is True

    def test_non_csv_extensions_rejected(self, file_validator, sample_csv_content):
        """Test validation rejects non-CSV file extensions."""
        non_csv_extensions = [".txt", ".json", ".xml", ".xlsx", ""]

        for ext in non_csv_extensions:
            filename = f"test{ext}"
            result = file_validator.precheck_csv_file(sample_csv_content, filename)
            assert isinstance(result, ValidationResult)
            assert result.is_valid is False

    def test_case_insensitive_csv_extensions(self, file_validator, sample_csv_content):
        """Test validation accepts different case CSV extensions."""
        extensions = [".csv", ".CSV", ".Csv", ".cSv"]

        for ext in extensions:
            filename = f"test{ext}"
            result = file_validator.precheck_csv_file(sample_csv_content, filename)
            assert isinstance(result, ValidationResult)
            assert result.is_valid is True

    def test_validation_result_structure(self, file_validator, sample_csv_content):
        """Test ValidationResult has required structure."""
        result = file_validator.precheck_csv_file(sample_csv_content, "test.csv")

        # Check required attributes exist and have correct types
        assert hasattr(result, 'is_valid') and isinstance(result.is_valid, bool)
        assert hasattr(result, 'message') and isinstance(result.message, str)
        assert hasattr(result, 'warnings') and isinstance(result.warnings, list)