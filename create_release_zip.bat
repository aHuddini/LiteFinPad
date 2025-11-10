@echo off
REM ============================================================================
REM LiteFinPad Release ZIP Creator - Batch Wrapper
REM ============================================================================
REM This batch file runs the PowerShell script with execution policy bypass
REM ============================================================================

cd /d "%~dp0"

echo.
echo ============================================
echo   LiteFinPad Release ZIP Creator
echo ============================================
echo.

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "create_release_zip.ps1"

if errorlevel 1 (
    echo.
    echo ERROR: Script execution failed!
    pause
    exit /b 1
)

echo.
pause

