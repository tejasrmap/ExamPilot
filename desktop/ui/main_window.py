"""
ExamPilot Main Application Window
GT InnoX LLP — Understand Questions. Learn the Answers.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QStackedWidget, QFrame, QButtonGroup
)
from PySide6.QtGui import QFont, QIcon, QPixmap
import os

from desktop.config import (
    COLORS, APP_NAME, APP_TAGLINE, APP_VERSION, COMPANY_NAME, ICONS_DIR
)
from desktop.ui.dashboard import DashboardView
from desktop.ui.question_view import PracticeAssistantView
from desktop.ui.history_view import HistoryView
from desktop.ui.analytics_view import AnalyticsView
from desktop.ui.model_manager import ModelManagerView
from desktop.ui.settings_view import SettingsView
from desktop.ui.floating_panel import FloatingPanel
from desktop.core.capture import SnippetOverlayWidget, HotkeyListener
from desktop.utils.logger import logger

class MainWindow(QMainWindow):
    """Primary commercial desktop application window for ExamPilot."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} — {APP_TAGLINE} [{COMPANY_NAME}]")
        self.resize(1180, 780)
        self.setMinimumSize(960, 640)

        # App Icon
        icon_path = str(ICONS_DIR / "icon_48x48.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.snippet_overlay = SnippetOverlayWidget()
        self.snippet_overlay.snippet_captured.connect(self.on_snippet_captured)

        self.floating_panel = FloatingPanel()
        self.floating_panel.capture_requested.connect(self.trigger_capture)

        self.hotkey_listener = HotkeyListener()
        self.hotkey_listener.hotkey_triggered.connect(self.trigger_capture)
        self.hotkey_listener.start()

        self.init_ui()

    def init_ui(self):
        # Base container
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        central_widget.setStyleSheet(f"background-color: {COLORS['bg_dark']};")

        root_layout = QHBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # 1. Left Navigation Sidebar
        sidebar = self._create_sidebar()
        root_layout.addWidget(sidebar)

        # 2. Main Workspace Layout (Top Status Bar + Stacked Pages)
        content_vbox = QVBoxLayout()
        content_vbox.setContentsMargins(0, 0, 0, 0)
        content_vbox.setSpacing(0)

        top_header = self._create_top_header()
        content_vbox.addWidget(top_header)

        # Stacked Widget for Views
        self.stacked_widget = QStackedWidget()
        
        self.dashboard_view = DashboardView()
        self.dashboard_view.navigate_to.connect(self.navigate_by_name)
        self.dashboard_view.start_capture_requested.connect(self.trigger_capture)

        self.practice_view = PracticeAssistantView()
        self.practice_view.start_capture_requested.connect(self.trigger_capture)
        self.practice_view.analysis_completed.connect(self.floating_panel.update_result)

        self.history_view = HistoryView()
        self.analytics_view = AnalyticsView()
        
        self.model_view = ModelManagerView()
        self.model_view.status_changed.connect(self.dashboard_view.refresh_data)

        self.settings_view = SettingsView()

        self.stacked_widget.addWidget(self.dashboard_view)    # index 0
        self.stacked_widget.addWidget(self.practice_view)     # index 1
        self.stacked_widget.addWidget(self.history_view)      # index 2
        self.stacked_widget.addWidget(self.analytics_view)    # index 3
        self.stacked_widget.addWidget(self.model_view)        # index 4
        self.stacked_widget.addWidget(self.settings_view)     # index 5

        content_vbox.addWidget(self.stacked_widget)
        root_layout.addLayout(content_vbox)

        # Initial navigation & data load
        self.navigate_to_index(0)
        self.model_view.refresh_status()

    def _create_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setFixedWidth(230)
        sidebar.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_secondary']};
                border-right: 1px solid {COLORS['border_color']};
            }}
        """)
        vbox = QVBoxLayout(sidebar)
        vbox.setContentsMargins(14, 20, 14, 20)
        vbox.setSpacing(6)

        # Brand header in sidebar
        brand_hbox = QHBoxLayout()
        logo_lbl = QLabel()
        logo_png = str(ICONS_DIR / "icon_32x32.png")
        if os.path.exists(logo_png):
            logo_lbl.setPixmap(QPixmap(logo_png))
        brand_hbox.addWidget(logo_lbl)

        brand_text_vbox = QVBoxLayout()
        brand_title = QLabel(APP_NAME)
        brand_title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        brand_title.setStyleSheet(f"color: {COLORS['text_primary']}; letter-spacing: -0.2px;")

        brand_co = QLabel("GT InnoX LLP")
        brand_co.setFont(QFont("Segoe UI", 8, QFont.Weight.Medium))
        brand_co.setStyleSheet(f"color: {COLORS['accent_secondary']};")

        brand_text_vbox.addWidget(brand_title)
        brand_text_vbox.addWidget(brand_co)
        brand_hbox.addLayout(brand_text_vbox)
        brand_hbox.addStretch()
        vbox.addLayout(brand_hbox)

        vbox.addSpacing(16)

        # Nav Buttons Group
        self.nav_btn_group = QButtonGroup(self)
        self.nav_btn_group.setExclusive(True)

        nav_items = [
            ("Dashboard", 0),
            ("Practice Assistant", 1),
            ("Question History", 2),
            ("Performance Analytics", 3),
            ("AI Model Manager", 4),
            ("Settings", 5)
        ]

        for text, index in nav_items:
            btn = QPushButton(f"  {text}")
            btn.setFixedHeight(38)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
            btn.setStyleSheet(f"""
                QPushButton {{
                    text-align: left;
                    padding-left: 14px;
                    border-radius: 6px;
                    color: {COLORS['text_muted']};
                    background-color: transparent;
                    border: none;
                    outline: none;
                }}
                QPushButton:focus {{
                    outline: none;
                    border: none;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['bg_card']};
                    color: {COLORS['text_primary']};
                }}
                QPushButton:checked {{
                    background-color: rgba(99, 102, 241, 0.22);
                    color: {COLORS['accent_secondary']};
                    border-left: 4px solid {COLORS['accent_primary']};
                    font-weight: 600;
                }}
            """)
            self.nav_btn_group.addButton(btn, index)
            vbox.addWidget(btn)

        self.nav_btn_group.idClicked.connect(self.navigate_to_index)

        vbox.addStretch()

        # Floating panel launcher button in sidebar
        btn_float = QPushButton("Launch Floating Panel")
        btn_float.setFixedHeight(34)
        btn_float.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
        btn_float.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['bg_card']};
                border: 1px solid {COLORS['border_color']};
                color: {COLORS['accent_secondary']};
                border-radius: 6px;
            }}
            QPushButton:hover {{
                border-color: {COLORS['accent_secondary']};
                background-color: {COLORS['bg_card_hover']};
            }}
        """)
        btn_float.clicked.connect(self.toggle_floating_panel)
        vbox.addWidget(btn_float)

        # Version stamp
        lbl_ver = QLabel(f"v{APP_VERSION} • Offline-First")
        lbl_ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_ver.setFont(QFont("Segoe UI", 8))
        lbl_ver.setStyleSheet(f"color: {COLORS['text_muted']};")
        vbox.addWidget(lbl_ver)

        return sidebar

    def _create_top_header(self) -> QFrame:
        header = QFrame()
        header.setFixedHeight(50)
        header.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_secondary']};
                border-bottom: 1px solid {COLORS['border_color']};
            }}
        """)
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(12)

        self.header_title = QLabel("Dashboard")
        self.header_title.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        self.header_title.setStyleSheet(f"color: {COLORS['text_primary']};")
        layout.addWidget(self.header_title)
        layout.addStretch()

        # Floating panel toggle pill
        self.btn_float_toggle = QPushButton("Floating Mode")
        self.btn_float_toggle.setFixedHeight(28)
        self.btn_float_toggle.setFont(QFont("Segoe UI", 9))
        self.btn_float_toggle.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid {COLORS['border_color']};
                color: {COLORS['text_muted']};
                border-radius: 14px;
                padding: 0 12px;
            }}
            QPushButton:hover {{
                border-color: {COLORS['accent_secondary']};
                color: {COLORS['accent_secondary']};
            }}
        """)
        self.btn_float_toggle.clicked.connect(self.toggle_floating_panel)
        layout.addWidget(self.btn_float_toggle)

        return header

    def navigate_to_index(self, index: int):
        self.stacked_widget.setCurrentIndex(index)
        btn = self.nav_btn_group.button(index)
        if btn and not btn.isChecked():
            btn.setChecked(True)

        titles = [
            "Workspace  ›  Dashboard", "Workspace  ›  Practice Assistant", "Workspace  ›  Question History",
            "Workspace  ›  Performance Analytics", "Workspace  ›  AI Model Manager", "Workspace  ›  Settings"
        ]
        if index < len(titles):
            self.header_title.setText(titles[index])

        if index == 0:
            self.dashboard_view.refresh_data()
        elif index == 2:
            self.history_view.refresh_table()
        elif index == 3:
            self.analytics_view.refresh_data()
        elif index == 4:
            self.model_view.refresh_status()

    def navigate_by_name(self, name: str):
        mapping = {
            "dashboard": 0,
            "practice": 1,
            "history": 2,
            "analytics": 3,
            "models": 4,
            "settings": 5
        }
        idx = mapping.get(name, 0)
        self.navigate_to_index(idx)

    def trigger_capture(self):
        """Activates fullscreen snippet overlay across displays."""
        logger.info("Triggering snippet overlay...")
        self.snippet_overlay.start_selection()

    def on_snippet_captured(self, pil_image):
        """Pass captured screenshot to Practice Assistant and process automatically."""
        self.navigate_to_index(1) # Switch to Practice Assistant
        is_floating = self.floating_panel.isVisible()
        if is_floating:
            self.floating_panel.set_processing(True)
        self.practice_view.process_captured_image(pil_image, auto_analyze=True)

    def toggle_floating_panel(self):
        if self.floating_panel.isVisible():
            self.floating_panel.hide()
        else:
            self.floating_panel.show()
            self.floating_panel.raise_()
            self.floating_panel.activateWindow()

    def closeEvent(self, event):
        self.hotkey_listener.stop()
        self.floating_panel.close()
        self.snippet_overlay.close()
        event.accept()

