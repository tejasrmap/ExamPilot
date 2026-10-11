"""
ExamPilot Application Lifecycle & Configuration
GT InnoX LLP
"""

import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtGui import QFont
from desktop.ui.main_window import MainWindow
from desktop.config import APP_NAME, COLORS
from desktop.utils.logger import logger

def exception_hook(exctype, value, tb):
    """Global unhandled exception logger and user notification."""
    logger.critical("Unhandled exception occurred:", exc_info=(exctype, value, tb))
    sys.__excepthook__(exctype, value, tb)

def create_application() -> QApplication:
    # High DPI Scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName("GT InnoX LLP")

    # Set default modern typography
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    # Set Global Dark Theme Stylesheet
    app.setStyleSheet(f"""
        QWidget {{
            color: {COLORS['text_primary']};
            background-color: {COLORS['bg_dark']};
        }}
        QScrollBar:vertical {{
            background: {COLORS['bg_secondary']};
            width: 10px;
            margin: 0;
            border-radius: 5px;
        }}
        QScrollBar::handle:vertical {{
            background: {COLORS['border_color']};
            min-height: 20px;
            border-radius: 5px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {COLORS['accent_primary']};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        QToolTip {{
            color: {COLORS['text_primary']};
            background-color: {COLORS['bg_card']};
            border: 1px solid {COLORS['border_color']};
            border-radius: 4px;
            padding: 4px;
        }}
    """)

    sys.excepthook = exception_hook
    return app

