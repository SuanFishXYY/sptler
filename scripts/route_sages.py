#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
算鱼圣人自动路由器 (route_sages.py)

根据议题、会议模式和用户指定邀请名单，推荐入会圣人、权重与入会理由。
用于 Phase 1，减少模型手动路由不稳定。

用法:
  python scripts/route_sages.py --topic "OA审查意见答复AI流水线" --mode dynamic
  python scripts/route_sages.py --topic "数据平台" --mode fast --invites 陆一帆,孙高德
  python scripts/route_sages.py --topic "整车传感器冗余" --mode complex --json
"""
import argparse
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

HOST = "邹蕴"
CORE = ["王升", "张鑫", "徐奕阳", "范征"]
CHIEFS = ["孙高德", "蔡悦", "黄嵩泉"]
WEIGHTS = {HOST: 0, **{n: 3.0 for n in CORE}, **{n: 2.0 for n in CHIEFS}}

SAGES = {
    "王升": {"role": "四核心", "title": "结构圣", "keywords": "结构 骨架 维度 边界 中间层 分层 模块 框架 系统 架构 专利 权利要求 坐标 权重 复杂 全景"},
    "张鑫": {"role": "四核心", "title": "控制圣", "keywords": "控制 输入 输出 异常 兜底 接管 流程 监控 审计 回退 权限 安全 加密 故障 自愈 风险 验证"},
    "徐奕阳": {"role": "四核心", "title": "铸模圣", "keywords": "铸模 模板 复用 自动化 ai prompt 标准化 资产化 工作流 产品化 场景 智能体 agent 推理 垂直模型"},
    "范征": {"role": "四核心", "title": "价值圣", "keywords": "价值 客户 roi 收益 回报 衡量 落点 为谁 兑现 战略 长期 资产 行业 标准 陪伴 市场"},
    "孙高德": {"role": "委员会首席", "title": "平台圣", "keywords": "平台 底座 复用 数据治理 学习共同体 服务 产品化 平台化 资产 能力中台 连接 枢纽"},
    "蔡悦": {"role": "委员会首席", "title": "跨界圣", "keywords": "跨界 跨域 集成 场景 模块复用 迁移 5g 射频 太阳能 燃料电池 智能终端 车辆 参数调优 连接"},
    "黄嵩泉": {"role": "委员会首席", "title": "组合圣", "keywords": "冗余 组合 传感器 光源 光学 测量 电气 隔离 失效 备份 可靠 发明 工程冗余 单点"},
    "喻学兵": {"role": "专科", "title": "连接圣", "keywords": "连接 装配 配合 方位 公差 热失配 制造 工装 机械 实体 现场 装配序列"},
    "卢若雨": {"role": "专科", "title": "位控圣", "keywords": "位置 边界 精修 复审 反驳 权利要求 语言 翻译 控制节点 空间定位 实施例"},
    "顾峻峰": {"role": "专科", "title": "现场组合圣", "keywords": "现场 客户 模块化 可拆卸 节俭 废物 资源化 耐用 工地 车间 实物 落地 痛点"},
    "骆希聪": {"role": "专科", "title": "整车集成圣", "keywords": "整车 集成 机电软 子系统 制造 试验 安全 跨域整合 汽车 轨道 整机"},
    "徐伟": {"role": "专科", "title": "通桥圣", "keywords": "半导体 电力电子 车规 轨道 硬科技 架构 全栈 系统 桥接 电力 芯片"},
    "钱文宇": {"role": "专科", "title": "生命工艺圣", "keywords": "生物 生命 医药 制药 工艺 生物工艺 基因 酶 发酵 稳定性 医疗"},
    "陈哲锋": {"role": "专科", "title": "材料工艺圣", "keywords": "材料 化工 锂电 高分子 参数 配方 放大 工艺 反应 组分 复合"},
    "陆一帆": {"role": "专科", "title": "数据炼金圣", "keywords": "数据 飞轮 检索 语义 向量 schema 可观测 指标 清洗 聚合 数据治理 召回"},
    "金辰宇": {"role": "专科", "title": "接口圣", "keywords": "接口 协议 契约 前端 网页 事件流 api 对接 交互 入口 端"},
    "徐骋": {"role": "专科", "title": "流式圣", "keywords": "流水线 长链路 状态图 节点 事件 流式 oa 翻译 质量闭环 编排 异步"},
    "陈方移": {"role": "专科", "title": "基座圣", "keywords": "基座 安全 合规 访问控制 审计 留痕 变更 审批 运维 部署 回退 it 底座"},
    "陈彤": {"role": "专科", "title": "流程圣", "keywords": "流程 oa 节点 字段 标准化 可追溯 官文 答复 审查意见 流程图 规则"},
    "江漪": {"role": "专科", "title": "闭环圣", "keywords": "流体 闭环 传感器 控制器 执行器 卫浴 水质 回路 密封 管路 物理"},
    "陆诗杰": {"role": "专科", "title": "度量圣", "keywords": "指标 评价 度量 量化 评分 权重 可视化 看板 平台 对接 算法 向量 评价体系"},
}

for n in SAGES:
    WEIGHTS.setdefault(n, 1.0)


def load_rules() -> dict:
    path = Path(__file__).resolve().parent.parent / "references" / "routing_rules.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


RULES = load_rules()
TRACK_RULES = RULES.get("tracks", {})
WEIGHT_RULES = RULES.get("weights", {})
STRATEGIC_KWS = TRACK_RULES.get("formal_keywords", "战略 规划 平台 建设 是否 方向 预算 资源 不可逆 制度 组织".split())
MEDIUM_MARKERS = TRACK_RULES.get("medium_markers", ["ai", "平台", "流程", "数据", "跨界", "系统", "流水线", "产品"])
FALLBACK_ORDER = RULES.get("fallback_order", ["徐奕阳", "王升", "孙高德", "张鑫", "范征"])
MUST_INCLUDE_BY_DOMAIN = RULES.get("must_include_by_domain", {})


def tokens(text: str) -> set[str]:
    text = (text or "").lower()
    # 兼容中英文：保留连续英文/数字，以及中文2字以上滑窗关键词通过包含匹配完成
    parts = set(re.findall(r"[a-z0-9_]+", text))
    for i in range(len(text) - 1):
        ch = text[i:i+2]
        if re.match(r"[一-鿿]{2}", ch):
            parts.add(ch)
    return parts


def score_sage(topic: str, sage: str, ignore_core_bias: bool = False) -> tuple[float, list[str]]:
    info = SAGES[sage]
    t = topic.lower()
    score = 0.0
    hits = []
    for kw in info["keywords"].split():
        if kw.lower() in t:
            score += 3 if len(kw) >= 2 else 1
            hits.append(kw)
    # 四核心/首席由 min_core 和委员会必到规则保障；这里只给轻微基础分，避免无关核心压过命中关键词的专科。
    # verdict 单圣人裁决时关闭核心偏袒，纯按专业匹配度——让专科（如卢若雨边界精修）有机会胜出。
    if not ignore_core_bias:
        if sage in CORE:
            score += 1.0
        if sage in CHIEFS:
            score += 0.5
    return score, hits[:5]


def decide_track(topic: str, track: str = "auto") -> tuple[str, str]:
    """返回 (track, reason)。verdict=单圣人裁决，fast=快速轨，formal=正式轨，followup=续议轨。"""
    t = (topic or "").lower()
    tr = (track or "auto").lower()
    if tr in ("fast", "快速", "quick"):
        return "fast", "用户指定快速轨"
    if tr in ("formal", "正式", "complex"):
        return "formal", "用户指定正式轨"
    if tr in ("followup", "续议"):
        return "followup", "用户指定续议轨"
    if tr in ("verdict", "裁决", "单圣人"):
        return "verdict", "用户指定单圣人裁决"
    formal_hits = [k for k in STRATEGIC_KWS if k in topic]
    chief_domains = sum(any(k in t for k in SAGES[s]["keywords"].split()) for s in CHIEFS)
    medium_markers = sum(k in t for k in MEDIUM_MARKERS)
    if formal_hits:
        return "formal", f"命中正式轨信号：{'、'.join(formal_hits[:3])}"
    if chief_domains >= 2:
        return "formal", "跨多个委员会领域，进入正式轨"
    medium_markers = sum(k in t for k in MEDIUM_MARKERS)
    if medium_markers >= 2:
        return "fast", "中等复杂但未触发正式轨，先走快速轨"
    # 单一明确、单领域、无战略信号 → 单圣人裁决（最轻量，3 句话出结论）
    if medium_markers == 0 and chief_domains <= 1:
        return "verdict", "单一明确问题，单圣人裁决"
    return "fast", "单一明确议题，默认快速轨"


def mode_size(mode: str, topic: str, track: str = "auto") -> tuple[int, str, str, str]:
    resolved_track, track_reason = decide_track(topic, track)
    mode = (mode or "dynamic").lower()
    if resolved_track == "verdict":
        return 1, "单圣人裁决", resolved_track, track_reason
    if resolved_track == "followup":
        return int(TRACK_RULES.get("followup_size", 3)), "续议轨", resolved_track, track_reason
    if mode in ("fast", "quick", "快速", "快速会议"):
        return int(TRACK_RULES.get("fast_size", 4)), "快速会议", resolved_track, track_reason
    if mode in ("complex", "deep", "复杂", "复杂会议"):
        return int(TRACK_RULES.get("formal_size", 8)), "复杂会议", resolved_track, track_reason
    if resolved_track == "formal":
        return int(TRACK_RULES.get("formal_size", 8)), "动态分辨→正式轨/复杂规格", resolved_track, track_reason
    # fast track auto sizing
    t = topic.lower()
    medium_markers = sum(k in t for k in MEDIUM_MARKERS)
    if medium_markers >= 2:
        return int(TRACK_RULES.get("medium_size", 6)), "动态分辨→快速轨/中等规格", resolved_track, track_reason
    return int(TRACK_RULES.get("fast_size", 4)), "动态分辨→快速轨/简报规格", resolved_track, track_reason


def normalize_invites(invites: str) -> list[str]:
    if not invites:
        return []
    raw = re.split(r"[,，、\s]+", invites.strip())
    out = []
    for x in raw:
        if x in SAGES and x not in out:
            out.append(x)
    return out


def route(topic: str, mode: str = "dynamic", invites: str = "", track: str = "auto") -> dict:
    target_size, resolved_mode, resolved_track, track_reason = mode_size(mode, topic, track)
    invited = normalize_invites(invites)
    roster = []
    reasons = {}

    def add(name, reason, score=0, hits=None):
        if name not in roster:
            roster.append(name)
            reasons[name] = {"reason": reason, "score": score, "hits": hits or [], "invited": name in invited}

    for n in invited:
        add(n, "用户指定邀请", 999, [])

    # 委员会首席：匹配即必到
    for chief in CHIEFS:
        sc, hits = score_sage(topic, chief)
        if hits:
            add(chief, f"委员会首席命中：{'、'.join(hits)}", sc, hits)

    # 配置化领域必到：如 数据/检索 -> 陆一帆，接口/前端 -> 金辰宇
    for domain, names in MUST_INCLUDE_BY_DOMAIN.items():
        parts = re.split(r"[/、]", domain)
        if any(p and p.lower() in topic.lower() for p in parts):
            for name in names:
                if name in SAGES:
                    add(name, f"领域必到：{domain}", 50, parts)

    # 至少核心（verdict 单圣人裁决不强制核心）
    core_scores = [(score_sage(topic, c), c) for c in CORE]
    core_scores.sort(key=lambda x: x[0][0], reverse=True)
    if resolved_track == "verdict":
        min_core = 0
    elif "复杂" in resolved_mode or any(k in topic for k in STRATEGIC_KWS):
        min_core = 2
    else:
        min_core = 1
    current_core = sum(1 for n in roster if n in CORE)
    for (sc_hits, c) in core_scores:
        if current_core >= min_core:
            break
        sc, hits = sc_hits
        add(c, f"核心席位保障：{'、'.join(hits) if hits else SAGES[c]['title']}", sc, hits)
        current_core += 1

    # 其余按分数补齐（verdict 时关闭核心偏袒，纯专业匹配）
    ignore_bias = (resolved_track == "verdict")
    scored = []
    for n in SAGES:
        sc, hits = score_sage(topic, n, ignore_core_bias=ignore_bias)
        if sc > 0:
            scored.append((sc, n, hits))
    # verdict 单圣人裁决：同分时专科优先（找最专业匹配者，而非最高权重者）
    if ignore_bias:
        # 专科(1.0) > 首席(2.0) > 核心(3.0)：专业优先，权重作降序的次要键需反转
        def verdict_key(x):
            sc, n, _ = x
            role_rank = 0 if n not in CORE and n not in CHIEFS else (1 if n in CHIEFS else 2)
            return (sc, -role_rank)
        scored.sort(key=verdict_key, reverse=True)
    else:
        scored.sort(key=lambda x: (x[0], WEIGHTS[x[1]]), reverse=True)
    for sc, n, hits in scored:
        if len(roster) >= target_size:
            break
        add(n, f"关键词命中：{'、'.join(hits) if hits else '角色保障'}", sc, hits)

    # 兜底：不足则补平台/结构/铸模
    for n in FALLBACK_ORDER:
        if len(roster) >= target_size:
            break
        add(n, "兜底补位", 0, [])

    attendees = []
    for n in roster:
        base = WEIGHTS[n]
        boost = 0.0
        # 动态加成：分数最高的非邀请前两位 +0.5
        attendees.append({
            "name": n,
            "title": SAGES[n]["title"],
            "role": SAGES[n]["role"],
            "weight": base + boost,
            "base_weight": base,
            "dynamic_boost": boost,
            **reasons[n],
        })
    # 给分数最高的前两位加成（不含host，且必须有命中）
    # 动态加成只给关键词高度契合者；用户邀请本身不等于议题契合，因此排除 invited。
    boostable = [a for a in attendees if a["score"] > 0 and a.get("hits") and not a.get("invited")]
    boostable.sort(key=lambda a: a["score"], reverse=True)
    for a in boostable[:2]:
        a["dynamic_boost"] = 0.5
        a["weight"] = a["base_weight"] + 0.5
        a["reason"] += "；动态加成+0.5"

    return {
        "topic": topic,
        "mode": resolved_mode,
        "track": resolved_track,
        "track_reason": track_reason,
        "target_size": target_size,
        "host": HOST,
        "attendees": attendees,
    }


def main():
    ap = argparse.ArgumentParser(description="算鱼议会自动路由圣人")
    ap.add_argument("--topic", required=True, help="议题")
    ap.add_argument("--mode", default="dynamic", help="fast/complex/dynamic 或 中文模式")
    ap.add_argument("--track", default="auto", help="fast/formal/followup/auto 或 中文轨道")
    ap.add_argument("--invites", default="", help="用户指定邀请名单，逗号分隔")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    args = ap.parse_args()
    result = route(args.topic, args.mode, args.invites, args.track)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    print(f"[邹蕴] 路由判定：{result['mode']}（{result['track']}轨：{result['track_reason']}），目标 {result['target_size']} 人，主持=邹蕴")
    for a in result["attendees"]:
        flag = "邀请" if a.get("invited") else "自动"
        print(f"- [{a['name']}] {a['title']}｜{a['role']}｜权重 {a['weight']}｜{flag}｜{a['reason']}")


if __name__ == "__main__":
    main()
