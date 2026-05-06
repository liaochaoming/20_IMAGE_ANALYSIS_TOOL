#  AI KINGDOM
> 版本：v2 | 最後更新：2026-05-06

---
建立一套可擴充的本地 AI 王國系統，整合：

* AI 分身
* NAS 記憶庫
* 自動化流程
* 醫學 / 投資 / 知識系統


## 系統名稱

AI 王國（LIAO AI SYSTEM）

---

## 架構概覽

 代號 | IP | CPU | GPU | RAM | 角色 |
|---------|------|----|-----|-----|-----|------|
HOST B（PC_B） | 192.168.0.234 | Core Ultra 7 265K | RTX 5080 16GB | 64GB | 主力 AI / LLM / Embedding |
HOST A（PC_A） | 192.168.0.167 | i7-14700F (20C/28T) | RTX 4060 8GB | 32GB | 控制中心 / Codex / 自動化 |
HOST C（PC_C） | 192.168.0.12 | Core Ultra 7 265K | RTX 5080 16GB | 64GB | 圖像/影片/3D生成 |
HOST D（PC_D） | 192.168.0.102 | i7-14700F (20C/28T) | RTX 4060 8GB | 32GB | RAG / 財務分析 / 輔助運算 |
| MYYNAS | NAS（AI_BRAIN） | 192.168.0.80 | DS1525+ | — | — | 唯一正式資料中心 |

---

## 網路環境

```text
Router：UDM-PRO
Switch：UniFi Switch Aggregation
Backbone：SFP+ 10GbE
Internet：中華電信 1Gbps
```

---

## 系統結構

- 所有 HOST → 連 NAS（I:\）
- AI 系統以 NAS 為中心
- 多主機共享同一份資料
-（HOST B）為 AI 核心節點
-（HOST A）為控制入口與自動化中心

---

---## 五、核心原則（不可違反）

1. HOST 負責算
2. BRAIN 負責存
3. 正式資料只在 NAS（BRAIN）
4. $LOCAL_ROOT 為各主機執行區（D:\AI_HOST 優先；不存在用 C:\AI_HOST）
5. 不同使用者資料不可混用
6. AI_WORK 不存正式資料
7. 向量庫 / 記憶 / 索引只保留一份

  、啟動流程（OPEN）

```text
1. 先讀 00_KINGDOM_SYS.md
2. project-defined EXECUTION_POLICY.md
3. project-defined ACTIVE_DIRECTORY_INDEX
4. project-defined SYSTEM_ARCHITECTURE / BLUEPRINT
5. PROJECT_KNOWLEDGE.md
6. PROJECT_STATUS_CURRENT.md
7. latest TOOL_CONTINUE_CONTENT

## 十六、最重要結論

```text
HOST 產生，NAS 保存，HOST 鏡像備援
SESSION 用來工作，SUMMARY 用來記住
DELTA 記變動，CORE 記結論
AI_KINGDOM 在 $LOCAL_ROOT 做事，AI_BRAIN 在 \\AI-BRAIN-NAS\10_AI_BRAIN 記住
```

---

## 專案可攜式開發標準（引用）

本系統所有專案必須遵循：

PORTABLE_PROJECT_STANDARD.md

核心原則摘要：

- 禁止使用絕對路徑（I:\ / D:\ / C:\）
- 所有路徑必須相對於專案根目錄
- 專案必須可打包（zip）並跨主機運行
- 必須提供 install.ps1 進行初始化
- results / logs 為執行產物，不得隨專案分發
- 必須使用 VERSION 管理版本與 migration

此為全域強制規則，所有專案必須遵守。


```

---
