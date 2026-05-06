from pathlib import Path

import cv2
import fastapi
import gradio
import mediapipe as mp
import ollama
import openpyxl
import requests
import torch
import tqdm
import uvicorn
from ultralytics import YOLO


YOLO_MODEL_DIR = Path(r"D:\30_AI_MODEL\YOLO_POSE\models")
YOLO_FAST = YOLO_MODEL_DIR / "yolo11n-pose.pt"
YOLO_STRONG = YOLO_MODEL_DIR / "yolo11x-pose.pt"

assert YOLO_FAST.exists(), f"Missing model: {YOLO_FAST}"
assert YOLO_STRONG.exists(), f"Missing model: {YOLO_STRONG}"

print("fastapi", fastapi.__version__)
print("gradio", gradio.__version__)
print("mediapipe", mp.__version__)
print("opencv", cv2.__version__)
print("torch", torch.__version__)
print("cuda_available", torch.cuda.is_available())
print("gpu", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "NONE")

YOLO(str(YOLO_FAST))
YOLO(str(YOLO_STRONG))

print("IMAGE_ANALYSIS_FULL_ENV_OK")
