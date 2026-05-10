# 六种审查模式与 Sprint Contract

Academic Paper Reviewer 提供 6 种审稿模式，从完整的多视角评审到针对性的方法论检查。其中 `full` 和 `methodology-focus` 模式在 v3.6.2 中引入了 **Sprint Contract（冲刺合约）** ——一种"先承诺标准，再评估论文"的两阶段预承诺机制，从根本上防止了审稿人"看了论文后再调整标准"的认知偏误。

## 模式一览

| 模式 | 光谱 | 审稿团队 | 监管 | 核心场景 |
|------|------|---------|------|---------|
| `full` | Balanced | EIC + R1 + R2 + R3 + DA (5人) | High | 完整同行评审 |
| `methodology-focus` | Fidelity | EIC + methodology (2人) | Medium | 专注方法论审查 |
| `re-review` | Fidelity | EIC + synthesizer (3人精简) | Medium | 验收修订 |
| `quick` | Fidelity | EIC only | Low | 快速评估 |
| `guided` | Originality | EIC dialogue | Very High | 引导式改进 |
| `calibration` | Fidelity | Full panel + gold set | Medium | 评审系统校准 |

---

## Full Mode：完整多视角同行评议

**触发**："review this paper" / "peer review" / "manuscript review"

**工作方式**：完整的 7 Agent 流程（field_analyst → R1/R2/R3 并行 → DA → synthesizer → EIC）。

**v3.6.2 Sprint Contract 协议**（详见下文）在此模式下**强制执行**——不可跳过、不可降级。

**输出**：5 份审稿报告（EIC 综合 + R1 + R2 + R3 + DA）+ 编辑决定 + 修订路线图。

**成本**：~$1.10（因 Sprint Contract 两阶段协议约增加 30-40%）。

---

## Methodology-Focus Mode：方法论深度审查

**触发**："check methodology" / "focus on methods"

**工作方式**：简化的 2 人审稿团队（EIC + methodology reviewer），专注评估研究设计的严谨性。

**适用场景**：
- 你是研究方法课的学生/教师，需要方法层面的反馈
- 论文的核心贡献在方法创新上，内容部分还在完善
- 你只需要确认"方法论上有没有硬伤"而不需要完整的同行评议

**v3.6.2 Sprint Contract** 在此模式下同样强制执行——panel 规模为 2。

---

## Re-Review Mode：验收审查

**触发**："check revisions" / "verification review"

**工作方式**：3 人精简复审团队（field_analyst + EIC + synthesizer），不做完整的新一轮审稿，而是检查：
1. 作者是否逐条回应了上一轮审稿意见
2. 修订是否真正解决了问题（而非表面修改）
3. 是否有新的问题被引入

**核心工具：R&R 追溯矩阵（Schema 11）**

| 审稿意见 | 作者声称的修改 | 验证状态 | 备注 |
|---------|-------------|---------|------|
| R1-3：样本量不足 | "增加至 n=200" | ✅ Verified | 新样本量符合 power analysis |
| DA-2：未控制混淆变量 X | "X 已纳入回归模型" | ❌ Not Verified | 回归表中 X 的系数为 NA |

追溯矩阵将"作者声称做了什么"和"独立验证发现了什么"放在同一行中，让声称与实际的差距一目了然。

**硬性限制**：Re-Review 只能发生一次。如果仍然有 Major issue，进入 Residual Coaching → Final Re-Revise 后不再允许审稿循环。

---

## Quick Mode：快速评估

**触发**："quick review" / "quick look"

**工作方式**：仅 EIC Agent 做快速评估。

**输出**：精简的关键问题列表 + 大致评分区间（不保证精确）。

**适合**：快速判断"这篇论文值不值得认真审"或"投稿前快速扫一眼有没有明显问题"。

**成本**：~$0.30。

---

## Guided Mode：引导式改进

**触发**："guide me to improve" / "walk me through issues"

**工作方式**：EIC Agent 以苏格拉底式对话，逐个问题引导你思考如何改进论文。

**与 Full Mode 的区别**：
- Full：AI 审稿 → 给你一份审稿报告 → 你拿着报告自己去改
- Guided：AI 带领你逐条思考——"你觉得审稿人为什么会提这个问题？你认为最好的处理方式是什么？"——在对话中完成改进策略的思考

**适合**：想**从审稿中学习**如何在未来避免类似问题的研究者。

---

## Calibration Mode：评审系统校准

**触发**："calibrate reviewer" / "measure reviewer accuracy"

**工作方式**：用户提供一组"gold set"——你已经知道真实质量评级的论文（如已知被接收/退稿的论文，或你自己对质量有明确判断的论文）。Reviewer 对这组论文进行盲评，然后测量：

- **False Negative Rate (FNR)**：好论文被错误标记为差的概率
- **False Positive Rate (FPR)**：差论文被错误标记为好的概率
- **Balanced Accuracy**：(敏感度 + 特异度) / 2

**输出**：Calibration Report，包含 FNR/FPR/balanced accuracy + 信心揭露声明。

**设计哲学**：v3.4.0 的设计决策——校准结果**以透明公布取代硬门槛**。不设"FNR 必须低于 X 才能使用 reviewer"的规则，而是要求校准结果被诚实地报告和理解。这与 ARS 的 `task_type: open-ended` 设计一致——文字品质评审不是二分类问题，不能用简单的阈值来校准。

**约束**：
- 5 次集成（对每篇论文跑 5 次取中位数）
- 跨模型验证默认开启（如果 `ARS_CROSS_MODEL` 已设置）
- 信心揭露强制附加——"本次校准使用了 N 篇 gold set 论文，在 A 类论文上的性能尤其不确定"

---

## Sprint Contract：先承诺，后评估

v3.6.2 引入的 Sprint Contract（Schema 13）是 Reviewer 系统最重要的架构升级。它解决了一个根本问题：

### 问题：后见之明偏误

传统的 AI 审稿流程中，"评估标准"和"论文阅读"是混在一起的。这导致了两种偏误：
1. **标准向论文倾斜**：读了一篇统计上严谨的论文，审稿人不知不觉降低了"方法论标准"的权重
2. **论文向标准倾斜**：看到"统计显著"就自动加分的倾向，忽略了效应量的大小

### 解决方案：两阶段预承诺

Sprint Contract 将每位审稿人的运行拆分为两个阶段：

**Phase 1（论文内容盲读）**：
- 审稿人看到：论文的标题、摘要、关键词、投稿的期刊类型
- 审稿人**看不到**：论文正文
- 审稿人必须在这个阶段提交**评分计划的预承诺**（scoring plan）：
  - `acceptance_dimensions`：将使用哪些维度来评估论文质量
  - `failure_conditions`：哪些情况视为不可接受的缺陷（含严重性和跨审稿量化词）
  - `measurement_procedure`：每个维度的具体测量方式

**Phase 2（论文可见评审）**：
- 审稿人看到完整论文
- 基于 Phase 1 中承诺的标准进行实际评审
- Phase 1 的输出被包裹在 `<phase1_output>...</phase1_output>` 数据分隔符中——分隔符在结构上阻止了 Phase 2 的评审去"修改" Phase 1 的承诺

### Contract 模板

ARS 随 v3.6.2 发布了两份 contract 模板：

**`reviewer/full.json`**（panel 5）：
- 7 个评估维度（D1–D7）：研究设计、方法严谨性、文献定位、论证质量、贡献新颖性、可复现性、写作质量
- 8 个失败条件（F1–F8）：每个条件附带 `severity` 优先级 + `cross_reviewer_quantifier`（如 "at least 2 reviewers"）

**`reviewer/methodology_focus.json`**（panel 2）：
- 5 个评估维度（D1–D5）：全部聚焦于方法论层面
- 6 个失败条件（F1–F6）

### Synthesizer 的三步机械协议

有了预承诺的评分标准后，synthesizer 的工作变成了一个**机械可执行**的协议（而非需要"判断力"的开放任务）：

1. **构建跨审稿矩阵**：行 = `failure_conditions`，列 = 审稿人（R1/R2/R3/DA），单元格 = 该审稿人对该条件的评估
2. **用 contract 中的量化词评估**：如果某个 `failure_condition` 的 `cross_reviewer_quantifier` 是 "at least 2 reviewers"，且矩阵中该行有 ≥2 个审稿人标记了此条件 → 触发
3. **按 `severity` 优先级解决**：CRITICAL → HIGH → MEDIUM → LOW，同级内按触发频率排序

这个协议是**确定性的**——给定相同的 contract 和相同的审稿报告，synthesizer 必须产出相同的结果。

---

## 模式选择速查

| 你想 | 选 |
|------|-----|
| 完整同行评审（投稿前自查） | `full` |
| 只关心方法论有没有硬伤 | `methodology-focus` |
| 论文修改完了，验收 | `re-review` |
| 快速扫一眼有没有重大问题 | `quick` |
| 从审稿中学习如何改进 | `guided` |
| 校准 AI 审稿在你领域的准确度 | `calibration` |

---

下一篇我们将进入 [Academic Pipeline 的 10 阶段编排](../07-pipeline/14-10-stage-orchestration.md)——理解整个调度器如何协调 3 个 Skill、2 次诚信闸门和 10 个人类决策点。

**参考来源**：
- `source/academic-research-skills/MODE_REGISTRY.md`
- `source/academic-research-skills/academic-paper-reviewer/references/sprint_contract_protocol.md`
- `source/academic-research-skills/docs/design/2026-04-23-ars-v3.6.2-sprint-contract-design.md`
- `source/academic-research-skills/shared/sprint_contract.schema.json`
