@echo off
setlocal

set "ROOT=D:\20_IMAGE_ANALYSIS_TOOL"
set "VENV=%ROOT%\.venv"
set "PYTHON=%VENV%\Scripts\python.exe"
set "ENGINE=%ROOT%\80_APP\ANALYSIS_ENGINE\analysis_engine.py"

if not exist "%PYTHON%" (
  echo Missing Python venv: %PYTHON%
  pause
  exit /b 1
)

if not exist "%ENGINE%" (
  echo Missing analysis engine: %ENGINE%
  pause
  exit /b 1
)

cd /d "%ROOT%"
echo Running YOGA analysis...
echo Input: %ROOT%\30_CATALOG\YOGA\15_YOGA_INPUT
echo.

"%PYTHON%" "%ENGINE%" --category YOGA

echo.
echo Done.
pause
