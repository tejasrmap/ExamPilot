# ExamPilot — Troubleshooting & Diagnostics Guide
**GT InnoX LLP**

This guide provides step-by-step diagnostic procedures for common operational issues.

---

## 1. Local AI / Ollama Service Issues

### Symptom: Status badge shows "Local AI: Disconnected" or "Service: Stopped"
**Cause**: The Ollama daemon is not running on `localhost:11434`.
**Solution**:
1. Check if Ollama is running in your Windows system tray.
2. If not running, open Command Prompt and execute:
   ```cmd
   ollama serve
   ```
3. Or run the automated setup wizard:
   ```cmd
   scripts\setup_ollama.bat
   ```
4. Click **Refresh Status** in the **AI Model Manager** view.

---

## 2. Model Missing or Inference Error

### Symptom: "Model 'qwen2.5:7b-instruct' is not installed locally"
**Cause**: The configured primary model has not been pulled to local storage.
**Solution**:
1. In ExamPilot, open the **AI Model Manager** from the sidebar.
2. Under **Recommended Open-Source Models**, click **Download** next to `Qwen 2.5 7B Instruct` (or `Qwen 2.5 1.5B` for 8 GB laptops).
3. Wait for the percentage progress bar to finish.
4. Select the newly downloaded model from the **Active AI Model** dropdown.

---

## 3. Chrome Extension Disconnected

### Symptom: Extension popup displays "Disconnected" status
**Cause**: Chrome Native Messaging Host is not registered in the Windows Registry.
**Solution**:
1. Run the installer script with administrator privileges if necessary:
   ```cmd
   scripts\install.bat
   ```
2. Check Windows Registry:
   - Key: `HKCU\Software\Google\Chrome\NativeMessagingHosts\com.gtinnox.exampilot`
   - Default value should point to: `<ExamPilot_Dir>\chrome-extension\native-messaging\host-manifest.json`
3. Restart Google Chrome.

---

## 4. OCR Extraction Returns Partial or Empty Text

### Symptom: Questions with dark backgrounds or low resolution have missing options
**Solution**:
1. Ensure your capture region encloses the full question text and option labels (A, B, C, D).
2. Use the **Extracted Question Preview** and **Editable Options** in the Practice Assistant to correct any missing characters before clicking **Analyse Question**.
3. For zoomed-in displays, ExamPilot applies automatic DPI scaling and contrast enhancement, but clear screenshots yield highest confidence.

---

## 5. Global Hotkey (Ctrl+Shift+Q) Conflict

### Symptom: Pressing `Ctrl + Shift + Q` does not open the selection overlay
**Cause**: Another background application (e.g. streaming tool, browser shortcut) has reserved the hotkey.
**Solution**:
1. You can launch snippet selection manually at any time by clicking the **Capture Practice MCQ** button on the Dashboard or Floating Panel.
2. Configure or inspect hotkey settings under the **Settings** view.

---

## 6. Accessing Diagnostic Logs

Detailed rotated logs are stored locally:
```
%LOCALAPPDATA%\ExamPilot\logs\exampilot.log
```
Logs contain timestamped execution events and sanitized error traces.

