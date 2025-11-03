"""
Main Controller Module
======================
Coordinates Bluetooth scanning, proximity detection, and system locking/unlocking.

Author: Professional Development Team
Version: 1.0.3 (Fixed Imports & Runtime + Robust RSSI Handling)
"""

import asyncio
import time
import sys
import traceback
import inspect
from typing import Optional

# Correct imports based on your filenames
import config_module as config
import logger_module as logger_module
import system_control_module as system_control_module
import bluetooth_scanner_module as bt_module


class ProximityLockController:
    """Main controller coordinating scanning + locking with hysteresis."""

    def __init__(self):
        # Validate configuration
        validator = getattr(config, "validate_config", None)
        if callable(validator):
            try:
                validator()
            except Exception as e:
                print(f"[CONFIG ERROR] {e}")
                sys.exit(1)

        # Initialize components
        self.logger = logger_module.get_logger()
        self.system_controller = system_control_module.get_controller()
        self.scanner = None

        # Attempt to initialize Bluetooth scanner
        if hasattr(bt_module, "BluetoothScanner"):
            try:
                self.scanner = bt_module.BluetoothScanner(
                    target_mac=config.PHONE_MAC,
                    scan_timeout=getattr(config, "SCAN_TIMEOUT", 3.0)
                )
            except Exception as e:
                self.logger.log_warning(f"BluetoothScanner init failed: {e}")

        # State variables
        self.is_locked = False
        self.consecutive_failures = 0
        self.scan_count = 0
        self.start_time = time.time()

        # Banner
        self._print_startup_banner()

    # -------------------------------------------------------------------------
    def _print_startup_banner(self):
        print("\n" + "=" * 70)
        print(" BLUETOOTH PROXIMITY LOCK SYSTEM")
        print("=" * 70)
        print(f"Target Device: {config.PHONE_MAC}")
        print(f"Lock Threshold: {config.LOCK_THRESHOLD} dBm")
        print(f"Unlock Threshold: {config.UNLOCK_THRESHOLD} dBm")
        print(f"Scan Interval: {config.SCAN_INTERVAL} seconds")
        try:
            print(f"Log File: {self.logger.get_log_path()}")
        except Exception:
            pass
        print("=" * 70)
        print("\nPress Ctrl+C to stop the system.\n")

    # -------------------------------------------------------------------------
    async def _get_rssi(self) -> Optional[int]:
        """Attempt to retrieve RSSI using available APIs."""
        self.scan_count += 1

        try:
            # 1) Try instance-level methods
            if self.scanner is not None:
                for name in ("get_rssi", "get_device_rssi", "scan_once"):
                    meth = getattr(self.scanner, name, None)
                    if meth:
                        sig = None
                        try:
                            sig = inspect.signature(meth)
                        except Exception:
                            pass

                        needs_mac = False
                        if sig is not None:
                            # Exclude 'self' if present
                            params = [
                                p for p in sig.parameters.values() if p.name != 'self']
                            needs_mac = len(params) >= 1

                        if inspect.iscoroutinefunction(meth):
                            if needs_mac:
                                return await meth(config.PHONE_MAC)
                            return await meth()
                        else:
                            loop = asyncio.get_running_loop()
                            if needs_mac:
                                return await loop.run_in_executor(None, meth, config.PHONE_MAC)
                            return await loop.run_in_executor(None, meth)

            # 2) Try module-level async functions
            if hasattr(bt_module, "scan_for_device"):
                meth = getattr(bt_module, "scan_for_device")
                sig = None
                try:
                    sig = inspect.signature(meth)
                except Exception:
                    pass

                needs_mac = False
                if sig is not None:
                    params = list(sig.parameters.values())
                    needs_mac = len(params) >= 1

                if inspect.iscoroutinefunction(meth):
                    if needs_mac:
                        return await meth(config.PHONE_MAC)
                    return await meth()
                else:
                    loop = asyncio.get_running_loop()
                    if needs_mac:
                        return await loop.run_in_executor(None, meth, config.PHONE_MAC)
                    return await loop.run_in_executor(None, meth)

            # 3) Try module-level sync functions
            for name in ("get_device_rssi", "get_rssi", "discover_once"):
                meth = getattr(bt_module, name, None)
                if meth:
                    sig = None
                    try:
                        sig = inspect.signature(meth)
                    except Exception:
                        pass

                    needs_mac = False
                    if sig is not None:
                        params = list(sig.parameters.values())
                        needs_mac = len(params) >= 1

                    loop = asyncio.get_running_loop()
                    if needs_mac:
                        return await loop.run_in_executor(None, meth, config.PHONE_MAC)
                    return await loop.run_in_executor(None, meth)

            self.logger.log_warning("No usable Bluetooth scanner API found.")
            return None

        except Exception as e:
            self.logger.log_warning(f"RSSI read failed: {e}")
            return None  # <-- safely handle any scan failure

    # -------------------------------------------------------------------------
    def _should_lock(self, rssi: Optional[int]) -> bool:
        """Determine if system should lock."""
        if rssi is None:
            self.consecutive_failures += 1
            if self.consecutive_failures >= config.CONSECUTIVE_FAIL_THRESHOLD:
                self.logger.log_phone_not_detected()
                return True
            return False

        self.consecutive_failures = 0
        if rssi < config.LOCK_THRESHOLD:
            self.logger.log_phone_detected(rssi)
            return True
        return False

    # -------------------------------------------------------------------------
    def _should_unlock(self, rssi: Optional[int]) -> bool:
        """Determine if system should unlock."""
        if rssi is None:
            return False
        if rssi > config.UNLOCK_THRESHOLD:
            self.logger.log_phone_detected(rssi)
            return True
        return False

    # -------------------------------------------------------------------------
    async def monitor_loop(self):
        """Main monitoring loop."""
        try:
            while True:
                rssi = None
                try:
                    rssi = await self._get_rssi()
                except Exception as e:
                    self.logger.log_warning(f"RSSI scan exception: {e}")
                    rssi = None

                if not self.is_locked:
                    if self._should_lock(rssi):
                        ok = self.system_controller.lock_system()
                        if ok:
                            self.is_locked = True
                            self.logger.log_system_locked(rssi)
                else:
                    if self._should_unlock(rssi):
                        ok = self.system_controller.wake_system()
                        if ok:
                            self.is_locked = False
                            self.logger.log_system_unlocked(rssi)

                await asyncio.sleep(config.SCAN_INTERVAL)

        except asyncio.CancelledError:
            pass
        except KeyboardInterrupt:
            pass
        except Exception as e:
            tb = ''.join(traceback.format_exception(None, e, e.__traceback__))
            self.logger.log_error(f"Fatal error: {tb}")
            raise

    # -------------------------------------------------------------------------
    def _shutdown(self):
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
            f"Locks: {stats.get('total_locks', 'N/A')} | Unlocks: {stats.get('total_unlocks', 'N/A')}")
        print("[EXIT] System stopped gracefully.\n")


# -------------------------------------------------------------------------
def run():
    controller = ProximityLockController()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(controller.monitor_loop())
    except KeyboardInterrupt:
        controller._shutdown()
    except Exception as e:
        controller.logger.log_error(f"Unhandled exception: {e}")
        controller._shutdown()
    finally:
        loop.close()


if __name__ == "__main__":
    run()
