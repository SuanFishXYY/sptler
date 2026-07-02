#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
算鱼圣人记忆 · 总览与查询 (list_memories.py)

查看所有圣人的记忆统计，或查询单个圣人的完整档案。

用法:
  # 总览：列出所有有记忆的圣人及其统计
  python list_memories.py

  # 查看某圣人完整档案
  python list_memories.py --sage 王升

  # 只看总览统计（不含详情）
  python list_memories.py --stats

  # JSON 输出
  python list_memories.py --json
"""
import argparse
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

DEFAULT_MEM_DIR = Path(__file__).resolve().parent.parent.parent / "memories"
MEM_DIR = DEFAULT_MEM_DIR


def memory_path(sage: str) -> Path:
    return MEM_DIR / f"{sage}.json"


def load_memory(sage: str):
    p = memory_path(sage)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def all_memories() -> list:
    if not MEM_DIR.exists():
        return []
    out = []
    for p in sorted(MEM_DIR.glob("*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            print(f"⚠️  跳过损坏的记忆文件：{p.name}", file=sys.stderr)
            continue
        if not isinstance(data, dict):
            print(f"⚠️  跳过非记忆文件：{p.name}（根结构非对象）", file=sys.stderr)
            continue
        out.append(data)
    return out


def stats_line(mem: dict) -> str:
    sage = mem.get("sage", "未知")
    p = mem.get("profile", {}) or {}
    st = p.get("stances", {}) or {}
    focus = "、".join(p.get("specialty_focus", []) or []) or "—"
    return (
        f"  {sage:<6} | {p.get('total_meetings',0):>2}次 | "
        f"赞{st.get('赞成',0)} 反{st.get('反对',0)} 弃{st.get('弃权',0)} | "
        f"{p.get('risk_tendency','未知'):<6} | 焦点：{focus}"
    )


def main():
    ap = argparse.ArgumentParser(description="总览/查询圣人记忆")
    ap.add_argument("--sage", help="查看某圣人完整档案")
    ap.add_argument("--stats", action="store_true", help="仅统计总览（不展开近期经历）")
    ap.add_argument("--json", action="store_true", help="JSON 输出")
    ap.add_argument("--mem-dir", help="覆盖记忆目录（默认：技能目录/memories）")
    args = ap.parse_args()

    global MEM_DIR
    if args.mem_dir:
        MEM_DIR = Path(args.mem_dir).expanduser().resolve()

    if args.sage:
        mem = load_memory(args.sage)
        if not mem:
            print(f"（{args.sage} 暂无记忆档案）")
            sys.exit(0)
        if args.json:
            print(json.dumps(mem, ensure_ascii=False, indent=2))
        else:
            print(stats_line(mem))
            if not args.stats:
                print("  ——— 近期经历 ———")
                for e in (mem.get("experiences", []) or [])[-10:]:
                    print(
                        f"  [{e.get('recorded_at') or ''}] {e.get('topic') or ''} "
                        f"（{e.get('mode') or ''}/{e.get('verdict') or ''}）"
                    )
                    print(f"      立场={e.get('stance') or ''}（权重{e.get('weight') or ''}）：{e.get('reason') or ''}")
                    if e.get("recommendation"):
                        print(f"      建议：{e.get('recommendation') or ''}")
        return

    mems = all_memories()
    if not mems:
        print("（暂无任何圣人记忆档案。议会运行后才会生成。）")
        return

    if args.json:
        print(json.dumps(
            [{"sage": m.get("sage", "未知"), "profile": m.get("profile", {}) or {}} for m in mems],
            ensure_ascii=False, indent=2
        ))
        return

    print(f"算鱼圣人记忆总览（共 {len(mems)} 位圣人有档案）")
    print(f"{'圣人':<8} | 次数 | 立场(赞/反/弃)      | 风险   | 专长焦点")
    print("  " + "-" * 78)
    for m in sorted(mems, key=lambda x: x.get("profile", {}).get("total_meetings", 0), reverse=True):
        print(stats_line(m))
    print()
    total_exp = sum(len(m.get("experiences", [])) for m in mems)
    print(f"累计经历 {total_exp} 条。用 --sage <姓名> 查看某人完整档案。")


if __name__ == "__main__":
    main()
