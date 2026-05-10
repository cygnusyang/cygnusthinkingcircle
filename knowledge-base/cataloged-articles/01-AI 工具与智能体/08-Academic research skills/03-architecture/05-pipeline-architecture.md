# Pipeline 架构全景

ARS 的核心不是任何一个单独的 Skill，而是 **Academic Pipeline**——一个 10 阶段的全流程编排器，将 Deep Research（深度研究）、Academic Paper（论文撰写）、Academic Paper Reviewer（论文审查）三个独立技能串联成一个端到端的学术生产管线。

本文从宏观到微观，解析 pipeline 的流程、阶段矩阵、数据访问层级和 Skill 依赖关系。

## 10 阶段全流程

```
用户输入
  ↓
Stage 1: RESEARCH      → RQ Brief + 方法论蓝图
  ↓
Stage 2: WRITE         → 大纲 + 初稿
  ↓
Stage 2.5: INTEGRITY   → 7 类失败模式检查（诚信闸门 ①）
  ↓
Stage 3: REVIEW        → 5 位审稿人 + 编辑决定
  ↓
  ├── Accept ──────────────────────→ Stage 4.5
  ├── Minor/Major → Revision Coaching → Stage 4: REVISE
  │                                      ↓
  │                                 Stage 3': RE-REVIEW
  │                                      ↓
  │                                 Stage 4': RE-REVISE（终版）
  │                                      ↓
  └── Reject ──────────────────────→ 结束
  
Stage 4.5: FINAL INTEGRITY → 零容忍重新验证（诚信闸门 ②）
  ↓
Stage 5: FINALIZE       → 格式转换（MD/DOCX/LaTeX/PDF）
  ↓
Stage 6: PROCESS SUMMARY → 过程记录 + AI 自我反思
  ↓
完成
```

### 关键设计特征

**两条回路**：
1. **修订回路**（Stage 3 → 4 → 3' → 4'）：最多 2 轮，硬性限制。Stage 3' 为 Major 时进入 Residual Coaching → Stage 4' 后不再允许进一步修订
2. **诚信失败回路**（Stage 2.5 FAIL → Stage 2）：最多 3 次重试

**不可跳过的闸门**：
- Stage 2.5 和 Stage 4.5 的诚信闸门在代码层面是不可绕过的
- 即使你说"跳过"，系统仍然要求你逐条确认检查结果

---

## 阶段 × 维度矩阵

每个阶段由特定的 Skill 执行，产出明确的交付物，经过特定的质量闸门后进入下一阶段。

| 阶段 | 执行者 | 数据层级 | 核心产出 |
|------|--------|---------|---------|
| 1. RESEARCH | `deep-research` | RAW | RQ Brief, 方法论蓝图, 注释书目, 综合报告 |
| 2. WRITE | `academic-paper` | REDACTED | 大纲, 论证图, 初稿, 双语摘要 |
| 2.5 INTEGRITY | `academic-pipeline` (gate) | VERIFIED_ONLY | 诚信报告 + Material Passport |
| 3. REVIEW | `academic-paper-reviewer` | VERIFIED_ONLY | 5 份审稿报告 + 编辑决定 + 修订路线图 |
| 3→4 COACHING | EIC Socratic | VERIFIED_ONLY | 修订策略对话（可选，最多 8 轮） |
| 4. REVISE | `academic-paper` | REDACTED | 逐点回复 + 修订稿 + Delta 报告 |
| 3'. RE-REVIEW | `academic-paper-reviewer` | VERIFIED_ONLY | 验证检查表 + 残余问题 + R&R 追溯矩阵 |
| 4'. RE-REVISE | `academic-paper` | REDACTED | 最终修订稿（终版，不再进入审稿循环） |
| 4.5 FINAL INTEGRITY | `academic-pipeline` (gate) | VERIFIED_ONLY | 更新后诚信报告（100% 声明验证） |
| 5. FINALIZE | `academic-paper` | VERIFIED_ONLY | 出版就绪稿（MD/DOCX/LaTeX/PDF）|
| 6. PROCESS SUMMARY | `academic-pipeline` | VERIFIED_ONLY | 过程记录 + AI 自我反思报告 |

---

## 两类用户确认点

Pipeline 中有 10 个人类决策点和 2 个诚信确认点：

### 决策重点（🧑）— 用户选择分支或确认实质性决定

| # | 阶段 | 用户决定什么 |
|---|------|------------|
| 🧑 1 | Stage 1 | 确认研究问题和方法论蓝图 |
| 🧑 2 | Stage 2 | 批准大纲后才开始撰写 |
| 🧑 3 | Stage 3 | 编辑决定（Accept/Minor/Major/Reject） |
| 🧑 4 | Stage 3→4 | 修订策略（最多 8 轮苏格拉底对话，可跳过） |
| 🧑 5 | Stage 4 | 确认修订内容 |
| 🧑 6 | Stage 3' | 复审决定 |
| 🧑 7 | Stage 3'→4' | 残余问题权衡（最多 5 轮） |
| 🧑 8 | Stage 4' | 内容冻结——不再进入审稿循环 |
| 🧑 9 | Stage 5 | 输出格式选择 |
| 🧑 10 | Stage 6 | 语言确认 + 协作品质评估确认 |

### 诚信闸门（✓）— 机器验证先运行，用户确认报告

| # | 阶段 | 验证内容 | 用户确认 |
|---|------|---------|---------|
| ✓ 1 | Stage 2.5 | 7 类失败模式检查 | PASS/FAIL + SUSPECTED 标志 |
| ✓ 2 | Stage 4.5 | Mode 2 深度检查，零容忍 | PASS + 完整 Material Passport |

---

## 数据访问层级（v3.3.2+）

ARS 为每个 Skill 标注了 `data_access_level`，形成三层数据隔离：

```
raw → redacted → verified_only
```

```
User Input (raw data)
    ↓
[deep-research]        data_access_level: raw
    ↓ source_verification 升级
[academic-paper]       data_access_level: redacted
    ↓ Gate 2.5: 7-mode integrity
[academic-paper-reviewer]  data_access_level: verified_only
[academic-pipeline]       data_access_level: verified_only
```

**三层含义**：

- **raw**：消费第一层数据——任意来源（可能是对抗性的）。`deep-research` 在此层运行，因为它的工作就是从原始 web/PDF/用户查询中提取和验证信息。
- **redacted**：在被净化的材料上运行，不接收新的原始输入。`academic-paper` 在此层运行——它消费研究阶段已验证的输出，而非重新搜索。
- **verified_only**：仅在上游诚信闸门通过后运行。`academic-paper-reviewer` 和 `academic-pipeline` 的闸门功能在此层运行——它们审查的是经过验证的论文，而非任意文本。

`data_access_level` 是**声明式标注**而非运行时强制执行——它由 CI lint 检查，不检查运行时的 context 窗口。真正的执行点在 Stage 2.5 和 Stage 4.5 的用户审查闸门。

---

## Skill 依赖关系

ARS 的 4 个 Skill 之间存在清晰的依赖图：

```
deep-research ──→ academic-paper ──→ academic-paper-reviewer
     ↑                  ↑                      ↑
     └──────────────────┴──────────────────────┘
                 academic-pipeline (orchestrates all)
```

- `deep-research` 产出研究简报和注释书目，`academic-paper` 消费这些材料进行论文撰写
- `academic-paper` 产出完整论文，`academic-paper-reviewer` 对论文进行多视角审稿
- `academic-pipeline` 作为编排器，调用上述三个 Skill 并按阶段注入诚信检查、Socratic 指导和协作品质评估

---

## 自适应性 Checkpoint（v3.1+）

Pipeline 根据上下文复杂度自动调整 checkpoint 的深度：

- **FULL checkpoint**：阶段间关键转换点（Stage 1→2、Stage 2→2.5、Stage 3→4）。完整的 5 题自检（引用完整性、谄媚让步、品质轨迹、范围纪律、完整性）+ 可能的上下文重置边界
- **SLIM checkpoint**：阶段内子步骤。简化确认，但仍需用户明确同意才能推进
- **MANDATORY checkpoint**：Stage 2.5 和 4.5。不可跳过、不可降级

---

## 中途进入机制

Pipeline 不强制从 Stage 1 开始。用户可以直接从中间阶段进入：

```
"我想做一篇完整的研究论文"    → 从 Stage 1 开始
"我已经有论文，帮我审查"      → 从 Stage 2.5 进入（先做诚信审查）
"我收到审稿意见了"           → 从 Stage 4 进入
```

中途进入依赖 **Material Passport**——一份随 pipeline 流转的 Schema 9 文档，记录所有阶段的产出物哈希、合规历史和 checkpoint 决策。

---

下一篇将逐一介绍 [四大技能的核心能力与适用场景](06-four-skills-overview.md)。

**参考来源**：
- `source/academic-research-skills/docs/ARCHITECTURE.md`
- `source/academic-research-skills/shared/ground_truth_isolation_pattern.md`
- `source/academic-research-skills/academic-pipeline/references/passport_as_reset_boundary.md`
