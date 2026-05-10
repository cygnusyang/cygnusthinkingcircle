# 第六章：消息路由 —— 消息如何正确送到对的会话

OpenClaw 的路由不是“模型自己决定回复到哪里”，而是 **Gateway 按确定性规则选定 agent 和 session key**。当前源码里，这套逻辑主要围绕 `bindings`、`session key` 和线程绑定展开。

## 路由真正解决的问题

路由层要同时回答两个问题：

1. 这条入站消息应该交给哪个 agent
2. 这条消息应该落到哪个 session key

如果这两步错了，就会出现最糟糕的问题：

- 群里串台
- 线程上下文断裂
- 子会话结果回到错误地方
- WebChat 和聊天渠道看到的上下文不一致

## 核心概念：Session Key

当前官方文档里，OpenClaw 把上下文桶定义成 **session key**。常见形态如下。

### 私聊

私聊会收敛到 agent 的主会话：

```text
agent:<agentId>:<mainKey>
```

默认主会话通常长这样：

```text
agent:main:main
```

### 群组 / 频道 / 房间

群或频道不会和私聊共用主会话，而是按渠道维度隔离：

```text
agent:<agentId>:<channel>:group:<id>
agent:<agentId>:<channel>:channel:<id>
```

例如：

```text
agent:main:telegram:group:-1001234567890
agent:main:discord:channel:123456
```

### 线程 / 话题

线程会在基础 key 后面继续追加后缀：

- Slack / Discord 线程：`:thread:<threadId>`
- Telegram forum topic：`:topic:<topicId>`

例如：

```text
agent:main:discord:channel:123456:thread:987654
agent:main:telegram:group:-1001234567890:topic:42
```

这里要注意一个关键点：**OpenClaw 当前没有文档化的那套旧式 scope 配置字符串。**

现在的路由依据是 session key 形态和 bindings 规则，而不是那几个 scope 字符串。

## 先选 agent，再选 session

OpenClaw 当前文档给出的 agent 选择顺序是：

1. 精确 peer 匹配
2. 父 peer 匹配（线程继承）
3. Discord 的 `guildId + roles`
4. Discord 的 `guildId`
5. Slack 的 `teamId`
6. `accountId`
7. `channel`
8. 默认 agent

也就是说，**路由优先级是由 `bindings` 决定的**。

一个最小例子：

```json5
{
  agents: {
    list: [
      {
        id: "support",
        name: "Support",
        workspace: "~/.openclaw/workspace-support",
      },
    ],
  },
  bindings: [
    {
      match: { channel: "slack", teamId: "T123" },
      agentId: "support",
    },
    {
      match: {
        channel: "telegram",
        peer: { kind: "group", id: "-100123" },
      },
      agentId: "support",
    },
  ],
}
```

一旦 agent 决定了，后面的会话仓库、工作区、转录和并发控制也就跟着这个 agent 走。

## 当前路由模型的直觉理解

你可以把它想成两层：

- **bindings** 决定“这是谁的大脑”
- **session key** 决定“这条消息属于这个大脑里的哪个上下文桶”

这比旧式的 `per-sender / per-thread / per-channel` 说法更接近当前源码。

## 线程绑定和子会话

当 `sessions_spawn` 或 ACP session 请求线程绑定，而且渠道支持时，OpenClaw 会把某个线程绑定到目标 session。

这时后续消息就不再只按普通群聊规则分流，而是优先落到这个绑定 session。

官方文档里重点提到的内置支持渠道是 Discord。相关能力包括：

- `/focus`
- `/unfocus`
- `/agents`
- `/session idle`
- `/session max-age`

这类机制解决的是“持久线程继续对话”，不是普通消息分发。

## WebChat 的特殊点

WebChat 也走同一套路由体系，但它默认附着在**选中的 agent 主会话**上。

这带来两个结果：

- WebChat 看到的是这个 agent 的主上下文
- 它不是一套单独的“网页版旧式 scope 配置”

所以如果你在别的渠道上把某个 agent 的主会话聊得很长，WebChat 打开时也会看到同一 agent 的这段上下文。

## Broadcast Groups 不是路由冲突，而是有意多播

当前源码还有一个容易混淆的能力：**broadcast groups**。

它的用途不是“随机让多个 agent 都试试”，而是在 OpenClaw 原本就应该回复的时候，把同一条消息并行发给多个 agent。

例如：

```json5
{
  broadcast: {
    strategy: "parallel",
    "120363403215116621@g.us": ["alfred", "baerbel"],
    "+15555550123": ["support", "logger"],
  },
}
```

这属于显式配置的多播，不是普通路由算法失控。

## 会话存储位置

默认状态目录下，每个 agent 都有自己的 session store：

- `~/.openclaw/agents/<agentId>/sessions/sessions.json`
- 对应的 JSONL transcript 文件也在附近

这也是为什么“先选 agent”很重要：agent 一旦不同，整个会话存储命名空间就不同。

## 常见问题

### Q: 群里为什么没有 `per-sender` 配置了？

因为当前文档和源码已经转向以 `bindings` + `session key` 形态来表达路由规则，而不是靠一个旧式 scope 字符串覆盖所有场景。

### Q: 线程消息为什么能持续命中同一个子会话？

因为这里走的是 thread binding，不是普通 group/channel key 推导。

### Q: WebChat 会不会单独开一个新的路由系统？

不会。它依然挂在 Gateway 的 agent 和 session 上，只是默认更接近 agent 主会话。

## 本章小结

- 当前 OpenClaw 路由的核心是 `bindings` 和 `session key`
- 私聊通常收敛到主会话，群组/频道按渠道对象隔离，线程再追加后缀
- agent 选择是确定性优先级匹配，不是模型自由决定
- 持久线程对话依赖 thread binding
- WebChat 不是另一套路由模型，它仍然附着在现有 agent/session 体系上

---

**系列目录**：
- [第一章：OpenClaw 是什么 —— 自托管个人 AI 助手的终极形态](./01-what-is-openclaw.md)
- [第二章：核心架构总览 —— Gateway 为什么是中心控制平面](./02-architecture-overview.md)
- [第三章：Gateway —— 核心网关服务到底做了什么](./03-gateway.md)
- [第四章：多渠道接入 —— 如何支持 25+ 聊天平台](./04-multi-channel-inbox.md)
- [第五章：ACP —— 如何对接外部 AI 客户端](./05-acp.md)
- 第六章：消息路由 —— 消息如何正确送到对的会话 👈 当前位置
- [第七章：安全模型 —— 配对白名单如何保护你](./07-security-model.md) 👉 下一章
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
