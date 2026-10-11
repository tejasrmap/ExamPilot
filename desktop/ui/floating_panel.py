"""
ExamPilot Floating Learning Assistant Panel
Compact, draggable, always-on-top floating helper widget.
GT InnoX LLP
"""

from PySide6.QtCore import Qt, QPoint, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QCheckBox, QFrame, QScrollArea, QProgressBar
)
from PySide6.QtGui import QFont, QCursor
from desktop.config import COLORS
from desktop.ui.components.widgets import ConfidenceMeter
from desktop.utils.helpers import truncate_text

class FloatingPanel(QWidget):
    """Compact floating assistant for non-intrusive desktop practice."""
    capture_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.drag_position = QPoint()
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.resize(380, 500)
        self.setStyleSheet(f"""
            FloatingPanel {{
                background-color: {COLORS['bg_dark']};
                border: 1px solid {COLORS['border_color']};
                border-radius: 12px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 14)
        layout.setSpacing(10)

        # Custom Draggable Title Bar
        title_bar = QHBoxLayout()
        title_bar.setSpacing(6)

        self.title_lbl = QLabel("ExamPilot Assistant")
        self.title_lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.title_lbl.setStyleSheet(f"color: {COLORS['text_primary']};")
        title_bar.addWidget(self.title_lbl)
        title_bar.addStretch()

        # Always on top toggle
        self.chk_pin = QCheckBox("Pin")
        self.chk_pin.setChecked(True)
        self.chk_pin.setFont(QFont("Segoe UI", 8))
        self.chk_pin.setStyleSheet(f"color: {COLORS['text_muted']};")
        self.chk_pin.stateChanged.connect(self.toggle_always_on_top)
        title_bar.addWidget(self.chk_pin)

        # Minimize Button
        btn_min = QPushButton("–")
        btn_min.setFixedSize(22, 22)
        btn_min.setStyleSheet(f"color: {COLORS['text_muted']}; background: transparent; border: none; font-size: 14px;")
        btn_min.clicked.connect(self.showMinimized)
        title_bar.addWidget(btn_min)

        # Close Button
        btn_close = QPushButton("✕")
        btn_close.setFixedSize(22, 22)
        btn_close.setStyleSheet(f"color: {COLORS['text_muted']}; background: transparent; border: none; font-size: 12px;")
        btn_close.clicked.connect(self.hide)
        title_bar.addWidget(btn_close)

        layout.addLayout(title_bar)

        # Quick Capture Button
        self.btn_capture = QPushButton("Capture MCQ (Ctrl+Shift+Q)")
        self.btn_capture.setFixedHeight(34)
        self.btn_capture.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_capture.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['accent_primary']}, stop:1 {COLORS['accent_secondary']});
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 600;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background: {COLORS['accent_primary_hover']};
            }}
        """)
        self.btn_capture.clicked.connect(self.capture_requested.emit)
        layout.addWidget(self.btn_capture)

        # Indeterminate Progress Bar for Inference
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setFixedHeight(3)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet(f"background: transparent; border: none;")
        self.progress.hide()
        layout.addWidget(self.progress)

        # Scrollable Content Area for Answer & Explanations
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(f"background-color: {COLORS['bg_dark']};")

        content_widget = QWidget()
        self.content_vbox = QVBoxLayout(content_widget)
        self.content_vbox.setContentsMargins(0, 0, 0, 0)
        self.content_vbox.setSpacing(8)

        # Suggested Answer Card
        self.ans_frame = QFrame()
        self.ans_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_card']};
                border: 1px solid {COLORS['border_color']};
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        ans_vbox = QVBoxLayout(self.ans_frame)
        ans_vbox.setSpacing(4)

        self.lbl_suggested = QLabel("Suggested: Waiting for capture...")
        self.lbl_suggested.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.lbl_suggested.setStyleSheet(f"color: {COLORS['success']};")
        ans_vbox.addWidget(self.lbl_suggested)

        self.conf_meter = ConfidenceMeter()
        ans_vbox.addWidget(self.conf_meter)
        self.content_vbox.addWidget(self.ans_frame)

        # Explanation Box
        self.lbl_explanation = QLabel("Select an MCQ on your screen to extract text and analyze options.")
        self.lbl_explanation.setWordWrap(True)
        self.lbl_explanation.setFont(QFont("Segoe UI", 9))
        self.lbl_explanation.setStyleSheet(f"""
            background-color: {COLORS['bg_secondary']};
            border-left: 2px solid {COLORS['accent_secondary']};
            border-radius: 6px;
            padding: 8px;
            color: {COLORS['text_primary']};
        """)
        self.content_vbox.addWidget(self.lbl_explanation)

        # Options Container
        self.options_vbox = QVBoxLayout()
        self.options_vbox.setSpacing(4)
        self.content_vbox.addLayout(self.options_vbox)

        scroll.setWidget(content_widget)
        layout.addWidget(scroll)

    def set_processing(self, is_processing: bool):
        if is_processing:
            self.progress.show()
            self.lbl_suggested.setText("Analyzing with local AI...")
        else:
            self.progress.hide()

    def update_result(self, data: dict):
        self.set_processing(False)
        suggested = data.get("suggested_answer", "-")
        ans_text = data.get("answer_text", "")
        detected_subj = data.get("detected_subject", "")
        prefix = f"[{detected_subj}] " if detected_subj else ""
        self.lbl_suggested.setText(f"{prefix}Option {suggested} ({truncate_text(ans_text, 28)})")
        self.conf_meter.set_confidence(data.get("confidence", 0.85))
        self.lbl_explanation.setText(data.get("explanation", ""))

        # Clear previous options
        while self.options_vbox.count():
            item = self.options_vbox.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        analysis = data.get("option_analysis", {})
        for opt, exp in sorted(analysis.items()):
            is_correct = (opt == suggested)
            opt_lbl = QLabel(f"• Option {opt}: {exp}")
            opt_lbl.setWordWrap(True)
            opt_lbl.setFont(QFont("Segoe UI", 8))
            opt_lbl.setStyleSheet(f"color: {COLORS['success'] if is_correct else COLORS['text_muted']};")
            self.options_vbox.addWidget(opt_lbl)

    def toggle_always_on_top(self, state):
        if state == Qt.CheckState.Checked.value:
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        else:
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, False)
        self.show()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

