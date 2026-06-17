#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
算鱼圣人记忆 · 记录器 (record_memory.py)

议会一次议事结束后调用：把每位入会圣人的本次经历追加进他的记忆档案，
并增量更新其「演化画像」(专长偏好 / 常提观点 / 风险偏好 / 立场倾向)。

用法:
  python record_memory.py --sage 王升 \
      --topic "把OA审查意见答复做成AI辅助流水线" \
      --meeting-id SPTLER-202606171430 \
      --mode 复杂会议 \
      --verdict 通过 \
      --stance 赞成 \
      --weight 3.0 \
      --reason "骨架清晰，先拆输入输出评估三段，再铸成可复用Prompt模具。" \
      --ideas "先建权利要求骨架;AI初稿+人工复核双轨;异常OA单独建模板" \
      --recommendation "建议把高频OA类型先做成3个种子模板，跑通再扩。"

也可一次性批量写入多个圣人（--batch <json_file>），用于一次议会记录所有与会者。
"""
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# Windows 控制台默认 GBK，强制 UTF-8 输出
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# 记忆目录：默认技能根目录下的 memories/；可用 --mem-dir 覆盖
DEFAULT_MEM_DIR = Path(__file__).resolve().parent.parent / "memories"
MEM_DIR = DEFAULT_MEM_DIR


def ensure_dir():
    MEM_DIR.mkdir(parents=True, exist_ok=True)


def memory_path(sage: str) -> Path:
    return MEM_DIR / f"{sage}.json"


def auto_meeting_id() -> str:
    return "SPTLER-" + datetime.now().strftime("%Y%m%d%H%M%S")


def _fresh_profile() -> dict:
    """每次返回全新的默认画像（深拷贝，避免多圣人共享可变对象）。"""
    return {
        "total_meetings": 0,
        "domains": {},
        "stances": {"赞成": 0, "反对": 0, "弃权": 0},
        "verdicts": {"通过": 0, "否决": 0},
        "frequent_views": [],
        "risk_tendency": "未知",
        "specialty_focus": [],
        "last_updated": "",
    }


def _normalize_profile(profile: dict) -> dict:
    """对已存在文件做 schema 补全：确保所有期望键存在，缺则补默认。"""
    base = {
        "total_meetings": 0,
        "domains": {},
        "stances": {},
        "verdicts": {},
        "frequent_views": [],
        "risk_tendency": "未知",
        "specialty_focus": [],
        "last_updated": "",
    }
    base.update(profile or {})
    # stances / verdicts 子键补全
    for k in ("赞成", "反对", "弃权"):
        base["stances"][k] = int(base["stances"].get(k, 0))
    for k in ("通过", "否决"):
        base["verdicts"][k] = int(base["verdicts"].get(k, 0))
    if not isinstance(base.get("frequent_views"), list):
        base["frequent_views"] = []
    if not isinstance(base.get("specialty_focus"), list):
        base["specialty_focus"] = []
    if not isinstance(base.get("domains"), dict):
        base["domains"] = {}
    base["total_meetings"] = int(base.get("total_meetings", 0) or 0)
    return base


def load_memory(sage: str) -> dict:
    p = memory_path(sage)
    if not p.exists():
        return {
            "sage": sage,
            "created_at": datetime.now().strftime("%Y-%m-%d"),
            "experiences": [],
            "profile": _fresh_profile(),
        }
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        print(f"⚠️  {sage} 记忆文件损坏，将重建：{e}", file=sys.stderr)
        return {
            "sage": sage,
            "created_at": datetime.now().strftime("%Y-%m-%d"),
            "experiences": [],
            "profile": _fresh_profile(),
        }
    if not isinstance(data, dict):
        data = {}
    data.setdefault("sage", sage)
    data.setdefault("experiences", [])
    if not isinstance(data.get("experiences"), list):
        data["experiences"] = []
    data["profile"] = _normalize_profile(data.get("profile", {}))
    return data


def infer_domain(topic: str) -> str:
    """从议题粗判领域，用于画像的 domains 计数。"""
    if not topic:
        return "其他"
    rules = [
        ("结构/专利", ["结构", "权利要求", "专利", "骨架", "边界"]),
        ("控制/流程", ["控制", "流程", "安全", "兜底", "监控", "审计"]),
        ("AI/铸模", ["ai", "prompt", "铸模", "模型", "工作流", "agent", "智能体"]),
        ("数据/检索", ["数据", "检索", "语义", "向量", "schema"]),
        ("价值/战略", ["价值", "客户", "战略", "roi", "资产", "市场"]),
        ("机械/装配", ["机械", "装配", "连接", "制造", "工装"]),
        ("整车/硬科技", ["整车", "半导体", "芯片", "电力", "轨道"]),
        ("跨界/集成", ["跨界", "集成", "场景", "模块复用"]),
        ("生命/材料", ["生物", "医药", "材料", "化工", "锂电"]),
        ("可靠性/度量", ["冗余", "可靠", "度量", "指标", "评价", "失效"]),
        ("平台/复用", ["平台", "复用", "中台", "底座"]),
        ("流水线/OA", ["流水线", "oa", "长链路", "节点"]),
    ]
    t = topic.lower()
    for label, kws in rules:
        if any(k in t for k in kws):
            return label
    return "其他"


def update_profile(profile: dict, exp: dict):
    """根据本次经历增量更新画像。"""
    profile["total_meetings"] = profile.get("total_meetings", 0) + 1

    domain = exp.get("domain") or "其他"
    profile.setdefault("domains", {})
    profile["domains"][domain] = profile["domains"].get(domain, 0) + 1

    stance = exp.get("stance") or "弃权"
    profile.setdefault("stances", {})
    for k in ("赞成", "反对", "弃权"):
        profile["stances"].setdefault(k, 0)
    if stance in profile["stances"]:
        profile["stances"][stance] += 1

    verdict = exp.get("verdict") or ""
    profile.setdefault("verdicts", {})
    for k in ("通过", "否决"):
        profile["verdicts"].setdefault(k, 0)
    if verdict in profile["verdicts"]:
        profile["verdicts"][verdict] += 1

    # 常提观点：从 ideas / recommendation 提取关键词短句（兼容全角；和半角;）
    views = []
    ideas = exp.get("ideas") or ""
    if ideas:
        import re as _re
        views = [s.strip() for s in _re.split(r"[;；]", ideas) if s.strip()][:3]
    rec = exp.get("recommendation") or ""
    if rec:
        views.append(rec)
    freq = profile.get("frequent_views", [])
    if not isinstance(freq, list):
        freq = []
    for v in views:
        found = next((x for x in freq if x.get("text") == v), None)
        if found:
            found["count"] = found.get("count", 1) + 1
        else:
            freq.append({"text": v, "count": 1})
    freq.sort(key=lambda x: x.get("count", 1), reverse=True)
    profile["frequent_views"] = freq[:12]

    # 风险偏好：反对率越高越偏保守/审慎
    total = sum(profile["stances"].values()) or 1
    oppose_rate = profile["stances"]["反对"] / total
    if oppose_rate >= 0.4:
        profile["risk_tendency"] = "审慎保守"
    elif oppose_rate <= 0.15 and profile["stances"]["赞成"] >= 3:
        profile["risk_tendency"] = "积极进取"
    else:
        profile["risk_tendency"] = "平衡中立"

    # 专长焦点：取 domains 中前 3
    doms = sorted(profile["domains"].items(), key=lambda x: x[1], reverse=True)
    profile["specialty_focus"] = [d for d, _ in doms[:3]]

    profile["last_updated"] = datetime.now().strftime("%Y-%m-%d")


def record_one(sage: str, exp: dict, verbose: bool = True) -> dict:
    mem = load_memory(sage)
    if "domain" not in exp or not exp["domain"]:
        exp["domain"] = infer_domain(exp.get("topic", ""))
    exp["recorded_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    mem["experiences"].append(exp)
    update_profile(mem["profile"], exp)
    memory_path(sage).write_text(
        json.dumps(mem, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    if verbose:
        print(f"✅ {sage}：记录第 {len(mem['experiences'])} 次经历（领域={exp['domain']}，立场={exp.get('stance','')}）")
    return mem


def main():
    ap = argparse.ArgumentParser(description="记录一位圣人的议会经历并更新画像")
    ap.add_argument("--sage", help="圣人姓名")
    ap.add_argument("--topic", help="议题")
    ap.add_argument("--meeting-id", dest="meeting_id", help="决议编号")
    ap.add_argument("--mode", default="", help="会议模式")
    ap.add_argument("--verdict", default="", help="通过/否决")
    ap.add_argument("--stance", default="弃权", help="赞成/反对/弃权")
    ap.add_argument("--weight", default="", help="本次权重")
    ap.add_argument("--reason", default="", help="投票理由")
    ap.add_argument("--ideas", default="", help="本次设想（分号分隔）")
    ap.add_argument("--recommendation", default="", help="最终建议")
    ap.add_argument("--meeting-type", default="regular", help="regular/followup")
    ap.add_argument("--parent-meeting-id", default="", help="续议对应的原会议ID")
    ap.add_argument("--followup-type", default="", help="解释型/行动项型/风险复核型/修正型/重投票型")
    ap.add_argument("--followup-target", default="", help="续议对象：行动项/圣人/风险点/方案/投票")
    ap.add_argument("--batch", help="批量 JSON 文件路径（覆盖单条参数）；传 - 表示从 stdin 读取")
    ap.add_argument("--mem-dir", help="覆盖记忆目录（默认：技能目录/memories）")
    args = ap.parse_args()

    global MEM_DIR
    if args.mem_dir:
        MEM_DIR = Path(args.mem_dir).expanduser().resolve()

    ensure_dir()

    if args.batch:
        try:
            if args.batch == "-":
                # Windows/Git Bash 下 sys.stdin 文本解码可能使用本地编码，导致中文乱码；强制按 UTF-8 读取 bytes。
                raw = sys.stdin.buffer.read().decode("utf-8-sig")
                data = json.loads(raw)
            else:
                data = json.loads(Path(args.batch).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            print(f"❌ 无法读取 batch 文件 {args.batch}：{e}", file=sys.stderr)
            sys.exit(1)
        if not isinstance(data, dict):
            print("❌ batch 文件根结构必须是 JSON 对象", file=sys.stderr)
            sys.exit(1)
        # null 值统一转空串（避免 .get(k,"") 在值为 null 时返回 None）
        base = {k: (data.get(k) or "") for k in (
            "topic", "meeting_id", "mode", "verdict",
            "meeting_type", "parent_meeting_id", "followup_type", "followup_target",
        )}
        if not base["meeting_id"]:
            prefix = "SPTLER-FOLLOWUP-" if base.get("meeting_type") == "followup" else "SPTLER-"
            base["meeting_id"] = prefix + datetime.now().strftime("%Y%m%d%H%M%S")
        attendees = data.get("attendees") or []
        if not isinstance(attendees, list):
            attendees = []
        recorded = 0
        for att in attendees:
            if not isinstance(att, dict):
                continue
            sage = att.get("sage")
            if not sage:
                print("⚠️  跳过一条缺 sage 的记录", file=sys.stderr)
                continue
            exp = {
                "topic": base["topic"],
                "meeting_id": base["meeting_id"],
                "mode": base["mode"],
                "verdict": base["verdict"],
                "meeting_type": base.get("meeting_type") or "regular",
                "parent_meeting_id": base.get("parent_meeting_id") or "",
                "followup_type": base.get("followup_type") or "",
                "followup_target": base.get("followup_target") or "",
                "stance": att.get("stance") or "弃权",
                "weight": att.get("weight") or "",
                "reason": att.get("reason") or "",
                "ideas": att.get("ideas") or "",
                "recommendation": att.get("recommendation") or "",
            }
            record_one(sage, exp)
            recorded += 1
        print(f"\n共记录 {recorded} 位圣人。")
        return

    if not args.sage:
        ap.error("需要 --sage 或 --batch")

    exp = {
        "topic": args.topic or "",
        "meeting_id": args.meeting_id or auto_meeting_id(),
        "mode": args.mode,
        "verdict": args.verdict,
        "meeting_type": args.meeting_type or "regular",
        "parent_meeting_id": args.parent_meeting_id or "",
        "followup_type": args.followup_type or "",
        "followup_target": args.followup_target or "",
        "stance": args.stance,
        "weight": args.weight,
        "reason": args.reason,
        "ideas": args.ideas,
        "recommendation": args.recommendation,
    }
    record_one(args.sage, exp)


if __name__ == "__main__":
    main()
