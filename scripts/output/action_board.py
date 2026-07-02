#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
算鱼议会 · 行动项看板 (action_board.py)

跨会议聚合所有未完成行动项，按责任人/优先级排序，可标记完成。
让议会产出的行动项不再写完就丢。

用法:
  python scripts/output/action_board.py                      # 看所有未完成行动项
  python scripts/output/action_board.py --by-owner           # 按责任人分组
  python scripts/output/action_board.py --done 3             # 标记行动项3完成（meeting_id:序号）
  python scripts/output/action_board.py --meeting-id SPTLER-xxx --item 2 --done
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


def save_index(meetings_dir, entries):
    (meetings_dir / "index.json").write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")


def collect_actions(entries):
    """收集所有行动项，带来源会议信息。"""
    out = []
    for e in entries:
        mid = e.get("meeting_id", "")
        topic = e.get("topic", "")
        for a in (e.get("action_items") or []):
            if isinstance(a, dict):
                out.append({**a, "meeting_id": mid, "topic": topic})
    return out


def main():
    ap = argparse.ArgumentParser(description="行动项看板——跨会议跟踪")
    ap.add_argument("--by-owner", action="store_true", help="按责任人分组")
    ap.add_argument("--done", action="store_true", help="标记完成（需配 --meeting-id --item）")
    ap.add_argument("--meeting-id", default="")
    ap.add_argument("--item", type=int, default=0)
    ap.add_argument("--meetings-dir", default="")
    ap.add_argument("--all", action="store_true", help="含已完成")
    args = ap.parse_args()
    md = Path(args.meetings_dir).expanduser().resolve() if args.meetings_dir else default_meetings_dir()
    entries = load_index(md)
    if not entries:
        print("（暂无会议记录）")
        return

    # 标记完成
    if args.done and args.meeting_id and args.item:
        for e in entries:
            if e.get("meeting_id") == args.meeting_id:
                for a in (e.get("action_items") or []):
                    if isinstance(a, dict) and a.get("id") == args.item:
                        a["done"] = True
                        save_index(md, entries)
                        print(f"✅ 已标记完成：{e.get('meeting_id')} 行动项{args.item} {a.get('title','')}")
                        return
        print(f"（未找到 {args.meeting_id} 的行动项{args.item}）")
        return

    actions = collect_actions(entries)
    if not args.all:
        actions = [a for a in actions if not a.get("done")]

    if not actions:
        print("🎉 所有行动项已完成（用 --all 查看含已完成的）")
        return

    prio_order = {"P0": 0, "P1": 1, "P2": 2}
    if args.by_owner:
        by_owner = {}
        for a in actions:
            owner = a.get("owner", "未指派")
            by_owner.setdefault(owner, []).append(a)
        for owner in sorted(by_owner.keys()):
            print(f"\n══ {owner} ══")
            for a in sorted(by_owner[owner], key=lambda x: prio_order.get(x.get("priority", "P2"), 2)):
                done = "✅" if a.get("done") else "⬜"
                print(f"  {done} [{a.get('priority','')}] {a.get('title','')}（{a.get('meeting_id','')}）")
                if a.get("acceptance"):
                    print(f"      验收：{a['acceptance']}")
    else:
        print(f"═══ 未完成行动项看板（{len(actions)}项）═══")
        for a in sorted(actions, key=lambda x: prio_order.get(x.get("priority", "P2"), 2)):
            done = "✅" if a.get("done") else "⬜"
            print(f"\n{done} [{a.get('priority','')}] {a.get('title','')}")
            print(f"  责任：{a.get('owner','')}｜来源：{a.get('meeting_id','')}（{a.get('topic','')}）")
            if a.get("collaborators"):
                print(f"  协作：{'、'.join(a['collaborators'])}")
            if a.get("acceptance"):
                print(f"  验收：{a['acceptance']}")


if __name__ == "__main__":
    main()
