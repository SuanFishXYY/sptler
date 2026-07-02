#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
算鱼议会 · 传承谱系查询 (lineage.py)

传承哲学机制：圣人谱系——师承链 + 传承包。
老圣人退场时把演化命题+失败模式+共议张力蒸馏成传承包，接班圣人继承。

用法:
  python scripts/saints/lineage.py --sage 王升              # 查王升师承链
  python scripts/saints/lineage.py --sage 王升 --inheritance # 查王升的传承包(给接班人)
  python scripts/saints/lineage.py --sage 王升 --json
"""
import argparse, json, re, sys
from pathlib import Path
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent.parent
SAINTS = ROOT / "saints"


def read_field(sage, field):
    """从 IDENTITY.md 读某字段值。"""
    p = SAINTS / sage / "IDENTITY.md"
    if not p.exists():
        return "（无档案）"
    for line in p.read_text(encoding="utf-8").splitlines():
        m = re.match(rf"- {re.escape(field)}：(.+)", line)
        if m:
            return m.group(1).strip()
    return "（未设）"


def first_under(text, heading):
    """提取 '## heading' 后第一个非空非标题行（首条）。"""
    in_sec = False
    for l in (text or "").strip().splitlines():
        ls = l.strip()
        if ls.startswith("## " + heading):
            in_sec = True; continue
        if in_sec and ls.startswith("## "):
            break
        if in_sec and ls:
            return ls.lstrip("-").strip().split(";")[0].strip()
    return ""


def lineage_chain(sage):
    """向上追师承链：sage → 师 → 师的师 → ..."""
    chain = [sage]
    current = sage
    seen = {sage}
    for _ in range(10):  # 防环
        master = read_field(current, "师承")
        if not master or master.startswith("（") or master in seen:
            break
        chain.append(master)
        seen.add(master)
        current = master
    return chain


def inheritance_pack(sage):
    """蒸馏传承包：演化命题 + 失败模式 + 边界 + 追问 —— 接班人继承的精华。"""
    d = SAINTS / sage
    if not d.exists():
        return {}
    soul = (d / "SOUL.md").read_text(encoding="utf-8") if (d / "SOUL.md").exists() else ""
    bdy = (d / "BOUNDARY.md").read_text(encoding="utf-8") if (d / "BOUNDARY.md").exists() else ""
    # 演化命题：查记忆转折点（若有），否则初始命题
    prop = first_under(soul, "核心命题")
    fail = first_under(soul, "失败模式")
    oppose = first_under(bdy, "必须反对")
    ask = first_under(bdy, "必须追问")
    # 查记忆的命题演化
    evo = ""
    mem_p = ROOT / "memories" / f"{sage}.json"
    if mem_p.exists():
        try:
            mem = json.loads(mem_p.read_text(encoding="utf-8"))
            for e in reversed(mem.get("experiences", []) or []):
                if isinstance(e, dict) and e.get("is_turning_point") and not e.get("superseded"):
                    evo = (e.get("recommendation", "") or e.get("reason", ""))[:60]
                    break
        except Exception:
            pass
    return {
        "sage": sage,
        "initial_proposition": prop,
        "evolved_proposition": evo or "（无转折，命题未演化）",
        "failure_mode": fail,
        "must_oppose": oppose,
        "must_ask": ask,
        "weight": read_field(sage, "议会权重"),
    }


def main():
    ap = argparse.ArgumentParser(description="圣人传承谱系查询")
    ap.add_argument("--sage", required=True)
    ap.add_argument("--inheritance", action="store_true", help="查传承包（给接班人的精华）")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.inheritance:
        pack = inheritance_pack(args.sage)
        if args.json:
            print(json.dumps(pack, ensure_ascii=False, indent=2)); return
        print(f"【{args.sage} 传承包】（接班人继承的精华）")
        print(f"· 初始命题：{pack.get('initial_proposition','—')}")
        print(f"· 演化命题：{pack.get('evolved_proposition','—')}")
        print(f"· 失败模式（自警）：{pack.get('failure_mode','—')}")
        print(f"· 必须反对（边界）：{pack.get('must_oppose','—')}")
        print(f"· 必须追问：{pack.get('must_ask','—')}")
        print(f"· 议会权重：{pack.get('weight','—')}")
        return

    chain = lineage_chain(args.sage)
    heir = read_field(args.sage, "传承给")
    if args.json:
        print(json.dumps({"chain": chain, "heir": heir}, ensure_ascii=False, indent=2)); return
    print(f"【{args.sage} 传承谱系】")
    print(f"· 师承链（向上）：{' → '.join(chain)}")
    print(f"· 传承给：{heir}")
    if len(chain) > 1:
        print(f"· 谱系深度：{len(chain) - 1} 代")


if __name__ == "__main__":
    main()
