---
name: sptler-lite
description: 算鱼议会·精简模式（省token快车道）。单域快判断、token敏感时用——不读references、薄灵魂、无记忆注入、verdict优先(1圣人,≤3人)、零AskUser单轮收口、最简结果md。是 /sptler 的省token变体，复用其28圣人+脚本。触发：/sptler-lite、/sptler#、/议会#、/议一议#。不适合：不可逆战略决策、专利场景(查新/FTO/OA/布局/无效需专属流程，lite硬拒绝)、需记忆连续性。
license: MIT
metadata:
  version: 1.3.0
  author: 算鱼工作室
  language: zh-CN
  variant_of: sptler
  mode: lite
---

# 算鱼议会 · 精简模式 /sptler-lite

> `/sptler-lite {问题}` = `/sptler# {问题}` 的独立入口——省 token 快车道。

本 skill 是 `/sptler` 的精简变体，**复用 sptler 的 28 圣人 + 22 脚本 + references**，只换运行时行为（省 token）。所有脚本在 sptler 目录内运行，`--lite` flag 强制精简行为。

**定位 sptler 目录**（跨平台，不硬编码路径）：优先 `${CLAUDE_SKILL_DIR}/../sptler`（Claude Code 标准）；若该变量未替换或不存在，按序检查 `~/.claude/skills/sptler`、`~/.codex/skills/sptler`、`.github/skills/sptler`、`.claude/skills/sptler`，取第一个含 `scripts/` 的。下文 `<SPTLER_DIR>` 代指定位到的目录。

## 触发

- `/sptler-lite {问题}` / `/sptler# {问题}` / `/议会# {问题}` / `/议一议# {问题}`

## 精简行为（强制）

- **不读 references**：orglaw/philosophy/runtime/templates/memory_philosophy 都不开，下面 cheat-sheet 即内核
- **verdict 优先、硬上限 ≤3**：`cd <SPTLER_DIR> && python scripts/routing/route_sages.py --topic "<问题>" --lite`
  - `--lite` 强制：verdict优先、规模封顶3、formal降级fast、专利场景硬拒绝(`lite_rejected=true`+0人，提示用标准 /sptler)
  - `lite_quality_concern=true` → 邹蕴提示"本题formal级，lite 3人降级可能不充分，建议标准 /sptler"
- **薄灵魂**：`python scripts/memory/summon_sage.py --sage <名> --lite`（一行：圣号/官职/角色+边界）
- **无记忆注入**：lite 跳记忆/关系/历史（无魔法时刻——这是 /sptler-lite 的明确代价）
- **单轮、零 AskUser**：3 句裁决(结论/理由/风险) + 最简结果 md，然后 `议会到此结束。`
- **轻量记忆**：`python scripts/memory/record_memory.py --batch - --lite`（标 lite=true，不翻转风险画像）

## 内核 cheat-sheet（不读 references，认这张表）

```
四律否决闸（投票前置；触发否决信号→对应核心必反）：
  结构律·王升(3.0)：先骨架后血肉；否决「先做起来边做边想/单指标独断/缺中间层硬接」
  控制律·张鑫(3.0)：流动有界、自动化有兜底；否决「全交AI无人管/无监控回退/权限全开」
  铸模律·徐奕阳(3.0)：经验铸成可复用模板；否决「只能靠经验没法模板/通用模型直套/输出无理由」
  价值律·范征(3.0)：价值落点在哪；否决「价值后看/凑数量/酷但不知给谁用」
权重：核心3.0 / 首席2.0(孙高德·蔡悦·黄嵩泉) / 专科1.0 / 议长邹蕴0不投票 / +0.5动态加成(至多2人)
计票：赞成权重和 vs 反对权重和(弃权不计)；通过=赞成>反对；差距≤1.0或平票→邹蕴裁决；重大事项≥60%且无核心反对
格式：所有发言 [姓名] 内容；建议 [姓名] 建议：xxx；收口 邹蕴；终止语 议会到此结束。
轨道：verdict(1人3句,零留痕) > fast(3-5人) > formal(7-9人) > followup；lite 默认 verdict，最多3人
交付物：议会是手段、交付物是目的；结果md强制写 sptler-meetings/
```

## 结果 md（模板九 · 4 节 · ≤15 行）

```
# 算鱼议会决议 · {议题}（lite）
> 编号 SPTLER-{ts} ｜ 模式 lite ｜ 议长 邹蕴 ｜ 主笔 {圣人}（权重{w}）
## 一、议题
{问题 + 1句议长提炼}
## 二、裁决
[{主笔}] {结论}——{1句理由}。{1句风险}。
## 三、交付物指针
{路径 或 无}
## 四、收口
[邹蕴] {1句总结}。议会到此结束。
```

## 什么时候不要用 lite

不可逆/战略决策、专利场景(查新/FTO/OA/布局/无效)、需记忆连续性(第二次问想引用上次) → 用标准 `/sptler` 或 `/sptler!` 简报。

## 复用说明

本 skill 不自带脚本/saints/references，全部复用 sptler 目录（见上方"定位 sptler 目录"）。sptler 更新（`cd <SPTLER_DIR> && git pull`）后，sptler-lite 自动获得最新脚本与圣人。
