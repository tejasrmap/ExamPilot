# ExamPilot 2.0 — AI-Powered Online Learning & MCQ Practice Platform
<p align="center">
  <img src="assets/icons/icon_128x128.png" width="96" height="96" alt="ExamPilot 2.0 Logo">
  <br>
  <strong>Understand Questions. Learn the Answers.</strong>
  <br>
  <em>Developed by GT InnoX LLP</em>
</p>

---

## Overview

**ExamPilot 2.0** is a full-featured, production-oriented online SaaS platform for multiple-choice question (MCQ) mastery and intelligent academic revision. 

Rather than functioning as a simplistic answer lookup tool, ExamPilot is a pedagogical learning partner: students capture, upload, extract, and dissect practice questions using high-accuracy OCR and curriculum-grounded AI providers. The platform delivers step-by-step reasoning, comprehensive option-by-option breakdowns, ambiguity detection, practice test sessions, and intelligent RAG-assisted knowledge library search.

---

## Platform Architecture

```
ExamPilot 2.0/
├── frontend/             # Next.js 14 App Router (Tailwind CSS, TypeScript)
│   ├── app/              # Web pages: Scanner, History, Practice, Library, PDF, Assistant, Analytics, Settings
│   ├── components/       # Shared UI components (Navbar, Sidebar)
│   ├── lib/              # API client, Option Identity engine, utilities
│   └── tests/            # Native Node.js unit tests (node --test)
├── backend/              # FastAPI Async REST Backend & Microservices
│   ├── alembic/          # Versioned, repeatable database migrations
│   ├── app/              # API routes, auth, core security, DB models, AI providers, OCR, RAG
│   │   ├── api/routes/   # Auth, Questions, Practice, OCR, Documents, Providers, Assistant, Analytics, Settings
│   │   ├── core/         # Config, dependencies, rate limiting, AES-256-GCM encryption, JWT
│   │   ├── db/           # SQLAlchemy models, session pooling, initialization
│   │   ├── providers/    # BYOK AI Engine: OpenAI, Gemini, Anthropic, OpenRouter with retry & cost tracking
│   │   └── services/     # RapidOCR engine, QuestionParser, domain detector, RAG, storage, email
│   └── migrations/       # Supabase RLS and raw SQL migrations
├── chrome-extension/     # Google Chrome Manifest V3 Companion Extension (REST API)
├── tests/                # Automated pytest regression & security suites (103 tests)
└── docs/                 # Production deployment, architecture, and security reports
```

---

## Key SaaS Capabilities

1. **Modern Responsive Web Application (Next.js 14)**:
   - Complete learning dashboard, screen capture scanner, PDF exam extractor, practice test generator, RAG library, and interactive AI tutor chat.
   - Pre-rendered as static content (`○`) with sub-100kB first-load JS bundles.

2. **Multi-Provider BYOK AI Engine**:
   - Secure Bring-Your-Own-Key integration for **OpenAI**, **Google Gemini**, **Anthropic Claude**, and **OpenRouter**.
   - Server-side **AES-256-GCM** authenticated encryption with zero-downtime key rotation support.
   - Transparent token usage and estimated API cost tracking per user.
   - Transient failure handling with exponential backoff retries (429, 502, 503, 504).

3. **High-Accuracy OCR & Question Parser**:
   - RapidOCR (PaddleOCR ONNX) deep learning text detection and spatial line sorting.
   - Stable option identity preservation: handles unlettered radio buttons, multi-line fill-in-the-blank questions, auxiliary endings, variable option counts (2–6), assembly code instructions, and never invents artificial option letters.

4. **Multi-Tenant Security & Isolation**:
   - Backend acts as a trusted authorization boundary with strict user ownership enforcement on all routes.
   - Complete password reset lifecycle with SHA-256 token hashing, 15-minute expiration, atomic consumption, user enumeration defense, and session invalidation via `token_version`.
   - Practice tests enforce session question membership, prevent duplicate answers, and strictly isolate user quiz pools.
   - Bounded streaming file uploads (25MB limit) with magic byte inspection (PNG, JPEG, WebP, PDF).
   - Pluggable durable storage abstraction supporting local and Supabase Storage private buckets.

5. **Chrome Manifest V3 Companion Extension**:
   - Captures visible screen areas via `chrome.tabs.captureVisibleTab` and connects directly to the SaaS REST API.
   - Clean Manifest V3 architecture with zero bundled private signing keys or obsolete native messaging dependencies.

---

## Quick Start (Development)

### 1. Prerequisites
- Python 3.10+
- Node.js 18+ or 20 LTS

### 2. Install Backend Dependencies
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r backend/requirements.txt
```

### 3. Run Database Migrations
```bash
python -m alembic upgrade head
```

### 4. Install Frontend Dependencies
```bash
npm --prefix frontend install
```

### 5. Launch Development Services
Run both FastAPI (port 8000) and Next.js (port 3000) simultaneously:
```bash
python scripts/run_saas.py
```
- Web Application: http://localhost:3000
- Backend Interactive API Docs: http://127.0.0.1:8000/api/docs

---

## Testing & Quality Verification

Run the full automated test suite:

```bash
# 1. Full Python Backend & Regression Test Suite (103 tests)
python -m pytest -s tests/

# 2. Frontend Option Identity Unit Tests (6 tests)
npm --prefix frontend test

# 3. Next.js Production Build Verification (13 static routes)
npm --prefix frontend run build
```

---

## Production Security & Deployment Documentation

- [PRODUCTION_READINESS_MASTER_AUDIT.md](PRODUCTION_READINESS_MASTER_AUDIT.md) — Comprehensive readiness audit & component assessment.
- [SECURITY_REMEDIATION_REPORT.md](SECURITY_REMEDIATION_REPORT.md) — Full security remediation register and CVSS fixes.
- [TENANT_ISOLATION_TEST_REPORT.md](TENANT_ISOLATION_TEST_REPORT.md) — Multi-user tenant isolation test evidence.
- [PASSWORD_RESET_SECURITY_REPORT.md](PASSWORD_RESET_SECURITY_REPORT.md) — Secure password reset architecture.
- [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) — Production deployment checklist for Vercel, Render/Railway, and Supabase.
- [PRODUCTION_CONFIGURATION_GUIDE.md](PRODUCTION_CONFIGURATION_GUIDE.md) — Environment variables and zero-downtime key rotation guide.
- [STORAGE_MIGRATION_GUIDE.md](STORAGE_MIGRATION_GUIDE.md) — Supabase Storage private bucket configuration.

---

## License & Copyright

© 2026 GT InnoX LLP. All rights reserved.  
Distributed under commercial and enterprise licensing agreements.
