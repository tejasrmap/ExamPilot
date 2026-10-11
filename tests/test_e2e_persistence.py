"""
E2E Database Persistence and Lifecycle Tests
GT InnoX LLP
"""

import tempfile
import csv
import json
from pathlib import Path
from desktop.database.database import DatabaseManager
from desktop.database.repository import Repository
from desktop.database.models import QuestionModel, FeedbackModel

def test_database_lifecycle_and_restart():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = Path(tmp.name)

    try:
        # Session 1: Create and write
        mgr1 = DatabaseManager(db_path=db_path)
        repo1 = Repository(manager=mgr1)

        q1 = QuestionModel(
            question_text="What is the time complexity of binary search?",
            options={"A": "O(1)", "B": "O(log n)", "C": "O(n)", "D": "O(n^2)"},
            suggested_answer="B",
            answer_text="O(log n)",
            explanation="Binary search divides search space in half each iteration.",
            confidence=0.97,
            subject_name="Computer Science"
        )
        qid1 = repo1.save_question(q1)
        assert qid1 > 0

        # Simulate Application Restart (drop instance, create new manager pointing to same file)
        del repo1
        del mgr1

        mgr2 = DatabaseManager(db_path=db_path)
        repo2 = Repository(manager=mgr2)

        # Verify question persisted across restart
        retrieved = repo2.get_question_by_id(qid1)
        assert retrieved is not None
        assert retrieved.question_text == q1.question_text
        assert retrieved.suggested_answer == "B"
        assert retrieved.confidence == 0.97

        # Search
        search_hits = repo2.list_questions(search="binary search")
        assert len(search_hits) == 1
        assert search_hits[0].id == qid1

        # Test CSV Export
        csv_file = db_path.with_suffix(".csv")
        questions = repo2.list_questions()
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Question", "Answer"])
            for q in questions:
                writer.writerow([q.id, q.question_text, q.suggested_answer])

        assert csv_file.exists()
        assert csv_file.stat().st_size > 0
        csv_file.unlink(missing_ok=True)

        # Individual Deletion
        del_success = repo2.delete_question(qid1)
        assert del_success is True
        assert repo2.get_question_by_id(qid1) is None

    finally:
        try:
            db_path.unlink(missing_ok=True)
        except Exception:
            pass

