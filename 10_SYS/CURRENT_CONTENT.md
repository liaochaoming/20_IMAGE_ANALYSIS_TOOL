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
D:\20_IMAGE_ANALYSIS_TOOL\10_SYS\02_ACTIVE_DIRECTORY_INDEX.md
```

核心架構檔：

```text
D:\20_IMAGE_ANALYSIS_TOOL\10_SYS\04_SYSTEM_ARCHITECTURE.md
```

長期決策檔：

```text
D:\20_IMAGE_ANALYSIS_TOOL\10_SYS\05_PROJECT_KNOWLEDGE.md
```

目前狀態檔：

```text
D:\20_IMAGE_ANALYSIS_TOOL\10_SYS\06_PROJECT_STATUS_CURRENT.md
```

## 本次完成

1. 統一四大分類資料夾架構：

```text
00_DATA
10_CONFIG
15_{CATEGORY}_INPUT
20_ANALYSIS_RESULT
30_DB
40_RAG
50_TAG
90_DOC
```

2. 將舊命名同步替換：

```text
40_INPUT -> 40_ALL_INPUT
00_CONFIG / 10_DATA -> 10_CONFIG / 00_DATA
20_OUTPUT -> 20_ANALYSIS_RESULT
70_SCRIPT\ASSET_MANAGER -> 70_SCRIPT
```

3. 建立共用分析引擎：

```text
D:\20_IMAGE_ANALYSIS_TOOL\80_APP\ANALYSIS_ENGINE\analysis_engine.py
```

4. 建立 YOGA 批次分析入口：

```text
D:\20_IMAGE_ANALYSIS_TOOL\70_SCRIPT\Run_Yoga_Analysis.bat
```

5. 建立四分類 Pipeline / Tag Schema：

```text
30_CATALOG\YOGA\10_CONFIG\YOGA_ANALYSIS_PIPELINE.json
30_CATALOG\YOGA\10_CONFIG\YOGA_TAG_SCHEMA.json
30_CATALOG\ANATOMY\10_CONFIG\ANATOMY_ANALYSIS_PIPELINE.json
30_CATALOG\ANATOMY\10_CONFIG\ANATOMY_TAG_SCHEMA.json
30_CATALOG\INTERIOR_DESIGN\10_CONFIG\INTERIOR_DESIGN_ANALYSIS_PIPELINE.json
30_CATALOG\INTERIOR_DESIGN\10_CONFIG\INTERIOR_DESIGN_TAG_SCHEMA.json
30_CATALOG\LIAO_PHOTO\10_CONFIG\LIAO_PHOTO_ANALYSIS_PIPELINE.json
30_CATALOG\LIAO_PHOTO\10_CONFIG\LIAO_PHOTO_TAG_SCHEMA.json
```

6. 建立四分類 DuckDB 初始檔：

```text
30_CATALOG\{CATEGORY}\30_DB\image_index.duckdb
```

7. WebUI 已改為讀取 YOGA 分析入口：

```text
D:\20_IMAGE_ANALYSIS_TOOL\30_CATALOG\YOGA\15_YOGA_INPUT
```

8. WebUI 已接入自動 TAG：

```text
D:\20_IMAGE_ANALYSIS_TOOL\30_CATALOG\YOGA\50_TAG\auto_tags
```

右側新增「自動分析標籤」，並把英文 tag 轉為中文顯示。TAG JSON 檔案仍維持英文 ID。

9. 建立根目錄中文捷徑：

```text
D:\20_IMAGE_ANALYSIS_TOOL\YOGA圖片放這裡.lnk
D:\20_IMAGE_ANALYSIS_TOOL\執行YOGA批次分析.lnk
```

10. 已更新架構與索引：

```text
D:\20_IMAGE_ANALYSIS_TOOL\10_SYS\04_SYSTEM_ARCHITECTURE.md
D:\20_IMAGE_ANALYSIS_TOOL\10_SYS\05_PROJECT_KNOWLEDGE.md
D:\20_IMAGE_ANALYSIS_TOOL\10_SYS\06_PROJECT_STATUS_CURRENT.md
D:\20_IMAGE_ANALYSIS_TOOL\10_SYS\02_ACTIVE_DIRECTORY_INDEX.md
D:\20_IMAGE_ANALYSIS_TOOL\DIR_INDEX.md
D:\20_IMAGE_ANALYSIS_TOOL\90_DOC\PROJECT_DIR_INDEX.md
D:\20_IMAGE_ANALYSIS_TOOL\90_DOC\ASSET_MANAGER_README.md
```

## 重要決策

1. `analysis_engine.py` 是共用引擎，不保存分類規則。
2. 分類規則放在各分類自己的 `10_CONFIG`。
3. `10_CONFIG` 是正式規則，模型不能直接覆蓋。
4. 模型建議的新規則先寫入：

```text
20_ANALYSIS_RESULT\config_suggestions
```

5. 每張圖實際產生的 tag 寫入：

```text
50_TAG\auto_tags
```

6. `20_ANALYSIS_RESULT` 是分析結果，不放原始圖片。
7. 原始待分析圖片仍留在：

```text
15_{CATEGORY}_INPUT
```

如需分流已處理圖片，後續可新增：

```text
16_{CATEGORY}_PROCESSED
17_{CATEGORY}_ERROR
```

## 驗證結果

已完成下列驗證：

```text
JSON 全部可解析
JSON 內 D:\ 路徑全部存在
Python 可編譯
四分類 analysis_engine --limit 0 空跑成功
WebUI import 成功
WebUI build 成功
YOGA 中文捷徑目標存在
舊 20_OUTPUT / 40_INPUT / YOGA\10_DATA / YOGA\00_CONFIG 無殘留
```

目前可執行：

```powershell
D:\20_IMAGE_ANALYSIS_TOOL\.venv\Scripts\python.exe D:\20_IMAGE_ANALYSIS_TOOL\80_APP\ANALYSIS_ENGINE\analysis_engine.py --category YOGA
D:\20_IMAGE_ANALYSIS_TOOL\.venv\Scripts\python.exe D:\20_IMAGE_ANALYSIS_TOOL\80_APP\ANALYSIS_ENGINE\analysis_engine.py --category ANATOMY
D:\20_IMAGE_ANALYSIS_TOOL\.venv\Scripts\python.exe D:\20_IMAGE_ANALYSIS_TOOL\80_APP\ANALYSIS_ENGINE\analysis_engine.py --category INTERIOR_DESIGN
D:\20_IMAGE_ANALYSIS_TOOL\.venv\Scripts\python.exe D:\20_IMAGE_ANALYSIS_TOOL\80_APP\ANALYSIS_ENGINE\analysis_engine.py --category LIAO_PHOTO
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

1. `D:\20_IMAGE_ANALYSIS_TOOL` 目前不是 Git repository。
2. 因為不是 Git repository，本次無法依收工流程 commit / push。
3. NAS 正式根路徑尚未指定為實際 UNC 或 I 槽路徑。
4. `analysis_engine.py` 目前 YOGA 會啟動 YOLO Pose；其他分類目前採安全預設，不啟動 YOLO / LLM，只做最小可跑流程。
5. WebUI Gradio 6 會提示 CSS 參數位置警告，但目前不影響 build / import。
