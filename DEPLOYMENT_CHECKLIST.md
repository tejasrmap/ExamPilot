# ExamPilot 2.0 — Production Deployment Checklist

**Company:** GT InnoX LLP  
**Product:** ExamPilot 2.0 — *Understand Questions. Learn the Answers.*  
**Target Environments:**
- **Frontend:** Vercel (Next.js 14 App Router)
- **Backend:** Render / Railway / Persistent Linux Host (FastAPI + Uvicorn)
- **Database:** Supabase Managed PostgreSQL
- **Companion:** Google Chrome Web Store (Manifest V3 Extension)

---

## 1. Pre-Deployment Configuration & Secrets Checklist

### 1.1 Backend Environment Variables (`backend/.env` or Host Secrets)
- [ ] `ENVIRONMENT=production`
- [ ] `PROJECT_NAME="ExamPilot 2.0"`
- [ ] `API_V1_STR=/api`
- [ ] `API_KEY_ENCRYPTION_SECRET`: Set to a cryptographically random 64-character hex string (minimum 32 bytes). **Never use development fallback.**
- [ ] `JWT_SECRET`: Set to a cryptographically random 64-character string.
- [ ] `JWT_ALGORITHM=HS256`
- [ ] `ACCESS_TOKEN_EXPIRE_MINUTES=10080` (or 1440 for 24-hour expiration)
- [ ] `DATABASE_URL`: Set to production Supabase PostgreSQL connection string (`postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres?sslmode=require`).
- [ ] `SUPABASE_URL`: Production Supabase project URL (`https://[PROJECT-REF].supabase.co`).
- [ ] `SUPABASE_ANON_KEY`: Production Supabase anon key.
- [ ] `BACKEND_CORS_ORIGINS`: JSON array of explicit domains (`["https://exampilot.gtinnox.com","https://exampilot.vercel.app"]`). **Remove wildcard `*`**.
- [ ] `EMAIL_PROVIDER_API_KEY`: API key for transactional password reset emails (Resend / SendGrid / Supabase).

### 1.2 Frontend Environment Variables (`frontend/.env.production` or Vercel Settings)
- [ ] `NEXT_PUBLIC_API_URL`: Public HTTPS backend API endpoint (`https://api.exampilot.gtinnox.com/api`).
- [ ] `NEXT_PUBLIC_SUPABASE_URL`: Public Supabase URL.
- [ ] `NEXT_PUBLIC_SUPABASE_ANON_KEY`: Public Supabase anon key.

---

## 2. Database Migration & RLS Execution Procedure

### 2.1 Supabase Schema Initialization
- [ ] Connect to Supabase SQL Editor as administrator.
- [ ] Execute Alembic migrations from clean state:
  ```bash
  python -m alembic upgrade head
  ```
- [ ] Verify that all 12 tables exist:
  `profiles`, `api_providers`, `subjects`, `questions`, `practice_sessions`, `practice_answers`, `documents`, `document_chunks`, `conversations`, `messages`, `usage_logs`, `user_settings`.
- [ ] Verify that column `structured_options_json` exists on table `questions`.
- [ ] Execute Supabase Row Level Security migration:
  ```sql
  -- File: backend/migrations/001_supabase_rls.sql
  ```
- [ ] Confirm RLS is enabled on all tables:
  ```sql
  SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname = 'public';
  ```

### 2.2 Database Backup & Retention
- [ ] Enable Supabase Point-in-Time Recovery (PITR) or daily automated backups.
- [ ] Establish automated backup retention schedule (minimum 14-day rolling retention).

---

## 3. Backend Deployment Execution (FastAPI / Render / Railway)

### 3.1 Build & Start Settings
- [ ] **Runtime:** Python 3.10 or 3.11
- [ ] **System Packages:** Install `libgl1`, `libglib2.0-0` for OpenCV and PaddleOCR dependencies.
- [ ] **Build Command:**
  ```bash
  pip install --upgrade pip
  pip install -r requirements.txt
  pip install -r backend/requirements.txt
  ```
- [ ] **Release Command (Pre-deploy migration):**
  ```bash
  python -m alembic upgrade head
  ```
- [ ] **Start Command:**
  ```bash
  uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT --workers 4 --proxy-headers --forwarded-allow-ips='*'
  ```
- [ ] **Health Check URL:** `/` (returns HTTP 200 with `status: online`).
- [ ] **Resource Sizing:** Minimum 1GB RAM and 1 CPU core allocated for ONNX OCR model caching.

---

## 4. Frontend Deployment Execution (Next.js / Vercel)

### 4.1 Build & Routing Settings
- [ ] **Root Directory:** `frontend`
- [ ] **Framework Preset:** Next.js
- [ ] **Node.js Version:** 20 LTS
- [ ] **Install Command:** `npm ci`
- [ ] **Build Command:** `next build`
- [ ] **Output Verification:** Ensure all 13 routes are generated without dynamic bailout warnings.
- [ ] **Custom Domain:** Configure `exampilot.gtinnox.com` with SSL certificate.

---

## 5. Chrome Extension Deployment (Web Store)

- [ ] Confirm `manifest_version: 3` in `chrome-extension/manifest.json`.
- [ ] Confirm no private signing keys or developer files are bundled.
- [ ] Confirm `nativeMessaging` permission is absent.
- [ ] Set default `backendUrl` in `background.js` and `popup.js` to `https://api.exampilot.gtinnox.com/api`.
- [ ] Run `python scripts/package_extension.py` to create clean distribution zip.
- [ ] Upload distribution zip to Chrome Web Store Developer Dashboard.

---

## 6. Post-Deployment Smoke Test & Verification

- [ ] Execute `GET /` &rarr; verify `HTTP 200` with `status: "online"`.
- [ ] Register new user (`POST /api/auth/register`) &rarr; verify JWT token returned.
- [ ] Login (`POST /api/auth/login`) &rarr; verify authentication.
- [ ] Add BYOK Provider (`POST /api/providers`) &rarr; verify AES-256-GCM encryption and masked key returned.
- [ ] Upload test MCQ image (`POST /api/ocr/image`) &rarr; verify OCR confidence and option extraction.
- [ ] Run AI Analysis (`POST /api/questions/analyse`) &rarr; verify explanation, evidence, and structured options.
- [ ] Check Question History (`GET /api/questions`) &rarr; verify structured options and labels are preserved.
- [ ] Create Practice Test (`POST /api/practice`) &rarr; verify tenant isolation (only user's questions).
- [ ] Test Chrome Extension capture against deployed API.

---

## 7. Rollback Strategy

1. **Frontend Rollback:** In Vercel Dashboard, select previous successful deployment &rarr; click **Instant Rollback**.
2. **Backend Rollback:** In Render/Railway Dashboard, trigger rollback to previous container image commit.
3. **Database Schema Rollback:**
   ```bash
   python -m alembic downgrade -1
   ```
   (Verify no destructive data loss before executing downgrade).

