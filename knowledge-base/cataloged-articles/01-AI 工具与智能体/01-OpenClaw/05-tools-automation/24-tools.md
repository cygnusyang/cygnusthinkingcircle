# 第二十四章：工具系统 (Tools) —— OpenClaw 工具调用框架设计

OpenClaw 的工具体系是**按内置工具名、工具组和策略配置**来组织的。

## 当前工具系统的几个核心点

### 1. 工具是一级能力

当前官方文档明确列出的内置重点包括：

- 文件工具：`read`、`write`、`edit`、`apply_patch`
- 运行时工具：`exec`、`bash`、`process`
- 会话工具：`sessions_list`、`sessions_history`、`sessions_send`、`sessions_spawn`、`session_status`
- Web 工具：`web_search`、`web_fetch`
- UI 工具：`browser`、`canvas`
- 自动化工具：`cron`、`gateway`
- 其他：`message`、`nodes`

## 2. 现在强调的是工具策略，不是工具是否内置

当前配置里，最重要的是：

```json5
{
  tools: {
    profile: "coding",
    allow: ["group:fs", "browser"],
    deny: ["group:runtime"],
  },
}
```

其中：

- `profile`：先给一个基础工具集合
- `allow`：追加允许
- `deny`：拒绝优先

## 3. 工具组是当前文档的重要抽象

OpenClaw 现在提供 `group:*` 速记：

- `group:runtime`
- `group:fs`
- `group:sessions`
- `group:memory`
- `group:web`
- `group:ui`
- `group:automation`
- `group:messaging`
- `group:nodes`
- `group:openclaw`

## Tool profiles

当前官方文档列出的基础 profile 有：

- `minimal`
- `coding`
- `messaging`
- `full`

例如：

```json5
{
  tools: {
    profile: "messaging",
    allow: ["slack", "discord"],
  },
}
```

或者：

```json5
{
  tools: {
    profile: "coding",
    deny: ["group:runtime"],
  },
}
```

## 当前最常用的几类工具

### 文件与补丁

- `read`
- `write`
- `edit`
- `apply_patch`

### 进程执行

- `exec`
- `process`

这是当前官方支持的 shell 执行面，带有：

- `workdir`
- `timeout`
- `pty`
- `background`
- `host`
- `security`
- `ask`

### Web 访问

- `web_search`
- `web_fetch`

文档也强调了：

- `web_fetch` 是普通 HTTP 抓取，不执行 JS
- 需要 JS、登录态或页面交互时，应该切到 `browser`

### 会话编排

- `sessions_list`
- `sessions_history`
- `sessions_send`
- `sessions_spawn`
- `session_status`

这是当前 OpenClaw 多智能体和跨会话操作的基础层。

## 插件也可以加工具

- 核心工具先由 OpenClaw 提供
- 插件可以额外注册工具
- 插件工具和核心工具一起进入同一个工具策略体系

所以重点不在“插件工具是额外特例”，而在“最终都受 `tools.*` 策略控制”。

## `exec` 是现在的关键工具之一

当前官方 `Exec tool` 文档里，核心参数包括：

- `command`
- `workdir`
- `env`
- `yieldMs`
- `background`
- `timeout`
- `pty`
- `host`
- `security`
- `ask`
- `node`
- `elevated`

## `web_search` / `web_fetch` 的边界

当前官方文档明确：

- `web_search`：搜索网页
- `web_fetch`：抓静态内容并提取可读文本
- `browser`：JS-heavy、登录态、点击、输入、截图

## 本章小结

- OpenClaw 的工具体系按内置工具名、工具组和策略配置组织
- 真实的关键工具包括 `read/write/edit/apply_patch`、`exec/process`、`web_search/web_fetch`、`browser`、`sessions_spawn`
- 当前配置重点是 `tools.profile`、`tools.allow`、`tools.deny` 和 `group:*`
- 插件工具会并入同一个工具策略体系，而不是一套独立规则

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
- 第二十四章：工具系统 (Tools) —— OpenClaw 工具调用框架设计 👈 当前位置
- [第二十五章：内置浏览器 —— 网页抓取和交互](./25-browser.md) 👉 下一章
- [第二十六章：Cron 自动化 —— 定时任务自动化](./26-cron.md)
- [第二十七章：Onboarding —— 新手引导流程设计](./27-onboarding.md)
- [第二十八章：blogwatcher —— 博客与 RSS 更新监控](./../06-builtin-skills/28-live-covers.md)
- [第二十九章：gh-issues —— GitHub Issues 自动修复编排](./../06-builtin-skills/29-gh-issues.md)
- [第三十章：coding-agent —— 调用外部编码代理](./../06-builtin-skills/30-coding-agent.md)
- [第三十一章：模型故障转移 (Model Failover) —— 如何提高可用性](./../07-ops-best-practices/31-failover.md)
- [第三十二章：调试技巧 —— 如何排查 OpenClaw 问题](./../07-ops-best-practices/32-debugging.md)
- [第三十三章：成本优化 —— 如何用模型分级降低总成本](./../07-ops-best-practices/33-cost-optimization.md)
- [第三十四章：部署运维 —— OpenClaw 网关生产环境最佳实践](./../07-ops-best-practices/34-deployment.md)
