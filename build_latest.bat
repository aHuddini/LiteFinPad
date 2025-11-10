@echo off
REM ============================================================
REM LiteFinPad Intelligent Build Script v2.9
REM ============================================================
REM Features:
REM - Auto-detects and kills running processes
REM - Validates each build stage before continuing
REM - Stops immediately on critical failures
REM - Verifies TCL/TK data folders exist
REM - Provides detailed diagnostics
REM ============================================================

setlocal enabledelayedexpansion

echo.
echo ========================================
echo LiteFinPad Intelligent Build Script
echo ========================================
echo.

REM ============================================================
REM STEP 1: Version Management
REM ============================================================
if not exist "version.txt" (
    echo 2.9> version.txt
    echo [INFO] Created version.txt with version 2.9
)

set /p CURRENT_VERSION=<version.txt
echo [INFO] Building version: %CURRENT_VERSION%
echo.

REM ============================================================
REM STEP 2: Process Detection & Cleanup
REM ============================================================
echo [STEP 1/8] Checking for running processes...
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
echo [STEP 2/8] Cleaning build environment...
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
echo [STEP 3/8] Installing dependencies...
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
echo [STEP 4/8] Building executable with PyInstaller...
echo [INFO] This may take 1-2 minutes...
echo.

REM NOTE: Python files are auto-detected by PyInstaller through import analysis
REM Only add resource files (icon.ico) here - DO NOT add .py files
py -3.14 -m PyInstaller ^
    --onedir ^
    --windowed ^
    --name LiteFinPad_v%CURRENT_VERSION% ^
    --icon=icon.ico ^
    --add-data "icon.ico;." ^
             --collect-submodules=xlsxwriter ^
             --collect-submodules=fpdf ^
             --hidden-import=xlsxwriter ^
             --hidden-import=xlsxwriter.workbook ^
             --hidden-import=xlsxwriter.worksheet ^
             --hidden-import=xlsxwriter.format ^
             --hidden-import=fpdf ^
             --hidden-import=fpdf.fpdf ^
             --hidden-import=encodings ^
             --hidden-import=encodings.utf_8 ^
             --hidden-import=encodings.ascii ^
             --hidden-import=encodings.latin_1 ^
             --hidden-import=encodings.cp1252 ^
             --hidden-import=html ^
             --hidden-import=html.parser ^
             --hidden-import=html.entities ^
             --hidden-import=urllib ^
             --hidden-import=urllib.parse ^
             --hidden-import=urllib.request ^
             --hidden-import=base64 ^
             --hidden-import=zlib ^
             --hidden-import=re ^
             --hidden-import=math ^
             --hidden-import=datetime ^
             --hidden-import=json ^
    --collect-all=tkinter ^
    --exclude-module=tkinter.test ^
    --exclude-module=test ^
    --exclude-module=setuptools ^
    --exclude-module=setuptools._vendor ^
    --exclude-module=pkg_resources ^
    --exclude-module=PIL ^
    --exclude-module=Pillow ^
    --exclude-module=ssl ^
    --exclude-module=_ssl ^
    --distpath "dist" ^
    --workpath "build" ^
    --specpath "." ^
    main.py

if errorlevel 1 (
    echo.
    echo [CRITICAL ERROR] PyInstaller failed!
    echo [DETAILS] Check the output above for specific errors
    echo [COMMON CAUSES]:
    echo   - Missing dependencies
    echo   - Syntax errors in Python files
    echo   - Module import issues
    pause
    exit /b 1
)

REM Verify COLLECT stage completed
if not exist "dist\LiteFinPad_v%CURRENT_VERSION%" (
    echo.
    echo [CRITICAL ERROR] PyInstaller did not create distribution folder!
    echo [LIKELY CAUSE] COLLECT stage failed - check output above
    pause
    exit /b 1
)

if not exist "dist\LiteFinPad_v%CURRENT_VERSION%\LiteFinPad_v%CURRENT_VERSION%.exe" (
    echo.
    echo [CRITICAL ERROR] Executable not created!
    echo [LIKELY CAUSE] PyInstaller build incomplete
    pause
    exit /b 1
)

echo.
echo [SUCCESS] PyInstaller build completed
echo.

REM ============================================================
REM STEP 6: Verify Critical Folders
REM ============================================================
echo [STEP 5/8] Verifying critical build components...

set CRITICAL_ERROR=0

if not exist "dist\LiteFinPad_v%CURRENT_VERSION%\_internal\_tcl_data" (
    echo [CRITICAL ERROR] _tcl_data folder missing!
    echo [IMPACT] Application will fail with encoding errors
    echo [CAUSE] PyInstaller did not bundle TCL/TK data properly
    set CRITICAL_ERROR=1
)

if not exist "dist\LiteFinPad_v%CURRENT_VERSION%\_internal\_tk_data" (
    echo [WARNING] _tk_data folder missing
    echo [IMPACT] Some UI features may not work correctly
)

if not exist "dist\LiteFinPad_v%CURRENT_VERSION%\_internal\_tcl_data\encoding" (
    echo [CRITICAL ERROR] _tcl_data\encoding folder missing!
    echo [IMPACT] Application WILL fail to start
    set CRITICAL_ERROR=1
)

if "%CRITICAL_ERROR%"=="1" (
    echo.
    echo [BUILD ABORTED] Critical components missing!
    echo [SOLUTION] This is a PyInstaller bundling issue
    echo [ACTION] Try running the build script again
    pause
    exit /b 1
)

echo [SUCCESS] All critical components present
echo.

REM ============================================================
REM STEP 7: Copy Additional Libraries
REM ============================================================
echo [STEP 6/8] Copying export libraries...
call copy_libraries.bat
if errorlevel 1 (
    echo [WARNING] Library copy had issues - exports may not work
    echo [CONTINUE] Build will continue...
)
echo.

REM ============================================================
REM STEP 8: Optimizations
REM ============================================================
echo [STEP 7/8] Applying size optimizations...

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

REM OpenSSL Optimization (offline app)
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

REM Remove redundant .py source files where .pyc compiled versions exist
if exist "dist\LiteFinPad_v%CURRENT_VERSION%\_internal\xlsxwriter\__pycache__" (
    del /q "dist\LiteFinPad_v%CURRENT_VERSION%\_internal\xlsxwriter\*.py" 2>NUL
    echo [OPT] Removed xlsxwriter source files (~800KB saved)
)
if exist "dist\LiteFinPad_v%CURRENT_VERSION%\_internal\fpdf\__pycache__" (
    del /q "dist\LiteFinPad_v%CURRENT_VERSION%\_internal\fpdf\*.py" 2>NUL
    echo [OPT] Removed fpdf source files (~250KB saved)
)

REM Hide _internal folder from users
attrib +h "dist\LiteFinPad_v%CURRENT_VERSION%\_internal" >NUL 2>&1

echo [SUCCESS] Optimizations applied
echo.

REM ============================================================
REM STEP 9: Copy Data & Support Files
REM ============================================================
echo [STEP 8/8] Copying data and support files...

if exist "data_2025-10" (
    xcopy /E /I /Y "data_2025-10" "dist\LiteFinPad_v%CURRENT_VERSION%\data_2025-10" >NUL
    echo [SUCCESS] Data folder copied
) else (
    echo [WARNING] data_2025-10 folder not found
)

REM NOTE: error_logger.py is auto-compiled by PyInstaller into _internal/
REM No need to copy separately - it's available through import statements

REM Copy user-editable configuration files (NOT bundled in exe)
copy "settings.ini" "dist\LiteFinPad_v%CURRENT_VERSION%\settings.ini" >NUL 2>&1
echo [SUCCESS] settings.ini copied (user-editable)

copy "version.txt" "dist\LiteFinPad_v%CURRENT_VERSION%\version.txt" >NUL 2>&1
echo [SUCCESS] version.txt copied

REM Copy README.txt for distribution (REQUIRED for release)
if not exist "README.txt" (
    echo [CRITICAL ERROR] README.txt file not found!
    echo [REQUIRED] README.txt file must exist in project root for distribution
    pause
    exit /b 1
)
copy "README.txt" "dist\LiteFinPad_v%CURRENT_VERSION%\README.txt" >NUL 2>&1
if errorlevel 1 (
    echo [CRITICAL ERROR] Failed to copy README.txt file!
    pause
    exit /b 1
)
echo [SUCCESS] README.txt copied

REM Copy license files for distribution (REQUIRED for release)
if not exist "LICENSE" (
    echo [CRITICAL ERROR] LICENSE file not found!
    echo [REQUIRED] LICENSE file must exist in project root for distribution
    pause
    exit /b 1
)
copy "LICENSE" "dist\LiteFinPad_v%CURRENT_VERSION%\LICENSE" >NUL 2>&1
if errorlevel 1 (
    echo [CRITICAL ERROR] Failed to copy LICENSE file!
    pause
    exit /b 1
)
echo [SUCCESS] LICENSE copied

if not exist "docs\developer\THIRD_PARTY_LICENSES.txt" (
    echo [CRITICAL ERROR] THIRD_PARTY_LICENSES.txt not found!
    echo [REQUIRED] THIRD_PARTY_LICENSES.txt must exist in docs\developer\ for distribution
    echo [INFO] Expected location: docs\developer\THIRD_PARTY_LICENSES.txt
    pause
    exit /b 1
)
copy "docs\developer\THIRD_PARTY_LICENSES.txt" "dist\LiteFinPad_v%CURRENT_VERSION%\THIRD_PARTY_LICENSES.txt" >NUL 2>&1
if errorlevel 1 (
    echo [CRITICAL ERROR] Failed to copy THIRD_PARTY_LICENSES.txt!
    pause
    exit /b 1
)
echo [SUCCESS] THIRD_PARTY_LICENSES.txt copied

echo.

REM ============================================================
REM FINAL VALIDATION & SUMMARY
REM ============================================================
echo.
echo ========================================
echo BUILD VALIDATION
echo ========================================
echo.

REM Count files in distribution
for /f %%A in ('dir /b /s "dist\LiteFinPad_v%CURRENT_VERSION%\_internal" ^| find /c /v ""') do set FILE_COUNT=%%A

echo [CHECK] Executable: 
if exist "dist\LiteFinPad_v%CURRENT_VERSION%\LiteFinPad_v%CURRENT_VERSION%.exe" (
    echo   [OK] dist\LiteFinPad_v%CURRENT_VERSION%\LiteFinPad_v%CURRENT_VERSION%.exe
) else (
    echo   [FAIL] Executable missing!
    pause
    exit /b 1
)

echo [CHECK] TCL/TK Data:
if exist "dist\LiteFinPad_v%CURRENT_VERSION%\_internal\_tcl_data" (
    echo   [OK] _tcl_data folder present
) else (
    echo   [FAIL] _tcl_data folder missing!
    pause
    exit /b 1
)

echo [CHECK] Encoding Data:
if exist "dist\LiteFinPad_v%CURRENT_VERSION%\_internal\_tcl_data\encoding" (
    echo   [OK] encoding folder present
) else (
    echo   [FAIL] encoding folder missing!
    pause
    exit /b 1
)

echo [CHECK] File Count:
echo   [INFO] Total files in _internal: %FILE_COUNT%
if %FILE_COUNT% LSS 200 (
    echo   [WARNING] File count seems low - build may be incomplete
    echo   [EXPECTED] ~300-350 files for complete build
)

REM Get executable size
for %%A in ("dist\LiteFinPad_v%CURRENT_VERSION%\LiteFinPad_v%CURRENT_VERSION%.exe") do set EXE_SIZE=%%~zA
set /a EXE_SIZE_MB=%EXE_SIZE% / 1048576

echo [CHECK] Executable Size:
echo   [INFO] %EXE_SIZE_MB% MB

echo.
echo ========================================
echo BUILD SUCCESSFUL!
echo ========================================
echo.
echo Version: %CURRENT_VERSION%
echo Location: dist\LiteFinPad_v%CURRENT_VERSION%\
echo Executable: LiteFinPad_v%CURRENT_VERSION%.exe
echo File Count: %FILE_COUNT% files
echo Size: %EXE_SIZE_MB% MB
echo.
echo [READY] Build is ready for testing and distribution
echo.
pause
