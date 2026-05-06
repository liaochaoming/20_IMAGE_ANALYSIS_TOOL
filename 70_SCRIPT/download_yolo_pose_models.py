from pathlib import Path

import cv2
import numpy as np
import torch
from ultralytics import YOLO


TOOL_ROOT = Path(r"D:\20_IMAGE_ANALYSIS_TOOL")
MODEL_DIR = Path(r"D:\30_AI_MODEL\YOLO_POSE\models")
MODEL_DIR.mkdir(parents=True, exist_ok=True)

print("tool_root", TOOL_ROOT)
print("model_dir", MODEL_DIR)
print("torch", torch.__version__)
print("cuda_available", torch.cuda.is_available())
print("gpu", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "NONE")

for name in ["yolo11n-pose.pt", "yolo11x-pose.pt"]:
    target = MODEL_DIR / name
    if target.exists():
        print(f"exists {target}")
        continue

    print(f"loading {name}")
    model = YOLO(name)
    source = Path(model.ckpt_path)
    target.write_bytes(source.read_bytes())
    print(f"saved {target}")

test_img = TOOL_ROOT / "30_CATALOG" / "YOGA" / "20_ANALYSIS_RESULT" / "gpu_test.jpg"
test_img.parent.mkdir(parents=True, exist_ok=True)

img = np.zeros((640, 640, 3), dtype=np.uint8)
cv2.line(img, (320, 100), (320, 500), (255, 255, 255), 8)
cv2.line(img, (220, 220), (420, 220), (255, 255, 255), 8)
cv2.line(img, (320, 500), (230, 620), (255, 255, 255), 8)
cv2.line(img, (320, 500), (410, 620), (255, 255, 255), 8)
cv2.imwrite(str(test_img), img)

model = YOLO(str(MODEL_DIR / "yolo11n-pose.pt"))
results = model.predict(str(test_img), device=0 if torch.cuda.is_available() else "cpu", verbose=False)
print("gpu_predict_ok", len(results))

