# 诚信闸门：Stage 2.5 与 Stage 4.5

诚信闸门是 ARS pipeline 中最不可妥协的设计。两个闸门在代码层面被硬编码为不可跳过——与那些"用户可以点继续跳过"的 checkpoint 不同，Stage 2.5 和 Stage 4.5 的检查结果必须被用户逐条审阅并明确确认。

这不是"信任 AI 的判断"，而是"将 AI 的判断结构化呈现给人类"。

本文详解两个闸门的检查内容、运行机制、阻断逻辑和 v3.4.0 Compliance Agent 的整合。

## 两个闸门的分工

| 属性 | Stage 2.5 | Stage 4.5 |
|------|-----------|-----------|
| 时机 | 论文初稿完成后、进入同行评议前 | 所有修订完成后、格式转换前 |
| 目标 | 在进入审稿前发现并解决诚信问题 | 在出版前以零容忍标准做最终验证 |
| 声明验证范围 | 30% 抽样（最少 10 条） | 100% 全部声明 |
| 重试机制 | 最多 3 次 | 无重试——FAIL 阻断 |
| 历史追踪 | 首次检查 | 对比 2.5 的结果，任何 SUSPECTED → 必须 CLEAR 或 Override |

---

## Stage 2.5 的检查内容

### 1. 7 类 AI 研究失败模式检查

Integrity Verification Agent 对论文逐条运行在[第二篇文章](../../01-philosophy/02-ai-research-failure-modes.md)中详细讨论过的 7 类检测问题。每条模式输出三个可能结论：

- **CLEAR**：有证据排除该模式——记录证据
- **SUSPECTED**：至少一个检测问题返回了令人担忧的答案——必须向用户呈现
- **INSUFFICIENT EVIDENCE**：没有足够信息判断

**阻断规则**：
- 任何 SUSPECTED → BLOCK，返回 Stage 2
- Mode 1/3/5/6 INSUFFICIENT EVIDENCE → BLOCK（需要用户提供实验日志等数据）
- Mode 2/4/7 INSUFFICIENT EVIDENCE → WARN，可在 Stage 4.5 重新检查

**用户选项**：
1. **确认问题** → 回到 Stage 2（或更早）修正
2. **Override 并说明理由** → 用户明确说明为什么该标志是误报，理由记录在 process log 中，带入 Stage 6
3. **修改具体段落并重新运行检查**

### 2. 30% 声明抽样验证

从论文中的全部事实性声明中随机抽取 30%（最少 10 条），对每条声明做验证：
- 该声明是否有文献支持？
- 文献是否确实包含该发现？
- 数字/统计是否准确？

抽样而非全量的原因：Stage 2.5 之后还有至少一轮修订，在此之后做全量验证效率低下。如果 30% 抽样中发现问题，说明可能需要全量检查。

### 3. Compliance Agent 检查（v3.4.0+）

v3.4.0 引入的 Compliance Agent 是一个 **mode-aware** 的共享 Agent：

**对于 `systematic-review` 模式**：
- 运行 PRISMA-trAIce 17 项合规检查（包括检索策略记录、研究选择流程、数据提取方法、偏倚风险评估等）
- tier-based block：Mandatory 项 → BLOCK；HR（highly recommended）项 → WARN；R/O（recommended/optional）项 → INFO

**对于非 SR 入口**：
- 只运行 RAISE 四原则检查（Responsibility, Accountability, Integrity, Scholarly Ethics）
- warn-only——不阻断流程，但发现的问题会记录在 Material Passport 的 `compliance_history[]` 中

**三回合 override 阶梯**：如果用户 override 了合规性问题，Compliance Agent 会自动向论文注入 `disclosure_addendum`——一份说明哪些合规项被 override 及理由的补充声明。**无法规避此揭露**。

### 4. Material Passport 生成/更新

Schema 9 Material Passport 在 Stage 2.5 首次生成（或更新），携带：
- 当前阶段的所有产出物哈希
- 7 类失败模式检查的状态
- Compliance Agent 的检查结果（`compliance_history[]`）
- Claim Verification Report

---

## Stage 4.5 的检查内容

### 1. 零容忍重新验证

全部 7 类模式以 **Mode 2 深度检查** 重新运行。附加规则：

- **历史对比**：任何在 Stage 2.5 被标记为 SUSPECTED 的模式，在 4.5 必须被解决（CLEAR 或用户 Override 并有理由）
- **零容忍**：如果同一模式在 4.5 仍为 SUSPECTED，pipeline **永久拒绝**进入 Stage 5 FINALIZE
- **不允许新问题滑过**：即使 2.5 为 CLEAR 的模式，如果在 4.5 被发现新问题，同样触发阻断

### 2. 100% 声明验证

不再抽样，而是对论文中的**每一条**事实性声明做全量验证。这是出版前的最后一道防线——确保论文中没有任何未经验证的事实性主张。

### 3. repro_lock 检查（v3.3.5+）

Material Passport 中的可选 `repro_lock` 子区块被检查：
- 是否存在？（如果用户声明了 → 检查其格式和完整性）
- `stochasticity_declaration` 是否逐字完整？
- 不是运行时阻断条件——事后文档。`repro_lock` 是**设定文件化，而非重播保证**

LLM 的输出不是位元可复现的——`repro_lock` 记录的是"用了什么输入、什么配置"，而非"保证下次能生成一模一样的输出"。

---

## Material Passport 中的诚信历史

两个闸门的检查结果都写入 Material Passport 的 append-only `compliance_history[]`，形成完整的审计轨迹：

```yaml
compliance_history:
  - stage: 2.5
    timestamp: 2026-05-07T14:30:00Z
    failure_modes:
      mode_1: CLEAR
      mode_2: CLEAR
      mode_3: INSUFFICIENT_EVIDENCE  # 用户未提供实验日志
      mode_4: CLEAR
      mode_5: CLEAR
      mode_6: SUSPECTED  # Methods 段落中 3 个数字不在运行日志中
      mode_7: CLEAR
    claim_verification:
      sampled: 15
      verified: 13
      mismatched: 1
      not_found: 1
    compliance_agent:
      prisma_trAIce: N/A (non-SR mode)
      raise_principles: PASS (4/4)

  - stage: 4.5
    timestamp: 2026-05-08T09:15:00Z
    failure_modes:
      mode_1: CLEAR
      mode_2: CLEAR
      mode_3: CLEAR  # 用户提供了实验日志，已排除
      mode_4: CLEAR
      mode_5: CLEAR
      mode_6: CLEAR  # 已修正 Methods 段落
      mode_7: CLEAR
    claim_verification:
      total: 52
      verified: 52
      mismatched: 0
      not_found: 0
```

这个审计轨迹在 Stage 6（过程记录）和出版后稽核中都是关键依据。

---

下一篇我们将探讨 [Material Passport 的完整设计](16-material-passport.md)——ARS 如何在跨 session、跨 checkpoint 的长时间研究中维持状态一致性。

**参考来源**：
- `source/academic-research-skills/academic-pipeline/references/ai_research_failure_modes.md`
- `source/academic-research-skills/shared/agents/compliance_agent.md`
- `source/academic-research-skills/shared/compliance_checkpoint_protocol.md`
- `source/academic-research-skills/academic-pipeline/references/claim_verification_protocol.md`
