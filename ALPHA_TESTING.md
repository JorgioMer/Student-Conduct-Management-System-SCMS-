# SCMS Alpha Testing Guide

## System Requirements
- Windows 10 or later
- Python 3.7+ (for source code testing)
- Microsoft Access Database Driver (for database connectivity)

## Installation & Running

### Method 1: From Source (Developers)
```bash
# Install dependencies
pip install -r requirements.txt

# Run application
cd SCMS
python main.py
```

### Method 2: Standalone Executable (End Users)
1. Download `SCMS.exe` from the releases folder
2. Double-click to launch
3. No installation required

## Testing Checklist
- [ ] Login window displays correctly
- [ ] Database connection works
- [ ] All menu items are accessible
- [ ] Forms submit data properly
- [ ] Reports generate successfully
- [ ] No crashes or errors in console

## Reporting Issues
Please report any bugs with:
- Exact steps to reproduce
- Screenshots if applicable
- Error messages from console
- Your system information (Windows version, Python version)

## Database Location
The application uses: `SCMS/backend/database/SMCSDatabase.accdb`
Ensure you have read/write access to this file.
