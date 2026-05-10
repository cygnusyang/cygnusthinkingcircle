# 第三十一章：模型故障转移 (Model Failover) —— 如何提高可用性

模型 API 不是 100% 可用，会有超时、限流、宕机。OpenClaw 设计了模型故障转移机制，主模型不可用时自动切备用模型，保证你的任务能继续跑。本章讲解故障转移配置和最佳实践。

## 什么是模型故障转移

故障转移 = **主模型挂了自动切下一个**：

你配置：`primary: A, fallbacks: [B, C]`
- 正常情况用 A
- A 超时/限流/报错 → 自动试 B
- B 也不行 → 自动试 C
- 都不行 → 才告诉你失败

这样大大提高可用性，不会因为一个模型宕机整个任务就废了。

## 为什么需要故障转移

- **API 限流**：Anthropic/OpenAI 都会限流，高峰期你可能命中限流
- **服务宕机**：云端 API 也会有 downtime
- **网络问题**：你的网络临时抽风，连不上
- **额度用完**：额度不小心花完了，切备用模型继续跑

有了故障转移，这些问题自动处理，不用你立刻手动切。

## 配置方法

### 全局默认配置

配置写在你的**主配置文件** `~/.openclaw/openclaw.json` 的 `agents.defaults.model` 下：

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "anthropic/claude-opus-4-6",
        fallbacks: [
          "anthropic/claude-sonnet-4-6",
          "openai/gpt-5",
          "ollama/llama3.3:70b",
        ],
      },
    },
  },
}
```

### 单个 Agent 覆盖

配置写在你的**主配置文件** `~/.openclaw/openclaw.json` 的 `agents.list[]` 下（每个 Agent 独立配置）：

```json5
{
  agents: {
    list: [
      {
        id: "coding-agent",
        model: {
          primary: "anthropic/claude-opus-4-6",
          fallbacks: ["openai/gpt-5"],
        },
      },
    ],
  },
}
```

### 每个模型可以有独立配置

配置写在你的**主配置文件** `~/.openclaw/openclaw.json` 的 `agents.defaults.models` 下：

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "anthropic/claude-opus-4-6",
        fallbacks: ["anthropic/claude-sonnet-4-6"],
      },
      models: {
        "anthropic/claude-opus-4-6": {
          params: {
            cacheRetention: "long",
          },
        },
        "anthropic/claude-sonnet-4-6": {
          params: {
            cacheRetention: "short",
          },
        },
      },
    },
  },
}
```

## 触发故障转移的条件

哪些错误会触发切 fallback：

| 错误类型 | 触发 failover | 说明 |
|----------|---------------|------|
| 网络超时 | ✅ | 是 |
| 连接错误 | ✅ | 是 |
| 429 限流 | ✅ | 是 |
| 5xx 服务器错误 | ✅ | 是 |
| 401 认证错误 | ❌ | 不会，密钥错了切了也没用 |
| 400 参数错误 | ❌ | 你参数错了，切模型也错 |
| 内容过滤拒绝 | ❌ | 内容违规，切模型也一样拒绝 |

设计原则：**只有模型服务本身不可用时才转移，客户端错误不用转移**。

## 重试策略

默认重试策略：

1. 主模型失败 → 等 1 秒 → 试第一个 fallback
2. 失败 → 等 2 秒 → 试第二个 fallback
3. 失败 → 等 3 秒 → 试第三个
4. 全失败 → 返回错误给用户

指数退避，避免雪崩。

配置可以改重试间隔，写在你的**主配置文件** `~/.openclaw/openclaw.json` 的根级别：

```json5
{
  failover: {
    retryIntervalMs: 1000, // 初始间隔
    backoffMultiplier: 2,  // 每次乘这个数
    maxRetries: 3,          // 最多重试几次
  },
}
```

## 成本优化策略

故障转移可以配合**成本分级**：

| 角色 | 模型 | 成本 | 能力 |
|------|------|------|------|
| Primary | Opus 4.6 | 贵 | 最强能力，复杂任务 |
| Fallback 1 | Sonnet 4.6 | 中等 | 够用，大部分任务能完成 |
| Fallback 2 | GPT-5 | 中等 | 另一家提供商，路由故障不影响 |
| Fallback 3 | 本地 Ollama | 免费 | 彻底断网也能跑简单任务 |

这样：
- 正常情况用最好的模型出最好结果
- 主模型不行自动降级，至少能完成任务
- 成本也控制住了，不会随便切贵的模型

## 最佳实践

### 1. 跨提供商 fallback

不要：`primary: anthropic/claude-opus, fallbacks: [anthropic/claude-sonnet]`  
（Anthropic 整个挂了你还是用不了）

要：`primary: anthropic/claude-opus, fallbacks: [openai/gpt-5]`  
（不同提供商，一个提供商挂了另一个顶上）

 availability 比同提供商高很多。

### 2. 能力匹配

fallback 模型能力不要差太多：
- 主模型 1M 上下文，fallback 也选有大上下文的
- 主模型支持工具调用，fallback 也要支持
- 不然切过去也做不了任务

### 3. 不要太多 fallback

2-3 个足够了，太多也没意义：
- 前两个都不行，第三个大概率也不行
- 多等半天不如早点告诉用户

### 4. 监控告警

配置了故障转移也要监控：
- 记录主模型失败次数
- 失败多了自动通知你
- 可能主模型配额用完了或者密钥过期了，你要处理

## 日志排查

看哪些失败触发了故障转移：

```bash
openclaw models status
```

显示：
- 每个模型调用成功次数
- 每个模型失败次数
- 多少次触发了 failover

看详细日志：

```bash
openclaw logs --grep "failover"
```

能看到：什么时候哪个模型失败，切到哪个模型了。

## 常见问题

**Q: 故障转移会多花钱吗？**  
A: 只有主模型失败才会切 fallback，正常情况不切。如果你搭配成本分级，主模型用贵的好的，fallback 用便宜的，总体成本不会增加多少，可用性提高很多。

**Q: 上下文会带到 fallback 模型吗？**  
A: 会的，整个对话上下文完整带过去，用户不用重新说一遍。

**Q: 流式输出也支持故障转移吗？**  
A: 支持，主模型流式输出断了，fallback 会重新完整输出，用户看到完整结果。

**Q: 可以关掉故障转移吗？**  
A: 可以，fallbacks 留空数组就关掉了，主模型失败直接报错。

## 本章小结

- 模型故障转移自动处理 API 不可用情况，主模型失败自动切备用
- 配置简单：`primary` + `fallbacks` 数组就好了
- 只在服务端错误触发，客户端错误不切
- 最佳实践：跨提供商 fallback，能力匹配，2-3 个足够
- 配合成本分级，可用性提高很多，成本不会增加多少

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
- 第三十一章：模型故障转移 (Model Failover) —— 如何提高可用性 👈 当前位置
- [第三十二章：调试技巧 —— 如何排查 OpenClaw 问题](./32-debugging.md) 👉 下一章
- [第三十三章：成本优化 —— 如何用模型分级降低总成本](./33-cost-optimization.md)
- [第三十四章：部署运维 —— OpenClaw 网关生产环境最佳实践](./34-deployment.md)
