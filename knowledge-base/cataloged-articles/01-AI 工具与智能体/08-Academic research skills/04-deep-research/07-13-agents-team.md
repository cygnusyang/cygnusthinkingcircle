# 13 个 Agent 的研究团队

Deep Research 是 ARS 的上游引擎——它将模糊的研究兴趣转化为可操作的 Research Question、可验证的证据体系和结构化的研究报告。这一过程不是由一个"全知全能"的 AI 完成的，而是由 13 个角色分工明确的 Agent 协作完成。

本文将 13 个 Agent 按职责分组，逐一剖析它们的工作方式。

## Agent 全景

Deep Research 的 13 个 Agent 可以按职责分为五组：

| 组 | Agent | 职责 |
|----|-------|------|
| **启动组** | research_question_agent | 从兴趣提炼研究问题 |
| | research_architect_agent | 设计方法论蓝图 |
| **文献组** | bibliography_agent | 文献检索与注释书目 |
| | source_verification_agent | 引用真实性验证 |
| **分析组** | synthesis_agent | 跨源整合与矛盾分析 |
| | meta_analysis_agent | Meta 分析 |
| **质控组** | editor_in_chief_agent | 内部主编质量控制 |
| | devils_advocate_agent | 论点挑战与反谄媚 |
| | risk_of_bias_agent | 偏倚风险评估 |
| | ethics_review_agent | 伦理与 IRB 审查 |
| **引导编译组** | socratic_mentor_agent | 苏格拉底式引导 |
| | report_compiler_agent | 最终报告编译 |
| | monitoring_agent | 流程监控与对话健康度 |

---

## 第一组：启动——从问题到方法论

### research_question_agent

**任务**：将用户模糊的研究兴趣转化为结构化的 Research Question。

用户说"我想研究 AI 对高等教育的影响"，Agent 会追问并精细化：
1. 影响什么？——教学质量？学生评估？行政效率？教师角色？
2. 什么类型的 AI？——生成式 AI？自适应学习系统？自动化评估工具？
3. 什么层面？——本科生教育？研究生培养？职业培训？
4. 什么方法？——定量（调查/实验）？定性（访谈/案例分析）？混合方法？

输出为一个包含主 RQ、子问题和概念定义的 **Research Question Brief**。

这是一个关键节点——RQ 的定义质量决定了整个后续研究的有效性。如果问题定义错了，即使后续每个环节都完美执行，最终论文也是在回答错误的问题。这就是为什么 ARS 在此设置了第一个用户确认 checkpoint。

### research_architect_agent

**任务**：基于 RQ Brief 设计方法论蓝图。

这个 Agent 的工作不是泛泛地建议"用定量方法"或"用定性方法"，而是：
- 推荐具体的研究设计（实验、准实验、横断面调查、纵向追踪、案例研究、扎根理论……）
- 指定数据来源策略（一手数据 vs. 二手数据、开放数据集 vs. 自采集）
- 评估每种设计的内部效度、外部效度和可行性的权衡
- 给出方法论选择的文献依据——"根据 XXX（2023）对类似 RQ 的研究，Y 方法在 Z 场景下具有显著优势"

输出为 **Methodology Blueprint**，与 RQ Brief 一起提交用户确认。

---

## 第二组：文献——从搜索到验证

### bibliography_agent

**任务**：文献检索与注释书目构建。

v3.6.5+ 的关键升级：bibliography_agent 现在支持 **文献库优先（corpus-first）** 流程。如果 Material Passport 携带了 `literature_corpus[]`（用户通过 Zotero/Obsidian/PDF 文件夹等渠道导入的个人文献库），它会：

1. 先对个人文献库做预筛选（Step 1）
2. 识别覆盖空白后用外部数据库搜索填补（Step 2）
3. 合并内外部文献为最终的纳入集合（Step 3）
4. 输出带 PRE-SCREENED 区块的 Search Strategy 报告（Step 4）

整个过程遵循四条铁律（Iron Rules）：内外部文献使用相同的纳入/排除标准、任何被跳过的文献必须记录原因、Consumer Agent 不得修改文献库内容、解析失败时优雅降级。

### source_verification_agent

**任务**：三层引用真实性验证。

v3.3 引入的 Semantic Scholar API（来自 PaperOrchestra 的启发）提供了程序化的引用验证：

- **Tier 0**：Semantic Scholar API 批量查询——标题 Levenshtein 匹配 ≥ 0.70、DOI 一致性检查、S2 ID 去重。API 不可用时优雅降级
- **Tier 1**：DOI 一致性检查——DOI 指向的论文元数据是否与引用中的信息一致
- **Tier 2**：WebSearch 手动验证——前两层无法确定时的人工级搜索

三层设计遵循"越是廉价快速的方法越优先"的原则。Tier 0 的 API 调用几乎零成本且批量高效；Tier 2 的 WebSearch 昂贵但能捕获前两层漏掉的边缘情况。

---

## 第三组：分析——跨源整合

### synthesis_agent

**任务**：跨源整合与矛盾分析。

文献分析的核心挑战不是"找到足够多的论文"，而是"理解论文之间的共识与矛盾"。synthesis_agent 的工作是：
- 识别不同研究的共同发现（convergence）
- 标记相互矛盾的发现（contradiction），并按证据层级评估哪一方的证据更强
- 定位文献中的空白（gap）——被普遍假设但从未直接验证的命题
- 生成跨源叙事（cross-source narrative），而非简单的逐篇摘要

v3.6.7 的 Pattern Protection 为 synthesis_agent 添加了 5 条反漂移条款（A1–A5），针对叙事性 Agent 常见的幻视模式：如将"相关性"叙述为"因果性"、在引用中补全论文未包含的发现、以及用 LLM 训练数据中的知识填补文献空白。

### meta_analysis_agent

**任务**：对定量研究进行 Meta 分析。

仅在系统评价模式（`systematic-review`）下激活。处理效应量计算、异质性评估（I² 统计量）、发表偏倚检测（漏斗图/Fail-safe N）等元分析核心步骤。

---

## 第四组：质控——内部挑战

### editor_in_chief_agent

**任务**：作为内部"主编"对所有其他 Agent 的输出进行质量控制。检查逻辑一致性、确保证据层级被正确应用、标记推理跳跃。

### devils_advocate_agent

**任务**：系统性质疑研究的核心论点。v3.0 反谄媚升级后，这个 Agent 的行为受到严格控制：
- **让步门槛**：对每个反驳评分 1–5，≥4 才允许让步
- **禁止连续让步**：上一轮让步后，下一轮必须至少坚持一个反驳
- **让步率追踪**：全程记录让步率，写入 Stage 6 AI 自我反思报告

这个 Agent 是 ARS 反谄媚系统的核心组件之一。详见[第十九篇：反谄媚系统](../08-advanced/19-anti-sycophancy.md)。

### risk_of_bias_agent

**任务**：评估纳入研究的偏倚风险。使用 Cochrane Risk of Bias 工具或 ROBINS-I（非随机干预研究），对选择偏倚、实施偏倚、测量偏倚、失访偏倚和报告偏倚进行结构化评估。

### ethics_review_agent

**任务**：评估研究的伦理合规性。检查是否涉及人类受试者（需要 IRB 批准）、数据隐私保护、知情同意、利益冲突声明等。

---

## 第五组：引导与编译

### socratic_mentor_agent

**任务**：在 `socratic` 和 `plan` 模式下，通过苏格拉底式提问引导用户理清研究思路。

关键创新是 **意图侦测（Intent Detection）**：
- **探索型（Exploratory）**：用户仍在探索可能的 RQ 方向 → 禁用自动收束，最大轮数提升至 60
- **目标型（Goal-Oriented）**：用户有明确方向，需要引导细化 → 启用 SCR 协议（State-Challenge-Reflect）

v3.5.1 新增了**阅读诚实探测**（`ARS_SOCRATIC_READING_PROBE=1`）：在目标型 session 中引用特定论文时，触发一次诚实探测——请用户摘述一段文字。拒绝回答仅记录，不扣分。

详见[第十八篇：苏格拉底导师与 SCR 协议](../08-advanced/18-socratic-mentor-scr.md)。

### report_compiler_agent

**任务**：将所有 Agent 的产出编译为结构化的最终研究报告。处理格式规范化、引用列表组装、章节衔接和 APA 7.0 合规性。

v3.6.7 的 Pattern Protection 为 report_compiler_agent 添加了 3 条反漂移条款（C1–C3），主要针对出版端常见的格式错误和术语不准确。

### monitoring_agent

**任务**：流程监控与对话健康度评估。

每 5 轮静默自检，侦测：
- 持续同意（用户连续 5 轮同意 AI 提议 → 可能谄媚）
- 回避冲突（AI 在应提出异议时保持沉默 → 触发健康警报）
- 过早收束（在探索尚不充分时锁定结论 → 注入挑战性问题）

对话健康度指标写入 Stage 6 的 AI 自我反思报告，但不阻断流程。

---

## Agent 间的协作模式

13 个 Agent 并非顺序执行。实际运行中存在并行化：

1. **RQ 定义**（research_question_agent）和**方法论设计**（research_architect_agent）有依赖关系——后者需要前者的 RQ Brief
2. **文献检索**（bibliography_agent）和**引用验证**（source_verification_agent）可以并行——验证只需要检索结果中的引用列表
3. **综合分析**（synthesis_agent）依赖前两者的完成输出
4. **质控组**（EIC + DA + RoB + Ethics）可以在综合分析的初步产出上并行运行
5. **报告编译**（report_compiler_agent）是最后一步，消费所有上游产出

---

下一篇我们将探讨 [Deep Research 的七种研究模式](08-seven-modes-in-action.md)——如何根据研究需求选择最合适的模式。

**参考来源**：
- `source/academic-research-skills/deep-research/agents/`（13 个 Agent 文件）
- `source/academic-research-skills/deep-research/SKILL.md`
- `source/academic-research-skills/deep-research/references/semantic_scholar_api_protocol.md`
- `source/academic-research-skills/deep-research/references/socratic_questioning_framework.md`
