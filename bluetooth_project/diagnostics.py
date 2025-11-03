"""
Diagnostics for Bluetooth Proximity Lock project.
Runs basic checks: Python version, cwd, sys.path, imports, and config validation.
"""

import sys
import os
import traceback


def main() -> int:
    print("=== Diagnostics ===")
    print(f"Python: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"CWD: {os.getcwd()}")
    print("\nsys.path:")
    for p in sys.path:
        print(" -", p)

    print("\n[1] Import config_module ...")
    try:
        import config_module as config  # noqa: F401
        print(" OK: config_module imported")
    except Exception as e:
        print(" FAIL: config_module import error:")
        traceback.print_exc()
        return 1

    print("\n[2] Validate config ...")
    try:
        import config_module as config
        if hasattr(config, "validate_config"):
            config.validate_config()
            print(" OK: validate_config() passed")
        else:
            print(" WARN: validate_config() not found")
    except Exception:
        print(" FAIL: validate_config() error:")
        traceback.print_exc()
        return 1

    print("\n[3] Import Bluetooth scanner ...")
    try:
        import bluetooth_scanner_module as bt  # noqa: F401
        print(" OK: bluetooth_scanner_module imported")
    except Exception:
        print(" FAIL: bluetooth_scanner_module import error:")
        traceback.print_exc()
        # not fatal for path issues

    print("\n[4] Import system control ...")
    try:
        import system_control_module as sysctl  # noqa: F401
        print(" OK: system_control_module imported")
    except Exception:
        print(" FAIL: system_control_module import error:")
        traceback.print_exc()
        return 1

    print("\n[5] Import logger ...")
    try:
        import logger_module as lm
        _ = lm.get_logger()
        print(" OK: logger_module imported and logger created")
    except Exception:
        print(" FAIL: logger_module import or init error:")
        traceback.print_exc()
        return 1

    print("\nAll diagnostics checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


