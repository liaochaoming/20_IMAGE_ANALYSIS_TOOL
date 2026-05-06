# IMAGE_ANALYSIS_STORAGE_POLICY

STATUS: ACTIVE
SCOPE: IMAGE_ANALYSIS_TOOL STORAGE / NAS MIGRATION / INPUT_OUTPUT_POLICY
LAST_UPDATE: 2026-05-07

## 目的

本文件定義圖像分析工具的本機與 NAS 儲存分工，符合 `00_KINGDOM_SYS.md` 的核心原則：HOST 負責算，BRAIN/NAS 負責存。

## 現在

```text
D:\20_IMAGE_ANALYSIS_TOOL
├─ 20_CONFIG
├─ 30_CATALOG       分類目錄工作區
├─ 40_ALL_INPUT     全域未分類入口
├─ 70_SCRIPT
├─ 80_APP
├─ 90_DOC
└─ 99_LOG
```

## 分類目錄內部結構

```text
30_CATALOG\{CATEGORY}
├─ 00_DATA          來源標準資料 / 參考資料
├─ 10_CONFIG        分類規則 / 標籤規則 / 圖名對照
├─ 15_{CATEGORY}_INPUT  分類後正式分析入口
├─ 20_ANALYSIS_RESULT        分析輸出
├─ 30_DB            DuckDB / SQLite 結構化資料
├─ 40_RAG           Chroma / Embedding / RAG 索引
├─ 50_TAG           標籤產物
└─ 90_DOC           分類文件
```

## YOGA DATA 規則

```text
30_CATALOG\YOGA\00_DATA\10_RAW_PDF         正式原始 PDF
30_CATALOG\YOGA\00_DATA\20_RAW_IMAGE       正式原始圖片
30_CATALOG\YOGA\00_DATA\30_REFERENCE_POSE  標準參考姿勢圖
30_CATALOG\YOGA\15_YOGA_INPUT                  已確認 YOGA 待分析圖片
40_ALL_INPUT                                   全域未分類入口
```

## 將來搬到 NAS

正式資料未來應放在：

```text
${NAS_AI_BRAIN_ROOT}\20_IMAGE_ANALYSIS_TOOL\30_CATALOG
${NAS_AI_BRAIN_ROOT}\20_IMAGE_ANALYSIS_TOOL\40_ALL_INPUT
```

## 分工

```text
HOST_B：YOLO / MediaPipe / Qwen / Embedding 運算
NAS：30_CATALOG / 40_ALL_INPUT 正式保存
本機 D 槽：快取、工作區、模型推論暫存
```

## 規則

- `40_ALL_INPUT` 是全域未分類入口，不是分析輸出區。
- `30_CATALOG\{CATEGORY}\10_CONFIG` 是分類目錄自己的設定位置。
- `30_CATALOG\{CATEGORY}\00_DATA` 是來源標準資料與參考資料。
- `30_CATALOG\{CATEGORY}\15_{CATEGORY}_INPUT` 是分類後正式分析入口。
- `30_CATALOG\{CATEGORY}\20_ANALYSIS_RESULT` 是分析後結果。
- 程式要讀 `STORAGE_POLICY.json`，不要硬寫死 `D:\` 或 `I:\`。
- 模型大檔仍放 `D:\30_AI_MODEL`，不放進可攜式專案包。


