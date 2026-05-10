# 第十五章：providers —— 各大模型提供者配置大全

OpenClaw 支持几乎所有主流大语言模型提供者，从云端 API 到本地部署都可以。本章我们讲解几个最常用的模型提供者的配置方法。

## 什么是模型提供者

模型提供者就是**提供 AI 模型推理服务**的地方：

- 云端 API：Anthropic、OpenAI、Google 等
- 本地运行：Ollama、vLLM 等
- 网关：LiteLLM、Vercel AI Gateway 等统一网关

OpenClaw 使用 `provider/model` 的格式来引用模型，比如 `anthropic/claude-opus-4-6`、`ollama/gpt-oss:20b`。

---

## Anthropic (Claude)

Anthropic 出品的 Claude 模型，是 OpenClaw 推荐使用的主力模型。支持两种认证方式：API 密钥 或 Claude Code CLI 的 setup-token。

### 方式一：API 密钥（推荐用于生产）

**适合**：标准 API 访问，按使用量计费。

#### 快速配置

```bash
# 交互式 onboard
openclaw onboard
# 选择 "Anthropic API key"

# 或者非交互式
openclaw onboard --anthropic-api-key "$ANTHROPIC_API_KEY"
```

#### 配置示例

配置写在你的**主配置文件** `~/.openclaw/openclaw.json`：

```json5
{
  env: { ANTHROPIC_API_KEY: "sk-ant-..." },
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-6" } } },
}
```

### 方式二：Claude Code CLI setup-token（复用订阅）

**适合**：你已经有 Claude Code 订阅，可以复用 token 不用再买 API。

#### 获取 token

在任何机器上运行：

```bash
claude setup-token
```

把 token 粘贴到 OpenClaw：

```bash
# 交互式 onboard
openclaw onboard --auth-choice setup-token

# 或者命令行
openclaw models auth setup-token --provider anthropic
```

### 提示缓存配置

Anthropic API 支持提示缓存，可以大幅降低成本。OpenClaw 默认开启：

| 配置值 | 缓存时间 | 说明 |
|--------|----------|------|
| `none` | 无缓存 | 禁用 |
| `short` | 5 分钟 | 默认值 |
| `long` | 1 小时 | 延长缓存（需要 beta 权限） |

配置示例，写在你的**主配置文件** `~/.openclaw/openclaw.json`：

```json5
{
  agents: {
    defaults: {
      model: { primary: "anthropic/claude-opus-4-6" },
      models: {
        "anthropic/claude-opus-4-6": {
          params: { cacheRetention: "long" },
        },
      },
    },
  },
}
```

**默认**：API 密钥认证自动使用 `cacheRetention: "short"`。

### 1M 上下文窗口（beta）

Anthropic 提供 1M 上下文 beta，开启方式，配置写在你的**主配置文件** `~/.openclaw/openclaw.json`：

```json5
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-opus-4-6": {
          params: { context1m: true },
        },
      },
    },
  },
}
```

### 常见问题

**Q: 401 error / token 突然失效**  
A: Claude 订阅 token 可能过期，重新用 `claude setup-token` 生成，再粘贴到 gateway。

**Q: No API key found**  
A: 认证是**按 Agent 区分**，新 Agent 不会继承主 Agent 的密钥，需要重新配置。

---

## OpenAI (GPT)

OpenAI 提供 GPT 模型系列，支持 API 密钥和 Codex 订阅两种方式。

### 方式一：API 密钥

**适合**：直接 API 访问，按使用量计费。

```bash
openclaw onboard --auth-choice openai-api-key
```

配置，写在你的**主配置文件** `~/.openclaw/openclaw.json`：

```json5
{
  env: { OPENAI_API_KEY: "sk-..." },
  agents: { defaults: { model: { primary: "openai/gpt-5.1" } } },
}
```

### 方式二：OpenAI Code (Codex) 订阅

**适合**：复用你的 ChatGPT/Codex 订阅，不用额外买 API 密钥。

```bash
openclaw onboard --auth-choice openai-codex
```

配置：

```json5
{
  agents: { defaults: { model: { primary: "openai-codex/gpt-5.3-codex" } } },
}
```

### 传输选择

Codex 支持两种传输方式，可配置，配置写在你的**主配置文件** `~/.openclaw/openclaw.json`:

```json5
{
  agents: {
    defaults: {
      models: {
        "openai-codex/gpt-5.3-codex": {
          params: { transport: "auto" }, // auto | websocket | sse
        },
      },
    },
  },
}
```

- `auto`：默认，先试 WebSocket，不行回退 SSE
- `websocket`：强制 WebSocket
- `sse`：强制 SSE

### 服务端上下文压缩

OpenAI Responses API 支持服务端上下文压缩，OpenClaw 默认开启，配置写在你的**主配置文件** `~/.openclaw/openclaw.json`:

```json5
// 禁用
{
  agents: {
    defaults: {
      models: {
        "openai/gpt-5": {
          params: { responsesServerCompaction: false },
        },
      },
    },
  },
}
```

---

## Google (Gemini)

Google Gemini 模型通常通过 **LiteLLM 网关** 或者 **Vertex AI** 接入。这里给出通用配置方式。

### 通过 LiteLLM 接入

如果你用 LiteLLM 统一网关，配置示例写在你的**主配置文件** `~/.openclaw/openclaw.json`:

```json5
{
  models: {
    providers: {
      litellm: {
        baseUrl: "https://your-litellm-gateway/v1",
        apiKey: "your-litellm-key",
      },
    },
  },
  agents: {
    defaults: {
      model: { primary: "litellm/gemini-2.5-pro" },
    },
  },
}
```

### 直接配置（如果你有直接 API 密钥）

配置写在你的**主配置文件** `~/.openclaw/openclaw.json`:

```json5
{
  env: { GOOGLE_API_KEY: "your-google-api-key" },
  models: {
    providers: {
      google: {
        apiKey: "$env:GOOGLE_API_KEY",
      },
    },
  },
  agents: {
    defaults: {
      model: { primary: "google/gemini-2.5-pro" },
    },
  },
}
```

---

## 本地模型（Ollama）

Ollama 是最简单的本地 LLM 运行方式，OpenClaw 原生支持，自动发现模型。

### 快速开始

1. 安装 Ollama：https://ollama.ai
2. pull 一个模型：
```bash
ollama pull gpt-oss:20b
ollama pull llama3.3
ollama pull qwen2.5-coder:32b
```

3. 启用 Ollama：
```bash
# 设置环境变量就行（任意值，Ollama 不需要真实密钥）
export OLLAMA_API_KEY="ollama-local"
```

4. 使用，配置写在你的**主配置文件** `~/.openclaw/openclaw.json`:
```json5
{
  agents: {
    defaults: {
      model: { primary: "ollama/gpt-oss:20b" },
    },
  },
}
```

### 自动发现模型

如果你只设置了 `OLLAMA_API_KEY` 没有手动配置 `models.providers.ollama`，OpenClaw 会：

1. 调用 `/api/tags` 获取已安装模型
2. 只保留声明了工具支持的模型
3. 自动读取上下文窗口大小
5. 成本都设为 0（本地运行免费）

查看发现的模型：

```bash
openclaw models list
```

### 手动配置（自定义地址端口）

如果 Ollama 跑在其他主机上，需要手动配置，写在你的**主配置文件** `~/.openclaw/openclaw.json`:

```json5
{
  models: {
    providers: {
      ollama: {
        baseUrl: "http://ollama-host:11434", // 不要加 /v1
        apiKey: "ollama-local",
        api: "ollama", // 使用原生 Ollama API，工具调用最可靠
        models: [
          {
            id: "gpt-oss:20b",
            name: "GPT-OSS 20B",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 8192,
            maxTokens: 81920,
          }
        ]
      },
    },
  },
}
```

> ⚠️ **重要**：不要在 URL 末尾加 `/v1`。`/v1` 是 OpenAI 兼容模式，工具调用不可靠。原生 Ollama API 直接用 `http://host:11434` 就行。

### 常见问题

**Q: 模型没有被发现**  
A: OpenClaw 只自动发现**声明了工具支持**的模型。如果你的模型没被发现，需要手动配置。

**Q: 连接被拒绝**  
A: 检查 Ollama 是否运行在正确端口：`ps aux | grep ollama`，`curl http://localhost:11434/api/tags` 测试。

---

## 其他常见提供者

OpenClaw 还支持很多其他提供者，配置方式类似：

| 提供者 | 说明 | 配置方式 |
|--------|------|----------|
| **LiteLLM** | 统一多模型网关 | 参考官方文档 [providers/litellm](https://docs.openclaw.ai/providers/litellm) |
| **vLLM** | 本地高性能推理 | 类似 Ollama 配置，指定 baseUrl 就行 |
| **OpenRouter** | 多模型聚合平台 | API 密钥方式，和 OpenAI 类似 |
| **Moonshot** | 月之暗面 Kimi | API 密钥方式 |
| **Mistral** | Mistral 官方 API | API 密钥方式 |
| **Amazon Bedrock** | AWS 托管模型 | IAM 认证 |
| **Venice AI** | 隐私优先推理 | 支持本地隐私推理 |

---

## 最佳实践

### 1.  fallback 配置

配置多个 fallback 模型，提高可用性，配置写在你的**主配置文件** `~/.openclaw/openclaw.json`:

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "anthropic/claude-opus-4-6",
        fallbacks: [
          "anthropic/claude-sonnet-4-5",
          "openai/gpt-5",
          "ollama/llama3.3",
        ],
      },
    },
  },
}
```

这样主模型不可用时，自动 fallback 到下一个，提高可用性。这就是**模型故障转移**，我们第七部分还会讲。

### 2. 成本分级

- 简单任务：用便宜小模型
- 复杂任务：用强大大模型
- OpenClaw 多智能体架构可以自动分配，省钱效果好

### 3. 本地模型适合什么

- 隐私敏感任务（数据不能出网）
- 低成本批量处理
- 离线使用
- 强力大模型本地跑需要好硬件

### 4. 云端模型适合什么

- 需要最强推理能力
- 没有高性能硬件
- 方便快捷，不用维护

---

## 本章小结

- OpenClaw 支持几乎所有主流模型提供者，格式 `provider/model`
- Anthropic Claude 支持 API 密钥和 Claude Code 订阅 token 两种方式
- OpenAI GPT 支持 API 密钥和 Codex 订阅两种方式
- Google Gemini 通常通过 LiteLLM 等网关接入
- Ollama 是最简单的本地模型方式，支持自动发现
- 配置 fallback 提高可用性，成本分级省 money

---

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
- 第十五章：providers —— 各大模型提供者配置大全 👈 当前位置
- [第十六章：plugins —— 插件系统开发指南](./16-plugins.md) 👉 下一章
- [第十七章： refactor —— OpenClaw 重构原则与工作流](./17-refactor.md)
- [第十八章：reference —— 完整配置、模板、CLI 命令参考](./18-reference.md)
- [第十九章：skills —— 技能系统核心概念与开发指南](./19-skills.md)
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
