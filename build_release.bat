@echo off
REM ============================================================
REM LiteFinPad Production Release Build Script v3.0
REM ============================================================
REM Purpose: Build production-ready releases
REM Usage:
REM   build_release.bat        - Build stable release (current version)
REM   build_release.bat major  - Increment major version (3.0 -> 4.0)
REM ============================================================

setlocal enabledelayedexpansion

echo.
echo ========================================
echo LiteFinPad Production Release Builder
echo ========================================
echo.

REM ============================================================
REM STEP 1: Version Management
REM ============================================================
echo [STEP 1/10] Managing release version...

REM Check if we should increment major version
set INCREMENT_MAJOR=0
if "%1"=="major" set INCREMENT_MAJOR=1

REM Read current version
for /f "delims=" %%i in ('python version_manager.py read') do set CURRENT_VERSION=%%i

if "%INCREMENT_MAJOR%"=="1" (
    echo [INFO] Incrementing major version for release...
    for /f "delims=" %%i in ('python version_manager.py increment major') do set CURRENT_VERSION=%%i
    echo [SUCCESS] Version incremented to: %CURRENT_VERSION%
) else (
    echo [INFO] Building release version: %CURRENT_VERSION%
)

echo.
echo ╔════════════════════════════════════════╗
echo ║  PRODUCTION RELEASE BUILD: v%CURRENT_VERSION%       ║
echo ╚════════════════════════════════════════╝
echo.

REM Confirmation for production build
echo [WARNING] You are about to create a PRODUCTION RELEASE
echo [INFO] This will be the stable, distributable version
echo.
set /p CONFIRM="Continue with production build? (Y/N): "
if /i not "%CONFIRM%"=="Y" (
    echo [CANCELLED] Build cancelled by user
    pause
    exit /b 0
)
echo.

REM ============================================================
REM STEP 2: Process Detection & Cleanup
REM ============================================================
echo [STEP 2/10] Checking for running processes...
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
echo [STEP 3/10] Cleaning build environment...
if exist "build" (
    rmdir /s /q "build" 2>NUL
    if exist "build" (
        echo [ERROR] Failed to remove build folder - files may be locked
        pause
        exit /b 1
    )
)
if exist "dist" (
    rmdir /s /q "dist" 2>NUL
    if exist "dist" (
        echo [ERROR] Failed to remove dist folder - files may be locked
        pause
        exit /b 1
    )
)
echo [SUCCESS] Build environment cleaned
echo.

REM ============================================================
REM STEP 4: Install Dependencies
REM ============================================================
echo [STEP 4/10] Installing dependencies...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [SUCCESS] Dependencies installed
echo.

REM ============================================================
REM STEP 5: PyInstaller Build
REM ============================================================
echo [STEP 5/10] Building production executable...
echo [INFO] This may take 2-3 minutes...
echo [INFO] Production build - fully optimized
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
    pause
    exit /b 1
)

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
echo [STEP 6/10] Verifying critical build components...

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
echo [STEP 7/10] Copying export libraries...
call copy_libraries.bat
if errorlevel 1 (
    echo [WARNING] Library copy had issues - exports may not work
)
echo.

REM ============================================================
REM STEP 8: Production Optimizations (Aggressive)
REM ============================================================
echo [STEP 8/10] Applying production optimizations...

REM TCL/TK Data Optimization
if exist "dist\LiteFinPad_v%CURRENT_VERSION%\_internal\_tcl_data\tzdata" (
    rmdir /s /q "dist\LiteFinPad_v%CURRENT_VERSION%\_internal\_tcl_data\tzdata"
    echo [OPT] Removed 609 timezone files [~3MB saved]
)
if exist "dist\LiteFinPad_v%CURRENT_VERSION%\_internal\_tcl_data\msgs" (
    rmdir /s /q "dist\LiteFinPad_v%CURRENT_VERSION%\_internal\_tcl_data\msgs"
    echo [OPT] Removed 127 TCL message files [~500KB saved]
)
if exist "dist\LiteFinPad_v%CURRENT_VERSION%\_internal\_tk_data\msgs" (
    rmdir /s /q "dist\LiteFinPad_v%CURRENT_VERSION%\_internal\_tk_data\msgs"
    echo [OPT] Removed 18 TK message files [~100KB saved]
)
if exist "dist\LiteFinPad_v%CURRENT_VERSION%\_internal\_tk_data\images" (
    rmdir /s /q "dist\LiteFinPad_v%CURRENT_VERSION%\_internal\_tk_data\images"
    echo [OPT] Removed 13 sample images [~200KB saved]
)

REM Setuptools Optimization
if exist "dist\LiteFinPad_v%CURRENT_VERSION%\_internal\setuptools" (
    rmdir /s /q "dist\LiteFinPad_v%CURRENT_VERSION%\_internal\setuptools"
    echo [OPT] Removed setuptools [~2MB saved]
)
if exist "dist\LiteFinPad_v%CURRENT_VERSION%\_internal\pkg_resources" (
    rmdir /s /q "dist\LiteFinPad_v%CURRENT_VERSION%\_internal\pkg_resources"
    echo [OPT] Removed pkg_resources [~500KB saved]
)

REM TCL8 Modules Optimization
if exist "dist\LiteFinPad_v%CURRENT_VERSION%\_internal\tcl8\8.4\platform" (
    rmdir /s /q "dist\LiteFinPad_v%CURRENT_VERSION%\_internal\tcl8\8.4\platform"
)
if exist "dist\LiteFinPad_v%CURRENT_VERSION%\_internal\tcl8\8.4\platform-1.0.19.tm" (
    del /q "dist\LiteFinPad_v%CURRENT_VERSION%\_internal\tcl8\8.4\platform-1.0.19.tm"
)
if exist "dist\LiteFinPad_v%CURRENT_VERSION%\_internal\tcl8\8.5\tcltest-2.5.8.tm" (
    del /q "dist\LiteFinPad_v%CURRENT_VERSION%\_internal\tcl8\8.5\tcltest-2.5.8.tm"
)
if exist "dist\LiteFinPad_v%CURRENT_VERSION%\_internal\tcl8\8.5\msgcat-1.6.1.tm" (
    del /q "dist\LiteFinPad_v%CURRENT_VERSION%\_internal\tcl8\8.5\msgcat-1.6.1.tm"
)
if exist "dist\LiteFinPad_v%CURRENT_VERSION%\_internal\tcl8\8.6\http-2.9.8.tm" (
    del /q "dist\LiteFinPad_v%CURRENT_VERSION%\_internal\tcl8\8.6\http-2.9.8.tm"
)
echo [OPT] Removed TCL8 modules [~150KB saved]

REM OpenSSL Optimization
if exist "dist\LiteFinPad_v%CURRENT_VERSION%\_internal\libcrypto-3.dll" (
    del /q "dist\LiteFinPad_v%CURRENT_VERSION%\_internal\libcrypto-3.dll"
    echo [OPT] Removed libcrypto-3.dll [~5MB saved]
)
if exist "dist\LiteFinPad_v%CURRENT_VERSION%\_internal\libssl-3.dll" (
    del /q "dist\LiteFinPad_v%CURRENT_VERSION%\_internal\libssl-3.dll"
    echo [OPT] Removed libssl-3.dll [~776KB saved]
)
if exist "dist\LiteFinPad_v%CURRENT_VERSION%\_internal\_ssl.pyd" (
    del /q "dist\LiteFinPad_v%CURRENT_VERSION%\_internal\_ssl.pyd"
    echo [OPT] Removed _ssl.pyd [~179KB saved]
)

echo [SUCCESS] Production optimizations applied
echo.

REM ============================================================
REM STEP 9: Copy Data & Support Files
REM ============================================================
echo [STEP 9/10] Copying data and support files...

if exist "data_2025-10" (
    xcopy /E /I /Y "data_2025-10" "dist\LiteFinPad_v%CURRENT_VERSION%\data_2025-10" >NUL
    echo [SUCCESS] Data folder copied
)

copy "error_logger.py" "dist\LiteFinPad_v%CURRENT_VERSION%\error_logger.py" >NUL 2>&1
echo [SUCCESS] Error logger copied
echo.

REM ============================================================
REM STEP 10: Production Validation & Summary
REM ============================================================
echo [STEP 10/10] Final production validation...

REM Count files
for /f %%A in ('dir /b /s "dist\LiteFinPad_v%CURRENT_VERSION%\_internal" ^| find /c /v ""') do set FILE_COUNT=%%A

REM Get sizes
for %%A in ("dist\LiteFinPad_v%CURRENT_VERSION%\LiteFinPad_v%CURRENT_VERSION%.exe") do set EXE_SIZE=%%~zA
set /a EXE_SIZE_MB=%EXE_SIZE% / 1048576

REM Calculate total distribution size
for /f "tokens=3" %%A in ('dir /s "dist\LiteFinPad_v%CURRENT_VERSION%" ^| find "File(s)"') do set TOTAL_SIZE=%%A
set /a TOTAL_SIZE_MB=%TOTAL_SIZE% / 1048576

echo.
echo ========================================
echo PRODUCTION RELEASE VALIDATION
echo ========================================
echo.

echo [CHECK] Executable:
if exist "dist\LiteFinPad_v%CURRENT_VERSION%\LiteFinPad_v%CURRENT_VERSION%.exe" (
    echo   [OK] LiteFinPad_v%CURRENT_VERSION%.exe
) else (
    echo   [FAIL] Executable missing!
    pause
    exit /b 1
)

echo [CHECK] TCL/TK Data:
if exist "dist\LiteFinPad_v%CURRENT_VERSION%\_internal\_tcl_data\encoding" (
    echo   [OK] All critical components present
) else (
    echo   [FAIL] Critical components missing!
    pause
    exit /b 1
)

echo [CHECK] File Count:
echo   [INFO] %FILE_COUNT% files in distribution
if %FILE_COUNT% LSS 200 (
    echo   [WARNING] File count seems low
)

echo [CHECK] Size Metrics:
echo   [INFO] Executable: %EXE_SIZE_MB% MB
echo   [INFO] Total Distribution: %TOTAL_SIZE_MB% MB
if %TOTAL_SIZE_MB% GTR 30 (
    echo   [WARNING] Distribution size is larger than expected
)

echo.
echo ╔════════════════════════════════════════╗
echo ║  PRODUCTION RELEASE READY!             ║
echo ╚════════════════════════════════════════╝
echo.
echo Version: v%CURRENT_VERSION% (STABLE)
echo Location: dist\LiteFinPad_v%CURRENT_VERSION%\
echo Executable: LiteFinPad_v%CURRENT_VERSION%.exe
echo File Count: %FILE_COUNT% files
echo Distribution Size: %TOTAL_SIZE_MB% MB
echo.
echo [RELEASE] This build is ready for distribution
echo [NEXT STEPS]:
echo   1. Test the application thoroughly
echo   2. Update CHANGELOG.md with release notes
echo   3. Create backup: backup_v%CURRENT_VERSION%_stable
echo   4. Tag release in version control
echo.
pause

