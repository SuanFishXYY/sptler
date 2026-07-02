---
name: sptler-brief
description: 算鱼议会·简报模式（免提问中等议题议会）。中等多域议题、要专家深度但不想被AskUser打断时用——读references、完整灵魂+记忆注入(保留魔法时刻)、强制fast轨、规模≤5、场景走快评不拒绝、零AskUser单轮收口。是 /sptler 的简报变体，复用其28圣人+脚本。触发：/sptler-brief、/sptler!、/议会!。不适合：不可逆战略决策(formal级)、单域快判断(用/sptler-lite)、需正式投票审计。
license: MIT
metadata:
  version: 1.3.0
  author: 算鱼工作室
  language: zh-CN
  variant_of: sptler
  mode: briefing
---

# 算鱼议会 · 简报模式 /sptler-brief

> `/sptler-brief {问题}` = `/sptler! {问题}` 的词化入口——免提问的中等议题议会。

本 skill 是 `/sptler` 的简报变体，**复用 sptler 的 28 圣人 + 22 脚本 + references**，只换运行时行为（跳 AskUser、强制 fast、≤5 人）。所有脚本在 sptler 目录内运行，`--briefing` flag 强制简报行为。

**定位 sptler 目录**（跨平台，不硬编码路径）：优先 `${CLAUDE_SKILL_DIR}/../sptler`（Claude Code 标准）；若该变量未替换或不存在，按序检查 `~/.claude/skills/sptler`、`~/.codex/skills/sptler`、`.github/skills/sptler`、`.claude/skills/sptler`，取第一个含 `scripts/` 的。下文 `<SPTLER_DIR>` 代指定位到的目录。

## 触发

- `/sptler-brief {问题}` / `/sptler! {问题}` / `/议会! {问题}`

## 简报行为（强制）

- **读 references**（与 lite 不同，briefing 保留深度）：philosophy/orglaw/runtime/roster/templates 正常读，在 `<SPTLER_DIR>/references/`
- **强制 fast、≤5**：`cd <SPTLER_DIR> && python scripts/routing/route_sages.py --topic "<问题>" --briefing`
  - `--briefing` 强制：fast 轨、规模封顶5、formal 降级 fast、返回 `briefing:true`
  - **场景不拒绝**（区别于 lite）：专利场景走**场景快评轨**（fast + 必到圣人 + 场景交付物，规模≤5），保留深度只跳 AskUser
- **完整灵魂 + 记忆注入**（保留魔法时刻）：`python scripts/memory/summon_sage.py --sage <名> --topic "<问题>"`（非 --lite，读 SOUL/记忆/关系）
- **零 AskUser**：跳 Phase 0 模式选择、Phase 1 名单确认、Phase 5b 导出选项；单轮交付
- **简洁输出**：每人 1 设想、1 组合方案、1 投票行、1 建议
- **全量记忆写入**：`python scripts/memory/record_memory.py --batch -`（画像随会议演化，正常）

## 与 /sptler-lite 的分水岭

| 维度 | /sptler-brief | /sptler-lite |
|---|---|---|
| 目的 | 中等议题要深度，免提问 | 单域快判断，省 token |
| references | ✅ 读 | ❌ 不读 |
| 灵魂 | ✅ 完整 | ❌ 薄灵魂一行 |
| 记忆注入 | ✅ 有（魔法时刻） | ❌ 无 |
| 规模 | ≤5 | ≤3 |
| 场景 | ✅ 走快评 | ❌ 硬拒绝 |

**一句话**：要"专家深议但不打断"用 `/sptler-brief`；要"快、省、单判断"用 `/sptler-lite`。第二次问想引用上次 → 用 `/sptler-brief` 或标准 `/sptler`（`/sptler-lite` 不读记忆）。

## 什么时候不要用 brief

- 不可逆/战略/formal 级决策 → 用标准 `/sptler` 开 7-9 人全会
- 单域快判断、token 敏感 → 用 `/sptler-lite`
- 需完整 Phase 0 模式选择 + 名单确认 → 用标准 `/sptler`

## 复用说明

本 skill 不自带脚本/saints/references，全部复用 sptler 目录（见上方"定位 sptler 目录"）。sptler 更新（`cd <SPTLER_DIR> && git pull`）后，sptler-brief 自动获得最新脚本与圣人。
