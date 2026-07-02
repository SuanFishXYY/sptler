# 🏛️ 算鱼真人议会 · sptler

> **先立骨，再铸模；以界为器，以值为尺。**

![License](https://img.shields.io/badge/license-MIT-blue)
![Skill](https://img.shields.io/badge/Claude%20Code-Skill-orange)
![Sages](https://img.shields.io/badge/圣人-28位-green)
![Tracks](https://img.shields.io/badge/轨道-4轨自动降级-purple)

**28 位带灵魂与记忆的圣人专家班子，按问题重量自动开议会。**

不是又一个 prompt 模板——这是一套会**记住你所有决定**的专家系统：日常小问题让最相关的 1 位圣人 3 句话裁决，复杂议题才召集多位圣人做加权投票；而当你第二次问同类问题，圣人开口第一句就引用上次的结论。

## 30 秒看懂

| 你问的 | sptler 怎么做 | 为什么比裸 Claude 强 |
|---|---|---|
| "权利要求边界怎么收" | 1 位圣人 3 句话裁决 | 秒级出专家判断，带人格不用铺垫 |
| "OA流水线怎么落地" | 6 圣人快速议会+加权投票 | 多视角+四律否决，结构化收敛 |
| 第二次问同类问题 | 圣人引用上次结论接续 | **有积累，不重复论证** |

## 模式总览（选哪个？）

sptler 有三组模式：**入口模式**（怎么触发）、**轨道**（按问题重量自动降级）、**专利场景**（专属流程）。三者正交——任一入口 × 自动轨道 ×（可能命中）场景。

### A. 入口模式（4 个 · 怎么触发）

| 入口 | 触发 | 规模 | 适合 | 关键特性 |
|---|---|---|---|---|
| **标准** | `/sptler {问题}` | route 自动（1-9） | 所有正经议题 | 完整流程，1-2 个 AskUser 确认模式/名单/导出 |
| **简报** | `/sptler-brief {问题}` 或 `/sptler! {问题}` | ≤5（脚本硬上限） | 中等议题、要深度但不想被 AskUser 打断 | 独立 skill `sptler-brief`，`route_sages --briefing` 强制 fast、免提问、单轮、场景走快评不拒绝 |
| **精简** | `/sptler-lite {问题}` 或 `/sptler# {问题}` | ≤3（脚本硬上限） | 单域快判断、token 敏感 | 独立 skill `sptler-lite`，不读 references、薄灵魂、无记忆注入、verdict 优先、专利场景硬拒绝 |
| **记忆查询** | `/sptler 记忆 {圣人名}` | — | 看某圣人记忆档案 | 不开议会，直接读 `memories/<名>.json` |

> **简报 `!` vs 精简 `#`**：都轻量单轮，但目的不同——`!` 要深度（读 references+完整灵魂+记忆注入，保留魔法时刻），`#` 要快省（不读+薄灵魂+无注入，无魔法时刻）。分水岭：第二次问想引用上次 → 用标准或 `!`；`#` 不读记忆。

### B. 四轨制（route_sages --track auto 自动降级，最轻优先）

| 轨道 | 触发 | 规模 | 仪式 | 留痕 |
|---|---|---|---|---|
| **单圣人裁决 verdict** | 单一明确单域问题 | 1 人 | 3 句话，不投票不四律 | 零留痕（不入记忆） |
| **快速轨 fast** | 中等多域 | 3-5 人 | 短头脑风暴+加权投票 | 全量记忆 |
| **正式轨 formal** | 战略/预算/不可逆/跨域 | 7-9 人 | 完整六阶段+四律检查 | 全量记忆+会议索引 |
| **续议轨 followup** | 会后追问/展开 | 1-3 人 | ≤8 条，最小召集 | 续议记忆（parent_meeting_id） |

### C. 六大专利场景（route 自动识别，走专属 Phase 流程）

| 场景 | 触发词 | 专属交付物 |
|---|---|---|
| **查新检索** | 查新/新颖性/现有技术 | 查新检索报告（三要素+语义矩阵+检索式） |
| **FTO 自由实施** | FTO/自由实施/侵权风险 | FTO 分析报告（侵权比对+规避设计+合规留痕） |
| **价值评估** | 价值评估/分级/运营 | 价值评估报告（五维打分+SABC分级） |
| **OA 答复** | 审查意见/OA/答复 | 答复策略（区别特征+修改方案+口径模板） |
| **布局选型** | 布局/选型/候选 | 布局建议（多维打分+加权排序） |
| **无效攻防** | 无效宣告/无效/攻防 | 无效分析（无效理由+证据组合+对方应对） |

> 场景需专属流程+feature_analysis，**精简模式 `#` 硬拒绝**（提示用标准）；**简报模式 `!` 走场景快评轨**（fast+必到圣人，规模缩到≤5，保留深度只跳 AskUser）。

### 命名澄清

- **简报模式**（`/sptler!`）= 免提问开议会（run-time 入口）
- **`briefing.py` 脚本** = 议会简报回顾（读 index.json 回顾上次会议结论/行动项）——两者同名但功能不同：前者是开会入口，后者是回顾工具。`briefing.py` 用 `--last N` 看最近 N 次概览。

## 架构：单脑多角色（不是 multi-agent）

sptler 是 **Skill（技能）**，不是 Agent（智能体）。**28 位圣人不是 subagent，是 prompt 角色扮演**——由主 Claude 单线程分饰多角，不 spawn 子 agent。

| 维度 | 普通 multi-agent skill | sptler 单脑多角色 |
|---|---|---|
| 圣人运行 | spawn N 个 subagent 并行 | `summon_sage.py` 注入灵魂块到主 Claude 上下文 |
| context | 每个 subagent 独立隔离 | 主 Claude 单一 context 串行扮演 |
| 通信 | subagent 间消息传递 | 主 Claude 自己接力 |
| 并行 | 真并行、真隔离 | 假多人、真单脑 |

**运行流程**：`/sptler {问题}` → `route_sages.py` 选圣人 → `summon_sage.py --sage 王升` 把王升的 SOUL+IDENTITY+BOUNDARY+记忆**注入主 Claude 上下文** → 主 Claude 以"王升"口吻发言 → 注入下一位 → 加权投票由主 Claude 计算 → 收口。

**为什么不用真 subagent？** 记忆魔法时刻（同类问题第二次问，圣人引用上次结论）**必须单脑**——subagent 间不共享 context，"我记得上次"做不出来。单脑多角色的代价是无真并行，但 sptler 的核心价值是**记忆统一+状态一致**，不是并行速度。这是设计取舍，不是缺陷。

## ✨ 十大亮点

### 🧠 1. 记忆魔法时刻——最大差异化
圣人记得自己历次议事的立场和建议。同类问题第二次问，开口第一句就引用上次结论：
> [徐奕阳] 上次我们议过 OA 流水线(06-15)，当时定的是"三段式Prompt模具+半自动起步"。这次我直接按那个骨架展开……

裸 Claude 每次从零开始，sptler 越用越懂你。记忆哲学宪法（价值驱动/分层/superseded/双画像）让圣人会记、会忘、会改主意。

### 🪶 2. 四轨自动降级——日常不背仪式税
```
单圣人裁决(1人,3句) → 快速轨(3-5人) → 正式轨(7-9人) → 续议轨
```
日常小问题 1 位圣人 3 句话裁决（秒级），复杂议题才开 8 人加权投票。小问题不走大流程——这是 sptler 比"每次都开全会"的系统好用的关键。

### 🔧 3. 六个专利专属场景——各有专属流程
不是统一六阶段套所有场景，每个专利场景有自己的 Phase 步骤：

| 场景 | 专属流程重点 |
|---|---|
| 查新检索 | 三要素拆解→语义矩阵6维度→检索式构建→完备性自检 |
| FTO 自由实施 | 风险专利解读→侵权比对(全要件+等同)→规避设计→合规留痕 |
| 价值评估 | 维度定权重(可调)→逐维打分→加权分级SABC→运营建议 |
| OA 答复 | 审查意见解读→区别特征提炼→修改方案→答复口径铸模 |
| 布局选型 | 候选方案→多维打分→加权排序→布局建议 |
| 无效攻防 | 目标专利解读→无效理由→证据组合→对方应对 |

### 📄 4. 产出真实交付物——议会是手段，交付物是目的
不是"关于会议的文档"，直接产出用户本来就要写的文件：
- 查新→查新检索报告（三要素+语义矩阵+检索式+逐特征比对表）
- FTO→FTO分析报告（侵权比对表+规避方案+合规留痕）
- 价值评估→价值评估报告（五维打分+SABC分级+运营建议）
- OA答复→答复策略（区别特征+修改方案+答复口径模板）

### 🤖 5. 智能动态补人——系统主动填能力缺口
议到检索式构建但名单没有擅长检索的人？系统自动邀请：
```
[邹蕴] 议题涉及检索语义，现邀请陆一帆入会。
```
不需要用户手动说"邀请陆一帆"——系统自己判断能力缺口并补人。

### 🛡️ 6. 诚实的能力边界——不硬塞模板
- 不检索专利库、不编造专利号（防执业事故）
- 不撰写专利全文、不代写诉讼文书
- 超出能力时邹蕴诚实说"这超出我的能力，我只能做X"
- 查新/FTO 需要用户提供风险专利清单，无清单则诚实说"只出框架"

### ⚡ 7. 第二次用只需1回合
- 场景命中→跳过模式选择
- 记忆默认写入不问
- 第二次同场景→Phase 0 跳过、记忆已记住
- 从4回合压到1-2回合

### 🏛️ 8. 28位有灵魂的圣人——不是NPC
每位圣人都有内在冲突、典型句式、与他人的张力。张鑫看到"全自动"会本能竖起防线（但Phase 2只说"我的本能是先加人工接管"，不否定别人），王升开口先建维度——有性格的专家在博弈，不是模板化NPC。

### 📊 9. 续议+行动项看板——会后不丢
- 续议：收口后说"展开行动项3"，不重开全会，最小召集接续
- 行动项看板：跨会议聚合未完成行动项，按责任人/优先级，可标记完成
- 会议简报：一键看上次会议结论+行动项

### 🔍 10. 深度自检——防潜伏bug
validate_sptler 不只查文件存在+语法，还运行时检查：
- RULES是否成功加载（防路径错误导致场景失效）
- 6场景是否都能正确识别
- verdict不误吞设计题
- 28圣人目录与注册表一致
- auto_invite能力表覆盖全部可路由圣人（每位圣人至少归属一个能力类别，智能补人无盲区）
- JSON 遍历/加载脚本含 isinstance(dict) 守卫（防杂散 JSON 致崩溃，覆盖记忆目录遍历 + 会议索引加载共 7 个脚本）
- lite 模式守卫：read_soul/summon_sage 支持 `--lite`，否则 /sptler# 会静默退化为完整模式

### ⚡ 11. lite 模式（/sptler#）——省 token 的快车道
当仪式税不值时：**不读 references**（内联 cheat-sheet 即内核）+ **薄灵魂**（`summon_sage --lite` 一行：圣号/官职/角色+边界，51词→1词）+ **无记忆注入** + **verdict 优先**（默认1圣人、最多3人）+ 零 AskUser 单轮收口。标准运行读 references 约 3400 词，lite 跳过这些、只内联 ~120 词 cheat-sheet，**单次省约 3300 词**。适合日常快速裁决；不适合不可逆战略决策与专利场景（查新/FTO/OA/布局/无效需专属流程，lite 跳过）。

## 触发

```bash
/sptler {问题}        # 标准议会：先选模式、邀请、名单确认
/sptler! {问题}       # 简报模式：免提问，自动动态路由，单轮给结论+结果md
/sptler# {问题}       # 精简省token模式：不读references、薄灵魂、无记忆注入、verdict优先、≤3人、零AskUser
/算鱼议会 {问题}
/议会 {问题}
/议会! {问题}        # 同 /sptler!
/议会# {问题}        # 同 /sptler#
/开会 {问题}
/议一议 {问题}
/sptler 记忆 王升     # 快捷查看某位圣人的记忆档案
```

**`!` 还是 `#`？** 都轻量单轮，但目的不同：
- `/sptler!` 简报——免提问的**中等议题议会**：读 references、完整灵魂+记忆注入（保留魔法时刻）、3–5人、要深度
- `/sptler#` 精简——省 token 的**快判断**：不读 references、薄灵魂、无记忆注入（无魔法时刻）、≤3人、要快省
- 分水岭：第二次问想引用上次结论 → 用标准或 `!`（`#` 不读记忆）
```

## 🚀 快速开始

```bash
git clone https://github.com/SuanFishXYY/sptler.git ~/.claude/skills/sptler
```

重启 Claude Code，然后：

```text
/sptler! 我们要把OA审查意见答复做成AI辅助流水线，怎么落地
```

或先看真实案例感受效果 👉 [examples/](examples/README.md)

**已安装用户更新**（保持 git clone 安装方式，一条命令升级）：

```bash
cd ~/.claude/skills/sptler && git pull
```

> ⚠️ 如果你是手动解压安装的（非 git clone），`git pull` 不可用——建议删掉旧目录重新 `git clone`，以后更新只需 `git pull`。运行时数据（`memories/*.json`、`sptler-meetings/`）已被 `.gitignore` 排除，重新 clone 不会丢你的议事记录。

**轻量入口独立 skill**（可选，词化更易记）：

```bash
# sptler-lite (精简, /sptler#) 和 sptler-brief (简报, /sptler!) 都是独立 skill
# 复用 sptler 的脚本/圣人/references，只装极薄 SKILL.md
cp -r ~/.claude/skills/sptler/sptler-lite ~/.claude/skills/sptler-lite
cp -r ~/.claude/skills/sptler/sptler-brief ~/.claude/skills/sptler-brief
```

装后即可 `/sptler-lite {问题}`（等价 `/sptler#`，省 token 快判断）和 `/sptler-brief {问题}`（等价 `/sptler!`，免提问中等议题）。sptler 更新后两者自动获得最新脚本，无需单独更新。三个入口：`/sptler`（标准）`/sptler-brief`（简报）`/sptler-lite`（精简）。

## 议会结构

- **议长 / 主持人（固定，权重 0 不投票）**：邹蕴（决策圣 · 郭嘉）——主持模式选择、议程、四律检查、僵局裁决、收口。
- **四核心（权重 3.0）**：王升（结构圣·结构律）、张鑫（控制圣·控制律）、徐奕阳（铸模圣·铸模律）、范征（价值圣·价值律）。
- **三大专业委员会首席（权重 2.0）**：孙高德（平台委员会）、蔡悦（跨界集成委员会）、黄嵩泉（组合工程委员会）。
- **专科圣人（权重 1.0）**：其余 20 位按议题路由入会。

## 四轨制（按问题重量自动降级）

sptler 自动按问题复杂度选择最轻的轨道，避免"小问题走大流程"：

| 轨道 | 触发 | 规模 | 仪式 |
|---|---|---|---|
| **单圣人裁决** | 单一明确单领域问题（"权利要求边界怎么收"） | 1人+邹蕴 | 3句话判断，不投票 |
| **快速轨** | 中等多域问题 | 3–5人 | 短头脑风暴+投票 |
| **正式轨** | 战略/预算/制度/跨域 | 7–9人 | 完整六阶段 |
| **续议轨** | 会后追问/修正 | 最小召集 | ≤8条 |

`route_sages.py --track auto` 自动判定。`/sptler!` 强制快速简报。

用户发送需求后用 AskUser 选择：

| 模式 | 规模 | 深度 |
|---|---|---|
| 快速会议 | 3–4 人 | 言简意赅，直接收敛 1 方案 |
| 复杂会议 | 7–9 人 | 全面召集，组合 2–3 方案，完整四律检查 |
| 动态分辨 | 3–9 人 | 议长自动判定规模与深度 |

## 六阶段流程

`Phase 0 模式选择` → `0.5 邀请询问（可选）` → `1 路由入会+记忆注入` → `2 头脑风暴（四原则·延迟评判）` → `3 组合改善` → `4 四律否决闸 + 加权投票` → `5 最终建议 + 记忆记录 + 输出`

### 简报模式 `/sptler!`

跳过所有 AskUser：自动动态分辨，召集 3–5 位圣人，单轮完成简版头脑风暴/组合/加权投票/最终建议，只导出强制结果 md，并以 `议会到此结束。` 收口。

### 续议/追问

收口后用户可说 `展开行动项3`、`徐奕阳再讲讲`、`让陆一帆评估数据层`，系统进入轻量续议：不重开全会，只召集最小相关席位，≤8条要点，必要时小范围重投票，最后 `续议到此结束。`

### 头脑风暴四原则
1. 自由思考 2. 延迟评判（阶段内零否定）3. 注重数量而非质量 4. 组合改善

### 加权投票（动态投票）
每位入会者按权重投票：赞成权重和 vs 反对权重和；差距 ≤ 1.0 或平票由议长裁决；重大事项要求赞成占比 ≥ 60% 且无核心反对。议题高度契合者可获 +0.5 动态加成。

### 发言格式
所有发言以 `[姓名] 内容` 前缀，例：`[徐奕阳] 这个场景得先拆成输入、输出、评估三段……`

### 最终建议
投票后每位入会圣人给一条 `[姓名] 建议：xxx`，议长邹蕴 `[邹蕴] 收口` 综合。

## 输出

- **交付物（按议题产出）**：议会是手段，交付物是目的。专利→权利要求骨架，架构→ADR，流程→SOP，直接产出用户本来就要写的文件。
- **结果 md（强制导出）**：决策记录，含议题/决议/四律检查/加权投票/行动项。
- **会议纪要 / 会议过程（可选）**：用 AskUser 让用户选是否导出。
- **记忆魔法时刻**：入会圣人若对同类议题有历史记忆，发言第一句强制引用——让用户感到"系统有积累"。

文件写入 `{当前工作目录}/sptler-meetings/`，UTF-8 编码。

## 示例

真实跑通的案例（脱敏），帮新用户理解"它能带来什么生产力"：

- [快速轨·OA流水线](examples/01-快速轨-OA流水线.md) — 中等议题走快速轨，产出 SOP 交付物 + 6 圣人积累记忆
- [魔法时刻·同类议题记忆引用](examples/02-魔法时刻-同类议题记忆引用.md) — 同类问题第二次问，圣人开口引用上次经历
- [单圣人裁决·日常生产力](examples/03-单圣人裁决-日常生产力.md) — 单一明确问题自动降级为 1 圣人 3 句话

详见 [examples/README.md](examples/README.md)。

## 文件结构

```
sptler/
├── SKILL.md                  技能主文件（1796词，流程骨架+指针）
├── saints/                   OpenClaw 圣人操作系统：28位圣人独立灵魂目录（以王升为例，28位均有相同结构）
│   └── 王升/                  （其余27位：张鑫/徐奕阳/范征/邹蕴/孙高德/蔡悦/黄嵩泉/喻学兵/卢若雨/顾峻峰/骆希聪/徐伟/钱文宇/陈哲锋/陆一帆/金辰宇/徐骋/陈方移/陈彤/江漪/陆诗杰/周全/吴畏/钱孟清/叶诚/须一平/朱立鸣）
│       ├── SOUL.md           灵魂命题/内在冲突/说话风格/典型句式/思维模式/张力/失败模式
│       ├── IDENTITY.md       圣号/官职/三国/权重/对应律
│       ├── BOUNDARY.md       必须反对与必须追问
│       ├── SUMMON.md         召唤/避免召唤规则
│       ├── GROWTH.md         成长日志（双画像+高价值+转折点）
│       └── RELATIONS.json    关系网（会议共现构建）
├── references/               模块化参考文件（5目录）
│   ├── core/                 核心制度
│   │   ├── orglaw.md         四轨制+议事程序+加权投票规则+续议制度
│   │   ├── philosophy.md     四律一核（结构/控制/铸模/价值）+ 否决信号
│   │   └── runtime.md        运行时细则（Phase详细步骤+脚本参数+投票规则+输出命名）
│   ├── saints/               圣人数据
│   │   ├── roster.md         28圣人名册 + 权重 + 路由关键词 + 路由速查表
│   │   └── saints.registry.json  机器可读圣人注册表
│   ├── memory/               记忆系统
│   │   └── memory_philosophy.md  记忆哲学宪法（分层/价值驱动/superseded/双画像）
│   ├── scenarios/            专利场景
│   │   ├── scenarios.md      6专利场景流程指引（查新/FTO/价值/OA/布局/无效）
│   │   ├── feature_analysis.md  特征分析框架（三要素拆解+语义扩展+检索式构建）
│   │   └── routing_rules.json    路由规则配置（轨道/权重/场景/领域必到/兜底）
│   └── templates/            输出模板
│       └── templates.md      结果md/纪要/过程/记忆batch/6专利交付物/续议/索引 模板
├── scripts/                  模块化脚本（5目录22脚本）
│   ├── routing/              路由与召集
│   │   ├── route_sages.py    自动路由（topic/mode/track/invites → roster+weights）
│   │   ├── auto_invite.py    智能动态补人（能力缺口检测+主动邀请）
│   │   ├── sptler_prelude.py 议题预热（判断是否值得开议会）
│   │   └── sptler_run.py     总控脚本（route/record/check 一条龙）
│   ├── memory/               记忆系统（10脚本）
│   │   ├── summon_sage.py    一次性召唤完整上下文（灵魂+记忆+关系+dry-run）
│   │   ├── read_soul.py      读取灵魂注入块
│   │   ├── read_memory.py    读取记忆摘要
│   │   ├── record_memory.py  记录经历+价值分+superseded（支持batch stdin）
│   │   ├── commit_citations.py  批量提交引用计数
│   │   ├── update_growth.py  自动更新GROWTH.md（双画像+高价值+转折点）
│   │   ├── build_relations.py   构建RELATIONS.json关系网
│   │   ├── compact_memories.py  价值驱动压缩（留/纲/删/转折豁免）
│   │   ├── memory_io.py      记忆导入导出
│   │   └── watch_memory.py   主动提醒记忆（未入会圣人的相关历史）
│   ├── output/               输出与跟踪
│   │   ├── index_meeting.py  登记会议索引
│   │   ├── continue_meeting.py  读取续议上下文
│   │   ├── briefing.py       议会简报（一键回顾）
│   │   └── action_board.py   行动项看板（跨会议跟踪+标记完成）
│   ├── saints/               圣人生成与查询
│   │   ├── generate_saints.py   生成灵魂文件+registry
│   │   └── list_memories.py     记忆总览查询
│   └── validate/             自检
│       ├── validate_sptler.py   全系统自检（文件/关键词/语法/旧规则残留）
│       └── validate_saints.py   圣人OS文件一致性校验
├── examples/                 5个脱敏案例
│   ├── 01-快速轨-OA流水线.md
│   ├── 02-魔法时刻-同类议题记忆引用.md
│   ├── 03-单圣人裁决-日常生产力.md
│   ├── 04-FTO场景-蓝牙定位模组.md
│   └── README.md
└── memories/                 运行时生成：每位圣人一个<姓名>.json（默认不入库）
```

## 圣人记忆系统

每位圣人有独立记忆档案 `memories/<姓名>.json`，记录其参与过的所有议事：

- **经历列表**：每次议事的议题、模式、立场、投票理由、设想、最终建议
- **演化画像**：总议事数、专长焦点、立场倾向（赞/反/弃）、风险偏好（审慎保守/平衡中立/积极进取）、常提观点

**工作流**：
1. **Phase 1 入会时**：`python scripts/memory/read_memory.py --sages <名单>` 读取每位与会者的记忆摘要，注入发言上下文——圣人能引用过往经验（"上次我们议过类似议题……"）
2. **Phase 5 议事后**：生成 batch json 并 `python scripts/memory/record_memory.py --batch <json>`，把每位与会者的经历写入档案并更新画像

圣人由此随时间积累、成长——议得越多，画像越清晰，发言越有积淀。可用 `python scripts/saints/list_memories.py` 查看所有圣人的记忆统计。

## 脚本示例

```bash
# 生成/校验 OpenClaw 圣人灵魂文件
python scripts/saints/generate_saints.py --force
python scripts/validate/validate_saints.py

# 读取某位圣人的灵魂注入块
python scripts/memory/read_soul.py --sage 徐奕阳

# 一次性召唤完整圣人上下文（灵魂+记忆+关系+相关历史记忆）
python scripts/memory/summon_sage.py --sage 徐奕阳 --topic "OA答复流水线"

# 自动路由（议题+模式+邀请名单 → 入会名单）
python scripts/routing/route_sages.py --topic "OA审查意见答复AI流水线" --mode dynamic --track auto --invites 陆一帆,金辰宇

# 从 stdin 记录记忆（免临时文件）
cat batch.json | python scripts/memory/record_memory.py --batch -

# 指定记忆目录（测试/多项目隔离）
python scripts/memory/read_memory.py --sage 王升 --mem-dir /tmp/sptler-mem

# 登记会议索引（供续议使用）
python scripts/output/index_meeting.py --meeting-id SPTLER-xxx --topic "..." --result-file result.md --attendees 王升,张鑫

# 读取上一次会议的行动项3，进入续议
python scripts/output/continue_meeting.py --last --item 3

# 压缩记忆，只保留最近20次经历
python scripts/memory/compact_memories.py --keep 20

# 技能自检
python scripts/validate/validate_sptler.py
```


> 记忆档案含真实议事记录，默认被 `.gitignore` 排除不入库。如需备份/共享，手动 force-add 或建私有仓库。


## 安装（多平台）

| 平台 | 安装路径 |
|---|---|
| Claude Code | `~/.claude/skills/sptler/` |
| Codex | `~/.codex/skills/sptler/` |
| Copilot CLI | `.github/skills/sptler/` |

```bash
git clone https://github.com/SuanFishXYY/sptler.git ~/.claude/skills/sptler
```

首次使用建议跑一次自检：

```bash
cd ~/.claude/skills/sptler && python scripts/validate/validate_sptler.py
```

## 技能规范

本技能遵循 [skill-creator](https://github.com/anthropics) 规范：frontmatter 仅含 `name` / `description` / `license` / `metadata`，详细内容按 progressive disclosure 拆分到 `references/`。

## License

MIT
