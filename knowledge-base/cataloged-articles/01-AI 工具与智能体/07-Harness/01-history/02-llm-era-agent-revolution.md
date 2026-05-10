# 第二章：LLM时代的Agent革命 —— 2023-2026爆发期

第一章我们走完了 Agent 概念 70 年的演进。这一章聚焦最近 3 年——Agent 从学术玩具变成生产力工具的过程。

## 2023：Agent 元年

### 催化剂：ChatGPT (2022.11)

2022 年 11 月 30 日，OpenAI 发布了 ChatGPT。两个月内用户突破 1 亿——史上最快。但 ChatGPT 本身不是 Agent：它没有工具、没有自主循环、不能操作外部世界。

它真正的历史作用是：让全世界**看见了可能性**。

### ReAct 论文：给 Agent 装上"手"

2023 年 2 月，Google 和普林斯顿的《ReAct: Synergizing Reasoning and Acting in Language Models》论文提出了一个关键范式：

```
Thought → Action → Observation → Thought → Action → Observation → ...
```

模型交替进行**推理**（"我应该先检查哪个文件"）和**行动**（调用 grep 搜索），并根据观察结果调整下一步计划。

这就是 Agent Loop 的雏形——今天 Claude Code、Codex 的循环都源自这里。

### AutoGPT & BabyAGI：自主 Agent 的实验

2023 年 3-4 月，两个项目引爆了 GitHub：

- **AutoGPT (2023.3.30)**：给它一个目标（"研究 AI 最新进展并写成报告"），它自主搜索 web、读写文件、迭代推进。Star 数一周破 10 万。
- **BabyAGI (2023.4.3)**：只有 ~100 行 Python，却是第一个完整实现"任务创建 → 优先级排序 → 执行 → 循环"的系统。

它们的共同问题：**不可靠**。AutoGPT 经常陷入搜索循环，BabyAGI 的任务队列会无限膨胀。

但方向是对的——它们暴露了 LLM Agent 真正需要什么：**一个稳定的基础设施来管理规划、执行、工具和上下文**。

这就是 Harness 的前身。

### Function Calling：模型开始"用工具"

2023 年 6 月，OpenAI 发布 Function Calling——模型可以输出结构化的函数调用请求，而不仅仅是文本。同期 Anthropic 也在 Claude API 中实现了 Tool Use。

```json
{
  "tool": "read_file",
  "parameters": {
    "path": "/src/auth/login.ts"
  }
}
```

这是革命性的：模型不再只是"生成文本"，而是能明确地**请求执行某个操作**。这让 Agent 从概念变成工程现实。

### 2023 年下半年：框架爆发

- **LangChain** 推出 Agent 模块：Tool、AgentExecutor、Memory 成为标准抽象
- **LlamaIndex** 推出 Agent 模块：数据 Agent 的范式
- **Semantic Kernel**：微软的企业 Agent 框架
- **CrewAI**：第一个多智能体协作框架

但这些框架有个共同问题：**用代码编排 Agent 的决策**——代码决定什么时候调什么工具。这违背了 Agent 的核心理念：**让模型做决策**。

## 2024：从框架到产品

### 2024.3：Claude 3 发布 —— Tool Use 成为一等公民

Anthropic 发布的 Claude 3 (Opus/Sonnet/Haiku) 原生支持 Tool Use，而且能力远超同期 GPT-4。Sonnet 尤其擅长工具调用和代码操作——这些能力直接催生了后来的 Claude Code。

### 2024.5：Devin —— 第一个"AI 软件工程师"

Cognition AI 发布 Devin，标榜"第一个 AI 软件工程师"。虽然实际可用性有争议，但它树立了一个标杆：**AI Agent 应该能独立完成端到端的工程任务**。

### 2024 下半年：编码 Agent 大战

- **Cursor** 发布 Agent 模式：不只是补全，而是自主修复、重构
- **Aider** 持续进化：基于 git diff 的 AI 结对编程
- **Cline**（VS Code 插件）：开源编码 Agent，用 Claude API
- **Claude Code** (2024.10)：Anthropic 官方终端 Agent，在开发者社区引爆

竞争的核心不再是"模型谁更强"，而是"**谁能在终端里更可靠地完成任务**"——Harness 工程浮出水面。

## 2025：Harness 概念确立

### 2025.2：swyx 的 AI Engineer Summit 演讲

> "The model is the brain. The harness is the body."

swyx 在一次主题演讲中正式提出 **Harness** 这个概念。他的核心论点：

1. **模型能力正在 commoditizing**：各家的模型越来越接近，模型本身的差异在缩小
2. **竞争焦点转向基础设施**：谁的工具系统更好、权限更安全、上下文管理更高效、多 Agent 协作更稳定——这些才是差异化的关键
3. **Harness 才是产品**：用户不关心用的是什么模型，用户关心"事办成了没有"

这标志着 Agent 工程从 **"选哪个模型"** 进入了 **"怎么设计 Harness"** 的新阶段。

### 2025.3-6：OpenAI Codex CLI

OpenAI 发布 Codex CLI 开源项目——用 Rust 写的 100+ crates 的编码 Agent。它的核心贡献：

- **多层沙箱安全模型**：macOS Seatbelt / Linux Landlock + bubblewrap / Windows Sandbox
- **两阶段记忆流水线**：并行提取 + 全局整合
- **MCP 集成**：外部工具的标准协议
- **Dogfooding**：Codex 用自己开发自己

Codex 的架构告诉我们：**一个好的 Harness 是用安全、隔离、模块化来保护 Agent 的自主决策**。

### 2025 下半年：多智能体爆发

- **OpenClaw**：25+ 消息平台的自托管 AI 网关，原生支持 `sessions_spawn` 多智能体
- **CrewAI** 推出 v1.0：多 Agent 角色分工
- **AutoGen** 持续演进：微软的多 Agent 对话框架
- **LangGraph**：有状态的 Agent 工作流图

### 2025 年底：Meta 收购 Manus

Meta 以约 $20 亿收购了 Manus——一个 AI Agent 创业公司。业界评论一致：**收购的是 Harness，不是模型**。

这个事件被广泛解读为：**Harness 工程的价值已经得到产业验证**。

## 2026：Harness 工程成为独立学科

### 2026.1：IMPACT 框架

swyx 在年初提出 IMPACT 框架——Agent 工程的六个维度：

| 维度 | 含义 | Harness 对应 |
|------|------|-------------|
| **I**ntent | 目标编码与验证 | Eval 系统 |
| **M**emory | 长程记忆与技能复用 | MEMORY.md / Skills |
| **P**lanning | 多步可编辑计划 | TodoWrite / Plan Mode |
| **A**uthority | 信任、权限、沙箱 | Permission System |
| **C**ontrol Flow | 动态 vs 预设执行路径 | Agent Loop |
| **T**ools | 搜索、执行、浏览器 | Tool System / MCP |

每一个维度都是一个 Harness 子系统。

### 2026.2：多智能体编排窗口

2026 年 2 月的两周内，几乎所有主要工具同步发布了多 Agent 功能：

- Claude Code：子代理 spawning
- Cursor：Agent teams
- Windsurf：Multi-agent workflows
- Grok Build：Agent orchestration
- Codex CLI：Sub-agent system
- Devin：Team mode
- Cline：Multi-agent mode

这不是巧合——这是 Harness 工程成熟的信号：**当基础设施（工具、权限、上下文管理）稳定后，多 Agent 协作自然成为下一步**。

### 2026.3.31：Claude Code 源码泄露

Anthropic 在发布 `@anthropic-ai/claude-code` npm 包时，意外将 `.map` source map 文件打包进去，导致约 1,906 个 TypeScript 文件、51.2 万行源码泄露。

社区迅速分析：

- **~19-40 个工具**：文件读写、shell、git、web、MCP、LSP、子代理...
- **权限系统**：deny → ask → allow 三级管道
- **上下文管理**：auto-inject + compaction + MCP lazy loading
- **MCP 集成**：HTTP/stdio/SSE 三种传输模式
- **LSP 集成**：Claude Code 的独有优势——通过语言服务器协议实现精确语义理解

这次泄露催生了大量开源 Harness 项目（我们后面会详细讲 OpenHarness、claw-code、learn-claude-code）。

### 2026.4-5：Harness 工程的教育化

- **learn-claude-code** 56K+ stars：12 节从零构建 Harness 的教程
- **OpenHarness** 9K+ stars：MIT 许可的完整 Harness 实现
- **agent-harness-framework**：统一 Claude Code/Copilot/Codex 的配置管理
- **claw-code** 160K+ stars：Rust 清洁室重写

Harness 从一个大厂的内部基础设施，变成了**可学习、可复现、可改进的公开知识**。

## 关键洞察

回头看这三年的演进，有一条清晰的轨迹：

```
2023: "模型可以当 Agent 用吗？"    → 能，但不可靠
2024: "怎么让 Agent 更可靠？"       → 加工具、加权限、加上下文管理
2025: "可靠性来自哪里？"            → 来自 Harness，不是模型
2026: "Harness 怎么设计？"          → 成为独立学科，百花齐放
```

**核心转折点**：2025 年，业界认识到——Agent 的可靠性不是靠更好的 prompt 来"说服"模型，而是靠更好的基础设施来**支撑**模型。这就是从 **Prompt Engineering** 到 **Harness Engineering** 的范式转移。

## 本章小结

- 2023 是 Agent 元年：ReAct、AutoGPT、Function Calling 铺平了路
- 2024 是从框架到产品：Claude Code、Devin、Cursor Agent 模式让 Agent 真正可用
- 2025 是 Harness 概念确立：swyx 的演讲、OpenAI Codex、Meta 收购 Manus
- 2026 是 Harness 工程成熟：多 Agent 爆发、Claude Code 源码泄露、教育化
- **核心范式转移**：从 Prompt Engineering（2023）→ Harness Engineering（2025-26）

下一章我们正式进入 Harness 的概念溯源——这个概念到底怎么定义，它的核心组件是什么。

---

**系列目录**：
- [第一章：从符号AI到深度学习 —— Agent的70年简史](./01-agent-70-years-history.md) 👈 前一章
- 第二章：LLM时代的Agent革命 —— 2023-2026爆发期 👈 当前位置
- [第三章：Harness概念溯源 —— "模型是大脑，Harness是身体"](../02-fundamentals/03-harness-concept-origin.md) 👉 下一章
- [第四章：Harness的核心架构 —— 四层模型详解](../02-fundamentals/04-harness-core-architecture.md)
- [第五章：Harness vs Agent vs Model —— 三者关系辨析](../02-fundamentals/05-harness-agent-model-relationship.md)
