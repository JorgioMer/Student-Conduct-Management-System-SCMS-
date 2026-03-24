# =============================================================================
#  SCMS — Settings Page
# =============================================================================
from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QFrame, QTabWidget, QWidget,
    QGridLayout, QGroupBox, QCheckBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QScrollArea
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QPainter, QPainterPath

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

# Backend imports for config
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from backend.config import load_config, save_config, get_school_years_list, add_school_year
from backend.db_accounts import (
    ensure_default_accounts,
    get_accounts,
    add_account,
    update_account,
    delete_account,
    get_account_by_username,
)


class SettingsPage(BasePage):
    def __init__(self, parent=None, current_user: dict = None):
        super().__init__(parent)
        self.settings_combos = {}
        self.settings_checkboxes = {}
        self.users_table = None
        # current_user: {"username": ..., "full_name": ..., "role": ..., "last_login": ...}
        self.current_user = current_user or {}
        self._ensure_accounts_ready()
        self._build()

    def _ensure_accounts_ready(self):
        try:
            ensure_default_accounts()
        except Exception:
            pass

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

        col = QVBoxLayout()
        col.setSpacing(2)

        t_lbl = QLabel("Settings & Administration")
        t_lbl.setFont(QFont("Segoe UI", 17, QFont.Bold))
        t_lbl.setStyleSheet(f"color: {GOLD}; background: transparent; border: none; padding: 0;")

        s_lbl = QLabel("System configuration, user management, and preferences")
        s_lbl.setFont(QFont("Segoe UI", 11))
        s_lbl.setStyleSheet("color: rgba(255,255,255,0.85); background: transparent; border: none; padding: 0;")

        col.addWidget(t_lbl)
        col.addWidget(s_lbl)
        h_lay.addLayout(col)
        self.main_layout.addWidget(header)

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
        save_pw.clicked.connect(lambda: self._change_password(curr_pw, new_pw, conf_pw))
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
        i_lay = QVBoxLayout(info_frame)
        i_lay.setContentsMargins(20, 14, 20, 14)
        i_lay.setSpacing(8)

        from backend.db_accounts import get_account_by_username
# Pull live data for the logged-in user
        uname = self.current_user.get("username", "admin")
        try:
            account_row = get_account_by_username(uname)
            # get_account_by_username returns (username, full_name, role, status, last_login)
            if account_row:
                uname_val      = account_row[0]
                fullname_val   = account_row[1]
                role_val       = account_row[3]
                raw_login      = account_row[5]
                if raw_login and hasattr(raw_login, "strftime"):
                    login_val = raw_login.strftime("%B %d, %Y — %I:%M %p")
                elif raw_login:
                    login_val = str(raw_login)
                else:
                    login_val = "No login recorded"
            else:
                uname_val, fullname_val, role_val, login_val = uname, "—", "—", "—"
        except Exception:
            uname_val, fullname_val, role_val, login_val = uname, "—", "—", "—"

        for label, value in [
        ("Username:",   uname_val),
        ("Full Name:",  fullname_val),
        ("Role:",       role_val),
        ("Last Login:", login_val),
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

    def _change_password(self, curr_pw_field, new_pw_field, conf_pw_field):
        from backend.db_accounts import get_account_by_username

        curr = curr_pw_field.text().strip()
        new  = new_pw_field.text().strip()
        conf = conf_pw_field.text().strip()

        if not curr or not new or not conf:
            InfoDialog("Missing Fields", "Please fill in all password fields.",
                   success=False, parent=self).exec_()
            return
        if new != conf:
            InfoDialog("Mismatch", "New password and confirmation do not match.",
                   success=False, parent=self).exec_()
            return
        if len(new) < 8:
            InfoDialog("Too Short", "New password must be at least 8 characters.",
                   success=False, parent=self).exec_()
            return

        uname = self.current_user.get("username", "admin")
        try:
            account_row = get_account_by_username(uname)
            if account_row and str(account_row[2]) != curr:   # [2] = accPass
                InfoDialog("Incorrect Password", "Current password is incorrect.",
                       success=False, parent=self).exec_()
                return

            from backend.db_accounts import update_account_password
            update_account_password(uname, new)

            curr_pw_field.clear()
            new_pw_field.clear()
            conf_pw_field.clear()
            InfoDialog("Password Updated",
                   "Your password has been updated successfully.",
                   parent=self).exec_()
        except Exception as e:
            InfoDialog("Error", f"Failed to update password: {str(e)}",
                   success=False, parent=self).exec_()
    # ── Users tab ─────────────────────────────────────────────────────────────
    def _build_users_tab(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background: {WHITE};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(14)

        lay.addWidget(SectionTitle("User Management"))
        lay.addWidget(SubTitle("Manage system users and their access roles"))

        is_admin = self.current_user.get("role", "").lower() == "admin"

        top_row = QHBoxLayout()
        self._user_search = QLineEdit()
        self._user_search.setPlaceholderText("  Search users...")
        self._user_search.setFixedHeight(38)
        self._user_search.textChanged.connect(self._apply_user_search)
        top_row.addWidget(self._user_search, 1)

        if is_admin:
            add_btn = QPushButton("  Add New User")
            add_btn.setStyleSheet(btn_primary())
            add_btn.setFixedHeight(38)
            add_btn.clicked.connect(self._show_add_user)
            top_row.addWidget(add_btn)

        lay.addLayout(top_row)

    # Show/hide Edit & Delete columns based on role
        col_count = 7 if is_admin else 5
        headers = ["Username", "Full Name", "Role", "Status", "Last Login"]
        if is_admin:
            headers += ["Edit", "Delete"]

        table = QTableWidget(0, col_count)
        table.setHorizontalHeaderLabels(headers)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.verticalHeader().setVisible(False)
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

        hdr = table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(1, QHeaderView.Stretch)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        if is_admin:
            hdr.setSectionResizeMode(5, QHeaderView.Fixed)
            hdr.setSectionResizeMode(6, QHeaderView.Fixed)
            table.setColumnWidth(5, 90)
            table.setColumnWidth(6, 90)

        table.setFixedHeight(300)
        self.users_table = table
        self._is_admin = is_admin
        self._refresh_users_table()
        lay.addWidget(self.users_table)

        if not is_admin:
            notice = QLabel("⚠  Only Admins can add, edit, or delete user accounts.")
            notice.setFont(QFont("Segoe UI", 11))
            notice.setStyleSheet(f"""
                color: #856404;
                background: #FFF3CD;
                border: 1px solid #FFEEBA;
                border-radius: 6px;
                padding: 8px 14px;
            """)
            lay.addWidget(notice)

        lay.addStretch()
        return w

    def _refresh_users_table(self):
        if not self.users_table:
            return

        try:
            self._all_user_rows = get_accounts()
        except Exception:
            self._all_user_rows = []

        self._render_users_table(self._all_user_rows)

    def _apply_user_search(self):
        text = self._user_search.text().strip().lower()
        if not text:
            self._render_users_table(self._all_user_rows)
            return
        filtered = [
            r for r in self._all_user_rows
            if text in str(r[0]).lower() or text in str(r[1]).lower() or text in str(r[2]).lower()
        ]
        self._render_users_table(filtered)

    def _render_users_table(self, rows):
        def _fmt_login(value):
            if not value:
                return "—"
            if hasattr(value, "strftime"):
                return value.strftime("%b %d, %Y %I:%M %p")
            return str(value)

        is_admin = getattr(self, "_is_admin", False)
        table = self.users_table
        table.setRowCount(len(rows))

        for r, (uname, name, role, status, last_login) in enumerate(rows):
            for c, val in enumerate([uname, name, role, status, _fmt_login(last_login)]):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignCenter)
            # Colour-code status
                if c == 3:
                    if str(val).lower() == "active":
                        item.setForeground(__import__('PyQt5.QtGui', fromlist=['QColor']).QColor("#155724"))
                        item.setBackground(__import__('PyQt5.QtGui', fromlist=['QColor']).QColor("#D4EDDA"))
                    else:
                        item.setForeground(__import__('PyQt5.QtGui', fromlist=['QColor']).QColor("#721C24"))
                        item.setBackground(__import__('PyQt5.QtGui', fromlist=['QColor']).QColor("#F8D7DA"))
                table.setItem(r, c, item)

            if is_admin:
                current_uname = self.current_user.get("username", "")

                edit_btn = QPushButton("Edit")
                edit_btn.setFixedSize(75, 32)
                edit_btn.setStyleSheet(btn_primary())
                edit_btn.clicked.connect(lambda _, u=uname, n=name, ro=role, s=status:
                                        self._show_edit_user(u, n, ro, s))

                del_btn = QPushButton("Delete")
                del_btn.setFixedSize(75, 32)
                del_btn.setStyleSheet(btn_danger())
            # Prevent admin from deleting their own account
                if uname == current_uname:
                    del_btn.setEnabled(False)
                    del_btn.setToolTip("You cannot delete your own account")
                else:
                    del_btn.clicked.connect(lambda _, u=uname: self._delete_user(u))

                for col_idx, btn in [(5, edit_btn), (6, del_btn)]:
                    cell_w = QWidget()
                    cell_w.setStyleSheet("background: transparent;")
                    cell_lay = QHBoxLayout(cell_w)
                    cell_lay.setContentsMargins(6, 4, 6, 4)
                    cell_lay.setAlignment(Qt.AlignCenter)
                    cell_lay.addWidget(btn)
                    table.setCellWidget(r, col_idx, cell_w)

            table.setRowHeight(r, 46)
    def _show_add_user(self):
        self._show_user_dialog()

    def _show_edit_user(self, username, full_name, role, status):
        self._show_user_dialog(
            edit_mode=True,
            username=username,
            full_name=full_name,
            role=role,
            status=status,
        )

    def _show_user_dialog(self, edit_mode=False, username="",
                        full_name="", role="Staff", status="Active"):
        from PyQt5.QtWidgets import QDialog
        dlg = QDialog(self)
        dlg.setWindowTitle("Edit User" if edit_mode else "Add New User")
        dlg.setModal(True)
        dlg.setFixedWidth(440)
        dlg.setStyleSheet(f"background: {WHITE};")

        lay = QVBoxLayout(dlg)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(12)

        title = QLabel("Edit User Account" if edit_mode else "Add New System User")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet(f"color: {NAVY}; border: none;")
        lay.addWidget(title)
        lay.addWidget(Divider())

        g = QGridLayout()
        g.setSpacing(10)
        g.setColumnStretch(1, 1)

    # Full Name
        g.addWidget(FieldLabel("Full Name", required=True), 0, 0)
        name_input = QLineEdit(full_name)
        name_input.setPlaceholderText("Enter full name")
        name_input.setFixedHeight(38)
        g.addWidget(name_input, 0, 1)

    # Username (read-only when editing)
        g.addWidget(FieldLabel("Username", required=True), 1, 0)
        user_input = QLineEdit(username)
        user_input.setPlaceholderText("Enter username")
        user_input.setFixedHeight(38)
        if edit_mode:
            user_input.setEnabled(False)
            user_input.setStyleSheet(f"background: {OFF_WHITE}; color: {MID_GRAY};")
        g.addWidget(user_input, 1, 1)

    # Password (optional when editing)
        pw_label = "New Password" if edit_mode else "Password"
        pw_hint  = "Leave blank to keep current" if edit_mode else "Enter password"
        g.addWidget(FieldLabel(pw_label, required=not edit_mode), 2, 0)
        pass_input = QLineEdit()
        pass_input.setPlaceholderText(pw_hint)
        pass_input.setEchoMode(QLineEdit.Password)
        pass_input.setFixedHeight(38)
        g.addWidget(pass_input, 2, 1)

    # Role
        g.addWidget(FieldLabel("Role", required=True), 3, 0)
        role_cb = QComboBox()
        role_cb.addItems(["Staff", "Admin"])
        role_cb.setFixedHeight(38)
        role_cb.setCurrentText(role if role in ["Staff", "Admin"] else "Staff")
        g.addWidget(role_cb, 3, 1)

    # Status (only shown when editing)
        status_cb = None
        if edit_mode:
            g.addWidget(FieldLabel("Status", required=True), 4, 0)
            status_cb = QComboBox()
            status_cb.addItems(["Active", "Inactive"])
            status_cb.setFixedHeight(38)
            status_cb.setCurrentText(status if status in ["Active", "Inactive"] else "Active")
            g.addWidget(status_cb, 4, 1)

        lay.addLayout(g)

        btn_row = QHBoxLayout()
        cancel = QPushButton("Cancel")
        cancel.setStyleSheet(btn_outline())
        cancel.setFixedHeight(38)
        cancel.clicked.connect(dlg.reject)

        save_lbl = "Save Changes" if edit_mode else "Save User"
        save = QPushButton(save_lbl)
        save.setStyleSheet(btn_primary())
        save.setFixedHeight(38)

        if edit_mode:
            save.clicked.connect(lambda: self._save_edit_user(
                dlg, username, name_input, pass_input, role_cb, status_cb
            ))
        else:
            save.clicked.connect(lambda: self._save_new_user(
                dlg, name_input, user_input, pass_input, role_cb
            ))

        btn_row.addWidget(cancel)
        btn_row.addWidget(save)
        lay.addLayout(btn_row)
        dlg.exec_()

    def _save_new_user(self, dlg, name_input, user_input, pass_input, role_cb):
        full_name = name_input.text().strip()
        username  = user_input.text().strip().lower()
        password  = pass_input.text().strip()
        role      = role_cb.currentText()

        if not full_name or not username or not password:
            InfoDialog("Input Required", "Please fill in all required fields.",
                    success=False, parent=self).exec_()
            return
        if len(password) < 6:
            InfoDialog("Weak Password", "Password must be at least 6 characters.",
                    success=False, parent=self).exec_()
            return
        try:
            if get_account_by_username(username):
                InfoDialog("Duplicate User", f"Username '{username}' already exists.",
                        success=False, parent=self).exec_()
                return
            add_account(username, full_name, password, role, status="Active")
        except Exception as e:
            InfoDialog("Error", f"Failed to add user: {str(e)}",
                    success=False, parent=self).exec_()
            return

        dlg.accept()
        self._refresh_users_table()
        InfoDialog("User Added", "New user has been added successfully.",
                parent=self).exec_()

    def _save_edit_user(self, dlg, username, name_input, pass_input, role_cb, status_cb):
        full_name  = name_input.text().strip()
        new_pass   = pass_input.text().strip()
        role       = role_cb.currentText()
        status     = status_cb.currentText() if status_cb else "Active"

        if not full_name:
            InfoDialog("Input Required", "Full name cannot be empty.",
                    success=False, parent=self).exec_()
            return
        try:
            update_account(username, full_name, role, status)
            if new_pass:
                if len(new_pass) < 6:
                    InfoDialog("Weak Password", "Password must be at least 6 characters.",
                            success=False, parent=self).exec_()
                    return
                from backend.db_accounts import update_account_password
                update_account_password(username, new_pass)
        except Exception as e:
            InfoDialog("Error", f"Failed to update user: {str(e)}",
                    success=False, parent=self).exec_()
            return

        dlg.accept()
        self._refresh_users_table()
        InfoDialog("User Updated", "User account has been updated successfully.",
                parent=self).exec_()

    def _delete_user(self, username):
        dlg = ConfirmDialog(
            "Confirm Delete",
            f"Are you sure you want to delete the account '{username}'?\n"
            "This action cannot be undone.",
            parent=self
        )
        if dlg.exec_():
            try:
                delete_account(username)
                self._refresh_users_table()
                InfoDialog("Deleted", f"Account '{username}' has been deleted.",
                        parent=self).exec_()
            except Exception as e:
                InfoDialog("Error", f"Failed to delete account: {str(e)}",
                        success=False, parent=self).exec_()

    # ── System Settings tab ───────────────────────────────────────────────────
    def _build_system_tab(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background: {WHITE};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(16)

        lay.addWidget(SectionTitle("System Configuration"))

        current_config = load_config()
        school_years = get_school_years_list()

        year_frame = QFrame()
        year_frame.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 1.5px solid {LIGHT_GRAY};
                border-radius: 8px;
            }}
        """)
        year_outer = QVBoxLayout(year_frame)
        year_outer.setContentsMargins(20, 14, 20, 14)
        year_outer.setSpacing(12)

        year_title = QLabel("Academic Year Settings")
        year_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        year_title.setStyleSheet(f"color: {NAVY}; background: transparent; border: none;")
        year_outer.addWidget(year_title)

        y_lay = QGridLayout()
        y_lay.setSpacing(10)
        y_lay.setColumnStretch(0, 1)

        lbl_w = QLabel("Current School Year:")
        lbl_w.setFont(QFont("Segoe UI", 12))
        lbl_w.setStyleSheet(f"color: {TEXT_DARK}; background: transparent; border: none;")

        year_combo = QComboBox()
        year_combo.addItems(school_years)
        year_combo.setFixedHeight(36)
        year_combo.setFixedWidth(220)
        current_year = current_config.get("school_year", school_years[0])
        index = year_combo.findText(current_year)
        if index >= 0:
            year_combo.setCurrentIndex(index)
        self.settings_combos["school_year"] = year_combo

        y_lay.addWidget(lbl_w, 0, 0)
        y_lay.addWidget(year_combo, 0, 1)

        add_year_lbl = QLabel("Add New School Year:")
        add_year_lbl.setFont(QFont("Segoe UI", 12))
        add_year_lbl.setStyleSheet(f"color: {TEXT_DARK}; background: transparent; border: none;")

        year_input = QLineEdit()
        year_input.setPlaceholderText("e.g., 2025–2026")
        year_input.setFixedHeight(36)
        year_input.setFixedWidth(220)

        add_year_btn = QPushButton("Add")
        add_year_btn.setStyleSheet(btn_primary())
        add_year_btn.setFixedHeight(36)
        add_year_btn.setFixedWidth(80)
        add_year_btn.clicked.connect(lambda: self._add_school_year(year_input, year_combo))

        y_lay.addWidget(add_year_lbl, 1, 0)
        y_lay.addWidget(year_input, 1, 1)
        y_lay.addWidget(add_year_btn, 1, 2)

        year_outer.addLayout(y_lay)
        lay.addWidget(year_frame)

        sem_frame = QFrame()
        sem_frame.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 1.5px solid {LIGHT_GRAY};
                border-radius: 8px;
            }}
        """)
        sem_outer = QVBoxLayout(sem_frame)
        sem_outer.setContentsMargins(20, 14, 20, 14)
        sem_outer.setSpacing(12)

        sem_title = QLabel("Semester Settings")
        sem_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        sem_title.setStyleSheet(f"color: {NAVY}; background: transparent; border: none;")
        sem_outer.addWidget(sem_title)

        s_lay = QGridLayout()
        s_lay.setSpacing(10)
        s_lay.setColumnStretch(0, 1)

        sem_lbl = QLabel("Current Semester:")
        sem_lbl.setFont(QFont("Segoe UI", 12))
        sem_lbl.setStyleSheet(f"color: {TEXT_DARK}; background: transparent; border: none;")
        sem_combo = QComboBox()
        sem_combo.addItems(["1st Semester", "2nd Semester"])
        sem_combo.setFixedHeight(36)
        sem_combo.setFixedWidth(220)
        current_sem = current_config.get("current_semester", "1st Semester")
        index = sem_combo.findText(current_sem)
        if index >= 0:
            sem_combo.setCurrentIndex(index)
        self.settings_combos["current_semester"] = sem_combo

        s_lay.addWidget(sem_lbl, 0, 0)
        s_lay.addWidget(sem_combo, 0, 1)

        sem_outer.addLayout(s_lay)
        lay.addWidget(sem_frame)

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
        n_outer.setSpacing(12)

        thresh_title = QLabel("Notifications & Alerts")
        thresh_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        thresh_title.setStyleSheet(f"color: {NAVY}; background: transparent; border: none;")
        n_outer.addWidget(thresh_title)

        thresh_lay = QGridLayout()
        thresh_lay.setSpacing(10)
        thresh_lay.setColumnStretch(0, 1)

        thresh_items = [
            ("Low Green Slip threshold (per student):", ["1", "2", "3", "4", "5"], "green_slip_threshold"),
            ("Escalation trigger (Blue Slip repeat):",  ["2", "3", "4"], "escalation_trigger"),
        ]

        for row, (lbl_text, options, config_key) in enumerate(thresh_items):
            lbl = QLabel(lbl_text)
            lbl.setFont(QFont("Segoe UI", 12))
            lbl.setStyleSheet(f"color: {TEXT_DARK}; background: transparent; border: none;")
            cb = QComboBox()
            cb.addItems(options)
            cb.setFixedHeight(36)
            cb.setFixedWidth(220)
            current_value = current_config.get(config_key, options[0])
            index = cb.findText(current_value)
            if index >= 0:
                cb.setCurrentIndex(index)
            self.settings_combos[config_key] = cb
            thresh_lay.addWidget(lbl, row, 0)
            thresh_lay.addWidget(cb, row, 1)

        n_outer.addLayout(thresh_lay)

        n_outer.addWidget(Divider())
        pref_title = QLabel("Notification Preferences")
        pref_title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        pref_title.setStyleSheet(f"color: {NAVY}; background: transparent; border: none;")
        n_outer.addWidget(pref_title)

        notif_map = [
            ("Show alert when student exceeds 2 Green Slips per semester", "green_slip_alert"),
            ("Warn before issuing 2nd Pink Slip (policy violation)", "pink_slip_warn"),
            ("Auto-flag Blue Slip as 'Escalated' on 3rd repeat offense", "auto_escalate"),
            ("Show monthly summary reminder on login", "monthly_summary"),
        ]

        notif_config = current_config.get("notifications", {})

        for label, config_key in notif_map:
            cb = QCheckBox(label)
            cb.setFont(QFont("Segoe UI", 12))
            cb.setChecked(notif_config.get(config_key, True))
            cb.setStyleSheet("background: transparent; border: none;")
            self.settings_checkboxes[config_key] = cb
            n_outer.addWidget(cb)

        lay.addWidget(notif_frame)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        save_btn = QPushButton("Save Settings")
        save_btn.setStyleSheet(btn_primary())
        save_btn.setFixedHeight(40)
        save_btn.clicked.connect(self._save_system_settings)
        btn_row.addWidget(save_btn)
        lay.addLayout(btn_row)
        lay.addStretch()
        return w

    def _save_system_settings(self):
        try:
            config = load_config()
            for key, combo in self.settings_combos.items():
                config[key] = combo.currentText()
            notif_config = {}
            for key, checkbox in self.settings_checkboxes.items():
                notif_config[key] = checkbox.isChecked()
            config["notifications"] = notif_config
            save_config(config)
            InfoDialog("Settings Saved",
                      "System settings have been saved successfully!\n\n"
                      "The school year will be applied to NEW student records.",
                      parent=self).exec_()
        except Exception as e:
            InfoDialog("Error",
                      f"Failed to save settings: {str(e)}",
                      success=False, parent=self).exec_()

    def _add_school_year(self, input_field, combo_box):
        new_year = input_field.text().strip()
        if not new_year:
            InfoDialog("Input Required",
                      "Please enter a school year (e.g., 2025–2026)",
                      success=False, parent=self).exec_()
            return
        if add_school_year(new_year):
            combo_box.clear()
            combo_box.addItems(get_school_years_list())
            input_field.clear()
            InfoDialog("Success",
                      f"School year '{new_year}' has been added.",
                      success=True, parent=self).exec_()
        else:
            InfoDialog("Error",
                      "Failed to add school year.",
                      success=False, parent=self).exec_()

    # ── About tab ─────────────────────────────────────────────────────────────
    def _build_about_tab(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background: {WHITE};")

        # Wrap everything in a scroll area so content is always reachable
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")

        content = QWidget()
        content.setStyleSheet(f"background: {WHITE};")
        lay = QVBoxLayout(content)
        lay.setContentsMargins(40, 30, 40, 30)
        lay.setSpacing(16)
        lay.setAlignment(Qt.AlignTop)

        # ── SCMS badge ────────────────────────────────────────────────────────
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

        # ── Developer Section ─────────────────────────────────────────────────
        lay.addWidget(Divider())

        dev_section_title = QLabel("Meet the Developers")
        dev_section_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        dev_section_title.setAlignment(Qt.AlignCenter)
        dev_section_title.setStyleSheet(f"color: {NAVY}; background: transparent; border: none;")
        lay.addWidget(dev_section_title)

        dev_subtitle = QLabel("Software Engineering Project — CJC")
        dev_subtitle.setFont(QFont("Segoe UI", 11))
        dev_subtitle.setAlignment(Qt.AlignCenter)
        dev_subtitle.setStyleSheet(f"color: {MID_GRAY}; background: transparent; border: none;")
        lay.addWidget(dev_subtitle)

        # Developer data
        developers = [
            {
                "name":     "Daisy Mae Lascuña",
                "email":    "daisylascuna@g.cjc.edu.ph",
                "facebook": "facebook.com/daisy.crujedo",
                "photo":    "dev1.jpg",
            },
            {
                
                "name":     "Merandreas Jorgio",
                "email":    "jorgiomer@g.cjc.edu.ph",
                "facebook": "facebook.com/merandreas.andre",
                "photo":    "dev2.jpg",
            },
            {
                "name":     "Juliana Bless Eltagonde",
                "email":    "eltagondejuliana@g.cjc.edu.ph",
                "facebook": "facebook.com/juliana.eltagonde.2025",
                "photo":    "dev3.jpg",
            },
        ]

        # Row of three developer cards
        cards_row = QHBoxLayout()
        cards_row.setSpacing(20)
        cards_row.setContentsMargins(0, 8, 0, 8)

        for dev in developers:
            card = self._build_dev_card(dev)
            cards_row.addWidget(card)

        lay.addLayout(cards_row)
        lay.addStretch()

        scroll.setWidget(content)

        # Outer layout for the tab widget
        outer = QVBoxLayout(w)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)
        return w

    # ── Developer card builder ────────────────────────────────────────────────
    def _build_dev_card(self, dev: dict) -> QFrame:
        """
        Creates a single developer card with:
          - Circular profile picture (loaded from SCMS/assets/<photo>)
          - Full name
          - Email
          - Facebook link (displayed as plain label)
        """
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame#devCard {{
                background: {WHITE};
                border: 1.5px solid {LIGHT_GRAY};
                border-radius: 14px;
            }}
            QFrame#devCard:hover {{
                border: 1.5px solid {NAVY};
                background: {OFF_WHITE};
            }}
        """)
        card.setObjectName("devCard")
        card.setMinimumWidth(200)
        add_shadow(card, blur=14, y=4, color=(0, 0, 0, 18))

        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(20, 24, 20, 24)
        card_lay.setSpacing(10)
        card_lay.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        # ── Profile picture ───────────────────────────────────────────────────
        pic_size = 100
        photo_label = QLabel()
        photo_label.setFixedSize(pic_size, pic_size)
        photo_label.setAlignment(Qt.AlignCenter)
        photo_label.setStyleSheet("background: transparent; border: none;")

        # Build the asset path relative to this file's location
        assets_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'assets')
        photo_path = os.path.join(assets_dir, dev["photo"])

        pixmap = QPixmap(photo_path)

        if pixmap.isNull():
            # Fallback: draw initials inside a coloured circle
            pixmap = self._make_initials_avatar(dev["name"], pic_size)
        else:
            pixmap = self._make_circular_pixmap(pixmap, pic_size)

        photo_label.setPixmap(pixmap)

        # Centre the photo label
        pic_row = QHBoxLayout()
        pic_row.addStretch()
        pic_row.addWidget(photo_label)
        pic_row.addStretch()
        card_lay.addLayout(pic_row)

        # ── Name ──────────────────────────────────────────────────────────────
        name_lbl = QLabel(dev["name"])
        name_lbl.setFont(QFont("Segoe UI", 13, QFont.Bold))
        name_lbl.setAlignment(Qt.AlignCenter)
        name_lbl.setWordWrap(True)
        name_lbl.setStyleSheet(f"color: {NAVY}; background: transparent; border: none;")
        card_lay.addWidget(name_lbl)

        # ── Thin accent line below name ───────────────────────────────────────
        accent = QFrame()
        accent.setFixedHeight(2)
        accent.setStyleSheet(f"background: {LIGHT_GRAY}; border: none; border-radius: 1px;")
        card_lay.addWidget(accent)

        # ── Email (clickable) ─────────────────────────────────────────────────
        email_row = QHBoxLayout()
        email_row.setSpacing(6)

        email_icon = QLabel("✉")
        email_icon.setFont(QFont("Segoe UI", 11))
        email_icon.setStyleSheet(f"color: {NAVY}; background: transparent; border: none;")
        email_icon.setFixedWidth(18)

        email_lbl = QLabel(f'<a href="mailto:{dev["email"]}" style="color:{NAVY}; text-decoration:underline;">{dev["email"]}</a>')
        email_lbl.setFont(QFont("Segoe UI", 10))
        email_lbl.setWordWrap(True)
        email_lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        email_lbl.setStyleSheet("background: transparent; border: none;")
        email_lbl.setOpenExternalLinks(True)
        email_lbl.setCursor(Qt.PointingHandCursor)
        email_lbl.setToolTip(f"Send email to {dev['email']}")

        email_row.addWidget(email_icon)
        email_row.addWidget(email_lbl, 1)
        card_lay.addLayout(email_row)

        # ── Facebook (clickable) ──────────────────────────────────────────────
        fb_row = QHBoxLayout()
        fb_row.setSpacing(6)

        fb_icon = QLabel("f")
        fb_icon.setFont(QFont("Segoe UI", 11, QFont.Bold))
        fb_icon.setStyleSheet(f"color: {NAVY}; background: transparent; border: none;")
        fb_icon.setFixedWidth(18)

        fb_full_url = f'https://www.{dev["facebook"]}'
        fb_lbl = QLabel(f'<a href="{fb_full_url}" style="color:{NAVY}; text-decoration:underline;">{dev["facebook"]}</a>')
        fb_lbl.setFont(QFont("Segoe UI", 10))
        fb_lbl.setWordWrap(True)
        fb_lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        fb_lbl.setStyleSheet("background: transparent; border: none;")
        fb_lbl.setOpenExternalLinks(True)
        fb_lbl.setCursor(Qt.PointingHandCursor)
        fb_lbl.setToolTip(f"Open Facebook profile")

        fb_row.addWidget(fb_icon)
        fb_row.addWidget(fb_lbl, 1)
        card_lay.addLayout(fb_row)

        return card

    # ── Image helpers ─────────────────────────────────────────────────────────
    @staticmethod
    def _make_circular_pixmap(pixmap: QPixmap, size: int) -> QPixmap:
        """Crop a pixmap into a circle of the given size."""
        scaled = pixmap.scaled(
            size, size,
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation
        )
        # Crop to square from centre
        x = (scaled.width()  - size) // 2
        y = (scaled.height() - size) // 2
        scaled = scaled.copy(x, y, size, size)

        result = QPixmap(size, size)
        result.fill(Qt.transparent)

        painter = QPainter(result)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addEllipse(0, 0, size, size)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, scaled)
        painter.end()
        return result

    @staticmethod
    def _make_initials_avatar(name: str, size: int) -> QPixmap:
        """Generate a fallback circular avatar with the person's initials."""
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw filled circle using NAVY colour
        from PyQt5.QtGui import QColor, QBrush
        painter.setBrush(QBrush(QColor(NAVY)))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, size, size)

        # Draw initials
        parts = name.strip().split()
        initials = "".join(p[0].upper() for p in parts[:2])
        painter.setPen(QColor(WHITE))
        font = QFont("Segoe UI", size // 3, QFont.Bold)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignCenter, initials)
        painter.end()
        return pixmap