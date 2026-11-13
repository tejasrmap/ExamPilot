# ExamPilot 2.0 — Comprehensive Security Review

**Company:** GT InnoX LLP  
**Product:** ExamPilot 2.0 — *Understand Questions. Learn the Answers.*  
**Baseline Commit:** `8b5a280d6ef2bb56c8ea6e199cf1a84840ed71cd`  
**Date:** November 14, 2026  
**Auditor:** Principal DevSecOps & Security Architect  

---

## 1. Executive Security Assessment

A comprehensive security audit of ExamPilot 2.0 was conducted across authentication mechanisms, credential storage, authorization boundaries, API surface, database isolation, input processing, and third-party integrations.

### Overall Security Posture: **Action Required Before Public Release**

While core features implement strong encryption (AES-256-GCM for BYOK credentials) and parameterized SQL queries via SQLAlchemy ORM, one critical vulnerability (password reset token leakage in HTTP responses) and one tenant isolation flaw (cross-user fallback in practice tests) must be remediated prior to public release.

---

## 2. Authentication & Authorization Review

### 2.1 Password Security & Hashing
- **Implementation:** `backend/app/core/security.py` uses `passlib.context.CryptContext` with `pbkdf2_sha256`.
- **Finding:** Verified secure. Salt generation is handled per user, resistant to rainbow table lookups. Password complexity requirement (minimum 6 characters) is enforced during registration and reset.
- **Recommendation:** Upgrade minimum password length to 8 characters and enforce mixed character sets.

### 2.2 JWT Tokens & Session Invalidation
- **Implementation:** Stateless JWT tokens signed with `settings.JWT_SECRET` via `jose.jwt`. Default expiry is 7 days (`ACCESS_TOKEN_EXPIRE_MINUTES = 10080`).
- **Finding:** Expiration (`exp`) and subject (`sub`) claims are present and checked on each request by `get_current_user` in `backend/app/core/deps.py`.
- **Finding:** `/api/auth/logout` is purely client-side; no server-side token revocation or blocklist (e.g. Redis JTI revocation) exists. A compromised token remains valid until expiration.
- **Recommendation:** Implement Redis token blocklisting or reduce access token lifespan to 15–30 minutes with rotating refresh tokens.

### 2.3 Password Reset Workflow (Vulnerability BLK-01)
- **Status:** **CRITICAL VULNERABILITY**
- **Location:** `backend/app/api/routes/auth.py` (lines 98–116)
- **Detail:** When `/api/auth/forgot-password` is invoked, the server returns the signed JWT `reset_token` in the HTTP response JSON.
- **Remediation:** Remove `reset_token` from the response. Integrate transactional email dispatch via Resend, SendGrid, or Supabase Auth.

---

## 3. Data Protection & Encryption at Rest

### 3.1 BYOK API Key Encryption
- **Implementation:**
  - Algorithm: **AES-256-GCM** via `cryptography.hazmat.primitives.ciphers.aead.AESGCM`.
  - Nonce: Cryptographically secure 12-byte random nonce (`os.urandom(12)`) per encryption.
  - Payload: URL-safe base64 string combining `nonce (12 bytes) + ciphertext + auth_tag (16 bytes)`.
  - Key Derivation: 32-byte key derived from `settings.API_KEY_ENCRYPTION_SECRET` using SHA-256.
- **Finding:** Key encryption is robust. Authenticated encryption (GCM) guarantees ciphertext integrity and prevents tampering.
- **Finding:** Keys are never returned in plaintext to the frontend; only `masked_key` (e.g. `sk-pr...1234`) is transmitted.

### 3.2 Secret Exposure in Frontend Bundles
- **Verification:** Audited `frontend/` source code and production build output.
- **Finding:** No private API keys, backend database connection strings, or signing secrets exist in the Next.js frontend code or `.env.local` files. Only public variables (`NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`) are referenced.
- **Status:** **PASSED**

---

## 4. Tenant Isolation & Database Security

### 4.1 SQL Injection Protection
- **Implementation:** All database queries utilize SQLAlchemy 2.0 ORM expressions (`db.query(Model).filter(...)`).
- **Finding:** No string-concatenated SQL queries exist in user-facing routes. Parameter binding is handled by SQLAlchemy.
- **Status:** **PASSED**

### 4.2 User-to-User Data Isolation
- **Audited Routes:**
  - `analytics.py`: Strictly isolated by `user_id == current_user.id`.
  - `assistant.py`: Strictly isolated by `user_id == current_user.id`.
  - `documents.py`: Strictly isolated by `user_id == current_user.id`.
  - `providers.py`: Strictly isolated by `user_id == current_user.id`.
  - `questions.py`: Strictly isolated by `user_id == current_user.id`.
  - `settings.py`: Strictly isolated by `user_id == current_user.id`.
  - `practice.py`: **FAILED** on line 67 (BLK-02: global fallback exposes other users' questions to zero-question accounts).
- **Remediation:** Remove global un-isolated fallback in `practice.py`.

### 4.3 Supabase Row Level Security (RLS)
- **Implementation:** `backend/migrations/001_supabase_rls.sql` defines strict RLS policies on all 12 tables using `auth.uid()::text = user_id`.
- **Finding (BLK-03):** FastAPI connections via SQLAlchemy pool do not set `request.jwt.claim.sub`. If connected with a non-superuser role, RLS will block all backend queries.
- **Remediation:** Align connection permissions and session claims between FastAPI and Supabase.

---

## 5. Network & API Security

### 5.1 CORS Configuration (BLK-04)
- **Status:** **HIGH VULNERABILITY**
- **Evidence:** `settings.BACKEND_CORS_ORIGINS` includes `"*"`, while `CORSMiddleware` enables `allow_credentials=True`.
- **Standard:** W3C Fetch spec prohibits `Access-Control-Allow-Origin: *` when credentials are included. Browsers will refuse cross-origin credentialed requests.
- **Remediation:** Remove `"*"` in production; use specific domains from environment variables and regex for extension origins.

### 5.2 Input Validation & File Uploads (BLK-05 & BLK-06)
- **Finding:**
  - Pydantic models validate request payloads across all API routes.
  - Image and PDF file uploads (`/api/ocr/image`, `/api/ocr/pdf`, `/api/documents/upload`) lack pre-read byte size limit checks.
  - OCR endpoints are unauthenticated and lack rate limiting.
- **Remediation:** Enforce authentication on OCR routes, add request rate limiting, and validate file magic bytes before processing.

---

## 6. Security Risk Summary Matrix

| Vulnerability ID | Vulnerability Description | Severity | CVSS v3.1 | Status |
|---|---|---|---|---|
| SEC-01 | Password Reset Token Exfiltration via Response Body | **Critical** | 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H) | Open (BLK-01) |
| SEC-02 | Cross-Tenant Exam Question Leakage | **High** | 7.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N) | Open (BLK-02) |
| SEC-03 | Permissive CORS with Credential Flag Mismatch | **High** | 7.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:N) | Open (BLK-04) |
| SEC-04 | Unauthenticated OCR CPU Resource Exhaustion | **Medium** | 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L) | Open (BLK-05) |
| SEC-05 | Unbounded File Upload Buffer Allocation | **Medium** | 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L) | Open (BLK-06) |
| SEC-06 | Absence of Server-Side Token Invalidation | **Low** | 3.1 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:N/A:N) | Open |

