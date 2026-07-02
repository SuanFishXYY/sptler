#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
算鱼议会 · 功绩权重 (merit_weight.py)

功绩哲学：权重随贡献演化，非世袭固定。
weight = base + min(功绩系数, 上限1.0)
功绩系数 = total_meetings × 0.02 + citation_sum × 0.05
从记忆 profile + experiences 读功绩数据。

用法:
  python scripts/routing/merit_weight.py --sage 王升
  python scripts/routing/merit_weight.py --all --json
"""
import argparse, json, sys
from pathlib import Path
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent.parent
MEM_DIR = ROOT / "memories"
BASE_WEIGHTS = {"邹蕴": 0.0}  # 邹蕴永远0
MERIT_CAP = 1.0  # 功绩上限，防寡头


def base_weight(sage, registry):
    """从 registry 读基础权重。"""
    entry = registry.get(sage, {})
    role = entry.get("role", "")
    w = entry.get("weight", 1.0)
    return float(w) if w else 1.0


def merit_coefficient(sage):
    """算功绩系数：议事数×0.02 + 引用数×0.05。从记忆档案读。"""
    p = MEM_DIR / f"{sage}.json"
    if not p.exists():
        return 0.0
    try:
        mem = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return 0.0
    if not isinstance(mem, dict):
        return 0.0
    total = mem.get("profile", {}).get("total_meetings", 0) or 0
    # 引用数 = 所有经历的 citation_count 之和
    cites = sum(int(e.get("citation_count", 0) or 0) for e in (mem.get("experiences", []) or []) if isinstance(e, dict))
    return min(total * 0.02 + cites * 0.05, MERIT_CAP)


def merit_weight(sage, registry):
    """功绩权重 = 基础 + 功绩系数（有上限）。"""
    base = base_weight(sage, registry)
    if sage == "邹蕴":
        return {"sage": sage, "base": 0.0, "merit": 0.0, "total": 0.0, "note": "议长不投票"}
    merit = merit_coefficient(sage)
    return {"sage": sage, "base": base, "merit": round(merit, 2), "total": round(base + merit, 2)}


def load_registry():
    p = ROOT / "references" / "saints" / "saints.registry.json"
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def main():
    ap = argparse.ArgumentParser(description="功绩权重——权重随贡献演化")
    ap.add_argument("--sage", help="查某圣人功绩权重")
    ap.add_argument("--all", action="store_true", help="全圣人")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    reg = load_registry()
    if args.sage:
        r = merit_weight(args.sage, reg)
        if args.json:
            print(json.dumps(r, ensure_ascii=False, indent=2)); return
        print(f"【{args.sage} 功绩权重】基础 {r['base']} + 功绩 {r['merit']} = {r['total']}" + (f"（{r.get('note','')}）" if r.get('note') else ""))
        return
    sages = [args.sage] if args.sage else sorted(reg.keys())
    out = [merit_weight(s, reg) for s in sages]
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2)); return
    print("【功绩权重总览】（基础 + 功绩 = 总权重，功绩上限1.0防寡头）")
    for r in out:
        note = f"（{r['note']}）" if r.get("note") else ""
        print(f"  {r['sage']:<6} 基础 {r['base']:<4} + 功绩 {r['merit']:<4} = {r['total']}{note}")


if __name__ == "__main__":
    main()
