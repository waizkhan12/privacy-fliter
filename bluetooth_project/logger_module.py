"""
Event Logger Module
===================
Handles detailed logging of system events, RSSI readings, and state changes.
Provides file-based and console logging with timestamps.

Author: Professional Development Team
Version: 1.0.2
"""

import atexit
from datetime import datetime
from typing import Optional
from enum import Enum
from pathlib import Path
import config_module as config


class EventType(Enum):
    """Enumeration of loggable event types."""
    SYSTEM_START = "SYSTEM_START"
    SYSTEM_STOP = "SYSTEM_STOP"
    PHONE_DETECTED = "PHONE_DETECTED"
    PHONE_NOT_DETECTED = "PHONE_NOT_DETECTED"
    SYSTEM_LOCKED = "SYSTEM_LOCKED"
    SYSTEM_UNLOCKED = "SYSTEM_UNLOCKED"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


class EventLogger:
    """
    Manages event logging with timestamps and RSSI tracking.
    Provides consistent log formatting and optional console output.
    """

    def __init__(self, log_file: Path = config.LOG_FILE, verbose: bool = config.VERBOSE_LOGGING):
        self.log_file = Path(log_file)
        self.verbose = verbose
        self._ensure_log_directory()
        self._log_session_start()
        # Ensure system stop is logged on exit
        atexit.register(self.log_system_stop)

    # =========================================================================
    # INTERNAL METHODS
    # =========================================================================

    def _ensure_log_directory(self):
        """Ensure log directory and file exist."""
        try:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            if not self.log_file.exists():
                self.log_file.touch()
        except Exception as e:
            print(f"[WARNING] Could not initialize log file: {e}")

    def _format_timestamp(self) -> str:
        """Generate formatted timestamp."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _format_log_entry(self, event_type: EventType, message: str, rssi: Optional[int]) -> str:
        """Create a structured log entry."""
        timestamp = self._format_timestamp()
        rssi_str = f"RSSI: {rssi} dBm" if rssi is not None else "RSSI: N/A"
        return f"[{timestamp}] [{event_type.value}] {message} | {rssi_str}"

    def _write_log_entry(self, event_type: EventType, message: str, rssi: Optional[int]):
        """Write log entry to file and optionally to console."""
        entry = self._format_log_entry(event_type, message, rssi)
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(entry + "\n")
        except Exception as e:
            print(f"[ERROR] Failed to write log entry: {e}")

        if self.verbose:
            print(self._colorize_console(entry, event_type))

    def _colorize_console(self, text: str, event_type: EventType) -> str:
        """Add color to console output for clarity."""
        colors = {
            EventType.ERROR: "\033[91m",    # Red
            EventType.WARNING: "\033[93m",  # Yellow
            EventType.INFO: "\033[96m",     # Cyan
            EventType.SYSTEM_LOCKED: "\033[95m",  # Magenta
            EventType.SYSTEM_UNLOCKED: "\033[92m",  # Green
        }
        reset = "\033[0m"
        color = colors.get(event_type, "\033[97m")
        return f"{color}{text}{reset}"

    # =========================================================================
    # PUBLIC LOGGING METHODS
    # =========================================================================

    def _log_session_start(self):
        self._write_log_entry(EventType.SYSTEM_START,
                              "Bluetooth Proximity Lock system started", None)

    def log_system_stop(self):
        self._write_log_entry(EventType.SYSTEM_STOP,
                              "Bluetooth Proximity Lock system stopped", None)

    def log_phone_detected(self, rssi: int):
        self._write_log_entry(EventType.PHONE_DETECTED,
                              "Target device detected in range", rssi)

    def log_phone_not_detected(self):
        self._write_log_entry(EventType.PHONE_NOT_DETECTED,
                              "Target device not detected", None)

    def log_system_locked(self, rssi: Optional[int] = None):
        self._write_log_entry(EventType.SYSTEM_LOCKED,
                              "System locked (device out of range)", rssi)

    def log_system_unlocked(self, rssi: Optional[int] = None):
        self._write_log_entry(EventType.SYSTEM_UNLOCKED,
                              "System unlocked (device nearby)", rssi)

    def log_error(self, message: str, rssi: Optional[int] = None):
        self._write_log_entry(EventType.ERROR, message, rssi)

    def log_warning(self, message: str, rssi: Optional[int] = None):
        self._write_log_entry(EventType.WARNING, message, rssi)

    def log_info(self, message: str, rssi: Optional[int] = None):
        self._write_log_entry(EventType.INFO, message, rssi)

    def get_log_path(self) -> Path:
        """Return absolute log file path."""
        return self.log_file


# ============================================================================
# GLOBAL LOGGER INSTANCE
# ============================================================================
_logger: Optional[EventLogger] = None


def get_logger() -> EventLogger:
    """Return singleton logger instance."""
    global _logger
    if _logger is None:
        _logger = EventLogger()
    return _logger


def log_event(event_type: EventType, message: str, rssi: Optional[int] = None):
    """Convenience wrapper for logging events directly."""
    logger = get_logger()
    logger._write_log_entry(event_type, message, rssi)


# ============================================================================
# TEST MODE
# ============================================================================
if __name__ == "__main__":
    print("Event Logger Module - Diagnostic Test")
    logger = EventLogger(config.LOG_FILE)
    logger.log_info("Diagnostic test started")
    logger.log_phone_detected(-65)
    logger.log_system_locked(-85)
    logger.log_warning("Low RSSI detected")
    logger.log_error("Bluetooth scan failure")
    logger.log_system_unlocked(-60)
    print(f"\n✅ Log file located at: {logger.get_log_path()}")

    # --- FIXED: Keep console open until user confirms exit ---
    input("\nPress Enter to stop logging and exit...")
    logger.log_system_stop()
