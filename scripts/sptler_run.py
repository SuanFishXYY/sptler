#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
算鱼议会总控脚本 (sptler_run.py)

一条命令完成议会运行时的脚本编排，减少模型漏步骤，也方便非 Claude 环境调用。
分阶段执行：route → summon（预览）→ 记录模板生成 → 成长/索引/关系刷新。

模型/Claude 仍负责生成发言内容和 batch json 的实际数据；本脚本负责把脚本链跑通。

用法:
  # 1. 路由 + 召唤预览（Phase 1）
  python scripts/sptler_run.py --topic "OA审查意见答复AI流水线" --track auto --invites 陆一帆

  # 2. 议事后：记录记忆 + 成长 + 索引 + 关系（Phase 5b/5e），batch 从 stdin
  cat batch.json | python scripts/sptler_run.py --record --batch - --index-batch - --meetings-dir ./sptler-meetings

  # 3. 自检
  python scripts/sptler_run.py --check
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable


def run(cmd: list, stdin_data: bytes = None) -> tuple[int, str]:
    """运行子脚本，返回 (returncode, stdout)。"""
    try:
        r = subprocess.run(cmd, input=stdin_data, capture_output=True)
        return r.returncode, r.stdout.decode("utf-8", "replace")
    except Exception as e:
        return 1, str(e)


def cmd_phase1(args):
    """Phase 1：路由 + 对每位入会圣人召唤预览。"""
    print("═══ Phase 1：路由 + 召唤 ═══")
    route_cmd = [PY, str(ROOT / "scripts/route_sages.py"), "--topic", args.topic,
                 "--track", args.track, "--mode", args.mode, "--json"]
    if args.invites:
        route_cmd += ["--invites", args.invites]
    rc, out = run(route_cmd)
    if rc != 0:
        print(f"❌ 路由失败：{out}", file=sys.stderr); sys.exit(1)
    route = json.loads(out)
    print(f"[邹蕴] 路由判定：{route['mode']}（{route['track']}轨：{route['track_reason']}），目标 {route['target_size']} 人")
    attendees = route["attendees"]
    # 召唤预览（不回写引用计数，仅预览；实际引用计数在模型调用 summon_sage 时发生）
    print("\n═══ 召唤预览（灵魂+记忆+关系） ═══")
    for a in attendees:
        sc, sout = run([PY, str(ROOT / "scripts/summon_sage.py"), "--sage", a["name"], "--topic", args.topic, "--json"])
        if sc == 0:
            summ = json.loads(sout)
            mem = summ.get("memory", {})
            lt = mem.get("profile_longterm") or {}
            rc2 = mem.get("profile_recent") or {}
            rel = mem.get("relevant", [])
            tp = mem.get("turning_points", [])
            print(f"\n[{a['name']}] {a['title']} 权重{a['weight']}（{a.get('reason','')}）")
            print(f"  画像：底色{lt.get('risk_tendency','?')}｜近况{rc2.get('risk_tendency','?')}｜{lt.get('total_meetings',0)}次")
            if rel:
                print(f"  ⚡可引用记忆 {len(rel)} 条")
            if tp:
                print(f"  🔄转折点 {len(tp)} 条")
    print("\n═══ 路由结果 JSON（供模型填充发言）═══")
    print(json.dumps(route, ensure_ascii=False, indent=2))


def cmd_record(args):
    """Phase 5b/5e：记录记忆 + 成长 + 索引 + 关系。"""
    print("═══ Phase 5b：记录记忆 ═══")
    if args.batch == "-":
        data = sys.stdin.buffer.read()
    else:
        data = Path(args.batch).read_bytes()
    rc, out = run([PY, str(ROOT / "scripts/record_memory.py"), "--batch", "-"], stdin_data=data)
    print(out.strip())
    if rc != 0:
        print(f"❌ 记录记忆失败", file=sys.stderr); sys.exit(1)

    print("\n═══ Phase 5b：更新成长日志 ═══")
    rc, out = run([PY, str(ROOT / "scripts/update_growth.py")])
    print(out.strip())

    if args.index_batch:
        print("\n═══ Phase 5e：登记会议索引 ═══")
        if args.index_batch == "-":
            idata = sys.stdin.buffer.read() if sys.stdin.isatty() is False else None
            if idata is None:
                idata = data  # fallback
        else:
            idata = Path(args.index_batch).read_bytes()
        idx_cmd = [PY, str(ROOT / "scripts/index_meeting.py"), "--batch", "-"]
        if args.meetings_dir:
            idx_cmd += ["--meetings-dir", args.meetings_dir]
        rc, out = run(idx_cmd, stdin_data=idata)
        print(out.strip())

        print("\n═══ Phase 5e：构建关系网 ═══")
        rel_cmd = [PY, str(ROOT / "scripts/build_relations.py")]
        if args.meetings_dir:
            rel_cmd += ["--meetings-dir", args.meetings_dir]
        rc, out = run(rel_cmd)
        print(out.strip())

    print("\n═══ Phase 5 完成 ═══")


def cmd_check(args):
    """全系统自检。"""
    print("═══ 全系统自检 ═══")
    rc, out = run([PY, str(ROOT / "scripts/validate_sptler.py")])
    print(out.strip())
    if rc != 0:
        sys.exit(1)
    print()
    rc, out = run([PY, str(ROOT / "scripts/validate_saints.py")])
    print(out.strip())


def main():
    ap = argparse.ArgumentParser(description="算鱼议会总控脚本")
    sub = ap.add_subparsers(dest="cmd")

    p1 = sub.add_parser("route", help="Phase 1 路由+召唤预览")
    p1.add_argument("--topic", required=True)
    p1.add_argument("--track", default="auto")
    p1.add_argument("--mode", default="dynamic")
    p1.add_argument("--invites", default="")

    pr = sub.add_parser("record", help="Phase 5 记录+成长+索引+关系")
    pr.add_argument("--batch", required=True, help="记忆 batch json；- 为 stdin")
    pr.add_argument("--index-batch", default="", help="会议索引 batch json；- 为 stdin")
    pr.add_argument("--meetings-dir", default="")

    sub.add_parser("check", help="全系统自检")

    # 兼容无子命令的旧式调用
    ap.add_argument("--topic", default="")
    ap.add_argument("--track", default="auto")
    ap.add_argument("--mode", default="dynamic")
    ap.add_argument("--invites", default="")
    ap.add_argument("--record", action="store_true")
    ap.add_argument("--batch", default="")
    ap.add_argument("--index-batch", default="")
    ap.add_argument("--meetings-dir", default="")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    if args.cmd == "route":
        cmd_phase1(args); return
    if args.cmd == "record":
        cmd_record(args); return
    if args.cmd == "check":
        cmd_check(args); return

    # 旧式
    if args.check:
        cmd_check(args); return
    if args.record:
        cmd_record(args); return
    if args.topic:
        cmd_phase1(args); return
    ap.print_help()


if __name__ == "__main__":
    main()
