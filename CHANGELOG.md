# Changelog

## v1.4.0 (2026-07-02)

### 5 大哲学维度
- **传承哲学**：圣人谱系机制（lineage.py），师承链 + 传承包
- **立场漂移监督**：命题演化重叠 <15% → ⚠️ 漂移警告（守恒量）
- **功绩权重**：权重随贡献演化（merit_weight.py），非世袭
- **议会自省**：议后邹蕴评议会本身（规模/匹配/流程/漂移）
- **置信度圣人**：发言带高/中/低/不确定（认知谦逊）

### 灵魂机制深化
- 28 圣人 6 件套灵魂：命题 + 内在冲突 + 边界 + 自警(失败模式) + 追问 + 典型句式
- 议会张力机制：核心圣人预设张力对（tensions.json + tensions.py）
- 命题演化：转折点 refine 命题（动态灵魂）
- 张力演化：共议历史磨合张力（议会动态灵魂）
- 28 圣人 conflict/quotes/fail 全个性化

### 隐患审计 9 类
- 单点崩溃（compact/index/stdin）
- 长期增长（compact 自动触发 + index 截断 200）
- 架构漂移（SOUL 恢复 + generate_saints 保护富 SOUL）
- 设计假设（lite 功绩减半 + 口语化战略词兜底）
- 边界交互（8 项全扫）
- 元审计（3 哲学脚本 + compact 触发加行为门）
- 用户误用（战略问题 quality_concern 触发）
- 缝隙隐患（lite compact value 区分 + validator 门同步）

### Jobs 减法
- SKILL.md lite 段 634→150 词（沉降到 sptler-lite 子 skill）
- body 2710→2184 词（54%→44%）
- 4 脚本死码审计确认（sptler_run/sptler_prelude/memory_io/action_board）

### Review 标注
- 5 项未来机制标注 [实验性]
- README 加功能状态总览表（即时/实验性/防御性）

### 真跑验证
- lite 端到端（AOA 权要）→ 暴露追问转化缺口 → 修复
- briefing 端到端（FTO 快评）→ 暴露场景流程缺口 → 修复
- 标准端到端（价值评估）→ 无新缺口

---

## v1.3.0 (2026-07-02)

### lite/briefing 模式机制强制
- `/sptler#` lite：5 脚本 --lite + 9 行为门（cap≤3/场景拒绝/质量护栏/邀请保护/记忆降权/画像不翻转/闭环/留痕不删/命题门）
- `/sptler!` briefing：route_sages --briefing，cap≤5，场景走快评不拒绝
- lite vs briefing 决策矩阵 + 命名澄清

### 全脚本崩溃守卫
- 10 脚本 isinstance(dict) 守卫（compact/watch/update_growth/list_memories/continue/index/build_relations/briefing/action_board/memory_io）

### 三入口独立 skill
- /sptler-lite（/sptler# 词化版）
- /sptler-brief（/sptler! 词化版）
- 跨平台路径（${CLAUDE_SKILL_DIR}/../sptler + 候选列表）

### 文档
- README 模式总览（入口 4 / 四轨 / 6 场景）
- README 架构章节（单脑多角色，非 multi-agent）
- SKILL.md lite cheat-sheet + 模板九 + example 08
- 跨平台安装说明（git pull 一条命令升级）

---

## v1.2.0 (2026-07-01)

### 原始发布
- 28 位带灵魂与记忆的圣人专家班子
- 四轨制自动降级（verdict/fast/formal/followup）
- 记忆魔法时刻（同类问题第二次引用上次结论）
- 6 专利专属场景（查新/FTO/价值/OA/布局/无效）
- 加权投票 + 四律否决闸
- 记忆哲学宪法（分层/价值驱动/superseded/双画像）
- 22 脚本模块化（routing/memory/output/saints/validate 5 目录）
- 自检脚本（validate_sptler + validate_saints）
