# 🚀 SCMS GitHub Deployment Guide

Complete guide to set up automated releases and deployment on GitHub for the Student Conduct Management System.

## 📋 Quick Overview

This guide explains how to:
1. Set up automated builds on every commit
2. Create GitHub Releases with installers
3. Deploy updates automatically
4. Manage versions and releases

---

## ⚙️ Setup for Local Development

### 1. Prerequisites

```powershell
# Check Python
python --version  # Should be 3.13+

# Check PyInstaller
python -m pip install pyinstaller

# Check Inno Setup
# Download from: https://jrsoftware.org/isdl.php
# Install to: C:\Program Files (x86)\Inno Setup 6\
```

### 2. Clone Repository

```powershell
git clone https://github.com/yourusername/Student-Conduct-Management-System-SCMS-.git
cd Student-Conduct-Management-System-SCMS-
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

---

## 🔄 Release Workflow (Local)

### For Each Release

1. **Make and test changes** in SCMS folder
2. **Build and package** automatically:
   ```powershell
   .\build-and-package.ps1 -VersionType patch
   # Or: -VersionType minor, -VersionType major
   ```
3. **Test the installer** (optional but recommended):
   ```powershell
   # Run SCMS-Setup-v1.0.1.exe on clean machine
   ```
4. **Commit to Git**:
   ```powershell
   git add .
   git commit -m "Release v1.0.1 - Bug fixes and improvements"
   git tag v1.0.1
   git push origin main --tags
   ```
5. **Create GitHub Release**:
   - Go to GitHub → Releases
   - Click "Draft new release"
   - Tag: v1.0.1
   - Upload: SCMS-Setup-v1.0.1.exe
   - Add release notes from CHANGELOG.md
   - Publish

---

## 🤖 GitHub Actions CI/CD Setup (Optional)

Automate builds on every tag push.

### 1. Create Workflow File

Create `.github/workflows/build-release.yml`:

```yaml
name: Build Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: windows-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pyinstaller
      
      - name: Install Inno Setup
        run: choco install innosetup -y
      
      - name: Build executable and installer
        run: .\build-and-package.ps1 -SkipTest
        shell: powershell
      
      - name: Upload Release Assets
        uses: softprops/action-gh-release@v1
        with:
          files: SCMS-Setup-v*.exe
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### 2. Enable Actions

- Go to repository Settings
- Click Actions → General
- Enable "Allow all actions and reusable workflows"

### 3. Create Release via CI/CD

```bash
git tag v1.0.1
git push origin v1.0.1
```

GitHub Actions automatically:
- ✓ Builds executable
- ✓ Creates installer
- ✓ Uploads to release

---

## 📦 Distribution Methods

### Method 1: GitHub Releases (Easiest)
- Users download from: GitHub → Releases
- Direct `.exe` download
- Automatic updates via GitHub notifications

### Method 2: Direct Download
- Share `SCMS-Setup-v1.0.1.exe` link
- Users run installer
- Clean installation

### Method 3: Update Script (Auto-Update)
```powershell
# Create update-scms.ps1
$latestVersion = (Invoke-WebRequest "https://api.github.com/repos/user/repo/releases/latest" | ConvertFrom-Json).tag_name
$downloadUrl = "https://github.com/user/repo/releases/download/$latestVersion/SCMS-Setup-$latestVersion.exe"
Invoke-WebRequest -Uri $downloadUrl -OutFile "SCMS-Setup-$latestVersion.exe"
& "SCMS-Setup-$latestVersion.exe"
```

### Method 4: Network/School Deployment
```powershell
# Deploy to network share
Copy-Item "SCMS-Setup-v1.0.1.exe" "\\network\share\SCMS\"

# Create deployment script for IT
.\Install-SCMS.ps1 -InstallPath "C:\Program Files\SCMS"
```

---

## 📋 Version Management

### VERSION File
```
1.0.0
```
Automatically updated by build script.

### CHANGELOG.md
Auto-generated entries:
```markdown
## [1.0.1] - 2026-05-04

### Added
- New features

### Fixed
- Bug fixes
```

---

## 🔐 Best Practices

### Before Release
- [ ] Test on clean Windows machine
- [ ] Verify database connectivity
- [ ] Check all core features
- [ ] Review CHANGELOG entries
- [ ] Update documentation

### For Each Release
- [ ] Use semantic versioning (major.minor.patch)
- [ ] Tag with `v` prefix: `v1.0.1`
- [ ] Create descriptive commit messages
- [ ] Upload installer to GitHub Release
- [ ] Add release notes

### After Release
- [ ] Monitor for user issues
- [ ] Keep backups of all releases
- [ ] Plan next version improvements
- [ ] Communicate updates to users

---

## 🎯 Example Release Workflow

### Local Development (Day 1-7)
```powershell
# Work on features
# Test locally
# Commit: git add . && git commit -m "Add feature X"
```

### Release Day
```powershell
# 1. Build and package
.\build-and-package.ps1 -VersionType minor

# 2. Test installer on clean machine
# Run SCMS-Setup-v1.1.0.exe

# 3. Commit everything
git add .
git commit -m "Release v1.1.0 - Add new reporting features"

# 4. Create tag
git tag v1.1.0

# 5. Push to GitHub
git push origin main --tags

# 6. Create GitHub Release
# Go to GitHub → New Release
# Upload SCMS-Setup-v1.1.0.exe
```

### After Release
```powershell
# Users download from GitHub → Releases
# Run installer
# Application updates
```

---

## 📊 Repository Structure

```
Student-Conduct-Management-System-SCMS-/
├── .github/
│   └── workflows/
│       └── build-release.yml          ← CI/CD configuration
├── SCMS/
│   ├── main.py
│   ├── backend/
│   ├── ui/
│   └── ...
├── build-and-package.ps1              ← Build automation
├── BUILD_AUTOMATION.md                ← Build documentation
├── DEPLOYMENT_GUIDE.md                ← Installation guide
├── DEPLOYMENT_CHECKLIST.md            ← QA checklist
├── VERSION                            ← Current version
├── CHANGELOG.md                       ← Release history
├── scms.spec                          ← PyInstaller config
├── SCMS-Installer.iss                 ← Inno Setup config
└── requirements.txt                   ← Python dependencies
```

---

## 🔗 GitHub Release Links

### For Stable Releases
```
https://github.com/yourusername/repo/releases/latest
```

### For Specific Version
```
https://github.com/yourusername/repo/releases/download/v1.0.1/SCMS-Setup-v1.0.1.exe
```

### For Changelog
```
https://github.com/yourusername/repo/blob/main/CHANGELOG.md
```

---

## 🐛 Troubleshooting

### Build Script Issues

**Error: "Python not found"**
```powershell
# Add Python to PATH or use full path
C:\Python313\python.exe -m pip install pyinstaller
```

**Error: "Inno Setup not found"**
```powershell
# Verify installation path
Test-Path "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
```

**Error: "Database not found"**
```powershell
# Verify database exists
Test-Path "SCMS\backend\database\SCMSDatabase.accdb"
```

### GitHub Actions Issues

**Workflow doesn't run**
- Check Actions are enabled in Settings
- Verify tag format: `v*`
- Check GitHub token permissions

**Upload fails**
- Verify GITHUB_TOKEN secret exists
- Check release permissions
- Ensure installer file created

---

## 📞 Support

### Resources
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Inno Setup Documentation](https://jrsoftware.org/ishelp/)
- [PyInstaller Documentation](https://pyinstaller.org/)

### Common Questions

**Q: How often should I release?**
A: As needed. Minor version for features, patch for bug fixes.

**Q: What if build fails?**
A: Review error messages, fix issues, rebuild locally with `-DryRun` first.

**Q: Can I skip the installer build?**
A: Yes: `.\build-and-package.ps1 -SkipInstallerBuild`

**Q: How do users get updates?**
A: Manual download from GitHub Releases (v1) or automatic update script (v2).

---

## ✅ Checklist for GitHub Setup

- [ ] Create `.github/workflows/build-release.yml`
- [ ] Enable GitHub Actions in repository settings
- [ ] Test workflow by creating a tag locally
- [ ] Verify Actions runs successfully
- [ ] Confirm installer uploaded to release
- [ ] Test downloaded installer on clean machine
- [ ] Create release notes
- [ ] Share release link with users
- [ ] Monitor for issues
- [ ] Plan next release

---

## 📈 Next Steps

1. **Set up GitHub Actions** (optional but recommended)
2. **Test first release** with small group
3. **Get feedback** on installation process
4. **Automate updates** if needed
5. **Document for users** how to update

---

**Last Updated:** May 4, 2026  
**SCMS Version:** 1.0.0
