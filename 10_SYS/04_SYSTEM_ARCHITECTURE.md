# SYSTEM_ARCHITECTURE

STATUS: ACTIVE
SCOPE: IMAGE_ANALYSIS_TOOL SYSTEM ARCHITECTURE
LAST_UPDATE: 2026-05-07

## 目的

本文件定義圖片分析工具的正式系統架構：資料入口、分類流程、來源標準、分析模型、WebUI 視窗、OUTPUT / DB / RAG / TAG 的分工。

## 核心原則

```text
HOST 負責運算
NAS 負責正式保存
D:\20_IMAGE_ANALYSIS_TOOL 是 HOST 本機工作鏡像與分析工廠
D:\30_AI_MODEL 是模型倉庫
40_ALL_INPUT 是全域未分類入口
30_CATALOG\{CATEGORY}\00_DATA 是來源標準資料
30_CATALOG\{CATEGORY}\10_CONFIG 是分類規則與標籤規則
30_CATALOG\{CATEGORY}\15_{CATEGORY}_INPUT 是分類後分析入口
```

## 四大分類

```text
ANATOMY
INTERIOR_DESIGN
LIAO_PHOTO
YOGA
```

## 正式目錄結構

```text
D:\20_IMAGE_ANALYSIS_TOOL
├─ 10_SYS
├─ 20_CONFIG
├─ 30_CATALOG
│  ├─ ANATOMY
│  │  ├─ 00_DATA
│  │  ├─ 10_CONFIG
│  │  ├─ 15_ANATOMY_INPUT
│  │  ├─ 20_ANALYSIS_RESULT
│  │  ├─ 30_DB
│  │  ├─ 40_RAG
│  │  ├─ 50_TAG
│  │  └─ 90_DOC
│  ├─ INTERIOR_DESIGN
│  │  ├─ 00_DATA
│  │  ├─ 10_CONFIG
│  │  ├─ 15_INTERIOR_DESIGN_INPUT
│  │  ├─ 20_ANALYSIS_RESULT
│  │  ├─ 30_DB
│  │  ├─ 40_RAG
│  │  ├─ 50_TAG
│  │  └─ 90_DOC
│  ├─ LIAO_PHOTO
│  │  ├─ 00_DATA
│  │  ├─ 10_CONFIG
│  │  ├─ 15_LIAO_PHOTO_INPUT
│  │  ├─ 20_ANALYSIS_RESULT
│  │  ├─ 30_DB
│  │  ├─ 40_RAG
│  │  ├─ 50_TAG
│  │  └─ 90_DOC
│  └─ YOGA
│     ├─ 00_DATA
│     ├─ 10_CONFIG
│     ├─ 15_YOGA_INPUT
│     ├─ 20_ANALYSIS_RESULT
│     ├─ 30_DB
│     ├─ 40_RAG
│     ├─ 50_TAG
│     └─ 90_DOC
├─ 40_ALL_INPUT
├─ 70_SCRIPT
├─ 80_APP
│  ├─ ANALYSIS_ENGINE
│  └─ ASSET_MANAGER_WEBUI
├─ 90_DOC
└─ 99_LOG
```

## 入口分工

```text
40_ALL_INPUT
= 全域未分類入口
= 使用者雜亂上傳圖片先放這裡
= 系統先判斷分類
```

```text
30_CATALOG\{CATEGORY}\00_DATA
= 來源資料 / 標準資料
= PDF、參考圖、圖文標準來源
= 不作為一般待分析圖片入口
```

```text
30_CATALOG\{CATEGORY}\10_CONFIG
= 分類規則
= 標籤規則
= 圖名對照
= 來源圖文標準產生的規則
```

```text
30_CATALOG\{CATEGORY}\15_{CATEGORY}_INPUT
= 已確認屬於該分類的正式分析入口
= analysis_engine 的主要輸入來源
```

## WebUI 視窗

WebUI 必須分成兩層。

```text
A. 全域分類視窗

40_ALL_INPUT
↓
自動或人工判斷分類
↓
ANATOMY / INTERIOR_DESIGN / LIAO_PHOTO / YOGA
↓
移入對應 15_{CATEGORY}_INPUT
```

```text
B. 分類分析視窗

00_DATA      來源標準視窗
10_CONFIG    規則標籤視窗
15_INPUT     待分析圖片視窗
20_ANALYSIS_RESULT    分析結果視窗
50_TAG       自動標籤視窗
```

## YOGA 範例

```text
來源標準：
D:\20_IMAGE_ANALYSIS_TOOL\30_CATALOG\YOGA\00_DATA

規則設定：
D:\20_IMAGE_ANALYSIS_TOOL\30_CATALOG\YOGA\10_CONFIG

YOGA 分析入口：
D:\20_IMAGE_ANALYSIS_TOOL\30_CATALOG\YOGA\15_YOGA_INPUT

分析輸出：
D:\20_IMAGE_ANALYSIS_TOOL\30_CATALOG\YOGA\20_ANALYSIS_RESULT
D:\20_IMAGE_ANALYSIS_TOOL\30_CATALOG\YOGA\30_DB
D:\20_IMAGE_ANALYSIS_TOOL\30_CATALOG\YOGA\40_RAG
D:\20_IMAGE_ANALYSIS_TOOL\30_CATALOG\YOGA\50_TAG
```

## 分析流程

```text
使用者上傳圖片
↓
40_ALL_INPUT
↓
分類判斷
↓
30_CATALOG\{CATEGORY}\15_{CATEGORY}_INPUT
↓
WebUI 按「分析」
↓
analysis_engine.analyze_image(image_path, category)
↓
產生：
20_ANALYSIS_RESULT\analysis_json
30_DB\image_index.duckdb
40_RAG\vector_index
50_TAG\auto_tags
↓
WebUI 讀結果顯示
```

無 WebUI 批次流程：

```text
圖片放入 30_CATALOG\YOGA\15_YOGA_INPUT
↓
執行 70_SCRIPT\Run_Yoga_Analysis.bat
↓
呼叫 80_APP\ANALYSIS_ENGINE\analysis_engine.py --category YOGA
↓
讀取 30_CATALOG\YOGA\10_CONFIG\YOGA_ANALYSIS_PIPELINE.json
↓
讀取 30_CATALOG\YOGA\10_CONFIG\YOGA_TAG_SCHEMA.json
↓
產生 20_ANALYSIS_RESULT\analysis_json 與 50_TAG\auto_tags
```

## CONFIG 產生與審核原則

模型可以輔助建立 CONFIG，但不能直接覆蓋正式 CONFIG。

正式規則分工如下：

```text
10_CONFIG
= 正式規則
= 人工確認後才可寫入
= 分類規則 / 標籤規則 / 圖名對照 / 分析 pipeline 設定
```

```text
20_ANALYSIS_RESULT\config_suggestions
= 模型建議的新規則
= 新標籤建議
= 常見錯誤修正建議
= 待人工審核
```

```text
50_TAG
= 每張圖實際分析出的標籤結果
= 不等於正式規則
= 可作為未來修正 CONFIG 的 evidence
```

正式流程：

```text
模型分析圖片
↓
產生 50_TAG\auto_tags
↓
發現不確定 / 常錯 / 新標籤
↓
寫入 20_ANALYSIS_RESULT\config_suggestions
↓
人工審核
↓
通過後才升級到 10_CONFIG
```

禁止流程：

```text
模型直接修改 10_CONFIG
模型直接覆蓋 YOGA_TAG_SCHEMA.json
模型把單張圖的臨時判斷直接變成正式規則
```

## 分析模型與套件

```text
YOLO Pose
= 使用 yolo11x-pose.pt
= 人體偵測 / 姿勢點 / 多人分析
= 本專案只保留正式 YOLO Pose 模式

MediaPipe
= pose landmark / 人體關節點

Qwen3-VL via Ollama
= 圖像語意理解 / 圖文摘要 / 分類理由

DuckDB
= 結構化索引 / 查詢 / 報表

Chroma 或等效向量庫
= Embedding / RAG / 語意搜尋
```

## 輸出契約

每張被分析圖片至少要產生：

```text
asset_id
source_path
category_id
file_hash
analysis_status
auto_tags
pose_result
vision_summary
embedding_id
last_analyzed_at
```

寫入位置：

```text
20_ANALYSIS_RESULT\analysis_json
30_DB\image_index.duckdb
40_RAG\vector_index
50_TAG\auto_tags
```

## 執行入口

```text
環境啟動：
D:\20_IMAGE_ANALYSIS_TOOL\70_SCRIPT\Start_ImageAnalysis_Env.bat

YOGA 批次分析：
D:\20_IMAGE_ANALYSIS_TOOL\70_SCRIPT\Run_Yoga_Analysis.bat

共用分析引擎：
D:\20_IMAGE_ANALYSIS_TOOL\80_APP\ANALYSIS_ENGINE\analysis_engine.py

WebUI 啟動：
D:\20_IMAGE_ANALYSIS_TOOL\70_SCRIPT\Start_ImageLabel_WebUI.bat

WebUI 主程式：
D:\20_IMAGE_ANALYSIS_TOOL\80_APP\ASSET_MANAGER_WEBUI\image_label_webui.py

WebUI TAG 讀取：
D:\20_IMAGE_ANALYSIS_TOOL\30_CATALOG\YOGA\50_TAG\auto_tags
= 右側「自動分析標籤」以中文顯示

環境驗證：
D:\20_IMAGE_ANALYSIS_TOOL\70_SCRIPT\verify_full_env.py
```

## YOGA 正式設定檔

```text
Pipeline 設定：
D:\20_IMAGE_ANALYSIS_TOOL\30_CATALOG\YOGA\10_CONFIG\YOGA_ANALYSIS_PIPELINE.json

正式 YOLO Pose 模型：
D:\30_AI_MODEL\YOLO_POSE\models\yolo11x-pose.pt

Tag Schema：
D:\20_IMAGE_ANALYSIS_TOOL\30_CATALOG\YOGA\10_CONFIG\YOGA_TAG_SCHEMA.json

既有姿勢標籤庫：
D:\20_IMAGE_ANALYSIS_TOOL\30_CATALOG\YOGA\10_CONFIG\YOGA_POSE_TAGS.json
```

## 長期同步

```text
HOST 本機分析
↓
OUTPUT / DB / RAG / TAG 寫入 D:\20_IMAGE_ANALYSIS_TOOL
↓
成熟後同步到 NAS / AI_BRAIN / I:\20_IMAGE_ANALYSIS_TOOL
```
