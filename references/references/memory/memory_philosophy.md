# 算鱼圣人记忆哲学宪法

> 圣人是有完整历史、会改主意、记忆会被价值筛选的活人——不是一致性的机器，也不是流水账数据库。

本文件是记忆系统的设计宪法，所有记忆脚本（record/summon/compact/update_growth）必须遵循。

## 四条根本原则

### 1. 记忆是分层的活体，不是流水账

- **近期（如最近 20 次经历）**：完整经历（议题/设想/理由/建议/立场），可被引用注入。
- **远期**：只留骨架（数量 + 主题清单 + 关键转折），不占日常上下文。
- 圣人既有近期细节，又有长期演进骨架。

### 2. 遗忘是价值驱动的，不是时间驱动的

一条记忆的价值 = 通过决议 × 被引用次数：

- 高价值（通过且被引用）：长期保留，强化。
- 低价值（未通过或零引用）：近期详，远期归档为纲。
- 零价值（单次 verdict、从未被引用、未形成结论）：定期清理。

### 3. 圣人会改主意，历史全留，但矛盾被标记

- 不物理删除"被推翻的旧结论"——它是**有价值的转折点**，保留。
- 新结论推翻旧时，旧记忆标记 `superseded=true`，不再被 `summon_sage` 引用。
- 圣人能看到"我曾主张 A，后来改主张 B"，这是成长不是 bug。

### 4. 画像是双层的，反映"骨子"与"近况"

- **长期画像 profile**：全部历史 → 圣人的底色（"骨子里审慎"）。
- **短期画像 profile_recent**：最近 30 次 → 圣人的近况（"最近变激进了"）。
- 发言注入时两个都给；圣人自己可说"我向来保守，但最近几次我发现……"。

## 价值判断的三角（综合标准）

```
        通过决议（形成结论）
              ×
        被引用次数（用过即重要）
              =
        记忆价值分 value_score

高价值 → 长期保留 + 强化
低价值 → 近期详 / 远期纲
零价值 → 琐事删除
转折点（superseded 但代表改主意）→ 永久保留，不强化
```

## 记忆类型与处理（琐事删 + 转折留）

| 记忆类型 | 处理 |
|---|---|
| 通过决议 + 被引用过 | 长期保留，value_score 高 |
| 通过决议 + 零引用 | 近期详，远期归档为纲 |
| 未通过 / 被否决 | 保留（反面教材），不强化 |
| 单次 verdict + 零引用 + 无后续 | **琐事，定期删** |
| 被新结论推翻的旧立场 | **转折点，永久留**，标 superseded |

## experience 字段（记忆实体）

```json
{
  "topic": "...",
  "meeting_id": "...",
  "meeting_type": "regular|followup",
  "domain": "...",
  "stance": "赞成|反对|弃权(主持)",
  "verdict": "通过|否决|小修",
  "reason": "...",
  "ideas": "...",
  "recommendation": "...",
  "recorded_at": "YYYY-MM-DD HH:MM",
  "value_score": 0,
  "citation_count": 0,
  "superseded": false,
  "supersedes": [],
  "is_turning_point": false
}
```

### 字段语义

- `value_score`：价值分 = (verdict 通过 ? 1 : 0) × (citation_count + 1)。record 时初始化，summon 引用时 +1 后重算，compact 时按此分层。
- `citation_count`：被 `summon_sage --topic` 命中的次数。命中即 +1 并回写。
- `superseded`：bool。被新结论推翻时置 true，不再被 summon 引用，但保留为转折点。
- `supersedes`：本条记忆推翻了哪些旧记忆的 meeting_id 列表。record 时可由 batch 带入。
- `is_turning_point`：bool。superseded=true 的旧立场 + 推翻它的新立场，都标记为转折点，compact 永久豁免。

## 价值分与引用计数的更新时机

1. **record_memory**：新经历初始化 `value_score = (通过?1:0) × 1`、`citation_count = 0`、`superseded = false`。若 batch 带 `supersedes`，把对应旧经历标 `superseded=true, is_turning_point=true`，新经历也标 `is_turning_point=true`。
2. **summon_sage**：命中一条非 superseded 记忆时 `citation_count += 1`，重算 `value_score = (通过?1:0) × (citation_count+1)`，回写。superseded 记忆不计数、不引用，但可在输出里提示"曾主张 X 后改 Y"。
3. **compact_memories**：按 `value_score` + `is_turning_point` 三层处理（见下）。compact 后 value_score/citation_count 仍随新引用继续增长。
4. **update_growth**：生成双画像——profile（全量）+ profile_recent（最近 30 次）。

## compact_memories 价值驱动三层处理

对每位圣人的 experiences（按时间排序），逐条判定：

```
if is_turning_point:        永久保留（转折点豁免）
elif value_score >= 2:      长期保留（高价值：通过且被引用）
elif value_score == 1:      保留近期，超阈值的归档为纲（低价值：通过但零引用）
else:                       value_score == 0
    if 单次verdict 且 citation_count==0 且 无followup:  删除（琐事）
    else:                                               归档为纲
```

归档 = 移入 archive_summary（只留数量 + 主题清单），从 experiences 移除。
删除 = 物理移除（琐事）。
保留 = 留在 experiences，可被 summon 引用。

## 双画像计算

- **profile（长期）**：基于全部 experiences（含未 compact 的）的 stance/domain/risk 计算。底色。
- **profile_recent（短期）**：仅基于最近 30 次 experiences。近况。
- 两画像字段结构相同：total_meetings / domains / stances / risk_tendency / frequent_views / specialty_focus。
- summon 输出两者，让圣人能表达"骨子 vs 近况"的张力。

## 设计红线

- ❌ 不上向量库/RAG：22 文件，过度工程。
- ❌ 不跨圣人共享记忆池：会状态泄漏。
- ❌ 不物理删除转折点：那是圣人的成长轨迹。
- ❌ 不让旧 superseded 记忆被引用：会引用过时结论。
- ✅ 记忆系统只记录与按价值筛选，不替圣人判断对错（对错由议会四律+投票决定）。
