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

MEM_DIR = Path(__file__).resolve().parent.parent / "memories"


def memory_path(sage: str) -> Path:
    return MEM_DIR / f"{sage}.json"


def load_memory(sage: str) -> dict | None:
    p = memory_path(sage)
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def all_memories() -> list[dict]:
    if not MEM_DIR.exists():
        return []
    out = []
    for p in sorted(MEM_DIR.glob("*.json")):
        try:
            out.append(json.loads(p.read_text(encoding="utf-8")))
        except Exception:
            pass
    return out


def stats_line(mem: dict) -> str:
    p = mem.get("profile", {})
    st = p.get("stances", {})
    focus = "、".join(p.get("specialty_focus", [])) or "—"
    return (
        f"  {mem['sage']:<6} | {p.get('total_meetings',0):>2}次 | "
        f"赞{st.get('赞成',0)} 反{st.get('反对',0)} 弃{st.get('弃权',0)} | "
        f"{p.get('risk_tendency','未知'):<6} | 焦点：{focus}"
    )


def main():
    ap = argparse.ArgumentParser(description="总览/查询圣人记忆")
    ap.add_argument("--sage", help="查看某圣人完整档案")
    ap.add_argument("--stats", action="store_true", help="仅统计总览")
    ap.add_argument("--json", action="store_true", help="JSON 输出")
    args = ap.parse_args()

    if args.sage:
        mem = load_memory(args.sage)
        if not mem:
            print(f"（{args.sage} 暂无记忆档案）")
            sys.exit(0)
        if args.json:
            print(json.dumps(mem, ensure_ascii=False, indent=2))
        else:
            print(stats_line(mem))
            print("  ——— 近期经历 ———")
            for e in mem.get("experiences", [])[-10:]:
                print(
                    f"  [{e.get('recorded_at','')}] {e.get('topic','')} "
                    f"（{e.get('mode','')}/{e.get('verdict','')}）"
                )
                print(f"      立场={e.get('stance','')}（权重{e.get('weight','')}）：{e.get('reason','')}")
                if e.get("recommendation"):
                    print(f"      建议：{e['recommendation']}")
        return

    mems = all_memories()
    if not mems:
        print("（暂无任何圣人记忆档案。议会运行后才会生成。）")
        return

    if args.json:
        print(json.dumps(
            [{"sage": m["sage"], "profile": m.get("profile", {})} for m in mems],
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
