"""
ExamPilot AI Model Manager View
GT InnoX LLP
"""

from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QScrollArea, QFrame, QProgressBar, QMessageBox, QGridLayout
)
from PySide6.QtGui import QFont
from desktop.config import COLORS
from desktop.ui.components.widgets import CardFrame, StatusChip
from desktop.core.model_manager import model_manager
from desktop.ai.model_config import model_config
from desktop.utils.system_info import get_system_hardware_info
from desktop.utils.logger import logger

class ModelPullWorker(QThread):
    """Background worker for streaming model download."""
    progress_update = Signal(dict)
    finished = Signal(bool, str)

    def __init__(self, model_name: str):
        super().__init__()
        self.model_name = model_name

    def run(self):
        def on_progress(data):
            self.progress_update.emit(data)

        success, msg = model_manager.download_model(self.model_name, on_progress)
        self.finished.emit(success, msg)

class ModelManagerView(QWidget):
    """Controls local Ollama lifecycle, model downloads, and hardware recommendations."""
    status_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(f"background-color: {COLORS['bg_dark']};")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(20)

        # Header
        head_layout = QHBoxLayout()
        vbox = QVBoxLayout()
        title = QLabel("AI Model Manager")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")

        desc = QLabel("Manage offline local inference models running on Ollama. 100% private, zero paid cloud APIs.")
        desc.setFont(QFont("Segoe UI", 10))
        desc.setStyleSheet(f"color: {COLORS['text_muted']};")

        vbox.addWidget(title)
        vbox.addWidget(desc)
        head_layout.addLayout(vbox)
        head_layout.addStretch()

        self.btn_refresh = QPushButton("Refresh Status")
        self.btn_refresh.setFixedHeight(34)
        self.btn_refresh.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border_color']};
                color: {COLORS['text_primary']};
                border-radius: 6px;
                padding: 0 14px;
            }}
            QPushButton:hover {{
                border-color: {COLORS['accent_secondary']};
            }}
        """)
        self.btn_refresh.clicked.connect(self.refresh_status)
        head_layout.addWidget(self.btn_refresh)
        layout.addLayout(head_layout)

        # Readiness Chips
        chip_box = QHBoxLayout()
        self.chip_ollama = StatusChip("Service: Checking...", False)
        self.chip_active_model = StatusChip("Active Model: None", False)
        chip_box.addWidget(self.chip_ollama)
        chip_box.addWidget(self.chip_active_model)
        chip_box.addStretch()
        layout.addLayout(chip_box)

        # Hardware Recommendation Card
        hw_card = CardFrame()
        hw_vbox = QVBoxLayout(hw_card)
        hw_vbox.setSpacing(8)

        hw_title = QLabel("Hardware Profile & Model Recommendation")
        hw_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        hw_title.setStyleSheet(f"color: {COLORS['text_primary']};")
        hw_vbox.addWidget(hw_title)

        hw = get_system_hardware_info()
        self.lbl_hw_desc = QLabel(
            f"• Installed RAM: {hw['total_ram_gb']} GB ({hw['available_ram_gb']} GB available)\n"
            f"• Free Storage: {hw['free_disk_gb']} GB\n"
            f"• Recommendation: {hw['recommendation_notes']}"
        )
        self.lbl_hw_desc.setFont(QFont("Segoe UI", 10))
        self.lbl_hw_desc.setStyleSheet(f"color: {COLORS['text_muted']}; line-height: 1.5;")
        hw_vbox.addWidget(self.lbl_hw_desc)
        layout.addWidget(hw_card)

        # Active Model Selector Card
        active_card = CardFrame()
        act_vbox = QVBoxLayout(active_card)
        act_vbox.setSpacing(10)

        act_title = QLabel("Select Active AI Model for Inference")
        act_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        act_title.setStyleSheet(f"color: {COLORS['text_primary']};")
        act_vbox.addWidget(act_title)

        act_row = QHBoxLayout()
        self.combo_models = QComboBox()
        self.combo_models.setFixedHeight(36)
        self.combo_models.setMinimumWidth(260)
        self.combo_models.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border_color']};
                border-radius: 6px;
                color: {COLORS['text_primary']};
                padding-left: 10px;
            }}
        """)
        self.combo_models.currentIndexChanged.connect(self.on_active_model_changed)
        act_row.addWidget(self.combo_models)
        act_row.addStretch()
        act_vbox.addLayout(act_row)
        layout.addWidget(active_card)

        # Model Download Progress Bar (Hidden by default)
        self.download_card = CardFrame()
        dl_vbox = QVBoxLayout(self.download_card)
        dl_vbox.setSpacing(6)

        self.lbl_dl_status = QLabel("Downloading model...")
        self.lbl_dl_status.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        self.lbl_dl_status.setStyleSheet(f"color: {COLORS['accent_secondary']};")
        dl_vbox.addWidget(self.lbl_dl_status)

        self.bar_dl = QProgressBar()
        self.bar_dl.setFixedHeight(10)
        self.bar_dl.setRange(0, 100)
        self.bar_dl.setValue(0)
        self.bar_dl.setStyleSheet(f"""
            QProgressBar {{
                background-color: {COLORS['bg_secondary']};
                border-radius: 5px;
                border: none;
            }}
            QProgressBar::chunk {{
                background-color: {COLORS['accent_primary']};
                border-radius: 5px;
            }}
        """)
        dl_vbox.addWidget(self.bar_dl)
        self.download_card.hide()
        layout.addWidget(self.download_card)

        # Recommended Models Catalog
        cat_card = CardFrame()
        cat_vbox = QVBoxLayout(cat_card)
        cat_vbox.setSpacing(12)

        cat_title = QLabel("Recommended Open-Source Models")
        cat_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        cat_title.setStyleSheet(f"color: {COLORS['text_primary']};")
        cat_vbox.addWidget(cat_title)

        self.catalog_vbox = QVBoxLayout()
        self.catalog_vbox.setSpacing(10)
        cat_vbox.addLayout(self.catalog_vbox)
        layout.addWidget(cat_card)

        # Ollama Troubleshooting & Setup Guide
        setup_card = CardFrame()
        setup_vbox = QVBoxLayout(setup_card)
        setup_title = QLabel("Ollama Setup Instructions")
        setup_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        setup_title.setStyleSheet(f"color: {COLORS['text_primary']};")
        setup_vbox.addWidget(setup_title)

        guide_txt = QLabel(
            "1. Download Ollama from https://ollama.com/download/windows (or run scripts/setup_ollama.bat)\n"
            "2. Start Ollama. The service runs locally on port 11434.\n"
            "3. Click 'Download' on any model above to install it directly onto your computer.\n"
            "4. All question processing operates 100% offline with zero cloud API keys."
        )
        guide_txt.setFont(QFont("Segoe UI", 9))
        guide_txt.setStyleSheet(f"color: {COLORS['text_muted']}; line-height: 1.5;")
        setup_vbox.addWidget(guide_txt)
        layout.addWidget(setup_card)

        layout.addStretch()
        scroll.setWidget(container)
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(scroll)

    def refresh_status(self):
        status = model_manager.get_status()
        is_running = status["service_running"]
        active = status["active_model"]
        installed = status["installed_models"]
        installed_names = [m["name"] for m in installed]

        if is_running:
            self.chip_ollama.set_status(True, "Service: Active (localhost:11434)")
        else:
            self.chip_ollama.set_status(False, "Service: Stopped / Not Installed")

        self.chip_active_model.set_status(bool(installed_names), f"Active: {active}")

        # Update Dropdown
        self.combo_models.blockSignals(True)
        self.combo_models.clear()
        if installed_names:
            for m in installed_names:
                self.combo_models.addItem(m, m)
            if active in installed_names:
                self.combo_models.setCurrentText(active)
        else:
            self.combo_models.addItem("No models installed locally", None)
        self.combo_models.blockSignals(False)

        # Render Recommended Catalog
        while self.catalog_vbox.count():
            item = self.catalog_vbox.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        catalog = status["recommended_catalog"]
        for cat_item in catalog:
            m_name = cat_item["name"]
            is_downloaded = any(m_name in inst or inst in m_name for inst in installed_names)

            row_frame = QFrame()
            row_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {COLORS['bg_secondary']};
                    border: 1px solid {COLORS['border_color']};
                    border-radius: 8px;
                    padding: 10px;
                }}
            """)
            row_layout = QHBoxLayout(row_frame)
            row_layout.setSpacing(12)

            info_vbox = QVBoxLayout()
            m_lbl = QLabel(cat_item["label"])
            m_lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            m_lbl.setStyleSheet(f"color: {COLORS['text_primary']};")

            m_desc = QLabel(f"{cat_item['description']} • Size: ~{cat_item['disk_gb']} GB • RAM: {cat_item['ram_gb']} GB+")
            m_desc.setFont(QFont("Segoe UI", 8))
            m_desc.setStyleSheet(f"color: {COLORS['text_muted']};")

            info_vbox.addWidget(m_lbl)
            info_vbox.addWidget(m_desc)
            row_layout.addLayout(info_vbox)
            row_layout.addStretch()

            btn_action = QPushButton("Installed" if is_downloaded else f"Download ({cat_item['disk_gb']} GB)")
            btn_action.setFixedHeight(32)
            btn_action.setEnabled(not is_downloaded and is_running)
            btn_action.setStyleSheet(f"""
                QPushButton {{
                    background-color: {'rgba(34, 197, 94, 0.2)' if is_downloaded else COLORS['accent_primary']};
                    color: {COLORS['success'] if is_downloaded else 'white'};
                    border: 1px solid {COLORS['success'] if is_downloaded else 'transparent'};
                    border-radius: 6px;
                    padding: 0 12px;
                    font-size: 10px;
                    font-weight: 600;
                }}
                QPushButton:hover:enabled {{
                    background-color: {COLORS['accent_primary_hover']};
                }}
            """)
            if not is_downloaded:
                btn_action.clicked.connect(lambda _, m=m_name: self.start_download(m))

            row_layout.addWidget(btn_action)
            self.catalog_vbox.addWidget(row_frame)

        self.status_changed.emit()

    def on_active_model_changed(self):
        selected = self.combo_models.currentData()
        if selected:
            model_manager.set_active_model(selected)
            self.chip_active_model.set_status(True, f"Active: {selected}")

    def start_download(self, model_name: str):
        confirm = QMessageBox.question(
            self, "Confirm Model Download",
            f"Download '{model_name}' to your local computer?\nEnsure you have an active internet connection for the initial download.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        self.download_card.show()
        self.lbl_dl_status.setText(f"Connecting to download '{model_name}'...")
        self.bar_dl.setValue(0)

        self.worker = ModelPullWorker(model_name)
        self.worker.progress_update.connect(self._on_download_progress)
        self.worker.finished.connect(self._on_download_finished)
        self.worker.start()

    def _on_download_progress(self, progress: dict):
        status = progress.get("status", "")
        percent = int(progress.get("percent", 0))
        self.lbl_dl_status.setText(f"{status} ({percent}%)")
        self.bar_dl.setValue(percent)

    def _on_download_finished(self, success: bool, message: str):
        self.download_card.hide()
        if success:
            QMessageBox.information(self, "Success", f"Model download complete: {message}")
            self.refresh_status()
        else:
            QMessageBox.critical(self, "Download Failed", f"Could not download model: {message}")

