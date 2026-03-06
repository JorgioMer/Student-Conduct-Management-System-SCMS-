# =============================================================================
#  SCMS — Settings Page
# =============================================================================
from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QFrame, QTabWidget, QWidget,
    QGridLayout, QGroupBox, QCheckBox, QTableWidget,
    QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from ui.styles import (
    NAVY, NAVY_DARK, GOLD, WHITE, OFF_WHITE,
    LIGHT_GRAY, MID_GRAY, TEXT_DARK, RED_ERR,
    btn_primary, btn_outline, btn_danger, btn_gold
)
from ui.components import (
    SectionTitle, SubTitle, Divider,
    FieldLabel, add_shadow, ConfirmDialog, InfoDialog
)
from ui.pages.base_page import BasePage


class SettingsPage(BasePage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        # FIX: removed emoji from title, added border: none + padding: 0 to labels
        header = QFrame()
        header.setFixedHeight(82)
        header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {NAVY_DARK}, stop:1 {NAVY}
                );
                border-radius: 12px;
                border-left: 6px solid {GOLD};
            }}
        """)
        add_shadow(header, blur=12, y=3, color=(0, 0, 0, 20))
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(24, 12, 24, 12)

        col = QVBoxLayout()
        col.setSpacing(2)

        t_lbl = QLabel("Settings & Administration")
        t_lbl.setFont(QFont("Segoe UI", 17, QFont.Bold))
        # FIX: border: none prevents the QFrame border from appearing around the label
        t_lbl.setStyleSheet(f"color: {GOLD}; background: transparent; border: none; padding: 0;")

        s_lbl = QLabel("System configuration, user management, and preferences")
        s_lbl.setFont(QFont("Segoe UI", 11))
        # FIX: bumped opacity to 0.85 for readability, border: none
        s_lbl.setStyleSheet("color: rgba(255,255,255,0.85); background: transparent; border: none; padding: 0;")

        col.addWidget(t_lbl)
        col.addWidget(s_lbl)
        h_lay.addLayout(col)
        self.main_layout.addWidget(header)

        # FIX: removed all emojis from tab labels
        tabs = QTabWidget()
        tabs.addTab(self._build_account_tab(), "  My Account ")
        tabs.addTab(self._build_users_tab(),   "  User Management ")
        tabs.addTab(self._build_system_tab(),  "  System Settings ")
        tabs.addTab(self._build_about_tab(),   "  About ")

        self.main_layout.addWidget(tabs)
        self.main_layout.addStretch()

    # ── Account tab ───────────────────────────────────────────────────────────
    def _build_account_tab(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background: {WHITE};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(16)

        lay.addWidget(SectionTitle("My Account — Change Password"))

        # FIX: replaced QGroupBox (which adds its own title border line) with a
        # clean QFrame + manual title label — eliminates the double-border look
        pw_frame = QFrame()
        pw_frame.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 1.5px solid {LIGHT_GRAY};
                border-radius: 10px;
            }}
        """)
        pw_outer = QVBoxLayout(pw_frame)
        pw_outer.setContentsMargins(20, 16, 20, 16)
        pw_outer.setSpacing(14)

        pw_title = QLabel("Update Password")
        pw_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        pw_title.setStyleSheet(f"color: {NAVY}; background: transparent; border: none;")
        pw_outer.addWidget(pw_title)

        g_lay = QGridLayout()
        g_lay.setSpacing(12)
        g_lay.setColumnStretch(1, 1)

        def lbl(text, req=False):
            return FieldLabel(text, required=req)

        g_lay.addWidget(lbl("Current Password", True), 0, 0)
        curr_pw = QLineEdit()
        curr_pw.setEchoMode(QLineEdit.Password)
        curr_pw.setPlaceholderText("Enter current password")
        curr_pw.setFixedHeight(38)
        g_lay.addWidget(curr_pw, 0, 1)

        g_lay.addWidget(lbl("New Password", True), 1, 0)
        new_pw = QLineEdit()
        new_pw.setEchoMode(QLineEdit.Password)
        new_pw.setPlaceholderText("Enter new password (min. 8 characters)")
        new_pw.setFixedHeight(38)
        g_lay.addWidget(new_pw, 1, 1)

        g_lay.addWidget(lbl("Confirm New Password", True), 2, 0)
        conf_pw = QLineEdit()
        conf_pw.setEchoMode(QLineEdit.Password)
        conf_pw.setPlaceholderText("Re-enter new password")
        conf_pw.setFixedHeight(38)
        g_lay.addWidget(conf_pw, 2, 1)

        pw_outer.addLayout(g_lay)
        lay.addWidget(pw_frame)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        save_pw = QPushButton("Update Password")
        save_pw.setStyleSheet(btn_primary())
        save_pw.setFixedHeight(40)
        save_pw.clicked.connect(lambda: InfoDialog(
            "Password Updated",
            "Your password has been updated successfully.",
            parent=self).exec_())
        btn_row.addWidget(save_pw)
        lay.addLayout(btn_row)

        lay.addWidget(Divider())
        lay.addWidget(SectionTitle("Account Information"))

        # FIX: cleaner info frame — labels get border: none explicitly
        info_frame = QFrame()
        info_frame.setStyleSheet(f"""
            QFrame {{
                background: {OFF_WHITE};
                border: 1px solid {LIGHT_GRAY};
                border-radius: 8px;
            }}
        """)
        i_lay = QVBoxLayout(info_frame)
        i_lay.setContentsMargins(20, 14, 20, 14)
        i_lay.setSpacing(8)

        for label, value in [
            ("Username:",   "admin"),
            ("Full Name:",  "Administrator"),
            ("Role:",       "Admin"),
            ("Last Login:", "November 20, 2024 — 8:30 AM"),
        ]:
            row_w = QWidget()
            row_w.setStyleSheet("background: transparent; border: none;")
            row_lay = QHBoxLayout(row_w)
            row_lay.setContentsMargins(0, 0, 0, 0)
            row_lay.setSpacing(8)

            lbl_w = QLabel(label)
            lbl_w.setFont(QFont("Segoe UI", 12))
            lbl_w.setFixedWidth(100)
            lbl_w.setStyleSheet(f"color: {MID_GRAY}; background: transparent; border: none;")

            val_w = QLabel(value)
            val_w.setFont(QFont("Segoe UI", 12, QFont.Bold))
            val_w.setStyleSheet(f"color: {NAVY}; background: transparent; border: none;")

            row_lay.addWidget(lbl_w)
            row_lay.addWidget(val_w)
            row_lay.addStretch()
            i_lay.addWidget(row_w)

        lay.addWidget(info_frame)
        lay.addStretch()
        return w

    # ── Users tab ─────────────────────────────────────────────────────────────
    def _build_users_tab(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background: {WHITE};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(14)

        lay.addWidget(SectionTitle("User Management"))
        lay.addWidget(SubTitle("Manage system users and their access roles"))

        top_row = QHBoxLayout()
        search = QLineEdit()
        # FIX: removed emoji from placeholder
        search.setPlaceholderText("  Search users...")
        search.setFixedHeight(38)

        # FIX: removed emoji from button
        add_btn = QPushButton("  Add New User")
        add_btn.setStyleSheet(btn_primary())
        add_btn.setFixedHeight(38)
        add_btn.clicked.connect(self._show_add_user)

        top_row.addWidget(search, 1)
        top_row.addWidget(add_btn)
        lay.addLayout(top_row)

        headers = ["Username", "Full Name", "Role", "Status", "Last Login", "Actions"]
        users = [
            ("admin",   "Administrator",    "Admin", "Active", "Nov 20, 2024"),
            ("staff",   "Office Staff",     "Staff", "Active", "Nov 19, 2024"),
            ("prefect", "Prefect Office",   "Admin", "Active", "Nov 18, 2024"),
            ("staff2",  "Mary Anne Santos", "Staff", "Active", "Nov 15, 2024"),
        ]

        from PyQt5.QtWidgets import QSizePolicy

        # Use 5 columns only — replace Actions column with two separate button columns
        table = QTableWidget(len(users), 7)
        table.setHorizontalHeaderLabels(
            ["Username", "Full Name", "Role", "Status", "Last Login", "Edit", "Delete"]
        )
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)
        table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Fixed)
        table.setColumnWidth(0, 100)
        table.setColumnWidth(2, 75)
        table.setColumnWidth(3, 75)
        table.setColumnWidth(4, 115)
        table.setColumnWidth(5, 80)   # Edit button column
        table.setColumnWidth(6, 80)   # Delete button column
        table.horizontalHeader().setStretchLastSection(False)
        table.setAlternatingRowColors(True)
        table.setStyleSheet(f"""
            QTableWidget {{
                alternate-background-color: #F5F8FF;
                background: {WHITE};
                border: 1px solid {LIGHT_GRAY};
                border-radius: 10px;
                outline: none;
            }}
        """)

        for r, (uname, name, role, status, last) in enumerate(users):
            for c, val in enumerate([uname, name, role, status, last]):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignCenter)
                table.setItem(r, c, item)

            edit_btn = QPushButton("Edit")
            edit_btn.setFixedHeight(32)
            edit_btn.setStyleSheet(btn_outline())

            del_btn = QPushButton("Delete")
            del_btn.setFixedHeight(32)
            del_btn.setStyleSheet(btn_danger())

            # Wrap each button in its own centered widget
            for col_idx, btn in [(5, edit_btn), (6, del_btn)]:
                cell_w = QWidget()
                cell_w.setStyleSheet("background: transparent;")
                cell_lay = QHBoxLayout(cell_w)
                cell_lay.setContentsMargins(6, 5, 6, 5)
                cell_lay.addWidget(btn)
                table.setCellWidget(r, col_idx, cell_w)

            table.setRowHeight(r, 44)

        table.setFixedHeight(258)
        lay.addWidget(table)
        lay.addStretch()
        return w

    def _show_add_user(self):
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QGridLayout
        dlg = QDialog(self)
        dlg.setWindowTitle("Add New User")
        dlg.setModal(True)
        dlg.setFixedWidth(420)
        dlg.setStyleSheet(f"background: {WHITE};")

        lay = QVBoxLayout(dlg)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(12)

        title = QLabel("Add New System User")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet(f"color: {NAVY}; border: none;")
        lay.addWidget(title)
        lay.addWidget(Divider())

        g = QGridLayout()
        g.setSpacing(10)
        g.setColumnStretch(1, 1)

        for row, (label, placeholder) in enumerate([
            ("Full Name", "Enter full name"),
            ("Username",  "Enter username"),
            ("Password",  "Enter password"),
            ("Role",      None),
        ]):
            lbl_w = FieldLabel(label, required=True)
            g.addWidget(lbl_w, row, 0)
            if placeholder:
                inp = QLineEdit()
                inp.setPlaceholderText(placeholder)
                inp.setFixedHeight(38)
                if label == "Password":
                    inp.setEchoMode(QLineEdit.Password)
                g.addWidget(inp, row, 1)
            else:
                role_cb = QComboBox()
                role_cb.addItems(["Staff", "Admin"])
                role_cb.setFixedHeight(38)
                g.addWidget(role_cb, row, 1)

        lay.addLayout(g)

        btn_row = QHBoxLayout()
        cancel = QPushButton("Cancel")
        cancel.setStyleSheet(btn_outline())
        cancel.setFixedHeight(38)
        cancel.clicked.connect(dlg.reject)

        # FIX: removed emoji from Save button
        save = QPushButton("Save User")
        save.setStyleSheet(btn_primary())
        save.setFixedHeight(38)
        save.clicked.connect(lambda: (dlg.accept(),
                                      InfoDialog("User Added",
                                                 "New user has been added successfully.",
                                                 parent=self).exec_()))
        btn_row.addWidget(cancel)
        btn_row.addWidget(save)
        lay.addLayout(btn_row)
        dlg.exec_()

    # ── System Settings tab ───────────────────────────────────────────────────
    def _build_system_tab(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background: {WHITE};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(16)

        lay.addWidget(SectionTitle("System Configuration"))

        # FIX: replaced QGroupBox with clean QFrame + title label for each section
        for section_title, items in [
            ("Academic Year Settings", [
                ("Current School Year:", ["2024–2025", "2023–2024"]),
                ("Current Semester:",    ["1st Semester", "2nd Semester"]),
            ]),
            ("Notifications & Alerts", [
                ("Low Green Slip threshold (per student):", ["1", "2", "3", "4", "5"]),
                ("Escalation trigger (Blue Slip repeat):",  ["2", "3", "4"]),
            ]),
        ]:
            sec_frame = QFrame()
            sec_frame.setStyleSheet(f"""
                QFrame {{
                    background: {WHITE};
                    border: 1.5px solid {LIGHT_GRAY};
                    border-radius: 8px;
                }}
            """)
            sec_outer = QVBoxLayout(sec_frame)
            sec_outer.setContentsMargins(20, 14, 20, 14)
            sec_outer.setSpacing(12)

            sec_title = QLabel(section_title)
            sec_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
            sec_title.setStyleSheet(f"color: {NAVY}; background: transparent; border: none;")
            sec_outer.addWidget(sec_title)

            g_lay = QGridLayout()
            g_lay.setSpacing(10)
            g_lay.setColumnStretch(0, 1)

            for row, (lbl_text, options) in enumerate(items):
                lbl_w = QLabel(lbl_text)
                lbl_w.setFont(QFont("Segoe UI", 12))
                lbl_w.setStyleSheet(f"color: {TEXT_DARK}; background: transparent; border: none;")
                cb = QComboBox()
                cb.addItems(options)
                cb.setFixedHeight(36)
                cb.setFixedWidth(220)
                g_lay.addWidget(lbl_w, row, 0)
                g_lay.addWidget(cb, row, 1)

            sec_outer.addLayout(g_lay)
            lay.addWidget(sec_frame)

        # Notification checkboxes — also a clean frame
        notif_frame = QFrame()
        notif_frame.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 1.5px solid {LIGHT_GRAY};
                border-radius: 8px;
            }}
        """)
        n_outer = QVBoxLayout(notif_frame)
        n_outer.setContentsMargins(20, 14, 20, 14)
        n_outer.setSpacing(10)

        notif_title = QLabel("Notification Preferences")
        notif_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        notif_title.setStyleSheet(f"color: {NAVY}; background: transparent; border: none;")
        n_outer.addWidget(notif_title)

        for label in [
            "Show alert when student exceeds 2 Green Slips per semester",
            "Warn before issuing 2nd Pink Slip (policy violation)",
            "Auto-flag Blue Slip as 'Escalated' on 3rd repeat offense",
            "Show monthly summary reminder on login",
        ]:
            cb = QCheckBox(label)
            cb.setFont(QFont("Segoe UI", 12))
            cb.setChecked(True)
            cb.setStyleSheet("background: transparent; border: none;")
            n_outer.addWidget(cb)

        lay.addWidget(notif_frame)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        # FIX: removed emoji from Save button
        save_btn = QPushButton("Save Settings")
        save_btn.setStyleSheet(btn_primary())
        save_btn.setFixedHeight(40)
        save_btn.clicked.connect(lambda: InfoDialog("Settings Saved",
                                                     "System settings have been saved.",
                                                     parent=self).exec_())
        btn_row.addWidget(save_btn)
        lay.addLayout(btn_row)
        lay.addStretch()
        return w

    # ── About tab ─────────────────────────────────────────────────────────────
    def _build_about_tab(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background: {WHITE};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(40, 30, 40, 30)
        lay.setSpacing(16)
        lay.setAlignment(Qt.AlignTop)

        # FIX: removed emoji icon, replaced with a clean styled text badge
        crest = QLabel("SCMS")
        crest.setFont(QFont("Segoe UI", 36, QFont.Bold))
        crest.setAlignment(Qt.AlignCenter)
        crest.setStyleSheet(f"""
            color: {WHITE};
            background: {NAVY};
            border-radius: 16px;
            border: none;
            padding: 16px 32px;
        """)
        crest.setFixedHeight(90)
        lay.addWidget(crest)

        for text, font_size, bold, color in [
            ("Student Conduct Management System", 20, True,  NAVY),
            ("SCMS v1.0 — UI Prototype",          13, False, MID_GRAY),
            ("Office of the Prefect — CJC",       14, True,  NAVY),
        ]:
            lbl = QLabel(text)
            lbl.setFont(QFont("Segoe UI", font_size, QFont.Bold if bold else QFont.Normal))
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet(f"color: {color}; background: transparent; border: none;")
            lay.addWidget(lbl)

        lay.addWidget(Divider())

        info_text = QLabel(
            "This system was developed as part of a Software Engineering course project.\n\n"
            "The SCMS is designed to help the Office of the Prefect efficiently manage\n"
            "student conduct records including Green Slips (Dispensation & Excuse),\n"
            "Pink Slips (Penalty — once per semester), and Blue Slips (Violations).\n\n"
            "Technology Stack:\n"
            "  Python 3.x\n"
            "  PyQt5 (User Interface)\n"
            "  MS Access Database (via pyodbc)\n"
            "  Windows OS"
        )
        info_text.setFont(QFont("Segoe UI", 12))
        info_text.setAlignment(Qt.AlignCenter)
        info_text.setStyleSheet(f"color: {TEXT_DARK}; background: transparent; border: none;")
        lay.addWidget(info_text)

        lay.addStretch()
        return w