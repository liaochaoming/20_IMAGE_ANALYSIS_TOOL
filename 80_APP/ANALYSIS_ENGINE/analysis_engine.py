from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TOOL_ROOT = Path(r"D:\20_IMAGE_ANALYSIS_TOOL")
CATALOG_ROOT = TOOL_ROOT / "30_CATALOG"
SUPPORTED_EXTS_DEFAULT = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


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
    model_key = "yolo_pose_fast"
    if pipeline.get("models", {}).get("active_yolo_pose") == "strong":
        model_key = "yolo_pose_strong"
    model_path = Path(pipeline["models"][model_key])
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


def build_tags(category: str, yolo_result: dict[str, Any], tag_schema: dict[str, Any]) -> dict[str, list[str]]:
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

    if not tags["quality"]:
        tags["quality"].append("clear")
    if not tags["pose_type"]:
        tags["pose_type"].append("unknown_pose")
    if "unknown_view" not in tags["visual"]:
        tags["visual"].append("unknown_view")
    return {k: sorted(set(v)) for k, v in tags.items()}


def analyze_image(image_path: Path, category: str, pipeline: dict[str, Any], tag_schema: dict[str, Any], yolo_model: Any | None) -> dict[str, Any]:
    digest = file_hash(image_path)
    asset_id = f"{category.lower()}_{digest[:16]}"
    yolo_result = run_yolo(yolo_model, image_path)
    tags = build_tags(category, yolo_result, tag_schema)
    paths = pipeline["paths"]
    analysis_json_path = Path(paths["analysis_json_dir"]) / f"{asset_id}.json"
    auto_tag_path = Path(paths["auto_tag_dir"]) / f"{asset_id}.json"
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
            "created_at": record["analyzed_at"],
        },
    )
    return record


def run_category(category: str, limit: int | None = None) -> dict[str, Any]:
    category = category.upper()
    pipeline, tag_schema = load_category_config(category)
    supported_exts = set(pipeline.get("rules", {}).get("supported_extensions", SUPPORTED_EXTS_DEFAULT))
    input_dir = Path(pipeline["paths"].get("input_dir") or category_paths(category)["default_input_dir"])
    images = iter_images(input_dir, supported_exts)
    if limit is not None:
        images = images[:limit]
    yolo_model = load_yolo_model(pipeline) if images else None
    analyzed = []
    for image in images:
        analyzed.append(analyze_image(image, category, pipeline, tag_schema, yolo_model))
    run_summary = {
        "category_id": category,
        "input_dir": str(input_dir),
        "image_count": len(images),
        "analyzed_count": len(analyzed),
        "status": "done",
        "finished_at": now_iso(),
    }
    log_dir = Path(pipeline["paths"]["log_dir"])
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
