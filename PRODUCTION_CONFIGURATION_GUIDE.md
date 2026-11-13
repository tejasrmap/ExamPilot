# ExamPilot 2.0 — Production Configuration & Secrets Guide

**Company:** GT InnoX LLP  
**Product:** ExamPilot 2.0 — *Understand Questions. Learn the Answers.*  
**Branch:** `security/production-readiness-remediation`  
**Date:** November 14, 2026  

---

## 1. Fail-Closed Production Configuration

ExamPilot 2.0 enforces fail-closed startup validation (`validate_production_config()` in `backend/app/core/config.py`). When `ENVIRONMENT=production`, the application refuses to start if insecure development defaults, SQLite, or wildcard CORS are detected.

---

## 2. Complete Environment Variable Reference

### Backend Secrets (`backend/.env` or Render/Railway Environment Variables)

| Variable Name | Required in Prod | Example / Recommended Value | Description |
|---|---|---|---|
| `ENVIRONMENT` | **Yes** | `production` | Enables production security guardrails |
| `PROJECT_NAME` | No | `"ExamPilot 2.0"` | API documentation branding |
| `API_V1_STR` | No | `/api` | Base path prefix |
| `DATABASE_URL` | **Yes** | `postgresql://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres?sslmode=require` | Supabase PostgreSQL direct connection string |
| `JWT_SECRET` | **Yes** | `[64-character random hex or base64]` | Secret used to sign user authentication JWTs |
| `JWT_ALGORITHM` | No | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `10080` (7 days) | Expiration window for user sessions |
| `RESET_TOKEN_EXPIRE_MINUTES` | No | `15` | Short-lived password reset token expiry |
| `API_KEY_ENCRYPTION_SECRET` | **Yes** | `[64-character random hex or 32+ byte string]` | Primary AES-256-GCM encryption key for user BYOK API keys |
| `API_KEY_ENCRYPTION_ROTATION_SECRETS`| No | `old_key_1,old_key_2` | Comma-separated list of secondary keys for zero-downtime key rotation |
| `FRONTEND_URL` | **Yes** | `https://exampilot.gtinnox.com` | Production web application URL used in reset emails |
| `BACKEND_CORS_ORIGINS` | **Yes** | `["https://exampilot.gtinnox.com","https://exampilot.vercel.app"]` | Allowed web origins. **Wildcard `*` is strictly forbidden.** |
| `CHROME_EXTENSION_IDS` | No | `["abcdefghijklmnopqrstuvwxyz123456"]` | Optional explicit Chrome Extension IDs |
| `EMAIL_PROVIDER` | **Yes** | `smtp` | Transactional email provider (`smtp`, `resend`, `console`) |
| `SMTP_HOST` | If smtp | `smtp.sendgrid.net` or `smtp.resend.com` | SMTP relay server hostname |
| `SMTP_PORT` | If smtp | `587` | SMTP relay port (typically 587 for STARTTLS) |
| `SMTP_USER` | If smtp | `apikey` | SMTP authentication username |
| `SMTP_PASSWORD` | If smtp | `[SMTP-PASSWORD-OR-API-KEY]` | SMTP authentication password/token |
| `SMTP_FROM` | If smtp | `noreply@exampilot.gtinnox.com` | Verified sender address |
| `SMTP_USE_TLS` | If smtp | `true` | Enforce TLS encryption |
| `STORAGE_PROVIDER` | **Yes** | `supabase` | Storage abstraction provider (`supabase` or `local`) |
| `SUPABASE_URL` | If supabase | `https://[PROJECT-REF].supabase.co` | Supabase API endpoint |
| `SUPABASE_ANON_KEY` | If supabase | `eyJhbGci...` | Supabase anon key |
| `SUPABASE_SERVICE_ROLE_KEY` | If supabase | `eyJhbGci...` | Supabase service role key (for private bucket management) |
| `SUPABASE_STORAGE_BUCKET` | If supabase | `exampilot-documents` | Name of private storage bucket |
| `RATE_LIMIT_OCR_PER_MINUTE` | No | `20` | Max OCR requests per user per minute |
| `RATE_LIMIT_AUTH_PER_MINUTE` | No | `10` | Max auth attempts per IP per minute |
| `MAX_UPLOAD_SIZE_MB` | No | `25` | Maximum file upload size in MB |

---

## 3. Zero-Downtime AES-256-GCM Key Rotation Procedure

To rotate the server-side API key encryption secret without breaking existing stored BYOK keys:

1. **Step 1:** Generate a new 64-character random key: `NEW_SECRET`.
2. **Step 2:** In your production hosting environment, configure:
   ```env
   API_KEY_ENCRYPTION_SECRET=NEW_SECRET
   API_KEY_ENCRYPTION_ROTATION_SECRETS=OLD_SECRET
   ```
3. **Step 3:** Deploy / restart. The backend will:
   - Encrypt all newly added or updated API keys using `NEW_SECRET`.
   - Decrypt existing keys using `NEW_SECRET` first, transparently falling back to `OLD_SECRET` if authentication tag verification indicates it was encrypted under the old key.
4. **Step 4:** Over time, as users save or update keys, or via a background re-encryption task, keys are migrated to `NEW_SECRET`. Once complete, remove `OLD_SECRET`.

---

## 4. Frontend Environment Variables (`frontend/.env.production`)

```env
NEXT_PUBLIC_API_URL=https://api.exampilot.gtinnox.com/api
NEXT_PUBLIC_SUPABASE_URL=https://[YOUR-PROJECT-REF].supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGci...
```
*(Never include backend service role keys or encryption secrets in the frontend bundle).*

