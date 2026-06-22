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

## ✨ 三个让人眼前一亮的特性

### 🧠 记忆魔法时刻
圣人记得自己历次议事的立场和建议。同类问题第二次问，开口就引用上次：
> [徐奕阳] 上次我们议过 OA 流水线(06-15)，当时定的是"三段式Prompt模具+半自动起步"。这次我直接按那个骨架展开……

这是裸 Claude 做不到的——它每次从零开始，而你的圣人班子越用越懂你。

### 🪶 四轨自动降级
按问题重量自动选最轻的轨道，**小问题不走大流程**：
```
单圣人裁决(1人,3句) → 快速轨(3-5人) → 正式轨(7-9人) → 续议轨
```

### 📄 产出真实交付物
议会是手段，交付物是目的。专利→权利要求骨架，架构→ADR，流程→SOP——直接给你本来就要写的文件，不只是"关于会议的文档"。

## 触发

```bash
/sptler {问题}        # 标准议会：先选模式、邀请、名单确认
/sptler! {问题}       # 简报模式：免提问，自动动态路由，单轮给结论+结果md
/算鱼议会 {问题}
/议会 {问题}
/议会! {问题}        # 同 /sptler!
/开会 {问题}
/议一议 {问题}
/sptler 记忆 王升     # 快捷查看某位圣人的记忆档案
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
