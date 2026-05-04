# SCMS Build & Package Automation Script
# Comprehensive build, test, and installer creation
# Run from project root directory

param(
    [string]$VersionType = "patch",  # patch, minor, major
    [switch]$SkipTest = $false,
    [switch]$SkipInstallerBuild = $false,
    [switch]$DryRun = $false,
    [switch]$CreateBackup = $true
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = $scriptDir

# ============================================================================
# CONFIGURATION
# ============================================================================

$SCMS_DIR = Join-Path $projectRoot "SCMS"
$MAIN_PY = Join-Path $SCMS_DIR "main.py"
$DIST_DIR = Join-Path $projectRoot "dist"
$BUILD_DIR = Join-Path $projectRoot "build"
$SPEC_FILE = Join-Path $projectRoot "scms.spec"
$ISS_SCRIPT = Join-Path $projectRoot "SCMS-Installer.iss"
$VERSION_FILE = Join-Path $projectRoot "VERSION"
$CHANGELOG = Join-Path $projectRoot "CHANGELOG.md"
$BACKUP_DIR = Join-Path $projectRoot ".backups"

$ISCC_PATH = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"

# ============================================================================
# FUNCTIONS
# ============================================================================

function Write-Header {
    param([string]$Message)
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║  $Message" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Section {
    param([string]$Message)
    Write-Host "➤ $Message" -ForegroundColor Yellow
}

function Write-Success {
    param([string]$Message)
    Write-Host "  ✓ $Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "  ✗ $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "  ℹ $Message" -ForegroundColor Cyan
}

function Get-CurrentVersion {
    if (Test-Path $VERSION_FILE) {
        return (Get-Content $VERSION_FILE).Trim()
    }
    return "1.0.0"
}

function Update-Version {
    param(
        [string]$CurrentVersion,
        [string]$VersionType
    )
    
    $parts = $CurrentVersion.Split('.')
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

function Validate-Environment {
    Write-Section "Validating environment..."
    
    # Check Python
    if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
        Write-Error "Python not found"
        return $false
    }
    Write-Success "Python installed"
    
    # Check Inno Setup
    if (-not (Test-Path $ISCC_PATH)) {
        Write-Error "Inno Setup not found at $ISCC_PATH"
        return $false
    }
    Write-Success "Inno Setup found"
    
    # Check main.py
    if (-not (Test-Path $MAIN_PY)) {
        Write-Error "main.py not found at $MAIN_PY"
        return $false
    }
    Write-Success "main.py found"
    
    # Check spec file
    if (-not (Test-Path $SPEC_FILE)) {
        Write-Error "scms.spec not found at $SPEC_FILE"
        return $false
    }
    Write-Success "scms.spec found"
    
    # Check ISS script
    if (-not (Test-Path $ISS_SCRIPT)) {
        Write-Error "SCMS-Installer.iss not found at $ISS_SCRIPT"
        return $false
    }
    Write-Success "SCMS-Installer.iss found"
    
    return $true
}

function Test-Application {
    Write-Section "Running application tests..."
    
    # Syntax check
    Write-Info "Checking Python syntax..."
    $pythonResult = python -m py_compile $MAIN_PY 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Syntax error in main.py"
        return $false
    }
    Write-Success "Syntax validation passed"
    
    return $true
}

function Create-Backup {
    param([string]$Version)
    
    if (-not $CreateBackup) { return }
    
    Write-Section "Creating backup..."
    
    if (-not (Test-Path $BACKUP_DIR)) {
        New-Item -ItemType Directory -Path $BACKUP_DIR -Force | Out-Null
    }
    
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupPath = Join-Path $BACKUP_DIR "SCMS_v${Version}_${timestamp}.zip"
    
    if (Test-Path $DIST_DIR) {
        Add-Type -AssemblyName System.IO.Compression.FileSystem
        [System.IO.Compression.ZipFile]::CreateFromDirectory($DIST_DIR, $backupPath)
        Write-Success "Backup created: $backupPath"
    }
}

function Clean-BuildArtifacts {
    Write-Section "Cleaning build artifacts..."
    
    if (Test-Path $BUILD_DIR) {
        Remove-Item $BUILD_DIR -Recurse -Force -ErrorAction SilentlyContinue
        Write-Success "Cleaned build directory"
    }
    
    if (Test-Path $DIST_DIR) {
        Remove-Item $DIST_DIR -Recurse -Force -ErrorAction SilentlyContinue
        Write-Success "Cleaned dist directory"
    }
}

function Build-Executable {
    param([string]$Version)
    
    Write-Section "Building executable with PyInstaller..."
    Write-Info "Version: $Version"
    
    if ($DryRun) {
        Write-Info "[DRY RUN] Would execute: pyinstaller scms.spec"
        return $true
    }
    
    Set-Location $projectRoot
    python -m pip install pyinstaller --quiet
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to install PyInstaller"
        return $false
    }
    
    pyinstaller $SPEC_FILE 2>&1 | ForEach-Object {
        if ($_ -match "error|Error|ERROR") {
            Write-Error $_
        } elseif ($_ -match "completed successfully") {
            Write-Success "PyInstaller build completed"
        }
    }
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "PyInstaller build failed"
        return $false
    }
    
    # Verify executable exists
    $exePath = Join-Path $DIST_DIR "SCMS.exe"
    if (-not (Test-Path $exePath)) {
        Write-Error "SCMS.exe not found after build"
        return $false
    }
    
    $exeSize = [Math]::Round((Get-Item $exePath).Length / 1MB, 2)
    Write-Success "Executable created: SCMS.exe ($exeSize MB)"
    
    return $true
}

function Build-Installer {
    param([string]$Version)
    
    Write-Section "Building installer with Inno Setup..."
    Write-Info "Version: $Version"
    
    if ($DryRun) {
        Write-Info "[DRY RUN] Would execute Inno Setup compilation"
        return $true
    }
    
    if (-not (Test-Path $ISCC_PATH)) {
        Write-Error "Inno Setup compiler not found"
        return $false
    }
    
    Set-Location $projectRoot
    & $ISCC_PATH $ISS_SCRIPT 2>&1 | ForEach-Object {
        if ($_ -match "Error|error|ERROR") {
            Write-Error $_
        } elseif ($_ -match "Successful compile") {
            Write-Success "Inno Setup compilation successful"
        }
    }
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Inno Setup compilation failed"
        return $false
    }
    
    # Verify installer exists
    $installerPath = Join-Path $projectRoot "SCMS-Setup-v${Version}.exe"
    if (-not (Test-Path $installerPath)) {
        Write-Error "Installer not found after compilation"
        return $false
    }
    
    $installerSize = [Math]::Round((Get-Item $installerPath).Length / 1MB, 2)
    Write-Success "Installer created: SCMS-Setup-v${Version}.exe ($installerSize MB)"
    
    return $true
}

function Update-VersionFile {
    param([string]$Version)
    
    Write-Section "Updating version information..."
    
    if ($DryRun) {
        Write-Info "[DRY RUN] Would update version to $Version"
        return $true
    }
    
    Set-Content -Path $VERSION_FILE -Value $Version -Force
    Write-Success "Version file updated: $Version"
    
    return $true
}

function Update-Changelog {
    param([string]$Version)
    
    Write-Section "Updating changelog..."
    
    if ($DryRun) {
        Write-Info "[DRY RUN] Would append changelog entry"
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
    } else {
        Set-Content -Path $CHANGELOG -Value $changelogEntry -Force
    }
    
    Write-Success "Changelog updated"
    return $true
}

function Show-BuildSummary {
    param(
        [string]$Version,
        [bool]$Success,
        [int]$BuildTime
    )
    
    Write-Header "BUILD & PACKAGING SUMMARY"
    
    Write-Host "Status:                $(if($Success) { "✓ SUCCESS" } else { "✗ FAILED" })" -ForegroundColor $(if($Success) { "Green" } else { "Red" })
    Write-Host "Version:               $Version"
    Write-Host "Build Time:            ${BuildTime}s"
    Write-Host "Date:                  $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    Write-Host ""
    
    if ($Success) {
        Write-Host "Deliverables:" -ForegroundColor Cyan
        Write-Host "  📄 SCMS-Setup-v${Version}.exe" -ForegroundColor Yellow
        
        $exePath = Join-Path $DIST_DIR "SCMS.exe"
        if (Test-Path $exePath) {
            $exeSize = [Math]::Round((Get-Item $exePath).Length / 1MB, 2)
            Write-Host "  📦 dist/SCMS/ (with SCMS.exe: $exeSize MB)" -ForegroundColor Yellow
        }
        
        Write-Host ""
        Write-Host "Next Steps:" -ForegroundColor Cyan
        Write-Host "  1. Test the installer on a clean machine"
        Write-Host "  2. Commit to GitHub: git add . && git commit -m 'Release v$Version'"
        Write-Host "  3. Tag release: git tag v$Version"
        Write-Host "  4. Push to GitHub: git push origin main --tags"
        Write-Host "  5. Create GitHub Release with SCMS-Setup-v${Version}.exe"
    }
    
    Write-Host ""
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

function Main {
    $startTime = Get-Date
    
    Write-Header "SCMS BUILD & PACKAGING AUTOMATION"
    Write-Host "Mode: $(if($DryRun) { "DRY RUN (No changes)" } else { "NORMAL" })" -ForegroundColor Cyan
    Write-Host ""
    
    # Step 1: Validate Environment
    if (-not (Validate-Environment)) {
        Write-Error "Environment validation failed"
        exit 1
    }
    
    # Step 2: Get current version
    $currentVersion = Get-CurrentVersion
    Write-Section "Current version: $currentVersion"
    Write-Info "Version type for increment: $VersionType"
    
    # Step 3: Calculate new version
    $newVersion = Update-Version -CurrentVersion $currentVersion -VersionType $VersionType
    Write-Success "New version: $newVersion"
    
    # Step 4: Test (optional)
    if (-not $SkipTest) {
        if (-not (Test-Application)) {
            Write-Error "Application tests failed"
            exit 1
        }
    }
    
    # Step 5: Create backup
    Create-Backup -Version $currentVersion
    
    # Step 6: Clean build artifacts
    Clean-BuildArtifacts
    
    # Step 7: Build executable
    if (-not (Build-Executable -Version $newVersion)) {
        Write-Error "Failed to build executable"
        exit 1
    }
    
    # Step 8: Build installer (optional)
    if (-not $SkipInstallerBuild) {
        if (-not (Build-Installer -Version $newVersion)) {
            Write-Error "Failed to build installer"
            exit 1
        }
    }
    
    # Step 9: Update version files
    if (-not (Update-VersionFile -Version $newVersion)) {
        Write-Error "Failed to update version file"
        exit 1
    }
    
    # Step 10: Update changelog
    if (-not (Update-Changelog -Version $newVersion)) {
        Write-Error "Failed to update changelog"
        exit 1
    }
    
    # Summary
    $endTime = Get-Date
    $buildTime = [int]($endTime - $startTime).TotalSeconds
    
    Show-BuildSummary -Version $newVersion -Success $true -BuildTime $buildTime
}

# Run main
try {
    Main
} catch {
    Write-Host ""
    Write-Error "Fatal error: $_"
    exit 1
}
