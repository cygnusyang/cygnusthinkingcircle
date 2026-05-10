# 四大技能一览

ARS 由 4 个独立的 Claude Code Skill 组成，每个都可以单独使用，也都可以被 Academic Pipeline 编排为端到端流程。本文逐一介绍它们的定位、核心能力、输入输出和协作关系。

## 概览

| Skill | 版本 | Agent 数 | 模式数 | 一句话定位 |
|-------|------|---------|--------|-----------|
| `deep-research` | v2.9.2 | 13 | 7 | 上游研究引擎：从问题到证据 |
| `academic-paper` | v3.1.1 | 12 | 10 | 下游出版引擎：从证据到论文 |
| `academic-paper-reviewer` | v1.9.0 | 7 | 6 | 多视角同行评议：从论文到决策 |
| `academic-pipeline` | v3.7.0 | 4 | 1 (+1 resume) | 全流程编排器：从调度到品质保障 |

25 种模式，统一由 [MODE_REGISTRY.md](https://github.com/Imbad0202/academic-research-skills/blob/main/MODE_REGISTRY.md) 管理。

---

## Deep Research — 研究引擎

**定位**：上游研究。将模糊的研究兴趣转化为可操作的研究问题、可验证的证据体系和结构化的研究报告。

**13 个 Agent 各司其职**：
- `research_question_agent`：从兴趣中提炼研究问题
- `research_architect_agent`：设计方法论蓝图
- `bibliography_agent`：文献检索与注释书目
- `source_verification_agent`：Semantic Scholar API 批量验证引用
- `synthesis_agent`：跨文献整合与矛盾分析
- `meta_analysis_agent`：Meta 分析
- `editor_in_chief_agent`：内部质量控制
- `devils_advocate_agent`：论点挑战
- `risk_of_bias_agent`：偏倚风险评估
- `ethics_review_agent`：伦理审查
- `socratic_mentor_agent`：苏格拉底式引导
- `report_compiler_agent`：报告编译
- `monitoring_agent`：流程监控

**7 种模式**：`full`（完整研究）、`quick`（快速简报）、`socratic`（苏格拉底引导）、`systematic-review`（PRISMA 系统评价）、`fact-check`（事实核查）、`lit-review`（文献回顾）、`review`（论文评审）

**关键输出**：Research Question Brief、Methodology Blueprint、Annotated Bibliography（经过 S2 API 验证）、Synthesis Report、INSIGHT Collection

---

## Academic Paper — 写作引擎

**定位**：下游出版。将研究成果转化为符合 APA 7.0 / IEEE / Chicago 等格式的学术论文。

**12 个 Agent 的分工**：
- `intake_agent`：接收和配置写作任务
- `literature_strategist_agent`：文献策略——将研究产出映射到论文结构
- `structure_architect_agent`：论文结构设计
- `argument_builder_agent`：论证构建
- `draft_writer_agent`：初稿撰写
- `citation_compliance_agent`：引用合规性检查
- `abstract_bilingual_agent`：中英双语摘要生成
- `peer_reviewer_agent`：内部同行评审
- `formatter_agent`：格式转换与排版
- `socratic_mentor_agent`：苏格拉底式引导规划
- `visualization_agent`：图表生成
- `revision_coach_agent`：修订指导

**10 种模式**：覆盖从规划（`plan`、`outline-only`）到撰写（`full`、`lit-review`）、从修改（`revision`、`revision-coach`）到出版（`abstract-only`、`format-convert`、`citation-check`、`disclosure`）的完整生命周期。

**v3.6.8 Generator-Evaluator 合约**：在 `full` 模式中，Phase 4（撰写）和 Phase 6（内部评审）各拆分为两个阶段——先做论文盲读的预承诺（Phase 4a/6a），再做论文可见的实际工作（Phase 4b/6b）。这防止了 Writer 看到论文后才调整评分标准、Evaluator 看了论文才决定怎么打分的自我欺骗行为。

---

## Academic Paper Reviewer — 审稿引擎

**定位**：独立质检。模拟真实学术期刊的同行评议过程，提供多视角、结构化的审稿意见。

**7 个 Agent 的角色**：
- `field_analyst_agent`：自动检测论文学科领域，据此配置 3 位领域适配的审稿人
- `eic_agent`（主编）：综合所有审稿意见，做出编辑决定
- `methodology_reviewer_agent`：方法论专家
- `domain_reviewer_agent`：领域内容专家
- `perspective_reviewer_agent`：跨学科视角
- `devils_advocate_reviewer_agent`：魔鬼代言人——对论文的核心论点提出系统性质疑
- `editorial_synthesizer_agent`：编辑综合者——将 5 份审稿报告整合为统一的编辑决定和修订路线图

**0-100 品质量表**是 Reviewer 的核心创新。它不是给出"通过/不通过"的二元判断，而是在 7 个维度上给出量化评分：

| 分数段 | 决策 |
|--------|------|
| ≥ 80 | 接受 |
| 65–79 | 小修 |
| 50–64 | 大修 |
| < 50 | 退稿 |

**v3.6.2 Sprint Contract 协议**：在 `full` 和 `methodology-focus` 模式中，每位审稿人在阅读论文之前必须先承诺评分标准和失败条件（Phase 1：论文盲读），再阅读论文进行实际评审（Phase 2：论文可见）。综合者通过三步机械协议（构建跨审稿矩阵 → 用 panel-relative 量化词评估失败条件 → 按严重性解决优先级）来合成最终报告，有一份禁止操作清单来约束其行为。

**6 种模式**：`full`（完整评审）、`re-review`（验收评审）、`quick`（快速评估）、`methodology-focus`（方法论聚焦）、`guided`（引导式改进）、`calibration`（评审校准）

---

## Academic Pipeline — 编排引擎

**定位**：总调度。将上述三个 Skill 编排成端到端流程，并在此之上叠加诚信验证、苏格拉底指导、中途强化和协作品质评估。

**4 个 Pipeline Agent**：
- `integrity_verification_agent`：在 Stage 2.5 和 4.5 运行 7 类失败模式检查
- `state_tracker_agent`：跟踪 pipeline 状态、管理 Material Passport
- `pipeline_orchestrator_agent`：总调度——决定何时调用哪个 Skill
- `collaboration_depth_agent`（v3.5.0+）：纯咨询性——在每次 checkpoint 评估人机协作品质，永不妨碍流程

**Pipeline 保证**：
- 每个阶段结束都需要用户明确的 checkpoint 确认
- Stage 2.5 和 4.5 的诚信闸门不可跳过
- R&R 追溯矩阵（Schema 11）独立验证作者的修订声明
- v3.4.0 起，Compliance Agent 在诚信闸门中执行 PRISMA-trAIce 17 项合规检查 + RAISE 四原则 + 8 角色矩阵

---

## 四个 Skill 如何协作

典型的一次完整运行：

1. **Stage 1**：用户说"我想研究 AI 对高等教育质量保证的影响" → `deep-research` 全模式运行 13 个 Agent → 产出 Research Question Brief + Methodology Blueprint + 注释书目（S2 API 验证） → 用户确认
2. **Stage 2**：`academic-paper` 全模式运行 12 个 Agent（消费 Stage 1 的研究产出） → 产出大纲 → 用户批准 → 撰写初稿 + 双语摘要
3. **Stage 2.5**：Pipeline 闸门——`integrity_verification_agent` 运行 7 类失败模式检查 + 30% 声明抽样验证 → 用户审阅诚信报告
4. **Stage 3**：`academic-paper-reviewer` 全模式运行 7 个 Agent（Sprint Contract 协议） → 5 份审稿报告 + 编辑决定 → 用户做出接受/修改/退稿决定
5. **Stage 4–4'**：`academic-paper` 修订模式 + `academic-paper-reviewer` 复审模式 → 逐点回复 + 最终修订稿
6. **Stage 4.5**：最终诚信闸门——零容忍、100% 声明验证
7. **Stage 5–6**：格式转换 + 出版就绪输出 + 过程记录 + AI 自我反思报告

---

## 选择单独使用还是走完整 Pipeline？

| 你的需求 | 推荐 |
|---------|------|
| 只想做文献调研 | 单独使用 `deep-research` |
| 已有完整数据和分析，只需要写论文 | 单独使用 `academic-paper` |
| 论文写好了，想在投稿前自查 | 单独使用 `academic-paper-reviewer` |
| 从零开始到投稿就绪 | 走完整 `academic-pipeline` |
| 收到了期刊的审稿意见 | Pipeline 从 Stage 4 中途进入 |

---

下一篇将深入 [Deep Research 的 13 个 Agent 团队](../04-deep-research/07-13-agents-team.md)，理解每个 Agent 如何分工协作完成研究任务。

**参考来源**：
- `source/academic-research-skills/MODE_REGISTRY.md`
- `source/academic-research-skills/docs/ARCHITECTURE.md`
- `source/academic-research-skills/academic-paper-reviewer/references/sprint_contract_protocol.md`
