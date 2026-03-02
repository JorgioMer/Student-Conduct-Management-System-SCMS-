# SCMS Build Script
# Builds standalone executable using PyInstaller

Write-Host "================================" -ForegroundColor Cyan
Write-Host "  SCMS Build Script" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if PyInstaller is installed
Write-Host "Checking for PyInstaller..." -ForegroundColor Yellow
$pyinstaller = python -m pip show pyinstaller 2>$null

if (-not $pyinstaller) {
    Write-Host "PyInstaller not found. Installing..." -ForegroundColor Yellow
    python -m pip install pyinstaller
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to install PyInstaller" -ForegroundColor Red
        exit 1
    }
}

Write-Host "PyInstaller is ready." -ForegroundColor Green
Write-Host ""

# Get script directory
$scriptDir = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition
Write-Host "Building from: $scriptDir" -ForegroundColor Cyan
Write-Host ""

# Run PyInstaller
Write-Host "Building executable..." -ForegroundColor Yellow
Push-Location $scriptDir
pyinstaller scms.spec

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✓ Build successful!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Executable location:" -ForegroundColor Cyan
    Write-Host "  dist/SCMS/SCMS.exe" -ForegroundColor Green
    Write-Host ""
    
    # Offer to clean up build folder
    Write-Host "Cleaning up build artifacts..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force "build" -ErrorAction SilentlyContinue
    Remove-Item -Force "scms.spec.bak" -ErrorAction SilentlyContinue
    Write-Host "✓ Cleanup complete" -ForegroundColor Green
    Write-Host ""
    
    # Show file size
    $exePath = "$scriptDir\dist\SCMS\SCMS.exe"
    if (Test-Path $exePath) {
        $size = (Get-Item $exePath).Length / 1MB
        Write-Host "Executable size: $([Math]::Round($size, 2)) MB" -ForegroundColor Cyan
    }
} else {
    Write-Host ""
    Write-Host "✗ Build failed!" -ForegroundColor Red
    exit 1
}

Pop-Location
Write-Host ""
Write-Host "Ready for alpha testing!" -ForegroundColor Green
