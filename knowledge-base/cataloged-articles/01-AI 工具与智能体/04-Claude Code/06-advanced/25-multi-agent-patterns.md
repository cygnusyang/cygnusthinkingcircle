# 第二十五章：多代理模式 —— 并行代理编排与工作流

当单个 AI 代理无法应对复杂任务时，多代理协作就是答案。Claude Code 原生支持并行代理，让多个专业化的 AI 同时工作。

## 为什么需要多代理

单个代理的困境：

- **上下文有限**：一个代理无法同时关注代码质量、安全、性能
- **速度瓶颈**：串行处理多维度审查太慢
- **视角单一**：一个系统提示词无法覆盖所有视角

多代理的优势：

- **并行加速**：多个代理同时工作，速度翻倍
- **专业分工**：每个代理专注于一个维度，质量更高
- **独立评分**：每个代理独立判断，减少偏见
- **灵活组合**：按需组合不同专业代理

## 三种多代理模式

### 模式一：并行审查（最常见）

多个代理同时审查同一段代码，各自关注不同维度。

```mermaid
graph TD
    CMD["/code-review 命令"] --> A1[CLAUDE.md Compliance<br/>代理1]
    CMD --> A2[Bug Detection<br/>代理2]
    CMD --> A3[Historical Context<br/>代理3]
    CMD --> A4[PR History<br/>代理4]
    CMD --> A5[Code Comments<br/>代理5]
    A1 --> AGG[聚合结果<br/>置信度过滤]
    A2 --> AGG
    A3 --> AGG
    A4 --> AGG
    A5 --> AGG
    AGG --> R[最终审查报告]
```

**源码实例：code-review 插件**

5 个 Sonnet 代理并行工作，各自独立审查：

| 代理 | 关注点 | 模型 |
|------|--------|------|
| claude-md-compliance | CLAUDE.md 规则遵守 | Sonnet |
| bug-detector | Bug 和缺陷检测 | Sonnet |
| historical-context | 代码历史上下文 | Sonnet |
| pr-history | PR 审查历史 | Sonnet |
| code-comments | 代码注释质量 | Sonnet |

**关键创新：置信度评分**

每个代理给出 0-1 的置信度分数。低置信度的发现被过滤掉，大幅减少误报。

### 模式二：流水线工作流（Phase-gated）

代理按阶段依次执行，每个阶段有用户确认关卡。

```mermaid
graph TD
    P1[Phase 1: Discovery] --> P2[Phase 2: Exploration<br/>2-3 code-explorer 代理并行]
    P2 --> P3[Phase 3: Clarifying Questions<br/>等待用户回答]
    P3 --> P4[Phase 4: Architecture<br/>2-3 code-architect 代理并行]
    P4 --> P5[Phase 5: Implementation<br/>等待用户批准]
    P5 --> P6[Phase 6: Review<br/>3 code-reviewer 代理并行]
    P6 --> P7[Phase 7: Summary]
    
    P3 -.->|用户确认| P4
    P5 -.->|用户批准| P6
```

**源码实例：feature-dev 插件**

7 阶段工作流，3 个不同代理在不同阶段使用：

| 阶段 | 代理 | 数量 | 目的 |
|------|------|------|------|
| Exploration | code-explorer | 2-3 并行 | 理解代码库 |
| Architecture | code-architect | 2-3 并行 | 设计方案 |
| Review | code-reviewer | 3 并行 | 质量保障 |

**关键设计：用户确认关卡**

- Phase 3 之后：等待用户回答澄清问题
- Phase 5 之前：等待用户批准实现方案
- Phase 6 之后：用户决定是否修复问题

### 模式三：自主迭代（Self-loop）

AI 反复迭代同一任务，直到完成。

```mermaid
graph TD
    START[开始任务] --> WORK[AI 执行工作]
    WORK --> CHECK{Stop 钩子<br/>检查完成度}
    CHECK -->|未完成| WORK
    CHECK -->|完成| DONE[输出结果]
    
    CHECK -.->|拦截退出| LOOP[继续迭代]
    LOOP --> WORK
```

**源码实例：ralph-wiggum 插件**

核心机制：
- `/ralph-loop` 命令启动自主迭代
- Stop 钩子拦截 AI 的退出尝试
- AI 看到自己的前一次工作结果
- `/cancel-ralph` 命令终止循环

## 代理编排最佳实践

### 1. 每个代理单一职责

```markdown
# 好的设计
code-architect: 只做架构设计
bug-detector: 只做 Bug 检测
security-reviewer: 只做安全审查

# 差的设计
super-agent: 同时做架构 + Bug + 安全 + 性能
```

单一职责让系统提示词更聚焦，代理表现更好。

### 2. 并行优于串行

```markdown
# 好：3 个代理并行审查（快）
Phase 6: Launch 3 code-reviewer agents in parallel

# 差：3 个代理串行审查（慢）
Phase 6a: Review for simplicity
Phase 6b: Review for bugs
Phase 6c: Review for conventions
```

### 3. 结果聚合与过滤

多个代理返回结果后，需要聚合：

```markdown
# feature-dev 的聚合模式
1. Consolidate findings from all agents
2. Identify highest severity issues
3. Present to user with recommendations
4. Let user decide what to fix
```

code-review 的聚合模式：
```markdown
1. Each agent scores findings with confidence (0-1)
2. Filter out low-confidence findings
3. Present remaining findings grouped by category
```

### 4. 明确用户决策点

```markdown
# feature-dev 的用户决策点
Phase 3: "Wait for answers before proceeding" 
Phase 5: "DO NOT START WITHOUT USER APPROVAL"
Phase 6: "Present findings and ask what they want to do"
```

### 5. 代理间信息传递

代理不能直接通信，但可以通过：

- **Todo 列表**：`TodoWrite` 跟踪共享进度
- **文件系统**：代理写入文件，其他代理读取
- **编排器读取**：主进程读取代理返回的关键文件列表

```markdown
# feature-dev 的模式
1. Launch agents, ask them to "return list of 5-10 key files"
2. After agents complete, READ those files
3. Build deep context before next phase
```

## 代理模型选择

| 代理类型 | 推荐模型 | 原因 |
|---------|---------|------|
| 架构设计 | Sonnet | 平衡能力和成本 |
| Bug 检测 | Sonnet | 够用，不需要最深度推理 |
| 代码审查 | Sonnet | 需要多个并行，成本敏感 |
| 安全审查 | Opus | 安全问题需要最深度推理 |
| 探索分析 | Sonnet | 快速扫描，不需要深度 |
| 简单验证 | Haiku | 快速、便宜、确定性任务 |

## 复杂度对比

| 插件 | 代理数 | 并行模式 | 阶段数 | 复杂度 |
|------|--------|---------|--------|--------|
| code-review | 5 | 并行审查 | 1 | 中等 |
| pr-review-toolkit | 6 | 并行审查 | 1 | 中等 |
| feature-dev | 3 | 流水线 | 7 | 复杂 |
| ralph-wiggum | 0 | 自主迭代 | 循环 | 复杂 |

## 本章小结

**一句话记住**：多代理就像项目组开会 —— 同一个问题让不同专家并行回答，再由主持人聚合结论。

**决策规则**：
- 需要多维度审查（安全 + 质量 + 规范） → 并行审查模式
- 需要分阶段推进且每阶段要人确认 → 流水线模式（Phase-gated）
- 需要 AI 反复打磨直到满意 → 自主迭代模式（Self-loop）
- 只有一个维度要检查 → 别用多代理，单代理更简单更快

**最容易踩的坑**：给代理塞太多职责（"你同时负责安全、性能和代码风格"），系统提示词臃肿导致每个维度都做不好。记住：一个代理只干一件事。

**现在就试**：在项目中创建一个简单的并行审查命令 —— 用 2 个代理分别检查"CLAUDE.md 规则遵守"和"Bug 检测"，观察它们如何返回不同视角的结果。

👉 接下来我们深入 Hookify 的多条件规则，让钩子更精准

---

**系列目录**：
- [第一章：Claude Code 是什么 —— 终端里的 AI 编码伙伴](./../01-intro/01-what-is-claude-code.md)
- [第二章：安装与上手 —— 从 curl 到第一个命令](./../01-intro/02-installation-setup.md)
- [第三章：权限模型 —— ask/allow/deny 与沙箱](./../01-intro/03-permission-model.md)
- [第四章：斜杠命令 —— 自定义提示词的标准化方法](./../02-core/04-slash-commands.md)
- [第五章：Hooks 系统 —— 事件驱动的自动化引擎](./../02-core/05-hooks-system.md)
- [第六章：两种钩子对比 —— Prompt 钩子 vs Command 钩子](./../02-core/06-prompt-hooks-vs-command-hooks.md)
- [第七章：插件架构 —— 目录结构、自动发现与清单](./../03-plugins/07-plugin-architecture.md)
- [第八章：插件命令开发 —— frontmatter、动态参数、bash 执行](./../03-plugins/08-plugin-commands.md)
- [第九章：插件代理开发 —— 触发机制、系统提示词设计](./../03-plugins/09-plugin-agents.md)
- [第十章：插件技能开发 —— 渐进式披露与 SKILL.md](./../03-plugins/10-plugin-skills.md)
- [第十一章：插件钩子开发 —— hooks.json 与可移植路径](./../03-plugins/11-plugin-hooks.md)
- [第十二章：MCP 集成 —— stdio/SSE/HTTP/WebSocket 四种模式](./../03-plugins/12-mcp-integration.md)
- [第十三章：插件配置 —— .local.md 模式与 YAML frontmatter](./../03-plugins/13-plugin-settings.md)
- [第十六章：commit-commands —— 最简命令插件](./../04-plugin-deep-dives/16-commit-commands.md)
- [第十七章：security-guidance —— 安全钩子实战](./../04-plugin-deep-dives/17-security-guidance.md)
- [第十八章：code-review —— 多代理并行审查](./../04-plugin-deep-dives/18-code-review.md)
- [第十九章：feature-dev —— 7 阶段功能开发工作流](./../04-plugin-deep-dives/19-feature-dev.md)
- [第二十章：hookify —— 零代码创建钩子规则](./../04-plugin-deep-dives/20-hookify.md)
- [第二十一章：plugin-dev —— 用插件开发插件的元工具](./../04-plugin-deep-dives/21-plugin-dev-toolkit.md)
- [第二十二章：设置层级 —— 企业/用户/项目三层配置](./../05-enterprise/22-settings-hierarchy.md)
- [第二十三章：MDM 部署 —— Jamf/Intune/Group Policy 推送](./../05-enterprise/23-mdm-deployment.md)
- [第二十四章：Marketplace —— 插件发布与分发](./../05-enterprise/24-marketplace.md)
- 第二十五章：多代理模式 —— 并行代理编排与工作流 👈 当前位置
- [第二十六章：Hookify 进阶 —— 多条件规则与操作符](./26-hookify-advanced-rules.md) 👉 下一章
- [第二十七章：从零构建完整插件 —— 端到端实战](./27-building-complete-plugin.md)
