# ExamPilot 2.0 — Integration Test Matrix

**Company:** GT InnoX LLP  
**Product:** ExamPilot 2.0 — *Understand Questions. Learn the Answers.*  
**Baseline Commit:** `8b5a280d6ef2bb56c8ea6e199cf1a84840ed71cd`  
**Execution Environment:** Python 3.10 / Node 20 LTS / SQLite (Dev) & Supabase Postgres (Target)  

---

## 1. Test Suite Overview

ExamPilot 2.0 maintains a multi-layer verification suite spanning unit tests, integration tests, OCR reliability tests, database persistence tests, and frontend formatting suites.

- **Total Python Tests:** 91
- **Python Tests Passed:** 91 (100%)
- **Frontend Unit Tests:** 6
- **Frontend Tests Passed:** 6 (100%)
- **Next.js Route Build:** 13/13 Static Pages (100%)

---

## 2. Mocked vs. Real Integration Distinction

In compliance with testing integrity standards, the table below clearly identifies whether each integration test runs against a live external cloud service or operates with deterministic server-side mocks/fixtures:

| Feature / Workflow | Test File | Test Type | Integration Target | Mock / Live Status |
|---|---|---|---|---|
| **User Registration & Login** | `tests/test_backend_api.py` | Real Integration | Local / Remote DB session | **LIVE** (Real database session & PBKDF2 hashing) |
| **Password Hashing & JWT** | `tests/test_security_audit.py` | Real Integration | Security Engine | **LIVE** (Real AES-256-GCM & JWT encryption) |
| **API Provider Key Encryption** | `tests/test_backend_api.py` | Real Integration | Database & Crypto | **LIVE** (Real encryption, storage, and decryption) |
| **AI Provider Request (OpenAI)** | `tests/test_ai.py` | Unit / Mock | OpenAI API | **MOCKED** (Simulated HTTP responses to prevent external API quota consumption) |
| **AI Provider Request (Gemini)** | `tests/test_ai.py` | Unit / Mock | Google Gemini API | **MOCKED** |
| **AI Provider Request (Anthropic)** | `tests/test_ai.py` | Unit / Mock | Anthropic Claude API | **MOCKED** |
| **AI Provider Request (OpenRouter)** | `tests/test_ai.py` | Unit / Mock | OpenRouter API | **MOCKED** |
| **OCR Image Scanning** | `tests/test_ocr.py`, `tests/test_backend_ocr_parser.py` | Real Integration | RapidOCR Engine | **LIVE** (Real PaddleOCR ONNX model execution) |
| **OCR Stress & Image Degradation** | `tests/test_ocr_stress_audit.py` | Real Integration | RapidOCR & OpenCV | **LIVE** (Real image transforms, blur, rotation) |
| **OCR MCQ Parsing & Regression** | `tests/test_ocr_mcq_regression.py` | Real Integration | QuestionParser | **LIVE** (18 real test fixtures covering Coursera defects) |
| **Option Identity Persistence** | `tests/test_option_identity_persistence.py` | Real Integration | Database & FastAPI | **LIVE** (Real database roundtrips, commits, reads) |
| **Practice Test Lifecycle** | `tests/test_backend_api.py` | Real Integration | Database & API | **LIVE** (Real session creation, submission, score computation) |
| **Knowledge Library & RAG** | `tests/test_backend_api.py` | Real Integration | Document Engine & DB | **LIVE** (Real text chunking & SQLite search) |
| **AI Assistant Conversations** | `tests/test_backend_api.py` | Unit / Mock | Conversation DB & AI | **HYBRID** (Real DB persistence, mocked AI reply) |
| **Analytics & Usage Tracking** | `tests/test_backend_api.py` | Real Integration | UsageLog Aggregations | **LIVE** (Real SQL `COUNT`, `SUM`, `AVG` queries) |
| **Chrome Extension Manifest & Files** | `tests/test_chrome_extension.py` | Real Integration | Manifest V3 & Filesystem | **LIVE** (Real filesystem assertions & JSON parsing) |

---

## 3. End-to-End Workflow Verification Matrix

| Workflow ID | Workflow Name | Description | Key Invariants Verified | Result |
|---|---|---|---|---|
| **WF-01** | **User Lifecycle** | Register &rarr; Login &rarr; Profile &rarr; Logout | Password hashed with PBKDF2; JWT signed with sub/exp claims; profile retrieved | **PASSED** |
| **WF-02** | **BYOK Key Management** | Add Key &rarr; Encrypt &rarr; Mask &rarr; Set Default &rarr; Delete | AES-256-GCM encryption verified; masked key `sk-pr...1234` displayed; raw key never exposed | **PASSED** |
| **WF-03** | **OCR Screen Capture Scan** | Upload PNG &rarr; RapidOCR &rarr; Parse MCQ &rarr; Detect Domain | Multi-line text extracted; question separated from options; spatial ordering preserved | **PASSED** |
| **WF-04** | **Unlettered Question Analysis** | Unlettered radio options &rarr; AI Analysis &rarr; History Save | `original_label: null` preserved; source position preserved; no letters invented in UI badge or clipboard | **PASSED** |
| **WF-05** | **Lettered Question Analysis** | Explicit `A)`, `B)`, `C)`, `D)` &rarr; AI Analysis &rarr; History Save | `original_label: "A"` preserved; badge displays `Option A`; clipboard copies `Option A: <text>` | **PASSED** |
| **WF-06** | **Manual Option Editing** | Student corrects typo in option text before analysis | `id` and `source_order` preserved; `is_user_edited: true` flag persisted; modified text saved | **PASSED** |
| **WF-07** | **Option Shuffle Resolution** | Exam shuffles options between attempts (Item #1 vs Item #3) | Answer text matches selected option; dynamic source position `#1` vs `#3` reflected without letter conflict | **PASSED** |
| **WF-08** | **Question History Retrieval** | Fetch history via `/api/questions` & `/api/questions/{id}` | Complete `structured_options` JSON array returned; legacy records (`NULL` JSON) load without errors | **PASSED** |
| **WF-09** | **Practice Test Lifecycle** | Create Quiz &rarr; Answer Questions &rarr; Submit & Score | Correct answers calculated; explanations displayed; session score percentage recorded | **PASSED** |
| **WF-10** | **Knowledge Library & RAG** | Upload Document &rarr; Chunk &rarr; Search Chunks | Text split into 500-char chunks with 80-char overlap; relevant chunks retrieved for queries | **PASSED** |
| **WF-11** | **AI Assistant Study Session** | Create Conversation &rarr; Send Message &rarr; Log Usage | History maintained up to 12 turns; usage tokens logged; estimated cost computed | **PASSED** |
| **WF-12** | **Account Deletion & GDPR** | Request data export &rarr; Delete account with confirmation | JSON export contains all user questions/sessions; cascade deletion completely purges all user data | **PASSED** |

---

## 4. Test Execution Summary

- **Total Integration Tests:** 97 (91 Python + 6 Frontend)
- **Passing Tests:** 97
- **Failing Tests:** 0
- **Skipped Tests:** 0
- **Regression Invariants Maintained:** 100%

