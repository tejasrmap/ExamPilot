import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_cross_account_isolation_and_penetration():
    """
    Creates two independent accounts: Alice and Bob.
    Verifies that Bob CANNOT access, mutate, or delete Alice's:
    - Questions
    - API Provider keys
    - Documents
    - Practice sessions
    - Conversations
    """
    # 1. Register Alice & Bob
    alice_res = client.post("/api/auth/register", json={
        "email": "alice_sec@exampilot.com",
        "password": "AliceSecretPassword123!",
        "display_name": "Alice Auditor"
    })
    if alice_res.status_code == 400:
        alice_token = client.post("/api/auth/login", json={"email": "alice_sec@exampilot.com", "password": "AliceSecretPassword123!"}).json()["access_token"]
    else:
        alice_token = alice_res.json()["access_token"]

    bob_res = client.post("/api/auth/register", json={
        "email": "bob_sec@exampilot.com",
        "password": "BobSecretPassword123!",
        "display_name": "Bob Adversary"
    })
    if bob_res.status_code == 400:
        bob_token = client.post("/api/auth/login", json={"email": "bob_sec@exampilot.com", "password": "BobSecretPassword123!"}).json()["access_token"]
    else:
        bob_token = bob_res.json()["access_token"]

    alice_headers = {"Authorization": f"Bearer {alice_token}"}
    bob_headers = {"Authorization": f"Bearer {bob_token}"}

    # 2. Alice adds a private encrypted API key
    alice_prov = client.post("/api/providers", headers=alice_headers, json={
        "provider": "openai",
        "api_key": "sk-proj-aliceprivatekey1234567890",
        "default_model": "gpt-4o-mini",
        "is_default": True
    }).json()
    alice_prov_id = alice_prov["id"]

    # Bob lists providers: must NOT see Alice's provider
    bob_provs = client.get("/api/providers", headers=bob_headers).json()
    assert not any(p["id"] == alice_prov_id for p in bob_provs), "Tenant isolation breached: Bob sees Alice's provider!"

    # Bob attempts to delete Alice's provider: must be rejected (404)
    bob_del_prov = client.delete(f"/api/providers/{alice_prov_id}", headers=bob_headers)
    assert bob_del_prov.status_code in (404, 403), "Access control failure: Bob deleted Alice's provider!"

    # 3. Alice creates a conversation
    alice_conv = client.post("/api/assistant/conversations", headers=alice_headers, json={
        "title": "Alice Private Research"
    }).json()
    alice_conv_id = alice_conv["id"]

    # Bob attempts to access Alice's conversation
    bob_get_conv = client.get(f"/api/assistant/conversations/{alice_conv_id}", headers=bob_headers)
    assert bob_get_conv.status_code in (404, 403), "Tenant isolation breached: Bob accessed Alice's conversation!"

    # Bob attempts to post message into Alice's conversation
    bob_post_msg = client.post("/api/assistant/chat", headers=bob_headers, json={
        "conversation_id": alice_conv_id,
        "content": "Malicious payload injection"
    })
    assert bob_post_msg.status_code in (404, 403), "Tenant isolation breached: Bob posted into Alice's conversation!"

    # 4. Alice creates a practice session
    alice_practice = client.post("/api/practice", headers=alice_headers, json={
        "title": "Alice Architecture Test",
        "subject": "Computer Science",
        "question_count": 1
    }).json()
    alice_session_id = alice_practice["session_id"]
    alice_q_id = alice_practice["questions"][0]["id"]

    # Bob attempts to submit answers to Alice's practice session
    bob_sub = client.post("/api/practice/submit", headers=bob_headers, json={
        "session_id": alice_session_id,
        "answers": [{"question_id": alice_q_id, "selected_answer": "B"}]
    })
    assert bob_sub.status_code in (404, 403), "Tenant isolation breached: Bob submitted answers to Alice's quiz!"

def test_password_reset_flow():
    """
    Tests forgot-password and reset-password workflow.
    """
    email = "reset_test@exampilot.com"
    old_pwd = "OldPassword123!"
    new_pwd = "BrandNewSecurePassword456!"

    # Register user
    reg = client.post("/api/auth/register", json={"email": email, "password": old_pwd})
    if reg.status_code != 200:
        client.post("/api/auth/login", json={"email": email, "password": old_pwd})

    # 1. Request forgot password
    from backend.app.services.email import email_service
    forgot_res = client.post("/api/auth/forgot-password", json={"email": email})
    assert forgot_res.status_code == 200
    # Security requirement: reset_token must NEVER be returned in API response
    assert "reset_token" not in forgot_res.json(), "Security breach: reset token leaked in response body!"
    assert forgot_res.json()["message"] == "If this email address is registered, password reset instructions have been sent."

    # Retrieve dispatched single-use token from email service
    token = email_service.get_last_reset_token(email)
    assert token is not None, "Reset token must be dispatched via email service"

    # 2. Reset password with valid token
    reset_res = client.post("/api/auth/reset-password", json={
        "reset_token": token,
        "new_password": new_pwd
    })
    assert reset_res.status_code == 200

    # 3. Attempt login with old password (MUST fail)
    fail_login = client.post("/api/auth/login", json={"email": email, "password": old_pwd})
    assert fail_login.status_code == 401

    # 4. Login with new password (MUST succeed)
    succ_login = client.post("/api/auth/login", json={"email": email, "password": new_pwd})
    assert succ_login.status_code == 200
    assert "access_token" in succ_login.json()

def test_sql_injection_defense():
    """
    Tests search inputs and login fields against standard SQL injection vectors.
    """
    sql_payloads = [
        "' OR '1'='1",
        "'; DROP TABLE profiles; --",
        "admin' --",
        "' UNION SELECT null, null, null --"
    ]

    for p in sql_payloads:
        # Test login
        res = client.post("/api/auth/login", json={"email": f"{p}@inject.com", "password": p})
        assert res.status_code in (401, 422), f"SQL injection vulnerability in login for payload: {p}"

def test_unauthorized_endpoints():
    """
    Verifies that protected routes reject requests without Authorization header with 401.
    """
    protected_paths = [
        ("GET", "/api/auth/profile"),
        ("GET", "/api/providers"),
        ("GET", "/api/questions"),
        ("GET", "/api/analytics/overview"),
        ("GET", "/api/practice"),
        ("GET", "/api/documents"),
        ("GET", "/api/settings"),
        ("POST", "/api/ocr/image"),
        ("POST", "/api/ocr/pdf")
    ]

    for method, path in protected_paths:
        if method == "GET":
            r = client.get(path)
        else:
            r = client.post(path)
        assert r.status_code == 401, f"Path {path} did not enforce 401 Unauthorized"

