@echo off
setlocal
set "SCRIPT_DIR=%~dp0.."
pushd "%SCRIPT_DIR%"

:: 1. If running as packaged distribution, try ExamPilot.exe directly
if exist "%SCRIPT_DIR%\ExamPilot.exe" (
    "%SCRIPT_DIR%\ExamPilot.exe" --native-host
    if %ERRORLEVEL% EQU 0 (
        popd
        exit /b 0
    )
)

if exist "%SCRIPT_DIR%\dist\ExamPilot\ExamPilot.exe" (
    "%SCRIPT_DIR%\dist\ExamPilot\ExamPilot.exe" --native-host
    if %ERRORLEVEL% EQU 0 (
        popd
        exit /b 0
    )
)

:: 2. Otherwise run using Python in development environment
where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    python "%SCRIPT_DIR%\desktop\communication\native_host.py"
    set "RET=%ERRORLEVEL%"
    popd
    exit /b %RET%
)

where py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    py "%SCRIPT_DIR%\desktop\communication\native_host.py"
    set "RET=%ERRORLEVEL%"
    popd
    exit /b %RET%
)

echo [ERROR] Neither ExamPilot.exe nor Python was found to run ExamPilot Native Messaging Host. >&2
popd
exit /b 1
