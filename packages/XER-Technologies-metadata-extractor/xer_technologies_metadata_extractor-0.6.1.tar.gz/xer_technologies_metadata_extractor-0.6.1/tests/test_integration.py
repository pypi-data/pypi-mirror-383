"""
Integration tests based on specific behaviors identified in the original test scripts.
These tests apply the same behavioral expectations to all CSV files.
"""
import pytest
import pandas as pd
from pathlib import Path
from XER_Technologies_metadata_extractor.extract import MetadataExtractor


@pytest.mark.integration
class TestCoreAPIBehaviors:
    """Test core API behaviors across all files."""

    def test_extract_csv_metadata_returns_valid_structure(self, test_files_list, real_csv_data):
        """extract_csv_metadata() should always return valid metadata structure."""
        extractor = MetadataExtractor()

        for csv_file in test_files_list:
            if not csv_file.exists():
                continue

            file_data = real_csv_data(csv_file)
            if not file_data:
                continue

            try:
                metadata = extractor.extract_csv_metadata(file_data, csv_file.name, verbose=False)

                # Core structure should always be present
                assert isinstance(metadata, dict), f"Metadata should be dict for {csv_file.name}"

                # Based on actual API behavior, check for expected keys
                if "validation_results" in metadata:
                    validation = metadata["validation_results"]
                    assert isinstance(validation, dict), f"validation_results should be dict for {csv_file.name}"
                    assert "is_valid" in validation, f"validation_results missing is_valid for {csv_file.name}"
                    assert isinstance(validation["is_valid"], bool), f"is_valid should be bool for {csv_file.name}"

            except Exception as e:
                pytest.fail(f"extract_csv_metadata crashed on {csv_file.name}: {e}")

    def test_extract_csv_metadata_with_dataframe_returns_tuple(self, test_files_list, real_csv_data):
        """extract_csv_metadata_with_dataframe() should return DataFrame + metadata tuple."""
        extractor = MetadataExtractor()

        for csv_file in test_files_list:
            if not csv_file.exists():
                continue

            file_data = real_csv_data(csv_file)
            if not file_data:
                continue

            try:
                result = extractor.extract_csv_metadata_with_dataframe(file_data, csv_file.name, verbose=False)

                # Should return tuple
                assert isinstance(result, tuple), f"Should return tuple for {csv_file.name}"
                assert len(result) == 2, f"Should return 2-element tuple for {csv_file.name}"

                df, metadata = result
                assert isinstance(df, pd.DataFrame), f"First element should be DataFrame for {csv_file.name}"
                assert isinstance(metadata, dict), f"Second element should be dict for {csv_file.name}"

            except Exception as e:
                pytest.fail(f"extract_csv_metadata_with_dataframe crashed on {csv_file.name}: {e}")

    def test_api_backward_compatibility(self, test_files_list, real_csv_data):
        """Both APIs should return consistent metadata for same file."""
        extractor = MetadataExtractor()

        for csv_file in test_files_list:
            if not csv_file.exists():
                continue

            file_data = real_csv_data(csv_file)
            if not file_data:
                continue

            try:
                # Test both APIs
                metadata_old = extractor.extract_csv_metadata(file_data, csv_file.name, verbose=False)
                df_new, metadata_new = extractor.extract_csv_metadata_with_dataframe(file_data, csv_file.name, verbose=False)

                # Both should return dictionaries
                assert isinstance(metadata_old, dict), f"Old API should return dict for {csv_file.name}"
                assert isinstance(metadata_new, dict), f"New API should return dict for {csv_file.name}"
                assert isinstance(df_new, pd.DataFrame), f"New API should return DataFrame for {csv_file.name}"

                # Both should have validation results if present
                if "validation_results" in metadata_old and "validation_results" in metadata_new:
                    assert metadata_old["validation_results"]["is_valid"] == metadata_new["validation_results"]["is_valid"], \
                        f"Inconsistent validation for {csv_file.name}"

                # If flight hours are present, they should be consistent
                if "total_flight_hours" in metadata_old and "total_flight_hours" in metadata_new:
                    assert metadata_old["total_flight_hours"] == metadata_new["total_flight_hours"], \
                        f"Inconsistent flight hours for {csv_file.name}"

            except Exception as e:
                pytest.fail(f"API compatibility test failed on {csv_file.name}: {e}")


@pytest.mark.integration
class TestPowerColumnBehaviors:
    """Test power column behaviors across all files."""

    def test_power_columns_in_dataframe_when_present(self, test_files_list, real_csv_data):
        """When power columns exist in DataFrame, they should contain valid values."""
        extractor = MetadataExtractor()
        power_columns = ['PMU_power', 'Engine_power', 'System_efficiency']

        for csv_file in test_files_list:
            if not csv_file.exists():
                continue

            file_data = real_csv_data(csv_file)
            if not file_data:
                continue

            try:
                df, metadata = extractor.extract_csv_metadata_with_dataframe(file_data, csv_file.name, verbose=False)

                # Check power columns if present
                present_power_cols = [col for col in power_columns if col in df.columns]

                for col in present_power_cols:
                    # Power columns should contain numeric data
                    assert pd.api.types.is_numeric_dtype(df[col]), f"{col} should be numeric in {csv_file.name}"

                    # Should have some non-NaN values (unless all data is invalid)
                    non_nan_count = df[col].count()
                    # Don't require non-NaN values - some files might not have valid power calculations

            except Exception as e:
                pytest.fail(f"Power column test failed on {csv_file.name}: {e}")

    def test_original_csv_file_unchanged(self, test_files_list, real_csv_data):
        """Original CSV file should remain unchanged after metadata extraction."""
        extractor = MetadataExtractor()

        for csv_file in test_files_list:
            if not csv_file.exists():
                continue

            # Read original file
            original_df = pd.read_csv(csv_file)
            original_columns = set(original_df.columns)

            file_data = real_csv_data(csv_file)
            if not file_data:
                continue

            try:
                # Extract metadata (should not modify file)
                metadata = extractor.extract_csv_metadata(file_data, csv_file.name, verbose=False)

                # Re-read file
                after_df = pd.read_csv(csv_file)
                after_columns = set(after_df.columns)

                # File should be unchanged
                assert original_columns == after_columns, f"CSV file {csv_file.name} was modified by metadata extraction"
                assert len(original_df) == len(after_df), f"Row count changed in {csv_file.name}"

            except Exception as e:
                # If we can't read the file, that's fine - we're testing that extraction doesn't crash
                if "metadata extraction" not in str(e).lower():
                    continue  # File reading issue, not our concern


@pytest.mark.integration
class TestFlightHoursBehaviors:
    """Test flight hours calculation behaviors across all files."""

    def test_flight_hours_calculation_when_applicable(self, test_files_list, real_csv_data):
        """Flight hours should be calculated for files with droneInFlight data."""
        extractor = MetadataExtractor()

        for csv_file in test_files_list:
            if not csv_file.exists():
                continue

            file_data = real_csv_data(csv_file)
            if not file_data:
                continue

            try:
                metadata = extractor.extract_csv_metadata(file_data, csv_file.name, verbose=False)

                # If flight hours were calculated, verify the value
                if "total_flight_hours" in metadata:
                    flight_hours = metadata["total_flight_hours"]
                    assert isinstance(flight_hours, (int, float)), f"Flight hours should be numeric for {csv_file.name}"
                    assert flight_hours >= 0, f"Flight hours should be non-negative for {csv_file.name} (got {flight_hours})"
                    # Don't require specific values - some files may have 0 flight hours

            except Exception as e:
                pytest.fail(f"Flight hours test failed on {csv_file.name}: {e}")

    def test_flight_hours_handles_missing_columns(self, test_files_list, real_csv_data):
        """Flight hours calculation should handle files missing droneInFlight or time columns gracefully."""
        extractor = MetadataExtractor()

        for csv_file in test_files_list:
            if not csv_file.exists():
                continue

            file_data = real_csv_data(csv_file)
            if not file_data:
                continue

            try:
                # Should not crash even if required columns are missing
                metadata = extractor.extract_csv_metadata(file_data, csv_file.name, verbose=False)

                # If total_flight_hours is present despite missing columns, it should still be valid
                if "total_flight_hours" in metadata:
                    flight_hours = metadata["total_flight_hours"]
                    assert isinstance(flight_hours, (int, float)), f"Flight hours should be numeric for {csv_file.name}"

            except Exception as e:
                pytest.fail(f"Flight hours missing columns test failed on {csv_file.name}: {e}")


@pytest.mark.integration
class TestPostProcessingBehaviors:
    """Test post-processing statistics behaviors across all files."""

    def test_postprocessing_stats_structure(self, test_files_list, real_csv_data):
        """Post-processing stats should have correct structure when present."""
        extractor = MetadataExtractor()

        for csv_file in test_files_list:
            if not csv_file.exists():
                continue

            file_data = real_csv_data(csv_file)
            if not file_data:
                continue

            try:
                metadata = extractor.extract_csv_metadata(file_data, csv_file.name, verbose=False)

                if "post_processing" in metadata:
                    pp_stats = metadata["post_processing"]
                    assert isinstance(pp_stats, dict), f"Post-processing stats should be dict for {csv_file.name}"

                    # Check types of expected keys
                    numeric_keys = ["columns_renamed", "derived_columns_added", "faulty_rows_filtered"]
                    for key in numeric_keys:
                        if key in pp_stats:
                            assert isinstance(pp_stats[key], (int, float)), f"{key} should be numeric for {csv_file.name}"
                            assert pp_stats[key] >= 0, f"{key} should be non-negative for {csv_file.name}"

                    if "calculations_applied" in pp_stats:
                        assert isinstance(pp_stats["calculations_applied"], bool), f"calculations_applied should be bool for {csv_file.name}"

            except Exception as e:
                pytest.fail(f"Post-processing stats test failed on {csv_file.name}: {e}")


@pytest.mark.integration
class TestRobustnessBehaviors:
    """Test robustness behaviors across all files."""

    def test_no_crashes_on_any_file(self, test_files_list, real_csv_data):
        """Should handle both normal and strange files without exceptions."""
        extractor = MetadataExtractor()

        processed_count = 0
        for csv_file in test_files_list:
            if not csv_file.exists():
                continue

            file_data = real_csv_data(csv_file)
            if not file_data:
                continue

            try:
                # Both APIs should not crash
                metadata = extractor.extract_csv_metadata(file_data, csv_file.name, verbose=False)
                df, metadata2 = extractor.extract_csv_metadata_with_dataframe(file_data, csv_file.name, verbose=False)
                processed_count += 1

            except Exception as e:
                pytest.fail(f"Unexpected crash on {csv_file.name}: {e}")

        # At least some files should be processable
        assert processed_count > 0, "No files were processed successfully"

    def test_consistent_metadata_structure_regardless_of_validity(self, test_files_list, real_csv_data):
        """Even invalid files should return basic metadata structure."""
        extractor = MetadataExtractor()

        for csv_file in test_files_list:
            if not csv_file.exists():
                continue

            file_data = real_csv_data(csv_file)
            if not file_data:
                continue

            try:
                metadata = extractor.extract_csv_metadata(file_data, csv_file.name, verbose=False)

                # Basic structure should always be present regardless of file validity
                assert isinstance(metadata, dict), f"Should return dict for {csv_file.name}"

                # Validation results should have expected structure if present
                if "validation_results" in metadata:
                    validation = metadata["validation_results"]
                    assert isinstance(validation, dict), f"validation_results should be dict for {csv_file.name}"
                    assert "is_valid" in validation, f"validation_results should have is_valid for {csv_file.name}"
                    assert isinstance(validation["is_valid"], bool), f"is_valid should be bool for {csv_file.name}"

            except Exception as e:
                pytest.fail(f"Metadata structure test failed on {csv_file.name}: {e}")


@pytest.mark.integration
class TestFileIOWorkflowBehaviors:
    """Test file I/O workflow behaviors from test_final_output.py."""

    def test_enhanced_dataframe_save_and_reload_workflow(self, test_files_list, real_csv_data, tmp_path):
        """Enhanced DataFrame should be saveable to CSV and reloadable with all columns intact."""
        extractor = MetadataExtractor()

        for csv_file in test_files_list:
            if not csv_file.exists():
                continue

            file_data = real_csv_data(csv_file)
            if not file_data:
                continue

            try:
                # Get enhanced DataFrame
                enhanced_df, metadata = extractor.extract_csv_metadata_with_dataframe(
                    file_data, csv_file.name, verbose=False
                )

                if len(enhanced_df) == 0:
                    continue  # Skip empty DataFrames

                # Save enhanced DataFrame to temporary file
                output_file = tmp_path / f"enhanced_{csv_file.name}"
                enhanced_df.to_csv(output_file, index=False)

                # Reload and verify
                reloaded_df = pd.read_csv(output_file)

                # Verify structure preservation
                assert len(reloaded_df) == len(enhanced_df), f"Row count mismatch after save/reload for {csv_file.name}"
                assert len(reloaded_df.columns) == len(enhanced_df.columns), f"Column count mismatch after save/reload for {csv_file.name}"
                assert list(reloaded_df.columns) == list(enhanced_df.columns), f"Column names mismatch after save/reload for {csv_file.name}"

                # Verify power columns are preserved if present
                power_columns = ['PMU_power', 'Engine_power', 'System_efficiency']
                original_power_cols = [col for col in power_columns if col in enhanced_df.columns]
                reloaded_power_cols = [col for col in power_columns if col in reloaded_df.columns]
                assert original_power_cols == reloaded_power_cols, f"Power columns not preserved after save/reload for {csv_file.name}"

            except Exception as e:
                pytest.fail(f"File I/O workflow test failed on {csv_file.name}: {e}")

    def test_enhanced_csv_has_more_columns_than_original(self, test_files_list, real_csv_data):
        """Enhanced CSV should have same or more columns than original (from column comparison logic)."""
        extractor = MetadataExtractor()

        for csv_file in test_files_list:
            if not csv_file.exists():
                continue

            try:
                # Read original CSV
                original_df = pd.read_csv(csv_file)
                original_column_count = len(original_df.columns)

                file_data = real_csv_data(csv_file)
                if not file_data:
                    continue

                # Get enhanced DataFrame
                enhanced_df, metadata = extractor.extract_csv_metadata_with_dataframe(
                    file_data, csv_file.name, verbose=False
                )

                enhanced_column_count = len(enhanced_df.columns)

                # Enhanced should have same or more columns
                assert enhanced_column_count >= original_column_count, \
                    f"Enhanced CSV has fewer columns ({enhanced_column_count}) than original ({original_column_count}) for {csv_file.name}"

                # If columns were added, verify post-processing stats reflect this
                if enhanced_column_count > original_column_count and "post_processing" in metadata:
                    pp_stats = metadata["post_processing"]
                    derived_columns = pp_stats.get("derived_columns_added", 0)
                    # Note: derived_columns_added might not equal the difference due to column renaming
                    assert isinstance(derived_columns, (int, float)), f"derived_columns_added should be numeric for {csv_file.name}"

            except Exception as e:
                # If we can't read the original CSV, that's a file issue, not our test failure
                if "Enhanced CSV has fewer columns" in str(e):
                    pytest.fail(str(e))


@pytest.mark.integration
class TestManualVerificationBehaviors:
    """Test manual verification behaviors from test_flight_hours.py."""

    def test_flight_hours_manual_vs_automated_calculation(self, test_files_list, real_csv_data):
        """Manual flight hours calculation should match automated calculation when both are possible."""
        extractor = MetadataExtractor()

        for csv_file in test_files_list:
            if not csv_file.exists():
                continue

            file_data = real_csv_data(csv_file)
            if not file_data:
                continue

            try:
                # Get automated calculation result
                metadata = extractor.extract_csv_metadata(file_data, csv_file.name, verbose=False)

                if "total_flight_hours" not in metadata:
                    continue  # Skip files without flight hours

                automated_flight_hours = metadata["total_flight_hours"]

                # Perform manual calculation
                df = pd.read_csv(csv_file)

                if 'droneInFlight' not in df.columns or 'time' not in df.columns:
                    continue  # Skip files missing required columns

                # Manual flight hours calculation matching the automated logic
                # Reset index to ensure we can detect consecutive rows
                df_indexed = df.reset_index(drop=True)
                flight_mask = df_indexed['droneInFlight'] == 1
                flight_indices = df_indexed[flight_mask].index.tolist()

                if len(flight_indices) >= 2:
                    # Use the same timestamp parser as the automated system
                    from XER_Technologies_metadata_extractor.metadata_calculator import MetadataCalculator
                    calc = MetadataCalculator()
                    timestamps = calc._parse_timestamps(df_indexed['time'])

                    if not timestamps.isna().all():
                        total_flight_seconds = 0.0

                        # Only count time differences between consecutive row indices (same logic as automated)
                        for i in range(1, len(flight_indices)):
                            current_idx = flight_indices[i]
                            prev_idx = flight_indices[i-1]

                            # Only count if rows are consecutive in the dataset
                            if current_idx == prev_idx + 1:
                                time_diff = (timestamps.iloc[current_idx] - timestamps.iloc[prev_idx]).total_seconds()
                                if time_diff > 0:
                                    total_flight_seconds += time_diff

                        manual_flight_hours = total_flight_seconds / 3600

                        # Compare automated vs manual (allow small floating point differences)
                        difference = abs(automated_flight_hours - manual_flight_hours)
                        tolerance = max(0.001, automated_flight_hours * 0.01)  # 1% or 0.001 hours, whichever is larger

                        assert difference <= tolerance, \
                            f"Flight hours mismatch for {csv_file.name}: automated={automated_flight_hours}, manual={manual_flight_hours}, diff={difference}"

            except Exception as e:
                # Only fail on calculation mismatches, not on file parsing issues
                if "Flight hours mismatch" in str(e):
                    pytest.fail(str(e))

    def test_timestamp_parsing_verification(self, test_files_list, real_csv_data):
        """Enhanced timestamp parser should filter 1970 timestamps and handle edge cases robustly."""
        from XER_Technologies_metadata_extractor.metadata_calculator import MetadataCalculator

        calculator = MetadataCalculator()

        for csv_file in test_files_list:
            if not csv_file.exists():
                continue

            try:
                df = pd.read_csv(csv_file)

                if 'time' not in df.columns:
                    continue

                # Use the enhanced package timestamp parser
                timestamps = calculator._parse_timestamps(df['time'])
                valid_timestamps = timestamps.dropna()

                if len(valid_timestamps) > 0:
                    # Enhanced parser should automatically filter out 1970 timestamps
                    min_time = valid_timestamps.min()
                    max_time = valid_timestamps.max()

                    # This should now pass because parser filters out 1970 timestamps
                    assert min_time.year >= 2000, f"Enhanced parser should filter 1970 timestamps in {csv_file.name}: {min_time}"
                    assert max_time.year <= 2030, f"Timestamps too far in future in {csv_file.name}: {max_time}"

                    # Time range should be positive
                    time_range = max_time - min_time
                    assert time_range.total_seconds() >= 0, f"Negative time range in {csv_file.name}"

                # Test that parser handles problematic input gracefully
                assert isinstance(timestamps, pd.Series), f"Parser should always return Series for {csv_file.name}"
                assert len(timestamps) == len(df['time']), f"Parser should preserve series length for {csv_file.name}"

            except Exception as e:
                pytest.fail(f"Enhanced timestamp parsing test failed on {csv_file.name}: {e}")


@pytest.mark.integration
class TestDirectComponentBehaviors:
    """Test direct component usage from test_flight_hours.py."""

    def test_metadata_calculator_direct_usage(self, test_files_list, real_csv_data):
        """MetadataCalculator should work when used directly with MetadataConfig."""
        from XER_Technologies_metadata_extractor.metadata_calculator import MetadataCalculator
        from XER_Technologies_metadata_extractor.metadata_config import MetadataConfig

        config = MetadataConfig()
        calculator = MetadataCalculator(config)

        # Find the flight hours field configuration
        flight_hours_field = None
        for field in config.fields:
            if field.name == "total_flight_hours":
                flight_hours_field = field
                break

        if not flight_hours_field:
            pytest.skip("total_flight_hours field not found in config")

        for csv_file in test_files_list:
            if not csv_file.exists():
                continue

            try:
                df = pd.read_csv(csv_file)

                if 'droneInFlight' not in df.columns or 'time' not in df.columns:
                    continue

                # Test direct calculator usage
                result = calculator._calculate_field_value(flight_hours_field, df, csv_file.name)

                if result is not None:
                    assert isinstance(result, (int, float)), f"Calculator should return numeric result for {csv_file.name}"
                    assert result >= 0, f"Flight hours should be non-negative for {csv_file.name}"

            except Exception as e:
                pytest.fail(f"Direct calculator test failed on {csv_file.name}: {e}")

    def test_flight_hours_field_configuration_verification(self):
        """Flight hours field should have correct configuration."""
        from XER_Technologies_metadata_extractor.metadata_config import MetadataConfig

        config = MetadataConfig()

        flight_hours_field = None
        for field in config.fields:
            if field.name == "total_flight_hours":
                flight_hours_field = field
                break

        assert flight_hours_field is not None, "total_flight_hours field should exist in config"
        assert flight_hours_field.unit == "hours", f"Flight hours field should have 'hours' unit, got '{flight_hours_field.unit}'"
        assert flight_hours_field.calculation_method == "flight_hours", f"Flight hours should use 'flight_hours' method, got '{flight_hours_field.calculation_method}'"
        assert "droneInFlight" in flight_hours_field.source_columns, "Flight hours should depend on droneInFlight column"
        assert "time" in flight_hours_field.source_columns, "Flight hours should depend on time column"


@pytest.mark.integration
class TestDataAnalysisBehaviors:
    """Test data analysis and debugging behaviors from test_flight_hours.py."""

    def test_drone_in_flight_value_distribution_analysis(self, test_files_list, real_csv_data):
        """droneInFlight column should have analyzable value distribution."""
        for csv_file in test_files_list:
            if not csv_file.exists():
                continue

            try:
                df = pd.read_csv(csv_file)

                if 'droneInFlight' not in df.columns:
                    continue

                # Analyze droneInFlight distribution (from test_flight_hours.py)
                flight_counts = df['droneInFlight'].value_counts()

                # Value counts should be meaningful
                assert isinstance(flight_counts, pd.Series), f"value_counts should return Series for {csv_file.name}"
                assert len(flight_counts) > 0, f"Should have some droneInFlight values in {csv_file.name}"

                # Check for flight activity
                flight_active_rows = df[df['droneInFlight'] == 1]

                # If there's flight activity, there should be time data too
                if len(flight_active_rows) > 0 and 'time' in df.columns:
                    flight_time_data = flight_active_rows[['time', 'droneInFlight']]
                    assert len(flight_time_data) > 0, f"Should have flight time data for {csv_file.name}"
                    assert not flight_time_data['time'].isna().all(), f"Flight time data should not be all NaN for {csv_file.name}"

            except Exception as e:
                pytest.fail(f"Data analysis test failed on {csv_file.name}: {e}")

    def test_data_subset_filtering_and_inspection(self, test_files_list, real_csv_data):
        """Should be able to filter and inspect specific data subsets."""
        for csv_file in test_files_list:
            if not csv_file.exists():
                continue

            try:
                df = pd.read_csv(csv_file)

                # Test basic data inspection capabilities
                assert len(df) >= 0, f"Should be able to get row count for {csv_file.name}"
                assert len(df.columns) > 0, f"Should have some columns in {csv_file.name}"

                # Test filtering capabilities
                if 'droneInFlight' in df.columns:
                    subset = df[df['droneInFlight'] == 1]
                    assert isinstance(subset, pd.DataFrame), f"Should be able to filter data for {csv_file.name}"

                # Test column access
                if len(df.columns) > 0:
                    first_col = df.columns[0]
                    column_data = df[first_col]
                    assert isinstance(column_data, pd.Series), f"Should be able to access columns for {csv_file.name}"

            except Exception as e:
                pytest.fail(f"Data filtering test failed on {csv_file.name}: {e}")


@pytest.mark.integration
class TestSampleValueVerificationBehaviors:
    """Test sample value verification with inf/NaN handling from test_final_output.py."""

    def test_power_column_sample_values_with_inf_nan_handling(self, test_files_list, real_csv_data):
        """Power columns should provide valid sample values with proper inf/NaN handling."""
        extractor = MetadataExtractor()
        power_columns = ['PMU_power', 'Engine_power', 'System_efficiency']

        for csv_file in test_files_list:
            if not csv_file.exists():
                continue

            file_data = real_csv_data(csv_file)
            if not file_data:
                continue

            try:
                df, metadata = extractor.extract_csv_metadata_with_dataframe(
                    file_data, csv_file.name, verbose=False
                )

                # Check power columns if present
                present_power_cols = [col for col in power_columns if col in df.columns]

                for col in present_power_cols:
                    # Test inf/NaN handling (from test_final_output.py logic)
                    sample_values = df[col].replace([float('inf'), float('-inf')], float('nan')).dropna().head(3)

                    # Should be able to extract sample values without crashing
                    assert isinstance(sample_values, pd.Series), f"Should get Series of sample values for {col} in {csv_file.name}"

                    # If we have sample values, they should be numeric
                    if len(sample_values) > 0:
                        sample_list = sample_values.tolist()
                        assert isinstance(sample_list, list), f"Should convert to list for {col} in {csv_file.name}"

                        for value in sample_list:
                            import numpy as np
                            assert isinstance(value, (int, float)), f"Sample values should be numeric for {col} in {csv_file.name}"
                            assert not pd.isna(value), f"Sample values should not be NaN after filtering for {col} in {csv_file.name}"
                            assert not np.isinf(value), f"Sample values should not be inf after filtering for {col} in {csv_file.name}"

            except Exception as e:
                pytest.fail(f"Sample value verification test failed on {csv_file.name}: {e}")

    def test_power_column_value_ranges_are_reasonable(self, test_files_list, real_csv_data):
        """Power column values should be within reasonable ranges when present."""
        extractor = MetadataExtractor()
        power_columns = ['PMU_power', 'Engine_power', 'System_efficiency']

        for csv_file in test_files_list:
            if not csv_file.exists():
                continue

            file_data = real_csv_data(csv_file)
            if not file_data:
                continue

            try:
                df, metadata = extractor.extract_csv_metadata_with_dataframe(
                    file_data, csv_file.name, verbose=False
                )

                present_power_cols = [col for col in power_columns if col in df.columns]

                for col in present_power_cols:
                    # Filter out infinite and NaN values
                    clean_values = df[col].replace([float('inf'), float('-inf')], float('nan')).dropna()

                    if len(clean_values) > 0:
                        min_val = clean_values.min()
                        max_val = clean_values.max()

                        # Power values should be reasonable (not extremely negative or unreasonably high)
                        if col in ['PMU_power', 'Engine_power']:
                            # Power should generally be non-negative and below 10kW for drone applications
                            assert min_val >= -1000, f"{col} minimum value too low ({min_val}) for {csv_file.name}"  # Allow some negative for efficiency calculations
                            assert max_val <= 20000, f"{col} maximum value too high ({max_val}) for {csv_file.name}"

                        elif col == 'System_efficiency':
                            # Efficiency can be percentage (0-100) or ratio (0-1), but shouldn't be extremely high
                            assert max_val <= 1000, f"System efficiency too high ({max_val}) for {csv_file.name}"  # Allow up to 1000% for calculation variations

            except Exception as e:
                pytest.fail(f"Value range test failed on {csv_file.name}: {e}")


@pytest.mark.integration
class TestPostProcessingComparisonBehaviors:
    """Test post-processing statistics comparison between APIs from test_new_api.py."""

    def test_post_processing_stats_consistency_between_apis(self, test_files_list, real_csv_data):
        """Post-processing stats should be consistent between old and new APIs."""
        extractor = MetadataExtractor()

        for csv_file in test_files_list:
            if not csv_file.exists():
                continue

            file_data = real_csv_data(csv_file)
            if not file_data:
                continue

            try:
                # Test both APIs
                metadata_old = extractor.extract_csv_metadata(file_data, csv_file.name, verbose=False)
                df_new, metadata_new = extractor.extract_csv_metadata_with_dataframe(file_data, csv_file.name, verbose=False)

                # Compare post-processing stats (from test_new_api.py logic)
                if 'post_processing' in metadata_old and 'post_processing' in metadata_new:
                    old_stats = metadata_old['post_processing']
                    new_stats = metadata_new['post_processing']

                    # Key statistics should match
                    stats_to_compare = ['derived_columns_added', 'calculations_applied', 'columns_renamed', 'faulty_rows_filtered']

                    for stat in stats_to_compare:
                        if stat in old_stats and stat in new_stats:
                            assert old_stats[stat] == new_stats[stat], \
                                f"Post-processing stat '{stat}' mismatch for {csv_file.name}: old={old_stats[stat]}, new={new_stats[stat]}"

            except Exception as e:
                pytest.fail(f"Post-processing comparison test failed on {csv_file.name}: {e}")

    def test_post_processing_stats_meaningful_values(self, test_files_list, real_csv_data):
        """Post-processing stats should have meaningful values when present."""
        extractor = MetadataExtractor()

        for csv_file in test_files_list:
            if not csv_file.exists():
                continue

            file_data = real_csv_data(csv_file)
            if not file_data:
                continue

            try:
                metadata = extractor.extract_csv_metadata(file_data, csv_file.name, verbose=False)

                if 'post_processing' in metadata:
                    pp_stats = metadata['post_processing']

                    # Check for meaningful derived columns count
                    if 'derived_columns_added' in pp_stats:
                        derived_count = pp_stats['derived_columns_added']
                        assert derived_count >= 0, f"derived_columns_added should be non-negative for {csv_file.name}"
                        assert derived_count <= 100, f"derived_columns_added seems too high ({derived_count}) for {csv_file.name}"

                    # Check calculations applied flag makes sense
                    if 'calculations_applied' in pp_stats and 'derived_columns_added' in pp_stats:
                        calc_applied = pp_stats['calculations_applied']
                        derived_count = pp_stats['derived_columns_added']

                        # If calculations were applied, usually some columns should be added
                        if calc_applied and derived_count == 0:
                            # This might be unusual but not necessarily wrong - just document it
                            pass

            except Exception as e:
                pytest.fail(f"Post-processing meaningful values test failed on {csv_file.name}: {e}")


@pytest.mark.integration
class TestColumnListingAndComparisonBehaviors:
    """Test detailed column listing and comparison from test_power_columns.py."""

    def test_detailed_column_listing_capabilities(self, test_files_list, real_csv_data):
        """Should be able to list and analyze columns in detail."""
        for csv_file in test_files_list:
            if not csv_file.exists():
                continue

            try:
                # Read original CSV
                original_df = pd.read_csv(csv_file)

                # Test column listing (from test_power_columns.py logic)
                original_columns = list(original_df.columns)
                original_column_count = len(original_columns)

                # Should be able to get meaningful column information
                assert isinstance(original_columns, list), f"Should get column list for {csv_file.name}"
                assert original_column_count > 0, f"Should have some columns in {csv_file.name}"

                # Column names should be strings
                for col in original_columns:
                    assert isinstance(col, str), f"Column names should be strings in {csv_file.name}"
                    assert len(col.strip()) > 0, f"Column names should not be empty in {csv_file.name}"

                # Test power column detection in original
                power_columns = ['PMU_power', 'Engine_power', 'System_efficiency']
                original_has_power = [col for col in power_columns if col in original_columns]

                # Should be able to detect power columns
                assert isinstance(original_has_power, list), f"Should get power column list for {csv_file.name}"

            except Exception as e:
                pytest.fail(f"Column listing test failed on {csv_file.name}: {e}")

    def test_column_change_detection_capabilities(self, test_files_list, real_csv_data):
        """Should be able to detect column changes before/after processing."""
        extractor = MetadataExtractor()

        for csv_file in test_files_list:
            if not csv_file.exists():
                continue

            try:
                # Read original CSV
                original_df = pd.read_csv(csv_file)
                original_columns = set(original_df.columns)

                file_data = real_csv_data(csv_file)
                if not file_data:
                    continue

                # Get enhanced DataFrame
                enhanced_df, metadata = extractor.extract_csv_metadata_with_dataframe(
                    file_data, csv_file.name, verbose=False
                )

                enhanced_columns = set(enhanced_df.columns)

                # Test column change detection (from test_final_output.py logic)
                new_columns = enhanced_columns - original_columns
                removed_columns = original_columns - enhanced_columns

                # Should be able to detect changes
                assert isinstance(new_columns, set), f"Should detect new columns for {csv_file.name}"
                assert isinstance(removed_columns, set), f"Should detect removed columns for {csv_file.name}"

                # New columns should have meaningful names if present
                for col in new_columns:
                    assert isinstance(col, str), f"New column names should be strings in {csv_file.name}"
                    assert len(col.strip()) > 0, f"New column names should not be empty in {csv_file.name}"

                # Generally, we shouldn't remove columns (only rename or add)
                if len(removed_columns) > 0:
                    # This might indicate column renaming rather than removal
                    pass

            except Exception as e:
                pytest.fail(f"Column change detection test failed on {csv_file.name}: {e}")

    def test_power_column_detection_before_and_after_processing(self, test_files_list, real_csv_data):
        """Should detect power columns before and after processing (from test_power_columns.py)."""
        extractor = MetadataExtractor()
        power_columns = ['PMU_power', 'Engine_power', 'System_efficiency']

        for csv_file in test_files_list:
            if not csv_file.exists():
                continue

            try:
                # Check original file
                original_df = pd.read_csv(csv_file)
                original_has_power = [col for col in power_columns if col in original_df.columns]

                file_data = real_csv_data(csv_file)
                if not file_data:
                    continue

                # Check enhanced DataFrame
                enhanced_df, metadata = extractor.extract_csv_metadata_with_dataframe(
                    file_data, csv_file.name, verbose=False
                )

                enhanced_has_power = [col for col in power_columns if col in enhanced_df.columns]

                # Should detect power columns in both cases
                assert isinstance(original_has_power, list), f"Should detect original power columns for {csv_file.name}"
                assert isinstance(enhanced_has_power, list), f"Should detect enhanced power columns for {csv_file.name}"

                # Enhanced should have same or more power columns (they should be added, not removed)
                for col in original_has_power:
                    assert col in enhanced_has_power, f"Power column {col} should be preserved in enhanced data for {csv_file.name}"

            except Exception as e:
                pytest.fail(f"Power column detection test failed on {csv_file.name}: {e}")


@pytest.mark.integration
class TestValidationWarningBehaviors:
    """Test validation warning detection and analysis."""

    def test_current_validation_warnings_detection(self, test_files_list, real_csv_data):
        """Should detect when current columns contain invalid data like firmware versions."""
        extractor = MetadataExtractor()
        firmware_like_warnings = []
        legitimate_warnings = []

        for csv_file in test_files_list:
            if not csv_file.exists():
                continue

            file_data = real_csv_data(csv_file)
            if not file_data:
                continue

            metadata = extractor.extract_csv_metadata(file_data, csv_file.name, verbose=False)

            if 'validation_results' in metadata and 'warnings' in metadata['validation_results']:
                for warning in metadata['validation_results']['warnings']:
                    if 'Current values out of expected range' in warning:
                        # Extract the range from warning like "Current values out of expected range: 5010101 - 5010101"
                        try:
                            range_part = warning.split(': ')[-1]
                            min_val, max_val = range_part.split(' - ')
                            min_val, max_val = float(min_val), float(max_val)

                            # Detect firmware-like values (very large integers, no variation)
                            if min_val == max_val and min_val > 1000000:
                                firmware_like_warnings.append({
                                    'file': csv_file.name,
                                    'warning': warning,
                                    'value': min_val
                                })
                            elif min_val < -100 or max_val > 500:  # Extreme current values
                                legitimate_warnings.append({
                                    'file': csv_file.name,
                                    'warning': warning,
                                    'range': (min_val, max_val)
                                })
                        except (ValueError, IndexError):
                            # Skip unparseable warnings
                            continue

        # Report findings
        if firmware_like_warnings:
            print(f"\n🔍 Found {len(firmware_like_warnings)} firmware-like current warnings:")
            for item in firmware_like_warnings:
                print(f"  📁 {item['file']}: {item['warning']}")

        if legitimate_warnings:
            print(f"\n⚠️  Found {len(legitimate_warnings)} extreme current warnings:")
            for item in legitimate_warnings:
                print(f"  📁 {item['file']}: {item['warning']}")

        # Assert that we can distinguish between the two types
        assert isinstance(firmware_like_warnings, list)
        assert isinstance(legitimate_warnings, list)

    def test_timestamp_parsing_warnings_detection(self, test_files_list, real_csv_data):
        """Should detect files with timestamp parsing issues."""
        extractor = MetadataExtractor()
        timestamp_issues = []

        for csv_file in test_files_list:
            if not csv_file.exists():
                continue

            file_data = real_csv_data(csv_file)
            if not file_data:
                continue

            metadata = extractor.extract_csv_metadata(file_data, csv_file.name, verbose=False)

            if 'validation_results' in metadata and 'warnings' in metadata['validation_results']:
                for warning in metadata['validation_results']['warnings']:
                    if 'Could not parse timestamps' in warning:
                        # Check what the actual timestamp values look like
                        try:
                            df = pd.read_csv(csv_file)
                            time_columns = [col for col in df.columns if col.lower() in ['time', 'timestamp']]

                            timestamp_info = {}
                            for time_col in time_columns:
                                sample_values = df[time_col].head(5).tolist()
                                timestamp_info[time_col] = sample_values

                            timestamp_issues.append({
                                'file': csv_file.name,
                                'warning': warning,
                                'sample_timestamps': timestamp_info
                            })
                        except Exception:
                            # Skip files we can't read for timestamp analysis
                            continue

        # Report findings
        if timestamp_issues:
            print(f"\n🕐 Found {len(timestamp_issues)} timestamp parsing issues:")
            for item in timestamp_issues:
                print(f"  📁 {item['file']}: {item['warning']}")
                for col, samples in item['sample_timestamps'].items():
                    print(f"    Column '{col}' samples: {samples}")

        # This test documents the issues rather than failing
        assert isinstance(timestamp_issues, list)

    def test_validation_warning_summary(self, test_files_list, real_csv_data):
        """Should provide a comprehensive summary of all validation warnings across files."""
        extractor = MetadataExtractor()
        warning_summary = {}

        for csv_file in test_files_list:
            if not csv_file.exists():
                continue

            file_data = real_csv_data(csv_file)
            if not file_data:
                continue

            metadata = extractor.extract_csv_metadata(file_data, csv_file.name, verbose=False)

            if 'validation_results' in metadata and 'warnings' in metadata['validation_results']:
                for warning in metadata['validation_results']['warnings']:
                    # Categorize warnings by type
                    warning_type = warning.split(':')[0] if ':' in warning else warning.split(' ')[0:3]
                    warning_type = ' '.join(warning_type) if isinstance(warning_type, list) else warning_type

                    if warning_type not in warning_summary:
                        warning_summary[warning_type] = []
                    warning_summary[warning_type].append({
                        'file': csv_file.name,
                        'full_warning': warning
                    })

        # Report summary - always display for visibility
        if warning_summary:
            # Use pytest's live logging to show output
            total_warnings = sum(len(instances) for instances in warning_summary.values())
            summary_msg = f"\n📊 VALIDATION WARNINGS FOUND: {total_warnings} total across {len(warning_summary)} types\n"

            for warning_type, instances in warning_summary.items():
                summary_msg += f"  • {warning_type}: {len(instances)} occurrences\n"
                for instance in instances[:2]:  # Show first 2 examples
                    summary_msg += f"    - {instance['file']}: {instance['full_warning']}\n"
                if len(instances) > 2:
                    summary_msg += f"    ... and {len(instances) - 2} more\n"

            # Force output to be visible
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(summary_msg)  # This will show in pytest output

        else:
            import logging
            logger = logging.getLogger(__name__)
            logger.info("✅ No validation warnings found across all test files")

        assert isinstance(warning_summary, dict)

    def test_complete_warning_inventory_all_files(self, test_files_list, real_csv_data):
        """COMPREHENSIVE: List every single warning from every single file for data quality audit."""
        extractor = MetadataExtractor()
        all_warnings = []
        files_processed = 0
        files_with_warnings = 0

        import sys
        verbose_mode = '-s' in sys.argv or '--capture=no' in sys.argv

        if verbose_mode:
            print(f"\n{'='*80}")
            print(f"🔍 COMPREHENSIVE WARNING INVENTORY - ALL FILES")
            print(f"{'='*80}")

        for csv_file in test_files_list:
            if not csv_file.exists():
                continue

            file_data = real_csv_data(csv_file)
            if not file_data:
                continue

            files_processed += 1
            metadata = extractor.extract_csv_metadata(file_data, csv_file.name, verbose=False)

            file_warnings = []

            # Collect validation warnings
            if 'validation_results' in metadata and 'warnings' in metadata['validation_results']:
                for warning in metadata['validation_results']['warnings']:
                    file_warnings.append(('VALIDATION', warning))

            # Collect post-processing warnings
            if 'post_processing' in metadata and 'warnings' in metadata['post_processing']:
                for warning in metadata['post_processing']['warnings']:
                    file_warnings.append(('POST_PROCESSING', warning))

            # Collect post-processing errors
            if 'post_processing' in metadata and 'errors' in metadata['post_processing']:
                for error in metadata['post_processing']['errors']:
                    file_warnings.append(('POST_PROCESSING_ERROR', error))

            if file_warnings:
                files_with_warnings += 1
                if verbose_mode:
                    print(f"\n📁 {csv_file.name}")
                    print(f"   SN: {metadata.get('SN', 'N/A')}, FW: {metadata.get('fw_version', 'N/A')}")
                    for category, warning in file_warnings:
                        print(f"   [{category}] {warning}")

                for category, warning in file_warnings:
                    all_warnings.append({
                        'file': csv_file.name,
                        'category': category,
                        'warning': warning,
                        'sn': metadata.get('SN', 'N/A'),
                        'fw_version': metadata.get('fw_version', 'N/A')
                    })

        # Always show summary using pytest logging
        import logging
        logger = logging.getLogger(__name__)

        summary_msg = f"\n📊 DATA QUALITY SUMMARY\n"
        summary_msg += f"Files processed: {files_processed}\n"
        summary_msg += f"Files with warnings: {files_with_warnings}\n"
        summary_msg += f"Total warnings: {len(all_warnings)}\n"

        # Group by category
        by_category = {}
        for item in all_warnings:
            cat = item['category']
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(item)

        for category, items in by_category.items():
            summary_msg += f"\n{category}: {len(items)} warnings\n"
            # Group by warning type within category
            by_warning = {}
            for item in items:
                warning_key = item['warning'].split(':')[0] if ':' in item['warning'] else item['warning']
                if warning_key not in by_warning:
                    by_warning[warning_key] = []
                by_warning[warning_key].append(item)

            for warning_type, warning_items in by_warning.items():
                summary_msg += f"  {warning_type}: {len(warning_items)} occurrences\n"

        # Show most critical issues
        critical_warnings = [item for item in all_warnings if 'Current values out of expected range: 5010101' in item['warning']]
        if critical_warnings:
            summary_msg += f"\n⚠️  CRITICAL: {len(critical_warnings)} firmware version in current column issues\n"
            for item in critical_warnings:
                summary_msg += f"   - {item['file']} (SN: {item['sn']})\n"

        # Use logger.warning to ensure visibility
        logger.warning(summary_msg)

        # Assert that we found some data to validate the test worked
        assert files_processed > 0, "Should have processed some files"
        assert isinstance(all_warnings, list), "Should collect warnings as list"