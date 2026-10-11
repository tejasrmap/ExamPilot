@echo off
setlocal
echo ======================================================================
echo ExamPilot — Uninstaller
echo GT InnoX LLP
echo ======================================================================
echo.

:: 1. Remove Registry Key & Manifest
echo [*] Unregistering Chrome Native Messaging Host...
reg delete "HKCU\Software\Google\Chrome\NativeMessagingHosts\com.gtinnox.exampilot" /f >nul 2>&1
if exist "%~dp0..\chrome-extension\native-messaging\host-manifest.json" (
    del "%~dp0..\chrome-extension\native-messaging\host-manifest.json" >nul 2>&1
)
echo [OK] Registry entry and host manifest removed.

:: 2. Remove Desktop Shortcut
set "DESKTOP_SHORTCUT=%USERPROFILE%\Desktop\ExamPilot.lnk"
if exist "%DESKTOP_SHORTCUT%" (
    del "%DESKTOP_SHORTCUT%"
    echo [OK] Removed Desktop shortcut.
)

:: 3. User Data Prompt
echo.
set /p del_data="Do you want to delete your local practice history and database? (y/N): "
if /i "%del_data%"=="y" (
    if exist "%LOCALAPPDATA%\ExamPilot" (
        rmdir /s /q "%LOCALAPPDATA%\ExamPilot"
        echo [OK] User data and history database removed.
    )
) else (
    echo [INFO] Local practice history preserved at %LOCALAPPDATA%\ExamPilot.
)

echo.
echo [SUCCESS] ExamPilot uninstallation finished.
pause

