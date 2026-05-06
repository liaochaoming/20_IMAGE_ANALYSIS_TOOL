# PROJECT_KNOWLEDGE

STATUS: ACTIVE
SCOPE: IMAGE_ANALYSIS_TOOL PROJECT KNOWLEDGE
LAST_UPDATE: 2026-05-07

## 目的

本文件保存本專案的長期穩定決策，不保存零散 session 對話。

## 穩定決策

1. 本專案定位為圖像分析工具，支援瑜珈、個人照片、人體解剖、室內設計四大分類。
2. YOGA 使用 PDF 與圖片建立標準姿勢標籤庫。
3. 標籤必須跟著主分類走，不可混在同一層。
4. JSON 使用英文 ID，並保留中文欄位或中文 MD 說明。
5. 本機是運算工作區，正式資料未來搬到 NAS。
6. 模型大檔獨立放在 `D:\30_AI_MODEL`。
7. RAG 使用 Chroma，結構化資料使用 DuckDB。
8. `10_CONFIG` 保存可用標籤規則與 pipeline 設定；模型不得直接覆蓋正式 CONFIG。
9. 模型建議的新規則先寫入 `20_ANALYSIS_RESULT\config_suggestions`，人工審核後才可升級到 `10_CONFIG`。
10. `50_TAG\auto_tags` 保存每張圖實際分析出的 TAG JSON。
11. WebUI 讀取人工 CSV 標籤與 `50_TAG\auto_tags`，並在介面用中文顯示自動分析標籤。
12. TAG 檔案維持 JSON 與英文 ID，中文顯示由 WebUI 轉譯，不改 TAG 檔名。
13. YOLO 與 Qwen3-VL 分工不同：YOLO 做快速人體 / 姿勢點偵測，Qwen3-VL 做整張圖語意理解、圖中文字理解、中文摘要、體式推測與標籤建議。
14. Qwen3-VL / Ollama 是慢速深度分析層，單張圖片可能需要約 60-120 秒；不應把它視為即時快速分類工具。
15. 建庫第一次可完整跑 Qwen3-VL；後續圖片若檔案 hash 未變，應優先讀既有 `analysis_json` / `auto_tags` / DuckDB / RAG 結果，避免重複呼叫 Qwen。
16. 建議流程是先用 YOLO 做第一層快速分析，再只對需要語意理解、OCR、體式名稱推測、摘要或標籤建議的圖片啟動 Qwen3-VL。
17. Qwen3-VL 的新標籤或新規則只能輸出到 `20_ANALYSIS_RESULT\config_suggestions`，不得直接改 `10_CONFIG`。

## 已建立資產

- `CATEGORY_SCHEMA.json`：四大主分類。
- `TAG_SCHEMA.json`：依主分類分層的標籤 schema。
- `YOGA_POSE_TAGS.json`：從 Iyengar 瑜珈 PDF 抽出的候選體式標籤。
- `STORAGE_POLICY.json`：本機 / NAS 儲存策略。
- `YOGA_ANALYSIS_PIPELINE.json`：YOGA 分析流程設定。
- `YOGA_TAG_SCHEMA.json`：YOGA 可用標籤規則。
- `50_TAG\auto_tags`：每張圖的自動 TAG 結果。
