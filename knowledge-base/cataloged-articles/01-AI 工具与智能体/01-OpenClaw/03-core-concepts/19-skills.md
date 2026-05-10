# 第十九章：skills —— 技能系统核心概念与开发指南

当前 OpenClaw 的 Skills 采用 **AgentSkills 风格的目录 + `SKILL.md`** 方案。

这一章按当前工程里的真实结构来讲。

## 什么是 Skill

在当前 OpenClaw 里，一个 Skill 本质上是：

> 一个目录，目录里至少有一个带 YAML frontmatter 的 `SKILL.md`，用来教智能体在什么条件下、如何使用某组工具或外部能力。

所以 Skill 更接近“可加载的能力说明包”，而不是早期设想里的“内建工作流 DSL”。

## 最小结构

最小可用 Skill 目录可以非常简单：

```text
my-skill/
└── SKILL.md
```

最小 frontmatter 例子：

```markdown
---
name: my-skill
description: Do one thing well.
---
```

正文里再写清楚：

- 什么时候该触发这个 skill
- 依赖哪些命令或环境变量
- 推荐怎么调用
- 常见命令例子是什么

## 当前加载位置和优先级

官方文档给出的加载来源有三个主层级：

1. 内置 skills
2. `~/.openclaw/skills`
3. `<workspace>/skills`

优先级是：

```text
<workspace>/skills > ~/.openclaw/skills > 内置 skills
```

此外还可以通过：

```text
skills.load.extraDirs
```

补充额外目录。

这点很重要，因为当前 skill 的“安装”本质上就是把 skill 目录放进 OpenClaw 会扫描的位置。

## 当前真正的文件格式

当前核心文件是 `SKILL.md`，并且 frontmatter 支持这些重要键：

- `name`
- `description`
- `homepage`
- `user-invocable`
- `disable-model-invocation`
- `command-dispatch`
- `command-tool`
- `command-arg-mode`
- `metadata`

其中 `metadata` 需要是**单行 JSON 对象**，这是当前解析器的约束。

## metadata 门控是当前重点

现在的 skill 不是“装上就一律可见”，而是会在加载阶段按 `metadata.openclaw` 过滤。

文档里的典型写法：

```markdown
---
name: nano-banana-pro
description: Generate or edit images via Gemini 3 Pro Image
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["uv"], "env": ["GEMINI_API_KEY"], "config": ["browser.enabled"] },
        "primaryEnv": "GEMINI_API_KEY",
      },
  }
---
```

当前常见门控字段包括：

- `requires.bins`
- `requires.anyBins`
- `requires.env`
- `requires.config`
- `primaryEnv`
- `os`
- `always`
- `install`

这才是现在 skills 系统的核心，不是旧 DSL。

## 一个更贴近当前源码的 Skill 例子

```markdown
---
name: blogwatcher
description: Monitor blogs and RSS/Atom feeds for updates using the blogwatcher CLI.
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["blogwatcher"] },
        "install":
          [
            {
              "id": "go",
              "kind": "go",
              "module": "github.com/Hyaxia/blogwatcher/cmd/blogwatcher@latest",
              "bins": ["blogwatcher"],
              "label": "Install blogwatcher (go)",
            },
          ],
      },
  }
---

# blogwatcher

Track blog and RSS/Atom feed updates with the `blogwatcher` CLI.

- Add a blog: `blogwatcher add "My Blog" https://example.com`
- Scan for updates: `blogwatcher scan`
- List articles: `blogwatcher articles`
```

这个例子体现了当前 skills 的真实风格：

- 不是定义一个内部工作流引擎
- 而是告诉 agent：这个能力何时可用、依赖什么、推荐怎么用

## 配置覆盖怎么做

当前配置文件里，skills 的覆盖入口在：

```text
skills.entries.<name>
```

例如：

```json5
{
  skills: {
    entries: {
      "nano-banana-pro": {
        enabled: true,
        apiKey: "GEMINI_KEY_HERE",
        env: {
          GEMINI_API_KEY: "GEMINI_KEY_HERE",
        },
        config: {
          model: "nano-pro",
        },
      },
      peekaboo: { enabled: true },
      sag: { enabled: false },
    },
  },
}
```

规则很清楚：

- `enabled: false` 可禁用 skill
- `env` 和 `apiKey` 在 agent run 生命周期内注入
- 自定义字段放到 `config`

## 会话快照和热更新

当前文档特别强调了一点：skills 列表通常在**会话开始时快照**。

这意味着：

- 你改了 skill 文件
- 当前会话不一定立刻看到变化
- 新开会话时一定会重新评估

如果开启 watcher，也可能在会话中热刷新，但不应该把它当成唯一刷新机制。

## 当前 CLI 命令

和旧稿不同，OpenClaw 当前 CLI 里稳定的 skills 命令主要是：

```bash
openclaw skills list
openclaw skills info <name>
openclaw skills check
```

安装、搜索、更新、发布技能，现在主要走 **ClawHub**。

## 开发一个 skill 的正确姿势

### 第一步：先写 `SKILL.md`

把最核心的四件事讲明白：

1. 什么时候触发
2. 依赖什么
3. 常用命令怎么写
4. 有什么限制

### 第二步：用 `metadata.openclaw.requires` 做门控

不要让一个缺依赖的 skill 永远出现在 prompt 里。

### 第三步：把资源文件放在同目录

当前官方模型允许 skill 目录里带辅助文件、脚本和资源，但主入口仍然是 `SKILL.md`。

### 第四步：用 `openclaw skills check` 验证

先检查依赖和可见性，再开始调试。

## Skill 和插件的关系

当前源码支持插件通过 `openclaw.plugin.json` 暴露自己的 skills 目录。也就是说：

- 插件可以带工具
- 也可以顺带带 skill

所以 skill 是“如何使用能力”的说明层，插件是“把能力接进系统”的扩展层。两者可以独立，也可以一起出现。

## 本章小结

- 当前 OpenClaw skill 的标准入口是 `SKILL.md`
- skills 从内置目录、`~/.openclaw/skills` 和 `<workspace>/skills` 加载
- `metadata.openclaw` 门控是当前系统的重点能力
- `skills.entries.*` 用于启用、注入 env/apiKey 和传入配置
- 安装和发布工作流现在主要走 ClawHub

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
- [第十五章：providers —— 各大模型提供者配置大全](./15-providers.md)
- [第十六章：plugins —— 插件系统开发指南](./16-plugins.md)
- [第十七章： refactor —— OpenClaw 重构原则与工作流](./17-refactor.md)
- [第十八章：reference —— 完整配置、模板、CLI 命令参考](./18-reference.md)
- 第十九章：skills —— 技能系统核心概念与开发指南 👈 当前位置
- [第二十章：ClawHub —— 技能市场如何分享和获取技能](./20-clawhub.md) 👉 下一章
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
