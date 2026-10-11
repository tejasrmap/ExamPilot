"""
ExamPilot Main Dashboard View
GT InnoX LLP
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGridLayout, QScrollArea, QFrame, QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtGui import QFont, QIcon
from desktop.config import COLORS
from desktop.ui.components.widgets import CardFrame, StatusChip
from desktop.database.repository import repository
from desktop.core.model_manager import model_manager
from desktop.core.ocr_engine import ocr_engine
from desktop.utils.system_info import get_system_hardware_info
from desktop.utils.helpers import format_timestamp, truncate_text

class DashboardView(QWidget):
    """Primary overview dashboard showing stats, system readiness, and quick actions."""
    navigate_to = Signal(str)  # Signal to navigate to another view
    start_capture_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(28, 24, 28, 24)
        main_layout.setSpacing(20)

        # Top Header & Quick Action
        top_bar = QHBoxLayout()
        header_text = QVBoxLayout()
        title = QLabel("Dashboard")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")

        subtitle = QLabel("Welcome to ExamPilot • Offline-First AI MCQ Practice Assistant")
        subtitle.setFont(QFont("Segoe UI", 10))
        subtitle.setStyleSheet(f"color: {COLORS['text_muted']};")

        header_text.addWidget(title)
        header_text.addWidget(subtitle)
        top_bar.addLayout(header_text)
        top_bar.addStretch()

        self.btn_capture = QPushButton("  Capture Practice MCQ (Ctrl+Shift+Q)")
        self.btn_capture.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        self.btn_capture.setFixedHeight(40)
        self.btn_capture.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_capture.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['accent_primary']}, stop:1 {COLORS['accent_secondary']});
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 0 16px;
            }}
            QPushButton:hover {{
                background: {COLORS['accent_primary_hover']};
            }}
        """)
        self.btn_capture.clicked.connect(self.start_capture_requested.emit)
        top_bar.addWidget(self.btn_capture)

        main_layout.addLayout(top_bar)

        # Status Readiness Bar
        status_bar = QHBoxLayout()
        status_bar.setSpacing(12)
        
        self.chip_ollama = StatusChip("Local AI: Checking...", False)
        self.chip_ocr = StatusChip("OCR Engine: Checking...", False)
        self.chip_model = StatusChip("Active Model: Checking...", False)

        status_bar.addWidget(self.chip_ollama)
        status_bar.addWidget(self.chip_ocr)
        status_bar.addWidget(self.chip_model)
        status_bar.addStretch()
        main_layout.addLayout(status_bar)

        # Metrics 4-Card Grid
        metrics_grid = QGridLayout()
        metrics_grid.setSpacing(16)

        self.card_total = self._create_metric_card("Questions Processed", "0", "Total questions analyzed", COLORS["accent_primary"])
        self.card_accuracy = self._create_metric_card("Practice Accuracy", "100%", "Based on unflagged questions", COLORS["success"])
        self.card_confidence = self._create_metric_card("Average Confidence", "0%", "Calibrated heuristic certainty", COLORS["accent_secondary"])
        self.card_sessions = self._create_metric_card("Practice Sessions", "0", "Completed learning runs", COLORS["warning"])

        metrics_grid.addWidget(self.card_total, 0, 0)
        metrics_grid.addWidget(self.card_accuracy, 0, 1)
        metrics_grid.addWidget(self.card_confidence, 0, 2)
        metrics_grid.addWidget(self.card_sessions, 0, 3)

        main_layout.addLayout(metrics_grid)

        # Split Section: Recent Questions (Left) & Hardware Readiness (Right)
        split_layout = QHBoxLayout()
        split_layout.setSpacing(16)

        # Recent Questions Card
        recent_card = CardFrame()
        recent_vbox = QVBoxLayout(recent_card)
        recent_vbox.setContentsMargins(16, 16, 16, 16)
        recent_vbox.setSpacing(12)

        recent_head = QHBoxLayout()
        recent_title = QLabel("Recent Practice Questions")
        recent_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        recent_title.setStyleSheet(f"color: {COLORS['text_primary']};")
        recent_head.addWidget(recent_title)
        recent_head.addStretch()

        btn_view_all = QPushButton("View All History →")
        btn_view_all.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
        btn_view_all.setStyleSheet(f"color: {COLORS['accent_secondary']}; background: transparent; border: none; cursor: pointer;")
        btn_view_all.clicked.connect(lambda: self.navigate_to.emit("history"))
        recent_head.addWidget(btn_view_all)
        recent_vbox.addLayout(recent_head)

        self.recent_table = QTableWidget()
        self.recent_table.setColumnCount(4)
        self.recent_table.setHorizontalHeaderLabels(["Subject", "Question Snippet", "Answer", "Confidence"])
        self.recent_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.recent_table.verticalHeader().setVisible(False)
        self.recent_table.setShowGrid(False)
        self.recent_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.recent_table.setAlternatingRowColors(True)
        self.recent_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {COLORS['bg_secondary']};
                alternate-background-color: {COLORS['bg_card']};
                border: 1px solid {COLORS['border_color']};
                border-radius: 8px;
                color: {COLORS['text_primary']};
                font-size: 11px;
            }}
            QHeaderView::section {{
                background-color: {COLORS['bg_secondary']};
                color: {COLORS['text_muted']};
                padding: 6px;
                border: none;
                font-weight: 600;
            }}
        """)
        recent_vbox.addWidget(self.recent_table)
        split_layout.addWidget(recent_card, 65)

        # Hardware & Model Readiness Card (Right)
        hw_card = CardFrame()
        hw_vbox = QVBoxLayout(hw_card)
        hw_vbox.setContentsMargins(16, 16, 16, 16)
        hw_vbox.setSpacing(12)

        hw_title = QLabel("Hardware & AI Tier")
        hw_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        hw_title.setStyleSheet(f"color: {COLORS['text_primary']};")
        hw_vbox.addWidget(hw_title)

        hw_info = get_system_hardware_info()
        self.lbl_ram = QLabel(f"RAM: {hw_info['total_ram_gb']} GB total ({hw_info['available_ram_gb']} GB available)")
        self.lbl_cpu = QLabel(f"CPU: {hw_info['cpu_threads']} Threads @ {hw_info['cpu_freq_ghz']} GHz")
        self.lbl_disk = QLabel(f"Free Storage: {hw_info['free_disk_gb']} GB free")
        self.lbl_tier = QLabel(f"Recommended Tier:\n{hw_info['tier_label']}")
        self.lbl_tier.setStyleSheet(f"color: {COLORS['accent_secondary']}; font-weight: bold;")
        self.lbl_tier.setWordWrap(True)

        for w in [self.lbl_ram, self.lbl_cpu, self.lbl_disk, self.lbl_tier]:
            w.setFont(QFont("Segoe UI", 10))
            w.setStyleSheet(f"color: {COLORS['text_muted']};")
            hw_vbox.addWidget(w)

        hw_vbox.addStretch()

        btn_manage_models = QPushButton("Manage AI Models")
        btn_manage_models.setFixedHeight(36)
        btn_manage_models.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        btn_manage_models.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border_color']};
                color: {COLORS['text_primary']};
                border-radius: 6px;
            }}
            QPushButton:hover {{
                border-color: {COLORS['accent_primary']};
                color: {COLORS['accent_primary']};
            }}
        """)
        btn_manage_models.clicked.connect(lambda: self.navigate_to.emit("models"))
        hw_vbox.addWidget(btn_manage_models)

        split_layout.addWidget(hw_card, 35)
        main_layout.addLayout(split_layout)

    def _create_metric_card(self, title: str, value: str, note: str, accent_color: str) -> CardFrame:
        card = CardFrame()
        card.setFixedHeight(115)
        vbox = QVBoxLayout(card)
        vbox.setContentsMargins(16, 12, 16, 12)
        vbox.setSpacing(4)

        t_lbl = QLabel(title)
        t_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
        t_lbl.setStyleSheet(f"color: {COLORS['text_muted']}; text-transform: uppercase; letter-spacing: 0.5px;")

        v_lbl = QLabel(value)
        v_lbl.setObjectName("val")
        v_lbl.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        v_lbl.setStyleSheet(f"color: {accent_color};")

        n_lbl = QLabel(note)
        n_lbl.setFont(QFont("Segoe UI", 8))
        n_lbl.setStyleSheet(f"color: {COLORS['text_muted']};")

        vbox.addWidget(t_lbl)
        vbox.addWidget(v_lbl)
        vbox.addWidget(n_lbl)
        return card

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_data()

    def refresh_data(self):
        """Refresh dashboard statistics and status indicators."""
        # Query repository
        analytics = repository.get_dashboard_analytics()
        self.card_total.findChild(QLabel, "val").setText(str(analytics["total_questions"]))
        self.card_accuracy.findChild(QLabel, "val").setText(f"{analytics['accuracy']}%")
        self.card_confidence.findChild(QLabel, "val").setText(f"{analytics['avg_confidence']}%")
        self.card_sessions.findChild(QLabel, "val").setText(str(analytics["sessions_count"]))

        # Populate recent questions
        recent = analytics["recent_questions"]
        self.recent_table.setRowCount(len(recent))
        for r_idx, q in enumerate(recent):
            item_subj = QTableWidgetItem(q["subject"])
            item_q = QTableWidgetItem(truncate_text(q["question_text"], 150))
            item_ans = QTableWidgetItem(f"Option {q['suggested_answer']}" if q["suggested_answer"] else "-")
            item_conf = QTableWidgetItem(f"{int(round((q['confidence'] or 0) * 100))}%")

            for item in [item_subj, item_q, item_ans, item_conf]:
                item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)

            self.recent_table.setItem(r_idx, 0, item_subj)
            self.recent_table.setItem(r_idx, 1, item_q)
            self.recent_table.setItem(r_idx, 2, item_ans)
            self.recent_table.setItem(r_idx, 3, item_conf)

        # Update OCR Engine Status
        ocr_avail = ocr_engine.is_available()
        self.chip_ocr.set_status(
            ocr_avail,
            "OCR Engine: Active" if ocr_avail else "OCR Engine: Offline"
        )

        # Check Ollama and Model Status
        status = model_manager.get_status()
        is_running = status["service_running"]
        installed_models = [m["name"] for m in status.get("installed_models", [])]
        active_model = status["active_model"]

        # Ensure active_model reflects an installed model if default 7B is not downloaded
        if active_model not in installed_models and installed_models:
            active_model = installed_models[0]
            model_manager.set_active_model(active_model)

        if is_running:
            self.chip_ollama.set_status(True, "Local AI: Connected (11434)")
            if installed_models:
                self.chip_model.set_status(True, f"Model: {active_model}")
            else:
                self.chip_model.set_status(False, "No Models Installed")
        else:
            self.chip_ollama.set_status(False, "Local AI: Disconnected")
            self.chip_model.set_status(False, "Model: Offline")

