# SCMS Installation Fix — Crash After Login

## Problem

Your SCMS application crashes on another PC after successfully entering credentials during login with the following sequence:

1. ✅ Installation completes without errors
2. ✅ Application starts and shows login window
3. ✅ User enters credentials
4. ✅ Loading screen appears
5. ❌ **App crashes after loading completes**

## Root Cause

The crash is caused by a **missing Microsoft Access Database Driver** on the target PC.

### Why This Happens

- SCMS uses an **Microsoft Access Database** (`.accdb` file) as its data store
- The Access driver is **NOT included by default** on Windows — it must be installed separately
- Even if Microsoft Office is installed, some Office versions don't include the database drivers
- When the app tries to initialize the database after login, `pyodbc` fails to connect
- Without proper error handling, this causes the application to crash silently

## Solution

### Step 1: Install Microsoft Access Database Engine

You need to install the **Microsoft Access Database Engine 2016**:

#### **For 64-bit Windows (most common):**
1. Download: [Microsoft Access Database Engine 2016 (64-bit)](https://www.microsoft.com/en-us/download/details.aspx?id=54920)
2. Click on `Download` → Select `AccessDatabaseEngine_X64.exe`
3. Run the installer and follow the on-screen instructions
4. **Restart your computer** after installation completes

#### **For 32-bit Windows:**
1. Download: [Microsoft Access Database Engine 2016 (32-bit)](https://www.microsoft.com/en-us/download/details.aspx?id=54920)
2. Click on `Download` → Select `AccessDatabaseEngine.exe`
3. Run the installer and follow the on-screen instructions
4. **Restart your computer** after installation completes

### Step 2: Verify Installation

After restarting:

1. Open SCMS-Setup-v1.0.15.exe again
2. Log in with your credentials (e.g., `admin` / `admin123`)
3. The loading screen should now complete successfully
4. Main dashboard should appear without crashes

### Alternative: Install Microsoft Office

If you prefer, you can also install **Microsoft Office** (any version from 2016+), which includes the database drivers by default.

## Error Message Improvements (New in This Update)

Starting with this version, SCMS will show **specific error messages** instead of silently crashing:

- **"Microsoft Access Driver is not installed"** → Install the driver above
- **"Database file not found"** → Check your installation directory
- **"Driver not properly installed"** → Reinstall the Microsoft Access Database Engine

## Updated Files

This fix updates the following files to provide better error handling:

1. **backend/db_connection.py**
   - Detects if Access driver is available before connection attempts
   - Provides user-friendly error messages
   - Better error classification

2. **ui/login_window.py**
   - Catches system configuration errors during login
   - Shows critical error dialogs instead of silent crashes
   - Handles errors during main window initialization

3. **main.py**
   - Catches errors during database initialization
   - Shows configuration error messages before login window

## Troubleshooting Checklist

If you still encounter issues after installing the database engine:

- [ ] **Restart your computer** after installing the driver (required!)
- [ ] Verify you downloaded the correct architecture (32-bit vs 64-bit)
  - Type "System Information" in Windows search
  - Look for "System Type" → Should match your download (x86 or x64)
- [ ] Ensure SCMS has write permissions to `%APPDATA%\SCMS` folder
  - This is where the database file is copied on first run
- [ ] Check your antivirus software — some antivirus blocks database access
  - Temporarily disable and try again
- [ ] For 64-bit Office on 32-bit Windows (rare): Use the 32-bit database engine instead

## How to Report Issues

If you still encounter crashes after following these steps:

1. Try to log in again to trigger the error message
2. Take a screenshot of the error dialog
3. Include:
   - Your Windows version (Settings → System → About)
   - Whether your Windows is 32-bit or 64-bit
   - Whether Microsoft Office is installed (and which version)
   - Any error messages shown

## Technical Details (For IT Support)

**Database Setup Process:**
1. SCMS uses `pyodbc` to connect to Access via ODBC driver
2. Template database: `SCMS\backend\database\SCMSDatabase.accdb`
3. User database: `%APPDATA%\SCMS\SCMSDatabase.accdb`
4. Connection string: `Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ={path}`

**Known Issues:**
- 32-bit Office on 64-bit Windows may require special driver configuration
- Windows N editions (no Media Features) may need additional packages
- Older builds of Windows 10 sometimes have driver conflicts

## Questions?

If you need additional help, check:
- The main [README.md](README.md)
- The [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- Or contact your system administrator
