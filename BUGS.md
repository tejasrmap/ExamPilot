# ExamPilot — Bug Tracker & Technical Audit Status
**Product:** ExamPilot™  
**Vendor:** GT InnoX LLP  
**Current Milestone:** Beta 1.0  
**Updated:** November 2026

---

## 1. Current Active / Blocking Defects
> **STATUS: 0 OPEN DEFECTS**  
> There are currently **no unresolved critical, high, or medium severity defects** in the codebase. All automated regression tests (33/33) and benchmark suites (104/104 MCQs) pass with 100% accuracy on Windows 11.

---

## 2. Resolved Defects & Technical Audit Changelog

| Bug ID | Severity | Component | Issue Description | Mitigation / Resolution | Status |
|--------|----------|-----------|-------------------|-------------------------|--------|
| **BUG-001** | High | Native Messaging | Host manifest contained wildcard origin `chrome-extension://*/` | Derived deterministic RSA key in `manifest.json` (`gdamjmdjoeegfhjolmnakjgphlgpckdh`); updated host manifest to exact origin | **Resolved** |
| **BUG-002** | High | Hardware Detection | Hardcoded `C:\` drive assumption in `system_info.py` | Implemented multi-drive path resolution across Windows/Linux/macOS; zero-overhead Registry GPU enumeration | **Resolved** |
| **BUG-003** | Medium | Database History | `cannot VACUUM from within a transaction` error on history wipe | Committed `DELETE` transaction first, then executed `VACUUM` in autocommit connection | **Resolved** |
| **BUG-004** | Medium | Screen Capture | Coordinate shift on High-DPI scaled displays (125%, 150%) | Added dynamic scale multipliers (`scale_x`, `scale_y`) matching Qt widget to physical pixels | **Resolved** |
| **BUG-005** | Medium | Question Parser | Crash/failure on option continuity gaps | Implemented type-aware gap detection handling alphabetic and integer continuity safely | **Resolved** |
| **BUG-006** | Medium | Question Parser | Duplicate option values passing through unnoticed | Added normalized text deduplication detecting identical option texts | **Resolved** |
| **BUG-007** | Low | AI Response Parser | Truncated AI responses missing closing brackets threw JSONDecodeError | Implemented `_attempt_repair_truncated_json()` to balance quotes and braces | **Resolved** |
| **BUG-008** | Low | AI Hygiene | Risk of open-source LLMs inventing fake citations | Added regex sanitizer stripping hallucinated URLs and citation markers | **Resolved** |
| **BUG-009** | Low | OCR Startup | Missing OCR dependencies caused unhandled tracebacks | Added pre-flight check in `OCREngine` with actionable terminal and log guidance | **Resolved** |
| **BUG-010** | Low | Chrome Extension | Content script communication failed if opened on tab before extension load | Added `chrome.scripting.executeScript` injection safeguard in `popup.js` | **Resolved** |
| **BUG-011** | Critical | Security / Keys | Private signing key `chrome-extension/key.pem` present in source and ZIP packages | Permanently deleted `key.pem`; embedded public SubjectPublicKeyInfo in `manifest.json`; added `*.pem` to `.gitignore`; enforced via packaging script | **Resolved** |
| **BUG-012** | High | Native Messaging | Hardcoded developer path `C:\Users\tejag\Downloads\ExamPilot` in host manifests | Replaced with dynamic template variables `{{HOST_PATH}}` and `{{EXTENSION_ID}}`; resolved at runtime | **Resolved** |
| **BUG-013** | Medium | Dependencies | `cv2` imported in `ocr_engine.py` without explicit `requirements.txt` declaration | Added `opencv-python>=4.8.0` to `requirements.txt`; verified on Windows 11 | **Resolved** |
| **BUG-014** | Medium | Test Suite | Synthetic OCR integration test failed on token boundary spacing | Standardized `render_mcq_image` with 20px TrueType font and whitespace-invariant normalization | **Resolved** |
| **BUG-015** | Medium | Portability | `import winreg` broke automated test runs on non-Windows environments | Added conditional platform guards (`sys.platform == 'win32'`) and `try...except ImportError` | **Resolved** |
| **BUG-016** | High | Packaging | Native Messaging host assumed customer machine had Python installed | Added `--native-host` CLI flag to `main.py`; compiled into standalone `dist/ExamPilot/ExamPilot.exe` | **Resolved** |
| **BUG-017** | Medium | Parser Regex | Mathematical matrices `[[a, b], [c, d]]` and fractions `3/4` false-matched as option bullets | Excluded unbracketed `]` and division `/` from option delimiters; benchmark accuracy reached 100.0% | **Resolved** |

---

## 3. Operational Requirements & Environmental Constraints

These are system design prerequisites, not software bugs:
1. **Local Ollama Daemon:** The user must have Ollama installed and running (`ollama serve`) with at least one supported model (`qwen2.5:7b-instruct`, `qwen2.5:1.5b`, or `qwen2.5:0.5b`). If Ollama is offline, ExamPilot displays a status alert with one-click diagnostic guidance.
2. **RAM Requirements:** Minimum 4 GB free RAM for `qwen2.5:0.5b` / `qwen2.5:1.5b`, or 8–16 GB for `qwen2.5:7b-instruct`.
3. **Chrome Developer Mode:** Until ExamPilot is published on the official Chrome Web Store, the Chrome extension must be loaded via "Load unpacked" from `chrome-extension/` or `dist/exampilot-chrome-extension.zip`.
