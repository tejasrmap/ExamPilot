"""
ExamPilot Database Repository
GT InnoX LLP
"""

import json
from typing import List, Optional, Dict, Any
from desktop.database.database import db_manager, DatabaseManager
from desktop.database.models import QuestionModel, FeedbackModel, SettingModel
from desktop.utils.logger import logger

class Repository:
    def __init__(self, manager: DatabaseManager = db_manager):
        self.db = manager

    # --- Questions ---
    def save_question(self, q: QuestionModel) -> int:
        """Insert or update a question."""
        with self.db.get_connection() as conn:
            cur = conn.cursor()
            
            # Resolve subject_id if not given but subject_name exists
            subj_id = q.subject_id
            if not subj_id and q.subject_name:
                cur.execute("SELECT id FROM subjects WHERE subject_name = ?", (q.subject_name,))
                row = cur.fetchone()
                if row:
                    subj_id = row[0]
                else:
                    cur.execute("INSERT INTO subjects (subject_name) VALUES (?)", (q.subject_name,))
                    subj_id = cur.lastrowid

            options_json = json.dumps(q.options, ensure_ascii=False)
            analysis_json = json.dumps(q.option_analysis, ensure_ascii=False)

            if q.id:
                cur.execute("""
                    UPDATE questions
                    SET question_text = ?, options_json = ?, suggested_answer = ?,
                        answer_text = ?, explanation = ?, option_analysis_json = ?,
                        confidence = ?, needs_review = ?, subject_id = ?
                    WHERE id = ?
                """, (
                    q.question_text, options_json, q.suggested_answer,
                    q.answer_text, q.explanation, analysis_json,
                    q.confidence, 1 if q.needs_review else 0, subj_id, q.id
                ))
                qid = q.id
            else:
                cur.execute("""
                    INSERT INTO questions (
                        question_text, options_json, suggested_answer,
                        answer_text, explanation, option_analysis_json,
                        confidence, needs_review, subject_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    q.question_text, options_json, q.suggested_answer,
                    q.answer_text, q.explanation, analysis_json,
                    q.confidence, 1 if q.needs_review else 0, subj_id
                ))
                qid = cur.lastrowid
            conn.commit()
            return qid

    def get_question_by_id(self, question_id: int) -> Optional[QuestionModel]:
        with self.db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT q.*, s.subject_name
                FROM questions q
                LEFT JOIN subjects s ON q.subject_id = s.id
                WHERE q.id = ?
            """, (question_id,))
            row = cur.fetchone()
            if not row:
                return None
            return self._row_to_question(row)

    def list_questions(
        self,
        subject_id: Optional[int] = None,
        search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[QuestionModel]:
        with self.db.get_connection() as conn:
            cur = conn.cursor()
            query = """
                SELECT q.*, s.subject_name
                FROM questions q
                LEFT JOIN subjects s ON q.subject_id = s.id
                WHERE 1=1
            """
            params: List[Any] = []

            if subject_id:
                query += " AND q.subject_id = ?"
                params.append(subject_id)

            if search:
                query += " AND (q.question_text LIKE ? OR q.explanation LIKE ?)"
                search_term = f"%{search}%"
                params.extend([search_term, search_term])

            query += " ORDER BY q.created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            cur.execute(query, params)
            return [self._row_to_question(row) for row in cur.fetchall()]

    def delete_question(self, question_id: int) -> bool:
        with self.db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM questions WHERE id = ?", (question_id,))
            conn.commit()
            return cur.rowcount > 0

    def _row_to_question(self, row: Any) -> QuestionModel:
        options = {}
        try:
            options = json.loads(row["options_json"])
        except Exception:
            pass

        analysis = {}
        try:
            if row["option_analysis_json"]:
                analysis = json.loads(row["option_analysis_json"])
        except Exception:
            pass

        return QuestionModel(
            id=row["id"],
            question_text=row["question_text"],
            options=options,
            suggested_answer=row["suggested_answer"],
            answer_text=row["answer_text"],
            explanation=row["explanation"],
            option_analysis=analysis,
            confidence=row["confidence"] or 0.0,
            needs_review=bool(row["needs_review"]),
            subject_id=row["subject_id"],
            subject_name=row["subject_name"] or "General",
            created_at=str(row["created_at"])
        )

    # --- Subjects ---
    def get_subjects(self) -> List[Dict[str, Any]]:
        with self.db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, subject_name FROM subjects ORDER BY subject_name ASC")
            return [{"id": row["id"], "name": row["subject_name"]} for row in cur.fetchall()]

    def add_subject(self, name: str) -> int:
        with self.db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("INSERT OR IGNORE INTO subjects (subject_name) VALUES (?)", (name.strip(),))
            conn.commit()
            cur.execute("SELECT id FROM subjects WHERE subject_name = ?", (name.strip(),))
            return cur.fetchone()[0]

    # --- Feedback ---
    def record_feedback(self, feedback: FeedbackModel) -> int:
        with self.db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO question_feedback (question_id, user_feedback, corrected_answer)
                VALUES (?, ?, ?)
            """, (feedback.question_id, feedback.user_feedback, feedback.corrected_answer))
            # Also mark question as needing review
            cur.execute("UPDATE questions SET needs_review = 1 WHERE id = ?", (feedback.question_id,))
            conn.commit()
            return cur.lastrowid

    # --- Settings ---
    def get_setting(self, key: str, default: str = "") -> str:
        with self.db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT setting_value FROM settings WHERE setting_key = ?", (key,))
            row = cur.fetchone()
            return row["setting_value"] if row else default

    def set_setting(self, key: str, value: str) -> bool:
        with self.db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO settings (setting_key, setting_value)
                VALUES (?, ?)
                ON CONFLICT(setting_key) DO UPDATE SET setting_value = excluded.setting_value
            """, (key, str(value)))
            conn.commit()
            return True

    # --- Analytics & Dashboard Stats ---
    def get_dashboard_analytics(self) -> Dict[str, Any]:
        with self.db.get_connection() as conn:
            cur = conn.cursor()
            
            # Total questions
            cur.execute("SELECT COUNT(*) FROM questions")
            total_questions = cur.fetchone()[0]

            # Feedback count (reports)
            cur.execute("SELECT COUNT(*) FROM question_feedback")
            feedback_count = cur.fetchone()[0]

            # Accuracy estimation:
            # Questions with no negative feedback vs total questions
            accuracy = 100.0 if total_questions == 0 else round(
                max(0.0, (total_questions - feedback_count) / total_questions * 100.0), 1
            )

            # Average confidence
            cur.execute("SELECT AVG(confidence) FROM questions WHERE confidence > 0")
            avg_conf_row = cur.fetchone()[0]
            avg_confidence = round((avg_conf_row or 0.0) * 100, 1)

            # Practice sessions count
            cur.execute("SELECT COUNT(*) FROM practice_sessions")
            sessions_count = cur.fetchone()[0]

            # Subject breakdown
            cur.execute("""
                SELECT s.subject_name, COUNT(q.id) as count
                FROM subjects s
                LEFT JOIN questions q ON s.id = q.subject_id
                GROUP BY s.id
                ORDER BY count DESC
            """)
            subject_counts = [{"subject": row["subject_name"], "count": row["count"]} for row in cur.fetchall()]

            # Recent questions (up to 5)
            cur.execute("""
                SELECT q.id, q.question_text, q.suggested_answer, q.confidence, q.created_at, s.subject_name
                FROM questions q
                LEFT JOIN subjects s ON q.subject_id = s.id
                ORDER BY q.created_at DESC LIMIT 5
            """)
            recent_questions = [
                {
                    "id": r["id"],
                    "question_text": r["question_text"],
                    "suggested_answer": r["suggested_answer"],
                    "confidence": r["confidence"],
                    "created_at": r["created_at"],
                    "subject": r["subject_name"] or "General"
                }
                for r in cur.fetchall()
            ]

            return {
                "total_questions": total_questions,
                "accuracy": accuracy,
                "sessions_count": sessions_count,
                "avg_confidence": avg_confidence,
                "subject_counts": subject_counts,
                "recent_questions": recent_questions
            }

repository = Repository()

