# Harness 博客系列目录

这个系列从浅入深讲解 AI Agent Harness，从 Agent 的 70 年历史出发，到 Harness 核心概念、各大实现、深入每个子系统、动手构建，最后探讨智能体的未来。

## 第一部分：Agent 历史回顾（01-history）

1. [从符号AI到深度学习 —— Agent的70年简史](./01-history/01-agent-70-years-history.md)
2. [LLM时代的Agent革命 —— 2023-2026爆发期](./01-history/02-llm-era-agent-revolution.md)

## 第二部分：Harness 基础（02-fundamentals）

3. [Harness概念溯源 —— "模型是大脑，Harness是身体"](./02-fundamentals/03-harness-concept-origin.md)
4. [Harness的核心架构 —— 四层模型详解](./02-fundamentals/04-harness-core-architecture.md)
5. [Harness vs Agent vs Model —— 三者关系辨析](./02-fundamentals/05-harness-agent-model-relationship.md)

## 第三部分：各大实现（03-implementations）

6. [Claude Code的Harness架构剖析](./03-implementations/06-claude-code-harness-architecture.md)
7. [Codex的Harness架构剖析](./03-implementations/07-codex-harness-architecture.md)
8. [OpenClaw的Harness架构](./03-implementations/08-openclaw-harness-architecture.md)
9. [开源Harness生态全景](./03-implementations/09-open-source-harness-ecosystem.md)

## 第四部分：深入 Harness（04-deep-dive）

10. [Agent Loop —— Harness的心跳](./04-deep-dive/10-agent-loop.md)
11. [工具系统 —— 从Bash到MCP的工具分发](./04-deep-dive/11-tool-system.md)
12. [权限系统 —— deny→ask→allow的安全边界](./04-deep-dive/12-permission-system.md)
13. [上下文管理 —— 自动注入、压缩与惰性加载](./04-deep-dive/13-context-management.md)
14. [MCP集成 —— 扩展Harness的能力边界](./04-deep-dive/14-mcp-integration.md)
15. [技能系统 —— 按需注入领域知识](./04-deep-dive/15-skills-system.md)

## 第五部分：Agent 与 Harness（05-agent-harness）

16. [Agent的生命周期 —— 从prompt到执行完成](./05-agent-harness/16-agent-lifecycle.md)
17. [Harness是Agent的操作系统](./05-agent-harness/17-harness-as-os.md)
18. [Claude Code、Codex、OpenClaw中的Agent-Harness协作模式](./05-agent-harness/18-agent-harness-collaboration.md)

## 第六部分：多智能体（06-multi-agent）

19. [多智能体架构模式 —— Master-Worker、Hub-Spoke、Pipeline](./06-multi-agent/19-multi-agent-architectures.md)
20. [子代理隔离与上下文管理](./06-multi-agent/20-subagent-isolation.md)
21. [Agent间通信协议 —— A2A、Task、Message Passing](./06-multi-agent/21-agent-communication.md)

## 第七部分：动手构建（07-build-your-own）

22. [从零构建Mini-Harness —— 最小可行循环](./07-build-your-own/22-build-mini-harness.md)
23. [添加工具系统与权限控制](./07-build-your-own/23-adding-tools-and-permissions.md)
24. [添加MCP与多智能体支持](./07-build-your-own/24-adding-mcp-and-multi-agent.md)

## 第八部分：智能体的未来（08-future）

25. [2026年Harness生态全景 —— 从模型竞争到Harness竞争](./08-future/25-harness-ecosystem-2026.md)
26. [从规则到环境 —— Agent工程的下一个范式转移](./08-future/26-from-rules-to-environment.md)
27. [智能体的未来 —— 自主性、安全性与AGI](./08-future/27-future-of-agents.md)

---

## 源码参考

所有源码都在 `source/` 目录：

| 项目 | 路径 | 语言 | 协议 |
|------|------|------|------|
| OpenHarness | `source/openharness/` | Python | MIT |
| learn-claude-code | `source/learn-claude-code/` | TS + Python | MIT |
| claw-code | `source/claw-code/` | Rust + Python | — |
| celesteanders-harness | `source/celesteanders-harness/` | Python | — |
| claude-code-harness | `source/chachamaru127-harness/` | TypeScript | MIT |
| agent-harness-framework | `source/agent-harness-framework/` | TypeScript (npm) | — |

## 关键文档

- `CLAUDE.md` — 仓库目的、结构、约定
- `source/openharness/README.md` — OpenHarness 官方文档
- `source/learn-claude-code/README.md` — 12 节课程总览

## 核心概念速查

| 概念 | 一句话定义 |
|------|-----------|
| **Model** | 推理引擎——输入→输出，无状态无感知无动作 |
| **Agent** | 决策循环——Model + 目标 + 记忆 + 循环 |
| **Harness** | 能力边界——工具 + 权限 + 上下文 + 编排 |
| **Agent Loop** | observe → think → act → feedback 的持续循环 |
| **MCP** | 连接 AI 和外部工具的开放协议 |
| **Skill** | 按需注入的领域知识（Markdown 文件） |

---

*本博客系列基于对 Claude Code、Codex、OpenClaw 及多个开源 Harness 项目的源码分析和社区研究撰写。Harness 工程是一个快速演进的领域，本文写于 2026 年 5 月。*
