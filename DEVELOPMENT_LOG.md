# ExamPilot — Development Log
**Product**: ExamPilot  
**Vendor**: GT InnoX LLP  
**Tagline**: Understand Questions. Learn the Answers.

---

## Log Entries

### Phase 1: Environment & Architecture Initialization (2026-11-05)
- Inspected development environment (Windows 10 64-bit, Python 3.10.9).
- Installed core production dependencies: `PySide6` (Qt 6.12), `mss` (multi-monitor screen capture), `rapidocr-onnxruntime` (PaddleOCR weights in ONNX runtime), `pynput` (global hotkey listener), `pydantic`.
- Generated custom ExamPilot commercial vector SVG logo, PNG icon suite (16x16 up to 512x512), and `app_icon.ico`.
- Structured repository into `desktop/`, `chrome-extension/`, `assets/`, `tests/`, `scripts/`, `docs/`.
- Created configuration and logging with automated redaction of sensitive credentials.

### Phase 2: Core Processing Engine (2026-11-05)
- Built `desktop/core/capture.py` featuring MSS multi-monitor virtual desktop capture, high-DPI scaling, and `SnippetOverlayWidget` for user-initiated region selection.
- Registered global hotkey `Ctrl+Shift+Q`.
- Built `desktop/core/ocr_engine.py` using RapidOCR with adaptive image contrast enhancement, denoising, and bounding box token confidence calculations.
- Built `desktop/core/question_parser.py` supporting single/multi-line questions, options A–E, numbers 1–5, mathematical notations, and ambiguity flagging (`needs_correction`).

### Phase 3: Local AI Inference Runtime (2026-11-05)
- Built `desktop/ai/ollama_client.py` connecting strictly to `http://localhost:11434`.
- Enforced privacy boundary preventing any external cloud API fallback.
- Built prompt builder and `ResponseParser` enforcing strict JSON output schemas, handling Markdown fences and trailing commas.
- Built `desktop/core/confidence_engine.py` with hedge word penalties and linguistic certainty calibration.
- Built `desktop/core/explanation_engine.py` for structured pedagogical breakdowns.

### Phase 4: Desktop User Interface (PySide6) (2026-11-05)
- Implemented premium dark theme matching specifications (`#0B1020`, `#111827`, `#6366F1`, `#06B6D4`).
- Built `DashboardView` with summary KPI cards, recent question table, readiness status badges, and hardware advisor.
- Built `PracticeAssistantView` supporting screen capture, image upload, manual entry, editable option inputs, local AI analysis, answer banner, and report/flag dialog.
- Built draggable, resizable `FloatingPanel` with always-on-top toggle.
- Built `HistoryView` with search, subject filter, details dialog, CSV/JSON export, and one-click history purge.
- Built `AnalyticsView` with subject practice distributions and accuracy meters.
- Built `ModelManagerView` with Ollama status detection, hardware tier guidance, model list, and percentage download progress bar.
- Built `SettingsView` with hotkey configuration, database backup/restore, and privacy factsheet.

### Phase 5: Chrome Extension (Manifest V3) & Native Messaging (2026-11-05)
- Created Manifest V3 Chrome extension with minimum permissions (`nativeMessaging`, `activeTab`, `storage`).
- Built toolbar popup UI matching brand styling with connection status badge, selection extraction, manual entry, answer display, and open desktop trigger.
- Implemented `desktop/communication/native_host.py` and `protocol.py` with 32-bit little-endian framing.
- Packaged extension into `dist/exampilot-chrome-extension.zip`.

### Phase 6: Automated Testing & 100+ MCQ Evaluation (2026-11-05)
- Created 104 verified benchmark MCQs across 8 subjects (`sample_mcq_dataset.py`).
- Built and executed `tests/evaluate_mcq_dataset.py`:
  - Parser Question Structuring Accuracy: **100.0%** (104/104)
  - Option Segmentation Fidelity: **100.0%** (416/416)
  - OCR Image Detection Rate: **100.0%** (8/8)
  - Average OCR Detection Confidence: **95.6%**
- Generated `docs/EVALUATION_REPORT.md`.
- Executed PyTest test suite (`tests/`): 21 out of 21 tests passed (100%).

### Phase 7: Packaging, Scripts & Documentation (2026-11-05)
- Created `scripts/install.bat`, `scripts/uninstall.bat`, `scripts/setup_ollama.bat`, `scripts/build.bat`.
- Authored complete documentation: `INSTALLATION.md`, `USER_GUIDE.md`, `ARCHITECTURE.md`, `PRIVACY.md`, `TROUBLESHOOTING.md`, `COMMERCIAL_READINESS.md`, `README.md`.
- Final verification complete.
