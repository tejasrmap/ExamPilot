# ExamPilot 2.0 — Remediation Changelog

**Company:** GT InnoX LLP  
**Product:** ExamPilot 2.0 — *Understand Questions. Learn the Answers.*  
**Branch:** `security/production-readiness-remediation`  
**Base Commit:** `8b5a280d6ef2bb56c8ea6e199cf1a84840ed71cd`  
**Date:** November 14, 2026  

---

## Changes Implemented

### 1. Authentication & Password Reset Security
- `backend/app/core/security.py`:
  - Added `validate_password_strength()` enforcing 8+ characters, letters, and numbers/specials.
  - Added `generate_secure_reset_token()` generating 256-bit entropy tokens and SHA-256 hashes.
  - Added key rotation support in `decrypt_api_key()` using secondary rotation secrets.
- `backend/app/core/deps.py`:
  - Added session revocation verification checking `payload.get("tv") == user.token_version`.
- `backend/app/services/email.py`:
  - Added `BaseEmailService`, `ConsoleEmailService` (for dev and tests), and `SMTPEmailService` (for production).
- `backend/app/api/routes/auth.py`:
  - Removed `reset_token` from response body of `/api/auth/forgot-password`.
  - Added uniform response for registered and unregistered email addresses to prevent user enumeration.
  - Added rate limiting on forgot-password and login endpoints.
  - Implemented atomic token consumption via `with_for_update()`.
  - Implemented session invalidation (`token_version += 1`) on password reset and logout.

### 2. Practice Test Tenant Isolation
- `backend/app/api/routes/practice.py`:
  - Removed global question fallback `db.query(Question).order_by(func.random()).limit(...)`.
  - Enforced strict query filtering `Question.user_id == current_user.id`.
  - Added safe user-isolated sample question generation when user has 0 questions.
  - Stored authorized question IDs in `practice_sessions.question_ids_json`.
  - Enforced question membership and ownership checks in `/api/practice/submit`.
  - Blocked duplicate answer submissions for the same question.
  - Blocked resubmission of completed practice sessions.
  - Anchored score percentage to session total questions.

### 3. Database Models & Alembic Migrations
- `backend/app/db/models.py`:
  - Added `token_version` on `Profile`.
  - Added `PasswordResetToken` model.
  - Added `question_ids_json` on `PracticeSession`.
  - Added `storage_provider` and `storage_key` on `Document`.
- `backend/alembic/versions/0002_security_hardening.py`:
  - Created versioned, safe migration applying all model updates.
- `backend/app/db/init_db.py`:
  - Disabled automatic runtime DDL execution when `ENVIRONMENT=production`.
  - Updated `backend/migrations/001_supabase_rls.sql` with `password_reset_tokens` table RLS policies.

### 4. CORS Hardening & Main Application Guardrails
- `backend/app/core/config.py`:
  - Upgraded to Pydantic `SettingsConfigDict`.
  - Removed wildcard `*` from default CORS origins.
  - Added `validate_production_config()` failing closed if dev defaults are used in production.
  - Added `CHROME_EXTENSION_REGEX = r"^chrome-extension://[a-z]{32}$"`.
- `backend/app/main.py`:
  - Integrated `validate_production_config(settings)` on startup.
  - Hardened `CORSMiddleware` with explicit methods, headers, and regex for Chrome extensions.

### 5. OCR Endpoint Protection & Bounded Uploads
- `backend/app/core/rate_limit.py`:
  - Implemented thread-safe sliding window rate limiter.
- `backend/app/api/routes/ocr.py`:
  - Added mandatory `current_user` authentication to `/api/ocr/image` and `/api/ocr/pdf`.
  - Added 20 req/min rate limiting per user.
  - Added file magic byte validation for PNG, JPEG, WebP, and PDF.
  - Bounded upload streaming to `MAX_UPLOAD_SIZE_MB = 25`.
  - Bounded PDF pages to max 20 pages.
- `backend/app/api/routes/documents.py`:
  - Implemented streaming chunk reading with immediate HTTP 413 abort on oversized files.
  - Added partial upload cleanup on error.

### 6. Durable Storage Abstraction
- `backend/app/services/storage.py`:
  - Created `BaseStorageService`, `LocalStorageService`, and `SupabaseStorageService`.
  - Integrated with `/api/documents/upload` and `/api/documents/{id}` deletion.

### 7. Test Suite Expansion
- `tests/test_production_security_remediation.py`:
  - Created 12 comprehensive security tests covering all remediated vulnerabilities.
- `tests/test_security_audit.py` & `tests/test_backend_ocr_parser.py`:
  - Updated to pass authentication and verify new secure token lifecycle.
- Full suite: **103 passed in 30.18s**.
