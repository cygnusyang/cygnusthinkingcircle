# 第二十五章：内置浏览器 —— 网页抓取和交互

当前 OpenClaw 的浏览器能力由 **Browser (openclaw-managed)**、`chrome` extension relay，以及 agent 侧 `browser` 工具 / `openclaw browser` CLI 组成，核心配置块在：

```text
browser
```

不是插件配置块。

## 当前浏览器能力是什么

按当前官方文档，可以概括为：

OpenClaw 可以运行一个由 agent 控制的独立 Chrome/Brave/Edge/Chromium profile。`openclaw` profile 是隔离的托管浏览器；默认 `chrome` profile 则通过 extension relay 控制用户手动 attach 的现有浏览器标签页。

这个能力有两种主要模式：

- `openclaw` profile：受 OpenClaw 管理的隔离浏览器
- `chrome` profile：通过 Chrome extension relay 接管你现有浏览器标签页

## 当前配置写法

配置文件位置仍然是：

```text
~/.openclaw/openclaw.json
```

浏览器配置示例：

```json5
{
  browser: {
    enabled: true,
    defaultProfile: "chrome",
    color: "#FF4500",
    headless: false,
    noSandbox: false,
    attachOnly: false,
    executablePath: "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    profiles: {
      openclaw: { cdpPort: 18800, color: "#FF4500" },
      work: { cdpPort: 18801, color: "#0066CC" },
      remote: { cdpUrl: "http://10.0.0.42:9222", color: "#00AA00" },
    },
    ssrfPolicy: {
      dangerouslyAllowPrivateNetwork: true,
    },
  },
}
```

## 当前 CLI 命令

官方 CLI 文档给出的常用命令是：

```bash
openclaw browser status
openclaw browser start
openclaw browser stop
openclaw browser reset-profile
openclaw browser profiles
openclaw browser create-profile --name work --color "#FF5A36"
openclaw browser delete-profile --name work
openclaw browser open https://example.com
openclaw browser tabs
openclaw browser focus <targetId>
openclaw browser close <targetId>
openclaw browser snapshot
openclaw browser screenshot
openclaw browser navigate https://example.com
openclaw browser resize 1280 720
openclaw browser click <ref>
openclaw browser type <ref> "hello"
openclaw browser press Enter
openclaw browser hover <ref>
openclaw browser drag <startRef> <endRef>
openclaw browser select <ref> <values...>
openclaw browser upload <paths...> --ref <ref>
openclaw browser download <ref> report.pdf
openclaw browser waitfordownload report.pdf
openclaw browser fill --fields '{"email":"me@example.com"}'
openclaw browser dialog --accept
openclaw browser wait --text "Done"
openclaw browser evaluate --fn "() => document.title"
openclaw browser console
openclaw browser pdf
openclaw browser highlight <ref>
```

## `openclaw` 和 `chrome` 两个 profile

### `openclaw`

这是 OpenClaw 自己管理的隔离浏览器：

- 独立 user data dir
- 独立 CDP 端口
- 不碰你的日常浏览器配置

### `chrome`

这是通过 Chrome extension relay 接到你现有 Chromium 浏览器标签页：

- 需要安装扩展
- 需要手动 attach 标签页
- 更像“借用你当前浏览器”

## 当前功能边界

浏览器能力现在主要覆盖：

- 标签页管理
- 页面 snapshot / 页面结构检查
- 截图
- PDF 导出
- 导航
- 点击
- 输入
- hover / drag / select / upload / download / press
- wait / evaluate / console / highlight
- cookies / storage / network / download / state 设置等调试能力

但官方文档并没有把这些能力对外命名成那组旧式动作接口：

- `browser_navigate`
- `browser_snapshot`
- `browser_click`
- `browser_type`
- `browser_select`
- `browser_back`
- `browser_forward`

所以博客里不应该继续把这些当成当前官方工具名。

## 远程浏览器与 node host

当前工程支持：

- 本地浏览器控制
- 远程 CDP
- node host 代理浏览器操作

这意味着 Gateway 不一定要和浏览器跑在同一台机器上。

如果浏览器在另一台机器上，OpenClaw 推荐的方向是：

- node host 浏览器代理
- 或远程 CDP profile

## SSRF 策略是当前安全重点

浏览器安全在当前工程里不是“allowDomains / blockedDomains 这种旧插件配置”为主，而是：

```text
browser.ssrfPolicy
```

例如：

```json5
{
  browser: {
    ssrfPolicy: {
      dangerouslyAllowPrivateNetwork: false,
    },
  },
}
```

官方文档还特别说明：

- 当前默认是 trusted-network model
- 可以改成严格 public-only 浏览

所以博客里最应该强调的是 SSRF guard，而不是旧式插件白名单。

## 安装扩展和接管现有 Chrome

如果你要走 `chrome` relay 模式，官方 CLI 提供：

```bash
openclaw browser extension install
openclaw browser extension path
```

然后再到 `chrome://extensions` 里启用开发者模式并加载该扩展目录。

这是当前正式文档里的浏览器接管方式。

## 本章小结

- 当前浏览器配置在 `browser` 块，不在 `plugins.entries.browser`
- 真实命令面是 `openclaw browser ...`，覆盖 profile、标签页、snapshot、screenshot、navigate、click、type、press、hover、drag、select、upload、download、wait、evaluate、console、pdf、highlight 等
- 核心 profile 是 `openclaw` 和 `chrome`
- 当前安全重点是 `browser.ssrfPolicy`

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
- [第二十四章：工具系统 (Tools) —— OpenClaw 工具调用框架设计](./24-tools.md)
- 第二十五章：内置浏览器 —— 网页抓取和交互 👈 当前位置
- [第二十六章：Cron 自动化 —— 定时任务自动化](./26-cron.md) 👉 下一章
- [第二十七章：Onboarding —— 新手引导流程设计](./27-onboarding.md)
- [第二十八章：blogwatcher —— 博客与 RSS 更新监控](./../06-builtin-skills/28-live-covers.md)
- [第二十九章：gh-issues —— GitHub Issues 自动修复编排](./../06-builtin-skills/29-gh-issues.md)
- [第三十章：coding-agent —— 调用外部编码代理](./../06-builtin-skills/30-coding-agent.md)
- [第三十一章：模型故障转移 (Model Failover) —— 如何提高可用性](./../07-ops-best-practices/31-failover.md)
- [第三十二章：调试技巧 —— 如何排查 OpenClaw 问题](./../07-ops-best-practices/32-debugging.md)
- [第三十三章：成本优化 —— 如何用模型分级降低总成本](./../07-ops-best-practices/33-cost-optimization.md)
- [第三十四章：部署运维 —— OpenClaw 网关生产环境最佳实践](./../07-ops-best-practices/34-deployment.md)
