#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
算鱼议会 · 议题预热 (sptler_prelude.py)

用户随手提问后先跑这个：判断"这值得开议会吗 / 该走哪个轨道"。
不值得（事实性/单点信息/闲聊）→ 直接答，别开议会。
值得 → 输出建议轨道 + 预期规模 + 预计耗时，让用户决定。

用法:
  python scripts/sptler_prelude.py --topic "这个权利要求边界怎么收"
  python scripts/sptler_prelude.py --topic "今天天气" --json
"""
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
import route_sages as r


# 不值得开议会的信号：事实性/单点信息/定义性/闲聊
SKIP_KEYWORDS = [
    "什么是", "解释一下", "定义", "意思是", "英文", "翻译", "怎么读",
    "今天", "天气", "几点", "你好", "谢谢", "帮我写一句", "格式是什么",
]
SKIP_PATTERNS = ["吗？", "吗?", "是不是", "对不对"]  # 纯是非题也不必开议会


def should_skip(topic: str) -> tuple[bool, str]:
    t = (topic or "").strip()
    if not t or len(t) < 4:
        return True, "问题太短，直接答即可"
    for kw in SKIP_KEYWORDS:
        if kw in t:
            return True, f"命中事实/定义类信号「{kw}」，直接答即可"
    # 纯是非题
    if any(p in t for p in SKIP_PATTERNS) and len(t) < 15:
        return True, "纯是非题，直接答即可"
    return False, ""


def prelude(topic: str) -> dict:
    skip, skip_reason = should_skip(topic)
    if skip:
        return {
            "topic": topic,
            "open_parliament": False,
            "reason": skip_reason,
            "suggestion": "直接回答，无需开议会。",
        }
    # 值得开：判定轨道
    result = r.route(topic, mode="dynamic", track="auto")
    scenario = result.get("scenario", "")
    track = result.get("track", "")
    size = result.get("target_size", 0)
    # 预计耗时（粗估）
    if track == "verdict":
        est = "秒级（1圣人3句话）"
    elif track == "fast":
        est = "1轮（3-5人快速议会）"
    else:
        est = "完整六阶段（7-9人正式议会）"
    return {
        "topic": topic,
        "open_parliament": True,
        "scenario": scenario,
        "track": track,
        "track_reason": result.get("track_reason", ""),
        "target_size": size,
        "estimated_time": est,
        "deliver_dir": result.get("deliver_dir", ""),
        "suggestion": (f"建议开议会：{scenario + '场景，' if scenario else ''}{track}轨，{size}人，{est}。"
                       + (f"交付物将写 {result.get('deliver_dir','')}。" if result.get("deliver_dir") else "")),
    }


def main():
    ap = argparse.ArgumentParser(description="议题预热——判断是否值得开议会")
    ap.add_argument("--topic", required=True)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    p = prelude(args.topic)
    if args.json:
        print(json.dumps(p, ensure_ascii=False, indent=2))
        return
    if not p["open_parliament"]:
        print(f"[邹蕴] {p['suggestion']}（{p['reason']}）")
    else:
        print(f"[邹蕴] {p['suggestion']}")
        print(f"  轨道：{p['track']}｜规模：{p['target_size']}人｜预计：{p['estimated_time']}")
        if p.get("scenario"):
            print(f"  场景：{p['scenario']}")


if __name__ == "__main__":
    main()
