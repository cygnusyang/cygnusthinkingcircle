# 第七章：安全模型 —— 配对白名单如何保护你

OpenClaw 跑在你自己服务器上，对外开放吗？谁能访问你的 AI？这就是安全模型要解决的问题。

OpenClaw 默认安全策略：**默认拒绝，手动配对允许**。本章我们讲解这个设计。

## 威胁模型

你把 Gateway 暴露在互联网上，可能的威胁：

1. **陌生人发到你 Gateway 消息** → 想用你的 AI，花你的 API 钱
2. **未授权访问会话** → 读到你的历史对话，泄露隐私
3. **恶意调用危险工具** → 比如 `bash -c rm -rf /`
4. **随机扫描端口** → 尝试闯入

OpenClaw 安全模型就是针对这些威胁。

## 核心设计：配对白名单

OpenClaw 用 **配对白名单** 模型：

```
谁能访问 → 你手动配对允许 → 进白名单 → 才能访问
不在白名单 → 直接拒绝 → 不会处理
```

就是这么简单。

### 哪里配对手

不同渠道配对方式不同：

- **Discord/Slack/Telegram**：机器人只回应你配对允许的用户/服务器
- **群组**：可以允许整个群组，或者只允许群组里某些用户
- **DM**：只允许配对的用户发 DM

### 配置示例

配对白名单配置写在你的**主配置文件** `~/.openclaw/openclaw.json` 的 `channels` 下：

```json5
{
  channels: {
    discord: {
      token: "bot-token",
      pairing: {
        allowUsers: ["your-user-id"], // 只允许这些用户
        allowGuilds: ["your-guild-id"], // 允许这个服务器
      },
    },
  },
}
```

## 默认安全策略

OpenClaw 默认：

| 项目 | 默认策略 |
|------|----------|
| 端口绑定 | `127.0.0.1` → 只本地能访问 |
| 新用户 | 默认拒绝 |
- 工具调用 `sessions_spawn` | HTTP API 默认拒绝 |
- 敏感工具 | 需要显式允许 |

**开箱安全**，你不用配也安全。

## 为什么默认拒绝

如果你不开白名单，谁也用不了，就算你忘记关端口，扫描到了也没用。

> "默认拒绝" 比 "默认允许" 安全。就算漏配置，也不会爆。

## 远程访问安全

你想要远程访问（比如在外边也能用家里 Gateway），推荐做法：

### 方法 1：SSH 隧道

```bash
ssh -N -L 18789:localhost:18789 your-server
```

只有 SSH 认证通过才能连上，安全。

### 方法 2：Tailscale

Tailscale 组网，你的设备都在 Tailnet 里，外部看不到，安全。

### 不推荐：直接绑 0.0.0.0 暴露到公网

你要是直接绑 `0.0.0.0:18789` 暴露公网：

- 任何人只要知道 IP 就能连
- 就算有白名单，也没必要暴露
- 真要暴露，放 Nginx 后面加认证

## 工具权限安全

除了访问控制，工具也有权限：

### `sessions_spawn` 权限

HTTP API 默认禁止 `sessions_spawn`，防止未认证调用 spawn 子任务。你要是 API 需要，显式打开，配置写在你的**主配置文件** `~/.openclaw/openclaw.json` 的 `gateway.tools` 下：

```json5
{
  gateway: {
    tools: {
      allow: ["sessions_spawn"],
    },
  },
}
```

### 敏感工具权限

像 `exec`、`bash` 这些危险工具，默认配置也要小心：

- 只给信任的 agent 开
- 不要给未认证用户开

## 数据安全

- 所有对话存在你本地磁盘，OpenClaw 不收集
- API 密钥只存在你本地，不会传给第三方
- AI 模型 API 调用是你自己密钥，走你自己网络

## 最佳实践

1. **保持默认**：端口绑 `127.0.0.1`，远程用 SSH 隧道/Tailscale
2. **最小权限**：只允许你自己用户，不要开放整个群组
3. **定期检查**：看看白名单，把不用的去掉
4. **不要**：直接绑 `0.0.0.0` 暴露公网，不要放 CDN 后面不加认证
5. **更新**：关注 OpenClaw 安全更新

## 本章小结

- OpenClaw 安全模型：**默认拒绝，配对白名单**
- 不在白名单直接拒绝，根本不处理
- 开箱安全，默认配置就是安全的
- 远程访问推荐 SSH 隧道或者 Tailscale，不推荐直接暴露公网
- 工具权限也要最小化，敏感工具小心开

---

---

**系列目录**：
- [第一章：OpenClaw 是什么 —— 自托管个人 AI 助手的终极形态](./01-what-is-openclaw.md)
- [第二章：核心架构总览 —— Gateway 为什么是中心控制平面](./02-architecture-overview.md)
- [第三章：Gateway —— 核心网关服务到底做了什么](./03-gateway.md)
- [第四章：多渠道接入 —— 如何支持 25+ 聊天平台](./04-multi-channel-inbox.md)
- [第五章：ACP —— 如何对接外部 AI 客户端](./05-acp.md)
- [第六章：消息路由 —— 消息如何正确送到对的会话](./06-routing.md)
- 第七章：安全模型 —— 配对白名单如何保护你 👈 当前位置
- [第八章：为什么你需要一个多智能体框架 —— 单智能体的困境](./../02-multi-agent/08-why-you-need-multi-agent-framework.md) 👉 下一章
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
