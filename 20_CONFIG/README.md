# CONFIG 目錄

STATUS: ACTIVE
SCOPE: IMAGE_ANALYSIS_TOOL GLOBAL CONFIG DIRECTORY INDEX
LAST_UPDATE: 2026-05-06

## 目的

本文件說明 `D:\20_IMAGE_ANALYSIS_TOOL\20_CONFIG` 的用途。

`20_CONFIG` 只保存全系統共用 schema 與政策；分類專案自己的 config 必須放在各自專案下。

## 結構

```text
20_CONFIG
└─ 10_SCHEMA
```

## 說明

- `10_SCHEMA`：全系統主分類、標籤規格、儲存策略。

## 分類目錄設定位置

```text
30_CATALOG\YOGA\10_CONFIG
30_CATALOG\LIAO_PHOTO\10_CONFIG
30_CATALOG\ANATOMY\10_CONFIG
30_CATALOG\INTERIOR_DESIGN\10_CONFIG
```

## App 設定位置

```text
80_APP\ASSET_MANAGER_WEBUI\00_CONFIG
```

## 規則

- 全域 schema 放 `20_CONFIG\10_SCHEMA`。
- 分類專案 config 跟著分類專案走。
- App config 跟著 app 走。


