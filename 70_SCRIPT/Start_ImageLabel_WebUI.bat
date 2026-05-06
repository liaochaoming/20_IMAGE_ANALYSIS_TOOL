@echo off
setlocal

set "ROOT=%~dp0.."
for %%I in ("%ROOT%") do set "ROOT=%%~fI"
set "VENV=%ROOT%\.venv"

if not exist "%VENV%\Scripts\activate.bat" (
  echo Missing venv: %VENV%
  pause
  exit /b 1
)

call "%VENV%\Scripts\activate.bat"
cd /d "%ROOT%"

echo Starting Image Label WebUI...
echo URL: http://127.0.0.1:7860
echo.

python 80_APP\ASSET_MANAGER_WEBUI\image_label_webui.py

pause
