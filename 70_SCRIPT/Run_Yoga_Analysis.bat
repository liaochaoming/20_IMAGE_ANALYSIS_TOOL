@echo off
setlocal

set "ROOT=%~dp0.."
for %%I in ("%ROOT%") do set "ROOT=%%~fI"
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
echo Running YOGA full analysis...
echo Input: %ROOT%\30_CATALOG\YOGA\15_YOGA_INPUT
echo YOLO Pose: ON
echo Qwen3-VL/Ollama: ON
echo DuckDB: ON
echo RAG/vector_index: ON
echo.

"%PYTHON%" "%ENGINE%" --category YOGA

echo.
echo Done.
pause
