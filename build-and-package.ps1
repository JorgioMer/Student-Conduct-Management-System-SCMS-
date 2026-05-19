# SCMS Build and Package Automation Script
# Comprehensive build, test, and installer creation
# Run from project root directory

param(
    [string]$VersionType = "patch",
    [switch]$SkipTest = $false,
    [switch]$SkipInstallerBuild = $false,
    [switch]$DryRun = $false,
    [switch]$CreateBackup = $true
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = $scriptDir

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
    Write-Host "  OK $Message" -ForegroundColor Green
}

function Write-CustomError {
    param([string]$Message)
    Write-Host "  ERROR $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "  INFO $Message" -ForegroundColor Cyan
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

function Validate-Environment {
    Write-Section "Validating environment..."
    
    if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
        Write-CustomError "Python not found"
        return $false
    }
    Write-Success "Python installed"
    
    if (-not (Test-Path $ISCC_PATH)) {
        Write-CustomError "Inno Setup not found at $ISCC_PATH"
        return $false
    }
    Write-Success "Inno Setup found"
    
    if (-not (Test-Path $MAIN_PY)) {
        Write-CustomError "main.py not found at $MAIN_PY"
        return $false
    }
    Write-Success "main.py found"
    
    if (-not (Test-Path $SPEC_FILE)) {
        Write-CustomError "scms.spec not found at $SPEC_FILE"
        return $false
    }
    Write-Success "scms.spec found"
    
    if (-not (Test-Path $ISS_SCRIPT)) {
        Write-CustomError "SCMS-Installer.iss not found at $ISS_SCRIPT"
        return $false
    }
    Write-Success "SCMS-Installer.iss found"
    
    return $true
}

function Test-Application {
    Write-Section "Running application tests..."
    
    Write-Info "Checking Python syntax..."
    $pythonResult = python -m py_compile $MAIN_PY 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-CustomError "Syntax error in main.py"
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
        Write-Info "DRY RUN - Would execute: pyinstaller scms.spec"
        return $true
    }
    
    Set-Location $projectRoot
    python -m pip install pyinstaller --quiet
    if ($LASTEXITCODE -ne 0) {
        Write-CustomError "Failed to install PyInstaller"
        return $false
    }
    
    # Let PyInstaller output flow directly — don't pipe/filter it
    pyinstaller $SPEC_FILE
    $exitCode = $LASTEXITCODE
    
    if ($exitCode -ne 0) {
        Write-CustomError "PyInstaller build failed (exit code $exitCode)"
        return $false
    }
    
    # After pyinstaller runs, check both possible output locations
    $exeInFolder = Join-Path $DIST_DIR "SCMS\SCMS.exe"   # from COLLECT
    $exeSingleFile = Join-Path $DIST_DIR "SCMS.exe"        # intermediate

    if (Test-Path $exeInFolder) {
        $exePath = $exeInFolder
    } elseif (Test-Path $exeSingleFile) {
        $exePath = $exeSingleFile
    } else {
        Write-CustomError "SCMS.exe not found after build"
    return $false
}

    $exeSize = [Math]::Round((Get-Item $exePath).Length / 1MB, 2)
    Write-Success "Executable created: $exePath ($exeSize MB)"
    return $true
}

function Build-Installer {
    param([string]$Version)
    
    Write-Section "Building installer with Inno Setup..."
    Write-Info "Version: $Version"
    
    if ($DryRun) {
        Write-Info "DRY RUN - Would execute Inno Setup compilation"
        return $true
    }
    
    if (-not (Test-Path $ISCC_PATH)) {
        Write-CustomError "Inno Setup compiler not found"
        return $false
    }
    
    # Update version in ISS file
    $issContent = Get-Content $ISS_SCRIPT -Raw
    $issContent = $issContent -replace '#define MyAppVersion ".*?"', "#define MyAppVersion `"$Version`""
    Set-Content $ISS_SCRIPT -Value $issContent -Force
    
    Set-Location $projectRoot
    & $ISCC_PATH $ISS_SCRIPT
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0) {
        Write-CustomError "Inno Setup compilation failed (exit code $exitCode)"
        return $false
    }
    Write-Success "Inno Setup compilation successful"
    
    if ($LASTEXITCODE -ne 0) {
        Write-CustomError "Inno Setup compilation failed"
        return $false
    }
    
    $installerPath = Join-Path $projectRoot "SCMS-Setup-v${Version}.exe"
    if (-not (Test-Path $installerPath)) {
        Write-CustomError "Installer not found after compilation"
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
        Write-Info "DRY RUN - Would update version to $Version"
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
        Write-Info "DRY RUN - Would append changelog entry"
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
    
    Write-Header "BUILD AND PACKAGING SUMMARY"
    
    $status = if($Success) { "OK SUCCESS" } else { "FAILED" }
    $statusColor = if($Success) { "Green" } else { "Red" }
    Write-Host "Status:                $status" -ForegroundColor $statusColor
    Write-Host "Version:               $Version"
    Write-Host "Build Time:            ${BuildTime}s"
    $dateStr = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "Date:                  $dateStr"
    Write-Host ""
    
    if ($Success) {
        Write-Host "Deliverables:" -ForegroundColor Cyan
        Write-Host "  SCMS-Setup-v${Version}.exe" -ForegroundColor Yellow
        
        $exePath = Join-Path $DIST_DIR "SCMS.exe"
        if (Test-Path $exePath) {
            $exeSize = [Math]::Round((Get-Item $exePath).Length / 1MB, 2)
            Write-Host "  dist/SCMS/ (with SCMS.exe: $exeSize MB)" -ForegroundColor Yellow
        }
        
        Write-Host ""
        Write-Host "Next Steps:" -ForegroundColor Cyan
        Write-Host "  1. Test the installer on a clean machine"
        Write-Host "  2. Commit: git add . && git commit -m Release-v$Version"
        Write-Host "  3. Tag: git tag v$Version"
        Write-Host "  4. Push: git push origin main --tags"
        Write-Host "  5. Create GitHub Release with SCMS-Setup-v${Version}.exe"
    }
    
    Write-Host ""
}

function Main {
    $startTime = Get-Date
    
    Write-Header "SCMS BUILD AND PACKAGING AUTOMATION"
    $modeText = if($DryRun) { "DRY RUN (No changes)" } else { "NORMAL" }
    Write-Host "Mode: $modeText" -ForegroundColor Cyan
    Write-Host ""
    
    if (-not (Validate-Environment)) {
        Write-CustomError "Environment validation failed"
        exit 1
    }
    
    $currentVersion = Get-CurrentVersion
    Write-Section "Current version: $currentVersion"
    Write-Info "Version type for increment: $VersionType"
    
    $newVersion = Update-Version -CurrentVersion $currentVersion -VersionType $VersionType
    Write-Success "New version: $newVersion"
    
    if (-not $SkipTest) {
        if (-not (Test-Application)) {
            Write-CustomError "Application tests failed"
            exit 1
        }
    }
    
    Create-Backup -Version $currentVersion
    
    Clean-BuildArtifacts
    
    if (-not (Build-Executable -Version $newVersion)) {
        Write-CustomError "Failed to build executable"
        exit 1
    }
    
    if (-not $SkipInstallerBuild) {
        if (-not (Build-Installer -Version $newVersion)) {
            Write-CustomError "Failed to build installer"
            exit 1
        }
    }
    
    if (-not (Update-VersionFile -Version $newVersion)) {
        Write-CustomError "Failed to update version file"
        exit 1
    }
    
    if (-not (Update-Changelog -Version $newVersion)) {
        Write-CustomError "Failed to update changelog"
        exit 1
    }
    
    $endTime = Get-Date
    $buildTime = [int]($endTime - $startTime).TotalSeconds
    
    Show-BuildSummary -Version $newVersion -Success $true -BuildTime $buildTime
}

try {
    Main
} catch {
    Write-Host ""
    Write-CustomError "Fatal error: $_"
    exit 1
}
