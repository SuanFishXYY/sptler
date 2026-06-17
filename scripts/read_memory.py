#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
算鱼圣人记忆 · 读取器 (read_memory.py)

议会 Phase 1 路由入会后调用：读取每位入会圣人的记忆摘要，
输出一段精简的「记忆注入文本」，供该圣人发言时引用过往经验。

用法:
  # 读取单个圣人（默认精简摘要）
  python read_memory.py --sage 王升

  # 读取多个圣人（入会名单），一次性输出注入块
  python read_memory.py --sages 王升,张鑫,徐奕阳,范征

  # 输出 JSON（便于程序消费）
  python read_memory.py --sages 王升,邹蕴 --json

  # 指定最近 N 次经历的详情
  python read_memory.py --sage 王升 --recent 3

无记忆档案的圣人输出「(新晋圣人，暂无议会经历)」。
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


def summarize(mem: dict, recent: int = 0) -> dict:
    """把记忆压缩成摘要。"""
    prof = mem.get("profile", {})
    exps = mem.get("experiences", [])
    summary = {
        "sage": mem.get("sage", ""),
        "total_meetings": prof.get("total_meetings", len(exps)),
        "specialty_focus": prof.get("specialty_focus", []),
        "risk_tendency": prof.get("risk_tendency", "未知"),
        "stances": prof.get("stances", {}),
        "frequent_views": prof.get("frequent_views", [])[:5],
        "last_updated": prof.get("last_updated", ""),
    }
    if recent and recent > 0:
        summary["recent_experiences"] = exps[-recent:]
    return summary


def inject_text(mem: dict, recent: int = 0) -> str:
    """生成一段可注入圣人发言上下文的中文摘要。"""
    if not mem:
        return ""
    s = summarize(mem, recent=recent)
    lines = []
    lines.append(f"【{s['sage']} 的议会记忆】共参与 {s['total_meetings']} 次议事")
    if s["specialty_focus"]:
        lines.append(f"· 专长焦点：{'、'.join(s['specialty_focus'])}")
    lines.append(f"· 风险偏好：{s['risk_tendency']}")
    st = s["stances"]
    if any(st.values()):
        lines.append(f"· 历史立场：赞成 {st.get('赞成',0)} / 反对 {st.get('反对',0)} / 弃权 {st.get('弃权',0)}")
    if s["frequent_views"]:
        views = "；".join(f"{v['text']}（{v['count']}次）" for v in s["frequent_views"][:3])
        lines.append(f"· 常提观点：{views}")
    if recent and s.get("recent_experiences"):
        lines.append("· 近期经历：")
        for e in s["recent_experiences"]:
            lines.append(
                f"    - [{e.get('recorded_at','')}] {e.get('topic','')}（{e.get('mode','')}/"
                f"{e.get('verdict','')}）：立场={e.get('stance','')}，"
                f"建议={e.get('recommendation','')[:40]}"
            )
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="读取圣人记忆摘要，供入会发言注入")
    ap.add_argument("--sage", help="单个圣人姓名")
    ap.add_argument("--sages", help="多个圣人，逗号分隔")
    ap.add_argument("--recent", type=int, default=0, help="附带最近 N 次经历详情")
    ap.add_argument("--json", action="store_true", help="输出 JSON 而非文本")
    args = ap.parse_args()

    names = []
    if args.sages:
        names = [n.strip() for n in args.sages.split(",") if n.strip()]
    elif args.sage:
        names = [args.sage.strip()]
    if not names:
        ap.error("需要 --sage 或 --sages")

    if args.json:
        out = []
        for n in names:
            mem = load_memory(n)
            out.append(summarize(mem, recent=args.recent) if mem else {"sage": n, "total_meetings": 0})
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return

    # 文本输出
    blocks = []
    for n in names:
        mem = load_memory(n)
        if not mem:
            blocks.append(f"【{n}】（新晋圣人，暂无议会经历）")
        else:
            blocks.append(inject_text(mem, recent=args.recent))
    print("\n\n".join(blocks))


if __name__ == "__main__":
    main()
