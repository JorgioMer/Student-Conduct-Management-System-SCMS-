# SCMS Deployment & Installation Guide

## System Status: ✅ READY FOR DEPLOYMENT

### Overview
The Student Conduct Management System (SCMS) has been successfully built, tested, and packaged for distribution. This document provides comprehensive deployment instructions for end users.

---

## 📦 Available Installation Methods

### Method 1: Professional Installer (Recommended)
**File:** `SCMS-Setup-v1.0.0.exe` (69.34 MB)

**For End Users:**
1. Download or receive `SCMS-Setup-v1.0.0.exe`
2. Double-click to run the installer
3. Follow the installation wizard
4. Choose installation location (default: `C:\Program Files\SCMS`)
5. Select optional desktop shortcut
6. Click "Finish" to complete installation
7. Application launches automatically (optional)

**Features:**
- Professional Windows installer
- Automatic Start Menu shortcuts
- Desktop icon option
- Uninstall support
- Backup of previous installations
- Clean installation wizard

---

### Method 2: PowerShell Installer Script
**File:** `Install-SCMS.ps1`

**For IT/System Administrators:**

**Prerequisites:**
- Windows PowerShell (built-in on all Windows systems)
- Administrator privileges
- Execution Policy set to allow scripts

**Installation:**
```powershell
# Run as Administrator:
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope CurrentUser -Force
Set-Location "C:\path\to\SCMS\folder"
.\Install-SCMS.ps1

# Or with custom installation path:
.\Install-SCMS.ps1 -InstallPath "C:\Custom\Path\SCMS"

# Create desktop icon:
.\Install-SCMS.ps1 -CreateDesktopIcon
```

**Features:**
- Scriptable installation (ideal for batch deployments)
- Custom installation paths
- Automatic Start Menu shortcuts
- Optional desktop icons
- Automatic uninstaller creation
- Installation validation
- Backup of previous versions

**Uninstall:**
```powershell
# Run the generated uninstall script:
PowerShell -ExecutionPolicy Bypass -File "C:\Program Files\SCMS\uninstall.ps1"
```

---

### Method 3: Portable Installation
**Files:** `dist\SCMS\` folder

**For Testing or Portable Use:**
1. Copy the entire `dist\SCMS` folder to desired location
2. Run `SCMS.exe` directly
3. No installation or setup required
4. Application runs from copied location

**Advantages:**
- No installation required
- Portable across USB drives
- No system modifications
- Can run from any location

---

### Method 4: Inno Setup Script
**File:** `SCMS-Installer.iss`

**For Customization:**
- Requires: [Inno Setup](https://jrsoftware.org/isdl.php)
- Modify `SCMS-Installer.iss` for custom branding
- Compile: Run Inno Setup IDE → Open .iss file → Build

---

## 🖥️ System Requirements

### Minimum Requirements
- **OS:** Windows 7 SP1 or later (64-bit)
- **RAM:** 2 GB
- **Disk Space:** 100 MB (for installation)
- **Database:** Microsoft Access 2010 or later (or ODBC driver)

### Recommended
- **OS:** Windows 10 or Windows 11
- **RAM:** 4 GB or more
- **Disk Space:** 500 MB
- **Internet:** Connection not required after installation

### No Additional Software Required
- Python is NOT required (bundled in executable)
- Database drivers are bundled
- All dependencies included

---

## ✅ Verification

### Test After Installation
1. **Launch Application:** Click Start Menu → SCMS or desktop icon
2. **Login:** Use default credentials or configured accounts
3. **Database Check:** Verify data loads correctly
4. **Create Test Record:** Add a test blue slip to confirm functionality
5. **Export Report:** Generate a test PDF report

### Troubleshooting
- **Won't Start:** Check Windows Event Viewer for error details
- **Database Error:** Verify database file is in `backend\database\` folder
- **Slow Startup:** Normal (first launch loads PyQt5 components)

---

## 📋 Installation Files Checklist

| File | Purpose | Size |
|------|---------|------|
| `SCMS-Setup-v1.0.0.exe` | Professional installer | 69.34 MB |
| `Install-SCMS.ps1` | PowerShell installer script | ~15 KB |
| `SCMS-Installer.iss` | Inno Setup script (customizable) | ~3 KB |
| `dist/SCMS/` | Portable installation folder | 1.25 GB |
| `README.md` | User documentation | - |

---

## 🔧 Deployment Scenarios

### Scenario 1: Single User Installation
→ Use **Professional Installer** or **Portable Installation**

### Scenario 2: School/District Network Deployment
→ Use **PowerShell Installer** with batch script
```powershell
# Deploy to multiple machines:
$computers = @("PC-001", "PC-002", "PC-003")
foreach ($computer in $computers) {
    Invoke-Command -ComputerName $computer -ScriptBlock {
        Set-ExecutionPolicy Bypass -Scope Process -Force
        & "\\network\share\Install-SCMS.ps1"
    }
}
```

### Scenario 3: USB Portable Deployment
→ Use **Portable Installation**
- Copy `dist\SCMS\` to USB drive
- Plug into any Windows PC
- Run `SCMS.exe` directly (no installation)

### Scenario 4: Custom Branding/Installer
→ Use **Inno Setup Script** (`SCMS-Installer.iss`)
- Modify version, company name, colors
- Add custom logo/icon
- Change installation directories
- Recompile with Inno Setup IDE

---

## 📝 Important Notes

### Database Location
- **Default:** `C:\Program Files\SCMS\backend\database\SCMSDatabase.accdb`
- **Portable:** `[InstallFolder]\backend\database\SCMSDatabase.accdb`
- Keep backed up regularly

### Uninstallation
- **Method 1:** Windows → Settings → Apps → SCMS → Uninstall
- **Method 2:** Run uninstall shortcut from Start Menu
- **Method 3:** PowerShell: `.\uninstall.ps1` (if using PowerShell installer)

### Updates & Reinstallation
- Installer automatically backs up previous versions
- Backup location: `C:\Program Files\SCMS.backup.[timestamp]`
- Old backups can be safely deleted

### Firewall & Security
- SCMS is a local application (no internet required)
- No firewall rules needed
- Database access is local only
- Safe to run on any Windows system

---

## 🚀 Quick Start After Installation

1. **Launch:** Open SCMS from Start Menu or desktop
2. **Login:** Use system administrator account
3. **Configuration:**
   - Set up officers/staff accounts
   - Configure school information
   - Import existing student data (if available)
4. **Usage:** Start recording conduct incidents
5. **Reporting:** Generate and export reports as needed

---

## 📞 Support

For issues or questions:
1. Check README.md in SCMS folder
2. Review error messages in application UI
3. Check Windows Event Viewer for system errors
4. Contact system administrator

---

## 🔐 Data Backup Recommendations

**Backup Schedule:**
- Daily: Backup database before end of school day
- Weekly: Full system backup
- Monthly: Archive to external storage

**Backup Location:**
```
C:\Program Files\SCMS\backend\database\SCMSDatabase.accdb
```

**Backup Tools:**
- Windows File History: Automatic backups
- Third-party backup software
- Network drive backup (for school deployments)

---

## Version Information
- **SCMS Version:** 1.0.0
- **Release Date:** May 4, 2026
- **Build Date:** May 4, 2026
- **Python Version:** 3.13.2 (bundled)
- **PyQt5 Version:** 5.15.9 (bundled)

---

*Installation guide created for SCMS v1.0.0 deployment*
