# SCMS Build Script (Unified)
# Default: Quick build only
# With -Package: Full build + packaging + installer creation
# With -VersionType: Auto-increment version
# Run from project root directory

param(
    [switch]$Package = $false,
    [string]$VersionType = "patch",
    [switch]$SkipTest = $false,
    [switch]$SkipInstaller = $false,
    [switch]$CreateBackup = $false,
    [switch]$DryRun = $false
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = $scriptDir

# ──────────────────────────────────────────────────────────────────────────
# PATHS & CONFIGURATION
# ──────────────────────────────────────────────────────────────────────────
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

# ──────────────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ──────────────────────────────────────────────────────────────────────────

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
    Write-Host "  ✓ $Message" -ForegroundColor Green
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "  ✗ $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "  ℹ $Message" -ForegroundColor Cyan
}

function Write-Warning-Custom {
    param([string]$Message)
    Write-Host "  ⚠ $Message" -ForegroundColor Yellow
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
        default { }
    }
    
    return "$major.$minor.$patch"
}

# ──────────────────────────────────────────────────────────────────────────
# QUICK BUILD MODE (DEFAULT)
# ──────────────────────────────────────────────────────────────────────────

function Build-Quick {
    Write-Header "SCMS QUICK BUILD"
    
    # Install dependencies
    Write-Section "Installing Python dependencies..."
    python -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Custom "Failed to install dependencies"
        exit 1
    }
    Write-Success "Dependencies installed"
    Write-Host ""

    # Check PyInstaller
    Write-Section "Checking PyInstaller..."
    python -m pip install pyinstaller --quiet
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Custom "Failed to install PyInstaller"
        exit 1
    }
    Write-Success "PyInstaller ready"
    Write-Host ""

    # Build executable
    Write-Section "Building executable with PyInstaller..."
    Set-Location $projectRoot
    
    pyinstaller $SPEC_FILE
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Custom "Build failed!"
        exit 1
    }
    Write-Success "Build successful!"
    Write-Host ""

    # Copy database
    Write-Section "Copying database..."
    $distDir = "$projectRoot\dist\SCMS"
    $dbDestDir = "$distDir\backend\database"
    $dbSource = "$projectRoot\SCMS\backend\database\SCMSDatabase.accdb"
    $dbDest = "$dbDestDir\SCMSDatabase.accdb"

    if (Test-Path $dbSource) {
        New-Item -ItemType Directory -Force -Path $dbDestDir | Out-Null
        Copy-Item -Force $dbSource $dbDest
        Write-Success "Database copied to dist"
    } else {
        Write-Error-Custom "Database source not found: $dbSource"
        exit 1
    }
    
    if (-not (Test-Path $dbDest)) {
        Write-Error-Custom "Database copy failed"
        exit 1
    }
    Write-Host ""

    # Create RAR package
    Write-Section "Creating RAR package..."
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
        $rarOut = "$projectRoot\dist\SCMS.rar"
        if (Test-Path $rarOut) { Remove-Item -Force $rarOut }

        Push-Location "$projectRoot\dist"
        & $rarCmd a -r "$rarOut" "SCMS\" | Out-Null
        Pop-Location

        if ($LASTEXITCODE -eq 0) {
            Write-Success "RAR package created: dist\SCMS.rar"
        } else {
            Write-Warning-Custom "RAR packaging failed (exit code $LASTEXITCODE)"
        }
    } else {
        Write-Warning-Custom "WinRAR not found. Install to create RAR packages."
    }
    Write-Host ""

    # Cleanup
    Write-Section "Cleaning build artifacts..."
    Remove-Item -Recurse -Force "build" -ErrorAction SilentlyContinue
    Remove-Item -Force "scms.spec.bak" -ErrorAction SilentlyContinue
    Write-Success "Cleanup complete"
    Write-Host ""

    # Show stats
    Write-Section "Build Summary"
    $exePath = "$distDir\SCMS.exe"
    if (Test-Path $exePath) {
        $sizeMB = [Math]::Round((Get-Item $exePath).Length / 1MB, 2)
        Write-Host "  Executable: $sizeMB MB" -ForegroundColor Cyan
    }

    $rarPath = "$projectRoot\dist\SCMS.rar"
    if (Test-Path $rarPath) {
        $rarMB = [Math]::Round((Get-Item $rarPath).Length / 1MB, 2)
        Write-Host "  Package: $rarMB MB (SCMS.rar)" -ForegroundColor Cyan
    }
    Write-Host ""
    Write-Host "✓ Ready for testing!" -ForegroundColor Green
    Write-Host ""
}

# ──────────────────────────────────────────────────────────────────────────
# FULL PACKAGING MODE (-Package flag)
# ──────────────────────────────────────────────────────────────────────────

function Build-Full {
    $startTime = Get-Date
    
    Write-Header "SCMS FULL BUILD AND PACKAGING"
    $modeText = if($DryRun) { "DRY RUN (No changes)" } else { "NORMAL" }
    Write-Host "Mode: $modeText" -ForegroundColor Cyan
    Write-Host ""

    # Validate environment
    Write-Section "Validating environment..."
    if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
        Write-Error-Custom "Python not found"
        exit 1
    }
    Write-Success "Python installed"

    if (-not (Test-Path $MAIN_PY)) {
        Write-Error-Custom "main.py not found"
        exit 1
    }
    Write-Success "main.py found"

    if (-not (Test-Path $SPEC_FILE)) {
        Write-Error-Custom "scms.spec not found"
        exit 1
    }
    Write-Success "scms.spec found"

    if (-not $SkipInstaller) {
        if (-not (Test-Path $ISS_SCRIPT)) {
            Write-Error-Custom "SCMS-Installer.iss not found"
            exit 1
        }
        Write-Success "SCMS-Installer.iss found"

        if (-not (Test-Path $ISCC_PATH)) {
            Write-Error-Custom "Inno Setup not found at $ISCC_PATH"
            exit 1
        }
        Write-Success "Inno Setup found"
    }
    Write-Host ""

    # Get version info
    $currentVersion = Get-CurrentVersion
    Write-Section "Version Management"
    Write-Info "Current version: $currentVersion"
    Write-Info "Increment type: $VersionType"
    
    $newVersion = Update-Version -CurrentVersion $currentVersion -VersionType $VersionType
    Write-Success "New version: $newVersion"
    Write-Host ""

    # Test application
    if (-not $SkipTest) {
        Write-Section "Running application tests..."
        Write-Info "Checking Python syntax..."
        python -m py_compile $MAIN_PY 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Error-Custom "Syntax error in main.py"
            exit 1
        }
        Write-Success "Syntax validation passed"
        Write-Host ""
    }

    # Create backup
    if ($CreateBackup) {
        Write-Section "Creating backup..."
        if (-not (Test-Path $BACKUP_DIR)) {
            New-Item -ItemType Directory -Path $BACKUP_DIR -Force | Out-Null
        }
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $backupPath = Join-Path $BACKUP_DIR "SCMS_v${currentVersion}_${timestamp}.zip"
        
        if (Test-Path $DIST_DIR) {
            Add-Type -AssemblyName System.IO.Compression.FileSystem
            [System.IO.Compression.ZipFile]::CreateFromDirectory($DIST_DIR, $backupPath)
            Write-Success "Backup created: $backupPath"
        }
        Write-Host ""
    }

    # Clean artifacts
    Write-Section "Cleaning build artifacts..."
    if (Test-Path $BUILD_DIR) {
        Remove-Item $BUILD_DIR -Recurse -Force -ErrorAction SilentlyContinue
        Write-Success "Cleaned build directory"
    }
    if (Test-Path $DIST_DIR) {
        Remove-Item $DIST_DIR -Recurse -Force -ErrorAction SilentlyContinue
        Write-Success "Cleaned dist directory"
    }
    Write-Host ""

    # Build executable
    Write-Section "Building executable with PyInstaller..."
    if ($DryRun) {
        Write-Info "DRY RUN - Would execute: pyinstaller scms.spec"
    } else {
        Set-Location $projectRoot
        
        Write-Info "Installing dependencies from requirements.txt..."
        python -m pip install -r requirements.txt --quiet
        if ($LASTEXITCODE -ne 0) {
            Write-Error-Custom "Failed to install dependencies"
            exit 1
        }
        
        python -m pip install pyinstaller --quiet
        if ($LASTEXITCODE -ne 0) {
            Write-Error-Custom "Failed to install PyInstaller"
            exit 1
        }
        
        pyinstaller $SPEC_FILE
        if ($LASTEXITCODE -ne 0) {
            Write-Error-Custom "PyInstaller build failed"
            exit 1
        }

        # Verify executable
        $exeInFolder = Join-Path $DIST_DIR "SCMS\SCMS.exe"
        $exeSingleFile = Join-Path $DIST_DIR "SCMS.exe"

        if (Test-Path $exeInFolder) {
            $exePath = $exeInFolder
        } elseif (Test-Path $exeSingleFile) {
            $exePath = $exeSingleFile
        } else {
            Write-Error-Custom "SCMS.exe not found after build"
            exit 1
        }

        $exeSize = [Math]::Round((Get-Item $exePath).Length / 1MB, 2)
        Write-Success "Executable created: $exePath ($exeSize MB)"
    }
    Write-Host ""

    # Build installer
    if (-not $SkipInstaller) {
        Write-Section "Building installer with Inno Setup..."
        if ($DryRun) {
            Write-Info "DRY RUN - Would compile Inno Setup script"
        } else {
            # Update version in ISS file
            $issContent = Get-Content $ISS_SCRIPT -Raw
            $issContent = $issContent -replace '#define MyAppVersion ".*?"', "#define MyAppVersion `"$newVersion`""
            Set-Content $ISS_SCRIPT -Value $issContent -Force

            Set-Location $projectRoot
            & $ISCC_PATH $ISS_SCRIPT
            if ($LASTEXITCODE -ne 0) {
                Write-Error-Custom "Inno Setup compilation failed"
                exit 1
            }

            $installerPath = Join-Path $projectRoot "SCMS-Setup-v${newVersion}.exe"
            if (-not (Test-Path $installerPath)) {
                Write-Error-Custom "Installer not found after compilation"
                exit 1
            }

            $installerSize = [Math]::Round((Get-Item $installerPath).Length / 1MB, 2)
            Write-Success "Installer created: SCMS-Setup-v${newVersion}.exe ($installerSize MB)"
        }
        Write-Host ""
    }

    # Update version file
    Write-Section "Updating version information..."
    if ($DryRun) {
        Write-Info "DRY RUN - Would update version to $newVersion"
    } else {
        Set-Content -Path $VERSION_FILE -Value $newVersion -Force
        Write-Success "Version file updated: $newVersion"
    }
    Write-Host ""

    # Update changelog
    Write-Section "Updating changelog..."
    if ($DryRun) {
        Write-Info "DRY RUN - Would append changelog entry"
    } else {
        $date = Get-Date -Format "yyyy-MM-dd"
        $changelogEntry = @"
## [$newVersion] - $date

### Changed
- Updated build and packaging process

### Fixed
- Various improvements and fixes

"@
        
        if (Test-Path $CHANGELOG) {
            $existing = Get-Content $CHANGELOG -Raw
            Set-Content -Path $CHANGELOG -Value ($changelogEntry + $existing) -Force
        } else {
            Set-Content -Path $CHANGELOG -Value $changelogEntry -Force
        }
        Write-Success "Changelog updated"
    }
    Write-Host ""

    # Summary
    $buildTime = [Math]::Round(((Get-Date) - $startTime).TotalSeconds)
    Write-Header "BUILD AND PACKAGING SUMMARY"
    $status = "SUCCESS"
    Write-Host "Status:                $status" -ForegroundColor Green
    Write-Host "Version:               $newVersion"
    Write-Host "Build Time:            ${buildTime}s"
    Write-Host "Date:                  $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    Write-Host ""

    if (-not $DryRun) {
        Write-Host "Deliverables:" -ForegroundColor Cyan
        if (-not $SkipInstaller) {
            Write-Host "  → SCMS-Setup-v${newVersion}.exe" -ForegroundColor Yellow
        }
        
        $exePath = Join-Path $DIST_DIR "SCMS\SCMS.exe"
        if (Test-Path $exePath) {
            $exeSize = [Math]::Round((Get-Item $exePath).Length / 1MB, 2)
            Write-Host "  → dist/SCMS/ (SCMS.exe: $exeSize MB)" -ForegroundColor Yellow
        }

        Write-Host ""
        Write-Host "Next Steps:" -ForegroundColor Cyan
        Write-Host "  1. Test the installer on a clean machine"
        Write-Host "  2. Review changes: git diff"
        if (-not $SkipInstaller) {
            Write-Host "  3. Commit: git add . && git commit -m 'Release v$newVersion'"
            Write-Host "  4. Tag: git tag v$newVersion"
            Write-Host "  5. Push: git push origin main --tags"
            Write-Host "  6. Create GitHub Release with SCMS-Setup-v${newVersion}.exe"
        }
    }

    Write-Host ""
}

# ──────────────────────────────────────────────────────────────────────────
# MAIN ENTRY POINT
# ──────────────────────────────────────────────────────────────────────────

Write-Host ""
Write-Host "SCMS Build System" -ForegroundColor Cyan
Write-Host "==================" -ForegroundColor Cyan

if ($Package) {
    Build-Full
} else {
    Build-Quick
}