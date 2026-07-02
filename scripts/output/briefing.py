#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
算鱼议会 · 议会简报 (briefing.py)

一键回顾上次会议（或指定会议）：结论、行动项、待办、交付物路径。
不用翻 md 文件。

用法:
  python scripts/output/briefing.py                    # 上次会议
  python scripts/output/briefing.py --meeting-id SPTLER-xxx
  python scripts/output/briefing.py --last 3           # 最近3次概览
"""
import argparse, json, sys
from pathlib import Path
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


def default_meetings_dir():
    return Path.cwd() / "sptler-meetings"


def load_index(meetings_dir):
    p = meetings_dir / "index.json"
    if not p.exists():
        return []
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return []
    if not isinstance(d, list):
        return []
    # 只保留 dict 条目：index.json 用户可编辑，可能混入非 dict（防 e.get 崩溃，同源 bug 类）
    return [e for e in d if isinstance(e, dict)]


def fmt_briefing(e: dict) -> str:
    lite_tag = " ｜ ⚡lite快调·可信度打折" if e.get("lite") else ""
    lines = [f"═══ {e.get('meeting_id','')} · {e.get('topic','')} ═══{lite_tag}"]
    lines.append(f"类型：{e.get('meeting_type','regular')}｜模式：{e.get('mode','')}｜结论：{e.get('verdict','')}")
    lines.append(f"日期：{e.get('created_at','')}")
    if e.get("result_file"):
        lines.append(f"决议：{e['result_file']}")
    if e.get("deliverable_file"):
        lines.append(f"交付物：{e['deliverable_file']}")
    actions = e.get("action_items", []) or []
    if actions:
        lines.append("行动项：")
        for a in actions:
            if isinstance(a, dict):
                done = "✅" if a.get("done") else "⬜"
                lines.append(f"  {done} {a.get('id','')}. {a.get('title','')} → {a.get('owner','')} [{a.get('priority','')}]")
            else:
                lines.append(f"  ⬜ {a}")
    attendees = e.get("attendees", []) or []
    if attendees:
        lines.append(f"与会：{'、'.join(attendees)}")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="议会简报——一键回顾")
    ap.add_argument("--meeting-id", default="")
    ap.add_argument("--last", type=int, default=0, help="最近N次概览")
    ap.add_argument("--meetings-dir", default="")
    args = ap.parse_args()
    md = Path(args.meetings_dir).expanduser().resolve() if args.meetings_dir else default_meetings_dir()
    entries = load_index(md)
    if not entries:
        print("（暂无会议记录，无法生成简报）")
        return
    if args.meeting_id:
        e = next((x for x in entries if x.get("meeting_id") == args.meeting_id), None)
        if not e:
            print(f"（未找到会议 {args.meeting_id}）")
            return
        print(fmt_briefing(e))
        return
    if args.last:
        for e in entries[-args.last:]:
            print(fmt_briefing(e))
            print()
        return
    # 默认：上一次
    print(fmt_briefing(entries[-1]))


if __name__ == "__main__":
    main()
