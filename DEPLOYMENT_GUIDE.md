# ExamPilot 2.0 — Production Deployment Guide
**Company:** GT InnoX LLP  
**Product:** ExamPilot 2.0  
**Target Environments:** Frontend on Vercel, Backend on Render/Railway/Persistent VM, Database on Supabase PostgreSQL.

---

## 1. Prerequisites & Services

1. **Supabase Account**:
   - Create a new project in Supabase.
   - Note the Project URL, Anon Key, and Postgres connection string.
2. **Persistent Python Hosting (Render / Railway / DigitalOcean / AWS)**:
   - Python 3.10+ runtime.
3. **Next.js Hosting (Vercel / Cloudflare Pages)**:
   - Node.js 18+ or 20+ runtime.

---

## 2. Environment Variables Configuration

### 2.1 Backend (`backend/.env` or Host Environment Secrets)
```env
# Runtime
ENVIRONMENT=production
PROJECT_NAME="ExamPilot 2.0"
API_V1_STR=/api

# Security Keys (Generate strong 32+ character secrets)
API_KEY_ENCRYPTION_SECRET=CHANGE_ME_TO_A_64_CHAR_HEX_OR_RANDOM_SECRET_KEY!
JWT_SECRET=CHANGE_ME_TO_A_STRONG_RANDOM_JWT_SIGNING_SECRET_KEY!
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# Supabase PostgreSQL Connection String
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres

# Supabase Auth
SUPABASE_URL=https://[YOUR-PROJECT-REF].supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Allowed Frontend Origins (CORS)
BACKEND_CORS_ORIGINS=["https://exampilot.gtinnox.com","https://exampilot.vercel.app"]
```

### 2.2 Frontend (`frontend/.env.production` or Vercel Environment Variables)
```env
NEXT_PUBLIC_API_URL=https://api.exampilot.gtinnox.com/api
NEXT_PUBLIC_SUPABASE_URL=https://[YOUR-PROJECT-REF].supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 3. Database Migration & RLS Execution

1. Log into your **Supabase Dashboard** &rarr; **SQL Editor**.
2. Run the RLS migration script located in the repository:
   ```sql
   -- File: backend/migrations/001_supabase_rls.sql
   ```
3. This will enable Row Level Security and establish user tenant isolation policies for all 12 tables.

---

## 4. Deploying the Backend (FastAPI)

### On Render or Railway:
1. **Build Command**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Start Command**:
   ```bash
   uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT --workers 4
   ```
3. Set health check path to `/` (returns HTTP 200).

---

## 5. Deploying the Frontend (Next.js)

### On Vercel:
1. Import repository and set root directory to `frontend`.
2. Framework preset: **Next.js**.
3. **Build Command**: `next build`.
4. Deploy!

---

## 6. Chrome Extension Distribution

1. Open `chrome-extension/manifest.json`.
2. In Google Chrome, navigate to `chrome://extensions`.
3. Enable **Developer mode** (toggle in upper right).
4. Click **Load unpacked** and select the `chrome-extension` folder.
5. In popup settings, configure your production API URL (`https://api.exampilot.gtinnox.com/api`).
