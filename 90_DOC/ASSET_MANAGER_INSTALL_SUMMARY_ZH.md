# ASSET_MANAGER_INSTALL_SUMMARY_ZH

STATUS: ACTIVE
SCOPE: IMAGE_ANALYSIS_TOOL ASSET_MANAGER INSTALL SUMMARY
LAST_UPDATE: 2026-05-06

## 目的

本文件記錄 Asset Manager WebUI 整合後的安裝與使用狀態。

## 目前狀態

```text
正式專案：D:\20_IMAGE_ANALYSIS_TOOL
舊專案：獨立 Asset Manager 專案已刪除
Python 環境：D:\20_IMAGE_ANALYSIS_TOOL\.venv
WebUI：D:\20_IMAGE_ANALYSIS_TOOL\80_APP\ASSET_MANAGER_WEBUI
啟動 BAT：D:\20_IMAGE_ANALYSIS_TOOL\70_SCRIPT\Start_ImageLabel_WebUI.bat
```

## 已整合項目

- Asset Manager WebUI 程式。
- Asset Manager 設定檔。
- PDF 來源資料。
- 啟動 / 安裝 / 驗證腳本。
- log 路徑。

## 驗證指令

```powershell
D:\20_IMAGE_ANALYSIS_TOOL\.venv\Scripts\python.exe -m py_compile D:\20_IMAGE_ANALYSIS_TOOL\80_APP\ASSET_MANAGER_WEBUI\image_label_webui.py
D:\20_IMAGE_ANALYSIS_TOOL\.venv\Scripts\python.exe -c "import json, pathlib; json.loads(pathlib.Path(r'D:\20_IMAGE_ANALYSIS_TOOL\80_APP\ASSET_MANAGER_WEBUI\00_CONFIG\paths.json').read_text(encoding='utf-8-sig')); print('PATHS_JSON_OK')"
```

## 資料規則

```text
40_ALL_INPUT = 全專案待分析入口
30_CATALOG\YOGA\00_DATA = YOGA 正式原始資料
30_CATALOG\YOGA\20_ANALYSIS_RESULT = YOGA 分析輸出
```



