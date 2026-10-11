# ExamPilot — Installation & Setup Guide
**GT InnoX LLP — Understand Questions. Learn the Answers.**

This guide covers installing ExamPilot on Windows, configuring the local Ollama AI engine, and registering the Chrome extension.

---

## 1. System Requirements

### Minimum Configuration:
- **OS**: Windows 10 or 11 (64-bit)
- **CPU**: Modern Dual-Core 2.0 GHz+
- **RAM**: 8 GB RAM
- **Storage**: 10 GB free space (for lightweight 1.5B/3B models)

### Recommended Configuration:
- **CPU**: Quad-Core 2.5 GHz+ (Intel Core i5/i7 or AMD Ryzen 5/7)
- **RAM**: 16 GB RAM
- **Storage**: 15 GB free SSD space (for Qwen 2.5 7B Instruct)

---

## 2. Desktop Installation

### Option A: Automated Quick Install
1. Open PowerShell or Command Prompt in the `ExamPilot` directory.
2. Run the automated installer:
   ```bat
   scripts\install.bat
   ```
   This will:
   - Validate Python 3.10+
   - Install production Python dependencies (`PySide6`, `rapidocr-onnxruntime`, `mss`, etc.)
   - Generate branding assets and high-resolution icons
   - Register the Chrome Native Messaging host in your Windows Registry
   - Create a desktop shortcut `ExamPilot.lnk`

3. Launch ExamPilot:
   ```bat
   python desktop\main.py
   ```

### Option B: Manual Installation
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Generate icons:
   ```bash
   python assets/logo/generate_branding.py
   ```
3. Run the desktop application:
   ```bash
   python desktop/main.py
   ```

---

## 3. Local AI Engine Setup (Ollama)

ExamPilot operates **100% offline-first**. No cloud API keys (OpenAI, ChatGPT, Gemini, Anthropic) are required or used.

1. **Install Ollama**:
   - Run our automated wizard:
     ```bat
     scripts\setup_ollama.bat
     ```
   - Or download manually from [ollama.com/download/windows](https://ollama.com/download/windows).

2. **Download AI Model**:
   - **For 16 GB machines (Recommended)**:
     ```bash
     ollama pull qwen2.5:7b-instruct
     ```
   - **For 8 GB machines (Lightweight)**:
     ```bash
     ollama pull qwen2.5:1.5b
     ```
   - Models can also be downloaded directly with one click inside ExamPilot's **AI Model Manager**.

---

## 4. Google Chrome Extension Setup

1. Open Google Chrome and navigate to `chrome://extensions/`.
2. Enable **Developer mode** toggle in the top-right corner.
3. Click **Load unpacked**.
4. Select the `ExamPilot\chrome-extension` directory.
5. The ExamPilot extension icon will appear in your Chrome toolbar.
6. Verify connection status: Click the extension icon. The status badge will display **Connected** if the native host registration is active.

---

## 5. Verification Checklist

- [x] Launch ExamPilot desktop application (`python desktop/main.py`).
- [x] Verify OCR Engine status chip shows **OCR Engine: Active**.
- [x] Verify Local AI chip shows **Connected (11434)** once Ollama is running.
- [x] Press `Ctrl + Shift + Q` to verify the multi-monitor snippet capture overlay.

