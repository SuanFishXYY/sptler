# 运行时细则

> 本文件集中 sptler 的运行时操作细节。SKILL.md 只保留流程骨架，具体规则在此。

## 记忆系统运行时

记忆遵循 `references/memory_philosophy.md`。运行时调用：

- **Phase 1 注入**：`python scripts/summon_sage.py --sage <name> --topic "<topic>"` 一次加载灵魂+记忆+关系+相关历史记忆。命中记忆自动 citation+1 回写。
- **Phase 5b 记录**：`python scripts/record_memory.py --batch -`（stdin）或 `--batch <file>`。batch 可带 `supersedes: [旧meeting_id]` 标记推翻旧结论。
- **Phase 5b 成长**：`python scripts/update_growth.py` 更新 GROWTH.md（双画像+高价值+转折点）。
- **Phase 5e 索引+关系**：`python scripts/index_meeting.py --batch -` 登记 index.json；`python scripts/build_relations.py` 更新 RELATIONS.json。

记忆字段（value_score/citation_count/superseded/supersedes/is_turning_point）语义见 memory_philosophy.md。

## 用户指定邀请圣人

两种时机：
1. **会前(Phase 0.5)**：模式选择后 AskUser 问是否指定邀请；选"我要指定邀请"则再发一次自由文本 AskUser 收姓名。
2. **会中插队(任意阶段)**：用户说"邀请陆一帆加入""让黄嵩泉评估可靠性"。邹蕴立即拉入，读其记忆注入，补发言/补投票，影响计票则重算。

邀请规则：被点名圣人必到（真实权重，不计关键词匹配）；计入规模上限，用户坚持可超1-2人；邹蕴须口头确认每次邀请（`[邹蕴] 现邀请XX入会——`），不得静默忽略。

## 续议制度

议会收口后用户说"展开""重议""行动项3深入""徐奕阳再讲讲""让陆一帆评估数据层"→ 视为续议，不重开全会：

1. 不重走 Phase 0/0.5。
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
- Phase 0.5 邀请 + 会中插队处理
- Phase 2 强制延迟评判（发现评判立即制止）
- Phase 4a 四律检查
- Phase 4b 接近/平票裁决（差距≤1.0 或 tie）
- Phase 5a 收口综合
- 不投票（权重0，立场记"弃权(主持)"不计票）

## 四律否决闸（投票前置硬约束）

投票前邹蕴组织对照 `references/philosophy.md` 四律检查方案。触发某律否决信号→对应核心必须投反对并引用信号。快速轨只查命中律，正式轨四律全查。这是事前约束，非事后解释。

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
