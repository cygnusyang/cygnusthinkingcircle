# 第二十三章：WebChat —— Gateway WebSocket 聊天界面

当前官方文档里，WebChat 的定位是：

> 它是一个直接连 Gateway WebSocket 的聊天 UI，不是独立的一套 Web 服务器产品。

## 当前 WebChat 是什么

官方文档给出的定义是：

- WebChat 使用 Gateway 的 WebSocket 接口通信
- 历史记录从 Gateway 获取
- 路由仍然遵循现有 agent / session 规则
- Gateway 不可达时，WebChat 会退成只读

所以它不是“一套单独 session 模型”，也不是“一套单独配置命名空间”。

## 关键行为

当前文档列出的核心行为包括：

- UI 通过 Gateway WebSocket 连接
- 使用 `chat.history`、`chat.send` 和 `chat.inject`
- `chat.inject` 可以直接把助手注释追加到 transcript
- 回复仍然确定性地回到 WebChat

## 和其他渠道的关系

WebChat 不是特殊渠道分支，而是附着在已有 agent/session 体系上。

这意味着：

- 会话规则和消息渠道保持一致
- 不是一套新的旧式 scope 配置
- 默认更接近所选 agent 的主会话

## 当前配置怎么看

当前官方文档明确写了：

> **没有专用的 `webchat.*` 块。**

WebChat 使用的是 Gateway 的公共配置，例如：

- `gateway.port`
- `gateway.bind`
- `gateway.auth.mode`
- `gateway.auth.token`
- `gateway.auth.password`
- `gateway.remote.url`
- `gateway.remote.token`
- `gateway.remote.password`
- `session.*`

所以像下面这些旧配置都不应该再当成官方接口写：

- `webchat.enabled`
- `webchat.bind`
- `webchat.port`
- `webchat.auth`
- 单独主题文件路径

## 当前的理解方式

你可以把 WebChat 想成：

- 一个前端 UI
- 通过 Gateway WebSocket 和 OpenClaw 通信
- 认证、路由、会话都复用 Gateway 现有能力

而不是“Gateway 里又嵌了一个完整 Web 应用产品”。

## 远程使用方式

当前文档提到的远程方案是：

- SSH 隧道
- Tailscale 隧道

这进一步说明 WebChat 仍然围绕 Gateway 自身在工作，而不是要求你单独部署一个 WebChat server。

## 现在应该怎么写部署与访问

更准确的表述是：

1. 启动 Gateway
2. 配好 Gateway 认证
3. WebChat UI 连接到 Gateway WebSocket
4. 如需远程访问，用 SSH 或 Tailscale 把 Gateway 暴露到可信环境

## 本章小结

- 当前 WebChat 是连接 Gateway WebSocket 的聊天 UI
- 它复用 Gateway 的会话、路由和认证，不再有官方 `webchat.*` 独立配置块
- 远程访问主要通过 Gateway 的远程连接方式完成

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
- [第二十一章：Canvas A2UI —— 实时可视化协作 workspace](./21-canvas.md)
- [第二十二章：语音唤醒 (Voice Wake) —— 语音交互体验](./22-voice-wake.md)
- 第二十三章：WebChat —— Gateway WebSocket 聊天界面 👈 当前位置
- [第二十四章：工具系统 (Tools) —— OpenClaw 工具调用框架设计](./../05-tools-automation/24-tools.md) 👉 下一章
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
