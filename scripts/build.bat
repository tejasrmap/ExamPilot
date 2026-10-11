@echo off
setlocal
echo ======================================================================
echo ExamPilot — PyInstaller Commercial Build Script
echo GT InnoX LLP — Understand Questions. Learn the Answers.
echo ======================================================================
echo.

set SCRIPT_DIR=%~dp0..
cd /d "%SCRIPT_DIR%"

:: Verify PyInstaller
python -m PyInstaller --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [*] Installing PyInstaller...
    python -m pip install pyinstaller
)

echo [*] Cleaning previous build artifacts...
if exist "build" rmdir /s /q "build"
if exist "dist\ExamPilot" rmdir /s /q "dist\ExamPilot"

echo [*] Compiling ExamPilot with PyInstaller...
python -m PyInstaller ^
    --noconfirm ^
    --onedir ^
    --windowed ^
    --name "ExamPilot" ^
    --icon "assets\icons\app_icon.ico" ^
    --add-data "assets;assets" ^
    --collect-all "rapidocr_onnxruntime" ^
    --collect-all "onnxruntime" ^
    --hidden-import "PySide6.QtCore" ^
    --hidden-import "PySide6.QtGui" ^
    --hidden-import "PySide6.QtWidgets" ^
    --hidden-import "mss" ^
    --hidden-import "pynput" ^
    --hidden-import "pynput.keyboard" ^
    --hidden-import "pynput.keyboard._win32" ^
    desktop\main.py

if %ERRORLEVEL% EQU 0 (
    echo [*] Verifying RapidOCR models in packaged distribution...
    python -c "import shutil, os, rapidocr_onnxruntime; src=os.path.dirname(rapidocr_onnxruntime.__file__); dst=r'dist\ExamPilot\_internal\rapidocr_onnxruntime'; [shutil.copytree(os.path.join(src, d), os.path.join(dst, d), dirs_exist_ok=True) for d in ['models', 'utils', 'ch_ppocr_cls', 'ch_ppocr_det', 'ch_ppocr_rec'] if os.path.exists(os.path.join(src, d))]; shutil.copy2(os.path.join(src, 'config.yaml'), os.path.join(dst, 'config.yaml'))"
    echo.
    echo ======================================================================
    echo [SUCCESS] Build succeeded! Executable located at:
    echo   dist\ExamPilot\ExamPilot.exe
    echo ======================================================================
) else (
    echo.
    echo [ERROR] PyInstaller build failed. Check error log output above.
)
pause

