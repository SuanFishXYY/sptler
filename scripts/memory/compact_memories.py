#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
算鱼圣人记忆 · 压缩器 (compact_memories.py)

防止 memories/*.json 长期膨胀：保留 profile 与最近 N 次经历，
把更早经历计入 archive_summary（只保留数量与主题清单）。

用法:
  python scripts/memory/compact_memories.py --keep 20
  python scripts/memory/compact_memories.py --sage 王升 --keep 10
  python scripts/memory/compact_memories.py --dry-run
"""
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

DEFAULT_MEM_DIR = Path(__file__).resolve().parent.parent.parent / "memories"
MEM_DIR = DEFAULT_MEM_DIR


def classify(e: dict, is_recent: bool) -> str:
    """按记忆哲学宪法判定一条经历的处置：keep / archive / delete。
    - 转折点(is_turning_point)：永久保留（豁免）
    - 高价值(value_score>=2)：保留
    - 低价值(value_score==1)：近期保留，远期归档
    - 零价值(value_score==0)：琐事(单次verdict+零引用+无followup)→删除；否则归档
    """
    if e.get("is_turning_point"):
        return "keep"
    vs = int(e.get("value_score", 0) or 0)
    if vs >= 2:
        return "keep"
    if vs == 1:
        return "keep" if is_recent else "archive"
    # vs == 0
    is_trivial = (
        str(e.get("meeting_type", "regular")) == "regular"
        and e.get("mode", "") in ("单圣人裁决", "verdict", "")
        and int(e.get("citation_count", 0) or 0) == 0
        and not e.get("parent_meeting_id")  # 无 followup 衍生
    )
    return "delete" if is_trivial else "archive"


def compact_file(path: Path, keep: int, dry_run: bool = False) -> tuple[bool, str]:
    """价值驱动压缩：keep 之外的经历按价值分层——高价值/转折点永久留，低价值归档为纲，琐事删。"""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return False, f"跳过损坏文件 {path.name}: {e}"
    exps = data.get("experiences", []) or []
    if len(exps) <= keep:
        return True, f"{path.stem}: {len(exps)} 条，无需压缩"
    recent = exps[-keep:]
    recent_ids = {id(e) for e in recent}
    summary = data.get("archive_summary", {}) or {}
    summary.setdefault("compacted_count", 0)
    summary.setdefault("topics", [])
    summary.setdefault("deleted_count", 0)
    archived, deleted, kept_old = 0, 0, 0
    for e in exps[:-keep]:
        is_recent = id(e) in recent_ids  # 老经历恒为 False，但保留参数语义
        action = classify(e, is_recent=False)
        if action == "keep":
            kept_old += 1
            recent.append(e)  # 高价值/转折点虽老也留
        elif action == "archive":
            archived += 1
            t = e.get("topic") or ""
            if t and t not in summary["topics"]:
                summary["topics"].append(t)
        else:  # delete
            deleted += 1
    summary["compacted_count"] += archived
    summary["deleted_count"] += deleted
    summary["topics"] = summary["topics"][-50:]
    summary["last_compacted_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    data["archive_summary"] = summary
    data["experiences"] = recent
    if not dry_run:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return True, f"{path.stem}: {len(exps)} → {len(recent)}（留老价值{kept_old}/归档{archived}/删琐事{deleted}）"


def main():
    ap = argparse.ArgumentParser(description="压缩圣人记忆档案")
    ap.add_argument("--sage", help="只压缩某位圣人")
    ap.add_argument("--keep", type=int, default=30, help="保留最近 N 次经历（默认30）")
    ap.add_argument("--dry-run", action="store_true", help="只预览不写入")
    ap.add_argument("--mem-dir", help="覆盖记忆目录")
    args = ap.parse_args()
    global MEM_DIR
    if args.mem_dir:
        MEM_DIR = Path(args.mem_dir).expanduser().resolve()
    if not MEM_DIR.exists():
        print("（暂无 memories 目录）")
        return
    paths = [MEM_DIR / f"{args.sage}.json"] if args.sage else sorted(MEM_DIR.glob("*.json"))
    if not paths:
        print("（暂无记忆文件）")
        return
    for p in paths:
        if not p.exists():
            print(f"（{p.stem} 暂无记忆文件）")
            continue
        ok, msg = compact_file(p, args.keep, args.dry_run)
        print(("✅ " if ok else "⚠️  ") + msg)


if __name__ == "__main__":
    main()
