# ExamPilot Beta 1.0 — Release Notes
**Product:** ExamPilot™  
**Developer:** GT InnoX LLP  
**Tagline:** Understand Questions. Learn the Answers.  
**Release Date:** November 2026  
**Target Platform:** Windows 10 & 11 (64-bit) + Google Chrome (Manifest V3)

---

## What is ExamPilot?

ExamPilot is an offline-first AI-powered MCQ practice and explanation assistant developed by **GT InnoX LLP**. Designed specifically for formative practice, self-paced study, and conceptual mastery, ExamPilot captures questions from your screen, extracts the text and options, identifies the best-supported answer, and explains why tricky alternatives are flawed.

---

## Key Highlights of Beta 1.0

### 1. 100% Offline-First AI Inference
- Powered by local open-source models through **Ollama** (`localhost:11434`).
- Pre-configured for **Qwen 2.5 7B Instruct** (recommended for 16 GB machines), **Qwen 2.5 1.5B** (lightweight for 8 GB machines), and **Qwen 2.5 0.5B** (ultra-fast).
- Zero paid API keys, zero cloud telemetry, zero subscription fees.
- Verified live with actual local Ollama models on Windows 11.

### 2. Multi-Monitor Screen Capture & RapidOCR
- Global hotkey `Ctrl + Shift + Q` launches an interactive transparent selection overlay.
- High-DPI scaling support for high-resolution displays.
- Integrated **RapidOCR** (PaddleOCR ONNX weights) with explicit OpenCV dependencies.
- Editable options preview allowing students to review and adjust extracted text before analysis.

### 3. Pedagogical Explanation & Confidence Engine
- Generates thorough explanations that break down **every single option** with educational rationale.
- Calibrates confidence scores using linguistic features to prevent misleading certainty.
- Report / Flag feature allows learners to record feedback on ambiguous questions.

### 4. Google Chrome Extension (Manifest V3)
- Native Messaging host bridge connecting the browser toolbar directly to the local desktop application.
- Deterministic extension key and exact allowed origin: `chrome-extension://gdamjmdjoeegfhjolmnakjgphlgpckdh/`.
- Packaged into clean distribution ZIP `dist/exampilot-chrome-extension.zip` with zero private keys or local machine paths.
- Standalone Native Host binary mode: packaged `ExamPilot.exe --native-host` executes without requiring Python on customer machines.

### 5. Floating Learning Assistant & Study History
- Compact, draggable, resizable floating panel with always-on-top mode.
- Searchable question history stored locally in SQLite with WAL mode.
- Export practice history to CSV or JSON.
- One-click instant history wipe for full privacy control.

---

## Installation & Getting Started

1. **Quick Install**:
   Run `scripts\install.bat` to install dependencies, generate icons, register the Chrome host, and create a desktop shortcut.

2. **Chrome Extension Setup**:
   - Open `chrome://extensions/` in Google Chrome.
   - Enable **Developer mode** (top right toggle).
   - Click **Load unpacked** and select the `chrome-extension/` directory, or unzip `dist/exampilot-chrome-extension.zip`.
   - Verify extension ID is `gdamjmdjoeegfhjolmnakjgphlgpckdh`.

3. **Install Local Model**:
   - Install Ollama from [ollama.com](https://ollama.com).
   - In terminal, run: `ollama pull qwen2.5:7b-instruct` or `ollama pull qwen2.5:1.5b`.
   - Launch ExamPilot and start practicing!
