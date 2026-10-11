# ExamPilot — Commercial Readiness Documentation
**GT InnoX LLP — Understand Questions. Learn the Answers.**

---

## 1. Product Ownership & Brand Identity

- **Product Name**: ExamPilot™
- **Proprietor & Developer**: GT InnoX LLP
- **Tagline**: Understand Questions. Learn the Answers.
- **Trademark Notice**: ExamPilot and the ExamPilot logo are proprietary trademarks of GT InnoX LLP.
- **Licensing Model**: Dual-licensed: Commercial core distribution by GT InnoX LLP with permissive client licensing.

---

## 2. Third-Party Open Source License Inventory

All open-source dependencies used in ExamPilot were reviewed for commercial compatibility:

| Component / Library | Version | License | Commercial Permissibility | Usage Purpose |
|---------------------|---------|---------|---------------------------|---------------|
| **PySide6 (Qt for Python)** | 6.12+ | LGPLv3 | Permitted (Dynamic linking) | Desktop GUI runtime & widgets |
| **RapidOCR (PaddleOCR weights)** | 1.4+ | Apache 2.0 | Permitted (Full commercial use) | High-speed ONNX optical character recognition |
| **ONNX Runtime** | 1.23+ | MIT | Permitted | Neural inference engine for OCR |
| **MSS** | 10.2+ | MIT | Permitted | Fast multi-monitor screen capture |
| **Pillow (PIL)** | 10.1+ | Historical HPND | Permitted | Image manipulation and preprocessing |
| **Pydantic** | 2.12+ | MIT | Permitted | Data schema validation & serialization |
| **Pynput** | 1.8+ | LGPLv3 | Permitted (Dynamic import) | Global hotkey listener |
| **Requests** | 2.32+ | Apache 2.0 | Permitted | Local HTTP communication with Ollama |
| **Qwen 2.5 (Alibaba Cloud)** | 7B / 1.5B | Apache 2.0 / Qwen License | Permitted (Commercial use allowed) | Local generative reasoning & explanation |
| **Ollama** | 0.5+ | MIT | Permitted | Local inference runtime daemon |

---

## 3. Terms of Use (Summary)

1. **Permitted Learning Use**: ExamPilot is intended as a personal tutor, study guide, and practice assistant for formative self-assessment and educational revision.
2. **Academic Integrity**: ExamPilot must never be deployed to evade proctoring controls, compromise examination security, or auto-submit unpermitted answers during high-stakes closed-book testing.
3. **No Warranty on Calibrated Probability**: Confidence scores reflect heuristic certainty based on linguistic and structural analysis. Users are advised to review foundational academic texts for disputed questions.

---

## 4. Website Landing Page Copy (Commercial Marketing)

### Hero Section:
- **Headline**: Master Every MCQ. Understand Every Answer.
- **Subheadline**: Meet ExamPilot — the offline-first AI study companion that extracts practice questions from your screen, explains why the correct answer works, and uncovers why tricky options fail.
- **CTA**: Download for Windows (Free Offline Beta) • Add Chrome Extension

### Feature Highlights:
1. **100% Offline & Private**: Runs directly on your laptop with open-source Qwen models. No OpenAI subscriptions, no cloud data transmission, no spying.
2. **Instant Screen-to-Answer**: Press `Ctrl+Shift+Q` to capture any practice problem across multiple monitors. Rapid OCR recognizes mathematical symbols and multi-line options in milliseconds.
3. **Deep Option-by-Option Analysis**: Rather than just showing the correct letter, ExamPilot breaks down every single option with educational reasoning.
4. **Learning Analytics & History**: Track your practice accuracy across Computer Science, Math, Data Science, and more.

---

## 5. Beta Testing Feedback Questionnaire Template

1. How fast was the local AI response on your laptop hardware (CPU vs GPU)?
2. Did the screen capture overlay accurately enclose practice questions across your display resolution?
3. How clear and helpful were the option-by-option explanations?
4. Did you experience any issues with Ollama model downloads or Chrome Native Messaging connectivity?
5. What additional subject categories would you like to see pre-configured?

