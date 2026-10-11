"""
Unit Tests for ExamPilot Database Layer
GT InnoX LLP
"""

import pytest
import tempfile
from pathlib import Path
from desktop.database.database import DatabaseManager
from desktop.database.repository import Repository
from desktop.database.models import QuestionModel, FeedbackModel

@pytest.fixture
def temp_repo():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = Path(tmp.name)
    manager = DatabaseManager(db_path=db_path)
    repo = Repository(manager=manager)
    yield repo, manager, db_path
    try:
        db_path.unlink(missing_ok=True)
    except Exception:
        pass

def test_database_initialization(temp_repo):
    repo, manager, _ = temp_repo
    subjects = repo.get_subjects()
    assert len(subjects) >= 8
    subject_names = [s["name"] for s in subjects]
    assert "Computer Science" in subject_names
    assert "Mathematics" in subject_names

def test_question_crud(temp_repo):
    repo, _, _ = temp_repo
    q = QuestionModel(
        question_text="Which data structure follows FIFO?",
        options={"A": "Stack", "B": "Queue", "C": "Tree", "D": "Graph"},
        suggested_answer="B",
        answer_text="Queue",
        explanation="Queue follows First In First Out.",
        confidence=0.95,
        subject_name="Computer Science"
    )
    qid = repo.save_question(q)
    assert qid is not None
    assert qid > 0

    retrieved = repo.get_question_by_id(qid)
    assert retrieved is not None
    assert retrieved.question_text == q.question_text
    assert retrieved.suggested_answer == "B"
    assert retrieved.options["B"] == "Queue"

    # Search
    search_results = repo.list_questions(search="FIFO")
    assert len(search_results) == 1
    assert search_results[0].id == qid

    # Delete
    deleted = repo.delete_question(qid)
    assert deleted is True
    assert repo.get_question_by_id(qid) is None

def test_feedback_and_analytics(temp_repo):
    repo, _, _ = temp_repo
    q = QuestionModel(
        question_text="Test question for analytics",
        options={"A": "Alpha", "B": "Beta"},
        suggested_answer="A",
        confidence=0.90,
        subject_name="Mathematics"
    )
    qid = repo.save_question(q)

    # Record feedback
    fb = FeedbackModel(question_id=qid, user_feedback="Incorrect key", corrected_answer="B")
    fid = repo.record_feedback(fb)
    assert fid > 0

    analytics = repo.get_dashboard_analytics()
    assert analytics["total_questions"] == 1
    assert analytics["accuracy"] == 0.0  # 1 question with 1 feedback flag

def test_settings_persistence(temp_repo):
    repo, _, _ = temp_repo
    repo.set_setting("hotkey", "Ctrl+Shift+Q")
    val = repo.get_setting("hotkey")
    assert val == "Ctrl+Shift+Q"

    repo.set_setting("hotkey", "Ctrl+Alt+P")
    assert repo.get_setting("hotkey") == "Ctrl+Alt+P"

def test_backup_and_restore(temp_repo):
    repo, manager, db_path = temp_repo
    q = QuestionModel(question_text="Backup test", options={"A": "1", "B": "2"})
    repo.save_question(q)

    with tempfile.NamedTemporaryFile(suffix=".bak", delete=False) as bkp:
        bkp_path = Path(bkp.name)

    try:
        success = manager.backup(bkp_path)
        assert success is True
        assert bkp_path.stat().st_size > 0

        # Clear history
        manager.clear_all_history()
        assert len(repo.list_questions()) == 0

        # Restore
        restored = manager.restore(bkp_path)
        assert restored is True
        assert len(repo.list_questions()) == 1
    finally:
        try:
            bkp_path.unlink(missing_ok=True)
        except Exception:
            pass

