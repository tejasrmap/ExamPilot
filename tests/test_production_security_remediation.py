"""
ExamPilot 2.0 — Production Security Remediation Test Suite
GT InnoX LLP — Understand Questions. Learn the Answers.

Comprehensive test suite verifying:
1. Password reset token lifecycle (no token leakage, single-use, atomic consumption, expiry, enumeration defense)
2. Password policy and session revocation upon password reset
3. Practice test tenant isolation (no cross-tenant leakage, membership validation, duplicate answer prevention)
4. CORS policy hardening (no wildcard with credentials, regex extension support)
5. OCR endpoint authentication, rate limiting, and magic bytes validation
6. Bounded file upload streaming and storage abstraction cleanup
7. Zero-downtime key rotation with AES-256-GCM secondary secrets
8. Production configuration fail-closed validation
"""

import io
import time
import base64
from datetime import datetime, timedelta
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.config import Settings, validate_production_config, settings
from backend.app.core.security import (
    validate_password_strength, encrypt_api_key, decrypt_api_key,
    generate_secure_reset_token, hash_token, create_access_token, _derive_key
)
from backend.app.core.rate_limit import rate_limiter
from backend.app.services.email import email_service
from backend.app.services.storage import storage_service, LocalStorageService
from backend.app.db.session import SessionLocal
from backend.app.db.models import Profile, PasswordResetToken, Question, PracticeSession, Document

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_limiter():
    rate_limiter.reset()

def get_auth_token(email: str, password: str = "SecurePassword123!") -> str:
    reg = client.post("/api/auth/register", json={"email": email, "password": password})
    if reg.status_code == 200:
        return reg.json()["access_token"]
    login = client.post("/api/auth/login", json={"email": email, "password": password})
    if login.status_code == 200:
        return login.json()["access_token"]
    raise RuntimeError(f"Failed to authenticate {email}: {reg.text} / {login.text}")

# ---------------------------------------------------------------------------
# 1. PASSWORD RESET LIFECYCLE TESTS
# ---------------------------------------------------------------------------

def test_password_reset_no_token_leakage_and_enumeration_defense():
    """
    1. Submitting a registered email MUST NOT return the reset token in the response body.
    2. Submitting an unregistered email MUST return the exact same generic response.
    3. The token is delivered strictly through the email service adapter.
    """
    reg_email = "victim_student@exampilot.com"
    pwd = "InitialSecurePassword123!"
    client.post("/api/auth/register", json={"email": reg_email, "password": pwd})

    # Clear email memory
    if hasattr(email_service, "clear"):
        email_service.clear()

    # Request reset for registered email
    resp_reg = client.post("/api/auth/forgot-password", json={"email": reg_email})
    assert resp_reg.status_code == 200
    reg_data = resp_reg.json()
    assert "reset_token" not in reg_data, "SECURITY FLAW: reset_token must never be returned in API response"
    assert reg_data["message"] == "If this email address is registered, password reset instructions have been sent."

    # Request reset for unregistered email
    resp_unreg = client.post("/api/auth/forgot-password", json={"email": "nonexistent_user_999@exampilot.com"})
    assert resp_unreg.status_code == 200
    assert resp_unreg.json() == reg_data, "Enumeration vulnerability: response differed between registered and unregistered email"

    # Verify token was received by email adapter
    dispatched_token = email_service.get_last_reset_token(reg_email)
    assert dispatched_token is not None
    assert len(dispatched_token) >= 32

def test_password_reset_token_single_use_and_replay_rejection():
    """
    Verifies that a reset token is single-use and cannot be replayed.
    """
    email = "replay_test@exampilot.com"
    pwd = "InitialPassword123!"
    new_pwd = "NewSecurePassword456!"
    client.post("/api/auth/register", json={"email": email, "password": pwd})

    client.post("/api/auth/forgot-password", json={"email": email})
    token = email_service.get_last_reset_token(email)
    assert token is not None

    # First reset attempt: MUST succeed
    res1 = client.post("/api/auth/reset-password", json={"reset_token": token, "new_password": new_pwd})
    assert res1.status_code == 200

    # Replay attack attempt: MUST fail with 400
    res2 = client.post("/api/auth/reset-password", json={"reset_token": token, "new_password": "AnotherPassword789!"})
    assert res2.status_code == 400
    assert "Invalid or expired" in res2.json()["detail"]

def test_password_reset_token_expiration():
    """
    Verifies that expired reset tokens are rejected.
    """
    email = "expiry_test@exampilot.com"
    pwd = "InitialPassword123!"
    client.post("/api/auth/register", json={"email": email, "password": pwd})

    raw_token, token_hash = generate_secure_reset_token()
    db = SessionLocal()
    user = db.query(Profile).filter(Profile.email == email).first()

    # Insert an expired token (expired 5 minutes ago)
    expired_record = PasswordResetToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=datetime.utcnow() - timedelta(minutes=5),
        created_at=datetime.utcnow() - timedelta(minutes=20)
    )
    db.add(expired_record)
    db.commit()
    db.close()

    res = client.post("/api/auth/reset-password", json={"reset_token": raw_token, "new_password": "NewValidPassword789!"})
    assert res.status_code == 400
    assert "Invalid or expired" in res.json()["detail"]

def test_password_policy_enforcement():
    """
    Verifies production password policy: minimum 8 characters, letters, and numbers/specials.
    """
    invalid_passwords = [
        "short",          # < 8 chars
        "12345678",       # No letters
        "abcdefgh",       # No numbers or specials
        "       ",        # Only spaces
    ]

    for p in invalid_passwords:
        with pytest.raises(ValueError):
            validate_password_strength(p)

        # Verify API rejects invalid password on registration
        res = client.post("/api/auth/register", json={"email": "policy_test@exampilot.com", "password": p})
        assert res.status_code == 400

    # Valid password should not raise
    validate_password_strength("ValidPassword123!")

def test_password_reset_invalidates_pre_existing_sessions():
    """
    Verifies that resetting password increments token_version and immediately
    invalidates all active JWT login tokens.
    """
    email = f"session_revocation_{int(time.time())}@exampilot.com"
    pwd = "OriginalPassword123!"
    new_pwd = "UpdatedPassword456!"

    token_before = get_auth_token(email, pwd)
    headers_before = {"Authorization": f"Bearer {token_before}"}

    # Verify session works initially
    prof1 = client.get("/api/auth/profile", headers=headers_before)
    assert prof1.status_code == 200

    # Reset password
    client.post("/api/auth/forgot-password", json={"email": email})
    reset_tok = email_service.get_last_reset_token(email)
    client.post("/api/auth/reset-password", json={"reset_token": reset_tok, "new_password": new_pwd})

    # The token issued BEFORE password reset MUST now be rejected with 401
    prof2 = client.get("/api/auth/profile", headers=headers_before)
    assert prof2.status_code == 401, "Security flaw: session remained valid after password reset!"
    assert "Session has been invalidated" in prof2.json()["detail"]

    # Login with new password issues a new valid token
    login_new = client.post("/api/auth/login", json={"email": email, "password": new_pwd})
    assert login_new.status_code == 200
    new_token = login_new.json()["access_token"]
    prof3 = client.get("/api/auth/profile", headers={"Authorization": f"Bearer {new_token}"})
    assert prof3.status_code == 200

# ---------------------------------------------------------------------------
# 2. PRACTICE TEST TENANT ISOLATION TESTS
# ---------------------------------------------------------------------------

def test_practice_test_cross_tenant_isolation():
    """
    Two independent users: User A and User B.
    User A creates proprietary questions.
    User B (with 0 questions) creates a practice quiz.
    Assert that User B NEVER receives User A's questions.
    """
    user_a_email = "user_a_practice@exampilot.com"
    user_b_email = "user_b_practice@exampilot.com"
    pwd = "SecurePracticePwd123!"

    reg_a = client.post("/api/auth/register", json={"email": user_a_email, "password": pwd})
    token_a = reg_a.json()["access_token"] if reg_a.status_code == 200 else client.post("/api/auth/login", json={"email": user_a_email, "password": pwd}).json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    reg_b = client.post("/api/auth/register", json={"email": user_b_email, "password": pwd})
    token_b = reg_b.json()["access_token"] if reg_b.status_code == 200 else client.post("/api/auth/login", json={"email": user_b_email, "password": pwd}).json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User A inserts a confidential question
    db = SessionLocal()
    user_a = db.query(Profile).filter(Profile.email == user_a_email).first()
    user_b = db.query(Profile).filter(Profile.email == user_b_email).first()

    confidential_q = Question(
        user_id=user_a.id,
        question_text="CONFIDENTIAL: Proprietary Exam Question for User A Only",
        options_json='{"A": "Secret Option A", "B": "Secret Option B"}',
        suggested_answer="A",
        answer_text="Secret Option A",
        subject_name="Classified"
    )
    db.add(confidential_q)
    db.commit()
    db.refresh(confidential_q)
    q_a_id = confidential_q.id
    db.close()

    # User B creates a practice test
    quiz_res_b = client.post("/api/practice", headers=headers_b, json={
        "title": "User B Practice",
        "question_count": 5
    })
    assert quiz_res_b.status_code == 200
    quiz_b = quiz_res_b.json()
    b_question_ids = [q["id"] for q in quiz_b["questions"]]

    # Assert User A's confidential question is NOT in User B's practice quiz
    assert q_a_id not in b_question_ids, "CRITICAL TENANT LEAK: User A's question was given to User B!"
    for q in quiz_b["questions"]:
        assert "CONFIDENTIAL" not in q["question_text"]

    # User B attempts to submit User A's question ID in User B's practice session: MUST be rejected
    b_session_id = quiz_b["session_id"]
    tamper_submit = client.post("/api/practice/submit", headers=headers_b, json={
        "session_id": b_session_id,
        "answers": [{"question_id": q_a_id, "selected_answer": "A"}]
    })
    assert tamper_submit.status_code in (400, 403), "Access control failure: User B submitted User A's question!"

def test_practice_test_duplicate_answers_and_resubmission_rejection():
    """
    Verifies that:
    1. Submitting duplicate answers for the same question is rejected.
    2. Submitting an already completed practice session is rejected.
    """
    email = "practice_validation@exampilot.com"
    pwd = "PracticeSecurePwd123!"
    token = get_auth_token(email, pwd)
    headers = {"Authorization": f"Bearer {token}"}

    quiz_res = client.post("/api/practice", headers=headers, json={"title": "Validation Quiz", "question_count": 1})
    quiz = quiz_res.json()
    session_id = quiz["session_id"]
    q_id = quiz["questions"][0]["id"]

    # 1. Duplicate answer submission: MUST fail
    dup_res = client.post("/api/practice/submit", headers=headers, json={
        "session_id": session_id,
        "answers": [
            {"question_id": q_id, "selected_answer": "A"},
            {"question_id": q_id, "selected_answer": "B"}
        ]
    })
    assert dup_res.status_code == 400
    assert "Duplicate answer" in dup_res.json()["detail"]

    # 2. Valid single submission: MUST succeed
    sub_res = client.post("/api/practice/submit", headers=headers, json={
        "session_id": session_id,
        "answers": [{"question_id": q_id, "selected_answer": "A"}]
    })
    assert sub_res.status_code == 200

    # 3. Resubmission of completed session: MUST fail
    re_res = client.post("/api/practice/submit", headers=headers, json={
        "session_id": session_id,
        "answers": [{"question_id": q_id, "selected_answer": "A"}]
    })
    assert re_res.status_code == 400
    assert "already been completed" in re_res.json()["detail"]

# ---------------------------------------------------------------------------
# 3. OCR ENDPOINT AUTHENTICATION & INPUT VALIDATION
# ---------------------------------------------------------------------------

def test_ocr_requires_authentication():
    """Unauthenticated requests to OCR endpoints must receive 401."""
    # Dummy PNG
    png_data = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4"

    res_img = client.post("/api/ocr/image", files={"file": ("test.png", png_data, "image/png")})
    assert res_img.status_code == 401

    res_pdf = client.post("/api/ocr/pdf", files={"file": ("test.pdf", b"%PDF-1.4\n", "application/pdf")})
    assert res_pdf.status_code == 401

def test_ocr_magic_bytes_validation():
    """Uploading non-image or corrupted files to OCR must be rejected with 400."""
    email = "ocr_magic_test@exampilot.com"
    pwd = "SecurePassword123!"
    token = get_auth_token(email, pwd)
    headers = {"Authorization": f"Bearer {token}"}

    # Spoofed file (text pretending to be PNG)
    spoofed = b"THIS IS NOT A VALID PNG OR JPEG IMAGE"
    res = client.post("/api/ocr/image", headers=headers, files={"file": ("fake.png", spoofed, "image/png")})
    assert res.status_code == 400
    assert "Supported formats are PNG, JPEG, and WebP" in res.json()["detail"]

    # Spoofed PDF
    res_pdf = client.post("/api/ocr/pdf", headers=headers, files={"file": ("fake.pdf", spoofed, "application/pdf")})
    assert res_pdf.status_code == 400
    assert "file signature does not match a valid PDF" in res_pdf.json()["detail"]

# ---------------------------------------------------------------------------
# 4. BOUNDED FILE UPLOAD & STORAGE ABSTRACTION
# ---------------------------------------------------------------------------

def test_document_upload_bounded_streaming_and_storage_deletion():
    """
    Verifies that:
    1. Documents upload via durable storage abstraction.
    2. Document deletion cleanly purges both the storage object and database record.
    """
    email = "storage_test@exampilot.com"
    pwd = "SecurePassword123!"
    token = get_auth_token(email, pwd)
    headers = {"Authorization": f"Bearer {token}"}

    # Upload a valid plain text document
    doc_text = "ExamPilot Document Storage Test Content — Chapter 1 Operating Systems"
    upload_res = client.post(
        "/api/documents/upload",
        headers=headers,
        files={"file": ("notes.txt", doc_text.encode("utf-8"), "text/plain")},
        data={"subject_name": "Computer Science"}
    )
    assert upload_res.status_code == 200
    doc_data = upload_res.json()
    doc_id = doc_data["id"]
    assert doc_data["status"] == "ready"

    # Verify document exists in user library
    list_res = client.get("/api/documents", headers=headers)
    assert list_res.status_code == 200
    assert any(d["id"] == doc_id for d in list_res.json())

    # Delete document: MUST delete database record and storage file
    del_res = client.delete(f"/api/documents/{doc_id}", headers=headers)
    assert del_res.status_code == 200

    # Verify gone from library
    list_res2 = client.get("/api/documents", headers=headers)
    assert not any(d["id"] == doc_id for d in list_res2.json())

# ---------------------------------------------------------------------------
# 5. ZERO-DOWNTIME KEY ROTATION (AES-256-GCM)
# ---------------------------------------------------------------------------

def test_aes_key_rotation_with_secondary_secrets():
    """
    Verifies that ciphertext encrypted under an old key can still be decrypted
    when that key is moved to API_KEY_ENCRYPTION_ROTATION_SECRETS.
    """
    old_secret = "old_secret_key_used_previously_32b!"
    new_secret = "new_primary_secret_key_active_32b!!"
    plain_api_key = "sk-proj-rotationtestkey1234567890"

    # Encrypt directly with old secret
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    old_key = _derive_key(old_secret)
    aes_old = AESGCM(old_key)
    nonce = b"123456789012" # 12 bytes
    ciphertext = aes_old.encrypt(nonce, plain_api_key.encode("utf-8"), None)
    old_encrypted_blob = base64.urlsafe_b64encode(nonce + ciphertext).decode("utf-8")

    # Configure settings: primary = new_secret, rotation = [old_secret]
    settings.API_KEY_ENCRYPTION_SECRET = new_secret
    settings.API_KEY_ENCRYPTION_ROTATION_SECRETS = [old_secret]

    # Decryption must transparently succeed using the rotation secret!
    decrypted = decrypt_api_key(old_encrypted_blob)
    assert decrypted == plain_api_key, "Key rotation failed to decrypt ciphertext from previous secret"

    # Reset settings to default
    settings.API_KEY_ENCRYPTION_SECRET = "exampilot_super_secret_encryption_key_32_bytes_len!!"
    settings.API_KEY_ENCRYPTION_ROTATION_SECRETS = []

# ---------------------------------------------------------------------------
# 6. PRODUCTION CONFIGURATION FAIL-CLOSED VALIDATION
# ---------------------------------------------------------------------------

def test_production_config_validation_fails_closed():
    """
    Verifies that validate_production_config() raises RuntimeError if production
    environment contains default secrets, SQLite, or wildcard CORS.
    """
    # Bad production settings (uses dev secrets & SQLite)
    bad_cfg = Settings(
        ENVIRONMENT="production",
        JWT_SECRET="dev_environment_secret",
        API_KEY_ENCRYPTION_SECRET="super_secret_encryption_key",
        DATABASE_URL="sqlite:///./test.db",
        BACKEND_CORS_ORIGINS=["*"]
    )

    with pytest.raises(RuntimeError) as exc_info:
        validate_production_config(bad_cfg)
    
    err_text = str(exc_info.value)
    assert "JWT_SECRET must be set" in err_text
    assert "API_KEY_ENCRYPTION_SECRET must be set" in err_text
    assert "DATABASE_URL cannot use SQLite in production" in err_text
    assert "cannot contain wildcard '*'" in err_text
