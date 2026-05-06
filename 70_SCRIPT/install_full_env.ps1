$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Venv = Join-Path $Root ".venv"
$Python = Join-Path $Venv "Scripts\python.exe"
$Log = Join-Path $Root "99_LOG\ASSET_MANAGER\install_full_env.log"

New-Item -ItemType Directory -Force -Path (Join-Path $Root "99_LOG\ASSET_MANAGER") | Out-Null

"[$(Get-Date -Format s)] Install image analysis Python environment" | Tee-Object -FilePath $Log -Append
"Root: $Root" | Tee-Object -FilePath $Log -Append

if (!(Test-Path -LiteralPath $Python)) {
    py -3.11 -m venv $Venv 2>&1 | Tee-Object -FilePath $Log -Append
}

& $Python -m pip install --upgrade pip setuptools wheel 2>&1 | Tee-Object -FilePath $Log -Append

& $Python -m pip install `
  fastapi uvicorn gradio tqdm openpyxl duckdb ollama requests `
  mediapipe ultralytics opencv-python pillow numpy pandas matplotlib `
  2>&1 | Tee-Object -FilePath $Log -Append

& $Python -m pip install --force-reinstall torch==2.11.0+cu130 torchvision==0.26.0+cu130 --index-url https://download.pytorch.org/whl/cu130 2>&1 | Tee-Object -FilePath $Log -Append
& $Python -m pip install ultralytics-thop 2>&1 | Tee-Object -FilePath $Log -Append

& $Python -m pip check 2>&1 | Tee-Object -FilePath $Log -Append

& $Python -c "import torch; import ultralytics; import mediapipe as mp; import cv2; print('torch', torch.__version__); print('cuda_available', torch.cuda.is_available()); print('gpu', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'NONE'); print('ultralytics', ultralytics.__version__); print('mediapipe', mp.__version__); print('opencv', cv2.__version__)" 2>&1 | Tee-Object -FilePath $Log -Append

"[$(Get-Date -Format s)] Install finished" | Tee-Object -FilePath $Log -Append
