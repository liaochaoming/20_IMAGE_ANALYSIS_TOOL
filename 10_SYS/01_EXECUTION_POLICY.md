# EXECUTION_POLICY

STATUS: ACTIVE
SCOPE: IMAGE_ANALYSIS_TOOL EXECUTION POLICY
LAST_UPDATE: 2026-05-07

## 目的

本文件定義本專案的最高執行規則，作為讀取 `00_KINGDOM_SYS.md` 後的第一份專案規則。

## 核心規則

1. HOST_B 負責運算，NAS / AI_BRAIN 負責正式保存。
2. 本機 `D:\20_IMAGE_ANALYSIS_TOOL` 是工作區，不是最終資料中心。
3. 未來正式 `30_CATALOG` 內的 `00_DATA / 20_ANALYSIS_RESULT / 30_DB / 40_RAG / 50_TAG` 搬到 NAS。
4. 程式不得硬寫死 `D:\` 或 `I:\`，必須讀取 `STORAGE_POLICY.json` 或環境變數。
5. 模型大檔放 `D:\30_AI_MODEL`，不放入本專案可攜式資料包。
6. 主分類與標籤必須分層管理，不可混在同一層。
7. JSON 保留英文 ID，必須保留中文欄位或中文 MD 供人工參考。
8. 工具產生的檔案與內文必須寫回原專案目錄 `D:\20_IMAGE_ANALYSIS_TOOL` 對應位置，不得寫到 `C:\Users\USER`、`C:\Users\USER\Documents` 或臨時工作目錄。
9. 若 Codex / WebUI / 腳本從其他目錄啟動，仍必須以專案根目錄 `D:\20_IMAGE_ANALYSIS_TOOL` 作為正式寫入根目錄。

## 不適用範圍

本文件不定義模型訓練細節、不定義外部 NAS 實際掛載流程。

