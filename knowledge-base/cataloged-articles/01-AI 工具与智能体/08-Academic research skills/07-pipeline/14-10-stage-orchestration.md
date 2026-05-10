# 10 阶段编排详解

Academic Pipeline 是 ARS 的"总调度"——它将 Deep Research、Academic Paper 和 Academic Paper Reviewer 三个独立 Skill 编排为端到端的学术生产管线。但它不是简单的顺序调用器。Pipeline 在三个阶段之间插入了两次诚信闸门、一次决策分支、两次苏格拉底式指导环节和一个协作评估层。

本文从编排器的视角，详解 10 个阶段的流转逻辑、checkpoint 机制和决策分支。

## 10 阶段全览

```
Stage 1:   RESEARCH         🧑 用户确认 RQ + 方法论
Stage 2:   WRITE            🧑 用户批准大纲
Stage 2.5: INTEGRITY        ✓ 7 类失败模式检查
Stage 3:   REVIEW           🧑 用户做出编辑决定
          ├── Accept ──────────────→ Stage 4.5
          ├── Minor/Major → Coaching → Stage 4
          └── Reject ──────────────→ 结束
Stage 4:   REVISE           🧑 用户确认修订
Stage 3':  RE-REVIEW        🧑 用户确认复审决定
Stage 4':  RE-REVISE        🧑 内容冻结
Stage 4.5: FINAL INTEGRITY  ✓ 零容忍最终验证
Stage 5:   FINALIZE         🧑 用户选择输出格式
Stage 6:   PROCESS SUMMARY  🧑 最终确认
```

🧑 = 决策重点 | ✓ = 诚信闸门

---

## Stage 1：RESEARCH — 从模糊到聚焦

**执行者**：`deep-research`（13 个 Agent）

**输入**：用户的初始研究兴趣或问题

**流程**：
1. RQ 提炼（research_question_agent）——将模糊兴趣转化为结构化 RQ
2. 方法论设计（research_architect_agent）——基于 RQ 推荐具体研究设计
3. 文献检索（bibliography_agent）——检索 + corpus-first 流程（如果有 Material Passport）
4. 引用验证（source_verification_agent）——三层验证（S2 API / DOI / WebSearch）
5. 综合分析（synthesis_agent + 质控组）——跨源整合 + 内部挑战
6. 报告编译（report_compiler_agent）

**Checkpoint**：用户审阅 RQ Brief + Methodology Blueprint，决定是否继续。

这是 pipeline 的第一个也是最关键的决策点——如果 RQ 定义错了，后续所有工作都建立在错误的基础上。

---

## Stage 2：WRITE — 从证据到论文

**执行者**：`academic-paper`（12 个 Agent）

**流程**：
1. Intake（intake_agent）——接收 Stage 1 产出，配置写作参数
2. 文献策略（literature_strategist_agent）——将文献映射到论文章节
3. 大纲生成（structure_architect_agent） → **用户批准大纲**
4. 正文撰写（draft_writer_agent + argument_builder_agent）——v3.6.8 两阶段 Generator 合约
5. 内部评审（peer_reviewer_agent）——v3.6.8 两阶段 Evaluator 合约
6. 引用检查 + 摘要生成 + 图表生成

**Checkpoint**：用户批准大纲后才开始正文撰写——这是 Stage 2 内的子确认点，比 Stage 1 的确认更轻量。

---

## Stage 2.5：INTEGRITY GATE ① — 第一道防线

**执行者**：`academic-pipeline` 闸门功能（integrity_verification_agent）

**内容**：
- 7 类 AI 研究失败模式检查（Mode 1–7）
- 30% 声明抽样验证（最少 10 条）
- Compliance Agent 检查（PRISMA-trAIce + RAISE）
- Material Passport 生成/更新

**阻断条件**：
- 任何模式被标记为 SUSPECTED → 阻断
- Mode 1/3/5/6 INSUFFICIENT EVIDENCE → 阻断（需要用户提供实验日志）
- Mode 2/4/7 INSUFFICIENT EVIDENCE → 可带警告通过（将在 Stage 4.5 重新检查）

**最大重试**：3 次。每次 FAIL 后回到 Stage 2 修正。

这是 pipeline 中不能被绕过的第一个闸门。详见[第十五篇：诚信闸门](15-integrity-gates.md)。

---

## Stage 3：REVIEW — 多视角同行评议

**执行者**：`academic-paper-reviewer`（7 个 Agent）

**流程**（v3.6.2 Sprint Contract 协议）：
1. field_analyst_agent 侦测领域，配置 R1/R2/R3
2. R1/R2/R3 各自独立运行两阶段合约（Phase 1 盲读预承诺 → Phase 2 可见评审）
3. devils_advocate_reviewer_agent 系统性攻击
4. editorial_synthesizer_agent 三步机械综合
5. eic_agent 审阅综合报告，做出编辑决定

**Checkpoint — 编辑决定**：用户收到 Accept / Minor / Major / Reject 决定 + 修订路线图，选择下一步。

这是 pipeline 中最重要的**分支决策点**：
- **Accept**：跳过 Stage 4，直接进入 Stage 4.5
- **Minor Revision / Major Revision**：进入 Revision Coaching → Stage 4
- **Reject**：结束 pipeline

---

## Stage 3→4：Revision Coaching — 苏格拉底式修订指导

**执行者**：eic_agent（扮演教练角色）

**工作方式**：苏格拉底式对话，帮助用户理解审稿意见和制定修订策略。不是"AI 替代你修改论文"，而是"AI 引导你思考如何修改"。

- 最多 8 轮对话
- 用户可以随时说"直接帮我改"跳过对话
- 产出不是文档形式的交付物，而是进入 Stage 4 的策略基础

---

## Stage 4：REVISE — 执行修订

**执行者**：`academic-paper` revision 模式

**流程**：
1. revision_coach_agent 解析审稿意见 → 生成逐点修订计划
2. draft_writer_agent 执行文本修改
3. 生成逐点回复（Response to Reviewers）+ Delta 报告（什么改了 + 为什么改）

**Checkpoint**：用户确认修订内容。

---

## Stage 3'：RE-REVIEW — 验收审查

**执行者**：`academic-paper-reviewer` re-review 模式（精简 3 人团队）

**核心工具**：R&R 追溯矩阵（Schema 11）——独立验证作者的每一条修订声明。

**Checkpoint**：用户确认复审决定。如果仍然是 Major → 进入 Residual Coaching → Stage 4'。

**硬性限制**：最多 1 轮 RE-REVIEW + 1 轮 RE-REVISE。总共 2 轮修订循环（Stage 4 + Stage 4'）。

---

## Stage 4'：RE-REVISE — 终版修订

修正 Stage 3' 的残余问题后，**内容冻结**——不再允许新的审稿循环。论文内容到此锁定，后续只有格式转换和诚信检查。

---

## Stage 4.5：FINAL INTEGRITY GATE ② — 最后防线

**内容**：
- 以**零容忍标准**重新运行全部 7 类失败模式
- **100% 声明验证**（而非 Stage 2.5 的 30% 抽样）
- 任何在 Stage 2.5 被标记为 SUSPECTED 的模式必须在 4.5 被 CLEAR 或用户 Override
- 同一模式在 4.5 仍为 SUSPECTED → pipeline 拒绝进入 Finalize

**无重试**。Stage 4.5 是最后检查点——FAIL 意味着论文有 unresolved 的系统性问题，不能进入出版流程。

---

## Stage 5：FINALIZE — 格式转换

**执行者**：`academic-paper` format-convert 模式

**Checkpoint**：用户选择输出格式（MD / DOCX / LaTeX / PDF）。

**输出路径**：
- Markdown（始终可用）
- DOCX（需要 Pandoc）
- LaTeX → PDF（需要 tectonic + 思源宋體 VF）

---

## Stage 6：PROCESS SUMMARY — 过程记录

**产出**：
1. **论文创建过程记录**（Paper Creation Process Record）：MD + PDF，双语
2. **AI 自我反思报告**：DA 让步率、对话健康警报、谄媚风险评级（LOW/MEDIUM/HIGH）、失败模式审计日志
3. **协作品质评估章节**（v3.5.0+）：综合各 checkpoint 的协作深度观察员报告
4. **分数轨迹可视化**（v3.3+）：跨修订轮次的逐维度评分变化

**Checkpoint**：用户确认语言和最终输出。

---

## 编排器如何管理状态

### Checkpoint 三类

| 类型 | 触发点 | 作用 | 可否降级 |
|------|--------|------|---------|
| FULL | 阶段间关键转换 | 完整 5 题自检 + 可能的上下文重置 | 否 |
| SLIM | 阶段内子步骤 | 简化确认，但必须用户明确同意 | 否 |
| MANDATORY | Stage 2.5, 4.5 | 不可跳过、不可降级 | 否 |

### 中途强化（v3.1+）

每次阶段转换时，编排器注入对应阶段的 IRON RULE + Anti-Pattern 提醒——防止在长 pipeline 中遗忘关键约束。这被称为**抗 Context Rot 锚定**。

### 协作深度观察员（v3.5.0+）

在每次 FULL/SLIM checkpoint 和 pipeline 完成时，`collaboration_depth_agent` 被触发——但它**永不妨碍流程**。MANDATORY 诚信闸门（2.5 / 4.5）明确跳过观察员，避免稀释合规检查。

---

下一篇我们将深入 [Stage 2.5 和 Stage 4.5 的诚信闸门](15-integrity-gates.md)——理解 ARS 如何在两次关键节点上确保学术诚信。

**参考来源**：
- `source/academic-research-skills/docs/ARCHITECTURE.md`
- `source/academic-research-skills/academic-pipeline/SKILL.md`
- `source/academic-research-skills/academic-pipeline/references/pipeline_state_machine.md`
- `source/academic-research-skills/shared/collaboration_depth_rubric.md`
