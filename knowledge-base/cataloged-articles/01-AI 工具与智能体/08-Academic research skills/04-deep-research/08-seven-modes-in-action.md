# 七种研究模式实战

Deep Research 提供 7 种研究模式，覆盖从"我不知道该研究什么"到"帮我验证这篇论文的每一条引用"的全光谱。选择正确的模式可以大幅降低 token 消耗，同时获得更精准的研究产出。

## 模式一览

| 模式 | 光谱 | 输出长度 | 监管强度 | 一句话 |
|------|------|---------|---------|--------|
| `socratic` | Originality | 研究计划摘要 | Very High | "我还不太确定研究方向" |
| `full` | Balanced | 3,000–8,000 词 | High | "帮我做完整研究" |
| `systematic-review` | Fidelity | 5,000–15,000 词 PRISMA | Medium | "要做系统评价/Meta 分析" |
| `lit-review` | Fidelity | 注释书目 + 综合 | Medium | "需要文献回顾" |
| `fact-check` | Fidelity | 逐条验证报告 | Medium | "验证这些说法" |
| `review` | Balanced | 评审报告 | High | "评估这篇论文" |
| `quick` | Fidelity | 500–1,500 词简报 | Medium | "30 分钟快速了解" |

光谱分类（Fidelity–Originality）来自 Lu 2026 Fig 1c 的分析框架：
- **Fidelity**：注重准确性和与证据的一致性——输出应该忠实于已验证的事实
- **Originality**：鼓励探索和新见解——输出应该帮助用户产生新的想法
- **Balanced**：两者兼顾

---

## Socratic Mode：当你不确定该研究什么

**最佳场景**：你有一个模糊的研究兴趣，但还没有形成清晰的研究问题。

**工作方式**：Socratic Mentor Agent 通过一系列引导性问题，帮助你：
1. 定义研究范围——从"AI 和教育"窄化到"生成式 AI 在本科编程教学中的反馈效果"
2. 识别关键概念和变量——自变量（AI 反馈类型）、因变量（学习效果）、调节变量（学生先验知识水平）
3. 评估研究可行性和新颖性——这个 RQ 有文献基础吗？有没有足够的新意？

**关键设计**：`socratic` 模式使用**意图匹配**而非关键词触发。它不检测"帮助"或"引导"等特定词汇，而是理解"用户的请求意味着他们仍在探索阶段"这个语义信号。这意味着它可以**在任何语言**下工作。

v3.0 升级后，Socratic Mentor 会自动判断用户处于**探索型**（还在找方向）还是**目标型**（有方向但需要细化）。探索型模式停用自动收束，最大轮数提升到 60。每 5 轮重新评估意图状态。

**对话收敛条件**（v2.6）：4 个信号——用户能清晰表述 RQ（S1）、RQ 与现有文献有明确区分（S2）、方法论可行性得到确认（S3）、用户表达了向下一阶段推进的意愿（S4）——当这些信号同步出现时，Socratic Mentor 会自动提议收敛。

**成本**：~$0.60（约 30K 输入 + 15K 输出 token）。

---

## Full Mode：完整研究

**最佳场景**：研究问题清晰，需要完整的文献调研和综合分析。

**工作方式**：13 个 Agent 全部激活，执行完整的研究流程：
1. RQ 提炼和方法论设计
2. 文献检索 + Semantic Scholar API 验证
3. 综合分析 + 内部质控
4. 结构化研究报告编译

**输出**：一份 3,000–8,000 词的 APA 7.0 格式研究报告，包含 RQ Brief、Methodology Blueprint、Annotated Bibliography（经过 S2 API 验证）、Synthesis Report 和 INSIGHT Collection。

**成本**：~$1.20。

---

## Systematic-Review Mode：PRISMA 系统评价

**最佳场景**：需要按照 PRISMA 2020 标准进行系统评价或 Meta 分析。

**工作方式**：在 full mode 的 Agent 团队之上，额外激活：
- `risk_of_bias_agent`：对纳入研究做偏倚风险评估
- `meta_analysis_agent`：对定量研究做 Meta 分析
- `monitoring_agent`：全程跟踪 PRISMA 流程合规性

输出遵循 PRISMA 2020 checklist，包含完整的检索策略记录、纳入/排除流程图、偏倚风险评估表。v3.4.0 起，Compliance Agent 在诚信闸门中运行 PRISMA-trAIce 17 项合规检查。

**特殊行为**：当 `ARS_PASSPORT_RESET=1` 时，每个 FULL checkpoint 强制上下文重置——系统评价的每个阶段独立性很强，不需要保留前序对话的完整上下文。

**成本**：~$2.00（约 100K 输入 + 50K 输出 token）。

---

## Lit-Review Mode：文献回顾

**最佳场景**：需要一份特定主题的文献回顾，但不要求 PRISMA 级别的系统性。

**工作方式**：bibliography_agent + synthesis_agent + report_compiler_agent 协作，产出注释书目和主题综合。

与 `systematic-review` 的区别：
- 不强制 PRISMA 报告格式
- 文献检索可以是有针对性的（而非穷尽的）
- 不需要偏倚风险评估和 Meta 分析

**成本**：介于 full 和 systematic-review 之间。

---

## Fact-Check Mode：事实核查

**最佳场景**：你有一段文本（论文草稿、新闻报道、研究声明），需要逐条核验其中的事实性主张。

**工作方式**：对文本中的每个事实性声明，做三层验证：
1. 是否有文献支持？（citation check）
2. 文献是否真的包含该发现？（attribution check）
3. 数字/统计是否准确？（numerical check）

**输出**：逐条声明验证报告，每条标记为 VERIFIED / NOT_FOUND / MISMATCH / INSUFFICIENT EVIDENCE。

---

## Review Mode：评估研究品质

**最佳场景**：你有一篇已发表的论文（或预印本），需要评估其研究方法、论证逻辑和证据品质。

**工作方式**：以审稿人的视角对论文做结构化的品质评估——但不走 Academic Paper Reviewer 的完整 7 Agent 流程。Review Mode 更轻量、更快。

**与 academic-paper-reviewer 的区别**：review mode 属于 deep-research，关注的是论文作为"研究证据来源"的品质；academic-paper-reviewer 是独立的 Skill，关注的是论文作为"投稿"的审稿意见。

---

## Quick Mode：快速简报

**最佳场景**：需要 30 分钟级的快速研究概览。

**工作方式**：简化流程——只激活核心 Agent（research_question_agent + bibliography_agent + report_compiler_agent），跳过深度综合和质控。

**输出**：500–1,500 词的研究简报，勾画主要文献和关键发现的基本轮廓。

**成本**：最低——适合在投入完整研究之前做方向性探索。

---

## 模式选择决策树

```
你有一个研究需求
│
├─ 不确定具体 RQ？ → socratic
│
├─ 有明确 RQ
│  ├─ 需要系统评价？ → systematic-review
│  ├─ 需要完整研究？ → full
│  ├─ 只需要文献回顾？ → lit-review
│  └─ 只需要快速概览？ → quick
│
├─ 有一段文本需要核验？ → fact-check
│
└─ 有一篇论文需要评估？ → review
```

---

下一篇我们将转向 [Academic Paper 的 12 个 Agent 写作团队](../05-academic-paper/09-12-agents-writing-team.md)，理解从研究产出到论文初稿的完整写作管线。

**参考来源**：
- `source/academic-research-skills/MODE_REGISTRY.md`
- `source/academic-research-skills/deep-research/SKILL.md`
- `source/academic-research-skills/deep-research/references/socratic_questioning_framework.md`
