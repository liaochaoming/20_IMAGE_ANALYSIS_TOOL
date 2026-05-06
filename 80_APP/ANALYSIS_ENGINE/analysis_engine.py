from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests


TOOL_ROOT = Path(__file__).resolve().parents[2]
CATALOG_ROOT = TOOL_ROOT / "30_CATALOG"
SUPPORTED_EXTS_DEFAULT = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
LEGACY_TOOL_ROOT = Path(r"D:\20_IMAGE_ANALYSIS_TOOL")
MODEL_DIR_ENV = "IMAGE_ANALYSIS_MODEL_DIR"
DEFAULT_MODEL_DIR = Path(r"D:\30_AI_MODEL\YOLO_POSE\models")
PORTABLE_MODEL_DIR = TOOL_ROOT / "90_MODEL" / "YOLO_POSE" / "models"


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def resolve_project_path(value: str | Path) -> Path:
    path = Path(value)
    try:
        relative = path.relative_to(LEGACY_TOOL_ROOT)
        return TOOL_ROOT / relative
    except ValueError:
        return path


def resolve_model_path(value: str | Path) -> Path:
    filename = Path(value).name
    candidates: list[Path] = []
    env_model_dir = os.environ.get(MODEL_DIR_ENV)
    if env_model_dir:
        candidates.append(Path(env_model_dir) / filename)
    candidates.extend(
        [
            PORTABLE_MODEL_DIR / filename,
            DEFAULT_MODEL_DIR / filename,
            resolve_project_path(value),
        ]
    )
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def category_paths(category: str) -> dict[str, Path]:
    category = category.upper()
    root = CATALOG_ROOT / category
    return {
        "category_root": root,
        "config_dir": root / "10_CONFIG",
        "default_input_dir": root / f"15_{category}_INPUT",
        "analysis_json_dir": root / "20_ANALYSIS_RESULT" / "analysis_json",
        "config_suggestions_dir": root / "20_ANALYSIS_RESULT" / "config_suggestions",
        "auto_tag_dir": root / "50_TAG" / "auto_tags",
        "db_path": root / "30_DB" / "image_index.duckdb",
        "rag_dir": root / "40_RAG" / "vector_index",
    }


def load_category_config(category: str) -> tuple[dict[str, Any], dict[str, Any]]:
    paths = category_paths(category)
    prefix = category.upper()
    pipeline_path = paths["config_dir"] / f"{prefix}_ANALYSIS_PIPELINE.json"
    tag_schema_path = paths["config_dir"] / f"{prefix}_TAG_SCHEMA.json"
    if not pipeline_path.exists():
        raise FileNotFoundError(f"Missing pipeline config: {pipeline_path}")
    if not tag_schema_path.exists():
        raise FileNotFoundError(f"Missing tag schema: {tag_schema_path}")
    return read_json(pipeline_path), read_json(tag_schema_path)


def iter_images(input_dir: Path, supported_exts: set[str]) -> list[Path]:
    input_dir.mkdir(parents=True, exist_ok=True)
    return sorted(
        [p for p in input_dir.iterdir() if p.is_file() and p.suffix.lower() in supported_exts],
        key=lambda p: p.name.lower(),
    )


def load_yolo_model(pipeline: dict[str, Any]) -> Any | None:
    if not pipeline.get("steps", {}).get("yolo_pose", False):
        return None
    model_path = resolve_model_path(pipeline["models"]["yolo_pose"])
    if not model_path.exists():
        raise FileNotFoundError(f"Missing YOLO model: {model_path}")
    from ultralytics import YOLO

    return YOLO(str(model_path))


def run_yolo(model: Any | None, image_path: Path) -> dict[str, Any]:
    if model is None:
        return {"enabled": False, "person_count": 0, "detections": [], "mean_confidence": 0.0}
    results = model.predict(str(image_path), verbose=False)
    detections: list[dict[str, Any]] = []
    for result in results:
        keypoints = getattr(result, "keypoints", None)
        if keypoints is None or keypoints.xy is None:
            continue
        xy = keypoints.xy.cpu().tolist()
        conf = keypoints.conf.cpu().tolist() if keypoints.conf is not None else []
        for idx, points in enumerate(xy):
            conf_values = conf[idx] if idx < len(conf) else []
            valid_conf = [float(v) for v in conf_values if v is not None]
            mean_conf = sum(valid_conf) / len(valid_conf) if valid_conf else 0.0
            detections.append(
                {
                    "keypoints_xy": points,
                    "keypoints_confidence": conf_values,
                    "mean_confidence": round(mean_conf, 4),
                }
            )
    mean = sum(d["mean_confidence"] for d in detections) / len(detections) if detections else 0.0
    return {
        "enabled": True,
        "person_count": len(detections),
        "detections": detections,
        "mean_confidence": round(mean, 4),
    }


def parse_json_object(text: str) -> dict[str, Any]:
    clean = text.strip()
    clean = re.sub(r"^```(?:json)?", "", clean, flags=re.IGNORECASE).strip()
    clean = re.sub(r"```$", "", clean).strip()
    try:
        data = json.loads(clean)
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", clean, flags=re.DOTALL)
        if not match:
            return {}
        try:
            data = json.loads(match.group(0))
            return data if isinstance(data, dict) else {}
        except json.JSONDecodeError:
            return {}


def run_vision_llm(image_path: Path, pipeline: dict[str, Any], yolo_result: dict[str, Any]) -> dict[str, Any]:
    if not pipeline.get("steps", {}).get("vision_llm", False):
        return {"enabled": False}
    model = pipeline.get("models", {}).get("vision_llm")
    ollama = pipeline.get("ollama", {})
    base_url = str(ollama.get("base_url", "http://127.0.0.1:11434")).rstrip("/")
    timeout = int(ollama.get("timeout_seconds", 240))
    prompt = ollama.get(
        "prompt",
        "Return concise JSON for this yoga image with keys summary_zh, pose_guess, visual_tags, quality_tags, needs_review, suggested_tags.",
    )
    payload = {
        "model": model,
        "prompt": (
            f"{prompt}\n"
            f"YOLO person_count={yolo_result.get('person_count', 0)}, "
            f"pose_confidence={yolo_result.get('mean_confidence', 0.0)}. "
            "Use Traditional Chinese for summary_zh. Return JSON only."
        ),
        "images": [base64.b64encode(image_path.read_bytes()).decode("ascii")],
        "stream": False,
        "options": {
            "temperature": float(ollama.get("temperature", 0)),
            "num_predict": int(ollama.get("num_predict", 256)),
        },
    }
    response = requests.post(f"{base_url}/api/generate", json=payload, timeout=timeout)
    response.raise_for_status()
    body = response.json()
    raw = str(body.get("response") or body.get("thinking") or "").strip()
    parsed = parse_json_object(raw)
    result = {
        "enabled": True,
        "model": model,
        "base_url": base_url,
        "raw_response": raw,
        "parsed": parsed,
        "summary_zh": parsed.get("summary_zh") or parsed.get("summary") or raw[:300],
        "pose_guess": parsed.get("pose_guess") or parsed.get("pose") or "",
        "visual_tags": parsed.get("visual_tags") or parsed.get("tags") or [],
        "quality_tags": parsed.get("quality_tags") or [],
        "suggested_tags": parsed.get("suggested_tags") or [],
    }
    result["summary_zh"] = fallback_summary_zh(image_path, yolo_result, result)
    return result


def normalize_tag_values(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        parts = re.split(r"[,，、\s]+", value)
        return [p.strip() for p in parts if p.strip()]
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    return [str(value).strip()]


def has_cjk(text: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", text or ""))


def to_traditional_zh(text: str) -> str:
    replacements = {
        "用户": "使用者",
        "接下来": "接下來",
        "图": "圖",
        "图片": "圖片",
        "显示": "顯示",
        "一个": "一個",
        "穿着": "穿著",
        "短裤": "短褲",
        "双脚": "雙腳",
        "并拢": "併攏",
        "双手": "雙手",
        "内容": "內容",
        "关于": "關於",
        "瑜伽": "瑜珈",
        "体式": "體式",
        "名称": "名稱",
        "说明": "說明",
        "注意事项": "注意事項",
        "步骤": "步驟",
        "女性": "女性",
        "图像": "圖像",
        "输出": "輸出",
        "请求": "請求",
        "这个": "這個",
        "一个": "一個",
        "处理": "處理",
        "视觉": "視覺",
        "资料库": "資料庫",
        "模型": "模型",
        "繁体": "繁體",
        "中文": "中文",
        "山式": "山式",
        "站立": "站立",
    }
    output = text
    for source, target in sorted(replacements.items(), key=lambda item: len(item[0]), reverse=True):
        output = output.replace(source, target)
    return output


def fallback_summary_zh(image_path: Path, yolo_result: dict[str, Any], vision_result: dict[str, Any]) -> str:
    parsed = vision_result.get("parsed", {}) if isinstance(vision_result.get("parsed"), dict) else {}
    for key in ("summary_zh", "summary", "description", "caption"):
        value = str(parsed.get(key, "")).strip()
        if value and has_cjk(value):
            return to_traditional_zh(value[:300])
    raw = str(vision_result.get("raw_response", "")).strip()
    cjk_sentences = re.findall(r"[^。！？\n]*[\u4e00-\u9fff][^。！？\n]*[。！？]?", raw)
    content_sentences = [
        sentence.strip()
        for sentence in cjk_sentences
        if any(key in sentence for key in ("圖片", "图片", "瑜伽", "瑜珈", "體式", "体式", "姿勢", "山式"))
        and not any(skip in sentence for skip in ("用户", "使用者", "请求", "請求", "JSON", "输出", "輸出", "要求"))
    ]
    if content_sentences:
        return to_traditional_zh("".join(content_sentences[:2]).strip()[:300]).replace("接下來，我需要分析圖片內容。", "")
    if cjk_sentences:
        return to_traditional_zh("".join(cjk_sentences[:2]).strip()[:300]).replace("接下來，我需要分析圖片內容。", "")
    person_count = int(yolo_result.get("person_count", 0))
    confidence = yolo_result.get("mean_confidence", 0.0)
    return f"這是一張 YOGA 圖片，YOLO 偵測到 {person_count} 人，姿勢信心 {confidence}，需由語意模型或人工進一步確認體式。"


def build_tags(
    category: str,
    yolo_result: dict[str, Any],
    vision_result: dict[str, Any],
    tag_schema: dict[str, Any],
) -> dict[str, list[str]]:
    rules = tag_schema.get("auto_tag_rules", {})
    default_tags = rules.get("default_tags", {})
    tags = {
        "category": [category.upper()],
        "source": list(default_tags.get("source", ["user_upload"])),
        "visual": [],
        "pose_type": [],
        "quality": [],
        "status": list(default_tags.get("status", ["analyzed"])),
    }
    person_count = int(yolo_result.get("person_count", 0))
    person_rules = rules.get("person_count", {})
    if person_count == 0:
        tags["visual"].append(person_rules.get("0", "no_person"))
        tags["pose_type"].append("unknown_pose")
        tags["quality"].append("needs_review")
        if "needs_review" not in tags["status"]:
            tags["status"].append("needs_review")
    elif person_count == 1:
        tags["visual"].append(person_rules.get("1", "single_person"))
    elif person_count == 2:
        tags["visual"].append(person_rules.get("2", "two_person"))
    else:
        tags["visual"].append(person_rules.get("3_or_more", "multi_person"))

    if yolo_result.get("enabled") and float(yolo_result.get("mean_confidence", 0.0)) < 0.4:
        tags["quality"].extend(["low_confidence", "needs_review"])
        if "needs_review" not in tags["status"]:
            tags["status"].append("needs_review")

    if vision_result.get("enabled"):
        pose_guess = str(vision_result.get("pose_guess") or "").strip()
        if pose_guess:
            tags["pose_type"].append(pose_guess)
        for tag in normalize_tag_values(vision_result.get("visual_tags")):
            tags["visual"].append(tag)
        for tag in normalize_tag_values(vision_result.get("quality_tags")):
            tags["quality"].append(tag)
        if vision_result.get("summary_zh"):
            tags["status"].append("vision_llm_analyzed")

    if not tags["quality"]:
        tags["quality"].append("clear")
    if not tags["pose_type"]:
        tags["pose_type"].append("unknown_pose")
    if "unknown_view" not in tags["visual"]:
        tags["visual"].append("unknown_view")
    return {k: sorted(set(v)) for k, v in tags.items()}


def write_config_suggestions(
    asset_id: str,
    pipeline: dict[str, Any],
    tag_schema: dict[str, Any],
    vision_result: dict[str, Any],
    tags: dict[str, list[str]],
) -> str | None:
    if not pipeline.get("steps", {}).get("config_suggestions", False):
        return None
    allowed = {str(tag) for values in tag_schema.get("tag_groups", {}).values() for tag in values}
    observed = {tag for values in tags.values() for tag in values}
    observed.update(normalize_tag_values(vision_result.get("suggested_tags")))
    suggestions = sorted(tag for tag in observed if tag and tag not in allowed)
    if not suggestions:
        return None
    path = resolve_project_path(pipeline["paths"]["config_suggestions_dir"]) / f"{asset_id}_tag_suggestions.json"
    write_json(
        path,
        {
            "asset_id": asset_id,
            "created_at": now_iso(),
            "policy": "suggestion_only_do_not_modify_10_CONFIG",
            "suggested_tags": suggestions,
            "source": "vision_llm_and_auto_tags",
        },
    )
    return str(path)


def vectorize_text(text: str, dimensions: int = 64) -> list[float]:
    buckets = [0.0] * dimensions
    tokens = re.findall(r"[\w\u4e00-\u9fff]+", text.lower())
    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        idx = int.from_bytes(digest[:2], "big") % dimensions
        buckets[idx] += 1.0
    total = sum(v * v for v in buckets) ** 0.5
    return [round(v / total, 6) if total else 0.0 for v in buckets]


def write_rag_record(record: dict[str, Any], pipeline: dict[str, Any]) -> str | None:
    if not pipeline.get("steps", {}).get("rag", False):
        return None
    rag_dir = resolve_project_path(pipeline["paths"]["rag_dir"])
    rag_dir.mkdir(parents=True, exist_ok=True)
    text = " ".join(
        [
            record["file_name"],
            json.dumps(record.get("auto_tags", {}), ensure_ascii=False),
            str(record.get("vision_llm_result", {}).get("summary_zh", "")),
            str(record.get("vision_llm_result", {}).get("pose_guess", "")),
        ]
    )
    item = {
        "asset_id": record["asset_id"],
        "category_id": record["category_id"],
        "file_name": record["file_name"],
        "text": text,
        "vector_model": "local_hash_vector_v1",
        "vector": vectorize_text(text),
        "updated_at": record["analyzed_at"],
    }
    vector_path = rag_dir / f"{record['asset_id']}.json"
    write_json(vector_path, item)
    manifest = rag_dir / "manifest.jsonl"
    existing_lines = []
    if manifest.exists():
        existing_lines = [line for line in manifest.read_text(encoding="utf-8").splitlines() if record["asset_id"] not in line]
    existing_lines.append(json.dumps({"asset_id": record["asset_id"], "path": str(vector_path), "updated_at": record["analyzed_at"]}, ensure_ascii=False))
    manifest.write_text("\n".join(existing_lines) + "\n", encoding="utf-8")
    return str(vector_path)


def write_duckdb_record(record: dict[str, Any], pipeline: dict[str, Any]) -> None:
    if not pipeline.get("steps", {}).get("duckdb", False):
        return
    import duckdb

    db_path = resolve_project_path(pipeline["paths"]["db_path"])
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(db_path))
    try:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS image_index (
                asset_id VARCHAR PRIMARY KEY,
                category_id VARCHAR,
                file_name VARCHAR,
                source_path VARCHAR,
                file_hash VARCHAR,
                analyzed_at VARCHAR,
                yolo_person_count INTEGER,
                yolo_mean_confidence DOUBLE,
                llm_model VARCHAR,
                llm_summary_zh VARCHAR,
                tags_json VARCHAR,
                analysis_json_path VARCHAR,
                auto_tag_path VARCHAR,
                rag_vector_path VARCHAR
            )
            """
        )
        con.execute(
            """
            INSERT OR REPLACE INTO image_index VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                record["asset_id"],
                record["category_id"],
                record["file_name"],
                record["source_path"],
                record["file_hash"],
                record["analyzed_at"],
                int(record.get("pose_result", {}).get("person_count", 0)),
                float(record.get("pose_result", {}).get("mean_confidence", 0.0)),
                str(record.get("vision_llm_result", {}).get("model", "")),
                str(record.get("vision_llm_result", {}).get("summary_zh", "")),
                json.dumps(record.get("auto_tags", {}), ensure_ascii=False),
                record["outputs"]["analysis_json"],
                record["outputs"]["auto_tags"],
                record["outputs"].get("rag_vector", ""),
            ],
        )
    finally:
        con.close()


def prune_missing_input_outputs(category: str, asset_ids: set[str], pipeline: dict[str, Any]) -> None:
    if not pipeline.get("rules", {}).get("prune_missing_input_outputs", False):
        return
    category_prefix = f"{category.lower()}_"
    for key, pattern in (
        ("analysis_json_dir", "*.json"),
        ("auto_tag_dir", "*.json"),
        ("rag_dir", "*.json"),
    ):
        directory = resolve_project_path(pipeline["paths"][key])
        if not directory.exists():
            continue
        for path in directory.glob(pattern):
            if path.stem.startswith(category_prefix) and path.stem not in asset_ids:
                path.unlink()
    manifest = resolve_project_path(pipeline["paths"]["rag_dir"]) / "manifest.jsonl"
    if manifest.exists():
        kept = []
        for line in manifest.read_text(encoding="utf-8").splitlines():
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            if item.get("asset_id") in asset_ids:
                kept.append(json.dumps(item, ensure_ascii=False))
        manifest.write_text(("\n".join(kept) + "\n") if kept else "", encoding="utf-8")
    if pipeline.get("steps", {}).get("duckdb", False):
        import duckdb

        db_path = resolve_project_path(pipeline["paths"]["db_path"])
        if db_path.exists():
            con = duckdb.connect(str(db_path))
            try:
                rows = con.execute("SELECT asset_id FROM image_index").fetchall()
                for (asset_id,) in rows:
                    if str(asset_id).startswith(category_prefix) and str(asset_id) not in asset_ids:
                        con.execute("DELETE FROM image_index WHERE asset_id = ?", [asset_id])
            except duckdb.CatalogException:
                return
            finally:
                con.close()


def cached_record_is_valid(record: dict[str, Any], digest: str, pipeline: dict[str, Any]) -> bool:
    if record.get("file_hash") != digest:
        return False
    steps = pipeline.get("steps", {})
    if steps.get("yolo_pose") and not record.get("pose_result", {}).get("enabled"):
        return False
    if steps.get("vision_llm") and not record.get("vision_llm_result", {}).get("enabled"):
        return False
    return True


def load_cached_record(asset_id: str, digest: str, pipeline: dict[str, Any]) -> dict[str, Any] | None:
    rules = pipeline.get("rules", {})
    if not rules.get("reuse_existing_analysis", True) or rules.get("force_reanalyze", False):
        return None
    analysis_json_path = resolve_project_path(pipeline["paths"]["analysis_json_dir"]) / f"{asset_id}.json"
    if not analysis_json_path.exists():
        return None
    record = read_json(analysis_json_path)
    if not cached_record_is_valid(record, digest, pipeline):
        return None
    record["analysis_status"] = "cached"
    return record


def analyze_image(
    image_path: Path,
    category: str,
    pipeline: dict[str, Any],
    tag_schema: dict[str, Any],
    yolo_model: Any | None,
) -> dict[str, Any]:
    digest = file_hash(image_path)
    asset_id = f"{category.lower()}_{digest[:16]}"
    cached = load_cached_record(asset_id, digest, pipeline)
    if cached is not None:
        rag_path = write_rag_record(cached, pipeline)
        if rag_path:
            cached.setdefault("outputs", {})["rag_vector"] = rag_path
        write_duckdb_record(cached, pipeline)
        return cached
    yolo_result = run_yolo(yolo_model, image_path)
    vision_result = run_vision_llm(image_path, pipeline, yolo_result)
    tags = build_tags(category, yolo_result, vision_result, tag_schema)
    paths = pipeline["paths"]
    analysis_json_path = resolve_project_path(paths["analysis_json_dir"]) / f"{asset_id}.json"
    auto_tag_path = resolve_project_path(paths["auto_tag_dir"]) / f"{asset_id}.json"
    record = {
        "asset_id": asset_id,
        "category_id": category.upper(),
        "source_path": str(image_path),
        "file_name": image_path.name,
        "file_hash": digest,
        "analysis_status": "done",
        "analyzed_at": now_iso(),
        "models": {
            "yolo_pose": pipeline.get("models", {}).get("active_yolo_pose"),
            "vision_llm": pipeline.get("models", {}).get("vision_llm"),
        },
        "pose_result": yolo_result,
        "vision_llm_result": vision_result,
        "auto_tags": tags,
        "outputs": {
            "analysis_json": str(analysis_json_path),
            "auto_tags": str(auto_tag_path),
        },
        "config_policy": {
            "formal_config_modified": False,
            "suggestions_only": True,
        },
    }
    suggestion_path = write_config_suggestions(asset_id, pipeline, tag_schema, vision_result, tags)
    if suggestion_path:
        record["outputs"]["config_suggestions"] = suggestion_path
    rag_path = write_rag_record(record, pipeline)
    if rag_path:
        record["outputs"]["rag_vector"] = rag_path
    write_json(analysis_json_path, record)
    write_json(
        auto_tag_path,
        {
            "asset_id": asset_id,
            "category_id": category.upper(),
            "image_path": str(image_path),
            "tags": tags,
            "confidence": {
                "pose_mean": yolo_result.get("mean_confidence", 0.0),
            },
            "yolo": {
                "enabled": yolo_result.get("enabled", False),
                "person_count": yolo_result.get("person_count", 0),
                "mean_confidence": yolo_result.get("mean_confidence", 0.0),
            },
            "vision_llm": {
                "enabled": vision_result.get("enabled", False),
                "model": vision_result.get("model", ""),
                "summary_zh": vision_result.get("summary_zh", ""),
                "pose_guess": vision_result.get("pose_guess", ""),
            },
            "outputs": record["outputs"],
            "created_at": record["analyzed_at"],
        },
    )
    write_duckdb_record(record, pipeline)
    return record


def active_step_summary(pipeline: dict[str, Any]) -> dict[str, bool]:
    steps = pipeline.get("steps", {})
    return {
        "yolo_pose": bool(steps.get("yolo_pose", False)),
        "vision_llm": bool(steps.get("vision_llm", False)),
        "duckdb": bool(steps.get("duckdb", False)),
        "rag": bool(steps.get("rag", False)),
        "auto_tag": bool(steps.get("auto_tag", False)),
        "config_suggestions": bool(steps.get("config_suggestions", False)),
    }


def run_category(category: str, limit: int | None = None) -> dict[str, Any]:
    category = category.upper()
    pipeline, tag_schema = load_category_config(category)
    supported_exts = set(pipeline.get("rules", {}).get("supported_extensions", SUPPORTED_EXTS_DEFAULT))
    input_dir = resolve_project_path(pipeline["paths"].get("input_dir") or category_paths(category)["default_input_dir"])
    images = iter_images(input_dir, supported_exts)
    if limit is not None:
        images = images[:limit]
    prechecked: list[tuple[Path, dict[str, Any] | None]] = []
    current_asset_ids: set[str] = set()
    needs_fresh_analysis = False
    for image in images:
        digest = file_hash(image)
        asset_id = f"{category.lower()}_{digest[:16]}"
        current_asset_ids.add(asset_id)
        cached = load_cached_record(asset_id, digest, pipeline)
        prechecked.append((image, cached))
        if cached is None:
            needs_fresh_analysis = True
    prune_missing_input_outputs(category, current_asset_ids, pipeline)
    yolo_model = load_yolo_model(pipeline) if images and needs_fresh_analysis else None
    analyzed = []
    cached_count = 0
    for image, cached in prechecked:
        if cached is not None:
            rag_path = write_rag_record(cached, pipeline)
            if rag_path:
                cached.setdefault("outputs", {})["rag_vector"] = rag_path
            write_duckdb_record(cached, pipeline)
            analyzed.append(cached)
            cached_count += 1
            continue
        analyzed.append(analyze_image(image, category, pipeline, tag_schema, yolo_model))
    run_summary = {
        "category_id": category,
        "input_dir": str(input_dir),
        "image_count": len(images),
        "analyzed_count": len(analyzed),
        "cached_count": cached_count,
        "fresh_count": len(analyzed) - cached_count,
        "active_steps": active_step_summary(pipeline),
        "status": "done",
        "finished_at": now_iso(),
    }
    log_dir = resolve_project_path(pipeline["paths"]["log_dir"])
    write_json(log_dir / f"analysis_run_{category.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", run_summary)
    return run_summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Image Analysis Engine")
    parser.add_argument("--category", default="YOGA", help="Category id, e.g. YOGA")
    parser.add_argument("--limit", type=int, default=None, help="Optional max images to analyze")
    args = parser.parse_args()
    summary = run_category(args.category, args.limit)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
