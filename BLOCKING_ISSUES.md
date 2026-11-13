# ExamPilot 2.0 — Blocking Issues & Pre-Production Defect Register

**Company:** GT InnoX LLP  
**Product:** ExamPilot 2.0 — *Understand Questions. Learn the Answers.*  
**Baseline Commit:** `8b5a280d6ef2bb56c8ea6e199cf1a84840ed71cd`  
**Audit Date:** November 14, 2026  
**Auditor:** Principal Software Architect, DevSecOps Engineer & SaaS Reliability Lead  

---

## Executive Summary

This register catalogs all architectural defects, security vulnerabilities, and deployment blockers identified during the independent production-readiness audit. Issues are categorized by severity with explicit evidence, business impact, remediation steps, and verification procedures.

---

## 1. Critical Severity Blockers

### BLK-01: Password Reset Token Leaked in API Response (Account Takeover)
- **Severity:** Critical
- **Affected Component:** `backend/app/api/routes/auth.py` (lines 98–116)
- **Evidence:**
  ```python
  @router.post("/forgot-password")
  def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
      user = db.query(Profile).filter(Profile.email == req.email.lower().strip()).first()
      ...
      reset_token = create_access_token(
          data={"sub": user.id, "email": user.email, "purpose": "password_reset"},
          expires_delta=timedelta(minutes=15)
      )
      return {
          "message": "Password reset token generated successfully.",
          "reset_token": reset_token  # <-- EXPOSED DIRECTLY TO CLIENT
      }
  ```
- **Business Impact:** Any anonymous user can submit another user's email address to `/api/auth/forgot-password`, receive the active reset token in the response payload, and immediately call `/api/auth/reset-password` to change the password. This allows instant account takeover of any registered student or administrator without requiring access to their email inbox.
- **Recommended Remediation:**
  1. Remove `reset_token` from the response payload immediately. The endpoint must return only a generic message: `{"message": "If the account exists, a password reset link has been dispatched to your email."}`.
  2. Implement an asynchronous email dispatch worker (e.g. using SendGrid, Resend, AWS SES, or Supabase Auth email templates) to send the reset link securely to the verified email address.
  3. Store reset token hashes or use Supabase Auth native password recovery.
- **Verification Method:** Send `POST /api/auth/forgot-password` with a valid user email. Assert that the response HTTP status is 200 and the JSON response contains no `reset_token` or credentials.

---

## 2. High Severity Remediation Items

### BLK-02: Cross-Tenant Question Leakage in Practice Test Creation
- **Severity:** High
- **Affected Component:** `backend/app/api/routes/practice.py` (lines 64–68)
- **Evidence:**
  ```python
  # If user doesn't have enough saved questions, pull any questions in the system or generate default
  if not questions:
      # Fallback to any questions or sample
      questions = db.query(Question).order_by(func.random()).limit(req.question_count).all()
  ```
- **Business Impact:** When a newly registered student with no saved questions creates a practice test, the query queries `Question` without filtering by `Question.user_id == current_user.id`. The user is served proprietary or private quiz questions scanned by other students, violating FERPA/GDPR tenant isolation and compromising confidential exam materials.
- **Recommended Remediation:**
  Remove the global un-isolated fallback. When a user has fewer than `req.question_count` questions, either seed questions strictly for that user's account or return pre-approved public curriculum practice questions stored in a dedicated `curriculum_questions` catalog table.
- **Verification Method:** Create User A and User B. Insert questions under User A. Log in as User B (0 questions) and call `POST /api/practice`. Assert that no questions belonging to User A are returned.

---

### BLK-03: Supabase RLS vs. Application JWT Authentication Mismatch
- **Severity:** High
- **Affected Component:** `backend/app/db/init_db.py`, `backend/migrations/001_supabase_rls.sql`, `backend/app/db/session.py`
- **Evidence:**
  The generated RLS policy enforces:
  ```sql
  CREATE POLICY "Users access own questions" ON questions
      FOR ALL USING (auth.uid()::text = user_id);
  ```
  However, the FastAPI backend uses its own internal JWT generation (`create_access_token`) signed with `settings.JWT_SECRET`, and connects to PostgreSQL using a direct SQLAlchemy connection pool (`DATABASE_URL`).
- **Business Impact:**
  - If FastAPI connects to Supabase as a non-superuser with RLS enforced, `auth.uid()` evaluates to `NULL` (because PostgreSQL session variables like `request.jwt.claim.sub` are not set by direct DB drivers). All database queries fail with permission denied or return 0 rows.
  - If FastAPI connects as the `postgres` superuser, PostgreSQL bypasses RLS completely, leaving tenant isolation entirely dependent on application code filters.
- **Recommended Remediation:**
  1. Clearly document and configure the backend connection user role.
  2. If using Supabase RLS with FastAPI, add a database session hook (`connection.execute(text("SET LOCAL request.jwt.claim.sub = :user_id"), {"user_id": user.id})`) on each request, OR integrate Supabase Auth directly so JWTs are verified by Supabase public keys and PostgREST claims.
- **Verification Method:** Execute the migration on a live Supabase PostgreSQL instance and execute CRUD operations through FastAPI; assert that records are created and retrieved without permission denial.

---

### BLK-04: Invalid CORS Origin Wildcard with Credential Support
- **Severity:** High
- **Affected Component:** `backend/app/core/config.py` (lines 34–41), `backend/app/main.py` (lines 20–26)
- **Evidence:**
  ```python
  # backend/app/core/config.py
  BACKEND_CORS_ORIGINS: list = [
      "http://localhost:3000",
      "http://127.0.0.1:3000",
      "http://localhost:8000",
      "http://127.0.0.1:8000",
      "chrome-extension://*",
      "*"
  ]

  # backend/app/main.py
  app.add_middleware(
      CORSMiddleware,
      allow_origins=settings.BACKEND_CORS_ORIGINS,
      allow_credentials=True,
      ...
  )
  ```
- **Business Impact:** Under the W3C CORS specification and modern browser implementations, `allow_credentials=True` cannot be paired with a wildcard `"*"` origin. Browsers reject responses to authenticated cross-origin requests. Additionally, `"chrome-extension://*"` wildcard patterns are ignored by Starlette unless `allow_origin_regex` is used, blocking extension requests in production browsers.
- **Recommended Remediation:**
  1. Remove `"*"` from `BACKEND_CORS_ORIGINS` when in production.
  2. Replace `"chrome-extension://*"` in `allow_origins` with `allow_origin_regex=r"^chrome-extension://[a-z]{32}$"` in `CORSMiddleware`.
  3. Populate `BACKEND_CORS_ORIGINS` strictly from environment variables matching deployed Vercel domains.
- **Verification Method:** Send an `OPTIONS` preflight request with `Origin: chrome-extension://<id>` and `Access-Control-Request-Headers: Authorization`; verify valid `Access-Control-Allow-Origin` and `Access-Control-Allow-Credentials: true` response.

---

## 3. Medium Severity Remediation Items

### BLK-05: Unauthenticated, Un-Rate-Limited OCR Endpoints (DoS Vulnerability)
- **Severity:** Medium
- **Affected Component:** `backend/app/api/routes/ocr.py` (lines 24–114)
- **Evidence:**
  `scan_image` and `scan_pdf` do not depend on `get_current_user` or any authentication dependency. There is no rate limiter middleware (such as `slowapi` or Redis token-bucket).
- **Business Impact:** RapidOCR runs deep-learning ONNX models on CPU, taking ~2.7 seconds per image. PyMuPDF renders multi-page PDFs synchronously. An anonymous attacker can issue hundreds of concurrent image/PDF OCR requests, exhausting server CPU/RAM and causing complete service denial for authenticated users.
- **Recommended Remediation:**
  1. Add `current_user: Profile = Depends(get_current_user)` to both `/api/ocr/image` and `/api/ocr/pdf`.
  2. Implement IP-based and user-based rate limiting (e.g., 20 OCR scans per minute per account).
- **Verification Method:** Send unauthenticated requests to `/api/ocr/image`; assert HTTP 401 response. Send 30 rapid requests; assert HTTP 429 response.

---

### BLK-06: Unbounded File Uploads into Server Memory
- **Severity:** Medium
- **Affected Component:** `backend/app/api/routes/ocr.py` (line 35, line 87), `backend/app/api/routes/documents.py` (line 54)
- **Evidence:**
  ```python
  content_bytes = await file.read()
  ```
  `await file.read()` buffers the entire incoming payload into Python process memory before checking file size or format headers. While `MAX_UPLOAD_SIZE_MB = 25` is in config, no guard enforces it before reading.
- **Business Impact:** Uploading multiple large files (e.g. 500MB+) can exhaust server RAM and trigger OOM killer termination on containers with 512MB–1GB limits.
- **Recommended Remediation:**
  Read file streams in chunks (e.g. 1MB) and abort with HTTP 413 Payload Too Large if the total byte count exceeds `MAX_UPLOAD_SIZE_MB * 1024 * 1024`. Validate MIME types using magic byte inspection (e.g. `%PDF-` for PDFs, `\x89PNG` for PNGs).
- **Verification Method:** Attempt to upload a 30MB payload; assert immediate HTTP 413 response without buffering entire payload.

---

### BLK-07: Ephemeral Local Disk Storage for Uploaded Documents
- **Severity:** Medium
- **Affected Component:** `backend/app/api/routes/documents.py` (lines 16–17, 58–64)
- **Evidence:**
  ```python
  UPLOAD_STORAGE_DIR = "backend/storage/documents"
  ...
  save_path = os.path.join(UPLOAD_STORAGE_DIR, save_filename)
  with open(save_path, "wb") as f:
      f.write(content_bytes)
  ```
- **Business Impact:** When deployed on containerized platforms (Render, Railway, Fly, Heroku, AWS ECS), the local container filesystem is ephemeral. All uploaded study documents will vanish upon container restart or redeployment, and documents uploaded to one replica will not be accessible to another.
- **Recommended Remediation:**
  Store uploaded document assets in Supabase Storage or an S3-compatible object bucket with signed download URLs.
- **Verification Method:** Restart backend container; verify that previously uploaded document records can still retrieve their source files.

---

## 4. Low Severity Architecture Recommendations

### BLK-08: Startup Table Mutation Outside Alembic
- **Severity:** Low
- **Affected Component:** `backend/app/main.py` (line 8), `backend/app/db/init_db.py` (lines 88–105)
- **Evidence:**
  `backend/app/main.py` invokes `init_db()` at top-level import, executing `Base.metadata.create_all()` and runtime `ALTER TABLE` commands. In multi-worker environments (e.g., `uvicorn --workers 4`), all 4 workers race to inspect and alter the database schema on startup.
- **Business Impact:** Potential race condition locks during concurrent container startup; schema drift between Alembic version tracking and runtime mutations.
- **Recommended Remediation:**
  Remove `init_db()` from `main.py` top-level. Execute migrations exclusively during deployment via `alembic upgrade head` in the deployment build/release phase.
- **Verification Method:** Start Uvicorn with `--workers 4`; verify no database lock contention or startup exceptions.

---

## 5. Summary Defect Tally

| Severity | Count | Classification |
|---|---|---|
| **Critical** | 1 | Production Blocker (Must fix before public launch) |
| **High** | 3 | High-Priority Remediation (Fix before production traffic) |
| **Medium** | 3 | High-Priority Remediation (Stabilize hosting and resilience) |
| **Low** | 1 | Recommended Improvement |
| **Total Findings** | **8** | |

