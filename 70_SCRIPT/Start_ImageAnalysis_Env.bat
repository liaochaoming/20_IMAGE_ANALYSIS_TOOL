@echo off
setlocal

set "ROOT=D:\20_IMAGE_ANALYSIS_TOOL"
set "VENV=%ROOT%\.venv"

if not exist "%VENV%\Scripts\activate.bat" (
  echo Missing venv: %VENV%
  pause
  exit /b 1
)

call "%VENV%\Scripts\activate.bat"
cd /d "%ROOT%"

echo Image Analysis Tool environment activated.
echo Tool root: %ROOT%
echo YOLO pose models: D:\30_AI_MODEL\YOLO_POSE\models
echo.
echo Test command:
echo python 70_SCRIPT\verify_full_env.py
echo.
cmd /k
