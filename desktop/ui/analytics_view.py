"""
ExamPilot Performance Analytics View
GT InnoX LLP
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar,
    QScrollArea, QFrame, QGridLayout
)
from PySide6.QtGui import QFont
from desktop.config import COLORS
from desktop.ui.components.widgets import CardFrame
from desktop.database.repository import repository

class AnalyticsView(QWidget):
    """Performance metrics, accuracy breakdown by subject, and learning insights."""

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
        title = QLabel("Performance Analytics")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")

        desc = QLabel("Comprehensive metrics on questions practiced, accuracy trends, and subject mastery.")
        desc.setFont(QFont("Segoe UI", 10))
        desc.setStyleSheet(f"color: {COLORS['text_muted']};")

        layout.addWidget(title)
        layout.addWidget(desc)

        # Summary KPIs Grid
        kpi_grid = QGridLayout()
        kpi_grid.setSpacing(14)

        self.card_acc = self._create_kpi_card("Overall Accuracy", "100%", COLORS["success"])
        self.card_total = self._create_kpi_card("Total Questions Practiced", "0", COLORS["accent_primary"])
        self.card_conf = self._create_kpi_card("Average AI Certainty", "0%", COLORS["accent_secondary"])
        self.card_subjects = self._create_kpi_card("Active Subjects", "0", COLORS["warning"])

        kpi_grid.addWidget(self.card_acc, 0, 0)
        kpi_grid.addWidget(self.card_total, 0, 1)
        kpi_grid.addWidget(self.card_conf, 0, 2)
        kpi_grid.addWidget(self.card_subjects, 0, 3)
        layout.addLayout(kpi_grid)

        # Subject Distribution Card
        subj_card = CardFrame()
        subj_vbox = QVBoxLayout(subj_card)
        subj_vbox.setSpacing(12)

        s_title = QLabel("Subject Practice Breakdown")
        s_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        s_title.setStyleSheet(f"color: {COLORS['text_primary']};")
        subj_vbox.addWidget(s_title)

        self.subject_bars_container = QVBoxLayout()
        self.subject_bars_container.setSpacing(10)
        subj_vbox.addLayout(self.subject_bars_container)

        layout.addWidget(subj_card)

        # Pedagogical Insights Card
        insight_card = CardFrame()
        ins_vbox = QVBoxLayout(insight_card)
        ins_title = QLabel("ExamPilot AI Learning Insights")
        ins_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        ins_title.setStyleSheet(f"color: {COLORS['text_primary']};")
        ins_vbox.addWidget(ins_title)

        tips = [
            "• High Confidence Correlation: Questions analyzed with ≥ 90% confidence have verified distinct options.",
            "• Option-by-Option Review: Deep retention improves by reading why incorrect options are flawed rather than memorizing only the correct key.",
            "• Practice Variety: Broadening across diverse subjects balances conceptual preparation."
        ]
        for tip in tips:
            t_lbl = QLabel(tip)
            t_lbl.setFont(QFont("Segoe UI", 9))
            t_lbl.setStyleSheet(f"color: {COLORS['text_muted']}; line-height: 1.4;")
            ins_vbox.addWidget(t_lbl)

        layout.addWidget(insight_card)
        layout.addStretch()

        scroll.setWidget(container)
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(scroll)

    def _create_kpi_card(self, title: str, value: str, color: str) -> CardFrame:
        card = CardFrame()
        vbox = QVBoxLayout(card)
        vbox.setContentsMargins(14, 12, 14, 12)
        vbox.setSpacing(4)

        t_lbl = QLabel(title)
        t_lbl.setFont(QFont("Segoe UI", 8, QFont.Weight.Medium))
        t_lbl.setStyleSheet(f"color: {COLORS['text_muted']}; text-transform: uppercase;")

        v_lbl = QLabel(value)
        v_lbl.setObjectName("val")
        v_lbl.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        v_lbl.setStyleSheet(f"color: {color};")

        vbox.addWidget(t_lbl)
        vbox.addWidget(v_lbl)
        return card

    def refresh_data(self):
        analytics = repository.get_dashboard_analytics()
        self.card_acc.findChild(QLabel, "val").setText(f"{analytics['accuracy']}%")
        self.card_total.findChild(QLabel, "val").setText(str(analytics["total_questions"]))
        self.card_conf.findChild(QLabel, "val").setText(f"{analytics['avg_confidence']}%")
        self.card_subjects.findChild(QLabel, "val").setText(str(len(analytics["subject_counts"])))

        # Refresh subject bars
        while self.subject_bars_container.count():
            item = self.subject_bars_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        total_q = max(1, analytics["total_questions"])
        for item in analytics["subject_counts"]:
            name = item["subject"]
            cnt = item["count"]
            pct = int(round((cnt / total_q) * 100))

            row = QVBoxLayout()
            row.setSpacing(2)

            head = QHBoxLayout()
            n_lbl = QLabel(name)
            n_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
            n_lbl.setStyleSheet(f"color: {COLORS['text_primary']};")

            c_lbl = QLabel(f"{cnt} questions ({pct}%)")
            c_lbl.setFont(QFont("Segoe UI", 9))
            c_lbl.setStyleSheet(f"color: {COLORS['text_muted']};")

            head.addWidget(n_lbl)
            head.addStretch()
            head.addWidget(c_lbl)
            row.addLayout(head)

            bar = QProgressBar()
            bar.setFixedHeight(6)
            bar.setTextVisible(False)
            bar.setValue(pct)
            bar.setStyleSheet(f"""
                QProgressBar {{
                    background-color: {COLORS['bg_secondary']};
                    border-radius: 3px;
                    border: none;
                }}
                QProgressBar::chunk {{
                    background-color: {COLORS['accent_primary']};
                    border-radius: 3px;
                }}
            """)
            row.addWidget(bar)

            self.subject_bars_container.addLayout(row)

