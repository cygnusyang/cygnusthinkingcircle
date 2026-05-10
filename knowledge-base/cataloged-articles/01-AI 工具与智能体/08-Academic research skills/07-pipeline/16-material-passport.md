# Material Passport：跨会话的状态护照

学术研究不是一次性的对话。一篇论文从构思到投稿可能跨越数天甚至数周，中间经过多次"暂停—思考—继续"的循环。ARS 的 Material Passport（Schema 9）就是为这种工作模式设计的——它是一份随 pipeline 流转的 YAML 文档，记录所有阶段的产出物哈希、合规历史和 checkpoint 决策，让你可以随时中断和恢复研究。

本文详解 Material Passport 的数据结构、输入端口（literature_corpus[]）、重置边界机制和可复现性文档（repro_lock）。

## Passport 的设计哲学

Material Passport 解决的核心问题是：**跨 session 状态管理**。

Claude Code 的 session 是短暂的。Prompt cache 在 5 分钟后过期。ARS 的完整 pipeline 运行通常跨越数小时到数天。当你关闭 Claude Code、第二天打开继续时，新的 session 无法"记住"昨天的对话。

Material Passport 的答案是：**不依赖对话记忆，依赖结构化状态文档**。每一个 checkpoint 完成后，passport 被更新。当你恢复工作时，编排器读取 passport 的最近状态，定位断点，继续推进。

## 核心数据结构

Schema 9 Material Passport 包含以下关键区块：

```yaml
passport_version: "3.7.0"
paper_slug: "ai-higher-education-quality"
created_at: "2026-05-07T10:00:00Z"
updated_at: "2026-05-08T15:30:00Z"

# 阶段完成标记
stages_completed:
  - stage: 1
    completed_at: "2026-05-07T11:00:00Z"
    artifacts_hash: "sha256:abc123..."
  - stage: 2
    completed_at: "2026-05-07T16:00:00Z"
    artifacts_hash: "sha256:def456..."

# 诚信历史（append-only）
compliance_history:
  - stage: 2.5
    # ... (详见第十五篇)

# 用户决策记录
checkpoint_decisions:
  - stage: 1
    decision: "confirmed"
    notes: "RQ 方向正确，增加了一个关于教师角色的子问题"
  - stage: 3
    decision: "major_revision"

# 可选：用户文献库
literature_corpus:
  - citation_key: "smith2023"
    authors: [...]
    year: 2023
    title: "..."
    source_pointer: "zotero://select/..."

# 可选：重置边界账本（append-only）
reset_boundary:
  - kind: boundary
    hash: "sha256:789abc..."
    stage: 2
    next: 2.5
  - kind: resume
    hash: "sha256:789abc..."
    resumed_at: "2026-05-08T09:00:00Z"
    resumed_in_session: "session-b"

# 可选：可复现性声明
repro_lock:
  inputs_hash: "sha256:..."
  stochasticity_declaration: "LLM outputs are not bit-reproducible..."
```

---

## literature_corpus[]：文献库输入端口

v3.6.4 引入的 `literature_corpus[]` 是 Material Passport 的可选输入端口——允许用户在启动 ARS 之前，将自己的文献库预载入 passport。

### 为什么需要这个

传统的学术 AI 工具从外部数据库（Google Scholar、Semantic Scholar）开始搜索。但对于一个深耕某领域多年的研究者来说，你的 Zotero 库、Obsidian Vault 或 PDF 文件夹中已经有大量经过你筛选的文献。让 ARS 从零开始搜索，意味着浪费了你多年积累的文献筛选工作。

`literature_corpus[]` 让 ARS **从你的文献库开始**，外部搜索只填补覆盖空白。

### 入口格式

每一条文献 entry 遵循 CSL-JSON 最小字段：

```yaml
literature_corpus:
  - citation_key: "wang2026"
    authors:
      - family: "Wang"
        given: "S."
    year: 2026
    title: "Pedagogical partnerships with generative AI..."
    source_pointer: "zotero://select/items/12345"
    # 以下为 PRIVATE 可选字段（不会进入论文）
    abstract: "..."
    user_notes: "这篇的方法论部分对 ARS v3.5 的 observer 设计很有参考价值"
```

`source_pointer` 是一个自由格式的 URI，指向你本地知识库中的原文。`abstract` 和 `user_notes` 是私有的可选字段——带有版权注意（不要在 user_notes 中存储全文摘要，可能侵犯版权）。

### Adapter 体系

ARS 不是直接读取 Zotero 或 Obsidian 的数据库——它通过 **adapter** 做转换。v3.6.4 发布了三个 reference Python adapter：

| Adapter | 输入 | 用法 |
|---------|------|------|
| `folder_scan.py` | 一个 PDF 文件夹 | `python folder_scan.py --input ~/papers/ --output passport.yaml` |
| `zotero.py` | Better BibTeX JSON export | `python zotero.py --input ~/library.json --output passport.yaml` |
| `obsidian.py` | Vault 中的 frontmatter | `python obsidian.py --vault ~/vault/ --tag research --output passport.yaml` |

这三个是**参考起点**——设计预期是用户根据自己使用的文献管理工具编写自定义 adapter。Adapter 的契约（语言中立，任何语言都可以实现）规定在 `academic-pipeline/references/adapters/overview.md` 中。

**Adapter 的错误处理**：
- Entry-level 错误 → fail-soft：单条文献格式错误被跳过，记录到 `rejection_log.yaml`
- Adapter-level 错误 → fail-loud：整个 adapter 失败时抛出明确错误
- `rejection_log.yaml` 永远会被生成——没有 rejection 时是空的

### Consumer 端（v3.6.5+）

Phase 1 的两个文献 Agent 现在会读取 `literature_corpus[]`：

- **bibliography_agent**（deep-research）：在搜索外部数据库前，先预筛选用户文献库
- **literature_strategist_agent**（academic-paper）：在构建文献策略前，先纳入用户文献库

两者的流程相同：Step 0 检测文献库是否非空 → Step 1 预筛选 → Step 2 外部搜索填补空白 → Step 3 合并 → Step 4 生成带 PRE-SCREENED 区块的报告。

四条铁律（Iron Rules）约束所有 consumer：
1. 内外部文献使用**相同的**纳入/排除标准
2. 任何被跳过的用户文献必须**记录原因**
3. Consumer Agent **不得修改**文献库内容（只读）
4. 文献库解析失败时**优雅降级**为纯外部搜索

---

## Reset Boundary：跨会话恢复

v3.6.3 引入的 `reset_boundary[]` 是一个 append-only 账本，记录了 pipeline 的"断点"。

### 工作原理

设置 `ARS_PASSPORT_RESET=1` 后，每个 FULL checkpoint 成为一个上下文重置边界：

1. 在 session A 中完成 Stage 2，checkpoint 通知中包含：`[PASSPORT-RESET: hash=sha256:abc, stage=2, next=2.5]`
2. 关闭 session A，打开新的 session B
3. 在 session B 中输入 `resume_from_passport=sha256:abc`
4. Session B 只加载 passport ledger——不重放 session A 的对话历史
5. 编排器定位到匹配的 `kind: boundary` entry，追加 `kind: resume` entry 消费该边界，继续执行

### 何时用 Reset，何时用延续

**Reset 更好**：
- 长 pipeline（session A 积累了 >100K 输入 token 的不必要上下文）
- `systematic-review` 模式（阶段独立性高）
- 跨天的暂停（prompt cache 已过期，重读整个大上下文没有意义）

**延续更好**：
- 短 pipeline（端到端 < 30K token）
- 有隐式 session 内状态需要保留（如苏格拉底对话的上下文）
- 默认情况下（flag OFF），行为与 v3.6.3 之前完全一致

### 决策传递

如果 checkpoint 时有一个待定的分支决策（如 Stage 3 的 Accept/Minor/Major/Reject），这个决策通过 `pending_decision` 字段传递给恢复后的 session。编排器在恢复后会重新提示用户——不假设用户在新 session 中仍然做相同的决定。

---

## repro_lock：可复现性文档

v3.3.5 引入的 `repro_lock` 是 Material Passport 的可选子区块，用于记录"这篇论文是在什么条件下生成的"。

**它是什么**：一份声明，记录：
- 输入数据/文献的哈希
- 使用的模型和配置
- 随机性声明（"LLM 输出不是位元可复现的"）

**它不是**：一个可重播的执行环境保证。没有容器镜像、没有锁定依赖版本、没有确定性推理模式。`repro_lock` 遵循 ARS 的诚实记录原则——"我们记录了生成这篇论文的条件，但这不意味着完全相同的输入会产生完全相同的输出"。

如果 `repro_lock` 被声明，`stochasticity_declaration` 必须逐字完整：`"LLM outputs are inherently stochastic and not bit-reproducible even under identical inputs. This repro_lock documents the generation conditions for transparency, not replayability."`

---

## Passport 的完整性保证

- **Append-only**：`compliance_history[]` 和 `reset_boundary[]` 只追加、不修改
- **哈希链**：每个 checkpoint 记录产出物哈希，形成可验证的完整性链
- **用户可见**：Passport 以 YAML 格式存储，用户可以直接阅读和编辑（但建议只通过 ARS 管道修改结构性字段）
- **非可执行**：Passport 是**数据**，不是代码。它不包含可执行指令，不能自动触发 pipeline 行为

---

下一篇我们将转向[跨模型验证](../08-advanced/17-cross-model-verification.md)——ARS 如何可选地使用 GPT 或 Gemini 作为第二 AI 模型独立审查 Claude 的输出。

**参考来源**：
- `source/academic-research-skills/shared/handoff_schemas.md`（Schema 9）
- `source/academic-research-skills/academic-pipeline/references/adapters/overview.md`
- `source/academic-research-skills/academic-pipeline/references/literature_corpus_consumers.md`
- `source/academic-research-skills/academic-pipeline/references/passport_as_reset_boundary.md`
- `source/academic-research-skills/shared/artifact_reproducibility_pattern.md`
