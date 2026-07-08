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
    # vs == 0：仅真正的单圣人裁决轨(verdict)才是可删琐事——它本就零留痕(不入记忆)，
    # 故此分支实际极少命中。空 mode 的常规会议（如「否决」未通过决议）是反面教材，
    # 须按哲学宪法「未通过/被否决→保留」归档而非物理删除，故 mode 不可含 ""。
    # lite 记忆(lite=true)：value_score>=1 的留痕不删（归档保可回溯）；
    # 但 value_score==0(否决/未通过) + 零引用 + 无followup = 纯琐事 lite 快调，该删（防膨胀）。
    is_trivial = (
        str(e.get("meeting_type", "regular")) == "regular"
        and e.get("mode", "") in ("单圣人裁决", "verdict")
        and int(e.get("citation_count", 0) or 0) == 0
        and not e.get("parent_meeting_id")  # 无 followup 衍生
        and e.get("scenario") != "专利挖掘"  # D14: 挖掘 memory 是 pre-filing 草稿留痕,归档不删
    )
    # lite value_score>=1 不删（留痕有回溯价值）；lite value_score==0 且琐碎 → 删（防膨胀）
    if e.get("lite") and int(e.get("value_score", 0) or 0) >= 1:
        return "archive"  # lite 留痕(通过过的)归档不删
    return "delete" if is_trivial else "archive"


def compact_file(path: Path, keep: int, dry_run: bool = False) -> tuple[bool, str]:
    """价值驱动压缩：keep 之外的经历按价值分层——高价值/转折点永久留，低价值归档为纲，琐事删。"""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return False, f"跳过损坏文件 {path.name}: {e}"
    if not isinstance(data, dict):
        return False, f"跳过非记忆文件 {path.name}（根结构非对象）"
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
            # D29: skeleton archive——保全挖掘/low_value/incomplete 等新字段,防 compact 静默丢弃
            # (旧版只存 topic 字符串,新字段会丢→summon 降权失效)。skeleton 供召唤时识别挖掘记忆。
            mid = e.get("meeting_id", "")
            _digits = "".join(c for c in mid if c.isdigit())[:8]  # YYYYMMDD(兼容 SPTLER- / SPTLER-FOLLOWUP- 前缀)
            skeleton = {
                "topic": t,
                "date": (_digits if len(_digits) == 8 else ""),
                "meeting_id": mid,
                "scenario": e.get("scenario", ""),
                "low_value": bool(e.get("low_value")),
                "elicitation_incomplete": bool(e.get("elicitation_incomplete")),
            }
            summary.setdefault("archived_skeletons", []).append(skeleton)
        else:  # delete
            deleted += 1
    summary["compacted_count"] += archived
    summary["deleted_count"] += deleted
    summary["topics"] = summary["topics"][-50:]
    summary["archived_skeletons"] = summary.get("archived_skeletons", [])[-50:]  # D29: skeleton 同样封顶 50
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
