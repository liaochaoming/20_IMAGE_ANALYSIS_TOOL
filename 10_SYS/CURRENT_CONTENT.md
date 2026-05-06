# CURRENT_CONTENT

STATUS: YOGA_V2_FULL_FLOW_READY
SCOPE: IMAGE_ANALYSIS_TOOL / YOGA FULL MODEL ANALYSIS FLOW V2
LAST_UPDATE: 2026-05-07 04:43

## Current Result

YOGA V2 主流程已跑通，不是只有架構。

已接上：

```text
YOLO Pose
Qwen3-VL / Ollama
DuckDB
RAG / vector_index
50_TAG\auto_tags
20_ANALYSIS_RESULT\analysis_json
WebUI 分析按鈕
快取機制
```

## How To Use

放圖片：

```text
D:\20_IMAGE_ANALYSIS_TOOL\30_CATALOG\YOGA\15_YOGA_INPUT
```

批次分析：

```text
D:\20_IMAGE_ANALYSIS_TOOL\70_SCRIPT\Run_Yoga_Analysis.bat
```

WebUI：

```text
D:\20_IMAGE_ANALYSIS_TOOL\70_SCRIPT\Start_ImageLabel_WebUI.bat
http://127.0.0.1:7860
```

在 WebUI 按「分析」後會呼叫：

```text
D:\20_IMAGE_ANALYSIS_TOOL\80_APP\ANALYSIS_ENGINE\analysis_engine.py --category YOGA
```

## Output

完整分析 JSON：

```text
D:\20_IMAGE_ANALYSIS_TOOL\30_CATALOG\YOGA\20_ANALYSIS_RESULT\analysis_json
```

每張圖 TAG：

```text
D:\20_IMAGE_ANALYSIS_TOOL\30_CATALOG\YOGA\50_TAG\auto_tags
```

DuckDB：

```text
D:\20_IMAGE_ANALYSIS_TOOL\30_CATALOG\YOGA\30_DB\image_index.duckdb
```

RAG：

```text
D:\20_IMAGE_ANALYSIS_TOOL\30_CATALOG\YOGA\40_RAG\vector_index
```

模型建議規則：

```text
D:\20_IMAGE_ANALYSIS_TOOL\30_CATALOG\YOGA\20_ANALYSIS_RESULT\config_suggestions
```

## Active Pipeline

正式設定：

```text
D:\20_IMAGE_ANALYSIS_TOOL\30_CATALOG\YOGA\10_CONFIG\YOGA_ANALYSIS_PIPELINE.json
```

目前啟用：

```text
yolo_pose: true
vision_llm: true
duckdb: true
rag: true
auto_tag: true
config_suggestions: true
reuse_existing_analysis: true
force_reanalyze: false
```

## Model Rule

YOLO 負責：

```text
快速人體偵測
姿勢點偵測
人數判斷
姿勢信心
```

Qwen3-VL / Ollama 負責：

```text
圖像語意理解
圖片中文字理解
中文摘要
體式推測
標籤建議
```

Qwen3-VL 是慢速深度分析層。`qwen3-vl:32b` 在目前機器上會 CPU/GPU 混跑，第一次分析新圖可能較慢。

## Cache Rule

圖片 `file_hash` 沒變時：

```text
不重新呼叫 Qwen3-VL
不重新載入 YOLO
直接讀既有 analysis_json / auto_tags
更新 DuckDB / RAG 索引
```

實測：

```text
4 張新圖完整分析：約 297 秒
同圖快取重跑：約 0.56 秒
```

## Config Safety

`10_CONFIG` 是正式規則。

Qwen 發現的新標籤 / 新規則只能寫入：

```text
20_ANALYSIS_RESULT\config_suggestions
```

人工確認後才可升級到：

```text
30_CATALOG\YOGA\10_CONFIG
```

## Git Ignore Policy

不得加入 Git：

```text
.venv
30_CATALOG\**\00_DATA
30_CATALOG\**\15_*_INPUT
30_CATALOG\**\20_ANALYSIS_RESULT
30_CATALOG\**\30_DB
30_CATALOG\**\40_RAG
30_CATALOG\**\50_TAG\auto_tags
40_ALL_INPUT
99_LOG
*.lnk
*.pt
*.onnx
*.safetensors
```

## Next Work

下一步建議：

```text
1. 建立 config_suggestions 審核 WebUI
2. 建立 40_ALL_INPUT 自動分類到四分類入口
3. 讓 Qwen 模型可切換 fast / deep 模式
4. 針對中文摘要品質調整 prompt
5. 將其他分類接上同一套 V2 流程
```
