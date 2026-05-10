# 第十八章：reference —— 完整配置、模板、CLI 命令参考

这一章只保留和当前工程一致的参考信息：配置文件位置、常见顶层结构、工作区模板文件，以及最常用的 CLI 命令族。

## 配置文件位置

当前 OpenClaw 使用的主配置文件是：

```text
~/.openclaw/openclaw.json
```

格式是 **JSON5**，所以允许注释和尾逗号。

## 顶层结构要看什么

源码里的配置非常大，但日常最常碰到的是这些块：

```json5
{
  env: {
    OPENAI_API_KEY: "sk-...",
    ANTHROPIC_API_KEY: "sk-ant-...",
  },

  gateway: {
    port: 18789,
    bind: "127.0.0.1",
  },

  agents: {
    defaults: {
      workspace: "~/.openclaw/workspace",
      models: {
        "anthropic/claude-opus-4-6": { alias: "opus" },
        "openai/gpt-5.2": { alias: "gpt" },
      },
      model: {
        primary: "anthropic/claude-opus-4-6",
        fallbacks: ["openai/gpt-5.2"],
      },
      heartbeat: {
        every: "30m",
      },
    },
    list: [
      {
        id: "main",
      },
    ],
  },

  channels: {
    telegram: {},
    discord: {},
  },

  plugins: {
    enabled: true,
    entries: {},
  },

  tools: {
    profile: "coding",
  },

  skills: {
    entries: {},
  },

  browser: {
    enabled: true,
    defaultProfile: "chrome",
  },

  session: {
    threadBindings: {
      enabled: true,
    },
  },
}
```

这里有几个容易写错的点：

- 主配置路径是 `~/.openclaw/openclaw.json`，不是旧文档里的 `~/.openclaw/openclaw.json`
- `agents.defaults.model` 当前可以是字符串，也可以是 `{ primary, fallbacks }`
- cron job 不建议手工塞在一个旧式的大数组里维护，当前官方流程更偏向 `openclaw cron add/edit`

## 配置校验规则

当前 OpenClaw 的配置校验是严格的：

- 未知字段会报错
- 插件配置按各自 `openclaw.plugin.json` 里的 `configSchema` 校验
- 配置错误会阻止 Gateway 正常启动

排查时最常用命令还是：

```bash
openclaw doctor
openclaw doctor --fix
```

## 当前工作区模板文件

当前参考模板目录里，核心模板是下面这些：

| 文件 | 作用 |
|------|------|
| `BOOTSTRAP.md` | 首次启动时的引导脚本 |
| `BOOT.md` | 更轻量的启动引导模板 |
| `AGENTS.md` | 工作区主规则 |
| `IDENTITY.md` | AI 身份与自我定义 |
| `USER.md` | 用户信息与偏好 |
| `SOUL.md` | 风格、价值观、边界 |
| `TOOLS.md` | 本地工具习惯与偏好 |
| `HEARTBEAT.md` | 心跳任务提示词 |

当前源码文档模板目录里没有把 `MEMORY.md` 列为这套标准模板的一部分，所以这里不应该再把它写成官方固定模板文件。

## 模板应该怎么理解

### `AGENTS.md`

这是工作区主说明书，给 agent 讲清楚：

- 这个工作区怎么协作
- 先读什么文件
- 风格和边界是什么
- 哪些工具偏好是本地约定

### `IDENTITY.md` / `USER.md` / `SOUL.md`

这三个文件分别解决三个不同问题：

- `IDENTITY.md`：我是谁
- `USER.md`：用户是谁
- `SOUL.md`：我们希望长期保持什么风格和价值判断

### `HEARTBEAT.md`

这是定时心跳 run 会参考的提示文件，不是普通对话模板。

### `BOOTSTRAP.md` / `BOOT.md`

这两类文件负责工作区“第一次启动时如何初始化人格和协作方式”，不是长期规则本体。

## CLI 命令族速查

### 配置与初始化

```bash
openclaw setup
openclaw onboard
openclaw configure
openclaw config get <path>
openclaw config set <path> <value>
openclaw config unset <path>
openclaw doctor
```

### 插件

```bash
openclaw plugins list
openclaw plugins info <id>
openclaw plugins install <spec>
openclaw plugins enable <id>
openclaw plugins disable <id>
openclaw plugins update <id>
openclaw plugins update --all
openclaw plugins doctor
```

### Skills

当前 CLI 里稳定存在的 skills 命令是：

```bash
openclaw skills list
openclaw skills info <name>
openclaw skills check
```

安装和发布工作流现在主要走 `clawhub`。

### 浏览器

```bash
openclaw browser profiles
openclaw browser tabs
openclaw browser open <url>
openclaw browser focus <targetId>
openclaw browser close <targetId>
openclaw browser snapshot
openclaw browser screenshot
openclaw browser navigate <url>
openclaw browser click <ref>
openclaw browser type <ref> "<text>"
```

### Cron

```bash
openclaw cron add
openclaw cron edit <job-id>
openclaw cron list
openclaw cron run <job-id>
openclaw cron runs --id <job-id>
openclaw cron rm <job-id>
```

## 现在最容易踩的坑

### 1. 配置文件路径写错

当前工程里应统一为：

```text
~/.openclaw/openclaw.json
```

### 2. 把技能安装理解成 `clawhub` 安装流

当前分发链路已经转向 `clawhub`。

### 3. 模板文件列表

当前参考模板是 `BOOTSTRAP / BOOT / AGENTS / IDENTITY / USER / SOUL / TOOLS / HEARTBEAT` 这一组。

## 本章小结

- 当前主配置文件是 `~/.openclaw/openclaw.json`
- 日常最关键的块是 `gateway`、`agents`、`channels`、`plugins`、`tools`、`skills`、`browser`、`session`
- 官方参考模板当前以 `AGENTS.md`、`BOOTSTRAP.md`、`BOOT.md`、`IDENTITY.md`、`USER.md`、`SOUL.md`、`TOOLS.md`、`HEARTBEAT.md` 为主
- skills 安装/发布链路看 `clawhub`，不是旧式 `openclaw skills` 安装方式

---

**系列目录**：
- [第一章：OpenClaw 是什么 —— 自托管个人 AI 助手的终极形态](./../01-intro/01-what-is-openclaw.md)
- [第二章：核心架构总览 —— Gateway 为什么是中心控制平面](./../01-intro/02-architecture-overview.md)
- [第三章：Gateway —— 核心网关服务到底做了什么](./../01-intro/03-gateway.md)
- [第四章：多渠道接入 —— 如何支持 25+ 聊天平台](./../01-intro/04-multi-channel-inbox.md)
- [第五章：ACP —— 如何对接外部 AI 客户端](./../01-intro/05-acp.md)
- [第六章：消息路由 —— 消息如何正确送到对的会话](./../01-intro/06-routing.md)
- [第七章：安全模型 —— 配对白名单如何保护你](./../01-intro/07-security-model.md)
- [第八章：为什么你需要一个多智能体框架 —— 单智能体的困境](./../02-multi-agent/08-why-you-need-multi-agent-framework.md)
- [第九章：sessions_spawn —— 多智能体协作的核心原语](./../02-multi-agent/09-sessions-spawn-core-primitive.md)
- [第十章：协作架构模式 —— 从 Master-Worker 到 Hub-and-Spoke](./../02-multi-agent/10-collaboration-architecture-patterns.md)
- [第十一章：隔离设计 —— 为什么每个子智能体需要独立会话](./../02-multi-agent/11-isolation-design.md)
- [第十二章：嵌套协作 —— 如何实现 Orchestrator-Worker 模式](./../02-multi-agent/12-nested-collaboration.md)
- [第十三章：实践案例 —— 从零构建一个代码评审团队](./../02-multi-agent/13-practical-case-code-review-team.md)
- [第十四章：platforms —— 全平台安装部署指南](./14-platforms.md)
- [第十五章：providers —— 各大模型提供者配置大全](./15-providers.md)
- [第十六章：plugins —— 插件系统开发指南](./16-plugins.md)
- [第十七章： refactor —— OpenClaw 重构原则与工作流](./17-refactor.md)
- 第十八章：reference —— 完整配置、模板、CLI 命令参考 👈 当前位置
- [第十九章：skills —— 技能系统核心概念与开发指南](./19-skills.md) 👉 下一章
- [第二十章：ClawHub —— 技能市场如何分享和获取技能](./20-clawhub.md)
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
