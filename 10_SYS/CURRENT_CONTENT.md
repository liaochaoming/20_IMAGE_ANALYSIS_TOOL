# CURRENT_CONTENT

STATUS: YOGA_V1_READY
SCOPE: IMAGE_ANALYSIS_TOOL / YOGA ANALYSIS FLOW V1
LAST_UPDATE: 2026-05-07

## Goal

完成 `IMAGE_ANALYSIS_TOOL` 的 YOGA 分析流程第一版。

本次範圍只針對：

```text
D:\20_IMAGE_ANALYSIS_TOOL
```

允許修改範圍：

```text
10_SYS
20_CONFIG
30_CATALOG\YOGA\10_CONFIG
70_SCRIPT
80_APP
90_DOC
```

## Current Architecture

YOGA 分析流程目前以共用 Engine 執行，分類規則由 CATALOG 內的 CONFIG 決定。

```text
30_CATALOG\YOGA\00_DATA
```

放來源資料，用來建立圖文標準與規則參考。

```text
30_CATALOG\YOGA\10_CONFIG
```

放正式規則與 pipeline。模型不得直接覆蓋這裡。

```text
30_CATALOG\YOGA\15_YOGA_INPUT
```

放要分析的 YOGA 圖片。

```text
30_CATALOG\YOGA\20_ANALYSIS_RESULT
```

放分析 JSON、config_suggestions 等分析結果。

```text
30_CATALOG\YOGA\50_TAG\auto_tags
```

放每張圖實際產生的標籤 JSON。

## Executable Flow

正式 Engine：

```text
80_APP\ANALYSIS_ENGINE\analysis_engine.py
```

YOGA 批次入口：

```text
70_SCRIPT\Run_Yoga_Analysis.bat
```

WebUI：

```text
80_APP\ASSET_MANAGER_WEBUI\image_label_webui.py
```

WebUI 設定：

```text
80_APP\ASSET_MANAGER_WEBUI\00_CONFIG\paths.json
```

## Model / Package Rule

Engine 本體共用，不把分類規則寫死在程式裡。

YOGA 執行時讀取：

```text
30_CATALOG\YOGA\10_CONFIG\YOGA_ANALYSIS_PIPELINE.json
30_CATALOG\YOGA\10_CONFIG\YOGA_TAG_SCHEMA.json
```

目前 YOLO Pose 正式模型路徑：

```text
D:\30_AI_MODEL\YOLO_POSE\models\yolo11x-pose.pt
```

模型大檔外置，不放入 Git。

## Config Rule

`10_CONFIG` 只放正式規則。

模型分析後如發現新規則、新標籤、新分類建議，只能先寫入：

```text
30_CATALOG\YOGA\20_ANALYSIS_RESULT\config_suggestions
```

人工確認後，才可升級寫入：

```text
30_CATALOG\YOGA\10_CONFIG
```

## TAG Rule

`50_TAG` 是每張圖實際分析後的標籤結果。

WebUI 讀取：

```text
30_CATALOG\YOGA\50_TAG\auto_tags
```

並以中文顯示自動標籤，例如：

```text
狀態：已分析
來源：使用者上傳
畫面：單人、視角待確認
姿勢：姿勢待確認
品質：清楚
```

TAG JSON 內仍保留穩定英文 ID，中文顯示由 WebUI 對照轉譯。

## Verification

2026-05-07 已完成驗證：

```text
analysis_engine.py --category YOGA --limit 0 成功
Run_Yoga_Analysis.bat 成功啟動並完成 YOGA 分析
WebUI 使用專案 .venv 可 import
WebUI 可讀 50_TAG\auto_tags
WebUI auto tag 中文顯示函式正常
JSON 全部可解析
```

本次 BAT 實測結果：

```text
category_id: YOGA
input_dir: D:\20_IMAGE_ANALYSIS_TOOL\30_CATALOG\YOGA\15_YOGA_INPUT
image_count: 7
analyzed_count: 7
status: done
```

## Git / Ignore Policy

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

下一階段建議：

```text
1. 將 WebUI 的分析按鈕直接接 analysis_engine.py
2. 建立 40_ALL_INPUT 自動分流到四分類入口
3. 實作 DuckDB image_index 寫入
4. 實作 RAG vector_index 寫入
5. 接入 Qwen3-VL / Ollama 圖像語意分析
```

## Stop Rules

後續工作如遇以下情況需停止並回報：

```text
需要刪除 00_DATA
需要新增大型模型或大型資料進 Git
測試連續失敗超過 3 次
需要改動 D:\30_AI_MODEL
```
