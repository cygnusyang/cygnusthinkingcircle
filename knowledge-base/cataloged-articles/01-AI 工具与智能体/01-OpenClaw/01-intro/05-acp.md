# 第五章：ACP —— 如何对接外部 AI 客户端

如果你已经在本机装了 Codex、Claude Code、Gemini CLI、OpenCode 这类外部编码代理，OpenClaw 不需要重造一套运行时。它可以通过 **ACP agents** 把这些外部 harness 接进自己的会话体系里。

这一章只讲当前源码里的真实能力，不讲已经废弃或不存在的旧接口。

## 什么是 ACP

ACP 指的是 **Agent Client Protocol**。在 OpenClaw 里，它的作用很明确：

> 用 ACP 后，OpenClaw 可以把一个任务交给外部 agent runtime 去跑，同时仍然保留 OpenClaw 自己的会话、路由、线程绑定和结果回传。

和普通 `sessions_spawn` 的区别，不是“有没有子任务”，而是**子任务到底跑在哪个 runtime 里**：

- 原生 sub-agent：跑在 OpenClaw 自己的 sub-agent runtime
- ACP session：跑在 ACP backend 插件后面的外部 harness 里

## 会话长什么样

ACP 会话不是普通子会话。当前文档和源码约定的会话键形态是：

```text
agent:<agentId>:acp:<uuid>
```

例如：

```text
agent:codex:acp:9c2c2c7e-...
agent:claude:acp:4c3f9b1a-...
```

这意味着 ACP 会话也进入了 OpenClaw 的标准会话体系：

- 可以被路由到正确线程
- 可以有会话级状态
- 可以被 `/acp status`、`/acp close` 之类命令管理

## 两种常见入口

### 1. 用 `/acp` 命令直接操作

这条路线适合人类操作员手动控制：

```text
/acp spawn codex --mode persistent --thread auto
/acp status
/acp steer tighten logging and continue
/acp close
```

当前官方文档列出的常用命令包括：

- `/acp spawn`
- `/acp cancel`
- `/acp steer`
- `/acp close`
- `/acp status`
- `/acp model`
- `/acp permissions`
- `/acp timeout`
- `/acp sessions`

### 2. 用 `sessions_spawn` 从智能体内部拉起 ACP 会话

这条路线适合让 OpenClaw 自己编排外部编码代理。

最关键的区别是：**要显式设置 `runtime: "acp"`**。

```json
{
  "task": "Open the repo and summarize failing tests",
  "runtime": "acp",
  "agentId": "codex",
  "thread": true,
  "mode": "session"
}
```

这里的字段里，ACP 相关的重点是：

- `runtime: "acp"`：告诉 OpenClaw 走 ACP runtime，而不是默认 sub-agent runtime
- `agentId`：指定 ACP target harness，例如 `codex`、`claude`、`gemini`
- `thread` + `mode: "session"`：在支持线程绑定的渠道里，创建一个可持续对话的 ACP 会话

## ACP 和普通 sub-agent 的区别

| 维度 | ACP session | 普通 sub-agent |
|------|-------------|----------------|
| 运行时 | ACP backend 插件 | OpenClaw 原生 sub-agent runtime |
| 会话键 | `agent:<agentId>:acp:<uuid>` | `agent:<agentId>:subagent:<uuid>` |
| 人类控制命令 | `/acp ...` | `/subagents ...` |
| 典型用途 | 调 Codex / Claude Code / Gemini CLI | OpenClaw 内部多智能体协作 |

一句话说清楚：

- 你要“调用外部编码代理”，用 ACP
- 你要“让 OpenClaw 自己拆任务”，用原生 sub-agent

## 和 MCP 不是一回事

ACP 和 MCP 经常被混淆，但在 OpenClaw 里它们解决的是完全不同的问题：

- **ACP**：把外部 agent runtime 接进来
- **MCP**：给模型提供额外工具、资源或上下文

所以一个完整链路可能长这样：

```text
OpenClaw -> ACP session -> Codex / Claude Code -> 调用其可用工具
```

ACP 负责“谁在干活”，不是“暴露哪些资源”。

## 当前源码里的配置基线

官方 ACP 文档给出的基础配置是：

```json5
{
  acp: {
    enabled: true,
    dispatch: { enabled: true },
    backend: "acpx",
    defaultAgent: "codex",
    allowedAgents: ["pi", "claude", "codex", "opencode", "gemini"],
    maxConcurrentSessions: 8,
    stream: {
      coalesceIdleMs: 300,
      maxChunkChars: 1200,
    },
    runtime: {
      ttlMinutes: 120,
    },
  },
}
```

这里最值得记住的是：

- `acp.enabled`：总开关
- `acp.dispatch.enabled`：允许正常会话消息被分发到 ACP runtime
- `acp.defaultAgent`：省略 `agentId` 时的默认目标
- `acp.allowedAgents`：允许使用哪些 ACP harness id

配置文件位置是当前工程使用的：

```text
~/.openclaw/openclaw.json
```

## 线程绑定是另一层能力

ACP session 能不能“绑定到线程继续聊”，取决于**渠道适配器是否支持 thread binding**。

当前官方文档明确提到的内置支持重点是 Discord。示例配置：

```json5
{
  session: {
    threadBindings: {
      enabled: true,
      idleHours: 24,
      maxAgeHours: 0,
    },
  },
  channels: {
    discord: {
      threadBindings: {
        enabled: true,
        spawnAcpSessions: true,
      },
    },
  },
}
```

这层能力开启后，才有下面这种体验：

1. `/acp spawn codex --mode persistent --thread auto`
2. OpenClaw 自动创建或绑定一个线程
3. 你后续在这个线程里说话，消息继续路由到同一个 ACP session

## 什么时候应该用 ACP

适合：

- 你已经有 Codex、Claude Code、Gemini CLI 这类现成外部代理
- 你希望保留这些工具自己的工作流和擅长领域
- 你希望 OpenClaw 负责协调、路由、回传和线程绑定

不适合：

- 你只是想在 OpenClaw 内部做普通多智能体拆分
- 你不需要外部 harness，只要原生 `sessions_spawn` 就够

## 常见误区

### 误区 1：ACP 就是普通 sub-agent 的别名

不是。两者的 runtime、命令族和会话键都不同。

### 误区 2：只开 `acp.enabled` 就够了

不够。当前文档要求至少还要确认 `acp.dispatch.enabled=true`，线程场景还要看渠道 thread binding 开关。

### 误区 3：ACP 一定绑定线程

不是。`--thread off` 或 `thread: false` 时，ACP session 可以是非绑定的一次性会话。

## 本章小结

- ACP agents 是 OpenClaw 接入外部编码代理的标准路径
- ACP session 的会话键形态是 `agent:<agentId>:acp:<uuid>`
- 人工操作走 `/acp ...`，智能体编排走 `sessions_spawn` + `runtime: "acp"`
- 线程持续对话依赖渠道 thread binding 能力，不是 ACP 自动自带
- 当前配置文件路径是 `~/.openclaw/openclaw.json`

---

**系列目录**：
- [第一章：OpenClaw 是什么 —— 自托管个人 AI 助手的终极形态](./01-what-is-openclaw.md)
- [第二章：核心架构总览 —— Gateway 为什么是中心控制平面](./02-architecture-overview.md)
- [第三章：Gateway —— 核心网关服务到底做了什么](./03-gateway.md)
- [第四章：多渠道接入 —— 如何支持 25+ 聊天平台](./04-multi-channel-inbox.md)
- 第五章：ACP —— 如何对接外部 AI 客户端 👈 当前位置
- [第六章：消息路由 —— 消息如何正确送到对的会话](./06-routing.md) 👉 下一章
- [第七章：安全模型 —— 配对白名单如何保护你](./07-security-model.md)
- [第八章：为什么你需要一个多智能体框架 —— 单智能体的困境](./../02-multi-agent/08-why-you-need-multi-agent-framework.md)
- [第九章：sessions_spawn —— 多智能体协作的核心原语](./../02-multi-agent/09-sessions-spawn-core-primitive.md)
- [第十章：协作架构模式 —— 从 Master-Worker 到 Hub-and-Spoke](./../02-multi-agent/10-collaboration-architecture-patterns.md)
- [第十一章：隔离设计 —— 为什么每个子智能体需要独立会话](./../02-multi-agent/11-isolation-design.md)
- [第十二章：嵌套协作 —— 如何实现 Orchestrator-Worker 模式](./../02-multi-agent/12-nested-collaboration.md)
- [第十三章：实践案例 —— 从零构建一个代码评审团队](./../02-multi-agent/13-practical-case-code-review-team.md)
- [第十四章：platforms —— 全平台安装部署指南](./../03-core-concepts/14-platforms.md)
- [第十五章：providers —— 各大模型提供者配置大全](./../03-core-concepts/15-providers.md)
- [第十六章：plugins —— 插件系统开发指南](./../03-core-concepts/16-plugins.md)
- [第十七章： refactor —— OpenClaw 重构原则与工作流](./../03-core-concepts/17-refactor.md)
- [第十八章：reference —— 完整配置、模板、CLI 命令参考](./../03-core-concepts/18-reference.md)
- [第十九章：skills —— 技能系统核心概念与开发指南](./../03-core-concepts/19-skills.md)
- [第二十章：ClawHub —— 技能市场如何分享和获取技能](./../03-core-concepts/20-clawhub.md)
- [第二十一章：Canvas A2UI —— 实时可视化协作 workspace](./../04-client-ux/21-canvas.md)
- [第二十二章：语音唤醒 (Voice Wake) —— 语音交互体验](./../04-client-ux/22-voice-wake.md)
- [第二十三章：WebChat —— Gateway WebSocket 聊天界面](./../04-client-ux/23-webchat.md)
- [第二十四章：工具系统 (Tools) —— OpenClaw 工具调用框架设计](./../05-tools-automation/24-tools.md)
- [第二十五章：内置浏览器 —— 网页抓取和交互](./../05-tools-automation/25-browser.md)
- [第二十六章：Cron 自动化 —— 定时任务自动化](./../05-tools-automation/26-cron.md)
- [第二十七章：Onboarding —— 新手引导流程设计](./../05-tools-automation/27-onboarding.md)
- [第二十八章：blogwatcher —— 博客与 RSS 更新监控](./../06-builtin-skills/28-live-covers.md)
- [第二十九章：gh-issues —— GitHub Issues 自动修复编排](./../06-builtin-skills/29-gh-issues.md)
- [第三十章：coding-agent —— 调用外部编码代理](./../06-builtin-skills/30-coding-agent.md)
- [第三十一章：模型故障转移 (Model Failover) —— 如何提高可用性](./../07-ops-best-practices/31-failover.md)
- [第三十二章：调试技巧 —— 如何排查 OpenClaw 问题](./../07-ops-best-practices/32-debugging.md)
- [第三十三章：成本优化 —— 如何用模型分级降低总成本](./../07-ops-best-practices/33-cost-optimization.md)
- [第三十四章：部署运维 —— OpenClaw 网关生产环境最佳实践](./../07-ops-best-practices/34-deployment.md)
