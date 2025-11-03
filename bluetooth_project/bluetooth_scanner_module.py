"""
Bluetooth Scanner Module
=========================
Handles all Bluetooth Low Energy (BLE) scanning operations using the bleak library.
Discovers nearby devices and retrieves RSSI values for proximity detection.

Environment:
    - OS: Windows 11
    - Python: 3.11+
    - Folder: project3
    - Dependencies: bleak>=0.21.0
    - Configured for Mr. Wayne’s personal Bluetooth device (Pixel / iPhone)
      MAC: 28:D2:5A:A1:29:6E

How it works:
    1. Scans nearby BLE devices asynchronously using Bleak.
    2. Looks for the configured MAC from `config.py`.
    3. Returns the RSSI signal (distance indicator).
    4. Used by system_control.py to trigger lock/unlock actions.
"""

# ============================================================================
# IMPORTS
# ============================================================================
import asyncio
from typing import Optional
from bleak import BleakScanner
from bleak.exc import BleakError
import config_module as config

# ============================================================================
# BLUETOOTH SCANNER CLASS
# ============================================================================


class BluetoothScanner:
    """
    Manages Bluetooth scanning operations for proximity detection.

    Attributes:
        target_mac (str): MAC address of the device to monitor
        scan_timeout (float): Timeout duration for each scan
    """

    def __init__(self, target_mac: str, scan_timeout: float = config.SCAN_TIMEOUT):
        """
        Initialize the Bluetooth scanner.

        Args:
            target_mac: Bluetooth MAC address to monitor
            scan_timeout: Maximum time to wait during each scan
        """
        self.target_mac = target_mac.lower()
        self.scan_timeout = scan_timeout
        self._last_rssi = None

    # ------------------------------------------------------------------------
    # MAIN SCAN METHOD
    # ------------------------------------------------------------------------
    async def get_rssi(self) -> Optional[int]:
        """
        Scan for nearby Bluetooth devices and retrieve RSSI of target device.

        Returns:
            int: RSSI value if device found (typically -30 to -100)
            None: If device not found or scan failed

        Raises:
            BleakError: If Bluetooth adapter is unavailable
        """
        try:
            # Discover nearby BLE devices
            devices = await BleakScanner.discover(timeout=self.scan_timeout)

            for device in devices:
                # Match by MAC address (case-insensitive)
                if device.address.lower() == self.target_mac:
                    self._last_rssi = device.rssi
                    if config.VERBOSE_LOGGING:
                        print(
                            f"[SCAN] Device found: {device.name or 'Unknown'} | RSSI: {device.rssi}")
                    return device.rssi

            # If not found
            if config.VERBOSE_LOGGING:
                print(f"[SCAN] Target device {self.target_mac} not detected")
            return None

        except BleakError as e:
            print(f"[ERROR] Bluetooth adapter error: {e}")
            raise
        except Exception as e:
            print(f"[ERROR] Unexpected scan error: {e}")
            return None

    # ------------------------------------------------------------------------
    # PROPERTY ACCESSORS
    # ------------------------------------------------------------------------
    @property
    def last_rssi(self) -> Optional[int]:
        """Returns the last successfully retrieved RSSI value."""
        return self._last_rssi

    def is_device_nearby(self, rssi: Optional[int], threshold: int) -> bool:
        """
        Check if device is nearby based on RSSI threshold.

        Args:
            rssi: Current RSSI value (None if not detected)
            threshold: RSSI threshold (e.g., -70)

        Returns:
            bool: True if RSSI > threshold, False otherwise
        """
        if rssi is None:
            return False
        return rssi > threshold


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
async def scan_for_device(mac_address: str) -> Optional[int]:
    """
    Performs a single scan for the given MAC address.

    Args:
        mac_address: Bluetooth MAC address to search for

    Returns:
        RSSI value if found, None otherwise
    """
    scanner = BluetoothScanner(mac_address)
    return await scanner.get_rssi()


async def list_nearby_devices():
    """
    Diagnostic tool to list all nearby Bluetooth devices.
    Helps in identifying MAC addresses.
    """
    print("\n[DIAGNOSTIC] Scanning for nearby Bluetooth devices...")
    print("=" * 60)

    try:
        devices = await BleakScanner.discover(timeout=5.0)

        if not devices:
            print("No devices found. Ensure Bluetooth is enabled.")
            return

        for device in devices:
            print(f"Name: {device.name or 'Unknown'}")
            print(f"Address: {device.address}")
            print(f"RSSI: {device.rssi} dBm")
            print("-" * 60)

    except Exception as e:
        print(f"[ERROR] Diagnostic scan failed: {e}")


# ============================================================================
# MAIN ENTRYPOINT (RUN DIRECTLY FOR TEST)
# ============================================================================
if __name__ == "__main__":
    print("Bluetooth Scanner Module - Diagnostic Mode")
    print("Target MAC:", config.PHONE_MAC)
    asyncio.run(list_nearby_devices())
