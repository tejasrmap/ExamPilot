@echo off
setlocal
echo ======================================================================
echo ExamPilot — Windows Installation & Host Registration
echo GT InnoX LLP — Understand Questions. Learn the Answers.
echo ======================================================================
echo.

set SCRIPT_DIR=%~dp0..
cd /d "%SCRIPT_DIR%"

:: 1. Verify Python
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python 3.10+ is required but not found in PATH.
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 2. Install Dependencies
echo [*] Installing required Python dependencies...
python -m pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

:: 3. Generate Branding Assets
echo [*] Verifying branding assets and icons...
python assets\logo\generate_branding.py

:: 4. Register Native Messaging Host in Windows Registry for Chrome
echo [*] Registering Chrome Native Messaging Host (com.gtinnox.exampilot)...
python desktop\communication\host_registration.py
if %ERRORLEVEL% EQU 0 (
    echo [OK] Chrome Native Messaging Host registered in Registry with exact Extension ID.
) else (
    echo [WARNING] Could not write to registry. Chrome extension may require manual host registration.
)

:: 5. Create Desktop and Start Menu Shortcuts
echo [*] Creating Application shortcuts for ExamPilot...
powershell -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%\scripts\create_shortcuts.ps1"

:: 6. Verify Ollama Service Status
echo [*] Checking local Ollama AI inference runtime...
powershell -Command "try { $res = Invoke-RestMethod -Uri 'http://localhost:11434/api/tags' -TimeoutSec 2; Write-Host '[OK] Ollama local service is active and responsive.' } catch { Write-Host '[INFO] Ollama service not currently detected. Starting Ollama...' ; Start-Process -FilePath \"$env:LOCALAPPDATA\Programs\Ollama\ollama.exe\" -ArgumentList 'serve' -WindowStyle Hidden -ErrorAction SilentlyContinue }"

echo.
echo ======================================================================
echo [SUCCESS] ExamPilot Installation Complete!
echo You can now launch ExamPilot from your Desktop shortcut or Start Menu.
echo ======================================================================
pause

