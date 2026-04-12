# =============================================================================
#  PDF Preview Dialog — PyQt5 Component for PDF Display
# =============================================================================
"""
PyQt5 dialog component for previewing PDF documents with export options.
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog,
    QFrame, QProgressBar, QComboBox
)
from PyQt5.QtCore import Qt, QTimer, QDate
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtGui import QFont, QIcon, QDesktopServices
from PyQt5.QtCore import QUrl, QThread, pyqtSignal
import subprocess
import os
from pathlib import Path
from datetime import datetime
import tempfile


# Color constants (match main UI)
NAVY = "#1a3a52"
GOLD = "#d4af37"
WHITE = "#ffffff"
OFF_WHITE = "#f8f9fa"
LIGHT_GRAY = "#e8e8e8"
TEXT_DARK = "#333333"


class PDFPreviewDialog(QDialog):
    """
    Dialog for previewing generated PDF documents with save/print options.
    """
    
    def __init__(self, pdf_path, document_title="Report", parent=None):
        """
        Initialize PDF Preview Dialog.
        
        Args:
            pdf_path: Path to the PDF file
            document_title: Title for the dialog
            parent: Parent widget
        """
        super().__init__(parent)
        self.pdf_path = pdf_path
        self.document_title = document_title
        
        self.setWindowTitle(f"PDF Preview - {document_title}")
        self.setMinimumSize(900, 700)
        self.setStyleSheet(f"QDialog {{ background: {WHITE}; }}")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        self._build()
        
        # Open PDF in default viewer after short delay
        QTimer.singleShot(500, self._open_preview)
    
    def _build(self):
        """Build the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # ── Header ────────────────────────────────────────────────────────────
        header = QFrame()
        header.setFixedHeight(70)
        header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {NAVY}, stop:1 #0f2438
                );
                border-bottom: 2px solid {GOLD};
            }}
        """)
        
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(20, 12, 20, 12)
        
        title_lbl = QLabel("📄  PDF Document Preview")
        title_lbl.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title_lbl.setStyleSheet(f"color: {GOLD}; background: transparent; border: none;")
        h_layout.addWidget(title_lbl)
        
        subtitle_lbl = QLabel(self.document_title)
        subtitle_lbl.setFont(QFont("Segoe UI", 11))
        subtitle_lbl.setStyleSheet(f"color: rgba(255,255,255,0.85); background: transparent; border: none; margin-left: 10px;")
        h_layout.addWidget(subtitle_lbl)
        
        h_layout.addStretch()
        
        status_lbl = QLabel("✓ Ready to preview, save, or print")
        status_lbl.setFont(QFont("Segoe UI", 10))
        status_lbl.setStyleSheet(f"color: #4CAF50; background: transparent; border: none;")
        h_layout.addWidget(status_lbl)
        
        layout.addWidget(header)
        
        # ── Info Bar ──────────────────────────────────────────────────────────
        info_bar = QFrame()
        info_bar.setFixedHeight(50)
        info_bar.setStyleSheet(f"""
            QFrame {{
                background: {OFF_WHITE};
                border-bottom: 1px solid {LIGHT_GRAY};
            }}
        """)
        
        info_layout = QHBoxLayout(info_bar)
        info_layout.setContentsMargins(20, 8, 20, 8)
        
        file_info = QLabel(f"📁 {Path(self.pdf_path).name}")
        file_info.setFont(QFont("Segoe UI", 10))
        file_info.setStyleSheet(f"color: {TEXT_DARK}; background: transparent; border: none;")
        info_layout.addWidget(file_info)
        
        size_kb = os.path.getsize(self.pdf_path) / 1024
        size_info = QLabel(f"Size: {size_kb:.1f} KB")
        size_info.setFont(QFont("Segoe UI", 9))
        size_info.setStyleSheet(f"color: #999; background: transparent; border: none;")
        info_layout.addWidget(size_info)
        
        time_info = QLabel(f"Generated: {datetime.now().strftime('%I:%M %p')}")
        time_info.setFont(QFont("Segoe UI", 9))
        time_info.setStyleSheet(f"color: #999; background: transparent; border: none;")
        info_layout.addWidget(time_info)
        
        info_layout.addStretch()
        
        layout.addWidget(info_bar)
        
        # ── Content Area (Placeholder) ────────────────────────────────────────
        content_frame = QFrame()
        content_frame.setStyleSheet(f"background: {WHITE};")
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        message = QLabel(
            "📖  PDF Document Preview\n\n"
            "The document preview is being prepared. It should open in your default PDF viewer.\n\n"
            "Use the buttons below to:\n"
            "• Save: Export the PDF to a location of your choice\n"
            "• Print: Send the document to your printer\n"
            "• Open: View the full PDF in your default viewer\n"
            "• Close: Close this preview dialog"
        )
        message.setFont(QFont("Segoe UI", 11))
        message.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_DARK};
                background: transparent;
                border: 2px solid {LIGHT_GRAY};
                border-radius: 8px;
                padding: 20px;
                line-height: 1.6;
            }}
        """)
        message.setWordWrap(True)
        content_layout.addWidget(message)
        content_layout.addStretch()
        
        layout.addWidget(content_frame, 1)
        
        # ── Footer / Action Buttons ───────────────────────────────────────────
        footer = QFrame()
        footer.setFixedHeight(70)
        footer.setStyleSheet(f"""
            QFrame {{
                background: {OFF_WHITE};
                border-top: 1px solid {LIGHT_GRAY};
            }}
        """)
        
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(20, 12, 20, 12)
        footer_layout.setSpacing(12)
        
        # Save button
        save_btn = QPushButton("💾  Save As")
        save_btn.setFixedHeight(40)
        save_btn.setFixedWidth(140)
        save_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background: {NAVY};
                color: {GOLD};
                border: none;
                border-radius: 6px;
                font-weight: bold;
                padding: 0 16px;
            }}
            QPushButton:hover {{
                background: {GOLD};
                color: {NAVY};
            }}
            QPushButton:pressed {{
                background: rgba(212, 175, 55, 0.7);
                color: {NAVY};
            }}
        """)
        save_btn.clicked.connect(self._save_pdf)
        footer_layout.addWidget(save_btn)
        
        # Print button
        print_btn = QPushButton("🖨️  Print")
        print_btn.setFixedHeight(40)
        print_btn.setFixedWidth(140)
        print_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        print_btn.setCursor(Qt.PointingHandCursor)
        print_btn.setStyleSheet(f"""
            QPushButton {{
                background: {NAVY};
                color: {GOLD};
                border: none;
                border-radius: 6px;
                font-weight: bold;
                padding: 0 16px;
            }}
            QPushButton:hover {{
                background: {GOLD};
                color: {NAVY};
            }}
            QPushButton:pressed {{
                background: rgba(212, 175, 55, 0.7);
                color: {NAVY};
            }}
        """)
        print_btn.clicked.connect(self._print_pdf)
        footer_layout.addWidget(print_btn)
        
        # Open button
        open_btn = QPushButton("👁️ Open Full PDF")
        open_btn.setFixedHeight(40)
        open_btn.setFixedWidth(140)
        open_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        open_btn.setCursor(Qt.PointingHandCursor)
        open_btn.setStyleSheet(f"""
            QPushButton {{
                background: #4CAF50;
                color: {WHITE};
                border: none;
                border-radius: 6px;
                font-weight: bold;
                padding: 0 16px;
            }}
            QPushButton:hover {{
                background: #45a049;
            }}
            QPushButton:pressed {{
                background: #3d8b40;
            }}
        """)
        open_btn.clicked.connect(self._open_pdf)
        footer_layout.addWidget(open_btn)
        
        footer_layout.addStretch()
        
        # Close button
        close_btn = QPushButton("✕  Close")
        close_btn.setFixedHeight(40)
        close_btn.setFixedWidth(140)
        close_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background: #f44336;
                color: {WHITE};
                border: none;
                border-radius: 6px;
                font-weight: bold;
                padding: 0 16px;
            }}
            QPushButton:hover {{
                background: #da190b;
            }}
            QPushButton:pressed {{
                background: #ba0000;
            }}
        """)
        close_btn.clicked.connect(self.accept)
        footer_layout.addWidget(close_btn)
        
        layout.addWidget(footer)
    
    def _open_preview(self):
        """Open the PDF in the default viewer."""
        try:
            # Windows
            os.startfile(self.pdf_path)
        except AttributeError:
            # macOS/Linux
            try:
                subprocess.run(['open', self.pdf_path])
            except:
                try:
                    subprocess.run(['xdg-open', self.pdf_path])
                except:
                    pass
    
    def _open_pdf(self):
        """Open PDF with the default application."""
        try:
            os.startfile(self.pdf_path)
        except AttributeError:
            try:
                subprocess.run(['open', self.pdf_path])
            except:
                try:
                    subprocess.run(['xdg-open', self.pdf_path])
                except:
                    pass
    
    def _save_pdf(self):
        """Save the PDF to a user-selected location."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"SCMS_Report_{timestamp}.pdf"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save PDF Report",
            default_filename,
            "PDF Files (*.pdf);;All Files (*.*)"
        )
        
        if file_path:
            try:
                # Copy the temporary PDF to the selected location
                with open(self.pdf_path, 'rb') as src:
                    with open(file_path, 'wb') as dst:
                        dst.write(src.read())
                
                from ui.components import InfoDialog
                InfoDialog(
                    "Success",
                    f"PDF saved successfully to:\n{file_path}",
                    success=True,
                    parent=self
                ).exec_()
            except Exception as e:
                from ui.components import InfoDialog
                InfoDialog(
                    "Save Error",
                    f"Failed to save PDF:\n{str(e)}",
                    success=False,
                    parent=self
                ).exec_()
    
    def _print_pdf(self):
        """Print the PDF document."""
        try:
            # On Windows, use default PDF printer
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setPageSize(QPrinter.A4)
            
            # Open print dialog
            print_dialog = QPrintDialog(printer, self)
            if print_dialog.exec_() == QDialog.Accepted:
                # Use system print command
                try:
                    os.startfile(self.pdf_path, 'print')
                except AttributeError:
                    subprocess.run(['lpr', self.pdf_path])
                
                from ui.components import InfoDialog
                InfoDialog(
                    "Print",
                    "Document sent to printer.",
                    success=True,
                    parent=self
                ).exec_()
        except Exception as e:
            from ui.components import InfoDialog
            InfoDialog(
                "Print Error",
                f"Failed to print document:\n{str(e)}",
                success=False,
                parent=self
            ).exec_()
