# SCMS Build & Package Automation

Automated build, test, and installer creation script for the Student Conduct Management System.

## Quick Start

### Prerequisites
- Windows 10+ (64-bit)
- PowerShell 5.0+
- Python 3.13+
- Inno Setup 6 installed
- PyInstaller

### Basic Usage

Run from project root:

```powershell
# Increment patch version (1.0.0 → 1.0.1)
.\build-and-package.ps1

# Increment minor version (1.0.0 → 1.1.0)
.\build-and-package.ps1 -VersionType minor

# Increment major version (1.0.0 → 2.0.0)
.\build-and-package.ps1 -VersionType major

# Dry run (see what would happen without making changes)
.\build-and-package.ps1 -DryRun

# Skip installer build (just create executable)
.\build-and-package.ps1 -SkipInstallerBuild

# Skip application tests
.\build-and-package.ps1 -SkipTest
```

## What It Does

1. **Validates Environment**
   - Checks Python installation
   - Verifies Inno Setup installed
   - Confirms all necessary files exist

2. **Runs Tests**
   - Python syntax validation
   - Dependency checks

3. **Creates Backup**
   - Backs up previous dist folder
   - Timestamped archives in `.backups/` directory

4. **Cleans Build Artifacts**
   - Removes old build/ and dist/ folders
   - Fresh build each time

5. **Builds Executable**
   - Runs PyInstaller with scms.spec
   - Creates SCMS.exe with all dependencies
   - Size: ~69 MB

6. **Builds Installer**
   - Compiles Inno Setup script
   - Creates SCMS-Setup-v{VERSION}.exe
   - Professional Windows installer

7. **Updates Version**
   - Updates VERSION file
   - Updates CHANGELOG.md
   - Tracks build history

## Parameters

### -VersionType
Determines how to increment version number
- **patch** (default): 1.0.0 → 1.0.1
- **minor**: 1.0.0 → 1.1.0  
- **major**: 1.0.0 → 2.0.0

### -SkipTest
Skip application testing (default: false)
```powershell
.\build-and-package.ps1 -SkipTest
```

### -SkipInstallerBuild
Skip Inno Setup compiler step (default: false)
```powershell
.\build-and-package.ps1 -SkipInstallerBuild
```

### -DryRun
Preview what would happen without making changes
```powershell
.\build-and-package.ps1 -DryRun
```

### -CreateBackup
Enable/disable backup creation (default: true)
```powershell
.\build-and-package.ps1 -CreateBackup $false
```

## Output Files

### After Build Complete

```
project-root/
├── SCMS-Setup-v1.0.1.exe         ← Professional Installer
├── dist/
│   ├── SCMS.exe                  ← Standalone Executable
│   └── SCMS/
│       ├── backend/
│       │   └── database/
│       │       └── SCMSDatabase.accdb
│       └── [all dependencies]
├── build/                        ← PyInstaller build artifacts
├── .backups/
│   └── SCMS_v1.0.0_*.zip        ← Versioned backups
├── VERSION                       ← Current version number
└── CHANGELOG.md                 ← Update history
```

## GitHub Integration

### Setup GitHub Actions (Optional)

Create `.github/workflows/build-release.yml`:

```yaml
name: Build & Package

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      
      - name: Install Inno Setup
        run: choco install innosetup -y
      
      - name: Build & Package
        run: .\build-and-package.ps1 -SkipTest
      
      - name: Upload Installer
        uses: softprops/action-gh-release@v1
        with:
          files: SCMS-Setup-v*.exe
```

### Manual GitHub Release Workflow

1. **Make changes** to source code
2. **Run build script**:
   ```powershell
   .\build-and-package.ps1 -VersionType patch
   ```
3. **Test the installer** (optional)
4. **Commit to Git**:
   ```powershell
   git add .
   git commit -m "Release v1.0.1"
   git tag v1.0.1
   git push origin main --tags
   ```
5. **Create GitHub Release**:
   - Go to GitHub repository
   - Releases → Draft new release
   - Tag: v1.0.1
   - Upload: SCMS-Setup-v1.0.1.exe
   - Publish

## Troubleshooting

### PyInstaller not found
```powershell
python -m pip install pyinstaller
```

### Inno Setup not found
- Download from: https://jrsoftware.org/isdl.php
- Install to default location: `C:\Program Files (x86)\Inno Setup 6\`

### Script won't run
```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope CurrentUser
```

### Build fails with database error
- Verify `SCMS/backend/database/SCMSDatabase.accdb` exists
- Check file permissions
- Run script as Administrator

### Version file not found
Script creates `VERSION` file if missing. Manual creation:
```powershell
"1.0.0" | Out-File -FilePath VERSION -Encoding ASCII
```

## Advanced Usage

### Batch Release (Multiple Versions)
```powershell
# Build three consecutive patches
.\build-and-package.ps1 -VersionType patch
# ... test ...
.\build-and-package.ps1 -VersionType patch
# ... test ...
.\build-and-package.ps1 -VersionType patch
```

### CI/CD Integration
```powershell
# Automated build without prompts
$ErrorActionPreference = "Stop"
.\build-and-package.ps1 -VersionType patch -SkipTest
```

### Custom Installer Configuration
Edit `SCMS-Installer.iss` before running:
- Change company name
- Modify installer UI
- Update installation path
- Add custom branding

Then run:
```powershell
.\build-and-package.ps1
```

## File Descriptions

| File | Purpose |
|------|---------|
| VERSION | Current version number (read by build script) |
| CHANGELOG.md | Automated version history |
| scms.spec | PyInstaller configuration |
| SCMS-Installer.iss | Inno Setup installer script |
| build-and-package.ps1 | This automation script |

## Backup Management

Backups are created automatically in `.backups/` directory:
- Named: `SCMS_v{VERSION}_{TIMESTAMP}.zip`
- Organized by version
- Use for rollback if needed

To restore a backup:
```powershell
Remove-Item dist -Recurse -Force
Expand-Archive ".backups\SCMS_v1.0.0_20260504_100000.zip" -DestinationPath dist
```

## Performance

**Typical build time:** 2-5 minutes
- Environment validation: ~5 seconds
- PyInstaller compilation: 1-2 minutes
- Inno Setup compilation: 30-60 seconds
- File operations: ~10 seconds

## Support

For issues:
1. Check prerequisite installations
2. Review error messages in terminal
3. Try `.\build-and-package.ps1 -DryRun` to diagnose
4. Check GitHub Issues

## License

Same as SCMS project

---

**Last Updated:** May 4, 2026  
**Script Version:** 1.0.0
