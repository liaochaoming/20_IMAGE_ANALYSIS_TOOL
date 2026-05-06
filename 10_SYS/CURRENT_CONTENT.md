# CURRENT_CONTENT

STATUS: ACTIVE
SCOPE: IMAGE_ANALYSIS_TOOL SESSION HANDOFF
LAST_UPDATE: 2026-05-07

## 專案目標

建立本機圖片分析工具，支援四大分類：

```text
YOGA
ANATOMY
INTERIOR_DESIGN
LIAO_PHOTO
```

系統目標是讓圖片從全域入口或分類入口進入，經由共用分析引擎讀取各分類 `10_CONFIG`，產出分析 JSON、TAG、DB、RAG 結果，並可透過 WebUI 以中文直觀看到標籤。

## 開機 / 控制檔

目前控制讀取順序以此檔為準：

```text
10_SYS\02_ACTIVE_DIRECTORY_INDEX.md
```

本專案不需要：

```text
10_SYS\03_MASTER_CONTROL_INDEX.md
```

`02_ACTIVE_DIRECTORY_INDEX.md` 已合併 active directory index 與 boot control index，不應將 `03_MASTER_CONTROL_INDEX.md` 視為缺少開機檔。

核心架構檔：

```text
10_SYS\04_SYSTEM_ARCHITECTURE.md
```

長期決策檔：

```text
10_SYS\05_PROJECT_KNOWLEDGE.md
```

目前狀態檔：

```text
10_SYS\06_PROJECT_STATUS_CURRENT.md
```

## 本次完成

1. 依序完成開工讀檔：

```text
10_SYS\00_KINGDOM_SYS.md
10_SYS\01_EXECUTION_POLICY.md
10_SYS\02_ACTIVE_DIRECTORY_INDEX.md
10_SYS\04_SYSTEM_ARCHITECTURE.md
10_SYS\05_PROJECT_KNOWLEDGE.md
10_SYS\06_PROJECT_STATUS_CURRENT.md
最新 10_SYS\CODEX_CONTINUE_CONTENT_*.md
10_SYS\CURRENT_CONTENT.md
```

2. 確認 WebUI 狀態：

```text
WebUI build 成功
啟動腳本：70_SCRIPT\Start_ImageLabel_WebUI.bat
主程式：80_APP\ASSET_MANAGER_WEBUI\image_label_webui.py
URL：http://127.0.0.1:7860
YOGA input：30_CATALOG\YOGA\15_YOGA_INPUT
YOGA auto_tags：30_CATALOG\YOGA\50_TAG\auto_tags
```

3. 確認 GPU / YOLO 環境：

```text
GPU：NVIDIA GeForce RTX 5080
Torch：2.11.0+cu130
CUDA：True
verify_full_env.py：IMAGE_ANALYSIS_FULL_ENV_OK
```

4. 移除舊快版 YOLO 依賴，正式模型統一為：

```text
D:\30_AI_MODEL\YOLO_POSE\models\yolo11x-pose.pt
```

已去除舊快版模型、快版模型鍵名、快版驗證變數與快版文件描述。

5. 更新 Analysis Engine：

```text
80_APP\ANALYSIS_ENGINE\analysis_engine.py
```

現在 `load_yolo_model()` 只讀 pipeline 裡的 `models.yolo_pose`。

6. 更新 YOGA Pipeline：

```text
30_CATALOG\YOGA\10_CONFIG\YOGA_ANALYSIS_PIPELINE.json
```

目前模型欄位：

```json
"yolo_pose": "D:\\30_AI_MODEL\\YOLO_POSE\\models\\yolo11x-pose.pt",
"active_yolo_pose": "strong"
```

7. 更新環境驗證與模型下載腳本：

```text
70_SCRIPT\verify_full_env.py
70_SCRIPT\download_yolo_pose_models.py
```

兩者都只檢查 / 下載 / 載入 `yolo11x-pose.pt`。

8. 更新 INDEX / ARCHITECTURE：

```text
10_SYS\02_ACTIVE_DIRECTORY_INDEX.md
10_SYS\04_SYSTEM_ARCHITECTURE.md
```

正式文件已改為：

```text
YOLO Pose 只使用 yolo11x-pose.pt。
本專案只保留正式 YOLO Pose 模式。
```

## 重要決策

1. 本專案不再保留 YOLO fast / light 模式。
2. YOLO Pose 正式模型只使用 `yolo11x-pose.pt`。
3. 模型大檔仍外置於 `D:\30_AI_MODEL`，不放入 Git。
4. 可攜式模型 fallback 仍保留為 `90_MODEL\YOLO_POSE\models`，但目前未放模型檔。
5. `analysis_engine.py` 是共用引擎，不保存分類規則。
6. 分類規則放在各分類自己的 `10_CONFIG`。
7. `10_CONFIG` 是正式規則，模型不能直接覆蓋。
8. 模型建議的新規則先寫入：

```text
20_ANALYSIS_RESULT\config_suggestions
```

9. 每張圖實際產生的 tag 寫入：

```text
50_TAG\auto_tags
```

## 驗證結果

已完成下列驗證：

```text
WebUI build 成功
NVIDIA GPU 可辨識
torch.cuda.is_available() = True
verify_full_env.py 成功
analysis_engine.py --category YOGA --limit 0 成功
核心文字掃描無舊快版 YOLO 殘留
```

目前可執行：

```powershell
.\.venv\Scripts\python.exe .\70_SCRIPT\verify_full_env.py
.\.venv\Scripts\python.exe .\80_APP\ANALYSIS_ENGINE\analysis_engine.py --category YOGA --limit 0
.\70_SCRIPT\Start_ImageLabel_WebUI.bat
.\70_SCRIPT\Run_Yoga_Analysis.bat
```

## 下一步

1. 將 WebUI 的「分析」按鈕接到 `analysis_engine.py`。
2. 建立全域分類流程：`40_ALL_INPUT` 自動分流到四分類 `15_{CATEGORY}_INPUT`。
3. 建立已處理 / 錯誤圖片分流：

```text
16_{CATEGORY}_PROCESSED
17_{CATEGORY}_ERROR
```

4. 清理 `YOGA_POSE_TAGS.json` 的 OCR 雜訊與錯誤體式名。
5. 從 YOGA PDF 抽出姿勢圖片，建立 reference pose index。
6. 實作 DuckDB 寫入，不只建立空 DB。
7. 實作 RAG / vector_index 寫入。
8. 將 Qwen3-VL / Ollama 圖像語意分析接入 pipeline。

## Blockers / 注意

1. NAS 正式根路徑尚未指定為實際 UNC 路徑。
2. 可攜式模型資料夾 `90_MODEL\YOLO_POSE\models` 目前沒有模型檔。
3. 目前實際模型來源是 `D:\30_AI_MODEL\YOLO_POSE\models\yolo11x-pose.pt`。
4. 工作區仍有本次未納入提交的既有 dirty / untracked 檔案，例如 `.gitignore`、部分 storage/script 檔、`.playwright-mcp`、`conversations`、`bash_events`、影片檔。
5. WebUI Gradio 6 會提示 CSS 參數位置警告，目前不影響 build / import。
