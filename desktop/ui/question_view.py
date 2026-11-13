"""
ExamPilot Practice Assistant View
GT InnoX LLP — Understand Questions. Learn the Answers.
"""

from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QLineEdit,
    QPushButton, QComboBox, QFileDialog, QScrollArea, QFrame, QMessageBox,
    QProgressBar, QDialog, QDialogButtonBox
)
from PySide6.QtGui import QFont, QPixmap
from PIL import Image
import io

from desktop.config import COLORS
from desktop.ui.components.widgets import CardFrame, ConfidenceMeter
from desktop.core.ocr_engine import ocr_engine
from desktop.core.question_parser import question_parser
from desktop.core.answer_engine import answer_engine
from desktop.ai.domain_detector import detect_domain
from desktop.database.repository import repository
from desktop.database.models import QuestionModel, FeedbackModel
from desktop.utils.logger import logger

class AIWorker(QThread):
    """Background worker for non-blocking local AI inference."""
    finished = Signal(bool, object, str)

    def __init__(self, question: str, options: dict, subject: str, structured_options: Optional[list] = None):
        super().__init__()
        self.question = question
        self.options = options
        self.subject = subject
        self.structured_options = structured_options

    def run(self):
        success, result, error = answer_engine.analyze(
            self.question, self.options, subject=self.subject, structured_options=self.structured_options
        )
        self.finished.emit(success, result, error)

class FeedbackDialog(QDialog):
    """User feedback dialog for reporting or correcting answers."""
    def __init__(self, question_id: int, current_answer: str, parent=None):
        super().__init__(parent)
        self.question_id = question_id
        self.setWindowTitle("Report / Flag Incorrect Answer")
        self.setFixedSize(400, 260)
        self.setStyleSheet(f"background-color: {COLORS['bg_dark']}; color: {COLORS['text_primary']};")

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        lbl = QLabel("Provide your correction or feedback:")
        lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        layout.addWidget(lbl)

        row = QHBoxLayout()
        row.addWidget(QLabel("Correct Option:"))
        self.combo_answer = QComboBox()
        self.combo_answer.addItems(["A", "B", "C", "D", "E", "Other"])
        if current_answer in ["A", "B", "C", "D", "E"]:
            self.combo_answer.setCurrentText(current_answer)
        row.addWidget(self.combo_answer)
        row.addStretch()
        layout.addLayout(row)

        self.txt_feedback = QTextEdit()
        self.txt_feedback.setPlaceholderText("Explain why the answer was incorrect or ambiguous...")
        self.txt_feedback.setStyleSheet(f"background-color: {COLORS['bg_secondary']}; border: 1px solid {COLORS['border_color']}; border-radius: 6px; padding: 6px;")
        layout.addWidget(self.txt_feedback)

        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btn_box.accepted.connect(self.submit_feedback)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def submit_feedback(self):
        feedback_text = self.txt_feedback.toPlainText().strip()
        corrected_ans = self.combo_answer.currentText()
        if not feedback_text:
            feedback_text = "User flagged as incorrect."
        
        fb = FeedbackModel(
            question_id=self.question_id,
            user_feedback=feedback_text,
            corrected_answer=corrected_ans
        )
        repository.record_feedback(fb)
        self.accept()

class PracticeAssistantView(QWidget):
    """Core interactive view for screen capture, OCR preview, and AI explanation."""
    start_capture_requested = Signal()
    analysis_completed = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_question_id = None
        self.current_result_data = None
        self.option_inputs = {}
        self.init_ui()

    def init_ui(self):
        # Outer scroll area
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(f"background-color: {COLORS['bg_dark']};")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(28, 20, 28, 24)
        layout.setSpacing(16)

        # Header Title & Subject
        head_layout = QHBoxLayout()
        title_vbox = QVBoxLayout()
        title = QLabel("Practice Assistant")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")

        desc = QLabel("Capture, extract, verify, and understand multiple choice questions with local AI.")
        desc.setFont(QFont("Segoe UI", 10))
        desc.setStyleSheet(f"color: {COLORS['text_muted']};")

        title_vbox.addWidget(title)
        title_vbox.addWidget(desc)
        head_layout.addLayout(title_vbox)
        head_layout.addStretch()

        # Subject Dropdown
        subj_vbox = QVBoxLayout()
        subj_lbl = QLabel("Subject:")
        subj_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
        subj_lbl.setStyleSheet(f"color: {COLORS['text_muted']};")
        self.subject_combo = QComboBox()
        self.subject_combo.setMinimumWidth(180)
        self.subject_combo.setFixedHeight(34)
        self.subject_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border_color']};
                color: {COLORS['text_primary']};
                border-radius: 6px;
                padding-left: 10px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {COLORS['bg_card']};
                color: {COLORS['text_primary']};
                selection-background-color: {COLORS['accent_primary']};
            }}
        """)
        self._load_subjects()
        subj_vbox.addWidget(subj_lbl)
        subj_vbox.addWidget(self.subject_combo)
        head_layout.addLayout(subj_vbox)

        layout.addLayout(head_layout)

        # Top Action Bar: Capture Screen, Upload Image, Paste Text
        action_bar = QHBoxLayout()
        action_bar.setSpacing(10)

        self.btn_capture = QPushButton("  Capture Screen (Ctrl+Shift+Q)")
        self.btn_capture.setFixedHeight(38)
        self.btn_capture.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_capture.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent_primary']};
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 600;
                padding: 0 16px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['accent_primary_hover']};
            }}
        """)
        self.btn_capture.clicked.connect(self.start_capture_requested.emit)

        self.btn_upload = QPushButton("Upload Image File")
        self.btn_upload.setFixedHeight(38)
        self.btn_upload.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border_color']};
                color: {COLORS['text_primary']};
                border-radius: 6px;
                padding: 0 14px;
            }}
            QPushButton:hover {{
                border-color: {COLORS['accent_secondary']};
                color: {COLORS['accent_secondary']};
            }}
        """)
        self.btn_upload.clicked.connect(self.upload_image_file)

        self.btn_clear = QPushButton("Clear Fields")
        self.btn_clear.setFixedHeight(38)
        self.btn_clear.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid {COLORS['border_color']};
                color: {COLORS['text_muted']};
                border-radius: 6px;
                padding: 0 12px;
            }}
            QPushButton:hover {{
                color: {COLORS['danger']};
                border-color: {COLORS['danger']};
            }}
        """)
        self.btn_clear.clicked.connect(self.clear_fields)

        action_bar.addWidget(self.btn_capture)
        action_bar.addWidget(self.btn_upload)
        action_bar.addWidget(self.btn_clear)
        action_bar.addStretch()
        layout.addLayout(action_bar)

        # Extracted Question & Options Card
        input_card = CardFrame()
        input_vbox = QVBoxLayout(input_card)
        input_vbox.setSpacing(12)

        q_head = QLabel("Question Statement (Extracted or Entered):")
        q_head.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        q_head.setStyleSheet(f"color: {COLORS['text_primary']};")
        input_vbox.addWidget(q_head)

        self.txt_question = QTextEdit()
        self.txt_question.setPlaceholderText("Question text extracted from OCR or typed manually...")
        self.txt_question.setFixedHeight(75)
        self.txt_question.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border_color']};
                border-radius: 6px;
                color: {COLORS['text_primary']};
                padding: 8px;
                font-size: 13px;
            }}
            QTextEdit:focus {{
                border-color: {COLORS['accent_primary']};
            }}
        """)
        input_vbox.addWidget(self.txt_question)

        # Options Container
        opt_head_layout = QHBoxLayout()
        opt_title = QLabel("Answer Options:")
        opt_title.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        opt_title.setStyleSheet(f"color: {COLORS['text_primary']};")
        opt_head_layout.addWidget(opt_title)
        opt_head_layout.addStretch()

        btn_add_opt = QPushButton("+ Add Option")
        btn_add_opt.setFont(QFont("Segoe UI", 9))
        btn_add_opt.setStyleSheet(f"color: {COLORS['accent_secondary']}; background: transparent; border: none; cursor: pointer;")
        btn_add_opt.clicked.connect(self.add_option_row)
        opt_head_layout.addWidget(btn_add_opt)
        input_vbox.addLayout(opt_head_layout)

        self.options_container = QVBoxLayout()
        self.options_container.setSpacing(8)
        input_vbox.addLayout(self.options_container)

        # Default options A, B, C, D
        for opt_label in ["A", "B", "C", "D"]:
            self._add_option_input(opt_label)

        # Analyze Button
        self.btn_analyze = QPushButton("  Analyse Question with Local AI")
        self.btn_analyze.setFixedHeight(44)
        self.btn_analyze.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_analyze.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.btn_analyze.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['accent_primary']}, stop:1 {COLORS['accent_secondary']});
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background: {COLORS['accent_primary_hover']};
            }}
            QPushButton:disabled {{
                background-color: {COLORS['bg_card_hover']};
                color: {COLORS['text_muted']};
            }}
        """)
        self.btn_analyze.clicked.connect(self.run_ai_analysis)
        input_vbox.addWidget(self.btn_analyze)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0) # Indeterminate spinner
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {COLORS['bg_secondary']};
                border: none;
                border-radius: 2px;
            }}
            QProgressBar::chunk {{
                background-color: {COLORS['accent_secondary']};
            }}
        """)
        self.progress_bar.hide()
        input_vbox.addWidget(self.progress_bar)

        layout.addWidget(input_card)

        # Results & Explanation Container (Initially Hidden)
        self.result_card = CardFrame()
        self.result_vbox = QVBoxLayout(self.result_card)
        self.result_vbox.setSpacing(14)

        res_head = QHBoxLayout()
        self.lbl_answer_banner = QLabel("Suggested Answer: B (Queue)")
        self.lbl_answer_banner.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.lbl_answer_banner.setStyleSheet(f"color: {COLORS['success']};")
        res_head.addWidget(self.lbl_answer_banner)
        res_head.addStretch()

        self.conf_meter = ConfidenceMeter()
        self.conf_meter.setFixedWidth(200)
        res_head.addWidget(self.conf_meter)
        self.result_vbox.addLayout(res_head)

        # Detailed Explanation Box
        exp_title = QLabel("Pedagogical Explanation:")
        exp_title.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        exp_title.setStyleSheet(f"color: {COLORS['text_muted']};")
        self.result_vbox.addWidget(exp_title)

        self.lbl_explanation = QLabel()
        self.lbl_explanation.setWordWrap(True)
        self.lbl_explanation.setFont(QFont("Segoe UI", 10))
        self.lbl_explanation.setStyleSheet(f"""
            background-color: {COLORS['bg_secondary']};
            border-left: 3px solid {COLORS['accent_secondary']};
            border-radius: 6px;
            padding: 12px;
            color: {COLORS['text_primary']};
            line-height: 1.5;
        """)
        self.result_vbox.addWidget(self.lbl_explanation)

        # Option by Option Analysis
        opt_analysis_title = QLabel("Option-by-Option Analysis:")
        opt_analysis_title.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        opt_analysis_title.setStyleSheet(f"color: {COLORS['text_muted']};")
        self.result_vbox.addWidget(opt_analysis_title)

        self.opt_analysis_container = QVBoxLayout()
        self.opt_analysis_container.setSpacing(6)
        self.result_vbox.addLayout(self.opt_analysis_container)

        # Bottom Results Action Bar (Save / Flag Incorrect)
        res_actions = QHBoxLayout()
        self.btn_save = QPushButton("Save to History")
        self.btn_save.setFixedHeight(34)
        self.btn_save.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border_color']};
                color: {COLORS['text_primary']};
                border-radius: 6px;
                padding: 0 14px;
            }}
            QPushButton:hover {{
                border-color: {COLORS['success']};
                color: {COLORS['success']};
            }}
        """)
        self.btn_save.clicked.connect(self.save_to_history)

        self.btn_flag = QPushButton("Report / Flag Incorrect Answer")
        self.btn_flag.setFixedHeight(34)
        self.btn_flag.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid {COLORS['border_color']};
                color: {COLORS['warning']};
                border-radius: 6px;
                padding: 0 14px;
            }}
            QPushButton:hover {{
                border-color: {COLORS['warning']};
                background-color: rgba(245, 158, 11, 0.1);
            }}
        """)
        self.btn_flag.clicked.connect(self.open_feedback_dialog)

        res_actions.addWidget(self.btn_save)
        res_actions.addWidget(self.btn_flag)
        res_actions.addStretch()
        self.result_vbox.addLayout(res_actions)

        self.result_card.hide()
        layout.addWidget(self.result_card)

        scroll.setWidget(container)
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(scroll)

    def _load_subjects(self):
        self.subject_combo.clear()
        self.subject_combo.addItem("⚡ Auto-Detect Domain", 0)
        subjects = repository.get_subjects()
        for s in subjects:
            self.subject_combo.addItem(s["name"], s["id"])
        self.subject_combo.setCurrentIndex(0)

    def _add_option_input(self, label: str, text: str = ""):
        row = QHBoxLayout()
        lbl = QLabel(f"{label}:")
        lbl.setFixedWidth(24)
        lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color: {COLORS['accent_secondary']};")

        line_edit = QLineEdit(text)
        line_edit.setFixedHeight(32)
        line_edit.setPlaceholderText(f"Option {label} content...")
        line_edit.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border_color']};
                border-radius: 6px;
                color: {COLORS['text_primary']};
                padding: 0 8px;
            }}
            QLineEdit:focus {{
                border-color: {COLORS['accent_secondary']};
            }}
        """)
        self.option_inputs[label] = line_edit

        row.addWidget(lbl)
        row.addWidget(line_edit)
        self.options_container.addLayout(row)

    def add_option_row(self):
        next_char = chr(ord('A') + len(self.option_inputs))
        if len(self.option_inputs) < 8:
            self._add_option_input(next_char)

    def clear_fields(self):
        self.txt_question.clear()
        for edit in self.option_inputs.values():
            edit.clear()
        self.result_card.hide()
        self.current_question_id = None
        self.current_result_data = None

    def process_captured_image(self, pil_image: Image.Image, auto_analyze: bool = True):
        """Called when a screenshot region is captured."""
        logger.info("Processing captured image via OCR...")
        ocr_result = ocr_engine.extract_text(pil_image)
        if not ocr_result["success"] or not ocr_result["lines"]:
            self.analysis_completed.emit({
                "suggested_answer": "—",
                "answer_text": "No text detected",
                "explanation": ocr_result.get("error") or "No text could be extracted from image.",
                "confidence": 0.0,
                "option_analysis": {}
            })
            QMessageBox.warning(self, "OCR Notice", ocr_result.get("error") or "No text could be extracted from image.")
            return

        parsed = question_parser.parse_from_lines(ocr_result["lines"])
        self.populate_parsed_data(parsed)

        # Domain auto-detection: identify domain immediately from extracted text
        q_text = parsed.get("question", "")
        opts = parsed.get("options", {})
        if q_text:
            detected_subj = detect_domain(q_text, opts)
            if detected_subj:
                idx = self.subject_combo.findText(detected_subj)
                if idx >= 0:
                    self.subject_combo.setCurrentIndex(idx)

        if auto_analyze and q_text and len(opts) >= 2:
            self.run_ai_analysis()
        elif auto_analyze:
            self.analysis_completed.emit({
                "suggested_answer": "Review Needed",
                "answer_text": "Incomplete Question",
                "explanation": "Please review extracted question and options in Practice Assistant before analyzing.",
                "confidence": 0.0,
                "option_analysis": {}
            })

    def upload_image_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select MCQ Screenshot", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.webp)"
        )
        if file_path:
            try:
                img = Image.open(file_path)
                self.process_captured_image(img, auto_analyze=True)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load image: {e}")

    def populate_parsed_data(self, parsed: dict):
        self.last_parsed = parsed
        self.txt_question.setPlainText(parsed.get("question", ""))
        opts = parsed.get("options", {})
        
        # Populate matching inputs
        for label, edit in self.option_inputs.items():
            edit.setText(opts.get(label, ""))

        # If options exceed current inputs, add them
        for label, val in opts.items():
            if label not in self.option_inputs:
                self._add_option_input(label, val)

        if parsed.get("needs_correction"):
            logger.info(f"Parsed with minor ambiguities: {parsed.get('validation_issues', [])}")

    def run_ai_analysis(self):
        question_text = self.txt_question.toPlainText().strip()
        if not question_text:
            QMessageBox.warning(self, "Incomplete Data", "Please provide the question text.")
            return

        options = {}
        for label, edit in self.option_inputs.items():
            val = edit.text().strip()
            if val:
                options[label] = val

        if len(options) < 2:
            QMessageBox.warning(self, "Incomplete Data", "Please provide at least 2 distinct options.")
            return

        subj = self.subject_combo.currentText()
        self.btn_analyze.setEnabled(False)
        self.progress_bar.show()

        structured_opts = getattr(self, "last_parsed", {}).get("structured_options")
        self.worker = AIWorker(question_text, options, subj, structured_options=structured_opts)
        self.worker.finished.connect(self._on_ai_finished)
        self.worker.start()

    analyze_question = run_ai_analysis

    def _on_ai_finished(self, success: bool, result: object, error: str):
        self.btn_analyze.setEnabled(True)
        self.progress_bar.hide()

        if not success or not result:
            self.analysis_completed.emit({
                "suggested_answer": "—",
                "answer_text": "Inference failed",
                "explanation": f"Failed to obtain answer: {error}",
                "confidence": 0.0,
                "option_analysis": {}
            })
            QMessageBox.critical(self, "Inference Error", f"Failed to obtain answer: {error}")
            return

        self.current_result_data = result
        self._display_results(result)

    def _display_results(self, data: dict):
        suggested = data.get("suggested_answer", "")
        answer_text = data.get("answer_text", "")
        confidence = data.get("confidence", 0.85)
        explanation = data.get("explanation", "")
        opt_analysis = data.get("option_analysis", {})
        detected_subject = data.get("detected_subject", "")

        if detected_subject:
            # Sync subject dropdown
            idx = self.subject_combo.findText(detected_subject)
            if idx >= 0:
                self.subject_combo.setCurrentIndex(idx)
            banner_prefix = f"[{detected_subject}] "
        else:
            banner_prefix = ""

        self.lbl_answer_banner.setText(f"{banner_prefix}Suggested Answer: Option {suggested} — {answer_text}")
        self.conf_meter.set_confidence(confidence)
        self.lbl_explanation.setText(explanation)
        self.analysis_completed.emit(data)

        # Clear previous option analysis widgets
        while self.opt_analysis_container.count():
            item = self.opt_analysis_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for opt, exp in sorted(opt_analysis.items()):
            is_correct = (opt == suggested)
            opt_frame = QFrame()
            opt_col = COLORS["success"] if is_correct else COLORS["border_color"]
            bg_col = "rgba(34, 197, 94, 0.1)" if is_correct else COLORS["bg_secondary"]

            opt_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {bg_col};
                    border: 1px solid {opt_col};
                    border-radius: 6px;
                    padding: 8px;
                }}
            """)
            opt_vbox = QVBoxLayout(opt_frame)
            opt_vbox.setContentsMargins(10, 6, 10, 6)
            opt_vbox.setSpacing(2)

            title_lbl = QLabel(f"Option {opt}:" + (" [BEST ANSWER]" if is_correct else ""))
            title_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            title_lbl.setStyleSheet(f"color: {COLORS['success'] if is_correct else COLORS['text_muted']};")

            exp_lbl = QLabel(exp)
            exp_lbl.setWordWrap(True)
            exp_lbl.setFont(QFont("Segoe UI", 9))
            exp_lbl.setStyleSheet(f"color: {COLORS['text_primary']};")

            opt_vbox.addWidget(title_lbl)
            opt_vbox.addWidget(exp_lbl)
            self.opt_analysis_container.addWidget(opt_frame)

        self.result_card.show()

        # Automatically save question to repository
        self.save_to_history(show_toast=False)

    def save_to_history(self, show_toast: bool = True):
        if not self.current_result_data:
            return

        try:
            q_text = self.txt_question.toPlainText().strip()
            options = {k: v.text().strip() for k, v in self.option_inputs.items() if v.text().strip()}
            subj_id = self.subject_combo.currentData()
            subj_name = self.subject_combo.currentText()

            q_model = QuestionModel(
                id=self.current_question_id,
                question_text=q_text,
                options=options,
                suggested_answer=self.current_result_data.get("suggested_answer"),
                answer_text=self.current_result_data.get("answer_text"),
                explanation=self.current_result_data.get("explanation"),
                option_analysis=self.current_result_data.get("option_analysis", {}),
                confidence=self.current_result_data.get("confidence", 0.0),
                subject_id=subj_id,
                subject_name=subj_name
            )

            qid = repository.save_question(q_model)
            self.current_question_id = qid

            if show_toast:
                QMessageBox.information(self, "Saved", "Question saved to learning history.")
        except Exception as e:
            logger.error(f"Failed to save question: {e}", exc_info=True)

    def open_feedback_dialog(self):
        if not self.current_question_id:
            self.save_to_history(show_toast=False)

        if not self.current_question_id:
            QMessageBox.warning(self, "Notice", "Please analyze the question before reporting.")
            return

        suggested = self.current_result_data.get("suggested_answer", "A") if self.current_result_data else "A"
        dlg = FeedbackDialog(self.current_question_id, suggested, self)
        if dlg.exec():
            QMessageBox.information(self, "Feedback Received", "Thank you. Your feedback has been recorded for review.")

