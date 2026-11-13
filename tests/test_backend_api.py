import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.security import encrypt_api_key, decrypt_api_key, mask_api_key

client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["product"] == "ExamPilot 2.0"

def test_api_key_encryption_and_masking():
    raw_key = "sk-proj-9876543210fedcba9876"
    encrypted = encrypt_api_key(raw_key)
    assert encrypted != raw_key
    decrypted = decrypt_api_key(encrypted)
    assert decrypted == raw_key
    masked = mask_api_key(raw_key)
    assert "••••" in masked
    assert not raw_key in masked

def test_auth_and_user_lifecycle():
    # 1. Register test user
    email = "testuser@exampilot.com"
    pwd = "SecurePassword123!"
    reg_res = client.post("/api/auth/register", json={
        "email": email,
        "password": pwd,
        "display_name": "Test Architect"
    })
    # If already exists, login instead
    if reg_res.status_code == 400:
        login_res = client.post("/api/auth/login", json={"email": email, "password": pwd})
        assert login_res.status_code == 200
        token = login_res.json()["access_token"]
    else:
        assert reg_res.status_code == 200
        token = reg_res.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get Profile
    prof_res = client.get("/api/auth/profile", headers=headers)
    assert prof_res.status_code == 200
    assert prof_res.json()["email"] == email

    # 3. Add Provider with encrypted key
    prov_res = client.post("/api/providers", headers=headers, json={
        "provider": "openai",
        "api_key": "sk-proj-testkey1234567890abcdef1234",
        "default_model": "gpt-4o-mini",
        "is_default": True
    })
    assert prov_res.status_code == 200
    prov_data = prov_res.json()
    assert prov_data["provider"] == "openai"
    assert "••••" in prov_data["masked_key"]
    # Ensure plaintext key is NEVER returned in response
    assert "sk-proj-testkey1234567890abcdef1234" not in str(prov_data)

    # 4. List Models
    models_res = client.get("/api/providers/models?provider=openai", headers=headers)
    assert models_res.status_code == 200
    assert len(models_res.json()) >= 1

    # 5. Question OCR status
    ocr_status = client.get("/api/ocr/status")
    assert ocr_status.status_code == 200
    assert ocr_status.json()["ready"] is True

    # 6. Analytics Overview (Empty state verification)
    analytics_res = client.get("/api/analytics/overview", headers=headers)
    assert analytics_res.status_code == 200
    assert "total_questions_scanned" in analytics_res.json()

    # 7. Practice Test Creation
    practice_res = client.post("/api/practice", headers=headers, json={
        "title": "Computer Architecture Midterm Practice",
        "subject": "Computer Science",
        "question_count": 1
    })
    assert practice_res.status_code == 200
    test_data = practice_res.json()
    session_id = test_data["session_id"]
    q_id = test_data["questions"][0]["id"]

    # 8. Practice Test Submission
    submit_res = client.post("/api/practice/submit", headers=headers, json={
        "session_id": session_id,
        "answers": [{"question_id": q_id, "selected_answer": "A"}]
    })
    assert submit_res.status_code == 200
    sub_data = submit_res.json()
    assert "score_percentage" in sub_data

    # 9. Data Export
    export_res = client.get("/api/settings/export", headers=headers)
    assert export_res.status_code == 200
    assert export_res.json()["user"]["email"] == email

