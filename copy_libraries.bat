@echo off
REM Copy required libraries from Python 3.11 site-packages to dist folder

echo Copying export libraries to distribution...

REM Get the version number
set /p CURRENT_VERSION=<version.txt

REM Define source and destination
set SRC_BASE=C:\Users\devuser\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\site-packages
set DIST_FOLDER=dist\LiteFinPad_v%CURRENT_VERSION%\_internal

REM Create _internal folder if it doesn't exist
if not exist "%DIST_FOLDER%" (
    mkdir "%DIST_FOLDER%"
)

REM Copy xlsxwriter
echo Copying xlsxwriter...
if exist "%SRC_BASE%\xlsxwriter" (
    xcopy /E /I /Y "%SRC_BASE%\xlsxwriter" "%DIST_FOLDER%\xlsxwriter"
    echo xlsxwriter copied
) else (
    echo ERROR: xlsxwriter not found at %SRC_BASE%\xlsxwriter
)

REM Copy fpdf (old library, no PIL dependency)
echo Copying fpdf...
if exist "%SRC_BASE%\fpdf" (
    xcopy /E /I /Y "%SRC_BASE%\fpdf" "%DIST_FOLDER%\fpdf"
    echo fpdf copied
) else (
    echo ERROR: fpdf not found at %SRC_BASE%\fpdf
)

echo.
echo Library copying complete!

