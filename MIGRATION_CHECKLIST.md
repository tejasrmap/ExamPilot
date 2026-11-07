# ExamPilot 2.0 — Codebase Audit & Migration Checklist
**Product:** ExamPilot 2.0  
**Company:** GT InnoX LLP  
**Date:** 2026-11-13  
**Auditor:** Principal Software Architect & Senior Full-Stack Engineer  

---

## 1. Executive Summary & Existing Codebase Inventory

A complete audit of the legacy ExamPilot repository (`desktop/`, `chrome-extension/`, `tests/`, `scripts/`) was conducted.
The existing product was an offline-first desktop application based on PySide6, local Ollama LLM inference, SQLite local storage, and Native Messaging IPC.

### 1.1 Existing Architecture Breakdown
| Module | Location | Current Role | Migration Strategy for ExamPilot 2.0 |
|---|---|---|---|
| **Question Parser** | `desktop/core/question_parser.py` | Regex and structure parser for single/multi-line MCQs, variable options (A-F), assembly instructions protection. | **PRESERVE & MIGRATE** to `backend/app/services/parser.py`. Retain `_find_question_end`, spatial sorting, multi-sentence preservation. |
| **OCR Engine** | `desktop/core/ocr_engine.py` | RapidOCR onnxruntime pipeline, Lanczos image enhancement, $(Y//12, X)$ polygon box spatial coordinate sorting. | **PRESERVE & MIGRATE** to `backend/app/services/ocr.py`. Add PyMuPDF PDF page renderer for multi-page PDF papers. |
| **Confidence & Explanation** | `desktop/core/confidence_engine.py`, `explanation_engine.py` | Pedagogical formatting, reason generation, calibrated confidence boundaries. | **PRESERVE & MIGRATE** to `backend/app/services/confidence.py` and `explanation.py`. |
| **Domain Detector** | `desktop/ai/domain_detector.py` | Keyword-based curriculum subject detector (Computer Science, Business, Electrical, etc.). | **PRESERVE & MIGRATE** to `backend/app/ai/domain_detector.py`. |
| **AI Prompts** | `desktop/ai/prompts.py` | Structured system prompts for MCQ analysis and distractors. | **PRESERVE & EXPAND** for OpenAI, Gemini, Anthropic, OpenRouter API provider layer with Pydantic JSON schemas. |
| **Ollama Client** | `desktop/ai/ollama_client.py` | Local Ollama HTTP daemon inference. | **REPLACE COMPLETELY** with Unified Multi-Provider AI Abstraction Layer (`backend/app/providers/`). |
| **PySide6 Desktop UI** | `desktop/ui/`, `desktop/app.py` | Windows PySide6 Qt GUI. | **REPLACE AS PRIMARY WORKFLOW** with Next.js 14+ App Router SaaS web application (`frontend/`). Desktop code kept archived. |
| **Storage / DB** | `desktop/database/` | SQLite local database. | **MIGRATE** to PostgreSQL / Supabase with SQLAlchemy 2.0, Alembic migrations, and Row Level Security (RLS). |
| **Native Messaging** | `desktop/communication/`, `chrome-extension/native-messaging/` | Windows registry Native Host IPC. | **REPLACE** with standard HTTP REST / Bearer Auth API communication for Chrome Extension MV3. |
| **Chrome Extension** | `chrome-extension/` | Manifest V3 extension with native host connector & hardcoded signing key. | **UPDATE** to connect directly to ExamPilot 2.0 web API with JWT session tokens; remove hardcoded signing key. |

---

## 2. Security Vulnerabilities & Remediation Identified

1. **Hardcoded Extension Key in `chrome-extension/manifest.json`**:
   - *Issue*: A public key string (`"key": "MIIBIj..."`) was present in `manifest.json`.
   - *Remediation*: Remove hardcoded `key` from manifest. Let Chrome Web Store generate package keys or provide clean development IDs.
2. **Obsolete Native Messaging**:
   - *Issue*: Requires Windows registry keys and local binaries running on localhost.
   - *Remediation*: Transition extension to standard web-native fetch requests targeting the authenticated SaaS backend API (`/api/questions/analyse`, `/api/ocr/image`).
3. **Plaintext / Local API Key Storage Risk**:
   - *Issue*: Storing API keys in plain text or client localStorage exposes keys to XSS or theft.
   - *Remediation*: All provider API keys (OpenAI, Gemini, Anthropic, OpenRouter) MUST be encrypted at rest using AES-256-GCM with a server-side `API_KEY_ENCRYPTION_SECRET`. Keys are masked upon storage (`sk-proj-••••••••••••1234`) and never decrypted to frontend responses.

---

## 3. Migration Roadmap & Checklist

- [x] **Phase 1: Codebase Audit & Architectural Mapping**
  - [x] Full inventory of existing modules.
  - [x] Identification of reusable business logic (`question_parser`, `ocr_engine`, `domain_detector`, `prompts`).
  - [x] Security vulnerability audit and remediation plan.
  - [x] Setup `MIGRATION_CHECKLIST.md`, `DEVELOPMENT_LOG.md`, `FEATURE_STATUS.md`.

- [ ] **Phase 2: Backend Architecture & Security Infrastructure (`backend/`)**
  - [ ] Initialize FastAPI project with modular routing (`backend/app/`).
  - [ ] Implement AES-256-GCM encryption & decryption service for user API keys.
  - [ ] Implement SQLAlchemy models: `Profile`, `APIProvider`, `Question`, `Subject`, `PracticeSession`, `PracticeAnswer`, `Document`, `DocumentChunk`, `Conversation`, `Message`, `UsageLog`, `UserSetting`.
  - [ ] Implement database initialization script & Supabase RLS schema generator.
  - [ ] Implement JWT Bearer token authentication & Supabase Auth validation dependency.

- [ ] **Phase 3: Multi-Provider AI Abstraction Layer (`backend/app/providers/`)**
  - [ ] Base AI provider interface (`validate_key`, `list_models`, `generate_answer`, `chat_stream`).
  - [ ] OpenAI Provider (`gpt-4o`, `gpt-4o-mini`, etc.).
  - [ ] Google Gemini Provider (`gemini-2.0-flash`, `gemini-1.5-pro`, etc.).
  - [ ] Anthropic Provider (`claude-3-5-sonnet`, `claude-3-5-haiku`, etc.).
  - [ ] OpenRouter Provider (`deepseek`, `meta-llama`, etc.).
  - [ ] Provider Registry & Model Catalog with token usage and cost estimation.

- [ ] **Phase 4: Core Services & API Endpoints (`backend/app/api/`)**
  - [ ] Migrate OCR engine (RapidOCR + OpenCV + PyMuPDF) into `/api/ocr/`.
  - [ ] Migrate Question Parser into `/api/questions/`.
  - [ ] Implement `/api/providers/` (CRUD, test connection, model list, set default).
  - [ ] Implement `/api/questions/analyse` with Pydantic structured output validation.
  - [ ] Implement `/api/assistant/` (conversational chat with session history).
  - [ ] Implement `/api/practice/` (test creation, timed sessions, grading, explanation).
  - [ ] Implement `/api/documents/` (PDF question papers & study documents).
  - [ ] Implement `/api/analytics/` (real SQL aggregated usage, accuracy, and cost metrics).
  - [ ] Implement `/api/settings/` (profile, export data, account deletion).

- [ ] **Phase 5: Next.js Frontend Application (`frontend/`)**
  - [ ] Initialize Next.js 14+ App Router TypeScript project.
  - [ ] Configure Tailwind CSS with dark-first SaaS theme (`#090D18`, `#101625`, `#151D2E`, `#7865F5`).
  - [ ] Build responsive Dashboard Layout (Sidebar, Top Navigation, Breadcrumbs).
  - [ ] Implement 10 production pages:
    1. Overview / Dashboard
    2. Question Scanner
    3. AI Assistant
    4. Practice Tests
    5. PDF Question Papers
    6. Knowledge Library
    7. Question History
    8. Analytics & Usage
    9. API Providers (BYOK Management)
    10. Settings & Account
  - [ ] Connect state to backend REST APIs.

- [ ] **Phase 6: Chrome Extension Companion (`chrome-extension/`)**
  - [ ] Update Manifest V3: remove private signing key, clean permissions.
  - [ ] Update popup and background scripts to authenticate via API and submit scans.

- [ ] **Phase 7: End-to-End Verification & Test Suite**
  - [ ] Pytest suite for backend APIs, encryption, OCR, parser, and provider adapters.
  - [ ] Acceptance test verification across all 20 criteria steps.

