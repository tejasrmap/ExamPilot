"""
ExamPilot Question History View
GT InnoX LLP
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QFileDialog, QDialog, QTextEdit
)
from PySide6.QtGui import QFont
import json
import csv
from desktop.config import COLORS
from desktop.database.repository import repository
from desktop.database.database import db_manager
from desktop.utils.helpers import format_timestamp, truncate_text

class QuestionDetailDialog(QDialog):
    """View full details of a saved question."""
    def __init__(self, q, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Question #{q.id} Details")
        self.resize(550, 480)
        self.setStyleSheet(f"background-color: {COLORS['bg_dark']}; color: {COLORS['text_primary']};")

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        subj_lbl = QLabel(f"Subject: {q.subject_name} • {format_timestamp(q.created_at)}")
        subj_lbl.setStyleSheet(f"color: {COLORS['accent_secondary']}; font-weight: bold;")
        layout.addWidget(subj_lbl)

        q_txt = QLabel(q.question_text)
        q_txt.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        q_txt.setWordWrap(True)
        layout.addWidget(q_txt)

        opts_vbox = QVBoxLayout()
        for opt, val in sorted(q.options.items()):
            is_ans = (opt == q.suggested_answer)
            col = COLORS["success"] if is_ans else COLORS["text_muted"]
            lbl = QLabel(f"Option {opt}: {val}" + (" [CORRECT]" if is_ans else ""))
            lbl.setStyleSheet(f"color: {col}; font-weight: {'bold' if is_ans else 'normal'};")
            opts_vbox.addWidget(lbl)
        layout.addLayout(opts_vbox)

        exp_title = QLabel("Explanation:")
        exp_title.setStyleSheet(f"color: {COLORS['text_muted']}; font-weight: bold;")
        layout.addWidget(exp_title)

        exp_txt = QTextEdit()
        exp_txt.setReadOnly(True)
        exp_txt.setPlainText(q.explanation or "No explanation recorded.")
        exp_txt.setStyleSheet(f"background-color: {COLORS['bg_secondary']}; border: 1px solid {COLORS['border_color']}; border-radius: 6px; padding: 8px;")
        layout.addWidget(exp_txt)

        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

class HistoryView(QWidget):
    """Searchable, filterable question history log with export and deletion controls."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        # Header
        head_layout = QHBoxLayout()
        vbox = QVBoxLayout()
        title = QLabel("Question History")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")

        desc = QLabel("Review past practice questions, option breakdowns, and accuracy.")
        desc.setFont(QFont("Segoe UI", 10))
        desc.setStyleSheet(f"color: {COLORS['text_muted']};")

        vbox.addWidget(title)
        vbox.addWidget(desc)
        head_layout.addLayout(vbox)
        head_layout.addStretch()

        # Export & Wipe Actions
        self.btn_export = QPushButton("Export (CSV/JSON)")
        self.btn_export.setFixedHeight(34)
        self.btn_export.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border_color']};
                color: {COLORS['text_primary']};
                border-radius: 6px;
                padding: 0 12px;
            }}
            QPushButton:hover {{
                border-color: {COLORS['accent_secondary']};
            }}
        """)
        self.btn_export.clicked.connect(self.export_history)

        self.btn_wipe = QPushButton("Clear All History")
        self.btn_wipe.setFixedHeight(34)
        self.btn_wipe.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid {COLORS['danger']};
                color: {COLORS['danger']};
                border-radius: 6px;
                padding: 0 12px;
            }}
            QPushButton:hover {{
                background-color: rgba(239, 68, 68, 0.1);
            }}
        """)
        self.btn_wipe.clicked.connect(self.wipe_history)

        head_layout.addWidget(self.btn_export)
        head_layout.addWidget(self.btn_wipe)
        layout.addLayout(head_layout)

        # Search & Filters Bar
        filter_bar = QHBoxLayout()
        filter_bar.setSpacing(10)

        self.txt_search = QLineEdit()
        self.txt_search.setFixedHeight(34)
        self.txt_search.setPlaceholderText("Search questions or explanations...")
        self.txt_search.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border_color']};
                border-radius: 6px;
                color: {COLORS['text_primary']};
                padding: 0 10px;
            }}
            QLineEdit:focus {{
                border-color: {COLORS['accent_primary']};
            }}
        """)
        self.txt_search.textChanged.connect(self.refresh_table)

        self.combo_subject = QComboBox()
        self.combo_subject.setFixedHeight(34)
        self.combo_subject.setMinimumWidth(160)
        self.combo_subject.addItem("All Subjects", None)
        self.combo_subject.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border_color']};
                border-radius: 6px;
                color: {COLORS['text_primary']};
                padding-left: 10px;
            }}
        """)
        self.combo_subject.currentIndexChanged.connect(self.refresh_table)

        filter_bar.addWidget(self.txt_search, 70)
        filter_bar.addWidget(self.combo_subject, 30)
        layout.addLayout(filter_bar)

        # History Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Date", "Subject", "Question", "Answer", "Confidence"])
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(f"""
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
                padding: 8px;
                border: none;
                font-weight: 600;
            }}
        """)
        self.table.doubleClicked.connect(self.view_question_details)
        layout.addWidget(self.table)

        self._load_subject_filters()

    def _load_subject_filters(self):
        subjects = repository.get_subjects()
        for s in subjects:
            self.combo_subject.addItem(s["name"], s["id"])

    def refresh_table(self):
        search = self.txt_search.text().strip() or None
        subject_id = self.combo_subject.currentData()

        questions = repository.list_questions(subject_id=subject_id, search=search)
        self.current_questions = {q.id: q for q in questions}

        self.table.setRowCount(len(questions))
        for r_idx, q in enumerate(questions):
            item_id = QTableWidgetItem(str(q.id))
            item_date = QTableWidgetItem(format_timestamp(q.created_at))
            item_subj = QTableWidgetItem(q.subject_name or "General")
            item_q = QTableWidgetItem(truncate_text(q.question_text, 80))
            item_ans = QTableWidgetItem(f"Option {q.suggested_answer}" if q.suggested_answer else "-")
            item_conf = QTableWidgetItem(f"{int(round((q.confidence or 0) * 100))}%")

            for item in [item_id, item_date, item_subj, item_q, item_ans, item_conf]:
                item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)

            self.table.setItem(r_idx, 0, item_id)
            self.table.setItem(r_idx, 1, item_date)
            self.table.setItem(r_idx, 2, item_subj)
            self.table.setItem(r_idx, 3, item_q)
            self.table.setItem(r_idx, 4, item_ans)
            self.table.setItem(r_idx, 5, item_conf)

    def view_question_details(self):
        selected_rows = self.table.selectedItems()
        if not selected_rows:
            return
        qid = int(self.table.item(selected_rows[0].row(), 0).text())
        q = self.current_questions.get(qid)
        if q:
            dlg = QuestionDetailDialog(q, self)
            dlg.exec()

    def export_history(self):
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self, "Export Question History", "exampilot_history.csv",
            "CSV Files (*.csv);;JSON Files (*.json)"
        )
        if not file_path:
            return

        questions = repository.list_questions(limit=10000)
        try:
            if file_path.endswith(".json") or "json" in selected_filter.lower():
                data = [q.model_dump() for q in questions]
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                with open(file_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["ID", "Subject", "Question", "Suggested Answer", "Confidence", "Explanation", "Date"])
                    for q in questions:
                        writer.writerow([q.id, q.subject_name, q.question_text, q.suggested_answer, q.confidence, q.explanation, q.created_at])
            
            QMessageBox.information(self, "Export Complete", f"Successfully exported {len(questions)} questions.")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", str(e))

    def wipe_history(self):
        confirm = QMessageBox.question(
            self, "Confirm History Wipe",
            "Are you sure you want to permanently delete all question history and feedback?\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            if db_manager.clear_all_history():
                self.refresh_table()
                QMessageBox.information(self, "Cleared", "Question history wiped successfully.")
            else:
                QMessageBox.critical(self, "Error", "Failed to clear database history.")

