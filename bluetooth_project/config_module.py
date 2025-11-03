"""
Configuration Module for Bluetooth Proximity Lock System
==========================================================
Contains all configurable parameters for proximity detection,
Bluetooth scanning, and system behavior.

Author: Professional Development Team
Version: 1.0.0
License: MIT
"""

from pathlib import Path

# ============================================================================
# DEVICE CONFIGURATION
# ============================================================================
# Your phone’s Bluetooth MAC address
# Find this in your phone’s Bluetooth settings or Windows Device Manager
# Format Example: 28:D2:5A:A1:29:6E
PHONE_MAC: str = "fc:02:96:97:30:00"

# Optional: Bluetooth MAC address of your headphones (leave empty to disable)
HEADPHONE_MAC: str = ""

# ============================================================================
# PROXIMITY THRESHOLDS (RSSI VALUES)
# ============================================================================
# RSSI (Received Signal Strength Indicator)
#   - Values typically range from -30 (very close) to -100 (very far)
#   - Adjust thresholds to tune proximity sensitivity
LOCK_THRESHOLD: int = -80       # Lock system when RSSI drops below this
UNLOCK_THRESHOLD: int = -70     # Unlock when RSSI rises above this
# Note: UNLOCK_THRESHOLD must be greater than LOCK_THRESHOLD to avoid flapping

# ============================================================================
# TIMING CONFIGURATION
# ============================================================================
SCAN_INTERVAL: float = 5.0      # Seconds between scans
SCAN_TIMEOUT: float = 3.0       # Seconds to wait for each BLE discovery

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
LOG_DIR: Path = Path(__file__).parent / "logs"
LOG_FILE: Path = LOG_DIR / "activity_log.txt"
VERBOSE_LOGGING: bool = True    # Enables console output for debugging

# ============================================================================
# ADVANCED SETTINGS
# ============================================================================
CONSECUTIVE_FAIL_THRESHOLD: int = 2  # Failures before locking system
SYSTEM_COMMAND_RETRIES: int = 3      # Retry count for system commands

# ============================================================================
# VALIDATION FUNCTION
# ============================================================================


def validate_config() -> None:
    """
    Validate configuration integrity before starting the system.
    Ensures proper MAC format and logical threshold order.
    """
    import re

    # Validate MAC format for required phone MAC
    if not re.match(r"^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$", PHONE_MAC):
        raise ValueError(f"Invalid PHONE_MAC format: {PHONE_MAC}")

    # Validate optional headphone MAC if provided
    if HEADPHONE_MAC:
        if not re.match(r"^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$", HEADPHONE_MAC):
            raise ValueError(f"Invalid HEADPHONE_MAC format: {HEADPHONE_MAC}")

    # Validate thresholds
    if LOCK_THRESHOLD >= UNLOCK_THRESHOLD:
        raise ValueError(
            f"LOCK_THRESHOLD ({LOCK_THRESHOLD}) must be less than UNLOCK_THRESHOLD ({UNLOCK_THRESHOLD})"
        )

    # Create log folder if it doesn’t exist
    LOG_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================================
# EXECUTION CHECK (Optional)
# ============================================================================
if __name__ == "__main__":
    print("Validating configuration...")
    validate_config()
    print("Configuration OK ✅")
