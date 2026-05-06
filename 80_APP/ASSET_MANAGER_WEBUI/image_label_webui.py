from __future__ import annotations

import csv
import json
import random
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import gradio as gr


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "30_CATALOG" / "YOGA" / "15_YOGA_INPUT"
OUTPUT_DIR = ROOT / "30_CATALOG" / "YOGA" / "20_ANALYSIS_RESULT"
AUTO_TAG_DIR = ROOT / "30_CATALOG" / "YOGA" / "50_TAG" / "auto_tags"
CONFIG_DIR = ROOT / "80_APP" / "ASSET_MANAGER_WEBUI" / "00_CONFIG"
ENGINE_PATH = ROOT / "80_APP" / "ANALYSIS_ENGINE" / "analysis_engine.py"
LABEL_CSV = OUTPUT_DIR / "image_labels.csv"
LABEL_JSON = OUTPUT_DIR / "image_labels.json"
FOLDERS_JSON = CONFIG_DIR / "folders.json"
SUPPORTED_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
FIELDS = ["image", "asset_type", "category", "tags", "rating", "favorite", "source_url", "note", "updated_at"]
ASSET_TYPES = ["image", "reference", "yoga_pose", "product", "design", "icon", "other"]
TAG_ZH = {
    "YOGA": "瑜珈",
    "user_upload": "使用者上傳",
    "source_pdf": "PDF 來源",
    "source_image": "來源圖片",
    "reference_pose": "參考姿勢",
    "all_input": "全域入口",
    "single_person": "單人",
    "two_person": "雙人",
    "multi_person": "多人",
    "no_person": "無人物",
    "front_view": "正面",
    "side_view": "側面",
    "back_view": "背面",
    "unknown_view": "視角待確認",
    "standing_pose": "站姿",
    "seated_pose": "坐姿",
    "kneeling_pose": "跪姿",
    "forward_bend": "前彎",
    "backbend": "後彎",
    "twist": "扭轉",
    "balance": "平衡",
    "inversion": "倒立",
    "unknown_pose": "姿勢待確認",
    "clear": "清楚",
    "blurry": "模糊",
    "partial_body": "身體不完整",
    "low_confidence": "低信心",
    "needs_review": "需要人工確認",
    "unprocessed": "未處理",
    "analyzed": "已分析",
    "confirmed": "已確認",
    "rejected": "已排除",
    "vision_llm_analyzed": "語意模型已分析",
}

TEXT_ZH = {
    "接下来": "接下來",
    "图片": "圖片",
    "显示": "顯示",
    "一个": "一個",
    "穿着": "穿著",
    "短裤": "短褲",
    "双脚": "雙腳",
    "并拢": "併攏",
    "双手": "雙手",
    "下垂": "下垂",
    "内容": "內容",
    "瑜伽": "瑜珈",
    "体式": "體式",
    "用户": "使用者",
    "关于": "關於",
    "视觉": "視覺",
    "资料库": "資料庫",
}


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    AUTO_TAG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def zh_tag(tag: str) -> str:
    return TAG_ZH.get(tag, tag)


def zh_text(text: str) -> str:
    output = text or ""
    for source, target in sorted(TEXT_ZH.items(), key=lambda item: len(item[0]), reverse=True):
        output = output.replace(source, target)
    output = output.replace("接下來，我需要分析圖片內容。", "")
    return output


def read_auto_tags() -> list[dict]:
    ensure_dirs()
    rows = []
    for path in sorted(AUTO_TAG_DIR.glob("*.json")):
        try:
            with path.open("r", encoding="utf-8-sig") as f:
                data = json.load(f)
            data["_tag_file"] = str(path)
            rows.append(data)
        except (OSError, json.JSONDecodeError):
            continue
    return rows


def auto_tags_by_image_name() -> dict[str, dict]:
    output: dict[str, dict] = {}
    for row in read_auto_tags():
        image_path = Path(row.get("image_path", ""))
        if image_path.name:
            output[image_path.name] = row
    return output


def auto_tag_text(row: dict | None) -> str:
    if not row:
        return "尚未分析"
    tags = row.get("tags") or {}
    lines = [
        f"狀態：{', '.join(zh_tag(t) for t in tags.get('status', [])) or '無'}",
        f"來源：{', '.join(zh_tag(t) for t in tags.get('source', [])) or '無'}",
        f"畫面：{', '.join(zh_tag(t) for t in tags.get('visual', [])) or '無'}",
        f"姿勢：{', '.join(zh_tag(t) for t in tags.get('pose_type', [])) or '無'}",
        f"品質：{', '.join(zh_tag(t) for t in tags.get('quality', [])) or '無'}",
    ]
    confidence = row.get("confidence") or {}
    if "pose_mean" in confidence:
        lines.append(f"姿勢信心：{confidence['pose_mean']}")
    yolo = row.get("yolo") or {}
    if yolo:
        lines.append(f"YOLO：{yolo.get('person_count', 0)} 人 / 信心 {yolo.get('mean_confidence', 0.0)}")
    vision = row.get("vision_llm") or {}
    if vision.get("enabled"):
        lines.append(f"Qwen：{zh_text(vision.get('summary_zh', ''))}")
        if vision.get("pose_guess"):
            lines.append(f"Qwen 姿勢：{vision.get('pose_guess')}")
    lines.append(f"asset_id：{row.get('asset_id', '')}")
    return "\n".join(lines)


def auto_tag_inline(row: dict | None) -> str:
    if not row:
        return "尚未分析"
    tags = row.get("tags") or {}
    values = []
    for group in ("visual", "pose_type", "quality", "status"):
        values.extend(zh_tag(t) for t in tags.get(group, []))
    return "、".join(values[:6]) if values else "已分析"


def normalize_row(row: dict[str, str]) -> dict[str, str]:
    legacy_label = row.get("label", "")
    return {
        "image": row.get("image", ""),
        "asset_type": row.get("asset_type", "") or "image",
        "category": row.get("category", "") or legacy_label,
        "tags": row.get("tags", "") or legacy_label,
        "rating": row.get("rating", ""),
        "favorite": row.get("favorite", ""),
        "source_url": row.get("source_url", ""),
        "note": row.get("note", ""),
        "updated_at": row.get("updated_at", ""),
    }


def read_labels() -> list[dict[str, str]]:
    ensure_dirs()
    if not LABEL_CSV.exists():
        return []
    with LABEL_CSV.open("r", encoding="utf-8-sig", newline="") as f:
        return [normalize_row(row) for row in csv.DictReader(f)]


def write_labels(rows: list[dict[str, str]]) -> None:
    ensure_dirs()
    normalized = [normalize_row(row) for row in rows]
    with LABEL_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(normalized)
    with LABEL_JSON.open("w", encoding="utf-8") as f:
        json.dump(normalized, f, ensure_ascii=False, indent=2)


def read_folders() -> list[str]:
    ensure_dirs()
    folders: set[str] = {row["category"] for row in read_labels() if row.get("category")}
    if FOLDERS_JSON.exists():
        with FOLDERS_JSON.open("r", encoding="utf-8-sig") as f:
            data = json.load(f)
        if isinstance(data, list):
            folders.update(str(item).strip() for item in data if str(item).strip())
    return sorted(folders)


def write_folders(folders: list[str]) -> None:
    ensure_dirs()
    with FOLDERS_JSON.open("w", encoding="utf-8") as f:
        json.dump(sorted({folder for folder in folders if folder}), f, ensure_ascii=False, indent=2)


def list_images() -> list[Path]:
    ensure_dirs()
    return sorted(
        [p for p in DATA_DIR.iterdir() if p.is_file() and p.suffix.lower() in SUPPORTED_EXTS],
        key=lambda p: p.name.lower(),
    )


def labels_by_image() -> dict[str, dict[str, str]]:
    return {row["image"]: row for row in read_labels() if row.get("image")}


def folder_choices() -> list[str]:
    return ["全部", "未分類", *read_folders()]


def tag_choices() -> list[str]:
    tags: set[str] = set()
    for row in read_labels():
        for tag in row.get("tags", "").replace("，", ",").split(","):
            clean = tag.strip()
            if clean:
                tags.add(clean)
    for row in read_auto_tags():
        for values in (row.get("tags") or {}).values():
            for tag in values:
                clean = zh_tag(str(tag).strip())
                if clean:
                    tags.add(clean)
    return ["全部", "未標籤", *sorted(tags)]


def filter_paths(folder: str, tag: str, keyword: str) -> list[Path]:
    label_map = labels_by_image()
    auto_map = auto_tags_by_image_name()
    clean_keyword = (keyword or "").strip().lower()
    output: list[Path] = []
    for image in list_images():
        row = label_map.get(image.name, {})
        auto_text = auto_tag_text(auto_map.get(image.name))
        category = row.get("category", "")
        tags = row.get("tags", "")
        haystack = " ".join([image.name, category, tags, row.get("note", ""), auto_text]).lower()
        if folder == "未分類" and category:
            continue
        if folder not in ("", "全部", "未分類") and category != folder:
            continue
        if tag == "未標籤" and tags:
            continue
        if tag not in ("", "全部", "未標籤"):
            parts = [part.strip().lower() for part in tags.replace("，", ",").split(",")]
            auto_parts = [part.strip().lower() for part in auto_text.replace("，", ",").replace("、", ",").split(",")]
            if tag.lower() not in parts and tag.lower() not in auto_parts and tag.lower() not in auto_text.lower():
                continue
        if clean_keyword and clean_keyword not in haystack:
            continue
        output.append(image)
    return output


def gallery_items(folder: str = "全部", tag: str = "全部", keyword: str = "") -> list[tuple[str, str]]:
    label_map = labels_by_image()
    auto_map = auto_tags_by_image_name()
    items: list[tuple[str, str]] = []
    for image in filter_paths(folder, tag, keyword):
        row = label_map.get(image.name, {})
        category = row.get("category") or "未分類"
        tags = row.get("tags") or "未標籤"
        auto_tags = auto_tag_inline(auto_map.get(image.name))
        fav = "★ " if row.get("favorite") == "yes" else ""
        items.append((str(image), f"{fav}{image.name}\n{category} / {tags}\n自動：{auto_tags}"))
    return items


def folder_summary() -> str:
    label_map = labels_by_image()
    auto_map = auto_tags_by_image_name()
    total = len(list_images())
    uncategorized = 0
    untagged = 0
    analyzed = 0
    counts = {folder: 0 for folder in read_folders()}
    for image in list_images():
        row = label_map.get(image.name, {})
        category = row.get("category", "")
        tags = row.get("tags", "")
        if category:
            counts[category] = counts.get(category, 0) + 1
        else:
            uncategorized += 1
        if not tags:
            untagged += 1
        if image.name in auto_map:
            analyzed += 1
    lines = [
        f"全部：{total}",
        f"已自動分析：{analyzed}",
        f"未分類：{uncategorized}",
        f"未標籤：{untagged}",
        "",
        "資料夾：",
    ]
    lines.extend([f"- {name}：{count}" for name, count in sorted(counts.items())])
    return "\n".join(lines)


def refresh(folder: str, tag: str, keyword: str) -> tuple[list[tuple[str, str]], gr.Dropdown, gr.Dropdown, str, str]:
    return gallery_items(folder, tag, keyword), gr.update(choices=folder_choices()), gr.update(choices=tag_choices()), folder_summary(), "已重新整理"


def upload_images(files: list[str] | None, folder: str, tag: str, keyword: str) -> tuple[list[tuple[str, str]], gr.Dropdown, str, str]:
    ensure_dirs()
    copied = 0
    for file_path in files or []:
        source = Path(file_path)
        if source.suffix.lower() not in SUPPORTED_EXTS:
            continue
        target = DATA_DIR / source.name
        if target.exists():
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            target = DATA_DIR / f"{source.stem}_{stamp}{source.suffix.lower()}"
        shutil.copy2(source, target)
        copied += 1
    return gallery_items(folder, tag, keyword), gr.update(choices=folder_choices()), folder_summary(), f"已匯入 {copied} 張圖片"


def select_image(folder: str, tag: str, keyword: str, event: gr.SelectData) -> tuple[str, str, str, str, str, bool, str, str, str]:
    paths = filter_paths(folder, tag, keyword)
    if event.index is None or event.index >= len(paths):
        return "", "", "image", "", "", False, "", "", "尚未選取圖片"
    image = paths[event.index]
    row = labels_by_image().get(image.name, {})
    auto_row = auto_tags_by_image_name().get(image.name)
    return (
        str(image),
        image.name,
        row.get("asset_type", "image"),
        row.get("category", ""),
        row.get("tags", ""),
        row.get("favorite", "") == "yes",
        row.get("source_url", ""),
        row.get("note", ""),
        auto_tag_text(auto_row),
    )


def save_asset(
    image_name: str,
    asset_type: str,
    category: str,
    tags: str,
    favorite: bool,
    source_url: str,
    note: str,
    folder_filter: str,
    tag_filter: str,
    keyword: str,
) -> tuple[list[tuple[str, str]], gr.Dropdown, gr.Dropdown, str, str]:
    if not image_name:
        return gallery_items(folder_filter, tag_filter, keyword), gr.update(), gr.update(), folder_summary(), "請先選圖片"
    rows = read_labels()
    now = datetime.now().isoformat(timespec="seconds")
    found = False
    for row in rows:
        if row.get("image") == image_name:
            row.update(
                {
                    "asset_type": asset_type or "image",
                    "category": (category or "").strip(),
                    "tags": (tags or "").strip(),
                    "favorite": "yes" if favorite else "",
                    "source_url": (source_url or "").strip(),
                    "note": note or "",
                    "updated_at": now,
                }
            )
            found = True
            break
    if not found:
        rows.append(
            {
                "image": image_name,
                "asset_type": asset_type or "image",
                "category": (category or "").strip(),
                "tags": (tags or "").strip(),
                "favorite": "yes" if favorite else "",
                "rating": "",
                "source_url": (source_url or "").strip(),
                "note": note or "",
                "updated_at": now,
            }
        )
    write_labels(rows)
    folders = read_folders()
    if category and category not in folders:
        folders.append(category)
        write_folders(folders)
    return gallery_items(folder_filter, tag_filter, keyword), gr.update(choices=folder_choices()), gr.update(choices=tag_choices()), folder_summary(), "已儲存"


def create_folder(name: str) -> tuple[gr.Dropdown, gr.Dropdown, str, str]:
    clean = (name or "").strip()
    if not clean:
        return gr.update(), gr.update(), folder_summary(), "請輸入資料夾名稱"
    folders = read_folders()
    if clean not in folders:
        folders.append(clean)
        write_folders(folders)
    return gr.update(choices=folder_choices(), value=clean), gr.update(choices=folder_choices(), value=clean), folder_summary(), f"已新增資料夾：{clean}"


def add_tag(image_name: str, new_tag: str, current_tags: str, folder: str, tag_filter: str, keyword: str) -> tuple[str, list[tuple[str, str]], gr.Dropdown, str]:
    clean = (new_tag or "").strip().strip(",")
    if not image_name:
        return current_tags, gallery_items(folder, tag_filter, keyword), gr.update(), "請先選圖片"
    if not clean:
        return current_tags, gallery_items(folder, tag_filter, keyword), gr.update(), "請輸入標籤"
    parts = [part.strip() for part in (current_tags or "").replace("，", ",").split(",") if part.strip()]
    if clean not in parts:
        parts.append(clean)
    merged = ", ".join(parts)
    rows = read_labels()
    now = datetime.now().isoformat(timespec="seconds")
    found = False
    for row in rows:
        if row.get("image") == image_name:
            row["tags"] = merged
            row["updated_at"] = now
            found = True
            break
    if not found:
        rows.append({"image": image_name, "asset_type": "image", "category": "", "tags": merged, "favorite": "", "rating": "", "source_url": "", "note": "", "updated_at": now})
    write_labels(rows)
    return merged, gallery_items(folder, tag_filter, keyword), gr.update(choices=tag_choices()), f"已新增標籤：{clean}"


def move_to_folder(image_name: str, target_folder: str, folder: str, tag: str, keyword: str) -> tuple[list[tuple[str, str]], gr.Dropdown, str, str]:
    if not image_name:
        return gallery_items(folder, tag, keyword), gr.update(), folder_summary(), "請先選圖片"
    clean = (target_folder or "").strip()
    if not clean or clean in ("全部", "未分類"):
        return gallery_items(folder, tag, keyword), gr.update(), folder_summary(), "請選目標資料夾"
    rows = read_labels()
    now = datetime.now().isoformat(timespec="seconds")
    found = False
    for row in rows:
        if row.get("image") == image_name:
            row["category"] = clean
            row["updated_at"] = now
            found = True
            break
    if not found:
        rows.append({"image": image_name, "asset_type": "image", "category": clean, "tags": "", "favorite": "", "rating": "", "source_url": "", "note": "", "updated_at": now})
    write_labels(rows)
    folders = read_folders()
    if clean not in folders:
        folders.append(clean)
        write_folders(folders)
    return gallery_items(clean, tag, keyword), gr.update(choices=folder_choices(), value=clean), folder_summary(), f"已移動到：{clean}"


def randomize(folder: str, tag: str, keyword: str) -> tuple[list[tuple[str, str]], str]:
    items = gallery_items(folder, tag, keyword)
    random.shuffle(items)
    return items, "已隨機排序"


def run_yoga_analysis(folder: str, tag: str, keyword: str) -> tuple[list[tuple[str, str]], gr.Dropdown, gr.Dropdown, str, str]:
    ensure_dirs()
    if not ENGINE_PATH.exists():
        return gallery_items(folder, tag, keyword), gr.update(), gr.update(), folder_summary(), f"找不到分析引擎：{ENGINE_PATH}"
    completed = subprocess.run(
        [sys.executable, str(ENGINE_PATH), "--category", "YOGA"],
        cwd=str(ROOT),
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )
    if completed.returncode != 0:
        message = (completed.stderr or completed.stdout or "").strip()
        return gallery_items(folder, tag, keyword), gr.update(), gr.update(), folder_summary(), f"分析失敗：{message[-800:]}"
    message = (completed.stdout or "").strip()
    return gallery_items(folder, tag, keyword), gr.update(choices=folder_choices()), gr.update(choices=tag_choices()), folder_summary(), f"分析完成：{message[-800:]}"


CSS = """
body, .gradio-container {
  background: #ffffff !important;
  color: #111827 !important;
  font-size: 28px !important;
  font-weight: 800 !important;
}
.gradio-container * {
  font-size: 28px !important;
  color: #111827 !important;
  font-weight: 800 !important;
}
.gradio-container h1 {
  font-size: 42px !important;
  font-weight: 900 !important;
}
.gradio-container .block, .gradio-container .form {
  background: #ffffff !important;
  border-color: #d1d5db !important;
}
input, textarea, select {
  background: #ffffff !important;
  color: #111827 !important;
  border-color: #9ca3af !important;
  min-height: 56px !important;
}
button {
  border-radius: 8px !important;
  min-height: 56px !important;
  font-weight: 900 !important;
}
#sidebar textarea { min-height: 180px !important; }
"""


def build_app() -> gr.Blocks:
    ensure_dirs()
    with gr.Blocks(title="Image Asset Manager", css=CSS) as demo:
        gr.Markdown("# Image Asset Manager")
        status = gr.Textbox(label="狀態", value="就緒", interactive=False)
        with gr.Row():
            with gr.Column(scale=1, min_width=260, elem_id="sidebar"):
                summary = gr.Textbox(label="資料庫", value=folder_summary(), interactive=False, lines=10)
                upload = gr.File(label="匯入圖片", file_count="multiple", file_types=["image"], type="filepath")
                folder_filter = gr.Dropdown(label="資料夾", choices=folder_choices(), value="全部", allow_custom_value=True)
                new_folder = gr.Textbox(label="新增資料夾")
                create_folder_btn = gr.Button("新增資料夾")
                analyze_btn = gr.Button("分析", variant="primary")
                refresh_btn = gr.Button("重新整理")
                random_btn = gr.Button("隨機")
            with gr.Column(scale=4):
                keyword = gr.Textbox(label="搜尋", placeholder="搜尋檔名 / 資料夾 / 標籤 / 備註")
                gallery = gr.Gallery(label="縮圖", value=gallery_items, columns=5, height=650, object_fit="cover")
            with gr.Column(scale=2, min_width=320):
                preview = gr.Image(label="目前圖片", type="filepath", height=280)
                image_name = gr.Textbox(label="檔名", interactive=False)
                asset_type = gr.Dropdown(label="類型", choices=ASSET_TYPES, value="image", allow_custom_value=True)
                category = gr.Textbox(label="資料夾")
                move_folder = gr.Dropdown(label="移動到", choices=folder_choices(), value="全部", allow_custom_value=True)
                move_btn = gr.Button("移動")
                tag_filter = gr.Dropdown(label="Tag 篩選", choices=tag_choices(), value="全部", allow_custom_value=True)
                tags = gr.Textbox(label="Tags")
                auto_tags = gr.Textbox(label="自動分析標籤", interactive=False, lines=8)
                new_tag = gr.Textbox(label="新增標籤")
                add_tag_btn = gr.Button("+ 新增標籤")
                favorite = gr.Checkbox(label="Favorite")
                source_url = gr.Textbox(label="Source URL")
                note = gr.Textbox(label="備註", lines=4)
                save_btn = gr.Button("儲存", variant="primary")

        gallery.select(select_image, inputs=[folder_filter, tag_filter, keyword], outputs=[preview, image_name, asset_type, category, tags, favorite, source_url, note, auto_tags])
        upload.upload(upload_images, inputs=[upload, folder_filter, tag_filter, keyword], outputs=[gallery, folder_filter, summary, status])
        analyze_btn.click(run_yoga_analysis, inputs=[folder_filter, tag_filter, keyword], outputs=[gallery, folder_filter, tag_filter, summary, status])
        refresh_btn.click(refresh, inputs=[folder_filter, tag_filter, keyword], outputs=[gallery, folder_filter, tag_filter, summary, status])
        folder_filter.change(refresh, inputs=[folder_filter, tag_filter, keyword], outputs=[gallery, folder_filter, tag_filter, summary, status])
        tag_filter.change(refresh, inputs=[folder_filter, tag_filter, keyword], outputs=[gallery, folder_filter, tag_filter, summary, status])
        keyword.submit(refresh, inputs=[folder_filter, tag_filter, keyword], outputs=[gallery, folder_filter, tag_filter, summary, status])
        random_btn.click(randomize, inputs=[folder_filter, tag_filter, keyword], outputs=[gallery, status])
        create_folder_btn.click(create_folder, inputs=new_folder, outputs=[folder_filter, move_folder, summary, status])
        move_btn.click(move_to_folder, inputs=[image_name, move_folder, folder_filter, tag_filter, keyword], outputs=[gallery, folder_filter, summary, status])
        add_tag_btn.click(add_tag, inputs=[image_name, new_tag, tags, folder_filter, tag_filter, keyword], outputs=[tags, gallery, tag_filter, status])
        save_btn.click(save_asset, inputs=[image_name, asset_type, category, tags, favorite, source_url, note, folder_filter, tag_filter, keyword], outputs=[gallery, folder_filter, tag_filter, summary, status])
    return demo


if __name__ == "__main__":
    app = build_app()
    app.launch(server_name="127.0.0.1", server_port=7860, inbrowser=False)

