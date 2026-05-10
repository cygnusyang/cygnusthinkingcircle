# 第三十章：coding-agent —— 调用外部编码代理

面对一个复杂的新功能开发任务，你是否有过这样的经历：

- 需要深入理解整个代码库的结构和设计模式
- 要在多个文件之间来回切换，理解上下文关系
- 编写代码时需要不断查阅文档和参考实现
- 代码写完后还要进行全面的测试和 review

这些工作如果完全靠人工完成，不仅耗时耗力，还容易出错。你可能会想：如果有一个专业的编码助手能够帮我处理这些复杂的编码任务，那该多好？

现在市面上确实有很多优秀的编码工具——Codex、Claude Code、Pi、OpenCode 等等。但问题是，它们各自独立运行，无法与你的工作流无缝集成。你需要在不同的工具之间切换，打断你的开发节奏。

如果能够把这些强大的编码代理统一纳入你的工作流，让它们在你需要的时候自动介入，处理那些复杂的编码任务，那会是一种怎样的体验？

OpenClaw 内置的 `coding-agent` skill 就能帮你实现这一点。

## `coding-agent` 是什么

当前 `coding-agent` skill 的描述非常明确：

> 通过后台进程委托 Codex、Claude Code、Pi、OpenCode 这类编码代理处理复杂编码任务。

这说明它的本质不是“营销工作台”，而是**把外部编码代理纳入 OpenClaw 工作流**。

## 它什么时候适合用

skill 文本里列出的典型场景包括：

- 新功能开发
- PR review
- 大型重构
- 需要大量文件探索和迭代的编码任务

同时也明确写了不适合：

- 很小的一行修复
- 纯读代码问题
- 在 `~/clawd` 工作区里乱开代理

## 当前依赖

这个 skill 需要宿主机至少有一个可用编码代理二进制，例如：

- `claude`
- `codex`
- `opencode`
- `pi`

并且特别强调：

> 运行这类编码代理时要使用 `pty:true`

这和当前 exec / process 工具的 PTY 支持是严格对应的。

## 当前 skill 反映出的真实实践

`coding-agent` skill 里反复强调三件事：

1. 用 `bash` / `exec` 驱动外部编码代理
2. 长任务放后台执行
3. 通过 `process` 轮询、写入、终止会话

这与当前 OpenClaw 的工具面完全对齐：

- `exec`
- `process`
- `pty`
- `background`

## 本章小结

- `coding-agent` 是一个用于调用外部编码代理处理复杂编码任务的内置 skill
- 它用于把 Codex、Claude Code、Pi、OpenCode 等编码代理纳入 OpenClaw 编排
- 它和当前 `exec` / `process` / PTY / 后台任务模型完全一致
- 适合新功能开发、PR review、大型重构等复杂编码任务

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
- [第二十八章：blogwatcher —— 博客与 RSS 更新监控](./28-live-covers.md)
- [第二十九章：gh-issues —— GitHub Issues 自动修复编排](./29-gh-issues.md)
- 第三十章：coding-agent —— 调用外部编码代理 👈 当前位置
- [第三十一章：模型故障转移 (Model Failover) —— 如何提高可用性](./../07-ops-best-practices/31-failover.md) 👉 下一章
- [第三十二章：调试技巧 —— 如何排查 OpenClaw 问题](./../07-ops-best-practices/32-debugging.md)
- [第三十三章：成本优化 —— 如何用模型分级降低总成本](./../07-ops-best-practices/33-cost-optimization.md)
- [第三十四章：部署运维 —— OpenClaw 网关生产环境最佳实践](./../07-ops-best-practices/34-deployment.md)
