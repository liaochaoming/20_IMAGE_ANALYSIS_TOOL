# PROJECT_STATUS_CURRENT

STATUS: ACTIVE
SCOPE: IMAGE_ANALYSIS_TOOL PROJECT STATUS
LAST_UPDATE: 2026-05-07

## 目的

本文件描述本專案目前狀態、下一步與阻塞點。此檔可覆蓋更新。

## 目前狀態

```text
專案根目錄：D:\20_IMAGE_ANALYSIS_TOOL
命名規則：已依 NAME_POLICY.MD 改為數字前綴 + 英文大寫
主分類：YOGA / LIAO_PHOTO / ANATOMY / INTERIOR_DESIGN
標籤架構：已改為跟著主分類分層
儲存策略：已定義本機工作區與未來 NAS 正式資料路徑
瑜珈 PDF 標籤庫：已抽出第一版 257 個候選標籤
資料夾整合：舊獨立 Asset Manager 專案已收斂進 D:\20_IMAGE_ANALYSIS_TOOL，舊資料夾已刪除
主資料結構：已改為 30_CATALOG\{CATEGORY}\00_DATA / 10_CONFIG / 15_{CATEGORY}_INPUT / 20_ANALYSIS_RESULT / 30_DB / 40_RAG / 50_TAG / 90_DOC
Asset Manager WebUI：已移至 80_APP\ASSET_MANAGER_WEBUI
全域未分類入口：已建立 40_ALL_INPUT
分類分析入口：已建立 15_ANATOMY_INPUT / 15_INTERIOR_DESIGN_INPUT / 15_LIAO_PHOTO_INPUT / 15_YOGA_INPUT
YOGA DATA：已整理為 10_RAW_PDF / 20_RAW_IMAGE / 30_REFERENCE_POSE
```

## 下一步

1. 清理 `YOGA_POSE_TAGS.json` 的 OCR 雜訊與錯誤體式名。
2. 從 PDF 抽出姿勢圖片，建立 reference pose index。
3. 建立 DuckDB schema。
4. 建立 Chroma RAG 索引。
5. 建立 analysis_engine.analyze_image(image_path, category)。
6. 將 WebUI 的「分析」按鈕接到 Analysis Engine。

## Blockers

- PDF 圖像抽取尚未完成。
- YOGA 標籤仍需要人工校正第一版。
- NAS 正式根路徑尚未指定為實際 UNC 或 I 槽路徑。


