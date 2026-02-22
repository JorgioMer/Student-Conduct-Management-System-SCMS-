# Student Conduct Management System (SCMS)
## Office of the Prefect — UI Prototype

---

## 🚀 Quick Start (Windows)

### 1. Install Python
Download Python 3.9+ from https://python.org (check "Add to PATH" during install)

### 2. Install PyQt5
Open Command Prompt and run:
```
pip install PyQt5
```

### 3. Run the System
Navigate to the project folder, then:
```
python main.py
```

---

## 🔐 Demo Login Credentials

| Username | Password   | Role  |
|----------|------------|-------|
| admin    | admin123   | Admin |
| staff    | staff123   | Staff |
| prefect  | prefect123 | Admin |

---

## 📁 Project Structure

```
SCMS/
├── main.py                  ← Entry point (run this)
├── ui/
│   ├── styles.py            ← Global colors & button styles
│   ├── components.py        ← Reusable widgets (cards, headers, dialogs)
│   ├── login_window.py      ← Login screen
│   ├── main_window.py       ← Main app window (sidebar + navigation)
│   └── pages/
│       ├── dashboard.py     ← Home dashboard
│       ├── green_slip.py    ← Green Slip (Dispensation + Excuse)
│       ├── pink_slip.py     ← Pink Slip (Once per semester)
│       ├── blue_slip.py     ← Blue Slip (Violations + Escalation)
│       ├── trackers.py      ← Combined record tracker + monthly summary
│       ├── reports.py       ← Reports & analytics
│       └── settings.py      ← Settings, users, system config
```

---

## 📋 Features Implemented (UI Only)

### ✅ Login Screen
- Username + password fields
- Error message display
- Demo credential hint
- Navigate to dashboard on success

### ✅ Dashboard
- Welcome banner with date
- Stat tiles (monthly slip counts)
- Quick-access slip type cards
- Recent activity table

### ✅ Green Slip Management
- **Dispensation Tab** — record student, date availed, number of days, auto-computed expiry
- **Excuse Tab** — record absence type, date, supporting documents
- **Tracker Tab** — searchable/filterable list of all green slips
- **Summary Tab** — stat tiles + chart placeholder

### ✅ Pink Slip Management
- **Record Tab** — one-per-semester enforcement notice, violation type, action taken
- Check student record before filing
- **Tracker Tab** — filtered list view
- **Summary Tab** — stat tiles + chart placeholder

### ✅ Blue Slip Management
- **File Blue Slip Tab** — violation type, severity level (1–4), escalation flag
- **Tracker Tab** — color-coded status, update/delete actions
- **Progress Tab** — step-by-step offense progression tracker per student
- **Summary Tab** — stat tiles + chart placeholder

### ✅ Record Trackers
- Combined all-slip view with filters
- Student lookup (individual history)
- Monthly summary view + chart placeholder

### ✅ Reports & Analytics
- Overview tab with monthly stat tiles + 3 chart placeholders
- Per-slip-type report tabs (Green/Pink/Blue)
- Student conduct summary / top records list

### ✅ Settings
- My Account / Change Password form
- User Management table with Add/Edit/Delete
- System configuration (school year, semester, escalation rules)
- Notification preferences (checkboxes)
- About page

---

## 🎨 Design Notes

- **Color theme**: Deep Navy (#1B2A4A) + Gold (#C9A84C) inspired by CJC OLSIS
- **Font**: Segoe UI (Windows system font — clean and readable)
- **Slip colors**: Green (#2E7D32), Pink (#C2185B), Blue (#1565C0)
- **Layout**: Sidebar navigation + stacked content pages
- All forms include: labels, input fields, action buttons, confirmation dialogs

---

## ⚠ Phase Note

> This is a **UI Prototype only**.
> No database connections, no data saving, no backend logic.
> All data shown is sample/demo data for layout demonstration.

---

*Developed for Software Engineering Course — CJC Office of the Prefect*
