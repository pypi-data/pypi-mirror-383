"""
Post-Processing Integration Module

This module integrates the postprocessing pipeline with the metadata extractor.
It handles column renaming, power calculations, and data validation.
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Union
import pandas as pd
import warnings

try:
    # Try relative import first (when used as package)
    from .postprocessing.naming_functions import (
        COLUMNS_DICT,
        rename_columns_and_add_derived,
        validate_renamed_columns
    )
    from .postprocessing.calculation_functions import XERDataCalculator
    from .validation_config import VALIDATION_CONFIG
    POSTPROCESSING_AVAILABLE = True
except ImportError:
    try:
        # Fall back to absolute import (when run directly)
        from postprocessing.naming_functions import (
            COLUMNS_DICT,
            rename_columns_and_add_derived,
            validate_renamed_columns
        )
        from postprocessing.calculation_functions import XERDataCalculator
        from validation_config import VALIDATION_CONFIG
        POSTPROCESSING_AVAILABLE = True
    except ImportError as e:
        warnings.warn(f"Postprocessing modules not available: {e}")
        POSTPROCESSING_AVAILABLE = False


class PostProcessingIntegration:
    """Integrates postprocessing pipeline with metadata extraction."""
    
    def __init__(self, reference_data_dir: str = None):
        """
        Initialize the postprocessing integration.
        
        Args:
            reference_data_dir: Path to directory containing reference RPM/power CSV files
        """
        if reference_data_dir is None:
            # Use package-relative path
            self.reference_data_dir = Path(__file__).parent / "reference_data"
        else:
            self.reference_data_dir = Path(reference_data_dir)
        self.calculator = None
        self.post_processing_stats = {
            "columns_renamed": 0,
            "derived_columns_added": 0,
            "faulty_rows_filtered": 0,
            "calculations_applied": False,
            "reference_data_loaded": False,
            "validation_passed": False,
            "warnings": [],
            "errors": []
        }
        
        if POSTPROCESSING_AVAILABLE:
            self.calculator = XERDataCalculator(str(self.reference_data_dir))
    
    def process_dataframe(self, df: pd.DataFrame, verbose: bool = False) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Process a DataFrame through the postprocessing pipeline.

        Args:
            df: Input DataFrame
            verbose: Whether to print detailed information

        Returns:
            Tuple of (processed DataFrame, processing statistics)
        """
        # Reset stats for each new processing run to avoid accumulating warnings across files
        self.post_processing_stats = {
            "columns_renamed": 0,
            "derived_columns_added": 0,
            "faulty_rows_filtered": 0,
            "calculations_applied": False,
            "reference_data_loaded": False,
            "validation_passed": False,
            "warnings": [],
            "errors": []
        }

        if not POSTPROCESSING_AVAILABLE:
            self.post_processing_stats["warnings"].append("Postprocessing modules not available")
            return df, self.post_processing_stats
        
        try:
            if verbose:
                print("🔄 Starting postprocessing pipeline...")
                print(f"   Input: {len(df)} rows, {len(df.columns)} columns")
            
            # Step 1: Filter out faulty time=0 rows
            if verbose:
                print("   🧹 Filtering out faulty time=0 rows...")
            
            df, filtered_count = self._filter_faulty_time_rows(df, verbose)
            self.post_processing_stats["faulty_rows_filtered"] = int(filtered_count)
            if filtered_count > 0:
                self.post_processing_stats["warnings"].append(f"Filtered out {filtered_count} rows with faulty time values (time=0, NaN, or chronologically out-of-order)")
            
            # Step 2: Column renaming and derived columns
            if verbose:
                print("   📝 Applying column renaming...")
            
            df, renamed_count = rename_columns_and_add_derived(df, COLUMNS_DICT)
            self.post_processing_stats["columns_renamed"] = renamed_count
            
            # Count derived columns added
            derived_columns = ["isGeneratorRunning", "droneInFlight"]
            derived_count = sum(1 for col in derived_columns if col in df.columns)
            self.post_processing_stats["derived_columns_added"] = derived_count
            
            if verbose:
                print(f"   ✓ Renamed {renamed_count} columns")
                print(f"   ✓ Added {derived_count} derived columns")
            
            # Step 3: Validate columns for calculations
            validation = validate_renamed_columns(df)
            self.post_processing_stats["validation_passed"] = all(validation.values())
            
            if verbose:
                print("   🔍 Column validation:")
                for key, available in validation.items():
                    status = "✓" if available else "✗"
                    print(f"      {status} {key}")
            
            # Step 4: Apply power calculations if possible
            can_calculate_pmu = validation.get('uc_voltage_available', False) and validation.get('pdu_current_available', False)
            can_calculate_engine = validation.get('rpm_available', False) and validation.get('throttle_available', False)
            
            if can_calculate_pmu or can_calculate_engine:
                if verbose:
                    print("   🧮 Applying power calculations...")
                
                # Load reference data if not already loaded
                if not self.post_processing_stats["reference_data_loaded"]:
                    self.post_processing_stats["reference_data_loaded"] = self.calculator.load_reference_data()
                    if verbose:
                        status = "✓" if self.post_processing_stats["reference_data_loaded"] else "✗"
                        print(f"      {status} Reference data loaded")
                
                # Apply calculations
                df = self.calculator.process_calculations(df)
                self.post_processing_stats["calculations_applied"] = True
                
                if verbose:
                    print("   ✓ Power calculations applied")
            else:
                if verbose:
                    print("   ⚠️  Skipping calculations (missing required columns)")
                self.post_processing_stats["warnings"].append("Missing required columns for power calculations")
            
            if verbose:
                print(f"   📊 Output: {len(df)} rows, {len(df.columns)} columns")
            
            return df, self.post_processing_stats
            
        except Exception as e:
            error_msg = f"Postprocessing error: {str(e)}"
            self.post_processing_stats["errors"].append(error_msg)
            if verbose:
                print(f"   ❌ {error_msg}")
            return df, self.post_processing_stats
    
    def _filter_faulty_time_rows(self, df: pd.DataFrame, verbose: bool = False) -> Tuple[pd.DataFrame, int]:
        """
        Filter out rows with faulty time values using three simple checks:
        1. Remove rows where time = 0
        2. Remove rows where time is NaN or empty
        3. Check if first 5 time values are ordered, if not remove and start from 6th

        Args:
            df: Input DataFrame
            verbose: Whether to print detailed information

        Returns:
            Tuple of (filtered DataFrame, number of rows removed)
        """
        original_count = len(df)
        
        # Find time columns
        time_columns = [col for col in df.columns if col.lower() in ['time', 'timestamp']]
        
        if not time_columns:
            if verbose:
                print("      No time columns found - skipping time filtering")
            return df, 0
        
        time_col = time_columns[0]  # Use first time column
        df_filtered = df.copy()
        
        # Check 1: Remove rows where time = 0
        zero_mask = df_filtered[time_col] == 0
        zero_count = int(zero_mask.sum())
        if zero_count > 0:
            df_filtered = df_filtered[~zero_mask]
            if verbose:
                print(f"      Removed {zero_count} rows with time=0")
        
        # Check 2: Remove rows where time is NaN or empty
        nan_mask = df_filtered[time_col].isna()
        nan_count = int(nan_mask.sum())
        if nan_count > 0:
            df_filtered = df_filtered[~nan_mask]
            if verbose:
                print(f"      Removed {nan_count} rows with NaN/empty time")
        
        # Check 3: Check if first 5 time values are ordered and valid Unix timestamps
        ordering_removed = 0
        while len(df_filtered) >= VALIDATION_CONFIG.min_chronological_check_rows:
            first_5_times = df_filtered[time_col].iloc[:5]
            
            # Check if all timestamps are in valid Unix range (year 2000+)
            valid_range = (first_5_times >= VALIDATION_CONFIG.min_unix_timestamp) & (first_5_times <= VALIDATION_CONFIG.max_unix_timestamp)
            all_valid = valid_range.all()
            
            # Check if ordered
            is_ordered = first_5_times.is_monotonic_increasing
            
            if is_ordered and all_valid:
                break  # First 5 are ordered and valid, we're good
            else:
                # Remove first row and try again
                df_filtered = df_filtered.iloc[1:]
                ordering_removed += 1
                if verbose:
                    if not all_valid:
                        invalid_value = first_5_times[~valid_range].iloc[0] if (~valid_range).any() else "unknown"
                        print(f"      Removed row with invalid timestamp: {invalid_value}")
                    else:
                        print(f"      Removed out-of-order row, trying again...")
                
                # Safety check - don't remove more than 10 rows
                if ordering_removed >= VALIDATION_CONFIG.max_faulty_rows_remove:
                    if verbose:
                        print(f"      Warning: Stopped after removing {ordering_removed} out-of-order rows")
                    break
        
        if ordering_removed > 0 and verbose:
            print(f"      Removed {ordering_removed} out-of-order rows from beginning")
        
        total_filtered = zero_count + nan_count + ordering_removed
        
        if verbose:
            if total_filtered > 0:
                print(f"      ✓ Filtered out {total_filtered} rows total")
                print(f"      Remaining: {len(df_filtered)} rows")
            else:
                print("      ✓ No faulty time rows found")

        # Ensure we return Python int, not numpy int64 for JSON serialization
        return df_filtered, int(total_filtered)

    def get_required_columns(self) -> List[str]:
        """Get list of required columns for postprocessing."""
        if not POSTPROCESSING_AVAILABLE:
            return []
        
        # Return columns that are needed for calculations
        return [
            "UC_voltage",  # For PMU power calculation
            "PDU_current",  # For PMU power calculation
            "generator_rpm",  # For engine power calculation
            "ECU_throttle",  # For engine power calculation
            "time"  # For timing calculations
        ]
    
    def get_available_columns(self) -> List[str]:
        """Get list of all available columns after postprocessing."""
        if not POSTPROCESSING_AVAILABLE:
            return []
        
        # Return all possible columns that could be available after postprocessing
        base_columns = list(COLUMNS_DICT.values())
        derived_columns = ["isGeneratorRunning", "droneInFlight"]
        calculated_columns = ["PMU_power", "Engine_power", "System_efficiency"]
        
        return base_columns + derived_columns + calculated_columns
    
    def validate_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate data quality after postprocessing.
        
        Args:
            df: Processed DataFrame
            
        Returns:
            Dictionary with validation results
        """
        validation_results = {
            "is_valid": True,
            "message": "Data quality validation passed",
            "warnings": [],
            "errors": []
        }
        
        # Check minimum data points
        if len(df) < VALIDATION_CONFIG.min_data_points:
            validation_results["warnings"].append(f"Less than {VALIDATION_CONFIG.min_data_points} data points")
        
        # Check for required columns
        required_columns = self.get_required_columns()
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            validation_results["warnings"].append(f"Missing columns: {missing_columns}")
        
        # Validate RPM values if available
        rpm_columns = [col for col in df.columns if "rpm" in col.lower()]
        for rpm_col in rpm_columns:
            if rpm_col in df.columns:
                rpm_values = pd.to_numeric(df[rpm_col], errors='coerce')
                if not rpm_values.isna().all():
                    min_rpm = rpm_values.min()
                    max_rpm = rpm_values.max()
                    if min_rpm < VALIDATION_CONFIG.rpm_min or max_rpm > VALIDATION_CONFIG.rpm_max:
                        validation_results["warnings"].append(f"RPM values out of expected range: {min_rpm} - {max_rpm}")
        
        # Validate voltage values if available
        voltage_columns = [col for col in df.columns if "voltage" in col.lower()]
        for voltage_col in voltage_columns:
            if voltage_col in df.columns:
                voltage_values = pd.to_numeric(df[voltage_col], errors='coerce')
                if not voltage_values.isna().all():
                    min_voltage = voltage_values.min()
                    max_voltage = voltage_values.max()
                    if min_voltage < VALIDATION_CONFIG.voltage_min or max_voltage > VALIDATION_CONFIG.voltage_max:
                        validation_results["warnings"].append(f"Voltage values out of expected range: {min_voltage} - {max_voltage}")
        
        # Validate current values if available
        current_columns = [col for col in df.columns if "current" in col.lower()]
        for current_col in current_columns:
            if current_col in df.columns:
                current_values = pd.to_numeric(df[current_col], errors='coerce')
                if not current_values.isna().all():
                    min_current = current_values.min()
                    max_current = current_values.max()
                    if min_current < VALIDATION_CONFIG.current_min or max_current > VALIDATION_CONFIG.current_max:
                        validation_results["warnings"].append(f"Current values out of expected range: {min_current} - {max_current}")
        
        # Check for sequential timestamps
        time_columns = [col for col in df.columns if col.lower() in ["time", "timestamp"]]
        for time_col in time_columns:
            if time_col in df.columns:
                try:
                    # Try to parse timestamps
                    timestamps = pd.to_datetime(df[time_col], errors='coerce')
                    if not timestamps.isna().all():
                        # Check if timestamps are sequential using pandas built-in method
                        if not timestamps.is_monotonic_increasing:
                            validation_results["warnings"].append("Timestamps are not sequential")
                except:
                    validation_results["warnings"].append(f"Could not parse timestamps in column {time_col}")
        
        if validation_results["warnings"]:
            validation_results["message"] = f"Data quality validation completed with {len(validation_results['warnings'])} warnings"
        
        return validation_results


# Global instance for easy access
postprocessing_integration = PostProcessingIntegration() 