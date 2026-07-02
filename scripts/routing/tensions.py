#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
算鱼议会 · 圣人张力查询 (tensions.py)

议会灵魂机制：给定入会名单，返回相关圣人间的预设张力对。
lite ≤3人时注入，驱动多人辩论有交锋而非各说各话。

用法:
  python scripts/routing/tensions.py --roster 王升,张鑫
  python scripts/routing/tensions.py --roster 王升,张鑫,范征 --json
"""
import argparse, json, sys
from pathlib import Path
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent.parent
TENSIONS_PATH = ROOT / "references" / "saints" / "tensions.json"


def load_tensions():
    try:
        d = json.loads(TENSIONS_PATH.read_text(encoding="utf-8"))
        return d.get("tensions", {}) if isinstance(d, dict) else {}
    except Exception:
        return {}


def load_relations(sage):
    """读某圣人的 RELATIONS.json，返回 {对方: {co_meetings, topics, last_topic}}。"""
    p = ROOT / "saints" / sage / "RELATIONS.json"
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
        rels = d.get("relations", {}) if isinstance(d, dict) else {}
        return rels if isinstance(rels, dict) else {}
    except Exception:
        return {}


def relevant_tensions(roster, tensions):
    """返回入会名单中两两相关的张力对 + 共现历史演化（议会动态灵魂）。"""
    roster_set = {n.strip() for n in roster if n.strip()}
    out = []
    for key, val in tensions.items():
        parts = key.split("-")
        if len(parts) != 2:
            continue
        a, b = parts
        matched = False
        if b == "四核心":
            if "邹蕴" in roster_set and any(c in roster_set for c in ["王升", "张鑫", "徐奕阳", "范征"]):
                matched = True
        elif a in roster_set and b in roster_set:
            matched = True
        if not matched:
            continue
        entry = {"pair": key, **val}
        # 议会动态：查共现历史，若共议≥2 次，张力演化
        if a != "邹蕴" and b != "四核心":
            rels_a = load_relations(a)
            rel = rels_a.get(b, {})
            n = rel.get("co_meetings", 0)
            if n >= 2:
                topics = rel.get("topics", []) or []
                t_str = "、".join(topics[:3]) if topics else "—"
                # 演化方向：共议多次，张力从"碰撞"转"磨合"（预设交锋→实战收敛/深化）
                entry["evolution"] = f"已共议{n}次（{t_str}），张力经实战磨合——交锋点从'谁先'转向'如何协同'"
        out.append(entry)
    return out


def main():
    ap = argparse.ArgumentParser(description="圣人张力查询——议会灵魂机制")
    ap.add_argument("--roster", required=True, help="入会名单,逗号分隔")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    roster = [n.strip() for n in args.roster.split(",") if n.strip()]
    tensions = load_tensions()
    rel = relevant_tensions(roster, tensions)
    if args.json:
        print(json.dumps(rel, ensure_ascii=False, indent=2)); return
    if not rel:
        print("[邹蕴] 本名单无预设张力对（单人或无核心碰撞）。")
        return
    print("[邹蕴] 入会张力（驱动辩论交锋，非各说各话）：")
    for t in rel:
        evo = t.get("evolution", "")
        evo_part = f" ｜ 🔄{evo}" if evo else ""
        print(f"  ⚡ {t['pair']}（{t.get('axis','')}）：{t.get('交锋点','')}{evo_part}")


if __name__ == "__main__":
    main()
