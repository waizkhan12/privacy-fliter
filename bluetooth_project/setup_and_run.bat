@echo off
REM ============================================================================
REM Bluetooth Proximity Lock System - Setup and Run Script (Fixed Version)
REM ============================================================================
REM Handles:
REM   1. Environment validation
REM   2. Dependency installation
REM   3. Configuration check
REM   4. System startup
REM ============================================================================

SETLOCAL EnableDelayedExpansion
COLOR 0A
TITLE Bluetooth Proximity Lock - Setup and Run
cd /d "%~dp0"
cls

echo.
echo ========================================================================
echo           BLUETOOTH PROXIMITY LOCK SYSTEM
echo                   Setup and Run Script
echo ========================================================================
echo.
echo Current Directory: %CD%
echo.
timeout /t 2 /nobreak >nul

REM ============================================================================
REM STEP 1 - Check Python Installation
REM ============================================================================
echo [STEP 1/5] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    COLOR 0C
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.10 or higher and add it to PATH.
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION% detected
echo.

REM ============================================================================
REM STEP 2 - Verify Project Files
REM ============================================================================
echo [STEP 2/5] Verifying project files...
set MISSING_FILES=0
set MISSING_LIST=

for %%f in (config_module.py bluetooth_scanner_module.py system_control_module.py logger_module.py main_module.py) do (
    if not exist "%%f" (
        echo [MISSING] %%f
        set MISSING_FILES=1
        set MISSING_LIST=!MISSING_LIST! %%f
    )
)

if !MISSING_FILES! equ 1 (
    COLOR 0C
    echo.
    echo Missing files detected: !MISSING_LIST!
    echo Ensure all Python modules are present in %CD%.
    pause
    exit /b 1
)
echo [OK] All required files found.
echo.

REM ============================================================================
REM STEP 3 - Check pip
REM ============================================================================
echo [STEP 3/5] Checking pip...
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    COLOR 0E
    echo [WARNING] pip not found. Installing...
    python -m ensurepip --default-pip
    if %errorlevel% neq 0 (
        COLOR 0C
        echo [ERROR] Failed to install pip.
        pause
        exit /b 1
    )
)
echo [OK] pip available.
echo.

REM ============================================================================
REM STEP 4 - Install Dependencies
REM ============================================================================
echo [STEP 4/5] Installing dependencies...
if not exist "requirements_file.txt" (
    echo [WARNING] requirements_file.txt not found! Installing bleak manually...
    python -m pip install --upgrade bleak
) else (
    python -m pip install --upgrade -r requirements_file.txt
)
if %errorlevel% neq 0 (
    COLOR 0C
    echo [ERROR] Dependency installation failed.
    pause
    exit /b 1
)
echo [OK] Dependencies installed successfully.
echo.

REM ============================================================================
REM STEP 5 - Validate Configuration
REM ============================================================================
echo [STEP 5/5] Validating configuration...
set PYTHONPATH=%CD%
python - <<PYCODE
import sys
try:
    import config_module as config
    if hasattr(config, 'validate_config'):
        config.validate_config()
    print('[OK] PHONE_MAC =', config.PHONE_MAC)
    print('[OK] HEADPHONE_MAC =', getattr(config, 'HEADPHONE_MAC', ''))
    sys.exit(0)
except Exception as e:
    print('[ERROR] Config validation failed:', e)
    sys.exit(1)
PYCODE
if %errorlevel% neq 0 (
    COLOR 0C
    echo [ERROR] Configuration validation failed. Please check config_module.py
    pause
    exit /b 1
)
echo.

REM ============================================================================
REM START SYSTEM
REM ============================================================================
COLOR 0A
cls
echo ========================================================================
echo                      STARTING PROXIMITY LOCK SYSTEM
echo ========================================================================
echo.
echo Keep your phone’s Bluetooth ON.
echo Move away to trigger auto-lock, come close to unlock.
echo Press Ctrl+C to stop the system.
echo ========================================================================
echo.
timeout /t 3 /nobreak >nul
cls

set PYTHONPATH=%CD%
python main_module.py

if %errorlevel% neq 0 (
    COLOR 0C
    echo [ERROR] System exited with error code %errorlevel%.
    echo Check activity_log.txt for details.
) else (
    COLOR 0A
    echo [OK] System stopped gracefully.
)
pause >nul
ENDLOCAL
exit /b %errorlevel%
