#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
算鱼议会 · 智能动态补人 (auto_invite.py)

扫描议题内容 + 当前入会名单，检查是否缺少关键能力（检索/语义/合规/边界/结构/控制/价值/铸模等），
自动建议邀请具备该能力的圣人。邹蕴据此口头确认拉入。

用法:
  python scripts/routing/auto_invite.py --topic "蓝牙模组FTO检索" --roster 卢若雨,王升
  python scripts/routing/auto_invite.py --topic "OA答复特征分析" --roster 王升,卢若雨 --json
"""
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
import route_sages as r


# 关键能力 → 能力关键词 → 具备该能力的圣人（按 priority 排序）
CAPABILITIES = {
    "特征拆解/结构分析": {
        "triggers": ["特征", "拆解", "结构", "骨架", "权利要求", "维度", "分层", "方案"],
        "sages": ["王升", "喻学兵", "骆希聪"],
    },
    "边界精修/复审": {
        "triggers": ["边界", "精修", "复审", "反驳", "位置", "实施例", "区别技术特征"],
        "sages": ["卢若雨", "王升"],
    },
    "语义扩展/检索式": {
        "triggers": ["检索", "语义", "同义词", "近义词", "分类号", "ipc", "cpc", "检索式", "召回", "查新"],
        "sages": ["陆一帆", "陆诗杰"],
    },
    "安全合规/留痕": {
        "triggers": ["合规", "留痕", "审计", "审批", "回退", "基座", "安全", "权限"],
        "sages": ["陈方移", "张鑫"],
    },
    "控制/兜底/风险": {
        "triggers": ["控制", "兜底", "风险", "监控", "异常", "回退", "失效", "接管"],
        "sages": ["张鑫", "邹蕴", "陈方移"],
    },
    "价值/客户/战略": {
        "triggers": ["价值", "客户", "战略", "roi", "资产", "市场", "分级", "评估"],
        "sages": ["范征", "陆诗杰"],
    },
    "AI/铸模/产品化": {
        "triggers": ["ai", "prompt", "铸模", "模板", "工作流", "自动化", "agent", "产品化"],
        "sages": ["徐奕阳", "陆一帆", "孙高德"],
    },
    "流水线/流程/编排": {
        "triggers": ["流水线", "流程", "编排", "状态图", "节点", "oa", "长链路"],
        "sages": ["徐骋", "陈彤", "陈方移"],
    },
    "跨界/集成/场景": {
        "triggers": ["跨界", "集成", "场景", "迁移", "模块复用", "组合"],
        "sages": ["蔡悦", "骆希聪"],
    },
    "可靠性/冗余/工程": {
        "triggers": ["冗余", "可靠", "失效", "备份", "组合工程", "单点"],
        "sages": ["黄嵩泉", "陈方移"],
    },
    "度量/指标/评价": {
        "triggers": ["指标", "度量", "量化", "评分", "权重", "可视化", "评价"],
        "sages": ["陆诗杰", "陆一帆"],
    },
    "现场/客户/落地": {
        "triggers": ["现场", "客户", "落地", "痛点", "实用", "模块化"],
        "sages": ["顾峻峰", "范征"],
    },
    "涉外专利/跨法域": {
        "triggers": ["涉外", "pct", "跨法域", "多国", "国际申请", "马德里", "海外布局"],
        "sages": ["周全", "徐伟"],
    },
    "商标/品牌": {
        "triggers": ["商标", "品牌", "抢注", "品牌保护", "驰名商标", "使用证据"],
        "sages": ["吴畏", "范征"],
    },
    "诉讼/政策/维权": {
        "triggers": ["诉讼", "侵权诉讼", "政策", "维权", "行政诉讼", "海外维权"],
        "sages": ["钱孟清", "周全", "卢若雨"],
    },
    "专利导航/信息分析": {
        "triggers": ["导航", "专利地图", "信息分析", "专利布局分析", "技术全景", "竞争对手分析"],
        "sages": ["叶诚", "陆一帆"],
    },
    "制度建设/规则": {
        "triggers": ["制度建设", "规则", "标准", "审查制度", "机构建制", "国际规则"],
        "sages": ["须一平", "王升"],
    },
    "工艺落地/公差/样机": {
        "triggers": ["工艺", "公差", "样机", "装配", "dfmea", "可制造性", "可维护性"],
        "sages": ["朱立鸣", "喻学兵"],
    },
}


def check_capabilities(topic: str, roster: list) -> list:
    """检查议题需要的能力，哪些在当前名单里缺失。返回建议邀请列表。"""
    t = (topic or "").lower()
    roster_set = set(roster)
    suggestions = []
    for cap, rule in CAPABILITIES.items():
        triggers = rule["triggers"]
        # 议题命中该能力的触发词
        if not any(tr in t for tr in triggers):
            continue
        # 检查当前名单是否已有具备该能力的圣人
        has_cap = any(s in roster_set for s in rule["sages"])
        if has_cap:
            continue  # 已有人具备,不需补
        # 建议邀请:取优先级最高的未入会圣人
        for sage in rule["sages"]:
            if sage not in roster_set and sage in r.SAGES:
                suggestions.append({
                    "capability": cap,
                    "suggested_sage": sage,
                    "title": r.SAGES[sage]["title"],
                    "reason": f"议题涉及「{cap}」，当前名单缺少该能力",
                    "triggered_by": [tr for tr in triggers if tr in t][:3],
                })
                break
    return suggestions


def main():
    ap = argparse.ArgumentParser(description="智能动态补人——检查缺关键能力并建议邀请")
    ap.add_argument("--topic", required=True)
    ap.add_argument("--roster", default="", help="当前入会名单,逗号分隔")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    roster = [n.strip() for n in args.roster.split(",") if n.strip()]
    suggestions = check_capabilities(args.topic, roster)
    if args.json:
        print(json.dumps(suggestions, ensure_ascii=False, indent=2))
        return
    if not suggestions:
        print("[邹蕴] 当前名单能力覆盖完整，无需补人。")
        return
    print("[邹蕴] 智能补人建议：")
    for s in suggestions:
        print(f"  - 邀请 [{s['suggested_sage']}] {s['title']}：{s['reason']}（触发词：{'、'.join(s['triggered_by'])}）")
    print("[邹蕴] 将自动邀请上述圣人入会。")


if __name__ == "__main__":
    main()
