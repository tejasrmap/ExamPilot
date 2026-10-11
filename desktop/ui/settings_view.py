"""
ExamPilot Settings View
GT InnoX LLP
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QScrollArea, QFrame, QMessageBox, QFileDialog
)
from PySide6.QtGui import QFont
from pathlib import Path
from desktop.config import COLORS, DEFAULT_CAPTURE_HOTKEY_STR, DEFAULT_OLLAMA_HOST, APP_VERSION, COMPANY_NAME, COPYRIGHT
from desktop.database.repository import repository
from desktop.database.database import db_manager
from desktop.security.privacy import PrivacyGuard

class SettingsView(QWidget):
    """User preferences, database backup/restore, shortcut, and privacy settings."""

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
        title = QLabel("Settings")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")

        desc = QLabel("Configure shortcuts, local inference endpoints, data privacy, and backups.")
        desc.setFont(QFont("Segoe UI", 10))
        desc.setStyleSheet(f"color: {COLORS['text_muted']};")

        layout.addWidget(title)
        layout.addWidget(desc)

        # General Preferences Card
        gen_card = QFrame()
        gen_card.setStyleSheet(f"background-color: {COLORS['bg_card']}; border: 1px solid {COLORS['border_color']}; border-radius: 10px; padding: 14px;")
        gen_vbox = QVBoxLayout(gen_card)
        gen_vbox.setSpacing(12)

        gen_title = QLabel("Application & Inference Preferences")
        gen_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        gen_title.setStyleSheet(f"color: {COLORS['text_primary']};")
        gen_vbox.addWidget(gen_title)

        # Hotkey setting
        row_hk = QHBoxLayout()
        hk_lbl = QLabel("Capture Keyboard Shortcut:")
        hk_lbl.setFont(QFont("Segoe UI", 10))
        hk_lbl.setStyleSheet(f"color: {COLORS['text_muted']};")
        self.txt_hotkey = QLineEdit(DEFAULT_CAPTURE_HOTKEY_STR)
        self.txt_hotkey.setReadOnly(True)
        self.txt_hotkey.setFixedWidth(160)
        self.txt_hotkey.setStyleSheet(f"background-color: {COLORS['bg_secondary']}; border: 1px solid {COLORS['border_color']}; border-radius: 6px; color: {COLORS['accent_secondary']}; padding: 6px; font-weight: bold; text-align: center;")
        row_hk.addWidget(hk_lbl)
        row_hk.addStretch()
        row_hk.addWidget(self.txt_hotkey)
        gen_vbox.addLayout(row_hk)

        # Ollama Host setting
        row_host = QHBoxLayout()
        host_lbl = QLabel("Ollama Local Endpoint:")
        host_lbl.setFont(QFont("Segoe UI", 10))
        host_lbl.setStyleSheet(f"color: {COLORS['text_muted']};")
        self.txt_host = QLineEdit(DEFAULT_OLLAMA_HOST)
        self.txt_host.setFixedWidth(220)
        self.txt_host.setStyleSheet(f"background-color: {COLORS['bg_secondary']}; border: 1px solid {COLORS['border_color']}; border-radius: 6px; color: {COLORS['text_primary']}; padding: 6px;")
        row_host.addWidget(host_lbl)
        row_host.addStretch()
        row_host.addWidget(self.txt_host)
        gen_vbox.addLayout(row_host)

        layout.addWidget(gen_card)

        # Database Backup & Restore Card
        db_card = QFrame()
        db_card.setStyleSheet(f"background-color: {COLORS['bg_card']}; border: 1px solid {COLORS['border_color']}; border-radius: 10px; padding: 14px;")
        db_vbox = QVBoxLayout(db_card)
        db_vbox.setSpacing(12)

        db_title = QLabel("Database Backup & Restore")
        db_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        db_title.setStyleSheet(f"color: {COLORS['text_primary']};")
        db_vbox.addWidget(db_title)

        db_desc = QLabel("Backup your local SQLite database or restore from a previously saved snapshot.")
        db_desc.setFont(QFont("Segoe UI", 9))
        db_desc.setStyleSheet(f"color: {COLORS['text_muted']};")
        db_vbox.addWidget(db_desc)

        btn_row = QHBoxLayout()
        self.btn_backup = QPushButton("Create Database Backup")
        self.btn_backup.setFixedHeight(34)
        self.btn_backup.setStyleSheet(f"""
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
        self.btn_backup.clicked.connect(self.backup_database)

        self.btn_restore = QPushButton("Restore Database Snapshot")
        self.btn_restore.setFixedHeight(34)
        self.btn_restore.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border_color']};
                color: {COLORS['text_primary']};
                border-radius: 6px;
                padding: 0 14px;
            }}
            QPushButton:hover {{
                border-color: {COLORS['warning']};
            }}
        """)
        self.btn_restore.clicked.connect(self.restore_database)

        btn_row.addWidget(self.btn_backup)
        btn_row.addWidget(self.btn_restore)
        btn_row.addStretch()
        db_vbox.addLayout(btn_row)

        layout.addWidget(db_card)

        # Privacy Factsheet Card
        priv_card = QFrame()
        priv_card.setStyleSheet(f"background-color: {COLORS['bg_card']}; border: 1px solid {COLORS['border_color']}; border-radius: 10px; padding: 14px;")
        priv_vbox = QVBoxLayout(priv_card)
        priv_vbox.setSpacing(8)

        priv_title = QLabel("Privacy & Security Declarations")
        priv_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        priv_title.setStyleSheet(f"color: {COLORS['text_primary']};")
        priv_vbox.addWidget(priv_title)

        facts = PrivacyGuard.get_privacy_declarations()
        for k, v in facts.items():
            k_fmt = k.replace("_", " ").title()
            row = QLabel(f"• {k_fmt}: {v}")
            row.setFont(QFont("Segoe UI", 9))
            row.setStyleSheet(f"color: {COLORS['text_muted']};")
            priv_vbox.addWidget(row)

        layout.addWidget(priv_card)

        # About ExamPilot Card
        about_card = QFrame()
        about_card.setStyleSheet(f"background-color: {COLORS['bg_card']}; border: 1px solid {COLORS['border_color']}; border-radius: 10px; padding: 14px;")
        ab_vbox = QVBoxLayout(about_card)
        ab_vbox.setSpacing(6)

        ab_title = QLabel(f"About ExamPilot v{APP_VERSION}")
        ab_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        ab_title.setStyleSheet(f"color: {COLORS['text_primary']};")
        ab_vbox.addWidget(ab_title)

        ab_vendor = QLabel(f"Developed by {COMPANY_NAME}\n{COPYRIGHT}\nTagline: Understand Questions. Learn the Answers.")
        ab_vendor.setFont(QFont("Segoe UI", 9))
        ab_vendor.setStyleSheet(f"color: {COLORS['text_muted']}; line-height: 1.4;")
        ab_vbox.addWidget(ab_vendor)

        layout.addWidget(about_card)
        layout.addStretch()

        scroll.setWidget(container)
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(scroll)

    def backup_database(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Backup Database", "exampilot_backup.db", "SQLite Database (*.db)"
        )
        if file_path:
            if db_manager.backup(Path(file_path)):
                QMessageBox.information(self, "Backup Success", f"Database backed up to {file_path}")
            else:
                QMessageBox.critical(self, "Error", "Failed to create database backup.")

    def restore_database(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Restore Database", "", "SQLite Database (*.db *.bak)"
        )
        if file_path:
            confirm = QMessageBox.question(
                self, "Confirm Restore",
                "Restoring will overwrite current database contents with the backup.\nDo you want to proceed?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if confirm == QMessageBox.StandardButton.Yes:
                if db_manager.restore(Path(file_path)):
                    QMessageBox.information(self, "Restore Success", "Database restored successfully.")
                else:
                    QMessageBox.critical(self, "Error", "Failed to restore database.")

