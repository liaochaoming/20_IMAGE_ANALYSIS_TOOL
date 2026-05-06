# ASSET_MANAGER_README

STATUS: YOGA_V2_READY
SCOPE: IMAGE_ANALYSIS_TOOL ASSET_MANAGER_WEBUI
LAST_UPDATE: 2026-05-07

## 目的

本文件說明 Asset Manager WebUI 已整合進 `D:\20_IMAGE_ANALYSIS_TOOL`，不再使用獨立專案。

## 正式位置

```text
D:\20_IMAGE_ANALYSIS_TOOL\80_APP\ASSET_MANAGER_WEBUI
```

## 啟動

```powershell
D:\20_IMAGE_ANALYSIS_TOOL\70_SCRIPT\Start_ImageLabel_WebUI.bat
```

URL：

```text
http://127.0.0.1:7860
```

## 主要路徑

```text
程式：D:\20_IMAGE_ANALYSIS_TOOL\80_APP\ASSET_MANAGER_WEBUI\image_label_webui.py
設定：D:\20_IMAGE_ANALYSIS_TOOL\80_APP\ASSET_MANAGER_WEBUI\00_CONFIG
待分析入口：D:\20_IMAGE_ANALYSIS_TOOL\40_ALL_INPUT
YOGA 分析入口：D:\20_IMAGE_ANALYSIS_TOOL\30_CATALOG\YOGA\15_YOGA_INPUT
YOGA 原始 PDF：D:\20_IMAGE_ANALYSIS_TOOL\30_CATALOG\YOGA\00_DATA\10_RAW_PDF
YOGA 原始圖片：D:\20_IMAGE_ANALYSIS_TOOL\30_CATALOG\YOGA\00_DATA\20_RAW_IMAGE
YOGA 參考姿勢：D:\20_IMAGE_ANALYSIS_TOOL\30_CATALOG\YOGA\00_DATA\30_REFERENCE_POSE
YOGA 輸出：D:\20_IMAGE_ANALYSIS_TOOL\30_CATALOG\YOGA\20_ANALYSIS_RESULT
LOG：D:\20_IMAGE_ANALYSIS_TOOL\99_LOG\ASSET_MANAGER
```

## YOGA 分析按鈕

WebUI 內的「分析」按鈕會執行：

```text
D:\20_IMAGE_ANALYSIS_TOOL\80_APP\ANALYSIS_ENGINE\analysis_engine.py --category YOGA
```

並讀取結果：

```text
D:\20_IMAGE_ANALYSIS_TOOL\30_CATALOG\YOGA\50_TAG\auto_tags
```

右側「自動分析標籤」會以中文顯示：

```text
YOLO 人數 / 姿勢信心
Qwen 中文摘要
Qwen 體式推測
自動 TAG
asset_id
```

## V2 已接通模型

```text
YOLO Pose：人體 / 姿勢點偵測
Qwen3-VL / Ollama：圖像語意理解 / 中文摘要 / 標籤建議
DuckDB：image_index.duckdb
RAG：40_RAG\vector_index
```

圖片 hash 未變時會使用快取，不重跑 Qwen。

## 資料規則

- `40_ALL_INPUT`：全專案臨時匯入、待分析、未分類資料。
- `10_RAW_PDF`：已決定長期保存的正式原始 PDF。
- `20_RAW_IMAGE`：已決定長期保存的正式原始圖片。
- `30_REFERENCE_POSE`：已人工確認、可作為標準答案的瑜珈姿勢圖。
- `20_ANALYSIS_RESULT`：分析後結果，不放原始素材。
- `50_TAG\auto_tags`：WebUI 讀取自動標籤並以中文顯示。
