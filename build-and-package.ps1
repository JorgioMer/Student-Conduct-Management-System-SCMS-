# =============================================================================
#  SCMS Build and Package Automation Script
#  Comprehensive build, test, and installer creation
#  Run from project root directory
# =============================================================================

param(
    [string]$VersionType      = "patch",
    [switch]$SkipTest         = $false,
    [switch]$SkipInstallerBuild = $false,
    [switch]$DryRun           = $false,
    [switch]$CreateBackup     = $true
)

$ErrorActionPreference = "Stop"
$scriptDir   = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = $scriptDir

$SCMS_DIR     = Join-Path $projectRoot "SCMS"
$MAIN_PY      = Join-Path $SCMS_DIR    "main.py"
$DIST_DIR     = Join-Path $projectRoot "dist"
$BUILD_DIR    = Join-Path $projectRoot "build"
$SPEC_FILE    = Join-Path $projectRoot "scms.spec"
$ISS_SCRIPT   = Join-Path $projectRoot "SCMS-Installer.iss"
$VERSION_FILE = Join-Path $projectRoot "VERSION"
$CHANGELOG    = Join-Path $projectRoot "CHANGELOG.md"
$BACKUP_DIR   = Join-Path $projectRoot ".backups"
$ISCC_PATH    = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"

# FIX: Correct database source path (was missing from this script entirely)
$DB_SOURCE    = Join-Path $SCMS_DIR "backend\database\SCMSDatabase.accdb"
$DB_DEST_DIR  = Join-Path $DIST_DIR "SCMS\backend\database"
$DB_DEST      = Join-Path $DB_DEST_DIR "SCMSDatabase.accdb"

# ── Console helpers ────────────────────────────────────────────────────────

function Write-Header {
    param([string]$Message)
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host "  $Message" -ForegroundColor Cyan
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Section {
    param([string]$Message)
    Write-Host "> $Message" -ForegroundColor Yellow
}

function Write-Success {
    param([string]$Message)
    Write-Host "  OK  $Message" -ForegroundColor Green
}

function Write-CustomError {
    param([string]$Message)
    Write-Host "  ERROR  $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "  INFO  $Message" -ForegroundColor Cyan
}

function Write-Warn {
    param([string]$Message)
    Write-Host "  WARN  $Message" -ForegroundColor Magenta
}

# ── Version helpers ────────────────────────────────────────────────────────

function Get-CurrentVersion {
    if (Test-Path $VERSION_FILE) {
        return (Get-Content $VERSION_FILE).Trim()
    }
    return "1.0.0"
}

function Update-Version {
    param([string]$CurrentVersion, [string]$VersionType)

    $parts = $CurrentVersion.Split(".")
    $major = [int]$parts[0]
    $minor = [int]$parts[1]
    $patch = [int]$parts[2]

    switch ($VersionType) {
        "major" { $major++; $minor = 0; $patch = 0 }
        "minor" { $minor++; $patch = 0 }
        "patch" { $patch++ }
    }

    return "$major.$minor.$patch"
}

# ── Environment validation ─────────────────────────────────────────────────

function Validate-Environment {
    Write-Section "Validating environment..."

    if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
        Write-CustomError "Python not found in PATH"
        return $false
    }
    Write-Success "Python found"

    if (-not (Test-Path $ISCC_PATH)) {
        Write-CustomError "Inno Setup not found at: $ISCC_PATH"
        return $false
    }
    Write-Success "Inno Setup found"

    if (-not (Test-Path $MAIN_PY)) {
        Write-CustomError "main.py not found at: $MAIN_PY"
        return $false
    }
    Write-Success "main.py found"

    if (-not (Test-Path $SPEC_FILE)) {
        Write-CustomError "scms.spec not found at: $SPEC_FILE"
        return $false
    }
    Write-Success "scms.spec found"

    if (-not (Test-Path $ISS_SCRIPT)) {
        Write-CustomError "SCMS-Installer.iss not found at: $ISS_SCRIPT"
        return $false
    }
    Write-Success "SCMS-Installer.iss found"

    # FIX: Validate the database file exists before we even attempt a build.
    #      Without this check the build succeeds but the installed app has no DB.
    if (-not (Test-Path $DB_SOURCE)) {
        Write-CustomError "Database not found at: $DB_SOURCE"
        Write-CustomError "The build cannot produce a working package without the database."
        return $false
    }
    Write-Success "Database file found: SCMSDatabase.accdb"

    # FIX: Warn if the Microsoft Access ODBC driver is absent on this machine.
    #      Target PCs also need it or every slip query will silently return empty.
    $odbcDrivers = Get-OdbcDriver -Name "*Access*" -ErrorAction SilentlyContinue
    if (-not $odbcDrivers) {
        Write-Warn "Microsoft Access ODBC driver NOT found on this machine."
        Write-Warn "Target PCs must have the Access Database Engine installed:"
        Write-Warn "https://www.microsoft.com/en-us/download/details.aspx?id=54920"
    }
    else {
        Write-Success "Microsoft Access ODBC driver found"
    }

    return $true
}

# ── Tests ──────────────────────────────────────────────────────────────────

function Test-Application {
    Write-Section "Running application tests..."

    Write-Info "Checking Python syntax..."
    python -m py_compile $MAIN_PY 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-CustomError "Syntax error detected in main.py"
        return $false
    }
    Write-Success "Syntax validation passed"

    return $true
}

# ── Backup ─────────────────────────────────────────────────────────────────

function Create-Backup {
    param([string]$Version)

    if (-not $CreateBackup) { return }

    Write-Section "Creating backup of previous dist..."

    # Only backup if there is something to back up
    if (-not (Test-Path $DIST_DIR)) {
        Write-Info "No existing dist folder — skipping backup"
        return
    }

    if (-not (Test-Path $BACKUP_DIR)) {
        New-Item -ItemType Directory -Path $BACKUP_DIR -Force | Out-Null
    }

    $timestamp  = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupPath = Join-Path $BACKUP_DIR "SCMS_v${Version}_${timestamp}.zip"

    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [System.IO.Compression.ZipFile]::CreateFromDirectory($DIST_DIR, $backupPath)
    Write-Success "Backup created: $backupPath"
}

# ── Clean ──────────────────────────────────────────────────────────────────

function Clean-BuildArtifacts {
    Write-Section "Cleaning build artifacts..."

    if (Test-Path $BUILD_DIR) {
        Remove-Item $BUILD_DIR -Recurse -Force -ErrorAction SilentlyContinue
        Write-Success "Cleaned: build\"
    }

    if (Test-Path $DIST_DIR) {
        Remove-Item $DIST_DIR -Recurse -Force -ErrorAction SilentlyContinue
        Write-Success "Cleaned: dist\"
    }
}

# ── PyInstaller build ──────────────────────────────────────────────────────

function Build-Executable {
    param([string]$Version)

    Write-Section "Building executable with PyInstaller..."
    Write-Info "Version: $Version"

    if ($DryRun) {
        Write-Info "DRY RUN — would execute: pyinstaller scms.spec"
        return $true
    }

    Set-Location $projectRoot
    python -m pip install pyinstaller --quiet
    if ($LASTEXITCODE -ne 0) {
        Write-CustomError "Failed to install/verify PyInstaller"
        return $false
    }

    # Let PyInstaller output stream directly — piping/filtering it can
    # suppress progress and hide real error messages.
    pyinstaller $SPEC_FILE
    $exitCode = $LASTEXITCODE

    if ($exitCode -ne 0) {
        Write-CustomError "PyInstaller failed (exit code $exitCode)"
        return $false
    }

    # Check both possible output locations (COLLECT bundle vs single-file)
    $exeInFolder  = Join-Path $DIST_DIR "SCMS\SCMS.exe"
    $exeSingleFile = Join-Path $DIST_DIR "SCMS.exe"

    if (Test-Path $exeInFolder) {
        $exePath = $exeInFolder
    }
    elseif (Test-Path $exeSingleFile) {
        $exePath = $exeSingleFile
    }
    else {
        Write-CustomError "SCMS.exe not found after PyInstaller completed"
        return $false
    }

    $exeSize = [Math]::Round((Get-Item $exePath).Length / 1MB, 2)
    Write-Success "Executable created: $exePath ($exeSize MB)"

    # FIX: Copy the database into the dist package right after the build.
    #      This was entirely missing from the original script, which is why
    #      green (and all) slip records were absent on fresh installs.
    Write-Section "Copying database into dist package..."

    New-Item -ItemType Directory -Force -Path $DB_DEST_DIR | Out-Null
    Copy-Item -Force $DB_SOURCE $DB_DEST

    if (-not (Test-Path $DB_DEST)) {
        Write-CustomError "Database copy failed — file not found at: $DB_DEST"
        return $false
    }
    Write-Success "Database copied: dist\SCMS\backend\database\SCMSDatabase.accdb"

    return $true
}

# ── Inno Setup installer ───────────────────────────────────────────────────

function Build-Installer {
    param([string]$Version)

    Write-Section "Building installer with Inno Setup..."
    Write-Info "Version: $Version"

    if ($DryRun) {
        Write-Info "DRY RUN — would compile Inno Setup script"
        return $true
    }

    if (-not (Test-Path $ISCC_PATH)) {
        Write-CustomError "Inno Setup compiler not found at: $ISCC_PATH"
        return $false
    }

    # Patch version string in the .iss file
    $issContent = Get-Content $ISS_SCRIPT -Raw
    $issContent = $issContent -replace '#define MyAppVersion ".*?"', "#define MyAppVersion `"$Version`""
    Set-Content $ISS_SCRIPT -Value $issContent -Force

    Set-Location $projectRoot
    & $ISCC_PATH $ISS_SCRIPT
    $exitCode = $LASTEXITCODE

    # FIX: Original had a duplicate $LASTEXITCODE check after this point.
    #      The second check always passed because $LASTEXITCODE was already
    #      captured above. Only one check is needed.
    if ($exitCode -ne 0) {
        Write-CustomError "Inno Setup compilation failed (exit code $exitCode)"
        return $false
    }
    Write-Success "Inno Setup compilation successful"

    $installerPath = Join-Path $projectRoot "SCMS-Setup-v${Version}.exe"
    if (-not (Test-Path $installerPath)) {
        Write-CustomError "Installer not found after compilation: $installerPath"
        return $false
    }

    $installerSize = [Math]::Round((Get-Item $installerPath).Length / 1MB, 2)
    Write-Success "Installer created: SCMS-Setup-v${Version}.exe ($installerSize MB)"

    return $true
}

# ── Version / changelog ────────────────────────────────────────────────────

function Update-VersionFile {
    param([string]$Version)

    Write-Section "Updating version file..."

    if ($DryRun) {
        Write-Info "DRY RUN — would write version $Version to VERSION"
        return $true
    }

    Set-Content -Path $VERSION_FILE -Value $Version -Force
    Write-Success "VERSION updated to: $Version"

    return $true
}

function Update-Changelog {
    param([string]$Version)

    Write-Section "Updating CHANGELOG.md..."

    if ($DryRun) {
        Write-Info "DRY RUN — would prepend changelog entry for $Version"
        return $true
    }

    $date = Get-Date -Format "yyyy-MM-dd"
    $changelogEntry = @"
## [$Version] - $date

### Added
- Release build automation
- Automated version management
- Installer generation

### Changed
- Updated build process

### Fixed
- Various bug fixes

"@

    if (Test-Path $CHANGELOG) {
        $existing = Get-Content $CHANGELOG -Raw
        Set-Content -Path $CHANGELOG -Value ($changelogEntry + $existing) -Force
    }
    else {
        Set-Content -Path $CHANGELOG -Value $changelogEntry -Force
    }

    Write-Success "CHANGELOG.md updated"
    return $true
}

# ── Summary ────────────────────────────────────────────────────────────────

function Show-BuildSummary {
    param([string]$Version, [bool]$Success, [int]$BuildTime)

    Write-Header "BUILD AND PACKAGING SUMMARY"

    $statusText  = if ($Success) { "SUCCESS" } else { "FAILED" }
    $statusColor = if ($Success) { "Green"   } else { "Red"    }
    Write-Host "  Status     : $statusText"  -ForegroundColor $statusColor
    Write-Host "  Version    : $Version"
    Write-Host "  Build Time : ${BuildTime}s"
    Write-Host "  Date       : $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    Write-Host ""

    if ($Success) {
        Write-Host "Deliverables:" -ForegroundColor Cyan

        # FIX: Original checked dist\SCMS.exe (flat) which is wrong for a
        #      COLLECT-mode PyInstaller build. Correct path is dist\SCMS\SCMS.exe.
        $exePath = Join-Path $DIST_DIR "SCMS\SCMS.exe"
        if (Test-Path $exePath) {
            $exeSize = [Math]::Round((Get-Item $exePath).Length / 1MB, 2)
            Write-Host "  dist\SCMS\SCMS.exe  ($exeSize MB)" -ForegroundColor Yellow
        }

        if (-not $SkipInstallerBuild) {
            Write-Host "  SCMS-Setup-v${Version}.exe" -ForegroundColor Yellow
        }

        Write-Host ""
        Write-Host "Next Steps:" -ForegroundColor Cyan
        Write-Host "  1. Test the installer on a CLEAN machine (no dev tools)"
        Write-Host "     Verify the target has: Microsoft Access Database Engine"
        Write-Host "     https://www.microsoft.com/en-us/download/details.aspx?id=54920"
        Write-Host "  2. Commit  : git add . && git commit -m `"Release-v$Version`""
        Write-Host "  3. Tag     : git tag v$Version"
        Write-Host "  4. Push    : git push origin main --tags"
        if (-not $SkipInstallerBuild) {
            Write-Host "  5. Release : Upload SCMS-Setup-v${Version}.exe to GitHub Releases"
        }

        Write-Host ""
        Write-Host "  NOTE: Target PCs must have the Microsoft Access Database Engine" -ForegroundColor Magenta
        Write-Host "        installed or ALL slip records will appear empty." -ForegroundColor Magenta
    }

    Write-Host ""
}

# ── Entry point ────────────────────────────────────────────────────────────

function Main {
    $startTime = Get-Date

    Write-Header "SCMS BUILD AND PACKAGING AUTOMATION"
    Write-Host "  Mode    : $(if ($DryRun) { 'DRY RUN (no changes written)' } else { 'NORMAL' })" -ForegroundColor Cyan
    Write-Host "  Version : $(Get-CurrentVersion)  →  bump type: $VersionType" -ForegroundColor Cyan
    Write-Host ""

    if (-not (Validate-Environment)) {
        Write-CustomError "Environment validation failed — aborting."
        exit 1
    }

    $currentVersion = Get-CurrentVersion
    $newVersion     = Update-Version -CurrentVersion $currentVersion -VersionType $VersionType
    Write-Success "New version will be: $newVersion"

    if (-not $SkipTest) {
        if (-not (Test-Application)) {
            Write-CustomError "Tests failed — aborting."
            exit 1
        }
    }

    # FIX: Backup the OLD dist BEFORE cleaning it, not after.
    #      Original called Create-Backup after Clean-BuildArtifacts which meant
    #      the dist folder was already gone and the zip was always empty/skipped.
    Create-Backup -Version $currentVersion

    Clean-BuildArtifacts

    if (-not (Build-Executable -Version $newVersion)) {
        Write-CustomError "Executable build failed — aborting."
        exit 1
    }

    if (-not $SkipInstallerBuild) {
        if (-not (Build-Installer -Version $newVersion)) {
            Write-CustomError "Installer build failed — aborting."
            exit 1
        }
    }

    if (-not (Update-VersionFile -Version $newVersion)) {
        Write-CustomError "Failed to update VERSION file."
        exit 1
    }

    if (-not (Update-Changelog -Version $newVersion)) {
        Write-CustomError "Failed to update CHANGELOG.md."
        exit 1
    }

    $buildTime = [int]((Get-Date) - $startTime).TotalSeconds
    Show-BuildSummary -Version $newVersion -Success $true -BuildTime $buildTime
}

try {
    Main
}
catch {
    Write-Host ""
    Write-CustomError "Fatal error: $_"
    exit 1
}