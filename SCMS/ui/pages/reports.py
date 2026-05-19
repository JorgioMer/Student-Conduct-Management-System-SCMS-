# =============================================================================
#  SCMS — Reports Page
# =============================================================================
import logging
from PyQt5.QtWidgets import (
    QScrollArea, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QFrame, QTabWidget, QWidget,
    QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

# NOTE: Do NOT call matplotlib.use() here at module level.
# The backend is initialized lazily when _make_canvas() is first called.

from collections import Counter
from datetime import datetime

logger = logging.getLogger(__name__)

from ui.styles import (
    NAVY, NAVY_DARK, GOLD, WHITE, OFF_WHITE,
    LIGHT_GRAY, MID_GRAY, TEXT_DARK,
    GREEN_SLIP, PINK_SLIP, BLUE_SLIP,
    btn_gold, btn_outline, btn_primary
)
from ui.components import (
    SectionTitle, SubTitle, Divider,
    StatTile, add_shadow, InfoDialog
)
from ui.pages.base_page import BasePage, build_record_table
from ui.data_events import data_events
from ui.pdf_preview_dialog import PDFPreviewDialog
from backend.pdf_export import (
    generate_overview_report, generate_slip_report,
    generate_student_conduct_summary
)
from backend.db_activity_log import log_export, log_report_generated
from backend.config import get_course_college, get_college_name, get_all_colleges
import tempfile
import os


# ---------------------------------------------------------------------------
# Lazy canvas factory — imports happen here, after QApplication exists
# ---------------------------------------------------------------------------
def _make_canvas(fig):
    """
    Render a matplotlib Figure to a QLabel via Agg PNG bytes.
    Avoids Qt5Agg entirely — compatible with Python 3.13 + PyQt5.
    """
    try:
        import io
        from matplotlib.backends.backend_agg import FigureCanvasAgg
        from PyQt5.QtWidgets import QLabel
        from PyQt5.QtGui import QPixmap

        canvas_agg = FigureCanvasAgg(fig)
        buf = io.BytesIO()
        canvas_agg.print_png(buf)
        buf.seek(0)

        pixmap = QPixmap()
        pixmap.loadFromData(buf.read(), "PNG")

        label = QLabel()
        label.setAlignment(Qt.AlignCenter)
        label.setPixmap(pixmap)
        label.setMinimumHeight(280)
        return label
    except Exception as e:
        logger.error(f"Chart render failed: {e}", exc_info=True)
        from PyQt5.QtWidgets import QLabel
        placeholder = QLabel("Chart unavailable")
        placeholder.setAlignment(Qt.AlignCenter)
        return placeholder


class ReportsPage(BasePage):
    def __init__(self, current_user=None, parent=None):
        logger.debug("ReportsPage.__init__ starting...")
        try:
            super().__init__(parent)
            logger.debug("  BasePage initialized")

            self.current_user = current_user or {}
            self.staff_id = self.current_user.get("username", "UNKNOWN")
            self._tabs = None
            self._built_tabs = set()
            logger.debug(f"  Set staff_id: {self.staff_id}")

            logger.debug("  Calling _build()...")
            self._build()
            logger.debug("  _build() completed")

            logger.debug("  Connecting data_events signal...")
            data_events.slips_changed.connect(self._on_slips_changed)
            logger.info("ReportsPage.__init__ completed successfully")
        except Exception as e:
            logger.error(f"Error in ReportsPage.__init__: {str(e)}", exc_info=True)
            raise

    # ------------------------------------------------------------------
    # Period filtering helpers
    # ------------------------------------------------------------------
    def _filter_records_by_period(self, records, date_field_index=6):
        period = self.period_cb.currentText() if hasattr(self, 'period_cb') else ""
        if not records or not period:
            return records

        filtered = []
        for record in records:
            try:
                if len(record) <= date_field_index:
                    continue
                date_str = str(record[date_field_index]).strip()
                if not date_str or date_str == "N/A":
                    continue
                try:
                    if "/" in date_str:
                        date_obj = datetime.strptime(date_str.split()[0], "%d/%m/%Y")
                    else:
                        date_obj = datetime.strptime(date_str.split()[0], "%Y-%m-%d")
                except ValueError:
                    continue
                if self._date_in_period(date_obj, period):
                    filtered.append(record)
            except Exception:
                continue
        return filtered

    def _date_in_period(self, date_obj, period_str):
        month = date_obj.month
        year  = date_obj.year

        if len(period_str.split()) == 2:
            try:
                period_date = datetime.strptime(period_str, "%B %Y")
                return month == period_date.month and year == period_date.year
            except ValueError:
                return True

        if "1st Semester" in period_str or "1ST Semester" in period_str:
            return month in [6, 7, 8, 9, 10, 11]
        if "2ND Semester" in period_str or "2nd Semester" in period_str:
            return month in [12, 1, 2, 3, 4, 5]
        if "Full Year" in period_str:
            return True
        return True

    # ------------------------------------------------------------------
    # Page skeleton
    # ------------------------------------------------------------------
    def _build(self):
        logger.debug("_build() starting...")
        try:
            # Header
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
            h_col = QVBoxLayout()
            h_col.setSpacing(2)

            t_lbl = QLabel("   Reports & Analytics")
            t_lbl.setFont(QFont("Segoe UI", 17, QFont.Bold))
            t_lbl.setStyleSheet(f"color: {GOLD}; background: transparent; border: none; padding: 0;")

            s_lbl = QLabel("Monthly summaries, visual graphs, and statistical records for all slip types")
            s_lbl.setFont(QFont("Segoe UI", 11))
            s_lbl.setStyleSheet("color: rgba(255,255,255,0.85); background: transparent; border: none; padding: 0;")

            h_col.addWidget(t_lbl)
            h_col.addWidget(s_lbl)
            h_lay.addLayout(h_col)
            h_lay.addStretch()

            export_all = QPushButton("   Export All Reports ")
            export_all.setStyleSheet(btn_gold())
            export_all.setFixedHeight(38)
            export_all.clicked.connect(self._export_overview_report)
            h_lay.addWidget(export_all)
            self.main_layout.addWidget(header)

            # Period selector
            period_row = QHBoxLayout()
            period_lbl = QLabel("Report Period:")
            period_lbl.setStyleSheet("border: none; background: transparent;")
            period_row.addWidget(period_lbl)
            self.period_cb = QComboBox()
            self.period_cb.addItems([
                "January 2026", "February 2026", "March 2026", "April 2026",
                "May 2026", "June 2026", "July 2026", "August 2026",
                "September 2026", "October 2026", "December 2026",
                "1st Semester S.Y. 2025–2026",
                "2ND Semester S.Y. 2025–2026",
                "S.Y. 2025–2026 (Full Year)",
            ])
            current_month = datetime.now().strftime("%B %Y")
            idx = self.period_cb.findText(current_month)
            if idx >= 0:
                self.period_cb.setCurrentIndex(idx)
            self.period_cb.setFixedHeight(38)
            self.period_cb.setFixedWidth(280)
            self.period_cb.currentIndexChanged.connect(self._on_period_changed)
            period_row.addWidget(self.period_cb)
            period_row.addStretch()

            self.top_print_btn = QPushButton(" Print Preview ")
            self.top_print_btn.setStyleSheet(btn_outline())
            self.top_print_btn.setFixedHeight(38)
            self.top_print_btn.clicked.connect(self._export_overview_report)
            period_row.addWidget(self.top_print_btn)
            self.main_layout.addLayout(period_row)

            self._update_print_button_state()

            # Tabs
            tabs = QTabWidget()
            self._tabs = tabs

            tabs.addTab(self._build_overview_tab(),    "   Overview ")
            tabs.addTab(self._build_green_report(),    "   Green Slips ")
            tabs.addTab(self._build_pink_report(),     "   Pink Slips ")
            tabs.addTab(self._build_blue_report(),     "   Blue Slips ")
            tabs.addTab(self._build_college_report(),  "   By College ")
            tabs.addTab(self._build_toplist_tab(),     "   Student Records ")

            self.main_layout.addWidget(tabs)
            self.main_layout.addStretch()
            logger.debug("_build() completed successfully")
        except Exception as e:
            logger.error(f"Error in ReportsPage._build(): {str(e)}", exc_info=True)
            raise

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    def closeEvent(self, event):
        try:
            data_events.slips_changed.disconnect(self._on_slips_changed)
        except Exception:
            pass
        super().closeEvent(event)

    def showEvent(self, event):
        super().showEvent(event)
        try:
            self._on_slips_changed()
        except Exception as e:
            logger.error(f"Failed to refresh reports on show: {e}")

    # ------------------------------------------------------------------
    # Overview tab
    # ------------------------------------------------------------------
    def _build_overview_tab(self) -> QWidget:
        container = QWidget()
        container.setStyleSheet(f"background: {WHITE};")
        lay = QVBoxLayout(container)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(18)

        scroll = QScrollArea()
        scroll.setWidget(container)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        selected_period = self.period_cb.currentText() if hasattr(self, 'period_cb') else "November 2026"
        lay.addWidget(SectionTitle(f"Monthly Overview — {selected_period}"))

        from backend.db_blue_slip  import get_blue_slips
        from backend.db_green_slip import get_green_slips
        from backend.db_pink_slip  import get_pink_slips

        green_slips = self._filter_records_by_period(get_green_slips(None) or [], date_field_index=6)
        pink_slips  = self._filter_records_by_period(get_pink_slips(None)  or [], date_field_index=5)
        blue_slips  = self._filter_records_by_period(get_blue_slips(None)  or [], date_field_index=6)

        green_count   = len(green_slips)
        pink_count    = len(pink_slips)
        blue_count    = len(blue_slips)
        total_records = green_count + pink_count + blue_count

        all_students = set()
        for r in green_slips + pink_slips + blue_slips:
            if len(r) > 1:
                all_students.add(r[1])
        students_involved = len(all_students)

        tiles_row = QHBoxLayout()
        tiles_row.setSpacing(16)
        for label, val, colour, icon in [
            ("Green Slips Issued",      str(green_count),      GREEN_SLIP, ""),
            ("Pink Slips Issued",       str(pink_count),       PINK_SLIP,  ""),
            ("Blue Slips / Violations", str(blue_count),       BLUE_SLIP,  ""),
            ("Total Records Filed",     str(total_records),    NAVY,       ""),
            ("Students Involved",       str(students_involved),GOLD,       ""),
        ]:
            tiles_row.addWidget(StatTile(f"{icon}  {label}", val, colour))
        lay.addLayout(tiles_row)

        lay.addWidget(Divider())

        charts_label = QLabel("Visual Summary Charts")
        charts_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        charts_label.setStyleSheet(f"color: {NAVY}; background: transparent; border: none;")
        lay.addWidget(charts_label)

        charts_row = QHBoxLayout()
        charts_row.setSpacing(16)

        for builder, bg in [
            (lambda: self._create_slip_distribution_chart(green_count, pink_count, blue_count), "#E8F5E9"),
            (lambda: self._create_year_breakdown_chart(green_slips + pink_slips + blue_slips),  "#FCE4EC"),
            (lambda: self._create_student_slip_distribution_chart(green_slips + pink_slips + blue_slips), "#E3F2FD"),
        ]:
            frame = QFrame()
            frame.setStyleSheet(f"""
                QFrame {{
                    background: {bg};
                    border: 1.5px solid {LIGHT_GRAY};
                    border-radius: 10px;
                }}
            """)
            frame_lay = QVBoxLayout(frame)
            frame_lay.setContentsMargins(10, 10, 10, 10)
            frame.setMinimumHeight(300)
            try:
                frame_lay.addWidget(builder())
            except Exception as e:
                logger.error(f"Chart build failed: {e}", exc_info=True)
                err_lbl = QLabel("Chart unavailable")
                err_lbl.setAlignment(Qt.AlignCenter)
                frame_lay.addWidget(err_lbl)
            charts_row.addWidget(frame, 1)

        lay.addLayout(charts_row)

        # College distribution
        lay.addWidget(Divider())
        college_chart_label = QLabel("Distribution by College")
        college_chart_label.setFont(QFont("Segoe UI", 13, QFont.Bold))
        college_chart_label.setStyleSheet(f"color: {NAVY}; background: transparent; border: none;")
        lay.addWidget(college_chart_label)

        all_slips   = green_slips + pink_slips + blue_slips
        college_data = self._build_college_data(all_slips, green_slips, pink_slips, blue_slips)

        college_frame = QFrame()
        college_frame.setStyleSheet(f"""
            QFrame {{
                background: #FFF3E0;
                border: 1.5px solid {LIGHT_GRAY};
                border-radius: 10px;
            }}
        """)
        college_layout = QVBoxLayout(college_frame)
        college_frame.setMinimumHeight(320)
        college_layout.setContentsMargins(10, 10, 10, 10)
        try:
            college_layout.addWidget(self._create_college_distribution_chart(college_data))
        except Exception as e:
            logger.error(f"College chart failed: {e}", exc_info=True)
            err_lbl = QLabel("Chart unavailable")
            err_lbl.setAlignment(Qt.AlignCenter)
            college_layout.addWidget(err_lbl)
        lay.addWidget(college_frame)

        return scroll

    # ------------------------------------------------------------------
    # Slip report tabs
    # ------------------------------------------------------------------
    def _build_green_report(self) -> QWidget:
        from backend.db_green_slip import get_green_slips
        green_records = self._filter_records_by_period(get_green_slips(None) or [], date_field_index=6)
        rows = []
        for record in green_records[:5]:
            try:
                stud_name = record[0] if len(record) > 0 else "Unknown"
                stud_num  = record[4] if len(record) > 4 else "N/A"
                year      = record[2] if len(record) > 2 else "N/A"
                is_dispensation = record[5] if len(record) > 5 else False
                slip_type = "Dispensation" if is_dispensation else "Excuse"
                date      = str(record[6])[:10] if len(record) > 6 else "N/A"
                days      = str(record[7]) if len(record) > 7 else "N/A"
                status    = record[8] if len(record) > 8 else "Active"
                rows.append((stud_num, stud_name, year, slip_type, date, days, status))
            except Exception:
                pass
        if not rows:
            rows = [("No records", "Add records to see them here", "-", "-", "-", "-", "-")]
        return self._build_slip_report_tab(
            "green", "Green Slip Monthly Report",
            "Dispensation and Excuse slips issued this month",
            GREEN_SLIP, "#E8F5E9",
            ["Student No.", "Student Name", "Year", "Type", "Date", "Days/Reason", "Status"],
            rows,
        )

    def _build_pink_report(self) -> QWidget:
        from backend.db_pink_slip import get_pink_slips
        pink_records = self._filter_records_by_period(get_pink_slips(None) or [], date_field_index=5)
        rows = []
        for record in pink_records[:5]:
            try:
                stud_name = record[0] if len(record) > 0 else "Unknown"
                stud_num  = record[4] if len(record) > 4 else "N/A"
                year      = record[2] if len(record) > 2 else "N/A"
                course    = record[1] if len(record) > 1 else "N/A"
                date      = str(record[5])[:10] if len(record) > 5 else "N/A"
                violation = record[6] if len(record) > 6 else "N/A"
                rows.append((stud_num, stud_name, year, course, violation, date))
            except Exception:
                pass
        if not rows:
            rows = [("No records", "Add records to see them here", "-", "-", "-", "-")]
        return self._build_slip_report_tab(
            "pink", "Pink Slip Monthly Report",
            "Penalty slips issued this month (one per student per semester)",
            PINK_SLIP, "#FCE4EC",
            ["Student No.", "Student Name", "Year", "Course", "Violation", "Date Issued"],
            rows,
        )

    def _build_blue_report(self) -> QWidget:
        from backend.db_blue_slip import get_blue_slips
        blue_records = self._filter_records_by_period(get_blue_slips(None) or [], date_field_index=6)
        rows = []
        for record in blue_records[:5]:
            try:
                stud_name = record[0] if len(record) > 0 else "Unknown"
                stud_num  = record[4] if len(record) > 4 else "N/A"
                year      = record[2] if len(record) > 2 else "N/A"
                violation = record[5] if len(record) > 5 else "N/A"
                severity  = record[8] if len(record) > 8 else "N/A"
                date      = str(record[6])[:10] if len(record) > 6 else "N/A"
                status    = record[10] if len(record) > 10 else "Open"
                rows.append((stud_num, stud_name, year, violation, severity, date, status))
            except Exception:
                pass
        if not rows:
            rows = [("No records", "Add records to see them here", "-", "-", "-", "-", "-")]
        return self._build_slip_report_tab(
            "blue", "Blue Slip Monthly Report",
            "Violation records and disciplinary actions taken this month",
            BLUE_SLIP, "#E3F2FD",
            ["Student No.", "Student Name", "Year", "Violation", "Severity", "Date", "Status"],
            rows,
        )

    def _build_slip_report_tab(self, slip_type, title, subtitle, colour, bg,
                                headers, rows) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background: {WHITE};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(14)

        top_row = QHBoxLayout()
        t_lbl = QLabel(title)
        t_lbl.setFont(QFont("Segoe UI", 15, QFont.Bold))
        t_lbl.setStyleSheet(f"color: {colour}; background: transparent; border: none;")
        top_row.addWidget(t_lbl)
        top_row.addStretch()

        has_data = not (len(rows) == 1 and rows[0][0] == "No records")

        export_pdf_btn = QPushButton("   Export PDF ")
        export_pdf_btn.setStyleSheet(btn_outline())
        export_pdf_btn.setFixedHeight(36)
        export_pdf_btn.setEnabled(has_data)
        export_pdf_btn.clicked.connect(
            lambda _, st=slip_type, ttl=title, sbt=subtitle, rw=rows:
            self._export_slip_report(st, ttl, sbt, rw)
        )
        top_row.addWidget(export_pdf_btn)

        print_btn = QPushButton("   Print ")
        print_btn.setStyleSheet(btn_outline())
        print_btn.setFixedHeight(36)
        print_btn.setEnabled(has_data)
        print_btn.clicked.connect(
            lambda _, st=slip_type, ttl=title, sbt=subtitle, rw=rows:
            self._export_slip_report(st, ttl, sbt, rw)
        )
        top_row.addWidget(print_btn)
        lay.addLayout(top_row)

        sub = QLabel(subtitle)
        sub.setFont(QFont("Segoe UI", 11))
        sub.setStyleSheet(f"color: {MID_GRAY}; background: transparent; border: none;")
        lay.addWidget(sub)

        t = build_record_table(headers, rows)
        t.setMinimumHeight(250)
        lay.addWidget(t)

        info_bar = QFrame()
        info_bar.setStyleSheet(f"""
            QFrame {{
                background: {bg};
                border-left: 4px solid {colour};
                border-radius: 6px;
                padding: 6px;
            }}
        """)
        i_lay = QHBoxLayout(info_bar)
        i_lay.setContentsMargins(12, 8, 12, 8)
        total_lbl = QLabel(f"Total records shown: <b>{len(rows)}</b>")
        total_lbl.setTextFormat(Qt.RichText)
        total_lbl.setFont(QFont("Segoe UI", 11))
        total_lbl.setStyleSheet(f"color: {colour}; background: transparent; border: none;")
        i_lay.addWidget(total_lbl)
        i_lay.addStretch()
        lay.addWidget(info_bar)
        lay.addStretch()
        return w

    # ------------------------------------------------------------------
    # College tab
    # ------------------------------------------------------------------
    def _build_college_data(self, all_slips, green_slips, pink_slips, blue_slips):
        college_data = {}
        for college_code in get_all_colleges():
            college_data[college_code] = {
                "name": get_college_name(college_code),
                "students": set(),
                "green": 0, "pink": 0, "blue": 0, "total": 0,
            }
        for slip in all_slips:
            try:
                course       = slip[1] if len(slip) > 1 else ""
                college_code = get_course_college(course)
                if college_code is None:
                    continue
                stud_name = slip[0] if len(slip) > 0 else "Unknown"
                college_data[college_code]["students"].add(stud_name)
                if slip in green_slips:
                    college_data[college_code]["green"] += 1
                elif slip in pink_slips:
                    college_data[college_code]["pink"] += 1
                elif slip in blue_slips:
                    college_data[college_code]["blue"] += 1
                college_data[college_code]["total"] += 1
            except Exception:
                pass
        return college_data

    def _build_college_report(self) -> QWidget:
        from backend.db_green_slip import get_green_slips
        from backend.db_pink_slip  import get_pink_slips
        from backend.db_blue_slip  import get_blue_slips

        container = QWidget()
        container.setStyleSheet(f"background: {WHITE};")
        lay = QVBoxLayout(container)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(16)

        lay.addWidget(SectionTitle("Distribution by College"))

        green_slips = self._filter_records_by_period(get_green_slips(None) or [], date_field_index=6)
        pink_slips  = self._filter_records_by_period(get_pink_slips(None)  or [], date_field_index=5)
        blue_slips  = self._filter_records_by_period(get_blue_slips(None)  or [], date_field_index=6)
        all_slips   = green_slips + pink_slips + blue_slips

        college_data = self._build_college_data(all_slips, green_slips, pink_slips, blue_slips)

        tiles_row = QHBoxLayout()
        tiles_row.setSpacing(12)
        for college_code, data in college_data.items():
            if data["total"] > 0:
                tile = QFrame()
                tile.setStyleSheet(f"""
                    QFrame {{
                        background: #F8F9FA;
                        border: 1.5px solid {LIGHT_GRAY};
                        border-radius: 10px;
                    }}
                """)
                tile_lay = QVBoxLayout(tile)
                tile_lay.setContentsMargins(14, 12, 14, 12)
                tile_lay.setSpacing(8)

                name_lbl = QLabel(college_code)
                name_lbl.setFont(QFont("Segoe UI", 11, QFont.Bold))
                name_lbl.setStyleSheet(f"color: {NAVY}; background: transparent; border: none;")
                tile_lay.addWidget(name_lbl)

                stats_lbl = QLabel(f"Students: {len(data['students'])}\nTotal Records: {data['total']}")
                stats_lbl.setFont(QFont("Segoe UI", 10))
                stats_lbl.setStyleSheet(f"color: {MID_GRAY}; background: transparent; border: none;")
                tile_lay.addWidget(stats_lbl)

                breakdown = QLabel(f"🟢 {data['green']}  🔴 {data['pink']}  🔵 {data['blue']}")
                breakdown.setFont(QFont("Segoe UI", 10))
                breakdown.setStyleSheet(f"color: {TEXT_DARK}; background: transparent; border: none;")
                tile_lay.addWidget(breakdown)

                tiles_row.addWidget(tile)

        tiles_row.addStretch()
        lay.addLayout(tiles_row)
        lay.addWidget(Divider())

        chart_frame = QFrame()
        chart_frame.setStyleSheet(f"""
            QFrame {{
                background: #F8F9FA;
                border: 1px solid {LIGHT_GRAY};
                border-radius: 10px;
            }}
        """)
        chart_frame.setMinimumHeight(320)
        chart_lay = QVBoxLayout(chart_frame)
        chart_lay.setContentsMargins(10, 10, 10, 10)
        try:
            chart_lay.addWidget(self._create_college_distribution_chart(college_data))
        except Exception as e:
            logger.error(f"College chart failed: {e}", exc_info=True)
            err_lbl = QLabel("Chart unavailable")
            err_lbl.setAlignment(Qt.AlignCenter)
            chart_lay.addWidget(err_lbl)
        lay.addWidget(chart_frame)

        detail_lbl = QLabel("College Details")
        detail_lbl.setFont(QFont("Segoe UI", 13, QFont.Bold))
        detail_lbl.setStyleSheet(f"color: {NAVY}; background: transparent; border: none;")
        lay.addWidget(detail_lbl)

        rows = []
        for college_code, data in college_data.items():
            rows.append((
                college_code, data["name"],
                str(len(data["students"])),
                str(data["green"]), str(data["pink"]),
                str(data["blue"]), str(data["total"]),
            ))

        detail_table = build_record_table(
            ["Code", "College Name", "Students", "Green", "Pink", "Blue", "Total"], rows
        )
        detail_table.setMinimumHeight(len(rows) * 40 + 60)
        detail_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        lay.addWidget(detail_table)
        lay.addStretch()

        scroll = QScrollArea()
        scroll.setWidget(container)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        return scroll

    # ------------------------------------------------------------------
    # Student top-list tab
    # ------------------------------------------------------------------
    def _build_toplist_tab(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background: {WHITE};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(14)

        lay.addWidget(SectionTitle("Student Conduct Summary"))
        lay.addWidget(SubTitle("Students with the most recorded slips this semester"))

        headers = ["Rank", "Student No.", "Student Name", "Year",
                   "Green Slips", "Pink Slips", "Blue Slips", "Total"]

        from backend.db_blue_slip  import get_blue_slips
        from backend.db_green_slip import get_green_slips
        from backend.db_pink_slip  import get_pink_slips
        from backend.db_students   import get_student

        student_counts = {}
        try:
            for record in get_green_slips(None) or []:
                sn = record[4] if len(record) > 4 else None
                if sn:
                    student_counts.setdefault(sn, {"green": 0, "pink": 0, "blue": 0, "info": None})
                    student_counts[sn]["green"] += 1
                    if not student_counts[sn]["info"]:
                        student_counts[sn]["info"] = get_student(sn)
            for record in get_pink_slips(None) or []:
                sn = record[4] if len(record) > 4 else None
                if sn:
                    student_counts.setdefault(sn, {"green": 0, "pink": 0, "blue": 0, "info": None})
                    student_counts[sn]["pink"] += 1
                    if not student_counts[sn]["info"]:
                        student_counts[sn]["info"] = get_student(sn)
            for record in get_blue_slips(None) or []:
                sn = record[4] if len(record) > 4 else None
                if sn:
                    student_counts.setdefault(sn, {"green": 0, "pink": 0, "blue": 0, "info": None})
                    student_counts[sn]["blue"] += 1
                    if not student_counts[sn]["info"]:
                        student_counts[sn]["info"] = get_student(sn)
        except Exception:
            pass

        sorted_students = sorted(
            student_counts.items(),
            key=lambda x: x[1]["green"] + x[1]["pink"] + x[1]["blue"],
            reverse=True,
        )

        sample = []
        for rank, (sn, counts) in enumerate(sorted_students[:8], 1):
            try:
                info      = counts["info"]
                stud_name = info[1] if info and len(info) > 1 else "Unknown"
                year      = info[3] if info and len(info) > 3 else "N/A"
                total     = counts["green"] + counts["pink"] + counts["blue"]
                sample.append((str(rank), sn, stud_name, year,
                               str(counts["green"]), str(counts["pink"]),
                               str(counts["blue"]), str(total)))
            except Exception:
                pass

        if not sample:
            sample = [("1", "No records", "Add records to see them here",
                       "-", "0", "0", "0", "0")]

        t = build_record_table(headers, sample)
        t.setMinimumHeight(300)
        lay.addWidget(t)

        note = QLabel(
            "   This list helps the Office of the Prefect identify students who may need "
            "additional counseling, guidance, or follow-up actions. "
            "Data shown is for the current semester."
        )
        note.setWordWrap(True)
        note.setFont(QFont("Segoe UI", 11))
        note.setStyleSheet(f"""
            background: #FFF8E1;
            border-left: 4px solid {GOLD};
            border-radius: 6px;
            padding: 10px 14px;
            color: #8D6E0A;
        """)
        lay.addWidget(note)
        lay.addStretch()
        return w

    # ------------------------------------------------------------------
    # Chart builders — matplotlib imported lazily inside each method
    # ------------------------------------------------------------------
    def _create_slip_distribution_chart(self, green, pink, blue):
        from matplotlib.figure import Figure
        fig = Figure(figsize=(5, 4), dpi=90, facecolor='white', edgecolor='none')
        ax  = fig.add_subplot(111)

        sizes  = [green, pink, blue]
        labels = ['Green Slips', 'Pink Slips', 'Blue Slips']
        colors = ['#4CAF50', '#E91E63', '#2196F3']

        if sum(sizes) > 0:
            wedges, texts, autotexts = ax.pie(
                sizes, labels=labels, colors=colors,
                autopct='%1.1f%%', startangle=90,
                textprops={'fontsize': 9},
            )
            for at in autotexts:
                at.set_color('white')
                at.set_fontweight('bold')
        else:
            ax.text(0.5, 0.5, 'No Data', ha='center', va='center', fontsize=12, color='gray')
            ax.set_xlim(0, 1); ax.set_ylim(0, 1)

        ax.set_title('Slip Distribution', fontsize=11, fontweight='bold', pad=10)
        fig.tight_layout(pad=0.5)
        return _make_canvas(fig)

    def _create_year_breakdown_chart(self, all_records):
        from matplotlib.figure import Figure
        fig = Figure(figsize=(5, 4), dpi=90, facecolor='white', edgecolor='none')
        ax  = fig.add_subplot(111)

        year_counts = Counter()
        for record in all_records:
            if len(record) > 2:
                year = record[2]
                if year and year != "N/A":
                    year_counts[str(year)] += 1

        if year_counts:
            years  = sorted(year_counts.keys())
            counts = [year_counts[y] for y in years]
            colors = ['#4CAF50', '#8BC34A', '#CDDC39', '#FFC107', '#FF9800', '#F44336']
            bars   = ax.bar(years, counts, color=colors[:len(years)],
                            edgecolor='black', linewidth=0.5)
            ax.set_ylabel('Count', fontsize=9)
            ax.set_xlabel('Year Level', fontsize=9)
            for bar in bars:
                h = bar.get_height()
                ax.text(bar.get_x() + bar.get_width() / 2., h,
                        f'{int(h)}', ha='center', va='bottom', fontsize=8)
        else:
            ax.text(0.5, 0.5, 'No Data', ha='center', va='center', fontsize=12, color='gray')
            ax.set_xlim(0, 1); ax.set_ylim(0, 1)

        ax.set_title('Records by Year Level', fontsize=11, fontweight='bold', pad=10)
        ax.tick_params(axis='both', labelsize=8)
        fig.tight_layout(pad=0.5)
        return _make_canvas(fig)

    def _create_student_slip_distribution_chart(self, all_records):
        from matplotlib.figure import Figure
        fig = Figure(figsize=(5, 4), dpi=90, facecolor='white', edgecolor='none')
        ax  = fig.add_subplot(111)

        student_counts = Counter()
        for record in all_records:
            if len(record) > 0:
                name = record[0]
                if name and name != "Unknown":
                    student_counts[name] += 1

        if student_counts:
            top  = sorted(student_counts.items(), key=lambda x: x[1], reverse=True)[:6]
            names  = [n[:15] for n, _ in top]
            counts = [c for _, c in top]
            bars   = ax.barh(names, counts, color='#FF9800', edgecolor='black', linewidth=0.5)
            ax.set_xlabel('Slip Count', fontsize=9)
            for bar in bars:
                w = bar.get_width()
                ax.text(w, bar.get_y() + bar.get_height() / 2.,
                        f'{int(w)}', ha='left', va='center', fontsize=8, fontweight='bold')
        else:
            ax.text(0.5, 0.5, 'No Data', ha='center', va='center', fontsize=12, color='gray')
            ax.set_xlim(0, 1); ax.set_ylim(0, 1)

        ax.set_title('Top Students by Slips', fontsize=11, fontweight='bold', pad=10)
        ax.tick_params(axis='both', labelsize=8)
        fig.tight_layout(pad=0.5)
        return _make_canvas(fig)

    def _create_college_distribution_chart(self, college_data):
        from matplotlib.figure import Figure
        fig = Figure(figsize=(8, 4), dpi=90, facecolor='white', edgecolor='none')
        ax  = fig.add_subplot(111)

        college_colors = {
            "CEDAS": "#FF6B6B", "CABE": "#4ECDC4", "CCIS": "#95E1D3",
            "COE":   "#F9CA24", "CHS":  "#6C5CE7", "CSP":  "#A29BFE",
        }

        colleges, totals, colors = [], [], []
        for code, data in college_data.items():
            if data["total"] > 0:
                colleges.append(code)
                totals.append(data["total"])
                colors.append(college_colors.get(code, "#999999"))

        if colleges:
            x_pos = range(len(colleges))
            bars  = ax.bar(x_pos, totals, color=colors, edgecolor='black', linewidth=0.5)
            ax.set_ylabel('Total Records', fontsize=9)
            ax.set_xlabel('College', fontsize=9)
            ax.set_xticks(x_pos)
            ax.set_xticklabels(colleges, fontsize=8)
            for bar in bars:
                h = bar.get_height()
                ax.text(bar.get_x() + bar.get_width() / 2., h,
                        f'{int(h)}', ha='center', va='bottom', fontsize=9, fontweight='bold')
            ax.yaxis.grid(True, alpha=0.3, linestyle='--')
            ax.set_axisbelow(True)
        else:
            ax.text(0.5, 0.5, 'No Data', ha='center', va='center', fontsize=12, color='gray')
            ax.set_xlim(0, 1); ax.set_ylim(0, 1)

        ax.set_title('Records by College', fontsize=11, fontweight='bold', pad=10)
        fig.tight_layout(pad=0.5)
        return _make_canvas(fig)

    # ------------------------------------------------------------------
    # PDF Export
    # ------------------------------------------------------------------
    def _export_overview_report(self):
        try:
            from backend.db_blue_slip  import get_blue_slips
            from backend.db_green_slip import get_green_slips
            from backend.db_pink_slip  import get_pink_slips

            records_data = {
                'green': self._filter_records_by_period(get_green_slips(None) or [], date_field_index=6),
                'pink':  self._filter_records_by_period(get_pink_slips(None)  or [], date_field_index=5),
                'blue':  self._filter_records_by_period(get_blue_slips(None)  or [], date_field_index=6),
            }
            total = sum(len(v) for v in records_data.values())

            if total == 0:
                InfoDialog("No Data",
                           "No slip records available for this period.\n"
                           "Please select a different time period or date range.",
                           success=False, parent=self).exec_()
                return

            selected_period = self.period_cb.currentText() if hasattr(self, 'period_cb') \
                else datetime.now().strftime("%B %Y")

            temp_pdf = os.path.join(tempfile.gettempdir(), 'SCMS_Overview_Report.pdf')
            generate_overview_report(temp_pdf, records_data, period=selected_period)
            log_report_generated(self.staff_id, "Monthly Overview")
            PDFPreviewDialog(temp_pdf, "Monthly Overview Report", parent=self).exec_()
        except Exception as e:
            InfoDialog("Export Error", f"Failed to generate overview report:\n{str(e)}",
                       success=False, parent=self).exec_()

    def _export_slip_report(self, slip_type, title, subtitle, rows):
        if not rows:
            InfoDialog("No Data",
                       f"No {slip_type} slip records available for this period.",
                       success=False, parent=self).exec_()
            return
        try:
            records = [tuple(row) for row in rows]
            selected_period = self.period_cb.currentText() if hasattr(self, 'period_cb') \
                else datetime.now().strftime("%B %Y")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_pdf  = os.path.join(tempfile.gettempdir(),
                                     f'SCMS_{slip_type.upper()}_Report_{timestamp}.pdf')
            generate_slip_report(temp_pdf, slip_type, records, subtitle, period=selected_period)
            log_report_generated(self.staff_id, f"{slip_type.title()} Slip Report")
            PDFPreviewDialog(temp_pdf, title, parent=self).exec_()
        except Exception as e:
            InfoDialog("Export Error", f"Failed to generate {slip_type} slip report:\n{str(e)}",
                       success=False, parent=self).exec_()

    # ------------------------------------------------------------------
    # State helpers
    # ------------------------------------------------------------------
    def _update_print_button_state(self):
        try:
            from backend.db_blue_slip  import get_blue_slips
            from backend.db_green_slip import get_green_slips
            from backend.db_pink_slip  import get_pink_slips

            total = (
                len(self._filter_records_by_period(get_green_slips(None) or [], date_field_index=6)) +
                len(self._filter_records_by_period(get_pink_slips(None)  or [], date_field_index=5)) +
                len(self._filter_records_by_period(get_blue_slips(None)  or [], date_field_index=6))
            )
            if hasattr(self, 'top_print_btn'):
                self.top_print_btn.setEnabled(total > 0)
                self.top_print_btn.setToolTip("" if total > 0 else "No data available for this period")
        except Exception as e:
            logger.error(f"Failed to update print button state: {e}")

    def _rebuild_tabs(self):
        """Remove all tabs and rebuild them with fresh data."""
        if self._tabs is None:
            return
        current_idx = self._tabs.currentIndex()

        for idx in range(self._tabs.count() - 1, -1, -1):
            self._tabs.removeTab(idx)

        for widget, label in [
            (self._build_overview_tab(),   "   Overview "),
            (self._build_green_report(),   "   Green Slips "),
            (self._build_pink_report(),    "   Pink Slips "),
            (self._build_blue_report(),    "   Blue Slips "),
            (self._build_college_report(), "   By College "),
            (self._build_toplist_tab(),    "   Student Records "),
        ]:
            try:
                self._tabs.addTab(widget, label)
            except Exception as e:
                logger.error(f"Failed to rebuild tab '{label}': {e}", exc_info=True)

        if current_idx < self._tabs.count():
            self._tabs.setCurrentIndex(current_idx)

    def _on_slips_changed(self):
        logger.debug("Reports page: _on_slips_changed() called")
        try:
            self._update_print_button_state()
            self._rebuild_tabs()
        except Exception as e:
            logger.error(f"Failed to refresh reports: {e}", exc_info=True)

    def _on_period_changed(self):
        try:
            self._update_print_button_state()
            self._rebuild_tabs()
        except Exception as e:
            logger.error(f"Failed to refresh on period change: {e}", exc_info=True)