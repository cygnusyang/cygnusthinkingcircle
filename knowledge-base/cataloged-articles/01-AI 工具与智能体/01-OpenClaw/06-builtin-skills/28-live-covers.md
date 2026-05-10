# 第二十八章：blogwatcher —— 博客与 RSS 更新监控

你关注了多少个技术博客？10 个？20 个？还是更多？

每天打开浏览器，逐个访问这些网站，看看有没有新文章发布，这听起来是不是很枯燥？更糟糕的是，你可能会错过那些真正重要的更新——因为谁有时间和耐心每天检查几十个网站呢？

RSS 订阅确实是个解决方案，但传统的 RSS 阅读器往往功能有限，要么不支持智能过滤，要么无法与你的工作流无缝集成。你想要的是一个能够：
- 自动监控你关注的博客和 RSS feeds
- 实时检测新文章发布
- 智能管理阅读状态
- 与你的日常工作环境无缝衔接

这样的工具存在吗？

OpenClaw 内置的 `blogwatcher` skill 就是为此而生的。

## blogwatcher 是什么

当前内置 `blogwatcher` skill 的描述很直接：

> 使用 `blogwatcher` CLI 监控博客和 RSS/Atom feed 的更新。

这说明它的能力边界是：

- 跟踪 feed / 博客
- 扫描更新
- 管理文章阅读状态

## 依赖是什么

`blogwatcher` skill 当前通过 `metadata.openclaw.requires.bins` 要求本机存在：

```text
blogwatcher
```

文档里给的安装方式是：

```bash
go install github.com/Hyaxia/blogwatcher/cmd/blogwatcher@latest
```

## 当前 skill 里写明的常用命令

官方 skill 文本列出的常用操作包括：

```bash
blogwatcher add "My Blog" https://example.com
blogwatcher blogs
blogwatcher scan
blogwatcher articles
blogwatcher read 1
blogwatcher read-all
blogwatcher remove "My Blog"
```

这就是当前工程里“博客更新监控”能力的真实接口。

## 它适合干什么

最适合的场景是：

- 追博客更新
- 跟 RSS/Atom feed
- 周期性扫描新文章
- 把文章标记为已读/未读

如果要做更复杂的"摘要工作流"，可以由智能体和其他工具组合实现。

## 本章小结

- `blogwatcher` 是一个用于监控博客和 RSS/Atom feed 更新的内置 skill
- 它依赖本地 `blogwatcher` CLI，主要做 feed/blog 跟踪、扫描和阅读状态管理
- 适合追博客更新、跟 RSS/Atom feed、周期性扫描新文章等场景

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
- 第二十八章：blogwatcher —— 博客与 RSS 更新监控 👈 当前位置
- [第二十九章：gh-issues —— GitHub Issues 自动修复编排](./29-gh-issues.md) 👉 下一章
- [第三十章：coding-agent —— 调用外部编码代理](./30-coding-agent.md)
- [第三十一章：模型故障转移 (Model Failover) —— 如何提高可用性](./../07-ops-best-practices/31-failover.md)
- [第三十二章：调试技巧 —— 如何排查 OpenClaw 问题](./../07-ops-best-practices/32-debugging.md)
- [第三十三章：成本优化 —— 如何用模型分级降低总成本](./../07-ops-best-practices/33-cost-optimization.md)
- [第三十四章：部署运维 —— OpenClaw 网关生产环境最佳实践](./../07-ops-best-practices/34-deployment.md)
