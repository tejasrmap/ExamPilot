"""
ExamPilot Reusable UI Components
GT InnoX LLP
"""

from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QProgressBar
)
from PySide6.QtGui import QFont, QColor
from desktop.config import COLORS

class CardFrame(QFrame):
    """Modern dark theme elevated card container."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            CardFrame {{
                background-color: {COLORS["bg_card"]};
                border: 1px solid {COLORS["border_color"]};
                border-radius: 10px;
                padding: 14px;
            }}
        """)

class StatusChip(QFrame):
    """Pill badge showing status with colored dot indicator."""
    def __init__(self, label: str, is_active: bool = False, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(8, 4, 10, 4)
        self.layout.setSpacing(6)

        self.dot = QLabel()
        self.dot.setFixedSize(8, 8)
        self.text_label = QLabel(label)
        self.text_label.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))

        self.layout.addWidget(self.dot)
        self.layout.addWidget(self.text_label)
        self.set_status(is_active, label)

    def set_status(self, is_active: bool, text: str = ""):
        if text:
            self.text_label.setText(text)
        
        bg_col = "rgba(34, 197, 94, 0.15)" if is_active else "rgba(239, 68, 68, 0.15)"
        text_col = COLORS["success"] if is_active else COLORS["danger"]
        dot_col = COLORS["success"] if is_active else COLORS["danger"]
        border_col = COLORS["success"] if is_active else COLORS["danger"]

        self.setStyleSheet(f"""
            StatusChip {{
                background-color: {bg_col};
                border: 1px solid {border_col};
                border-radius: 12px;
            }}
            QLabel {{
                color: {text_col};
            }}
        """)
        self.dot.setStyleSheet(f"background-color: {dot_col}; border-radius: 4px;")

class ConfidenceMeter(QWidget):
    """Visual meter showing calibrated confidence percentage."""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        header_layout = QHBoxLayout()
        self.title_label = QLabel("Calibrated Confidence")
        self.title_label.setFont(QFont("Segoe UI", 9))
        self.title_label.setStyleSheet(f"color: {COLORS['text_muted']};")

        self.val_label = QLabel("0%")
        self.val_label.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.val_label.setStyleSheet(f"color: {COLORS['accent_secondary']};")

        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.val_label)

        self.bar = QProgressBar()
        self.bar.setFixedHeight(8)
        self.bar.setTextVisible(False)
        self.bar.setRange(0, 100)
        self.bar.setValue(0)
        self.bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {COLORS['bg_secondary']};
                border-radius: 4px;
                border: none;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['accent_primary']}, stop:1 {COLORS['accent_secondary']});
                border-radius: 4px;
            }}
        """)

        layout.addLayout(header_layout)
        layout.addWidget(self.bar)

    def set_confidence(self, score: float):
        percent = int(round(score * 100))
        self.val_label.setText(f"{percent}%")
        self.bar.setValue(percent)

        if percent >= 85:
            col = COLORS["success"]
        elif percent >= 60:
            col = COLORS["warning"]
        else:
            col = COLORS["danger"]
        self.val_label.setStyleSheet(f"color: {col}; font-weight: bold;")

