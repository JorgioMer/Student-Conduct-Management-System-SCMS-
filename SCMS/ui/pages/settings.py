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
        t_lbl = QLabel("⚙  Settings & Administration")
        t_lbl.setFont(QFont("Segoe UI", 17, QFont.Bold))
        t_lbl.setStyleSheet(f"color: {GOLD}; background: transparent;")
        s_lbl = QLabel("System configuration, user management, and preferences")
        s_lbl.setFont(QFont("Segoe UI", 11))
        s_lbl.setStyleSheet("color: rgba(255,255,255,0.65); background: transparent;")
        col = QVBoxLayout()
        col.addWidget(t_lbl)
        col.addWidget(s_lbl)
        h_lay.addLayout(col)
        self.main_layout.addWidget(header)

        tabs = QTabWidget()
        tabs.addTab(self._build_account_tab(),    "👤  My Account")
        tabs.addTab(self._build_users_tab(),      "👥  User Management")
        tabs.addTab(self._build_system_tab(),     "🔧  System Settings")
        tabs.addTab(self._build_about_tab(),      "ℹ  About")

        self.main_layout.addWidget(tabs)
        self.main_layout.addStretch()

    # ── Account tab ───────────────────────────────────────────────────────────
    def _build_account_tab(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background: {WHITE};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(20)

        lay.addWidget(SectionTitle("My Account — Change Password"))

        pw_group = QGroupBox("Update Password")
        pw_group.setFont(QFont("Segoe UI", 12, QFont.Bold))
        pw_group.setStyleSheet(f"""
            QGroupBox {{
                border: 1.5px solid {LIGHT_GRAY};
                border-radius: 10px;
                margin-top: 18px;
                padding: 16px;
                background: {WHITE};
                color: {NAVY};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 16px; top: -2px;
                padding: 0 8px;
                background: {WHITE};
            }}
        """)
        g_lay = QGridLayout(pw_group)
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

        lay.addWidget(pw_group)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        save_pw = QPushButton("🔐  Update Password")
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
        info_frame = QFrame()
        info_frame.setStyleSheet(f"""
            QFrame {{
                background: {OFF_WHITE};
                border: 1px solid {LIGHT_GRAY};
                border-radius: 8px;
            }}
        """)
        i_lay = QGridLayout(info_frame)
        i_lay.setContentsMargins(20, 14, 20, 14)
        i_lay.setSpacing(10)

        for i, (label, value) in enumerate([
            ("Username:", "admin"),
            ("Full Name:", "Administrator"),
            ("Role:", "Admin"),
            ("Last Login:", "November 20, 2024 — 8:30 AM"),
        ]):
            lbl_w = QLabel(label)
            lbl_w.setFont(QFont("Segoe UI", 12))
            lbl_w.setStyleSheet(f"color: {MID_GRAY}; background: transparent;")
            val_w = QLabel(value)
            val_w.setFont(QFont("Segoe UI", 12, QFont.Bold))
            val_w.setStyleSheet(f"color: {NAVY}; background: transparent;")
            i_lay.addWidget(lbl_w, i, 0)
            i_lay.addWidget(val_w, i, 1)

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
        search.setPlaceholderText("🔍  Search users...")
        search.setFixedHeight(38)

        add_btn = QPushButton("➕  Add New User")
        add_btn.setStyleSheet(btn_primary())
        add_btn.setFixedHeight(38)
        add_btn.clicked.connect(self._show_add_user)

        top_row.addWidget(search, 1)
        top_row.addWidget(add_btn)
        lay.addLayout(top_row)

        # Users table
        headers = ["Username", "Full Name", "Role", "Status", "Last Login", "Actions"]
        users = [
            ("admin",   "Administrator",    "Admin", "Active", "Nov 20, 2024"),
            ("staff",   "Office Staff",     "Staff", "Active", "Nov 19, 2024"),
            ("prefect", "Prefect Office",   "Admin", "Active", "Nov 18, 2024"),
            ("staff2",  "Mary Anne Santos", "Staff", "Active", "Nov 15, 2024"),
        ]

        table = QTableWidget(len(users), 6)
        table.setHorizontalHeaderLabels(headers)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
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

            # Action buttons in last column
            action_w = QWidget()
            a_lay = QHBoxLayout(action_w)
            a_lay.setContentsMargins(4, 2, 4, 2)
            a_lay.setSpacing(4)

            edit_btn = QPushButton("✏")
            edit_btn.setFixedSize(30, 28)
            edit_btn.setToolTip("Edit user")
            edit_btn.setStyleSheet(btn_outline())

            del_btn = QPushButton("🗑")
            del_btn.setFixedSize(30, 28)
            del_btn.setToolTip("Delete user")
            del_btn.setStyleSheet(btn_danger())

            a_lay.addWidget(edit_btn)
            a_lay.addWidget(del_btn)
            table.setCellWidget(r, 5, action_w)

        table.setFixedHeight(220)
        lay.addWidget(table)
        lay.addStretch()
        return w

    def _show_add_user(self):
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QGridLayout, QDialogButtonBox
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
        title.setStyleSheet(f"color: {NAVY};")
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

        save = QPushButton("💾  Save User")
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
        lay.setSpacing(20)

        lay.addWidget(SectionTitle("System Configuration"))

        for section_title, items in [
            ("Academic Year Settings", [
                ("Current School Year:", ["2024–2025", "2023–2024"]),
                ("Current Semester:",   ["1st Semester", "2nd Semester"]),
            ]),
            ("Notifications & Alerts", [
                ("Low Green Slip threshold (per student):", ["1", "2", "3", "4", "5"]),
                ("Escalation trigger (Blue Slip repeat):", ["2", "3", "4"]),
            ]),
        ]:
            group = QGroupBox(section_title)
            group.setFont(QFont("Segoe UI", 12, QFont.Bold))
            group.setStyleSheet(f"""
                QGroupBox {{
                    border: 1.5px solid {LIGHT_GRAY};
                    border-radius: 8px;
                    margin-top: 16px;
                    padding: 14px;
                    background: {WHITE};
                    color: {NAVY};
                }}
                QGroupBox::title {{
                    subcontrol-origin: margin;
                    left: 14px; top: -1px;
                    padding: 0 6px;
                    background: {WHITE};
                }}
            """)
            g_lay = QGridLayout(group)
            g_lay.setSpacing(10)
            g_lay.setColumnStretch(1, 1)

            for row, (lbl_text, options) in enumerate(items):
                lbl_w = QLabel(lbl_text)
                lbl_w.setFont(QFont("Segoe UI", 12))
                lbl_w.setStyleSheet(f"color: {TEXT_DARK}; background: transparent;")
                cb = QComboBox()
                cb.addItems(options)
                cb.setFixedHeight(36)
                cb.setFixedWidth(220)
                g_lay.addWidget(lbl_w, row, 0)
                g_lay.addWidget(cb, row, 1)

            lay.addWidget(group)

        # Notification checkboxes
        notif_group = QGroupBox("Notification Preferences")
        notif_group.setFont(QFont("Segoe UI", 12, QFont.Bold))
        notif_group.setStyleSheet(f"""
            QGroupBox {{
                border: 1.5px solid {LIGHT_GRAY};
                border-radius: 8px;
                margin-top: 16px;
                padding: 14px;
                background: {WHITE};
                color: {NAVY};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 14px; top: -1px;
                padding: 0 6px;
                background: {WHITE};
            }}
        """)
        n_lay = QVBoxLayout(notif_group)
        for label in [
            "Show alert when student exceeds 2 Green Slips per semester",
            "Warn before issuing 2nd Pink Slip (policy violation)",
            "Auto-flag Blue Slip as 'Escalated' on 3rd repeat offense",
            "Show monthly summary reminder on login",
        ]:
            cb = QCheckBox(label)
            cb.setFont(QFont("Segoe UI", 12))
            cb.setChecked(True)
            cb.setStyleSheet("background: transparent;")
            n_lay.addWidget(cb)
        lay.addWidget(notif_group)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        save_btn = QPushButton("💾  Save Settings")
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

        crest = QLabel("⚖")
        crest.setFont(QFont("Segoe UI", 56))
        crest.setAlignment(Qt.AlignCenter)
        crest.setStyleSheet(f"color: {NAVY}; background: transparent;")
        lay.addWidget(crest)

        for text, font_size, bold, color in [
            ("Student Conduct Management System", 20, True,  NAVY),
            ("SCMS v1.0 — UI Prototype",          13, False, MID_GRAY),
            ("Office of the Prefect — CJC",       14, True,  NAVY),
        ]:
            lbl = QLabel(text)
            lbl.setFont(QFont("Segoe UI", font_size, QFont.Bold if bold else QFont.Normal))
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet(f"color: {color}; background: transparent;")
            lay.addWidget(lbl)

        lay.addWidget(Divider())

        info_text = QLabel(
            "This system was developed as part of a Software Engineering course project.\n\n"
            "The SCMS is designed to help the Office of the Prefect efficiently manage\n"
            "student conduct records including Green Slips (Dispensation & Excuse),\n"
            "Pink Slips (Penalty — once per semester), and Blue Slips (Violations).\n\n"
            "Technology Stack:\n"
            "  • Python 3.x\n"
            "  • PyQt5 (User Interface)\n"
            "  • MS Access Database (via pyodbc)\n"
            "  • Windows OS"
        )
        info_text.setFont(QFont("Segoe UI", 12))
        info_text.setAlignment(Qt.AlignCenter)
        info_text.setStyleSheet(f"color: {TEXT_DARK}; background: transparent; line-height: 1.6;")
        lay.addWidget(info_text)

        lay.addStretch()
        return w
