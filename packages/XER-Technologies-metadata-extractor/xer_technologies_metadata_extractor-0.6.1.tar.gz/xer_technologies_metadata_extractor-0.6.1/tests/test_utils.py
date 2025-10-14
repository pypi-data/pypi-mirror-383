"""
Test utilities and helper functions for the test suite.
"""
import os
import tempfile
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd


def create_test_csv(content: str, filename: str = "test.csv") -> Path:
    """
    Create a temporary CSV file for testing.

    Args:
        content: CSV content as string
        filename: Name for the temporary file

    Returns:
        Path to the created temporary file
    """
    temp_dir = Path(tempfile.mkdtemp())
    temp_file = temp_dir / filename

    with open(temp_file, 'w', encoding='utf-8') as f:
        f.write(content)

    return temp_file


def create_test_dataframe(
    rows: int = 100,
    include_flight_data: bool = True,
    include_power_data: bool = False
) -> pd.DataFrame:
    """
    Create a test DataFrame with realistic XER data structure.

    Args:
        rows: Number of rows to generate
        include_flight_data: Whether to include droneInFlight column
        include_power_data: Whether to include power-related columns

    Returns:
        Test DataFrame
    """
    import numpy as np

    # Base timestamp (Unix milliseconds)
    base_time = 1609459200000  # 2021-01-01 00:00:00

    data = {
        'time': [base_time + (i * 1000) for i in range(rows)],  # 1 second intervals
        'latitude': np.random.normal(59.3293, 0.001, rows),  # Around Stockholm
        'longitude': np.random.normal(18.0686, 0.001, rows),
        'altitude': np.random.uniform(5, 100, rows),  # 5-100 meters
        'battery_voltage': np.random.uniform(11.0, 12.6, rows),  # Realistic battery voltage
        'current': np.random.uniform(1.0, 5.0, rows),  # Current draw in amps
    }

    if include_flight_data:
        # Create realistic flight patterns (periods of flight)
        flight_status = np.zeros(rows, dtype=int)
        current_status = 0
        status_duration = 0

        for i in range(rows):
            if status_duration <= 0:
                # Change status
                current_status = 1 - current_status
                if current_status == 1:  # Starting flight
                    status_duration = np.random.randint(10, 50)  # 10-50 seconds of flight
                else:  # Landing
                    status_duration = np.random.randint(5, 20)   # 5-20 seconds on ground

            flight_status[i] = current_status
            status_duration -= 1

        data['droneInFlight'] = flight_status

    if include_power_data:
        data['PMU_power'] = data['battery_voltage'] * data['current']
        data['Engine_power'] = np.random.uniform(50, 200, rows)  # Mock engine power
        data['System_efficiency'] = np.random.uniform(0.7, 0.95, rows)  # 70-95% efficiency

    return pd.DataFrame(data)


def assert_metadata_structure(metadata: Dict[str, Any]) -> None:
    """
    Assert that metadata has the expected basic structure.

    Args:
        metadata: Metadata dictionary to validate
    """
    required_keys = ["filename", "file_size", "validation"]

    for key in required_keys:
        assert key in metadata, f"Required key '{key}' missing from metadata"

    assert isinstance(metadata["filename"], str)
    assert isinstance(metadata["file_size"], (int, float))
    assert metadata["file_size"] >= 0

    validation = metadata["validation"]
    assert isinstance(validation, dict)
    assert "is_valid" in validation
    assert "message" in validation
    assert isinstance(validation["is_valid"], bool)
    assert isinstance(validation["message"], str)


def assert_power_columns_present(dataframe: pd.DataFrame, expected_columns: List[str] = None) -> List[str]:
    """
    Check for presence of power columns in DataFrame and return which ones are present.

    Args:
        dataframe: DataFrame to check
        expected_columns: List of expected power columns (defaults to standard power columns)

    Returns:
        List of power columns that are present
    """
    if expected_columns is None:
        expected_columns = ['PMU_power', 'Engine_power', 'System_efficiency']

    present_columns = [col for col in expected_columns if col in dataframe.columns]
    return present_columns


def assert_flight_hours_calculation(metadata: Dict[str, Any]) -> None:
    """
    Assert that flight hours calculation is reasonable if present.

    Args:
        metadata: Metadata dictionary containing flight hours
    """
    if "total_flight_hours" in metadata:
        flight_hours = metadata["total_flight_hours"]
        assert isinstance(flight_hours, (int, float)), "Flight hours should be numeric"
        assert flight_hours >= 0, "Flight hours should be non-negative"
        assert flight_hours <= 24, "Flight hours should be reasonable (less than 24h per log)"


def get_test_file_info(file_path: Path) -> Dict[str, Any]:
    """
    Get basic information about a test file.

    Args:
        file_path: Path to the test file

    Returns:
        Dictionary with file information
    """
    if not file_path.exists():
        return {"exists": False, "size": 0, "name": file_path.name}

    stat = file_path.stat()
    return {
        "exists": True,
        "name": file_path.name,
        "size": stat.st_size,
        "modified": stat.st_mtime,
        "is_csv": file_path.suffix.lower() == ".csv"
    }


def compare_dataframes(df1: pd.DataFrame, df2: pd.DataFrame, tolerance: float = 1e-10) -> Dict[str, Any]:
    """
    Compare two DataFrames and return comparison results.

    Args:
        df1: First DataFrame
        df2: Second DataFrame
        tolerance: Numerical tolerance for floating point comparisons

    Returns:
        Dictionary with comparison results
    """
    comparison = {
        "shapes_equal": df1.shape == df2.shape,
        "columns_equal": list(df1.columns) == list(df2.columns),
        "common_columns": list(set(df1.columns) & set(df2.columns)),
        "df1_only_columns": list(set(df1.columns) - set(df2.columns)),
        "df2_only_columns": list(set(df2.columns) - set(df1.columns))
    }

    if comparison["shapes_equal"] and comparison["columns_equal"]:
        # Check if data is equal within tolerance
        try:
            comparison["data_equal"] = df1.equals(df2)
            if not comparison["data_equal"]:
                # Check with tolerance for numerical columns
                numeric_cols = df1.select_dtypes(include=[float, int]).columns
                comparison["numeric_data_close"] = True
                for col in numeric_cols:
                    if col in df2.columns:
                        if not pd.api.types.is_numeric_dtype(df2[col]):
                            comparison["numeric_data_close"] = False
                            break
                        diff = abs(df1[col] - df2[col]).max()
                        if diff > tolerance:
                            comparison["numeric_data_close"] = False
                            break
        except Exception as e:
            comparison["data_equal"] = False
            comparison["comparison_error"] = str(e)

    return comparison


def validate_postprocessing_stats(stats: Dict[str, Any]) -> List[str]:
    """
    Validate postprocessing statistics structure and return any issues found.

    Args:
        stats: Postprocessing statistics dictionary

    Returns:
        List of validation issues (empty if all good)
    """
    issues = []

    expected_keys = {
        "columns_renamed": (int, float),
        "derived_columns_added": (int, float),
        "calculations_applied": bool,
        "faulty_rows_filtered": (int, float)
    }

    for key, expected_type in expected_keys.items():
        if key in stats:
            if not isinstance(stats[key], expected_type):
                issues.append(f"'{key}' should be {expected_type}, got {type(stats[key])}")

            # Additional validation for numeric fields
            if isinstance(expected_type, tuple) and (int, float) == expected_type:
                if isinstance(stats[key], (int, float)) and stats[key] < 0:
                    issues.append(f"'{key}' should be non-negative, got {stats[key]}")

    return issues


class TestDataGenerator:
    """Helper class for generating test data with various characteristics."""

    @staticmethod
    def generate_csv_with_issues(issue_type: str = "missing_columns") -> str:
        """Generate CSV content with specific issues for testing robustness."""
        if issue_type == "missing_columns":
            return "time,latitude,longitude\n1609459200000,59.3293,18.0686\n1609459260000,59.3294\n"

        elif issue_type == "inconsistent_types":
            return "time,value\n1609459200000,123\n1609459260000,abc\n1609459320000,456\n"

        elif issue_type == "empty_rows":
            return "time,value\n1609459200000,123\n,\n1609459320000,456\n"

        elif issue_type == "unicode_characters":
            return "name,value\nTëst,123\nÄnother Tëst,456\n"

        elif issue_type == "very_long_lines":
            long_value = "x" * 10000
            return f"name,value\ntest,{long_value}\nnormal,123\n"

        else:
            # Default: minimal valid CSV
            return "col1,col2\nval1,val2\n"

    @staticmethod
    def generate_large_csv(rows: int = 10000) -> str:
        """Generate a large CSV for performance testing."""
        lines = ["time,latitude,longitude,altitude"]
        base_time = 1609459200000

        for i in range(rows):
            time_val = base_time + (i * 1000)
            lat = 59.3293 + (i * 0.0001)
            lon = 18.0686 + (i * 0.0001)
            alt = 10 + (i % 100)
            lines.append(f"{time_val},{lat},{lon},{alt}")

        return "\n".join(lines)


def cleanup_temp_files(temp_paths: List[Path]) -> None:
    """
    Clean up temporary files and directories created during testing.

    Args:
        temp_paths: List of paths to clean up
    """
    for path in temp_paths:
        try:
            if path.exists():
                if path.is_file():
                    path.unlink()
                elif path.is_dir():
                    import shutil
                    shutil.rmtree(path)
        except Exception as e:
            print(f"Warning: Could not clean up {path}: {e}")