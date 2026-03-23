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

    # Ensure database template is present in the dist package
    $distDir = "$scriptDir\\dist\\SCMS"
    $dbSource = "$scriptDir\\SCMS\\backend\\database\\SMCSDatabase.accdb"
    $dbDestDir = "$distDir\\backend\\database"
    $dbDest = "$dbDestDir\\SMCSDatabase.accdb"

    if (Test-Path $dbSource) {
        New-Item -ItemType Directory -Force -Path $dbDestDir | Out-Null
        Copy-Item -Force $dbSource $dbDest
        Write-Host "✓ Database template added to dist package" -ForegroundColor Green
    } else {
        Write-Host "⚠ Database template not found at $dbSource" -ForegroundColor Yellow
    }

    # Create RAR package for easy transfer
    $rarCmd = Get-Command rar -ErrorAction SilentlyContinue
    if (-not $rarCmd) {
        $possibleRar = @(
            "C:\\Program Files\\WinRAR\\rar.exe",
            "C:\\Program Files (x86)\\WinRAR\\rar.exe"
        )
        foreach ($candidate in $possibleRar) {
            if (Test-Path $candidate) {
                $rarCmd = $candidate
                break
            }
        }
    } else {
        $rarCmd = $rarCmd.Source
    }

    if ($rarCmd) {
        $rarOut = "$scriptDir\\dist\\SCMS.rar"
        if (Test-Path $rarOut) {
            Remove-Item -Force $rarOut
        }
        & $rarCmd a -r $rarOut $distDir | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ RAR package created: dist/SCMS.rar" -ForegroundColor Green
        } else {
            Write-Host "⚠ RAR package creation failed (exit code $LASTEXITCODE)" -ForegroundColor Yellow
        }
    } else {
        Write-Host "⚠ WinRAR/rar.exe not found. Install WinRAR or add rar.exe to PATH to create the RAR package." -ForegroundColor Yellow
    }
    
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
