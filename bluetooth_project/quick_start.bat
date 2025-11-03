@echo off
REM ============================================================================
REM Quick Start Script - Run this after initial setup is complete
REM ============================================================================
REM This is a lightweight script to start the system quickly after the first
REM setup. It skips the installation steps and goes straight to running.
REM
REM Use this for daily operation after running setup_and_run.bat once.
REM ============================================================================

SETLOCAL
cd /d "%~dp0"

COLOR 0A
TITLE Bluetooth Proximity Lock - Quick Start

cls
echo.
echo ========================================================================
echo           BLUETOOTH PROXIMITY LOCK SYSTEM
echo                    Quick Start
echo ========================================================================
echo.

REM Quick validation
if not exist "main_module.py" (
    COLOR 0C
    echo [ERROR] main_module.py not found!
    echo Please run setup_and_run.bat first.
    echo.
    pause
    exit /b 1
)

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    COLOR 0C
    echo [ERROR] Python not found!
    echo Please run setup_and_run.bat first.
    echo.
    pause
    exit /b 1
)

echo [OK] Starting Proximity Lock System...
echo.
echo Press Ctrl+C to stop
echo.
timeout /t 2 /nobreak >nul

cls

REM Run the system
set PYTHONPATH=%CD%
python main_module.py

REM Handle exit
if %errorlevel% neq 0 (
    COLOR 0C
    echo.
    echo [ERROR] System exited with an error.
    echo Check activity_log.txt for details.
) else (
    COLOR 0A
    echo.
    echo [OK] System stopped.
)

echo.
pause

ENDLOCAL
exit /b %errorlevel%
