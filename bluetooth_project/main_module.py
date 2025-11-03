"""
Main Module (Multi-Device)
==========================
Coordinates Bluetooth scanning for multiple BLE devices (e.g., phone and
headphones), proximity evaluation with hysteresis, and system lock/unlock.

Design goals:
- Async, non-blocking scanning using existing bluetooth_scanner_module
- Supports multiple target devices with per-device thresholds
- Structured logging via logger_module
- System control via system_control_module
- Clear, PEP8-compliant code under 500 lines
"""

import asyncio
import sys
import os
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import config_module as config
import logger_module as logger_module
import system_control_module as system_control_module
import bluetooth_scanner_module as bt_module


@dataclass
class TargetDevice:
    """Represents a target BLE device configuration and runtime state."""

    name: str
    mac: str
    lock_threshold: int
    unlock_threshold: int
    scanner: Optional[bt_module.BluetoothScanner] = None
    consecutive_failures: int = 0


class ProximityLockController:
    """Main controller coordinating multi-device scanning and lock/unlock."""

    def __init__(self):
        # Validate configuration if available
        validator = getattr(config, "validate_config", None)
        if callable(validator):
            validator()

        self.logger = logger_module.get_logger()
        self.system_controller = system_control_module.get_controller()

        self.devices: List[TargetDevice] = self._load_devices_from_config()
        self._init_scanners()

        self.is_locked: bool = False
        self.scan_count: int = 0
        self.start_time: float = time.time()

        self._print_startup_banner()

    # ------------------------------------------------------------------
    def _load_devices_from_config(self) -> List[TargetDevice]:
        """Create device descriptors from config settings.

        Always includes the phone. Adds headphones if HEADPHONE_MAC exists.
        """
        devices: List[TargetDevice] = []

        devices.append(
            TargetDevice(
                name="phone",
                mac=config.PHONE_MAC,
                lock_threshold=config.LOCK_THRESHOLD,
                unlock_threshold=config.UNLOCK_THRESHOLD,
            )
        )

        headphone_mac: Optional[str] = getattr(config, "HEADPHONE_MAC", None)
        if headphone_mac:
            devices.append(
                TargetDevice(
                    name="headphones",
                    mac=headphone_mac,
                    lock_threshold=config.LOCK_THRESHOLD,
                    unlock_threshold=config.UNLOCK_THRESHOLD,
                )
            )

        return devices

    # ------------------------------------------------------------------
    def _init_scanners(self) -> None:
        """Initialize per-device scanners using the existing module."""
        for device in self.devices:
            try:
                device.scanner = bt_module.BluetoothScanner(
                    target_mac=device.mac, scan_timeout=getattr(
                        config, "SCAN_TIMEOUT", 3.0)
                )
            except Exception as e:
                self.logger.log_warning(
                    f"Scanner init failed for {device.name}: {e}")
                device.scanner = None

    # ------------------------------------------------------------------
    def _print_startup_banner(self) -> None:
        print("\n" + "=" * 70)
        print(" BLUETOOTH PROXIMITY LOCK SYSTEM (Multi-Device)")
        print("=" * 70)
        for d in self.devices:
            print(
                f"Target: {d.name} | MAC: {d.mac} | L:{d.lock_threshold} / U:{d.unlock_threshold}")
        print(
            f"Scan Interval: {getattr(config, 'SCAN_INTERVAL', 5.0)} seconds")
        try:
            print(f"Log File: {self.logger.get_log_path()}")
        except Exception:
            pass
        print("=" * 70)
        print("\nPress Ctrl+C to stop the system.\n")

    # ------------------------------------------------------------------
    async def _scan_device(self, device: TargetDevice) -> Optional[int]:
        """Scan a single device asynchronously, returning RSSI or None."""
        try:
            if device.scanner is None:
                return None

            get_rssi = getattr(device.scanner, "get_rssi", None)
            if get_rssi is None:
                return None

            if asyncio.iscoroutinefunction(get_rssi):
                return await get_rssi()

            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(None, get_rssi)

        except Exception as e:
            self.logger.log_warning(f"RSSI read failed for {device.name}: {e}")
            return None

    # ------------------------------------------------------------------
    async def _scan_all(self) -> Dict[str, Optional[int]]:
        """Scan all devices concurrently and return per-device RSSI results."""
        tasks = [self._scan_device(d) for d in self.devices]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        rssi_map: Dict[str, Optional[int]] = {}
        for device, result in zip(self.devices, results):
            if isinstance(result, Exception):
                self.logger.log_warning(
                    f"Scan exception for {device.name}: {result!r}")
                rssi_map[device.name] = None
            else:
                rssi_map[device.name] = result
        return rssi_map

    # ------------------------------------------------------------------
    def _evaluate_lock(self, rssi_map: Dict[str, Optional[int]]) -> bool:
        """Return True to lock if any device is out of range per rules."""
        should_lock = False
        for device in self.devices:
            rssi = rssi_map.get(device.name)

            if rssi is None:
                device.consecutive_failures += 1
                if device.consecutive_failures >= getattr(
                    config, "CONSECUTIVE_FAIL_THRESHOLD", 2
                ):
                    self.logger.log_phone_not_detected()
                    should_lock = True
                continue

            device.consecutive_failures = 0
            self.logger.log_phone_detected(rssi)
            if rssi < device.lock_threshold:
                should_lock = True

        return should_lock

    # ------------------------------------------------------------------
    def _evaluate_unlock(self, rssi_map: Dict[str, Optional[int]]) -> bool:
        """Return True to unlock if any device is in range per rules."""
        for device in self.devices:
            rssi = rssi_map.get(device.name)
            if rssi is None:
                continue
            if rssi > device.unlock_threshold:
                self.logger.log_phone_detected(rssi)
                return True
        return False

    # ------------------------------------------------------------------
    async def monitor_loop(self) -> None:
        """Main monitoring loop: scan, decide, and act every interval."""
        try:
            while True:
                self.scan_count += 1
                rssi_map = await self._scan_all()

                # Log per-device RSSI
                for device in self.devices:
                    rssi = rssi_map.get(device.name)
                    # informational logs only when verbose, avoid blocking
                    if getattr(config, "VERBOSE_LOGGING", True):
                        msg = (
                            f"{device.name} RSSI: {rssi if rssi is not None else 'N/A'}"
                        )
                        self.logger.log_info(msg)

                if not self.is_locked:
                    if self._evaluate_lock(rssi_map):
                        ok = self.system_controller.lock_system()
                        if ok:
                            self.is_locked = True
                            # Use phone RSSI if available for context
                            self.logger.log_system_locked(
                                rssi_map.get("phone"))
                else:
                    if self._evaluate_unlock(rssi_map):
                        ok = self.system_controller.wake_system()
                        if ok:
                            self.is_locked = False
                            self.logger.log_system_unlocked(
                                rssi_map.get("phone"))

                await asyncio.sleep(getattr(config, "SCAN_INTERVAL", 5.0))

        except asyncio.CancelledError:
            pass
        except KeyboardInterrupt:
            pass
        except Exception as e:
            # Log full traceback to aid diagnosis
            import traceback as _tb

            tb_str = "".join(_tb.format_exception(None, e, e.__traceback__))
            self.logger.log_error(f"Fatal error: {tb_str}")
            raise

    # ------------------------------------------------------------------
    def shutdown(self) -> None:
        """Print summary and log shutdown."""
        uptime = int(time.time() - self.start_time)
        hrs, rem = divmod(uptime, 3600)
        mins, secs = divmod(rem, 60)
        stats = getattr(self.system_controller, "get_statistics", lambda: {})()

        self.logger.log_system_stop()
        print("\n=== SHUTTING DOWN ===")
        print(f"Uptime: {hrs}h {mins}m {secs}s")
        print(f"Total scans: {self.scan_count}")
        print(
            f"Locks: {stats.get('total_locks', 'N/A')} | Unlocks: {stats.get('total_unlocks', 'N/A')}"
        )
        print("[EXIT] System stopped gracefully.\n")


def run() -> None:
    # Ensure Bleak works reliably on Windows
    if sys.platform == "win32":
        try:
            asyncio.set_event_loop_policy(
                asyncio.WindowsSelectorEventLoopPolicy())
        except Exception:
            pass

    controller = ProximityLockController()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(controller.monitor_loop())
    except KeyboardInterrupt:
        controller.shutdown()
    except Exception as e:
        # Print traceback to console for visibility when double-clicked
        import traceback as _tb

        tb_str = "".join(_tb.format_exception(None, e, e.__traceback__))
        print("\n[UNHANDLED EXCEPTION]\n" + tb_str)
        controller.logger.log_error(f"Unhandled exception: {e}")
        controller.shutdown()
        # Pause on exit unless disabled
        if not os.environ.get("NO_PAUSE_ON_EXIT"):
            try:
                input("\nPress Enter to exit...")
            except Exception:
                pass
    finally:
        loop.close()
        # If the loop ended without KeyboardInterrupt, keep console open briefly
        if not os.environ.get("NO_PAUSE_ON_EXIT"):
            try:
                print("\n[INFO] Exiting. Close this window or press Enter.")
                input()
            except Exception:
                pass


if __name__ == "__main__":
    run()
