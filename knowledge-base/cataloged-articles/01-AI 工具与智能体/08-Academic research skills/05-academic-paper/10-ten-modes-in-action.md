# 十种写作模式详解

Academic Paper 是 ARS 中模式最多的 Skill——10 种模式覆盖了从"帮我理清论文思路"到"生成 NeurIPS 的 AI 使用声明"的完整写作生命周期。理解每种模式的定位和适用场景，是用好 ARS 的关键。

## 模式全景

| # | 模式 | 光谱 | 监管 | 核心场景 |
|---|------|------|------|---------|
| 1 | `plan` | Originality | Very High | "我不知道怎么写" |
| 2 | `outline-only` | Balanced | High | "先给我一个大纲" |
| 3 | `full` | Balanced | High | "帮我写完整论文" |
| 4 | `abstract-only` | Fidelity | Medium | "只需要摘要" |
| 5 | `lit-review` | Fidelity | Medium | "把文献整理成综述论文" |
| 6 | `revision` | Fidelity | High | "根据审稿意见修改" |
| 7 | `revision-coach` | Balanced | Medium | "帮我解读审稿意见" |
| 8 | `format-convert` | Fidelity | Low | "转成 LaTeX / 改引用格式" |
| 9 | `citation-check` | Fidelity | Low | "检查引用格式和准确性" |
| 10 | `disclosure` | Fidelity | Low | "生成 AI 使用声明" |

监管强度从 Very High（用户主导对话 + 每步强制确认）到 Low（机械化/模板驱动，人类输入最少）。

---

## Plan Mode：苏格拉底式论文规划

**触发**："引导我写论文" / "帮我规划论文" / "step by step paper"

**与 deep-research 的 Socratic Mode 的区别**：
- deep-research socratic：引导你理清**研究问题**和**方法论**
- academic-paper plan：引导你规划**论文章节**和**论证结构**

Plan Mode 在章节层面应用 SCR 协议。Socratic Mentor 在每个章节转换前先问："你期望这一章得出什么结论？"然后呈现 AI 的规划建议，制造认知冲突以促进反思。

**输出**：Chapter Plan + INSIGHT Collection。不含论文正文——那需要 `full` 模式。

**成本**：~$0.80。

---

## Outline-Only Mode：只要大纲

**触发**："帮我搭论文大纲" / "just need an outline"

**与 Plan Mode 的区别**：
- `plan`：苏格拉底式对话引导，互动性强，用户主导
- `outline-only`：直接生成，效率优先，AI 主导

**输出**：详细大纲 + 证据映射表（每个章节对应哪些文献和论证单元）。

适合已经很清楚论文要写什么的用户——不需要对话引导，只需要结构化的大纲。

---

## Full Mode：完整论文撰写

**触发**："帮我写一篇论文" / "write a paper"

**流程**：
1. Intake——接收材料，配置参数（语言、引用格式、论文结构类型）
2. 文献策略映射——将上游研究产出映射到论文章节
3. 结构设计——生成大纲 → **用户批准** → 继续
4. Phase 4a——Writer 论文盲读预承诺（Generator-Evaluator 合约）
5. Phase 4b——Writer 论文可见撰写 + 自评
6. 内部同行评审——peer_reviewer_agent + citation_compliance_agent + abstract_bilingual_agent
7. Phase 6a——Evaluator 论文盲读预承诺
8. Phase 6b——Evaluator 论文可见评分 + 决策

**输出**：完整初稿（可选 IMRaD / 主题式 / 理论分析 / 案例分析 / 政策简报结构）、双语摘要、图表、引用列表。

**成本**：~$1.80。

---

## Abstract-Only Mode：只写摘要

**触发**："帮我写摘要" / "write abstract"

**工作方式**：从论文全文中提取关键信息，按照 APA 7.0 结构化摘要格式（Background / Objective / Method / Results / Conclusion）生成中英双语摘要和关键词。

**特别适用**：会议投稿（很多会议只需要摘要）、论文修改后重新生成摘要、已有英文摘要需要补充中文版本。

---

## Lit-Review Mode：文献回顾论文

**触发**："把这批资料写成文献回顾论文" / "literature review paper"

**与 deep-research lit-review 的区别**：
- deep-research `lit-review`：以研究简报格式输出的注释书目——"研究附件"
- academic-paper `lit-review`：以论文格式输出的文献回顾——"论文体裁"

**输出**：一篇以主题式文献回顾为结构的完整论文，包含引言、主题分类回顾、研究空白识别、未来方向建议。

---

## Revision Mode：修订模式

**触发**："根据审稿意见修改" / "revise paper"

**工作方式**：
1. 解析审稿意见——将每条 comment 归类：需要改的（revision）、需要回应的（clarification）、需要反驳的（rebuttal）
2. 逐点修改——对每个 revision item 执行具体修改
3. 生成 Delta 报告——记录什么改了、为什么改
4. 起草回复信——为每条审稿意见准备回复文本

**与 Revision Coach 模式的配合**：先用 `revision-coach` 生成修订路线图，确认方向后再用 `revision` 执行修改。

---

## Revision-Coach Mode：修订教练

**触发**："帮我整理审稿意见" / "parse reviews"

这个模式**不修改论文**。它做的事是：
1. 解析审稿意见——将分散的多位审稿人意见归纳为结构化的修订路线图
2. 识别一致性——多位审稿人的意见是否有共识点？
3. 识别冲突——不同审稿人是否有矛盾意见？矛盾点在哪里？
4. 草拟回复信框架——为每条意见准备回复的骨架，但不填充具体内容

**输出**：Revision Roadmap + Response Letter Skeleton。

这是 AI 审稿意见的"翻译器"和"组织者"。它帮你理解审稿人到底在说什么，但修改论文的实际决定权在你。

---

## Format-Convert Mode：格式转换

**触发**："转成 LaTeX" / "引用格式转 IEEE" / "convert to"

**功能**：
- 引用格式转换：APA 7.0 ↔ Chicago ↔ MLA ↔ IEEE ↔ Vancouver
- 文件格式转换：Markdown → LaTeX → PDF（via tectonic）或 Markdown → DOCX（via Pandoc）
- APA 7.0 LaTeX 输出使用 `apa7` document class（`man` 模式）+ XeCJK 中英双语支持

**字体要求**：Times New Roman + 思源宋體 VF + Courier New。

**成本**：低——这是最机械化的模式。

---

## Citation-Check Mode：引用检查

**触发**："检查引用格式" / "check citations" / "verify references"

**工作方式**：对论文中的每条引用做格式和准确性检查：
- 引用格式是否与目标格式一致？
- 文内引用和参考文献列表是否一一对应？
- 是否有遗漏的引用？
- DOI / URL 是否有效？

**与 deep-research source_verification 的区别**：citation-check 关注的是**格式合规性**（引用写对了吗），source_verification 关注的是**存在性和归因准确性**（这篇引用真的存在吗，这篇论文真的有这个发现吗）。

---

## Disclosure Mode：AI 使用声明

**触发**："生成 NeurIPS 的 AI 使用声明" / "AI disclosure for [venue]"

**功能**：针对特定期刊/会议生成 AI 使用揭露声明。v1 覆盖：
- ICLR
- NeurIPS
- Nature
- Science
- ACL
- EMNLP

每个 venue 有不同的 AI 使用声明政策和格式要求。disclosure mode 根据目标 venue 的政策生成合规的声明文本。

---

## 模式选择速查

| 你想要的 | 对应模式 |
|---------|---------|
| 跟我对话帮我理清论文思路 | `plan` |
| 直接给我一个结构完整的大纲 | `outline-only` |
| 写完整初稿 | `full` |
| 已有的数据/分析，只写摘要 | `abstract-only` |
| 把文献调研写成综述论文 | `lit-review` |
| 审稿意见回来了，需要修改论文 | `revision` |
| 审稿意见太复杂，先帮我理一理 | `revision-coach` |
| 改引用格式或文件格式 | `format-convert` |
| 投稿前检查引用有没有错误 | `citation-check` |
| 生成 AI 使用合规声明 | `disclosure` |

---

下一篇我们将探讨 [风格校准与写作品质检查](11-style-calibration-quality.md)——ARS 如何从你的历史论文中学习你的写作声音，以及用 5 大类规则检测 AI 写作的常见模式。

**参考来源**：
- `source/academic-research-skills/MODE_REGISTRY.md`
- `source/academic-research-skills/academic-paper/SKILL.md`
- `source/academic-research-skills/academic-paper/references/disclosure_mode_protocol.md`
