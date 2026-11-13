# ExamPilot 2.0 — Known Issues & Operational Considerations
**Company:** GT InnoX LLP  
**Product:** ExamPilot 2.0  
**Date:** 2026-11-13  

---

## 1. Third-Party AI Provider Considerations

### 1.1 Provider Quotas & Rate Limits
- **Observation**: External AI providers (especially new OpenAI or Google Gemini accounts) may impose tiered Requests Per Minute (RPM) or Tokens Per Minute (TPM) rate limits.
- **Handling**: ExamPilot 2.0 includes an exponential backoff retry mechanism in `backend/app/providers/http_utils.py` for transient `429 Too Many Requests` responses.
- **User Impact**: If a user's personal quota is completely exhausted, the backend returns a clear error notifying the user to check their provider billing threshold.

### 1.2 Provider Unavailability & Status
- **Observation**: Third-party API outages (e.g., Anthropic or OpenAI partial service degradation) can affect question analysis.
- **Handling**: The system allows one-click switching to alternative configured providers (e.g., from OpenAI to Gemini 2.0 Flash or OpenRouter) without loss of questions or history.

---

## 2. OCR & Document Processing Considerations

### 2.1 Severely Blurred or Low-DPI Screenshots
- **Observation**: Screenshots taken at extreme angles or below 100 DPI may require manual correction.
- **Handling**: The Question Scanner view (`/scanner`) provides an interactive editable review form for both the question statement and each individual option ($A$–$F$) prior to calling the AI model. This guarantees that OCR defects do not silently mislead the student.

### 2.2 Very Large PDF Exam Papers
- **Observation**: PDF exam papers exceeding 50 scanned pages can consume significant memory during batch OCR.
- **Handling**: The PDF Question Paper module processes up to 15 pages per upload batch by default, preventing worker memory exhaustion.

---

## 3. Chrome Extension Environment

### 3.1 Unpermitted Exam Portals
- **Observation**: Certain locked exam browsers (such as Safe Exam Browser) disable all browser extensions by design.
- **Handling**: ExamPilot 2.0 is designed as a practice and learning assistant. It does not attempt to circumvent system-level kiosk lockdown software.
