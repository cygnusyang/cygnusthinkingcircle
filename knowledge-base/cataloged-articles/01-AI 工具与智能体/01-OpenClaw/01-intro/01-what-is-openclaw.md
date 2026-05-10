# 第一章：OpenClaw 是什么 —— 自托管个人 AI 助手的终极形态

你有没有想过：拥有一个**完全属于你自己**的 AI 助手，它可以：

- 在你所有常用的聊天平台（WhatsApp/Telegram/Discord/iMessage）上工作
- 本地运行，你的数据不会离开你的设备
- 支持多个 AI 模型，你可以自由切换 Anthropic/OpenAI/Google 等等
- 内置浏览器自动化，可以帮你自动浏览网页
- 支持定时任务，定期帮你收集信息
- 多智能体协作，让多个专家 AI 一起帮你解决复杂问题
- 开放技能市场，你可以随时安装新技能

这就是 **OpenClaw**。

## OpenClaw 定义

OpenClaw 是一个**开源自托管个人 AI 助手网关**，它帮你把 AI 能力接入到你日常使用的聊天平台，让 AI 随时随地陪伴你。

> "Multi-channel AI gateway with extensible messaging integrations" —— GitHub 官方定义

简单说：

- **网关**：中心服务，连接 AI 模型和聊天渠道
- **自托管**：你自己部署，数据完全在你控制之下
- **多渠道**：同一个 AI 助手，在 WhatsApp/Telegram/Discord/iMessage 都能用
- **可扩展**：通过技能和插件，随时增加新能力

## 核心架构

OpenClaw 采用中心网关架构：

```mermaid
%%{init: {'theme':'base','themeVariables': {'primaryColor':'#f1f5f9','primaryBorderColor':'#0f4c81','primaryTextColor':'#0f172a','secondaryColor':'#f1f5f9','secondaryBorderColor':'#0f4c81','secondaryTextColor':'#0f172a','tertiaryColor':'#fbbf24','tertiaryBorderColor':'#fbbf24','tertiaryTextColor':'#0f172a','background':'#f8fafc','fontFamily':'Inter, system-ui, sans-serif','fontSize':'14px','textColor':'#0f172a','lineColor':'#334155','edgeLabelBackground':'#ffffff','actorBorderColor':'#0f4c81','actorTextColor':'#0f172a','actorFill':'#f1f5f9'}}}%%
graph TD
  G[Gateway<br/>中心控制平面 ws://127.0.0.1:18789]
  G --> C1[Chat Channel<br/>WhatsApp/Telegram/Discord]
  G --> C2[CLI<br/>命令行工具]
  G --> C3[WebChat UI<br/>网页界面]
  G --> C4[Native Clients<br/>macOS/iOS/Android]
  G --> C5[Pi Agent Runtime<br/>树莓派运行时]
```

所有组件都连接到中心 Gateway，Gateway 负责：

1. 接收来自各个渠道的用户消息
2. 路由给对应的 AI 会话处理
3. 调用 AI 模型
4. 把结果返回给用户

## 关键特性

让我们来看 OpenClaw 最重要的特性：

### 1. 25+ 消息平台支持

OpenClaw 开箱即用支持 **25+ 聊天平台**：

- 大平台：WhatsApp, Telegram, Discord, Slack, iMessage, Signal
- 其他：Matrix, Mastodon, Twitch, Line, 飞书等等

你不用换聊天软件，继续用你每天都用的那个，OpenClaw 直接接进去。

### 2. 本地优先，远程可访问

- Gateway 运行在你自己的服务器或者电脑上
- 默认本地访问，数据不出去
- 需要远程访问的时候，可以通过 Tailscale 或者 SSH 隧道暴露
- 完全你掌控

### 3. 多智能体协作原生支持

这是 OpenClaw 最核心的能力之一：

- `sessions_spawn` 核心原语，一键生成隔离子智能体
- 支持多种协作架构：Master-Worker, Hub-and-Spoke, Pipeline
- 深度限制防止上下文漂移
- 自动结果回传，不用你管

我们这个系列后面会专门讲这个。

### 4. 语音唤醒与语音交互

- macOS 支持语音唤醒，说一声"Open Claw"就能唤醒
- 语音输入语音输出
- 完全本地，不用云

### 5. Live Canvas A2UI

实时可视化协作工作区，AI 可以直接在画布上画图、排版，你可以实时看到进度。

### 6. 内置工具开箱即用

- **浏览器控制**：AI 可以帮你自动浏览网页、抓取内容
- **Cron 自动化**：定时任务，比如每天早上给你汇总新闻
- **文件读写**：读写本地文件
- **技能市场 ClawHub**：分享和获取社区技能

### 7. 安全模型

- 配对白名单：只有允许的发送者才能访问你的 AI
- DM 安全策略：阻止未认证发送者
- 所有数据你自己掌控，不会上传到第三方云

### 8. 模型故障转移

配置多个模型，一个失败了自动切到下一个，可用性更高。

## 谁适合用 OpenClaw

✅ **适合你如果**：

- 你想要一个**完全属于自己**的 AI 助手，不想把数据给大厂
- 你经常在聊天平台，想要 AI 就在聊天窗口里面
- 你需要处理复杂任务，想要多个 AI 专家分工协作
- 你想要自定义扩展，开发自己的技能

❌ **可能不适合**：

- 你想要开箱即用的 SaaS 服务，不想自己部署
- 你只需要简单的聊天，不需要多智能体协作

## OpenClaw 和其他 AI 助手有什么不一样

| 维度 | OpenClaw | ChatGPT APP | Claude.ai | 其他 self-hosted 框架 |
|------|----------|------------|-----------|----------------------|
| 自托管 | ✅ | ❌ | ❌ | ⚠️ 部分支持 |
| 多渠道接入 | ✅ 25+ | ❌ 单 APP | ❌ 单 APP | ❌ 一般只支持单渠道 |
| 原生多智能体 | ✅ | ⚠️ 有限 | ⚠️ 有限 | ❌ 很少原生支持 |
| 技能扩展 | ✅ 市场 | ❌ | ❌ | ⚠️ 需要自己写 |
| 语音唤醒 | ✅ | ✅ | ✅ | ❌ |

## 文档导航

OpenClaw 官方文档结构：

| 文档 | 内容 |
|------|------|
| **入门导航** | `onboarding` 引导你完成设置 |
| **平台指南** | Windows (WSL2), Linux, macOS, iOS, Android 各平台安装 |
| **架构** | Gateway + 协议模型架构概述 |
| **配置参考** | 完整配置键参考 |
| **操作手册** | Gateway 运行维护 |
| **远程访问** | SSH 隧道 / Tailscale 配置 |
| **故障排查** | 常见问题调试 |
| **安全指南** | 暴露服务前必读 |

你看完这个系列，就能对照官方文档，部署一个自己用的 OpenClaw，并且理解背后的设计原理。

## 本章小结

- OpenClaw 是**自托管个人 AI 助手网关**，让 AI 能力接入你日常聊天平台
- 中心 Gateway 连接各个渠道和 AI 运行时
- 核心特性：25+ 渠道支持、原生多智能体协作、本地优先、可扩展技能
- 接下来我们讲解核心架构，Gateway 为什么是中心控制平面

---

---

**系列目录**：
- 第一章：OpenClaw 是什么 —— 自托管个人 AI 助手的终极形态 👈 当前位置
- [第二章：核心架构总览 —— Gateway 为什么是中心控制平面](./02-architecture-overview.md) 👉 下一章
- [第三章：Gateway —— 核心网关服务到底做了什么](./03-gateway.md)
- [第四章：多渠道接入 —— 如何支持 25+ 聊天平台](./04-multi-channel-inbox.md)
- [第五章：ACP —— 如何对接外部 AI 客户端](./05-acp.md)
- [第六章：消息路由 —— 消息如何正确送到对的会话](./06-routing.md)
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
