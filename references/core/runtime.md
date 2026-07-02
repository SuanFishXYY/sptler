# 运行时细则

> 本文件集中 sptler 的运行时操作细节。SKILL.md 只保留流程骨架，具体规则在此。

## 记忆系统运行时

记忆遵循 `references/memory/memory_philosophy.md`。运行时调用：

- **Phase 1 注入**：`python scripts/summon_sage.py --sage <name> --topic "<topic>"` 一次加载灵魂+记忆+关系+相关历史记忆。命中记忆自动 citation+1 回写。
- **Phase 5b 记录（用户确认后）**：先 AskUser 问是否写入记忆（写入记忆/不留痕）。选"写入记忆"才运行 `python scripts/record_memory.py --batch -`（stdin）或 `--batch <file>`。batch 可带 `supersedes: [旧meeting_id]` 标记推翻旧结论。选"不留痕"则跳过，仅保留结果 md。
- **Phase 5b 成长**：`python scripts/update_growth.py` 更新 GROWTH.md（双画像+高价值+转折点）。
- **Phase 5e 索引+关系**：`python scripts/index_meeting.py --batch -` 登记 index.json；`python scripts/build_relations.py` 更新 RELATIONS.json。

记忆字段（value_score/citation_count/superseded/supersedes/is_turning_point）语义见 memory_philosophy.md。

## 用户指定邀请圣人

两种时机：
1. **会前（并入名单确认，非独立AskUser）**：Phase 1 路由后，邹蕴呈现名单时一并询问"确认开议，或指定邀请某几位圣人？"——用户在同一轮回答即可（确认 / 报姓名邀请）。不再单独发"是否邀请"AskUser。
2. **会中插队(任意阶段)**：用户说"邀请陆一帆加入""让黄嵩泉评估可靠性"。邹蕴立即拉入，读其记忆注入(dry-run)，补发言/补投票，影响计票则重算。

邀请规则：被点名圣人必到（真实权重，不计关键词匹配）；计入规模上限，用户坚持可超1-2人；邹蕴须口头确认每次邀请（`[邹蕴] 现邀请XX入会——`），不得静默忽略。

## 续议制度

议会收口后用户说"展开""重议""行动项3深入""徐奕阳再讲讲""让陆一帆评估数据层"→ 视为续议，不重开全会：

1. 不重走 Phase 0/1（模式选择 + 路由/名单确认）。
2. 先 `python scripts/continue_meeting.py --last`（或 `--meeting-id`）读上下文，加 `--item N`/`--sage`/`--target`。
3. 判续议类型：解释型/行动项型/风险复核型/修正型/重投票型。
4. 最小召集（1-3人），读记忆，≤8条 `[姓名]` 输出。
5. 改变原决议→小范围加权投票+导出 amendment/revote；否则只续议。
6. 记 followup 记忆（meeting_type=followup, parent_meeting_id），登记索引。
7. `续议到此结束。` 收口。

续议边界：单次≤8条；连续续议超2次邹蕴提示升级为正式议题；对象不明只问一个澄清。

## 议长(邹蕴)行为

邹蕴以"实时决策/失效安全"专长主持：预判下一帧风险、控节奏、防失控。
- Phase 0 模式选择 + 动态判定理由
- 名单确认 + 邀请（合并） + 会中插队处理
- Phase 2 强制延迟评判（发现评判立即制止）
- Phase 4a 四律检查
- Phase 4b 接近/平票裁决（差距≤1.0 或 tie）
- Phase 5a 收口综合
- 不投票（权重0，立场记"弃权(主持)"不计票）

## 四律否决闸（投票前置硬约束）

投票前邹蕴组织对照 `references/core/philosophy.md` 四律检查方案。触发某律否决信号→对应核心必须投反对并引用信号。快速轨只查命中律，正式轨四律全查。这是事前约束，非事后解释。

## 加权投票规则

- 权重：核心3.0 / 首席2.0 / 专科1.0 / +0.5动态加成（至多2人，仅加分不降权，只给关键词命中者）
- 计票：赞成权重和 vs 反对权重和（弃权不计）
- 通过：赞成 > 反对
- 接近/平票（差距≤1.0或tie）：邹蕴裁决
- 重大事项：赞成/(赞成+反对) ≥ 60% 且无核心反对，否则否决

## 输出文件命名

`{cwd}/sptler-meetings/` 下：
- 结果 md（强制）：`sptler-result-{slug}-{ts}.md`
- 交付物：`deliverable-{claim|adr|sop}-{slug}-{ts}.md`
- 会议纪要/过程（可选）：`sptler-{summary|transcript}-{slug}-{ts}.md`
- 续议：`sptler-{followup|amendment|revote}-{slug}-{ts}.md`
- 记忆 batch json：`sptler-memory-{slug}-{ts}.json`
- 会议索引：`index.json`（累计）

主题 slug：议题前8汉字或关键英文词，去标点。UTF-8 编码。写盘后告知用户绝对路径。

## Phase 详细步骤（从 SKILL.md 沉降）

### Verdict 模式（单圣人裁决）
1. No Phase 0 AskUser, no roster-confirm/invite (unless user named a sage).
2. Summon 1 matched sage (`summon_sage.py --sage <name> --topic "<topic>" --dry-run`). **--dry-run mandatory**: verdict does NOT write memory/citation — zero-trace.
3. Sage gives 3-sentence judgment (call/why/risk). `[姓名]` prefix, cite memory if relevant.
4. No brainstorm/four-law/vote. 邹蕴 closes in 1 line (this IS the conclusion — verdict exempt from Discipline #14).
5. Produce deliverable (Template 7) if applicable + minimal result md + index. **No record_memory/citation/growth.**
6. End `议会到此结束。`

### Briefing 模式（/sptler!）
1. Run `route_sages.py --topic "<q>" --briefing` — 脚本强制 fast 轨、cap ≤5、formal 降级 fast、返回 `briefing:true`。
2. No AskUser at all.
3. 邹蕴 auto-selects ≤5 attendees (script-capped), ≥1 core.
4. **场景不拒绝**（区别于 lite）：专利场景走**场景快评轨**（fast + 必到圣人保留 + 场景交付物，规模缩到 ≤5），保留深度只跳 AskUser。
5. Concise: each 1 idea, 1 combined plan, 1 vote line, 1 recommendation.
6. Record memories + mandatory result md only.
7. End `议会到此结束。`

### Phase 0 — Mode selection
Run `route_sages.py --track auto`. If scenario identified → skip AskUser, 邹蕴 declares track+size. If no scenario → AskUser: 快速/复杂/动态.

### Phase 1 — Routing + injection + roster confirm (10 steps)
1. Seed with user invites.
2. `route_sages.py --topic --mode --track auto --invites --json`.
3. Fallback: manual routing from roster.md.
4. Host = 邹蕴 (weight 0).
5. `summon_sage.py --sage <name> --topic --dry-run` per attendee (mandatory dry-run).
6. Classify major/ordinary.
7. Present roster + invite + confirm (auto-proceed for first-time/no-memory: `[邹蕴] 召集{N}人，主笔{X}。3秒后开议，如需调整说停。`; experienced: present roster + invite prompt, wait for confirmation). Runs HERE, after routing produces the roster — never before.
8. `watch_memory.py --topic --roster` → active memory reminder.
9. Scenario data collection (查新/FTO/无效: AskUser for prior art/patent list/evidence).
10. `auto_invite.py --topic --roster` → smart capability-gap fill.

### Phase 2 — Brainstorming
- Zero negation (Priority: 零评判 > 人格表达; hates → positive alternative only).
- `[姓名]` prefix. Quick: 1-2 points. Complex: 3 ideas.
- Memory citation mandatory for score≥4; anti-hallucination (real dates only); vary phrasing by persona; no-match sages speak naturally without announcing "新晋".
- Brevity: 1 idea = 1 sentence. Quick ≤2 sentences/sage. Complex ≤4.
- Formal-track compression: conversation = executive summary (1 idea/sage); full brainstorm → files.

### Phase 3 — Combine
Quick → 1 plan. Complex → 2-3 plans. No negation, only convergence.

### Phase 4 — Four-law + vote
4a. Four-law check (`philosophy.md`). Triggered veto signal → core must oppose. Quick: hit laws only. Complex: all four.
4b. Weighted vote `[姓名](权重) 立场——理由`. Rules: see §加权投票规则 above.

### Phase 5 — Output
5a. Final recommendations: each sage `[姓名] 建议：xxx`. (邹蕴 does NOT synthesize here.)
5b. Memory (default write) + export merged AskUser: "默认写入记忆+结果md。需加纪要/过程？或说不留痕。" If write → `commit_citations.py` + `record_memory.py --batch -` + `update_growth.py`. If 不留痕 → skip all.
   **lite (/sptler#) 5b**：无 AskUser，默认写轻量记忆——`record_memory.py --batch - --lite`（experience 标 `lite=true`，跳过 profile_recent 重算 + 风险画像重算，一次 lite 快调不翻转圣人底色）；跳过 `commit_citations.py` + `update_growth.py`。事件留痕、画像不动。
5d. Write result md (Template 1, patent scenario = 瘦版).
5d-bis. Write deliverable (Template 7/8). Default `sptler-meetings/`; user says "直投" → `deliver_dir`. Register in index.
5e. `index_meeting.py` + `build_relations.py`.
   **lite (/sptler#) 5e**：`index_meeting.py --lite` 登记 `lite:true`（与 record_memory 的 lite=true、route_sages 的 lite 字段对齐，闭环）。续议时 `continue_meeting.py` 据此走精简续议（≤3人、不重跑四律、零 AskUser）。
5f. 邹蕴 substantive conclusion (decision + reason + risk). File paths. Action items. `议会到此结束。` STOP.
5g. **议会自省**（#4 哲学，强制）：收口前邹蕴用 1 句评议会本身——规模是否合适（过大/过小）/圣人是否匹配（有无缺席关键视角）/流程是否过重（verdict 级问题走了 fast 是否浪费）。写入结果 md 末尾「议会自省」栏。这是议会的元认知——防议会变机械流程，每次反思自身有效性。lite 模式也须自省（但 1 句，不展开）。
