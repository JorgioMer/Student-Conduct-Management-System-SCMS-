# SCMS Installer Script
# PowerShell-based installer for Student Conduct Management System
# Run with Administrator privileges

param(
    [string]$InstallPath = "$env:ProgramFiles\SCMS",
    [switch]$CreateDesktopIcon = $false,
    [switch]$CreateStartMenuIcon = $true
)

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "This script requires Administrator privileges. Please run as Administrator." -ForegroundColor Red
    exit 1
}

Write-Host "╔════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   SCMS (Student Conduct Management System)║" -ForegroundColor Cyan
Write-Host "║              Installer v1.0.0              ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Define paths
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$sourceDir = Join-Path $scriptDir "dist"
$sourceExe = Join-Path $sourceDir "SCMS.exe"
$sourceScmsFolder = Join-Path $sourceDir "SCMS"
$databaseSource = Join-Path $sourceScmsFolder "backend\database\SCMSDatabase.accdb"

# Validate source files exist
Write-Host "🔍 Validating installation files..." -ForegroundColor Yellow
if (-not (Test-Path $sourceExe)) {
    Write-Host "✗ Error: SCMS.exe not found at $sourceExe" -ForegroundColor Red
    exit 1
}
if (-not (Test-Path $databaseSource)) {
    Write-Host "⚠ Warning: Database not found at $databaseSource" -ForegroundColor Yellow
}
Write-Host "✓ All source files validated" -ForegroundColor Green
Write-Host ""

# Create installation directory
Write-Host "📁 Creating installation directory: $InstallPath" -ForegroundColor Yellow
if (Test-Path $InstallPath) {
    Write-Host "⚠ Installation directory already exists. Backing up old version..." -ForegroundColor Yellow
    $backupPath = "$InstallPath.backup.$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Move-Item $InstallPath $backupPath -Force | Out-Null
    Write-Host "✓ Old version backed up to: $backupPath" -ForegroundColor Green
}
New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
Write-Host "✓ Installation directory created" -ForegroundColor Green
Write-Host ""

# Copy executable and supporting files
Write-Host "📦 Installing application files..." -ForegroundColor Yellow
try {
    Copy-Item $sourceExe -Destination $InstallPath -Force | Out-Null
    if (Test-Path $sourceScmsFolder) {
        Copy-Item "$sourceScmsFolder\*" -Destination $InstallPath -Recurse -Force | Out-Null
    }
    Write-Host "✓ Application files installed successfully" -ForegroundColor Green
} catch {
    Write-Host "✗ Error installing files: $_" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Create desktop shortcut if requested
if ($CreateDesktopIcon) {
    Write-Host "🔗 Creating desktop shortcut..." -ForegroundColor Yellow
    $desktopPath = [Environment]::GetFolderPath('Desktop')
    $shortcutPath = Join-Path $desktopPath "SCMS.lnk"
    
    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortCut($shortcutPath)
    $shortcut.TargetPath = Join-Path $InstallPath "SCMS.exe"
    $shortcut.WorkingDirectory = $InstallPath
    $shortcut.IconLocation = Join-Path $InstallPath "SCMS.exe"
    $shortcut.Save()
    
    Write-Host "✓ Desktop shortcut created" -ForegroundColor Green
    Write-Host ""
}

# Create Start Menu shortcut if requested
if ($CreateStartMenuIcon) {
    Write-Host "🔗 Creating Start Menu shortcut..." -ForegroundColor Yellow
    $appDataPath = [Environment]::GetFolderPath('ApplicationData')
    $startMenuPath = Join-Path $appDataPath "Microsoft\Windows\Start Menu\Programs\SCMS"
    
    if (-not (Test-Path $startMenuPath)) {
        New-Item -ItemType Directory -Path $startMenuPath -Force | Out-Null
    }
    
    $shortcutPath = Join-Path $startMenuPath "SCMS.lnk"
    
    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortCut($shortcutPath)
    $shortcut.TargetPath = Join-Path $InstallPath "SCMS.exe"
    $shortcut.WorkingDirectory = $InstallPath
    $shortcut.IconLocation = Join-Path $InstallPath "SCMS.exe"
    $shortcut.Save()
    
    Write-Host "✓ Start Menu shortcut created" -ForegroundColor Green
    Write-Host ""
}

# Create Uninstall script
Write-Host "🔧 Creating uninstaller..." -ForegroundColor Yellow
$uninstallScript = @"
# SCMS Uninstaller
`$installPath = "$InstallPath"

if (Test-Path `$installPath) {
    Remove-Item `$installPath -Recurse -Force
    Write-Host "✓ SCMS uninstalled successfully"
} else {
    Write-Host "✗ Installation directory not found"
}
`@

$uninstallPath = Join-Path $InstallPath "uninstall.ps1"
Set-Content -Path $uninstallPath -Value $uninstallScript -Force
Write-Host "✓ Uninstaller created" -ForegroundColor Green
Write-Host ""

# Display installation summary
Write-Host "╔════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║       Installation Complete!               ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Installation Summary:" -ForegroundColor Cyan
Write-Host "   Installation Path: $InstallPath"
$exeSize = (Get-Item (Join-Path $InstallPath "SCMS.exe")).Length / 1MB
Write-Host "   Executable Size: $([Math]::Round($exeSize, 2)) MB"
Write-Host ""
Write-Host "🚀 Quick Start:" -ForegroundColor Cyan
Write-Host "   Run: $InstallPath\SCMS.exe"
Write-Host ""
Write-Host "❌ To Uninstall:" -ForegroundColor Cyan
Write-Host "   PowerShell -ExecutionPolicy Bypass -File `"$uninstallPath`""
Write-Host ""
Write-Host "✓ SCMS is ready to use!" -ForegroundColor Green
Write-Host ""

# Optional: Launch application
$response = Read-Host "Do you want to launch SCMS now? (Y/n)"
if ($response -eq "" -or $response.ToUpper() -eq "Y") {
    & (Join-Path $InstallPath "SCMS.exe")
}
