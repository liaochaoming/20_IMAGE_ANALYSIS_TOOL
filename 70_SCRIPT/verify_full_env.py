import os
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


ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR_ENV = "IMAGE_ANALYSIS_MODEL_DIR"
MODEL_DIR = Path(os.environ.get(MODEL_DIR_ENV, r"D:\30_AI_MODEL\YOLO_POSE\models"))
PORTABLE_MODEL_DIR = ROOT / "90_MODEL" / "YOLO_POSE" / "models"


def resolve_model(filename: str) -> Path:
    candidates = [
        MODEL_DIR / filename,
        PORTABLE_MODEL_DIR / filename,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


YOLO_POSE = resolve_model("yolo11x-pose.pt")

assert YOLO_POSE.exists(), f"Missing model: {YOLO_POSE}"

print("fastapi", fastapi.__version__)
print("gradio", gradio.__version__)
print("mediapipe", mp.__version__)
print("opencv", cv2.__version__)
print("torch", torch.__version__)
print("cuda_available", torch.cuda.is_available())
print("gpu", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "NONE")
print("model_dir", str(YOLO_POSE.parent))

YOLO(str(YOLO_POSE))

print("IMAGE_ANALYSIS_FULL_ENV_OK")
