# ============================================================================
# LiteFinPad Release ZIP Creator
# ============================================================================
# Creates a release ZIP from the latest dist build with _internal folder
# automatically hidden upon extraction.
#
# Usage: .\create_release_zip.ps1
# ============================================================================

param(
    [string]$DistPath = ".\dist"
)

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "  LiteFinPad Release ZIP Creator" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

# Step 1: Find the latest build folder in dist/
Write-Host "[1/5] Finding latest build folder..." -ForegroundColor Yellow

if (-not (Test-Path $DistPath)) {
    Write-Host "ERROR: dist/ folder not found. Run a build first." -ForegroundColor Red
    exit 1
}

$buildFolders = Get-ChildItem -Path $DistPath -Directory | Where-Object { $_.Name -like "LiteFinPad_v*" }

if ($buildFolders.Count -eq 0) {
    Write-Host "ERROR: No build folders found in dist/" -ForegroundColor Red
    exit 1
}

$latestBuild = $buildFolders | Sort-Object LastWriteTime -Descending | Select-Object -First 1
$buildPath = $latestBuild.FullName
$buildName = $latestBuild.Name

Write-Host "      Found: $buildName" -ForegroundColor Green
Write-Host "      Path: $buildPath" -ForegroundColor Gray

# Step 2: Verify _internal folder exists
Write-Host "`n[2/5] Verifying build integrity..." -ForegroundColor Yellow

$internalPath = Join-Path $buildPath "_internal"
if (-not (Test-Path $internalPath)) {
    Write-Host "ERROR: _internal folder not found in build!" -ForegroundColor Red
    exit 1
}

$internalFiles = (Get-ChildItem -Path $internalPath -Recurse -File | Measure-Object).Count
Write-Host "      _internal folder: $internalFiles files" -ForegroundColor Green

# Check for user data that shouldn't be in release
$hasData = Test-Path (Join-Path $buildPath "data_*")
$hasLogs = Test-Path (Join-Path $buildPath "logs")
$hasSettings = Test-Path (Join-Path $buildPath "settings.ini")

if ($hasData -or $hasLogs -or $hasSettings) {
    Write-Host "      WARNING: User data found in build folder!" -ForegroundColor Red
    Write-Host "      Cleaning: data_*, logs/, settings.ini" -ForegroundColor Yellow
    
    Get-ChildItem -Path $buildPath -Directory -Filter "data_*" | Remove-Item -Recurse -Force
    if (Test-Path (Join-Path $buildPath "logs")) { Remove-Item (Join-Path $buildPath "logs") -Recurse -Force }
    if (Test-Path (Join-Path $buildPath "settings.ini")) { Remove-Item (Join-Path $buildPath "settings.ini") -Force }
    
    Write-Host "      Cleaned successfully" -ForegroundColor Green
}

# Optional: Add documentation files if they exist in project root
Write-Host "`n      Checking for optional documentation files..." -ForegroundColor Gray
$docFiles = @("README.md", "LICENSE")
$docsAdded = 0

foreach ($docFile in $docFiles) {
    $sourcePath = Join-Path (Get-Location) $docFile
    $destPath = Join-Path $buildPath $docFile
    
    if (Test-Path $sourcePath) {
        Copy-Item -Path $sourcePath -Destination $destPath -Force | Out-Null
        Write-Host "      Added: $docFile" -ForegroundColor Gray
        $docsAdded++
    }
}

if ($docsAdded -gt 0) {
    Write-Host "      Added $docsAdded documentation file(s) to release" -ForegroundColor Green
}

# Step 3: Ensure _internal is NOT hidden for zipping
Write-Host "`n[3/6] Preparing folders for compression..." -ForegroundColor Yellow

$internalAttribs = (Get-Item $internalPath -Force).Attributes
if ($internalAttribs -band [System.IO.FileAttributes]::Hidden) {
    Write-Host "      Temporarily unhiding _internal..." -ForegroundColor Gray
    attrib -h $internalPath
}

# Step 4: Create the ZIP file
Write-Host "`n[4/6] Creating release ZIP..." -ForegroundColor Yellow

# Kill any running instances
taskkill /F /IM "$buildName.exe" 2>$null | Out-Null
taskkill /F /IM "python.exe" 2>$null | Out-Null
Start-Sleep -Milliseconds 500

$zipName = "$buildName-Windows-x64.zip"
$zipPath = Join-Path $DistPath $zipName

if (Test-Path $zipPath) {
    Write-Host "      Removing old ZIP..." -ForegroundColor Gray
    Remove-Item $zipPath -Force
}

Write-Host "      Compressing files (this may take 10-15 seconds)..." -ForegroundColor Gray

# Use .NET compression for better control
Add-Type -AssemblyName System.IO.Compression.FileSystem

try {
    # Create ZIP from folder contents
    [System.IO.Compression.ZipFile]::CreateFromDirectory($buildPath, $zipPath, 'Optimal', $false)
    
    # Step 5: Set hidden attribute on _internal folder INSIDE the ZIP
    Write-Host "`n[5/6] Setting hidden attribute for _internal in ZIP..." -ForegroundColor Yellow
    
    # Open the ZIP for modification
    $zip = [System.IO.Compression.ZipFile]::Open($zipPath, 'Update')
    
    # Find all entries in _internal folder and set external attributes
    $hiddenFlag = [System.IO.FileAttributes]::Hidden -bor [System.IO.FileAttributes]::Directory
    
    foreach ($entry in $zip.Entries) {
        if ($entry.FullName -like "_internal*") {
            # Set Windows file attributes in ZIP (ExternalAttributes)
            # Format: (attributes << 16) for DOS/Windows attributes
            $entry.ExternalAttributes = ($hiddenFlag -as [int]) -shl 16
        }
    }
    
    $zip.Dispose()
    
    Write-Host "      Hidden attribute set successfully" -ForegroundColor Green
}
catch {
    Write-Host "ERROR: Failed to create ZIP: $_" -ForegroundColor Red
    exit 1
}

# Re-hide _internal locally
if ($internalAttribs -band [System.IO.FileAttributes]::Hidden) {
    attrib +h $internalPath
}

# Step 6: Verify and report
Write-Host "`n[6/6] Finalizing release package..." -ForegroundColor Yellow
Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "  Release Package Created Successfully!" -ForegroundColor Green
Write-Host "============================================`n" -ForegroundColor Cyan

$zipInfo = Get-Item $zipPath
$zipSizeMB = [math]::Round($zipInfo.Length / 1MB, 2)

Write-Host "File:     $zipName" -ForegroundColor White
Write-Host "Size:     $zipSizeMB MB" -ForegroundColor White
Write-Host "Location: dist\$zipName" -ForegroundColor White
Write-Host "`nNote: ZIP file created in dist/ folder for easy organization.`n" -ForegroundColor Cyan

# Optional: Test extraction to verify
$testExtract = Read-Host "Test extraction to verify hidden attribute? (y/N)"
if ($testExtract -eq 'y' -or $testExtract -eq 'Y') {
    $testPath = Join-Path (Get-Location) "temp_test_extract"
    
    Write-Host "`nExtracting to temp folder for testing..." -ForegroundColor Yellow
    
    if (Test-Path $testPath) { Remove-Item $testPath -Recurse -Force }
    Expand-Archive -Path $zipPath -DestinationPath $testPath -Force
    
    $extractedInternal = Join-Path $testPath "_internal"
    if (Test-Path $extractedInternal) {
        $extractedAttribs = (Get-Item $extractedInternal -Force).Attributes
        if ($extractedAttribs -band [System.IO.FileAttributes]::Hidden) {
            Write-Host "SUCCESS: _internal is HIDDEN after extraction!" -ForegroundColor Green
        } else {
            Write-Host "WARNING: _internal is NOT hidden after extraction" -ForegroundColor Yellow
            Write-Host "Note: Some ZIP tools may not preserve Windows attributes." -ForegroundColor Gray
        }
    }
    
    Remove-Item $testPath -Recurse -Force
    Write-Host "Test cleanup complete`n" -ForegroundColor Gray
}

Write-Host "Ready for GitHub release!`n" -ForegroundColor Green

