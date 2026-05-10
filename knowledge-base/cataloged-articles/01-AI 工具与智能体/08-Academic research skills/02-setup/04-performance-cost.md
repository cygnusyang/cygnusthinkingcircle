# Token 预算与成本控制

使用 AI 辅助学术研究，成本是绕不开的话题。ARS 设计者对此有清醒的认识：一套完整 pipeline 运行下来，token 消耗不菲。但相比于聘请专业编辑、购买文献管理软件、或者因为引用错误导致的退稿重投——ARS 的成本是可预测、可控制的。

本文基于 ARS 官方性能文档，拆解各模式的 token 消耗、完整 pipeline 的成本构成，以及如何在不同场景下优化开销。

## 各模式 Token 估算

以下估算基于一篇约 15,000 字、约 60 篇引用的论文。实际消耗随论文长度、修订轮次和对话深度变化。

| 技能 / 模式 | 输入 Token | 输出 Token | 预估费用 (Opus 4.7) |
|------------|-----------|-----------|-------------------|
| `deep-research` socratic | ~30K | ~15K | ~$0.60 |
| `deep-research` full | ~60K | ~30K | ~$1.20 |
| `deep-research` systematic-review | ~100K | ~50K | ~$2.00 |
| `academic-paper` plan | ~40K | ~20K | ~$0.80 |
| `academic-paper` full | ~80K | ~50K | ~$1.80 |
| `academic-paper-reviewer` full | ~50K | ~30K | ~$1.10 |
| `academic-paper-reviewer` quick | ~15K | ~8K | ~$0.30 |
| **完整 pipeline (10 阶段)** | **~200K+** | **~100K+** | **~$4-6** |
| + 跨模型验证 | +~10K (外部) | +~5K (外部) | +~$0.60-1.10 |

*定价基于 2026 年 4 月 Anthropic API 价格。*

## 完整 Pipeline 的成本拆解

一次完整的 ARS pipeline 运行大约花费 $4–6。这笔费用覆盖：

1. **Stage 1 — Deep Research（~$1.20）**：13 个 Agent 的研究团队产出 RQ Brief、方法论蓝图、注释书目、综合报告
2. **Stage 2 — Academic Paper（~$1.80）**：12 个 Agent 的写作团队产出大纲、论证图、初稿、双语摘要
3. **Stage 2.5 — 诚信审查（~$0.30）**：7 类失败模式检查 + 30% 声明抽样验证
4. **Stage 3 — 同行评审（~$1.10）**：5 位审稿人 + 编辑综合报告
5. **Stage 4 — 修订（~$0.50）**：逐点回复评审意见 + 修订稿
6. **Stage 3' — 复审（~$0.30）**：3 人精简复审团队
7. **Stage 4.5 — 最终诚信审查（~$0.30）**：100% 声明验证 + 零容忍重新检查
8. **Stage 5 — 定稿（~$0.20）**：格式转换（LaTeX/DOCX/PDF）
9. **Stage 6 — 过程记录（~$0.30）**：论文创建过程记录 + AI 自我反思报告

## 成本影响因素

### 修订轮次

这是最大的成本变量。每一次 Major Revision → Re-Review → Re-Revise 循环都会增加约 $1.5–2.0 的成本。ARS 硬性限制最多 2 轮修订（Stage 4 + Stage 4'），避免无限循环。

### Sprint Contract 开销（v3.6.2）

对于 `academic-paper-reviewer full` 模式，Schema 13 Sprint Contract 将每位审稿人的运行分成两个阶段（论文盲读预承诺 + 论文可见评审），每位审稿人的 token 消耗增加约 30-40%。5 位审稿人 = 约 $0.30–0.50 的固定增量。

这个成本不能调低——两阶段协议是模式的核心质量保证机制。

### Compliance Agent 开销（v3.4.0）

`compliance_agent` 在 Stage 2.5 和 Stage 4.5 运行，增加：
- `systematic-review` 模式：+$0.15（Stage 2.5）+ $0.15（Stage 4.5）= +$0.30
- 非 SR 入口：只跑 RAISE 四原则，成本较低

### 跨模型验证（可选）

设置 `ARS_CROSS_MODEL=1` 使用第二 AI 模型（GPT-5.4 Pro 或 Gemini 3.1 Pro）进行独立审查，增加约 $0.60–1.10。可以通过 `ARS_CROSS_MODEL_SAMPLE_INTERVAL` 调低采样频率来控制成本。

---

## 成本优化策略

### 1. 分阶段运行，避免一次性全 pipeline

不要一上来就跑完整 10 阶段 pipeline。先单独跑 `deep-research socratic`（~$0.60）来理清研究问题，确认方向后再逐步推进。每个阶段结束后都有 checkpoint 可以暂停，这种设计本身就支持分次运行。

### 2. 选择合适的模式

- 只是想**理清思路**：用 `socratic` / `plan` 模式（$0.60–0.80），而非 `full`（$1.20–1.80）
- 只想**快速评估一篇论文**：用 `academic-paper-reviewer quick`（$0.30），而非 `full`（$1.10）
- 只需要**摘要**：用 `abstract-only` 模式，而非完整写作流程

### 3. 利用 Passport Reset Boundary（v3.6.3+）

对于长 pipeline，设置 `ARS_PASSPORT_RESET=1`，在每次 FULL checkpoint 后启动新 session。这样可以避免：
- 上下文膨胀（前一阶段不需要的上下文占用了后一阶段的 token 预算）
- Prompt cache 过期后的大上下文重新读取

新 session 只加载 Material Passport ledger，不重放之前的对话——节省了大量 token。

### 4. 用 Sonnet 处理低复杂度阶段

- Opus 4.7：复杂架构决策、论文全流程、审稿意见解读
- Sonnet 4.6：格式转换（`format-convert`）、引用检查（`citation-check`）、AI 使用揭露声明生成（`disclosure`）

Plugin 安装模式下的 `/ars-*` slash commands 已自动配置了模型路由——`/ars-full` 和 `/ars-revision-coach` 使用 Opus，其余使用 Sonnet。

---

## Context 窗口管理

ARS 的完整 pipeline 以人类在回路中执行为设计前提，每个阶段都有强制用户确认。实际运行一个完整流程通常跨越数小时到数天——远超 Anthropic 的 prompt cache TTL（5 分钟）。

### 两个实际后果

1. **Checkpoint 之间的 cache miss 是正常的**。当一个阶段 checkpoint 暂停超过 5 分钟，下一阶段将读取未缓存的上下文。这是人节奏 pipeline 不可避免的成本。

2. **跨 session 恢复依赖 Material Passport**。ARS 不在 session 之间维护自己的编排器状态。在新 session 中恢复，需要粘贴 Material Passport YAML；编排器读取 `compliance_history[]` 和阶段完成标记来定位断点。

### 什么应该放在 Context 窗口后 20%

避免在 context 窗口的最后 20% 进行：
- 大规模重构
- 跨越多文件的功能实现

适合放在 context 窗口后段的低敏感度任务：
- 单文件编辑
- 独立工具创建
- 文档更新

---

## 推荐配置

| 设置 | 用途 | 如何启用 |
|------|------|---------|
| **Skip Permissions** | 跳过逐工具确认，启用全自主执行 | `claude --dangerously-skip-permissions` |
| **Agent Team**（可选）| 跨 session 手动编排多 Agent | `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` |

> Skip Permissions 会禁用所有工具使用确认对话框。对可信的长时 pipeline 很方便，但会移除人工审批的安全网。仅在信任 Claude 执行文件读写和 shell 命令的环境中启用。

---

理解了安装配置和成本控制之后，接下来我们进入 ARS 的[架构全景](../03-architecture/05-pipeline-architecture.md)——了解 10 阶段管线如何将 4 个技能编排成一个完整的学术研究流程。

**参考来源**：
- `source/academic-research-skills/docs/PERFORMANCE.md`
- `source/academic-research-skills/docs/PERFORMANCE.zh-TW.md`
