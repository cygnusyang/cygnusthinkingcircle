# 12 个 Agent 的写作团队

如果 Deep Research 是 ARS 的"调研部"，Academic Paper 就是"出版部"。它消费上游的研究产出——RQ Brief、Methodology Blueprint、注释书目、综合报告——然后通过 12 个角色分工明确的 Agent，将原始材料转化为符合学术出版标准的完整论文。

本文逐一剖析这 12 个 Agent 的职责，以及它们如何通过 v3.6.8 的 Generator-Evaluator 合约防止自我欺骗。

## Agent 全景

12 个 Agent 按写作流程分为五组：

| 组 | Agent | 职责 |
|----|-------|------|
| **启动与文献** | intake_agent | 任务接收与配置 |
| | literature_strategist_agent | 文献策略映射 |
| **结构与论证** | structure_architect_agent | 论文结构设计 |
| | argument_builder_agent | 论证构建 |
| **撰写与引用** | draft_writer_agent | 初稿撰写 |
| | citation_compliance_agent | 引用合规检查 |
| | abstract_bilingual_agent | 双语摘要 |
| **内审与图表** | peer_reviewer_agent | 内部同行评审 |
| | visualization_agent | 图表生成 |
| **引导与出版** | socratic_mentor_agent | 苏格拉底规划引导 |
| | revision_coach_agent | 修订指导 |
| | formatter_agent | 格式转换 |

---

## 第一组：启动与文献

### intake_agent

**任务**：接收上游研究产出（或用户直接提供的材料），配置写作任务。

intake_agent 是写作管线的入口。它做三件事：
1. **消费材料**：读取 RQ Brief、Methodology Blueprint、Annotated Bibliography、Synthesis Report 和 Material Passport
2. **检测模式**：判断用户想要完整的论文、只做大纲、修改现有稿件还是格式转换
3. **配置参数**：设定语言（中/英）、引用格式（APA/Chicago/IEEE/MLA/Vancouver）、论文结构（IMRaD/主题式回顾/理论分析/案例分析/政策简报）

### literature_strategist_agent

**任务**：将上游的文献产出映射到论文结构中。

v3.6.5+ 的关键升级：与 bibliography_agent 一样，literature_strategist_agent 支持**文献库优先（corpus-first）**流程。如果 Material Passport 携带了 `literature_corpus[]`，它会先预筛选个人文献库，再用外部搜索填补空白。

它的核心工作是决定**哪些文献在论文的哪个位置发挥作用**——Introduction 的文献用于建立研究背景和空白，Method 的文献用于证明方法论选择的合理性，Discussion 的文献用于与已有发现进行对比和解释。

---

## 第二组：结构与论证

### structure_architect_agent

**任务**：设计论文的章节结构。

不只是一个"IMRaD 模板填充器"。它需要：
- 根据论文类型选择结构（实证研究用 IMRaD、综述用主题式、理论论文用分层论证）
- 决定每个章节的篇幅分配
- 识别哪些发现应该放在正文中（高贡献、直接回答 RQ）、哪些应该放入补充材料
- 设计图表在文本中的位置策略

### argument_builder_agent

**任务**：在章节骨架中填入论证链条。

这个 Agent 使用了 Toulmin 论证模型（Claim + Grounds + Warrant + Backing + Qualifier + Rebuttal），将论文的核心论点分解为可独立验证的论证单元。v3.1 引入的认知框架 reference 文件教 Agent "如何思考"论证结构，而非仅仅执行步骤。

v3.3 的 Stage 2 并行化允许 argument_builder_agent 和 visualization_agent 在大纲确认后并行运行，缩短了写作阶段的端到端时间。

---

## 第三组：撰写与引用

### draft_writer_agent

**任务**：基于大纲和论证图生成论文初稿。

v3.6.8 的 Generator-Evaluator 合约将 draft_writer_agent 的 Phase 4 工作拆分为两个子阶段：
- **Phase 4a（论文盲读预承诺）**：Writer 在没有看到完整论文的情况下，承诺将使用哪些评价维度来评估自己的写作质量
- **Phase 4b（论文可见撰写与自评）**：Writer 撰写初稿，然后用 Phase 4a 中承诺的维度进行自评

这个设计防止了 Writer 在写完论文后才"调整"标准来让自己的作品看起来更好。先承诺标准，再写作，最后用同一个标准自评。

### citation_compliance_agent

**任务**：验证论文中的每一条引用是否合规——引用格式是否正确、引用内容是否准确归属于被引论文、是否有遗漏的引用。

v3.6.5 中 citation_compliance_agent 的文献库集成被推迟到了 v3.6.6+——这是 12 个 Agent 中唯一尚未接入 corpus-first 流程的文献消费者。

### abstract_bilingual_agent

**任务**：生成中英双语摘要和关键词。

ARS 的默认行为：无论论文主体是中文还是英文，都自动生成双语摘要。中文摘要注意学术汉语的简洁性，英文摘要遵循对应期刊的风格惯例（APA 要求约 250 词的结构化摘要）。

---

## 第四组：内审与图表

### peer_reviewer_agent

**任务**：在论文进入外部评审（Stage 3）之前，作为"内部审稿人"对初稿进行自评。

v3.6.8 的 Generator-Evaluator 合约同样拆分了这个 Agent 的工作：
- **Phase 6a（论文盲读预承诺）**：Evaluator 在看到论文之前，承诺评分标准和失败条件
- **Phase 6b（论文可见评分与决策）**：Evaluator 阅读论文，基于预承诺的标准打分，并做出 Pass/Revise/Reject 的决定

这构成了 ARS 的**内部 Generator-Evaluator 循环**——在论文进入外部同行评审之前，先由内部的 Writer-Evaluator 对跑一遍完整的两阶段合约协议。

### visualization_agent

**任务**：根据论文数据生成符合 APA 7.0 标准的表格和图表。

v3.3 引入的 VLM 图表验证（来自 PaperOrchestra 的启发）：可选启用视觉模型对生成的图表进行 10 项闭环保真检查——坐标轴标签是否正确、图例是否匹配数据、误差棒是否合理、配色是否在灰度打印下可区分等。最多 2 轮修正。

---

## 第五组：引导与出版

### socratic_mentor_agent

**任务**：在 `plan` 模式下，通过苏格拉底式对话引导用户规划论文章节。

与 deep-research 中的同名 Agent 类似——通过 State-Challenge-Reflect（SCR）协议，在每个章节转换前收集用户的预测，再呈现 AI 的规划建议，制造认知冲突以促进反思。

`plan` 模式使用**意图匹配**启动——检测"用户不确定如何开始"、"用户想要逐步引导"等语义信号，不受语言限制。

### revision_coach_agent

**任务**：在 `revision` 和 `revision-coach` 模式下，解析审稿意见并指导修订。

在**修订教练（Revision Coach）**模式中，不直接修改论文，而是：
1. 解析审稿意见——将每个 comment 归类为"需要修改"、"需要回应但可不修改"、"需要反驳"
2. 生成修订路线图——按优先级排列修改任务
3. 草拟回复信框架——为每条审稿意见准备回复的骨架

### formatter_agent

**任务**：将论文转换为目标出版格式。

支持的输出路径：
- **Markdown**（始终可用）
- **DOCX**（需要 Pandoc；不可用时回退为 Markdown + 转换说明）
- **LaTeX**（APA 7.0 使用 `apa7` document class + XeCJK 中文支持；IEEE / Chicago 等）
- **PDF**（从 LaTeX 通过 tectonic 编译；仅 LaTeX 输出时可用）

格式转换在 Stage 5 FINALIZE 阶段执行，在论文通过 Stage 4.5 最终诚信闸门之后。

---

## Generator-Evaluator 合约：防止自我欺骗

v3.6.8 引入的 Generator-Evaluator Contract 是 Academic Paper `full` 模式中最值得注意的设计创新。它解决了 AI 写作中的一类特定问题：

**问题**：当同一个 AI 既写论文又评论文时，它天然有一种倾向——调整评分标准来让作品看起来更好。这不是恶意欺骗，而是人类和 AI 共有的认知偏误：我们倾向于用更宽松的标准评价自己的产出。

**解决方案**：两阶段预承诺协议。

1. **Writer 的 Phase 4a（盲读预承诺）**：在写出论文之前，Writer 先定义"一篇好论文应该满足什么标准"
2. **Writer 的 Phase 4b（可见撰写）**：Writer 撰写论文，然后用 Phase 4a 中定义的标准自评
3. **Evaluator 的 Phase 6a（盲读预承诺）**：Evaluator 在读论文之前，先承诺评分维度和失败条件
4. **Evaluator 的 Phase 6b（可见评分）**：Evaluator 基于预承诺的标准打分

`<phase4a_output>` 和 `<phase6a_output>` 数据分隔符确保预承诺不能被后续步骤"修改"。这些分隔符在结构上隔离了两个阶段的输出，防止了自我注入（self-injection）——即后期阶段不能看到早期的"已修改版"承诺。

---

下一篇我们将探讨 [Academic Paper 的十种写作模式](10-ten-modes-in-action.md)，从全流程撰写到单一功能的格式转换。

**参考来源**：
- `source/academic-research-skills/academic-paper/SKILL.md`
- `source/academic-research-skills/academic-paper/agents/`（12 个 Agent 文件）
- `source/academic-research-skills/docs/design/2026-04-27-ars-v3.6.6-generator-evaluator-contract-design.md`
- `source/academic-research-skills/shared/style_calibration_protocol.md`
