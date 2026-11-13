"""
ExamPilot 2.0 — Option Identity Database Persistence Regression Suite
GT InnoX LLP — Understand Questions. Learn the Answers.

Verifies end-to-end database persistence, history retrieval, backward compatibility,
and deletion across real database sessions and FastAPI history endpoints.
"""

import json
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db.session import SessionLocal
from backend.app.db.models import Question, Profile, APIProvider
from backend.app.providers.base import QuestionAnalysisResult, ConfidenceModel

client = TestClient(app)

@pytest.fixture(scope="module")
def auth_context():
    """Register and configure an authenticated user with an encrypted API provider."""
    email = "persistence_audit@exampilot.com"
    pwd = "AuditSecretPassword123!"
    reg_res = client.post("/api/auth/register", json={
        "email": email,
        "password": pwd,
        "display_name": "Persistence Auditor"
    })
    if reg_res.status_code == 200:
        token = reg_res.json()["access_token"]
        user_id = reg_res.json()["user"]["id"]
    else:
        login_res = client.post("/api/auth/login", json={"email": email, "password": pwd})
        assert login_res.status_code == 200
        token = login_res.json()["access_token"]
        user_id = login_res.json()["user"]["id"]

    headers = {"Authorization": f"Bearer {token}"}

    client.post("/api/providers", headers=headers, json={
        "provider": "openai",
        "api_key": "sk-proj-testkey1234567890abcdef1234",
        "default_model": "gpt-4o-mini",
        "is_default": True
    })

    return {"headers": headers, "user_id": user_id}

# ---------------------------------------------------------------------------
# TEST 1: Unlettered Option Metadata Complete Lifecycle (Analysis -> DB -> History)
# ---------------------------------------------------------------------------
def test_unlettered_option_metadata_complete_persistence_roundtrip(auth_context):
    headers = auth_context["headers"]

    mock_result = QuestionAnalysisResult(
        question="What is the term for the computer software system in which organizations store data?",
        suggested_answer="B",
        answer_text="Database",
        explanation="A database provides secure multi-user structured storage.",
        option_analysis={"A": "Incorrect", "B": "Correct", "C": "Incorrect", "D": "Incorrect"},
        confidence=ConfidenceModel(level="high", reason="Core computer systems standard"),
        subject="Computer Science"
    )

    structured_opts = [
        {"id": "opt_uuid_101", "text": "Cache", "original_label": None, "internal_label": "A", "source_order": 1, "confidence": 0.99, "is_user_edited": False},
        {"id": "opt_uuid_102", "text": "Database", "original_label": None, "internal_label": "B", "source_order": 2, "confidence": 0.98, "is_user_edited": False},
        {"id": "opt_uuid_103", "text": "Catalog", "original_label": None, "internal_label": "C", "source_order": 3, "confidence": 0.97, "is_user_edited": False},
        {"id": "opt_uuid_104", "text": "Data ecosystem", "original_label": None, "internal_label": "D", "source_order": 4, "confidence": 0.99, "is_user_edited": False}
    ]

    payload = {
        "question_text": "What is the term for the computer software system in which organizations store data?",
        "options": {
            "A": "Cache",
            "B": "Database",
            "C": "Catalog",
            "D": "Data ecosystem"
        },
        "structured_options": structured_opts,
        "subject": "Computer Science"
    }

    # 1. Analyze and save to DB
    with patch("backend.app.providers.openai_provider.OpenAIProvider.generate_analysis", new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = mock_result
        analyze_res = client.post("/api/questions/analyse", headers=headers, json=payload)

    assert analyze_res.status_code == 200
    res_data = analyze_res.json()
    assert res_data["original_label"] is None
    assert res_data["source_position"] == 2

    # 2. Retrieve history list
    hist_res = client.get("/api/questions?limit=10", headers=headers)
    assert hist_res.status_code == 200
    history = hist_res.json()
    assert len(history) >= 1

    saved = next(q for q in history if q["question_text"] == payload["question_text"])
    q_id = saved["id"]

    # Verify unlettered presentation
    assert saved["original_label"] is None
    assert saved["source_position"] == 2
    assert saved["answer_text"] == "Database"
    assert saved["structured_options"] is not None
    assert len(saved["structured_options"]) == 4

    # Verify no option ID regeneration
    assert saved["structured_options"][0]["id"] == "opt_uuid_101"
    assert saved["structured_options"][1]["id"] == "opt_uuid_102"
    assert saved["structured_options"][1]["original_label"] is None
    assert saved["structured_options"][1]["source_order"] == 2

    # 3. Retrieve single-question endpoint
    single_res = client.get(f"/api/questions/{q_id}", headers=headers)
    assert single_res.status_code == 200
    single_q = single_res.json()
    assert single_q["id"] == q_id
    assert single_q["original_label"] is None
    assert single_q["source_position"] == 2
    assert single_q["structured_options"][1]["id"] == "opt_uuid_102"

# ---------------------------------------------------------------------------
# TEST 2: Lettered Option Metadata Complete Lifecycle
# ---------------------------------------------------------------------------
def test_lettered_option_metadata_complete_persistence_roundtrip(auth_context):
    headers = auth_context["headers"]

    mock_result = QuestionAnalysisResult(
        question="Which protocol operates at Layer 4 of the OSI model?",
        suggested_answer="B",
        answer_text="TCP",
        explanation="TCP is a transport layer protocol.",
        option_analysis={"A": "Incorrect: IP is Layer 3", "B": "Correct: TCP is Layer 4"},
        confidence=ConfidenceModel(level="high", reason="OSI standard"),
        subject="Networking"
    )

    lettered_structured = [
        {"id": "opt_let_1", "text": "IP", "original_label": "A", "internal_label": "A", "source_order": 1, "confidence": 0.99, "is_user_edited": False},
        {"id": "opt_let_2", "text": "TCP", "original_label": "B", "internal_label": "B", "source_order": 2, "confidence": 0.99, "is_user_edited": False}
    ]

    payload = {
        "question_text": "Which protocol operates at Layer 4 of the OSI model?",
        "options": {"A": "IP", "B": "TCP"},
        "structured_options": lettered_structured,
        "subject": "Networking"
    }

    with patch("backend.app.providers.openai_provider.OpenAIProvider.generate_analysis", new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = mock_result
        analyze_res = client.post("/api/questions/analyse", headers=headers, json=payload)

    assert analyze_res.status_code == 200
    hist_res = client.get("/api/questions", headers=headers)
    history = hist_res.json()
    saved = next(q for q in history if q["question_text"] == payload["question_text"])

    assert saved["original_label"] == "B"
    assert saved["source_position"] == 2
    assert saved["suggested_answer"] == "B"
    assert saved["structured_options"][1]["original_label"] == "B"

# ---------------------------------------------------------------------------
# TEST 3: User-Edited Option Text and is_user_edited Survive Persistence
# ---------------------------------------------------------------------------
def test_user_edited_option_metadata_survives_persistence(auth_context):
    headers = auth_context["headers"]

    mock_result = QuestionAnalysisResult(
        question="Identify the permanent data deletion phase in the Data Life Cycle.",
        suggested_answer="C",
        answer_text="Destroy",
        explanation="The destroy phase securely deletes data.",
        option_analysis={"A": "Incorrect", "B": "Incorrect", "C": "Correct: Destroy"},
        confidence=ConfidenceModel(level="high", reason="Google Data Analytics curriculum"),
        subject="Data Science"
    )

    structured_opts = [
        {"id": "opt_edit_1", "text": "Plan", "original_label": None, "internal_label": "A", "source_order": 1, "confidence": 0.95, "is_user_edited": False},
        {"id": "opt_edit_2", "text": "Archive", "original_label": None, "internal_label": "B", "source_order": 2, "confidence": 0.95, "is_user_edited": False},
        # User manually fixed OCR typo "Destrooy" -> "Destroy"
        {"id": "opt_edit_3", "text": "Destroy", "original_label": None, "internal_label": "C", "source_order": 3, "confidence": 0.82, "is_user_edited": True}
    ]

    payload = {
        "question_text": "Identify the permanent data deletion phase in the Data Life Cycle.",
        "options": {"A": "Plan", "B": "Archive", "C": "Destroy"},
        "structured_options": structured_opts,
        "subject": "Data Science"
    }

    with patch("backend.app.providers.openai_provider.OpenAIProvider.generate_analysis", new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = mock_result
        analyze_res = client.post("/api/questions/analyse", headers=headers, json=payload)

    assert analyze_res.status_code == 200
    hist_res = client.get("/api/questions", headers=headers)
    saved = next(q for q in hist_res.json() if q["question_text"] == payload["question_text"])

    assert saved["structured_options"][2]["is_user_edited"] is True
    assert saved["structured_options"][2]["text"] == "Destroy"
    assert saved["structured_options"][2]["source_order"] == 3
    assert saved["structured_options"][0]["is_user_edited"] is False

# ---------------------------------------------------------------------------
# TEST 4: Source Order and Original Labels Remain Unchanged
# ---------------------------------------------------------------------------
def test_source_order_and_original_labels_remain_unchanged(auth_context):
    headers = auth_context["headers"]

    mock_result = QuestionAnalysisResult(
        question="Which sorting algorithm has average O(n log n) runtime?",
        suggested_answer="A",
        answer_text="Merge Sort",
        explanation="Merge Sort is divide and conquer with O(n log n).",
        option_analysis={"A": "Correct: Merge Sort", "B": "Incorrect: Bubble Sort"},
        confidence=ConfidenceModel(level="high", reason="Algorithm complexity"),
        subject="Computer Science"
    )

    structured_opts = [
        {"id": "opt_sort_1", "text": "Merge Sort", "original_label": "1", "internal_label": "A", "source_order": 1, "confidence": 0.99, "is_user_edited": False},
        {"id": "opt_sort_2", "text": "Bubble Sort", "original_label": "2", "internal_label": "B", "source_order": 2, "confidence": 0.99, "is_user_edited": False}
    ]

    payload = {
        "question_text": "Which sorting algorithm has average O(n log n) runtime?",
        "options": {"A": "Merge Sort", "B": "Bubble Sort"},
        "structured_options": structured_opts,
        "subject": "Computer Science"
    }

    with patch("backend.app.providers.openai_provider.OpenAIProvider.generate_analysis", new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = mock_result
        client.post("/api/questions/analyse", headers=headers, json=payload)

    hist_res = client.get("/api/questions", headers=headers)
    saved = next(q for q in hist_res.json() if q["question_text"] == payload["question_text"])

    assert saved["original_label"] == "1"
    assert saved["source_position"] == 1
    assert saved["structured_options"][0]["id"] == "opt_sort_1"
    assert saved["structured_options"][0]["original_label"] == "1"
    assert saved["structured_options"][0]["source_order"] == 1

# ---------------------------------------------------------------------------
# TEST 5: Existing Historical Records Without Structured Metadata Load Successfully
# ---------------------------------------------------------------------------
def test_existing_historical_records_without_structured_metadata_load_successfully(auth_context):
    headers = auth_context["headers"]
    user_id = auth_context["user_id"]

    # Directly insert a legacy Question record where structured_options_json IS NULL
    db = SessionLocal()
    try:
        legacy_q = Question(
            user_id=user_id,
            question_text="Legacy question created before structured options migration.",
            options_json=json.dumps({"A": "Option Alpha", "B": "Option Beta"}),
            structured_options_json=None, # Legacy record without structured metadata
            suggested_answer="A",
            answer_text="Option Alpha",
            explanation="Legacy explanation.",
            option_analysis_json=json.dumps({"A": "Correct", "B": "Incorrect"}),
            confidence_level="high",
            confidence_reason="Legacy",
            subject_name="General",
            provider="openai",
            model="gpt-4o-mini"
        )
        db.add(legacy_q)
        db.commit()
        db.refresh(legacy_q)
        legacy_id = legacy_q.id
    finally:
        db.close()

    # 1. Fetch via history list
    hist_res = client.get("/api/questions", headers=headers)
    assert hist_res.status_code == 200
    saved = next(q for q in hist_res.json() if q["id"] == legacy_id)

    assert saved["question_text"] == "Legacy question created before structured options migration."
    assert saved["options"] == {"A": "Option Alpha", "B": "Option Beta"}
    assert saved["structured_options"] is None # None handled cleanly without crashing
    assert saved["original_label"] == "A"
    assert saved["source_position"] == 1

    # 2. Fetch via single question endpoint
    single_res = client.get(f"/api/questions/{legacy_id}", headers=headers)
    assert single_res.status_code == 200
    single_data = single_res.json()
    assert single_data["id"] == legacy_id
    assert single_data["structured_options"] is None

# ---------------------------------------------------------------------------
# TEST 6: Deleting a Question Cleans Up Metadata Completely
# ---------------------------------------------------------------------------
def test_delete_question_cleans_up_metadata(auth_context):
    headers = auth_context["headers"]

    mock_result = QuestionAnalysisResult(
        question="Question to be deleted completely.",
        suggested_answer="A",
        answer_text="ToDelete",
        explanation="Will be deleted.",
        option_analysis={"A": "Correct", "B": "Incorrect"},
        confidence=ConfidenceModel(level="high", reason="Test"),
        subject="General"
    )

    structured_opts = [
        {"id": "opt_del_1", "text": "ToDelete", "original_label": None, "internal_label": "A", "source_order": 1, "confidence": 1.0, "is_user_edited": False},
        {"id": "opt_del_2", "text": "Distractor", "original_label": None, "internal_label": "B", "source_order": 2, "confidence": 1.0, "is_user_edited": False}
    ]

    payload = {
        "question_text": "Question to be deleted completely.",
        "options": {"A": "ToDelete", "B": "Distractor"},
        "structured_options": structured_opts,
        "subject": "General"
    }

    with patch("backend.app.providers.openai_provider.OpenAIProvider.generate_analysis", new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = mock_result
        client.post("/api/questions/analyse", headers=headers, json=payload)

    hist_res = client.get("/api/questions", headers=headers)
    saved = next(q for q in hist_res.json() if q["question_text"] == payload["question_text"])
    q_id = saved["id"]

    # Verify exists in database
    db = SessionLocal()
    try:
        assert db.query(Question).filter(Question.id == q_id).first() is not None
    finally:
        db.close()

    # Delete via API
    del_res = client.delete(f"/api/questions/{q_id}", headers=headers)
    assert del_res.status_code == 200

    # Verify single question returns 404
    assert client.get(f"/api/questions/{q_id}", headers=headers).status_code == 404

    # Verify completely deleted from database
    db = SessionLocal()
    try:
        assert db.query(Question).filter(Question.id == q_id).first() is None
    finally:
        db.close()

