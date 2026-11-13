# ExamPilot 2.0 — Tenant Isolation Test Report

**Company:** GT InnoX LLP  
**Product:** ExamPilot 2.0 — *Understand Questions. Learn the Answers.*  
**Branch:** `security/production-readiness-remediation`  
**Date:** November 14, 2026  

---

## 1. Executive Summary

This report validates multi-tenant data isolation across ExamPilot 2.0. Following the remediation of defect BLK-02, no user can access, mutate, generate practice questions from, or submit answers against another user's private data.

---

## 2. Multi-User Isolation Invariants Tested

### Invariant 1: Practice Test Question Selection
- **Prior Flaw (BLK-02):** If a user requested a practice test with more questions than existed in their history, the backend queried `db.query(Question).order_by(func.random()).limit(...)` without filtering by `user_id`.
- **Remediated Behavior:**
  - Queries strictly filter `Question.user_id == current_user.id`.
  - If 0 questions are available, an isolated, self-contained sample question is created and owned strictly by `current_user.id`.
  - No global fallback exists.
- **Verification Evidence (`test_practice_test_cross_tenant_isolation`):**
  User A inserted confidential question `CONFIDENTIAL: Proprietary Exam Question for User A Only`. User B requested a practice test. The test verified that `q_a_id` was absent from User B's practice test, and no text matching User A's confidential question was returned.

### Invariant 2: Practice Test Submission Ownership & Membership
- **Remediated Checks in `/api/practice/submit`:**
  1. `session.user_id == current_user.id`: User B cannot submit answers to User A's practice session (HTTP 404).
  2. `session.completed_at is None`: A practice session cannot be submitted repeatedly (HTTP 400).
  3. `item.question_id in session.question_ids_json`: Questions submitted must belong to the active practice session.
  4. `Question.user_id == current_user.id`: Questions submitted must be owned by the authenticated student (HTTP 403).
  5. `duplicate check`: Submitting multiple answers for the same question is rejected (HTTP 400).
- **Verification Evidence (`test_practice_test_duplicate_answers_and_resubmission_rejection`):**
  Tested duplicate answer submission (rejected with 400), valid submission (accepted with 200), and resubmission attempt (rejected with 400).

### Invariant 3: Provider API Keys & Conversations
- **Audited in `tests/test_security_audit.py` (`test_cross_account_isolation_and_penetration`):**
  - Alice saves private API key `sk-proj-aliceprivatekey...`. Bob lists `/api/providers`: Alice's key is not listed. Bob calls `DELETE /api/providers/{alice_key_id}`: rejected with HTTP 404.
  - Alice creates a study conversation. Bob attempts `GET /api/assistant/conversations/{alice_conv_id}`: rejected with HTTP 404. Bob attempts `POST /api/assistant/chat`: rejected with HTTP 404.

### Invariant 4: Study Documents & Knowledge Library
- **Audited in `backend/app/api/routes/documents.py`:**
  - `list_documents`: strictly filtered by `Document.user_id == current_user.id`.
  - `search_library`: `search_relevant_chunks` filters chunks joined with `Document.user_id == current_user.id`.
  - `delete_document`: strictly filtered by `Document.id == document_id, Document.user_id == current_user.id`.

---

## 3. Test Matrix Summary

| Test Identifier | Scope | Status | Notes |
|---|---|---|---|
| `test_practice_test_cross_tenant_isolation` | Practice test question generation | **PASSED** | 0 cross-tenant question exposure |
| `test_practice_test_duplicate_answers_and_resubmission_rejection` | Answer submission & integrity | **PASSED** | Membership & resubmission guards enforced |
| `test_cross_account_isolation_and_penetration` | Providers, assistant chat, history | **PASSED** | 100% tenant isolation across resources |
