# =============================================================================
#  SCMS Build Script
#  Builds standalone executable using PyInstaller, copies database, packages RAR
#  Run from project root directory
# =============================================================================

Write-Host "================================" -ForegroundColor Cyan
Write-Host "  SCMS Build Script"             -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# FIX: Resolve project root once from the script's own location.
#      Using $MyInvocation.MyCommand.Definition is reliable whether the script
#      is dot-sourced, called by path, or run from a different working directory.
$scriptDir = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition

# ── PyInstaller check ──────────────────────────────────────────────────────

Write-Host "Checking for PyInstaller..." -ForegroundColor Yellow
python -m pip show pyinstaller 2>&1 | Out-Null

if ($LASTEXITCODE -ne 0) {
    Write-Host "PyInstaller not found. Installing..." -ForegroundColor Yellow
    python -m pip install pyinstaller
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Failed to install PyInstaller" -ForegroundColor Red
        exit 1
    }
}
Write-Host "✓ PyInstaller is ready." -ForegroundColor Green
Write-Host ""

# ── Paths ──────────────────────────────────────────────────────────────────

$distDir    = Join-Path $scriptDir "dist\SCMS"
$dbDestDir  = Join-Path $distDir   "backend\database"
$dbSource   = Join-Path $scriptDir "SCMS\backend\database\SCMSDatabase.accdb"
$dbDest     = Join-Path $dbDestDir "SCMSDatabase.accdb"
$specFile   = Join-Path $scriptDir "scms.spec"

# ── ODBC driver warning ────────────────────────────────────────────────────
# FIX: Warn early if the Access ODBC driver is missing.
#      Without it every slip query returns empty on the target PC — this is
#      the primary reason green (and all) slip records disappear after install.

$odbcDrivers = Get-OdbcDriver -Name "*Access*" -ErrorAction SilentlyContinue
if (-not $odbcDrivers) {
    Write-Host "⚠  Microsoft Access ODBC driver NOT detected on this machine." -ForegroundColor Magenta
    Write-Host "   Target PCs must install the Access Database Engine or slip" -ForegroundColor Magenta
    Write-Host "   records will be empty after deployment." -ForegroundColor Magenta
    Write-Host "   Download: https://www.microsoft.com/en-us/download/details.aspx?id=54920" -ForegroundColor Magenta
    Write-Host ""
}
else {
    Write-Host "✓ Microsoft Access ODBC driver found." -ForegroundColor Green
    Write-Host ""
}

# ── Validate database source ───────────────────────────────────────────────
# FIX: Fail immediately if the database file doesn't exist.
#      The original script only checked this after PyInstaller finished,
#      wasting build time and still producing a broken package.

Write-Host "Checking database source file..." -ForegroundColor Yellow
if (-not (Test-Path $dbSource)) {
    Write-Host "✗ Database not found: $dbSource" -ForegroundColor Red
    Write-Host "  Build aborted — cannot produce a working package without the database." -ForegroundColor Red
    exit 1
}
Write-Host "✓ Database found: SCMSDatabase.accdb" -ForegroundColor Green
Write-Host ""

# ── Clean previous dist ────────────────────────────────────────────────────
# FIX: Remove the old dist\SCMS folder before building so stale files from
#      previous runs do not persist (e.g. old database or removed modules).

Write-Host "Cleaning previous dist output..." -ForegroundColor Yellow
if (Test-Path $distDir) {
    Remove-Item -Recurse -Force $distDir -ErrorAction SilentlyContinue
    Write-Host "✓ Cleaned dist\SCMS\" -ForegroundColor Green
}
else {
    Write-Host "  (nothing to clean)" -ForegroundColor DarkGray
}
Write-Host ""

# ── PyInstaller build ──────────────────────────────────────────────────────

Write-Host "Building from: $scriptDir" -ForegroundColor Cyan
Write-Host ""
Write-Host "Building executable..." -ForegroundColor Yellow

Push-Location $scriptDir
pyinstaller $specFile

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "✗ Build failed!" -ForegroundColor Red
    Pop-Location
    exit 1
}

Write-Host ""
Write-Host "✓ Build successful!" -ForegroundColor Green
Write-Host ""

# ── Copy database into dist ────────────────────────────────────────────────

Write-Host "Copying database into dist package..." -ForegroundColor Yellow

New-Item -ItemType Directory -Force -Path $dbDestDir | Out-Null
Copy-Item -Force $dbSource $dbDest

# Verify the copy actually landed
if (-not (Test-Path $dbDest)) {
    Write-Host "✗ Database copy failed — file not found at: $dbDest" -ForegroundColor Red
    Pop-Location
    exit 1
}
Write-Host "✓ Database copied to: dist\SCMS\backend\database\" -ForegroundColor Green
Write-Host ""

# ── RAR packaging ─────────────────────────────────────────────────────────

Write-Host "Creating RAR package..." -ForegroundColor Yellow

$rarCmd = $null
$rarCandidate = Get-Command rar -ErrorAction SilentlyContinue
if ($rarCandidate) {
    $rarCmd = $rarCandidate.Source
}
else {
    foreach ($path in @(
        "C:\Program Files\WinRAR\rar.exe",
        "C:\Program Files (x86)\WinRAR\rar.exe"
    )) {
        if (Test-Path $path) { $rarCmd = $path; break }
    }
}

if ($rarCmd) {
    $rarOut = Join-Path $scriptDir "dist\SCMS.rar"

    # Remove stale RAR if it exists
    if (Test-Path $rarOut) { Remove-Item -Force $rarOut }

    # Archive the contents of dist\ so extracting SCMS.rar produces a clean
    # SCMS\ folder — not a nested dist\SCMS\ path.
    Push-Location (Join-Path $scriptDir "dist")
    & $rarCmd a -r "$rarOut" "SCMS\" | Out-Null
    $rarExit = $LASTEXITCODE
    Pop-Location

    if ($rarExit -eq 0) {
        Write-Host "✓ RAR package created: dist\SCMS.rar" -ForegroundColor Green
    }
    else {
        Write-Host "⚠ RAR packaging failed (exit code $rarExit)" -ForegroundColor Yellow
    }
}
else {
    Write-Host "⚠ WinRAR not found. Install WinRAR or add rar.exe to PATH." -ForegroundColor Yellow
}

# ── Cleanup build artifacts ────────────────────────────────────────────────

Write-Host ""
Write-Host "Cleaning up build artifacts..." -ForegroundColor Yellow
Remove-Item -Recurse -Force (Join-Path $scriptDir "build") -ErrorAction SilentlyContinue
Remove-Item -Force (Join-Path $scriptDir "scms.spec.bak")  -ErrorAction SilentlyContinue
Write-Host "✓ Cleanup complete" -ForegroundColor Green
Write-Host ""

# ── Stats ─────────────────────────────────────────────────────────────────

$exePath = Join-Path $distDir "SCMS.exe"
if (Test-Path $exePath) {
    $sizeMB = [Math]::Round((Get-Item $exePath).Length / 1MB, 2)
    Write-Host "Executable size : $sizeMB MB" -ForegroundColor Cyan
}

$rarPath = Join-Path $scriptDir "dist\SCMS.rar"
if (Test-Path $rarPath) {
    $rarMB = [Math]::Round((Get-Item $rarPath).Length / 1MB, 2)
    Write-Host "Package size    : $rarMB MB  (SCMS.rar)" -ForegroundColor Cyan
}

# FIX: This Pop-Location matches the Push-Location before pyinstaller above.
#      The original script had an unmatched Pop-Location at the end which would
#      throw a "stack empty" error (or pop an unintended directory in some shells).
Pop-Location

Write-Host ""
Write-Host "✓ Ready for alpha testing!" -ForegroundColor Green
Write-Host ""
Write-Host "  NOTE: Target PCs must have the Microsoft Access Database Engine" -ForegroundColor Magenta
Write-Host "        installed or ALL slip records will appear empty after install." -ForegroundColor Magenta
Write-Host "  Download: https://www.microsoft.com/en-us/download/details.aspx?id=54920" -ForegroundColor Magenta