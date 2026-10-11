# ExamPilot — Security Audit & Hardening Report
**Product:** ExamPilot  
**Vendor:** GT InnoX LLP  
**Date:** November 2026  
**Auditor:** GT InnoX Software Architecture & Security Team  
**Compliance Level:** Commercial Release Readiness (Beta 1.0)

---

## 1. Executive Summary

A comprehensive security audit of the ExamPilot hybrid Windows desktop and Chrome extension architecture was conducted, specifically targeting:
1. Native Messaging origin matching and IPC integrity.
2. Cryptographic key hygiene and secret leakage.
3. Extension packaging and permission minimization under Chrome Manifest V3.
4. Local AI inference boundaries and data leakage risks.
5. Windows registry safety and uninstallation cleanup.

All critical vulnerabilities identified during prior audits (including the accidental exposure of private signing keys and static developer directory paths) have been remediated and verified through automated tests.

---

## 2. Cryptographic Key Lifecycle & Remediation

### The Vulnerability (SEC-001)
Previous development iterations created `chrome-extension/key.pem` to retain extension ID continuity. This private RSA key was mistakenly present in the source repository and packaged into early ZIP distributions.

### Remediation & Verification
1. **Permanent Removal:** `key.pem` has been deleted from the repository.
2. **Git Hygiene:** Added `*.pem`, `*.key`, `*.pfx`, `*.p12`, `*.id` to `.gitignore`.
3. **Public Key Embedding:** Derived the public SubjectPublicKeyInfo directly into `chrome-extension/manifest.json`:
   ```json
   "key": "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA09h3..."
   ```
   This guarantees that unpacked developer installations and distributed packages maintain the exact same deterministic extension ID:
   `gdamjmdjoeegfhjolmnakjgphlgpckdh`
4. **Automated Enforcement:** `scripts/package_extension.py` scans every file during build and raises a fatal exception if any `.pem`, `.key`, or private artifact is found.

---

## 3. Native Messaging IPC & Sandbox Integrity

### Non-Wildcard Origin Matching
Chrome Native Messaging requires an `allowed_origins` field in the host manifest. Wildcards (`*`) are prohibited by Chrome Web Store policies and allow arbitrary extensions to execute native binaries.
- ExamPilot host manifest now dynamically binds exclusively to:
  `chrome-extension://gdamjmdjoeegfhjolmnakjgphlgpckdh/`

### Dynamic Installation Path Resolution
- Removed hardcoded developer paths (`C:\Users\tejag\...`) from templates.
- Manifest generation resolves the actual runtime path dynamically via `host_registration.py`.
- Windows Registry registration key:
  `HKCU\Software\Google\Chrome\NativeMessagingHosts\com.gtinnox.exampilot`

### Standalone Executable Invocation
The native host is launched via `ExamPilot.exe --native-host`, eliminating the requirement for Python interpreters, pip packages, or external scripting environments on customer machines.

---

## 4. Local AI Inference & Zero-Data-Exfiltration Architecture

- **100% Offline-First:** AI processing is routed strictly to the local Ollama instance on `127.0.0.1:11434`.
- **Zero Cloud API Telemetry:** No user questions, screen captures, or OCR transcripts are transmitted to ChatGPT, OpenAI, Google Gemini, Anthropic, or external telemetry servers.
- **Sanitized Model Responses:** AI responses are filtered through regex sanitizers to strip hallucinated URLs and simulated markdown links.
- **Input Validation:** All payloads received across Native Messaging stdio undergo strict JSON schema and length validation (`desktop/security/validation.py`) to prevent buffer overflows or injection attempts.

---

## 5. Chrome Manifest V3 Compliance

The extension manifest strictly complies with Chrome Web Store developer guidelines:
- Minimal permissions: `"nativeMessaging"`, `"activeTab"`, `"scripting"`, `"storage"`.
- Zero background persistent pages (uses standard MV3 service worker `background.js`).
- Zero remote code execution (no `eval()`, no external script injection).
- All UI assets and stylesheets are bundled locally within the extension directory.
