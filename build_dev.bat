@echo off
REM ============================================================
REM LiteFinPad Development Build Script v3.0
REM ============================================================
REM Purpose: Build development/testing versions
REM Usage:
REM   build_dev.bat           - Build current version (no increment)
REM   build_dev.bat increment - Build and auto-increment minor version
REM ============================================================

setlocal enabledelayedexpansion

echo.
echo ========================================
echo LiteFinPad Development Build Script
echo ========================================
echo.

REM ============================================================
REM STEP 1: Version Management
REM ============================================================
echo [STEP 1/9] Managing version...

REM Check if we should increment
set INCREMENT_VERSION=0
if "%1"=="increment" set INCREMENT_VERSION=1

REM Read current version using Python script
for /f "delims=" %%i in ('python version_manager.py read') do set CURRENT_VERSION=%%i

if "%INCREMENT_VERSION%"=="1" (
    echo [INFO] Auto-incrementing version...
    for /f "delims=" %%i in ('python version_manager.py increment minor') do set CURRENT_VERSION=%%i
    echo [SUCCESS] Version incremented to: %CURRENT_VERSION%
) else (
    echo [INFO] Building current version: %CURRENT_VERSION%
)

echo [INFO] Development Build: v%CURRENT_VERSION%
echo.

REM ============================================================
REM STEP 2: Process Detection & Cleanup
REM ============================================================
echo [STEP 2/9] Checking for running processes...
tasklist /FI "IMAGENAME eq LiteFinPad_v%CURRENT_VERSION%.exe" 2>NUL | find /I /N "LiteFinPad_v%CURRENT_VERSION%.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo [WARNING] Detected running LiteFinPad process!
    echo [ACTION] Terminating process to prevent file locks...
    taskkill /F /IM "LiteFinPad_v%CURRENT_VERSION%.exe" >NUL 2>&1
    timeout /t 2 /nobreak >NUL
    echo [SUCCESS] Process terminated
) else (
    echo [OK] No running processes detected
)
echo.

REM ============================================================
REM STEP 3: Clean Build Environment
REM ============================================================
echo [STEP 3/9] Cleaning build environment...
if exist "build" (
    rmdir /s /q "build" 2>NUL
    if exist "build" (
        echo [ERROR] Failed to remove build folder - files may be locked
        echo [SOLUTION] Close all applications and try again
        pause
        exit /b 1
    )
)
if exist "dist" (
    rmdir /s /q "dist" 2>NUL
    if exist "dist" (
        echo [ERROR] Failed to remove dist folder - files may be locked
        echo [SOLUTION] Close all applications and try again
        pause
        exit /b 1
    )
)
echo [SUCCESS] Build environment cleaned
echo.

REM ============================================================
REM STEP 4: Install Dependencies
REM ============================================================
echo [STEP 4/9] Installing dependencies...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    echo [SOLUTION] Check requirements.txt and your Python environment
    pause
    exit /b 1
)
echo [SUCCESS] Dependencies installed
echo.

REM ============================================================
REM STEP 5: PyInstaller Build
REM ============================================================
echo [STEP 5/9] Building executable with PyInstaller...
echo [INFO] This may take 1-2 minutes...
echo [INFO] Development build - optimized for testing
echo.

REM Auto-detect the current .spec file (excludes archived specs)
set "SPEC_FILE="
for %%F in (LiteFinPad_v*.spec) do (
    if defined SPEC_FILE (
        echo [ERROR] Multiple .spec files found in root directory!
        echo [ERROR] Please keep only one .spec file in the root.
        pause
        exit /b 1
    )
    set "SPEC_FILE=%%F"
)

if not defined SPEC_FILE (
    echo [ERROR] No .spec file found in root directory!
    echo [ERROR] Expected file: LiteFinPad_v*.spec
    pause
    exit /b 1
)

echo [INFO] Using spec file: %SPEC_FILE%
echo.

REM Use the pre-configured .spec file (includes all modules: analytics, data_manager, validation, widgets)
py -3.14 -m PyInstaller %SPEC_FILE%

if errorlevel 1 (
    echo.
    echo [CRITICAL ERROR] PyInstaller failed!
    echo [DETAILS] Check the output above for specific errors
    pause
    exit /b 1
)

REM Verify build completed
if not exist "dist\LiteFinPad_v%CURRENT_VERSION%\LiteFinPad_v%CURRENT_VERSION%.exe" (
    echo.
    echo [CRITICAL ERROR] Executable not created!
    pause
    exit /b 1
)

echo.
echo [SUCCESS] PyInstaller build completed
echo.

REM ============================================================
REM STEP 6: Verify Critical Folders
REM ============================================================
echo [STEP 6/9] Verifying critical build components...

set CRITICAL_ERROR=0

if not exist "dist\LiteFinPad_v%CURRENT_VERSION%\_internal\_tcl_data" (
    echo [CRITICAL ERROR] _tcl_data folder missing!
    set CRITICAL_ERROR=1
)

if not exist "dist\LiteFinPad_v%CURRENT_VERSION%\_internal\_tcl_data\encoding" (
    echo [CRITICAL ERROR] _tcl_data\encoding folder missing!
    set CRITICAL_ERROR=1
)

if "%CRITICAL_ERROR%"=="1" (
    echo.
    echo [BUILD ABORTED] Critical components missing!
    pause
    exit /b 1
)

echo [SUCCESS] All critical components present
echo.

REM ============================================================
REM STEP 7: Copy Additional Libraries
REM ============================================================
echo [STEP 7/9] Copying export libraries...
call copy_libraries.bat
if errorlevel 1 (
    echo [WARNING] Library copy had issues - exports may not work
)
echo.

REM ============================================================
REM STEP 8: Optimizations (Light for Dev Builds)
REM ============================================================
echo [STEP 8/9] Applying development optimizations...

REM Only remove the most bloated items for dev builds
if exist "dist\LiteFinPad_v%CURRENT_VERSION%\_internal\_tcl_data\tzdata" (
    rmdir /s /q "dist\LiteFinPad_v%CURRENT_VERSION%\_internal\_tcl_data\tzdata"
    echo [OPT] Removed timezone files [~3MB saved]
)

if exist "dist\LiteFinPad_v%CURRENT_VERSION%\_internal\libcrypto-3.dll" (
    del /q "dist\LiteFinPad_v%CURRENT_VERSION%\_internal\libcrypto-3.dll"
    echo [OPT] Removed libcrypto-3.dll [~5MB saved]
)

if exist "dist\LiteFinPad_v%CURRENT_VERSION%\_internal\libssl-3.dll" (
    del /q "dist\LiteFinPad_v%CURRENT_VERSION%\_internal\libssl-3.dll"
    echo [OPT] Removed libssl-3.dll [~776KB saved]
)

echo [SUCCESS] Development optimizations applied
echo.

REM ============================================================
REM STEP 9: Copy Data & Support Files
REM ============================================================
echo [STEP 9/9] Copying data and support files...

if exist "data_2025-10" (
    xcopy /E /I /Y "data_2025-10" "dist\LiteFinPad_v%CURRENT_VERSION%\data_2025-10" >NUL
    echo [SUCCESS] Data folder copied
)

copy "error_logger.py" "dist\LiteFinPad_v%CURRENT_VERSION%\error_logger.py" >NUL 2>&1
echo [SUCCESS] Error logger copied
echo.

REM ============================================================
REM FINAL VALIDATION & SUMMARY
REM ============================================================
echo.
echo ========================================
echo DEVELOPMENT BUILD COMPLETE
echo ========================================
echo.
echo Version: %CURRENT_VERSION% (DEV)
echo Location: dist\LiteFinPad_v%CURRENT_VERSION%\
echo Executable: LiteFinPad_v%CURRENT_VERSION%.exe
echo.
echo [DEV BUILD] This build is for testing and development
echo [NEXT STEP] Test the application before creating a release build
echo.
echo To create a production release, use: build_release.bat
echo.
pause

