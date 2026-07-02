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


def relevant_tensions(roster, tensions):
    """返回入会名单中两两相关的张力对。"""
    roster_set = {n.strip() for n in roster if n.strip()}
    out = []
    for key, val in tensions.items():
        # key 形如 "王升-张鑫" 或 "邹蕴-四核心"
        parts = key.split("-")
        if len(parts) == 2:
            a, b = parts
            # 四核心 是个组，若名单含任一核心且含邹蕴则命中
            if b == "四核心":
                if "邹蕴" in roster_set and any(c in roster_set for c in ["王升", "张鑫", "徐奕阳", "范征"]):
                    out.append({"pair": key, **val})
            elif a in roster_set and b in roster_set:
                out.append({"pair": key, **val})
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
        print(f"  ⚡ {t['pair']}（{t.get('axis','')}）：{t.get('交锋点','')}")


if __name__ == "__main__":
    main()
