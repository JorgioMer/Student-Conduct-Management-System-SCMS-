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

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "✗ Build failed!" -ForegroundColor Red
    Pop-Location  # FIX: must pop even on failure
    exit 1
}

Write-Host ""
Write-Host "✓ Build successful!" -ForegroundColor Green
Write-Host ""

$distDir   = "$scriptDir\dist\SCMS"
$dbDestDir = "$distDir\backend\database"

# ── FIX: Correct filename was SMCSDatabase (typo) → SCMSDatabase ──────────
$dbSource  = "$scriptDir\SCMS\backend\database\SCMSDatabase.accdb"
$dbDest    = "$dbDestDir\SCMSDatabase.accdb"

# ── Copy database template into dist ──────────────────────────────────────
Write-Host "Copying database to dist package..." -ForegroundColor Yellow

if (Test-Path $dbSource) {
    New-Item -ItemType Directory -Force -Path $dbDestDir | Out-Null
    Copy-Item -Force $dbSource $dbDest
    Write-Host "✓ Database copied to: dist\SCMS\backend\database\" -ForegroundColor Green
} else {
    Write-Host "✗ Database source not found: $dbSource" -ForegroundColor Red
    Write-Host "  Build cannot produce a working package without the database." -ForegroundColor Red
    Pop-Location
    exit 1  # FIX: treat missing DB as a hard failure, not a warning
}

# ── Verify the database actually landed in dist ────────────────────────────
if (-not (Test-Path $dbDest)) {
    Write-Host "✗ Database copy failed — file not found at: $dbDest" -ForegroundColor Red
    Pop-Location
    exit 1
}
Write-Host "✓ Database verified in dist package" -ForegroundColor Green
Write-Host ""

# ── RAR packaging ─────────────────────────────────────────────────────────
Write-Host "Creating RAR package..." -ForegroundColor Yellow

$rarCmd = Get-Command rar -ErrorAction SilentlyContinue
if (-not $rarCmd) {
    foreach ($candidate in @(
        "C:\Program Files\WinRAR\rar.exe",
        "C:\Program Files (x86)\WinRAR\rar.exe"
    )) {
        if (Test-Path $candidate) { $rarCmd = $candidate; break }
    }
} else {
    $rarCmd = $rarCmd.Source
}

if ($rarCmd) {
    $rarOut = "$scriptDir\dist\SCMS.rar"
    if (Test-Path $rarOut) { Remove-Item -Force $rarOut }

    # FIX: archive the CONTENTS of the dist folder so extracting SCMS.rar
    # produces a clean SCMS\ folder — not a nested dist\SCMS\ path
    Push-Location "$scriptDir\dist"
    & $rarCmd a -r "$rarOut" "SCMS\" | Out-Null
    Pop-Location

    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ RAR package created: dist\SCMS.rar" -ForegroundColor Green
    } else {
        Write-Host "⚠ RAR packaging failed (exit code $LASTEXITCODE)" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠ WinRAR not found. Install WinRAR or add rar.exe to PATH." -ForegroundColor Yellow
}

# ── Cleanup ───────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "Cleaning up build artifacts..." -ForegroundColor Yellow
Remove-Item -Recurse -Force "build"        -ErrorAction SilentlyContinue
Remove-Item -Force         "scms.spec.bak" -ErrorAction SilentlyContinue
Write-Host "✓ Cleanup complete" -ForegroundColor Green
Write-Host ""

# ── Stats ─────────────────────────────────────────────────────────────────
$exePath = "$distDir\SCMS.exe"
if (Test-Path $exePath) {
    $sizeMB = [Math]::Round((Get-Item $exePath).Length / 1MB, 2)
    Write-Host "Executable size : $sizeMB MB" -ForegroundColor Cyan
}

$rarPath = "$scriptDir\dist\SCMS.rar"
if (Test-Path $rarPath) {
    $rarMB = [Math]::Round((Get-Item $rarPath).Length / 1MB, 2)
    Write-Host "Package size    : $rarMB MB  (SCMS.rar)" -ForegroundColor Cyan
}

Pop-Location
Write-Host ""
Write-Host "Ready for alpha testing!" -ForegroundColor Green