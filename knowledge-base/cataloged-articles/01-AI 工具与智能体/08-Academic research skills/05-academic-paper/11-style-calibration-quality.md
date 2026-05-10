# 风格校准与写作品质

Academic Paper 的 12 个 Agent 可以生成结构完整、论证清晰的学术论文。但有两个问题对研究者至关重要：(1) 这篇论文听起来像**我**写的吗？(2) 这篇论文读起来像**机器**写的吗？

ARS v2.9 引入的**风格校准（Style Calibration）**和**写作品质检查（Writing Quality Check）**分别回答了这两个问题。前者让 AI 学习你的声音，后者检测 AI 写作的常见模式。v3.3 引入的**反泄漏协议（Anti-Leakage Protocol）**和**VLM 图表验证**则保证了这些品质机制不会被 AI 自身破坏。

## 风格校准：让 AI 学你的声音

### 原理

风格校准是 Academic Paper intake 流程的 Step 10（可选步骤）。你提供 3 篇以上的既往论文，pipeline 会分析你的写作风格特征：

- **句子节奏**：短句 vs. 长句的交替模式、句首词的多样性、段落长度分布
- **词汇偏好**：你在"show / demonstrate / reveal / indicate / suggest"之间的选择倾向、连接词使用习惯（"however / nevertheless / in contrast"的选择模式）
- **引用整合方式**：你是倾向于作者突出型引用（"Smith (2023) found..."）还是信息突出型引用（"...has been demonstrated (Smith, 2023)"）？
- **学科用语**：你所在领域特有的表达方式和技术术语选择

### 三级优先级系统

风格校准不是自由应用——它受到一个清晰的三级约束：

| 优先级 | 层级 | 约束力 | 示例 |
|--------|------|--------|------|
| 1（最高）| 学科规范 | 硬性 | "p 值应报告为精确值，仅当 p < .001 时才写作 p < .001" |
| 2 | 期刊惯例 | 强制 | "Nature 要求 Methods 在正文末尾，而非单独一节" |
| 3（最低）| 个人风格 | 软性 | "作者倾向于将 however 放在句中而非句首" |

当学科规范和个人风格冲突时，学科规范无条件优先。这确保了风格校准不会以牺牲学术规范性为代价来追求"个性化"。

### 与"AI Humanizer"的本质区别

市面上的 AI humanizer 工具的目标是**隐藏 AI 参与的事实**——通过改写让文本看起来像人类写的，从而绕过 AI 检测。

ARS 的风格校准目标完全不同：
- **不是为了隐藏**，而是为了让 AI 的协助更贴合你的思维方式
- **不是为了逃避检测**，而是为了让文本读起来自然、连贯
- **风格校准是透明的**——你在论文中应该（按照期刊要求）声明 AI 的使用

这就是为什么 ARS 还提供了 `disclosure` 模式——帮你生成合规的 AI 使用声明。

---

## 写作品质检查：5 大类 AI 写作模式检测

写作品质检查在初稿自评阶段（peer_reviewer_agent 运行时）套用。它检测的不是"写得对不对"，而是"写得是否像机器"。

### 第 1 类：AI 高频词汇警告

25 个在 AI 生成的学术文本中过度出现的词汇和短语，包括但不限于：

- "delve into"（深入探讨）——AI 偏爱的最常见动词之一
- "moreover" / "furthermore" / "in addition" ——AI 倾向于过度使用三级递进连接词
- "underscores" / "highlights" / "elucidates" ——AI 偏好的学术动词
- "a testament to" ——在人类学术写作中很少出现的高频 AI 短语

检测到这些词汇时，不是禁止使用，而是提示作者：这个词汇在 AI 生成的学术文本中异常高频，你可以选择替换，也可以保留——但要知道你在做一个风格选择。

### 第 2 类：标点模式控制

- **Em dash 限制**：每 2,000 词 ≤ 3 个 em dash。AI 生成的学术文本中 em dash 的密度通常是人类写作的 3–5 倍
- **分号密度**：正常范围内不做限制，但连续 3 句使用分号连接是 AI 写作的强信号

### 第 3 类：开头废话侦测

AI 生成的学术段落经常以"废话导向句"开头：

- "In the rapidly evolving landscape of..."（在不断演变的...领域）
- "In recent years, there has been growing interest in..."（近年来，...引起了越来越多的关注）
- "The advent of...has fundamentally transformed..."（...的出现从根本上改变了...）

这些开头的问题不在于语法错误，而在于它们**延迟了信息密度**——读者要读完一整句才知道这段话在说什么。检查规则要求：每个段落的开头句应该包含具体的、信息密集的断言。

### 第 4 类：结构模式警告

AI 写作中常见的结构性习惯：

- **三连枚举强迫症**：AI 倾向于"三点"——"three key factors"、"three main approaches"、"three primary challenges"。当论文中出现过多"三个一组"的枚举时，它会标记出来
- **均等段落**：AI 倾向于生成长度几乎完全一致的段落（5–7 句）。人类写作的段落长度变化更大
- **同义反复**：连续两句用不同的词说同一件事——"X is critically important. The significance of X cannot be overstated."

### 第 5 类：句子长度变化检查

计算句长的标准差。AI 生成的学术文本往往有一个特征：句子长度对仗过于工整。人类写作中，一个 5 词的短句紧接一个 40 词的长句是正常的；AI 生成的文本中，句子长度倾向于在一个窄区间内小幅波动。

---

## 反泄漏协议：防止 AI 用记忆填补空白

**问题**：当一个 LLM 被要求写某篇论文的 Methodology 段落，但 session 中没有提供该论文的具体方法细节时，LLM 可能基于训练数据中的"一般知识"填补——"合理的 Methodology 看起来应该是什么样"。这就是 Mode 6（方法论伪造）的根本原因。

**ARS 的反泄漏协议**（v3.3，灵感来自 PaperOrchestra）制定了严格的规则：

1. **知识隔离**：优先使用 session 内材料填充论文内容
2. **缺失标记**：如果 session 材料中缺少某个信息，LLM 必须标记 `[MATERIAL GAP]` 而非用训练数据填补
3. **显式需求**：当遇到 `[MATERIAL GAP]` 时，停止当前段落的写作，向用户提出具体的信息请求——"需要对 X 方法的 Y 参数进行说明，请提供实际使用的值"

这不能完全消除方法论伪造的风险，但它将不可见的 AI 记忆填补转化为**可见的、可被用户干预的缺口标记**。

---

## VLM 图表验证：图表也需要质检

**问题**：AI 生成的学术图表可能出现：坐标轴标签错误、图例与数据不匹配、误差棒在正确方向但错误大小、配色在灰度打印下无法区分……

**ARS 的解决方案**（v3.3，选项启用）：使用视觉语言模型（Vision Language Model）对生成的图表做 10 项闭环保真检查：

1. 坐标轴标签是否正确？单位是否标注？
2. 图例是否与数据系列匹配？
3. 误差棒方向是否正确？大小是否合理？
4. 整体配色在灰度打印下是否可区分？
5. 图表标题是否准确描述图表内容？
6. 数据点的视觉呈现是否与底层数值一致？
7. 比例尺是否合理（没有通过截断 Y 轴制造视觉误导）？
8. 字体大小是否可读？
9. 引用来源是否标注？
10. 图表编号是否正确？

最多 2 轮修正。如果 2 轮后仍有问题，图表会被标记为 `[VISUAL VERIFICATION FAILED]` 并为用户提供手动修正指南。

---

## 这些机制的关系

```
写作流程
  │
  ├─ 风格校准（可选）──→ 学习你的声音
  │                       优先级：学科规范 > 期刊惯例 > 个人风格
  │
  ├─ 写作品质检查 ────→ 检测 AI 写作模式
  │                       5 大类：高频词 / 标点 / 开头废话 / 结构模式 / 句长变化
  │
  ├─ 反泄漏协议 ──────→ 防止 AI 记忆填补
  │                       [MATERIAL GAP] 标记替代静默填充
  │
  └─ VLM 图表验证（可选）→ 图表保真检查
                          10 项清单，最多 2 轮修正
```

四者共同构成了 ARS 的"写作品质保障层"——不是单点检查，而是覆盖文本、数据、图表和认知过程的系统性品质控制。

---

下一篇我们将转向 [Academic Paper Reviewer 的 7 个审稿 Agent](../06-reviewer/12-7-reviewer-agents.md)，理解多视角同行评议如何模拟真实学术期刊的审稿过程。

**参考来源**：
- `source/academic-research-skills/shared/style_calibration_protocol.md`
- `source/academic-research-skills/academic-paper/references/writing_quality_check.md`
- `source/academic-research-skills/academic-paper/references/anti_leakage_protocol.md`
- `source/academic-research-skills/academic-paper/references/vlm_figure_verification.md`
