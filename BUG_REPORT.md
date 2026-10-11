# ExamPilot — Bug Tracker & Technical Audit Resolution Report
**Product:** ExamPilot  
**Vendor:** GT InnoX LLP  
**Date:** November 2026  
**Target:** Windows 11 + Google Chrome (Manifest V3)  
**Release:** Beta 1.0

---

## 1. Resolved Defects & Audit Fixes

| Bug ID | Severity | Component | Issue Description | Root Cause | Resolution & Verification | Status |
|---|---|---|---|---|---|---|
| **BUG-001** | High | Native Messaging | Host manifest contained wildcard origin `chrome-extension://*/` | Incompatible with strict Chrome Web Store security | Derived deterministic RSA keypair in `manifest.json` yielding fixed ID `gdamjmdjoeegfhjolmnakjgphlgpckdh`; updated host manifest to exact origin | **Resolved & Verified** |
| **BUG-002** | High | Hardware Detection | Hardcoded `C:\` drive assumption in `system_info.py` | Assumed all users store AppData on `C:\` | Implemented `get_disk_info()` resolving root path dynamically across Windows/Linux/macOS with Registry-based display adapter enumeration | **Resolved & Verified** |
| **BUG-003** | Medium | Database History | `cannot VACUUM from within a transaction` | Calling `VACUUM` inside an open SQLite transaction block | Committed `DELETE` transaction first, then executed `VACUUM` in autocommit connection outside the transaction | **Resolved & Verified** |
| **BUG-004** | Medium | Screen Capture | Coordinate shift on High-DPI scaled displays (e.g. 125%, 150%) | Qt logical widget coordinates did not match MSS physical pixels | Added dynamic `scale_x = desktop_image.width / widget.width()` and `scale_y` multipliers before cropping | **Resolved & Verified** |
| **BUG-005** | Medium | Question Parser | Parser crashed or failed on alphanumeric/numeric option gaps | Only validated single characters without type checks, causing `ord()` crashes on multi-character keys | Implemented type-aware gap detection handling alphabetic and integer continuity safely | **Resolved & Verified** |
| **BUG-006** | Medium | Question Parser | Duplicate option values could pass through unnoticed | No uniqueness check across option string values | Added normalized value deduplication detecting identical option texts | **Resolved & Verified** |
| **BUG-007** | Low | AI Response Parser | Truncated AI responses missing closing brackets threw fatal JSONDecodeError | Model output stream cutoff | Added `_attempt_repair_truncated_json()` to balance quotes and braces | **Resolved & Verified** |
| **BUG-008** | Low | AI Output Hygiene | Potential for models to invent hallucinated URLs or reference strings | Open-source LLMs occasionally hallucinating citations | Added regex sanitizer stripping fake URL links and `[cite: ...]` patterns | **Resolved & Verified** |
| **BUG-009** | Low | OCR Startup | Missing OCR dependencies resulted in uninformative traceback | No startup pre-flight check in `OCREngine` | Added check for `rapidocr-onnxruntime` and `onnxruntime` with clear terminal/log instructions | **Resolved & Verified** |
| **BUG-010** | Low | Chrome Extension | Content script communication failed if opened on tab before extension load | Content script not injected in already-open tabs | Added `chrome.scripting.executeScript` injection safeguard in `popup.js` | **Resolved & Verified** |
| **BUG-011** | Critical | Security / Packaging | RSA private signing key `key.pem` present in source tree and ZIP distribution | Developer keypair committed into source directory | Permanently purged `key.pem`, added `*.pem`, `*.key`, `*.pfx`, `*.p12` to `.gitignore`, created automated packaging assertion in `scripts/package_extension.py` | **Resolved & Verified** |
| **BUG-012** | High | Native Messaging | Hardcoded developer path `C:\Users\tejag\Downloads\ExamPilot` in host manifests | Static paths in `host-manifest.json` and template | Replaced template paths with `{{HOST_PATH}}` and `{{EXTENSION_ID}}`; `host_registration.py` dynamically resolves runtime installation directory | **Resolved & Verified** |
| **BUG-013** | Medium | Dependencies | `cv2` imported in `ocr_engine.py` but undeclared in `requirements.txt` | Missing explicit dependency declaration | Added `opencv-python>=4.8.0` to `requirements.txt`; verified runtime loading on Windows 11 | **Resolved & Verified** |
| **BUG-014** | Medium | Test Suite | Synthetic OCR integration tests failed on word token boundary without spaces | Tiny 10px default font caused text spacing compression | Added `render_mcq_image` with 20px TrueType font and space-invariant normalization | **Resolved & Verified** |
| **BUG-015** | Medium | Cross-Platform Testing | Unconditional `import winreg` broke test execution on non-Windows environments | Windows-only module imported at module level | Wrapped `winreg` imports with platform guards (`sys.platform == 'win32'`) and `try...except ImportError` | **Resolved & Verified** |
| **BUG-016** | High | Deployment / Packaging | Native Messaging host assumed Python development environment existed on end-user machine | Batch script invoked `python` directly | Added `--native-host` CLI mode to `desktop/main.py` and compiled into `dist/ExamPilot/ExamPilot.exe`; `run_native_host.bat` prioritizes compiled executable | **Resolved & Verified** |
| **BUG-017** | Medium | Parser Regex | Matrix brackets `[c, d]]` and math fractions `3/4` false-matched as option bullets | Stray closing brackets `]` and division slashes `/` present in delimiter regex | Refined `OPTION_PATTERN` and `INLINE_OPTION_SPLIT` to require matched brackets and excluded `/`; benchmark accuracy reached 100.0% | **Resolved & Verified** |

---

## 2. Open Issues / Known Constraints

- **No critical, high, or medium severity defects remain open.**
- **Known Runtime Constraint:** Local LLM inference requires a minimum of 4 GB free RAM (for `qwen2.5:0.5b` / `qwen2.5:1.5b`) or 8 GB+ RAM for 7B models. Hardware checks enforce this requirement gracefully before model download.
