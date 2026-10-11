# ExamPilot — Remaining Work & Post-Beta Roadmap
**Product:** ExamPilot  
**Vendor:** GT InnoX LLP  
**Current Milestone:** Beta 1.0 (Audit & Technical Tasks Completed)  
**Future Target:** Production Release 1.1+

---

## 1. Beta 1.0 Completion Status

All 21 tasks across Phases 1 through 7 and the 11 technical audit tasks have been completed and verified with empirical test suites on Windows 11:

- [x] Task 1: Fix Native Messaging Registration (Exact Extension ID derived, wildcard removed)
- [x] Task 2: Fix Hardware Detection (Non-hardcoded drives, GPU detection, memory advisor)
- [x] Task 3: Fix OCR Dependencies (RapidOCR + ONNX runtime + explicit OpenCV declared)
- [x] Task 4: Verify Screen Capture (MSS multi-monitor, DPI scaling, rubberband overlay)
- [x] Task 5: Improve MCQ Extraction (Multi-line, math symbols, options A–F)
- [x] Task 6: Improve Question Parser (Missing options, duplicates, math fractions, matrices)
- [x] Task 7: Verify Ollama Integration (Local REST API, timeout, connection recovery)
- [x] Task 8: Improve Model Manager (Hardware recommendations, live download progress)
- [x] Task 9: Improve AI Answer Engine (Pedagogical option-by-option analysis)
- [x] Task 10: AI Response Reliability (Repairs truncated JSON, strips fake citations)
- [x] Task 11: Validate Manifest V3 (MV3 compliant, minimum permissions, fixed public key)
- [x] Task 12: Complete Native Messaging (32-bit little-endian framing, request/response IDs)
- [x] Task 13: Chrome Practice Workflow (Permitted tab extraction & manual entry)
- [x] Task 14: Dashboard (Statistics, recent questions, status chips, hardware info)
- [x] Task 15: Floating Panel (Draggable, resizable, always-on-top, compact)
- [x] Task 16: Question History (SQLite WAL, search, filter, CSV/JSON export, wipe)
- [x] Task 17: Settings (Shortcuts, endpoints, backups, restore, privacy factsheet)
- [x] Task 18: Security Audit (Zero cloud leakage, sanitized logging, permission check, key hygiene)
- [x] Task 19: Performance Audit (Sub-second startup, <100MB RAM, 2400+ qps parser)
- [x] Task 20: Windows Installer (PyInstaller build, native host standalone execution)
- [x] Task 21: Final QA & Documentation (33 automated unit tests, 104 MCQ benchmark, live Ollama test)

---

## 2. Post-Beta Product Roadmap (Release 1.1+)

The following secondary enhancements are planned for future iterative updates based on student and educator feedback:

1. **LaTeX Rendered Preview Widget**:
   - Render mathematical equations natively using KaTeX / MathJax inside the Practice Assistant and Question History dialogs.
2. **Spaced Repetition Flashcard Mode**:
   - Add a Leitner box or SM-2 algorithm practice mode that automatically re-quizzes students on previously flagged or low-confidence questions.
3. **Chrome Web Store Public Storefront Submission**:
   - Submit `dist/exampilot-chrome-extension.zip` to the official Chrome Web Store dashboard once the commercial landing page and store listing assets are finalized.
4. **Direct Windows Installer MSI / InnoSetup Package**:
   - In addition to the existing `scripts/install.bat` and PyInstaller build script, package an optional one-click `.msi` or InnoSetup wizard for enterprise classroom rollouts.
5. **Additional Specialized Subject Model Adapters**:
   - Add fine-tuned LoRA weights or specialized system prompts for medical examinations (USMLE), law assessments (LSAT), and civil service exams.
