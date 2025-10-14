"""
Validation configuration for XER Technologies Metadata Extractor.

Contains all validation thresholds and ranges used throughout the package.
Centralized configuration allows easy adjustment of validation parameters.
"""

from dataclasses import dataclass
from typing import Dict, Tuple, Optional


@dataclass
class ValidationRanges:
    """Configuration for data validation ranges and thresholds."""

    # === DATA QUALITY THRESHOLDS ===
    min_data_points: int = 100
    max_faulty_rows_remove: int = 10
    min_chronological_check_rows: int = 5

    # === TIMESTAMP VALIDATION ===
    # Unix timestamp range (milliseconds)
    min_unix_timestamp: int = 946684800000   # Jan 1, 2000
    max_unix_timestamp: int = int(2e12)      # ~2033

    # Timestamp range for enhanced parser
    unix_timestamp_min: int = int(1e12)      # 2001
    unix_timestamp_max: int = int(2e12)      # 2033

    # === SENSOR RANGE VALIDATION ===
    # RPM validation
    rpm_min: float = 0
    rpm_max: float = 9000

    # Voltage validation (Volts)
    voltage_min: float = -50
    voltage_max: float = 50

    # Current validation (Amps)
    current_min: float = -30
    current_max: float = 100

    # === POWER SYSTEM VALIDATION ===
    # PMU Power validation (Watts)
    pmu_power_abs_max: float = 5000         # Used in validation_analysis.py
    pmu_power_warning_abs_max: float = 1000  # Used in validation_analysis.py

    # Engine Power validation (Watts)
    engine_power_min: float = 100           # Typical generator minimum
    engine_power_max: float = 5000          # Typical generator maximum
    engine_power_std_min: float = 10        # Minimum variation expected

    # System Efficiency validation (%)
    efficiency_min: float = 0
    efficiency_max: float = 100
    efficiency_low_threshold: float = 10    # Below this is concerning

    # === CALCULATION THRESHOLDS ===
    # Power calculation minimums
    engine_power_calc_min: float = 0.1      # Minimum for efficiency calculation
    pmu_power_calc_abs_min: float = 0.01    # Minimum absolute value for efficiency

    # === CORRELATION AND RELATIONSHIP CHECKS ===
    # Minimum correlation thresholds
    min_power_rpm_correlation: float = 0.1
    min_power_throttle_correlation: float = 0.1

    # === DATA QUALITY PERCENTAGES ===
    max_pmu_negative_percent: float = 50    # Max % of negative PMU power readings
    min_engine_unique_values: int = 10      # Minimum unique engine power values
    max_low_efficiency_percent: float = 80  # Max % of readings below efficiency_low_threshold


# Global configuration instance
VALIDATION_CONFIG = ValidationRanges()


def get_validation_ranges() -> ValidationRanges:
    """Get the current validation configuration."""
    return VALIDATION_CONFIG


def update_validation_ranges(**kwargs) -> None:
    """Update specific validation ranges at runtime."""
    global VALIDATION_CONFIG
    for key, value in kwargs.items():
        if hasattr(VALIDATION_CONFIG, key):
            setattr(VALIDATION_CONFIG, key, value)
        else:
            raise ValueError(f"Unknown validation parameter: {key}")


def get_voltage_range() -> Tuple[float, float]:
    """Get voltage validation range."""
    return VALIDATION_CONFIG.voltage_min, VALIDATION_CONFIG.voltage_max


def get_current_range() -> Tuple[float, float]:
    """Get current validation range."""
    return VALIDATION_CONFIG.current_min, VALIDATION_CONFIG.current_max


def get_rpm_range() -> Tuple[float, float]:
    """Get RPM validation range."""
    return VALIDATION_CONFIG.rpm_min, VALIDATION_CONFIG.rpm_max


def get_power_ranges() -> Dict[str, Tuple[float, float]]:
    """Get all power-related validation ranges."""
    return {
        "pmu_power_abs_max": (0, VALIDATION_CONFIG.pmu_power_abs_max),
        "engine_power": (VALIDATION_CONFIG.engine_power_min, VALIDATION_CONFIG.engine_power_max),
        "efficiency": (VALIDATION_CONFIG.efficiency_min, VALIDATION_CONFIG.efficiency_max)
    }


# === SYSTEM-SPECIFIC PRESETS ===
# These can be used to quickly reconfigure for different drone systems

def configure_for_48v_system():
    """Configure validation ranges for 48V battery systems."""
    update_validation_ranges(
        voltage_min=-60,    # Allow for some overvoltage protection
        voltage_max=60,     # 48V nominal, ~54V fully charged + margin
        current_max=150     # Higher current capability for 48V systems
    )


def configure_for_24v_system():
    """Configure validation ranges for 24V battery systems."""
    update_validation_ranges(
        voltage_min=-30,    # 24V systems
        voltage_max=30,     # ~28V fully charged + margin
        current_max=200     # Higher current for lower voltage
    )


def configure_for_high_power_system():
    """Configure validation ranges for high-power drone systems."""
    update_validation_ranges(
        engine_power_max=8000,      # Higher power generators
        pmu_power_abs_max=8000,     # Higher power handling
        rpm_max=12000               # Higher RPM capability
    )