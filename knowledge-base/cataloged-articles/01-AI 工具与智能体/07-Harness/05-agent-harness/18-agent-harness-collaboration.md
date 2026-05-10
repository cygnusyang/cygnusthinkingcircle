# 第十八章：Claude Code、Codex、OpenClaw中的Agent-Harness协作模式

前面我们分别讲了 Harness 的各子系统。这一章把它们串起来——看看三个主要产品中 Agent 和 Harness 是如何协作的。

## 协作的本质

Agent 和 Harness 的协作可以用一个简单公式表达：

```
Agent 的职责: 决定做什么 (What) + 为什么 (Why)
Harness 的职责: 执行怎么做 (How) + 约束不能做什么 (Won't)
```

三个产品都在这个框架下运行，但实现不同。

## Claude Code：最流畅的人机协作

### 协作模式：REPL + 实时可见

```
用户: 给这个 React 组件加个删除按钮

Claude Code Agent:
  Thought: "我需要先看组件代码"
  → [Harness 执行 Read → 返回组件代码]

  Thought: "这是一个用户列表组件，我需要在每一行加删除按钮。
           还要加确认对话框。"
  → [Harness 执行 Edit → 修改 TSX 文件]
  → [用户可以看到修改内容，实时反馈]

  Thought: "需要更新测试"
  → [Harness 执行 Read → 读取测试文件]
  → [Harness 执行 Edit → 添加删除测试]
  → [Harness 执行 Bash → npm test]

  结果: 测试通过
  → 交付
```

关键特征：
- **REPL 交互**：对话式，每一步用户都能看到 Agent 在做什么
- **流式输出**：实时看到 Agent 的思考过程和工具调用
- **即时干预**：用户可以在任何时刻 Ctrl+C 中断，给出新指令

### 权限协作

```
Agent: 我需要执行 npm install
Harness: [权限检查] 匹配 "ask" 规则 → 弹窗询问用户
User: [点击 Allow]
Harness: 执行 npm install → 返回结果给 Agent
```

或者是：

```
Agent: 我需要读取 .env 文件
Harness: [权限检查] 匹配 "deny" 规则 → BLOCK
Agent: [收到拒绝信息] "无法读取 .env。我将基于环境变量文档配置。"
```

Agent 和 Harness 在权限上的协作：Agent 提出请求，Harness 执行检查，Agent 根据结果调整。

## Codex：最安全的协作

### 协作模式：TUI + 沙箱

```
用户: 重构这个 Python 项目的数据库层

Codex Agent:
  Thought: "我需要了解当前数据库结构"
  → [Harness 执行 Read(沙箱内) → 返回代码]

  Thought: "当前使用原始 SQL，重构为 SQLAlchemy ORM"
  → [Harness 生成计划 → TodoWrite 显示在 TUI 面板]

  Thought: "开始实施..."
  → [Harness: 每次 Write 都在沙箱内完成]
  → [Harness: 每次 Bash 都在 OS 级沙箱内执行]
```

关键特征：
- **TUI 面板**：分区域显示计划、对话、文件变更
- **OS 沙箱**：所有执行在隔离环境中，即使 Agent 犯错也不会影响系统
- **Rust 类型安全**：Harness 本身用 Rust 编写，内存安全在编译时保证

### 沙箱协作

Codex 的沙箱是 Agent-Harness 协作的一种特殊模式：

```
Agent: "运行 pip install -r requirements.txt"
Harness: [在 macOS Seatbelt 沙箱内执行]
  允许: 网络访问 (下载包)
  允许: 文件写入 (/project/.venv/)
  拒绝: 文件写入 (/etc/, /usr/, ...)
  拒绝: 文件读取 (/Users/user/.ssh/)
```

Agent 不知道自己在一个沙箱里——它正常请求执行，Harness 透明地隔离。如果沙箱拒绝某个操作，Agent 会收到错误并调整。

## OpenClaw：最多渠道的协作

### 协作模式：Gateway + 消息驱动

```
User (WhatsApp): "帮我查下明天天气"

OpenClaw Gateway: 
  → 接收 WhatsApp 消息
  → 路由到用户会话
  → Agent 处理
  → 返回 WhatsApp

Harness 的职责:
  - 消息路由 (WhatsApp → Agent → WhatsApp)
  - 会话管理 (每个用户的对话历史独立)
  - 多模型故障转移 (Claude 挂了切 GPT)
  - 身份验证 (WhatsApp 号是否在白名单)
```

### 多 Agent 协作

```
用户: "帮我做竞品分析报告"

主 Agent:
  Thought: "这个任务需要三个子任务"
  → sessions_spawn("research-agent", "搜索竞品信息")
  → sessions_spawn("analysis-agent", "分析优劣势")
  → sessions_spawn("writer-agent", "撰写报告")

Harness 的职责:
  - 为每个子 Agent 创建独立会话
  - 隔离上下文
  - 收集结果回传给主 Agent
  - 主 Agent 整合后交付用户
```

## 三种协作模式对比

| 维度 | Claude Code | Codex | OpenClaw |
|------|------------|-------|----------|
| **Agent 看到什么** | REPL 对话流 | TUI 多面板 | 消息时间线 |
| **Harness 如何介入** | 每轮 auto-inject | OS 沙箱 + TUI | Gateway 路由 |
| **用户如何协作** | 对话中随时打断 | TUI 面板中操作 | 消息回复 |
| **安全机制** | 权限管道 | OS 级沙箱 | 身份白名单 |
| **多 Agent** | 子代理 (内部) | 子代理 (内部) | sessions_spawn (跨渠道) |

## 核心洞察

1. **Agent 的体验由 Harness 定义**：同一个模型，在 Claude Code 里是 REPL 风格，在 Codex 里是面板风格，在 OpenClaw 里是消息风格。Agent 的"人格"来自 Harness。

2. **安全策略决定使用场景**：Codex 的沙箱让它适合企业环境，Claude Code 的权限管道让它更适合个人开发者，OpenClaw 的身份白名单让它适合个人 AI 助手。

3. **Harness 设计 = 产品设计**：以前我们以为产品体验来自 UI，但在 Agent 时代，产品体验来自**Harness 如何让 Agent 和用户协作**。

4. **没有完美的 Harness**：三种模式各有取舍。选择 Harness 就是选择**你最看重的 trade-off 是什么**。

## 本章小结

- Claude Code = 最流畅的人机协作（REPL + 实时 + 随时干预）
- Codex = 最安全（OS 沙箱 + Rust 类型安全 + 模块化）
- OpenClaw = 最多渠道（Gateway + 消息路由 + 多模型）
- Agent-Harness 协作的本质：Agent 决定 What/Why，Harness 执行 How/Won't
- 产品体验 = Harness 设计——不是 UI，是协作模式
- 下一章：多智能体架构模式

---

**系列目录**：
- [第十七章：Harness是Agent的操作系统](./17-harness-as-os.md)
- 第十八章：Agent-Harness协作模式 👈 当前位置
- [第十九章：多智能体架构模式](../06-multi-agent/19-multi-agent-architectures.md) 👉 下一章
