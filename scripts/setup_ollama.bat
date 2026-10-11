@echo off
setlocal
echo ======================================================================
echo ExamPilot — Ollama Local AI Setup Wizard
echo GT InnoX LLP — Understand Questions. Learn the Answers.
echo ======================================================================
echo.

:: 1. Check if Ollama CLI is already installed
where ollama >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Ollama is already installed on your system.
    goto :check_service
)

if exist "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" (
    echo [OK] Ollama executable found in AppData.
    set "PATH=%LOCALAPPDATA%\Programs\Ollama;%PATH%"
    goto :check_service
)

echo [!] Ollama is not detected on your system.
echo [*] Downloading official Ollama installer for Windows...
powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object System.Net.WebClient).DownloadFile('https://ollama.com/download/OllamaSetup.exe', '%TEMP%\OllamaSetup.exe')"

if exist "%TEMP%\OllamaSetup.exe" (
    echo [*] Running Ollama Setup...
    start /wait "" "%TEMP%\OllamaSetup.exe" /silent
    echo [OK] Ollama installation finished.
    set "PATH=%LOCALAPPDATA%\Programs\Ollama;%PATH%"
) else (
    echo [ERROR] Failed to download Ollama. Please manually install from https://ollama.com/download/windows
    pause
    exit /b 1
)

:check_service
echo.
echo [*] Checking local Ollama service status on port 11434...
powershell -Command "try { $res = Invoke-WebRequest -Uri 'http://localhost:11434/api/tags' -TimeoutSec 3 -UseBasicParsing; Write-Host '[OK] Ollama service is active and listening.' } catch { Write-Host '[!] Starting Ollama service...'; Start-Process 'ollama' -ArgumentList 'serve' -WindowStyle Hidden; Start-Sleep -Seconds 3 }"

echo.
echo ======================================================================
echo Recommended Initial Model Download:
echo 1) Qwen 2.5 7B Instruct (Recommended, 4.7 GB, requires 16 GB RAM)
echo 2) Qwen 2.5 1.5B (Lightweight, 1.0 GB, suitable for 8 GB RAM laptops)
echo 3) Skip model download for now (manage later inside ExamPilot)
echo ======================================================================
set /p choice="Select an option (1-3): "

if "%choice%"=="1" (
    echo [*] Pulling qwen2.5:7b-instruct...
    ollama pull qwen2.5:7b-instruct
) else if "%choice%"=="2" (
    echo [*] Pulling qwen2.5:1.5b...
    ollama pull qwen2.5:1.5b
) else (
    echo [*] Skipped model download. You can download models anytime in the desktop UI.
)

echo.
echo [SUCCESS] Ollama setup configuration complete!
pause

