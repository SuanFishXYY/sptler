# 示例八：lite 精简模式（/sptler#）· 省 token 快车道

> 这是 sptler 省 token 的场景。同一个"权利要求边界"问题，标准 verdict（示例三）要读 references + 完整灵魂 + 记忆注入；**lite 模式不读 references、薄灵魂、无记忆注入**，单轮收口。当你只想要一个专家的快判断、不想付仪式税时用它。

## 议题

`/sptler# 这个权利要求边界怎么收？`

（`#` = lite 触发。单一明确、单领域、无战略信号——lite 默认 verdict 优先）

## Lite 路由（verdict 优先，1 圣人）

```bash
python scripts/routing/route_sages.py --topic "这个权利要求边界怎么收" --track auto
```

```
[邹蕴] 路由判定：单圣人裁决（verdict轨：单一明确问题，单圣人裁决），目标 1 人，主持=邹蕴
- [卢若雨] 位控圣｜专科｜权重 1.5｜关键词命中：边界、权利要求 + 动态加成
```

## Lite 召唤（薄灵魂 · 一行注入 · 不读记忆）

标准 verdict 召唤（示例三）会注入完整灵魂+记忆+关系；lite 只取一行身份+边界：

```bash
python scripts/memory/summon_sage.py --sage 卢若雨 --lite
```

```
【卢若雨·lite】圣号：位控圣｜官职：位界尚书｜角色：专科 ｜ 边界：边界过宽不稳
```

（51 词 → 1 词；不读 SOUL/SUMMON/记忆/关系/历史）

## Lite 裁决（3 句话，不投票不四律，零 AskUser 单轮收口）

> lite 内联 cheat-sheet 即内核——四律一行式：结构律·王升「先骨架后血肉」、控制律·张鑫「流动有界自动有兜底」、铸模律·徐奕阳「经验铸成模板」、价值律·范征「价值落点在哪」。本议题命中结构律边界维度，未触发否决。

```
[卢若雨] 权利要求边界收口——独权钉死必要技术特征 A/B/C（缺一不可），可扩展的 D 退守从属权；边界收窄靠"让对手绕不过"而非堆词。
[卢若雨] 风险：独权过宽易被无效、过窄缩水——从属权作退守阵地。
[邹蕴] 结论：独权 A/B/C 必要特征钉死、D 退从属，从属权做退守；风险是宽窄失度。议会到此结束。
```

## Lite 结果 md（模板九 · 4 节 · ≤15 行）

```markdown
# 算鱼议会决议 · 权利要求边界怎么收（lite）

> 编号 SPTLER-20260701-xxx ｜ 模式 lite ｜ 议长 邹蕴 ｜ 主笔 卢若雨（1.5）

## 一、议题
用户问"权利要求边界怎么收"——议长提炼：独权/从属权的必要特征划分。

## 二、裁决
[卢若雨] 独权钉死必要特征 A/B/C，D 退守从属权；收窄靠"绕不过"非堆词。——风险：过宽易无效、过窄缩水，从属权做退守阵地。

## 三、交付物指针
无专属交付物，本结果 md 即结论。

## 四、收口
[邹蕴] 独权必要特征钉死、可扩展项退从属、从属权退守。议会到此结束。
```

## Token 经济对照（同问题 vs 标准 verdict）

| 环节 | 标准 verdict（示例三） | lite（/sptler#） |
|---|---|---|
| references 读取 | ~3424 词（philosophy/orglaw/runtime/roster/templates） | **0**（内联 ~120 词 cheat-sheet） |
| 灵魂注入 | ~50 词（完整 SOUL/IDENTITY/BOUNDARY/SUMMON） | **1 词**（薄灵魂一行） |
| 记忆注入 | 有（相关记忆+引用回写） | **无**（零注入，记忆仍可后写） |
| 结果 md | 9 节（模板一压缩版） | **4 节**（模板九，≤15 行） |
| **单次合计省** | — | **≈ 3300 词** |

## Lite 留痕闭环（事件留、画像不动）

lite 不是零留痕（那是 verdict），而是**轻留痕**——三处对齐 `lite:true`：

| 环节 | 标记 | 效果 |
|---|---|---|
| `route_sages --lite` | 返回 `lite:true` | caller 知道走精简分支 |
| `record_memory.py --lite` | experience 标 `lite:true` | 事件保留可回溯（"上次 lite 怎么说的"），但**不重算风险画像**——一次快调不翻转圣人底色 |
| `index_meeting.py --lite` | index.json entry 标 `lite:true` | `continue_meeting` 读到后走精简续议（≤3人、不重跑四律、零 AskUser） |

所以 lite 会议可被续议引用，但续议也保持精简——闭环一致。

## 什么时候不要用 lite

- **不可逆/战略决策**——lite 跳过四律详查与加权投票，不适合。
- **专利场景**（查新/FTO/OA/布局/无效）——需 feature_analysis.md + 场景专属流程，lite 跳过。
- **需要记忆连续性**——同类问题第二次问想引用上次结论时，用标准模式（记忆是 sptler 最大差异化，见示例二）。

## 复现

```bash
python scripts/routing/route_sages.py --topic "这个权利要求边界怎么收" --track auto
python scripts/memory/summon_sage.py --sage 卢若雨 --lite
```
