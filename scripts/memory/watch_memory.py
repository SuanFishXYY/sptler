#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
算鱼圣人 · 主动提醒记忆 (watch_memory.py)

扫描所有圣人记忆，找出与当前议题强相关、但不在入会名单里的历史记忆。
邹蕴据此主动提醒："王升上次说过X"——让记忆从被动注入变主动。

用于 Phase 1 路由后：检查是否漏了"有相关经验但没入会"的圣人。

用法:
  python scripts/memory/watch_memory.py --topic "OA答复AI流水线" --roster 王升,张鑫,徐奕阳
  python scripts/memory/watch_memory.py --topic "权利要求边界" --json
"""
import argparse, json, re, sys
from pathlib import Path
from datetime import datetime
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent.parent
MEM_DIR_DEFAULT = ROOT / "memories"


def load(path):
    try: return json.loads(path.read_text(encoding="utf-8"))
    except Exception: return None


def recency_days(recorded_at):
    try:
        return max(0, (datetime.now() - datetime.strptime(recorded_at[:10], "%Y-%m-%d")).days)
    except Exception:
        return 9999


def time_decay(days):
    if days <= 90: return 1.0
    if days <= 365: return 0.7
    if days <= 730: return 0.4
    return 0.15


def relevance(exp, topic):
    """一条经历对议题的相关度分。排除 superseded。"""
    if exp.get("superseded"):
        return 0, []
    t = topic.lower()
    et = (exp.get("topic", "") or "").lower()
    ed = exp.get("domain", "") or ""
    s = 0
    hits = []
    for part in re.split(r"[/、 ]", ed):
        p = part.strip().lower()
        if p and len(p) >= 2 and p in t:
            s += 5; hits.append(p)
    for bg in {et[i:i+2] for i in range(len(et)-1) if re.match(r"[一-鿿]{2}", et[i:i+2])}:
        if bg in t:
            s += 2; hits.append(bg)
    if s == 0:
        return 0, []
    days = recency_days(exp.get("recorded_at", ""))
    final = s * time_decay(days) * (exp.get("value_score", 1) or 1)
    return final, hits


def watch(topic, roster, mem_dir):
    roster_set = {n.strip() for n in (roster or "").split(",") if n.strip()}
    alerts = []
    for p in sorted(mem_dir.glob("*.json")):
        sage = p.stem
        mem = load(p)
        if not mem:
            continue
        if not isinstance(mem, dict):
            continue  # 非记忆文件（如杂散 list json）跳过，避免 .get 崩溃
        best = None
        for e in (mem.get("experiences", []) or []):
            sc, hits = relevance(e, topic)
            if sc > 0 and (best is None or sc > best[0]):
                best = (sc, e, hits)
        if best and best[0] >= 4:  # 阈值：足够相关才提醒
            sc, e, hits = best
            in_roster = sage in roster_set
            alerts.append({
                "sage": sage,
                "score": round(sc, 2),
                "in_roster": in_roster,
                "topic": e.get("topic", ""),
                "stance": e.get("stance", ""),
                "recommendation": e.get("recommendation", ""),
                "days_ago": recency_days(e.get("recorded_at", "")),
                "value_score": e.get("value_score", 0),
            })
    alerts.sort(key=lambda x: x["score"], reverse=True)
    return alerts


def main():
    ap = argparse.ArgumentParser(description="主动提醒记忆——扫描未入会圣人的相关历史记忆")
    ap.add_argument("--topic", required=True)
    ap.add_argument("--roster", default="", help="当前入会名单，逗号分隔")
    ap.add_argument("--mem-dir", default="")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    mem_dir = Path(args.mem_dir).expanduser().resolve() if args.mem_dir else MEM_DIR_DEFAULT
    if not mem_dir.exists():
        print("（暂无 memories 目录，无主动提醒）")
        return
    alerts = watch(args.topic, args.roster, mem_dir)
    if args.json:
        print(json.dumps(alerts, ensure_ascii=False, indent=2))
        return
    # 只提醒"未入会但有强相关记忆"的圣人（入会的已在召唤时注入）
    missed = [a for a in alerts if not a["in_roster"]]
    if not missed:
        print("[邹蕴] 无主动提醒——相关记忆的圣人均已入会，或暂无强相关历史。")
        return
    print("[邹蕴] 主动提醒：以下圣人虽未入会，但有相关历史记忆，可考虑邀请或引用：")
    for a in missed[:5]:
        age = f"{a['days_ago']//365}年前" if a["days_ago"] >= 365 else f"{a['days_ago']}天前"
        print(f"  - [{a['sage']}] {age}议过「{a['topic']}」：{a['stance']}，建议={a['recommendation']}（相关度{a['score']}·价值{a['value_score']}）")


if __name__ == "__main__":
    main()
