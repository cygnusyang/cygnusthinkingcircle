# 第二十章：ClawHub —— 技能市场如何分享和获取技能

ClawHub 在当前 OpenClaw 里不是“一个 GitHub 索引仓库的别名”，而是官方 Skills 注册中心和对应的 CLI 工作流。

如果你要搜索、安装、更新、发布 Skills，当前工程的正确入口是 **`clawhub`**。

网站：

```text
https://clawhub.com
```

## ClawHub 是什么

官方文档对它的定位很明确：

- 它是 OpenClaw 的公共 Skills 注册中心
- Skills 的发布单位是一个包含 `SKILL.md` 的文件夹
- 你既可以在网页里浏览，也可以用 CLI 搜索、安装、更新、发布

## 当前推荐的安装方式

### 安装 CLI

```bash
npm i -g clawhub
```

或者：

```bash
pnpm add -g clawhub
```

### 搜索 skill

```bash
clawhub search "calendar"
```

### 安装 skill

```bash
clawhub install <skill-slug>
```

默认情况下，ClawHub 会把 skill 装到当前工作目录下的 `./skills`，如果存在 OpenClaw 工作区配置，也会回退到那个工作区。

这正好和当前 OpenClaw 的 `<workspace>/skills` 加载机制对上。

## 当前常用命令

### 搜索

```bash
clawhub search "postgres backups"
```

### 安装

```bash
clawhub install my-skill-pack
```

常见参数：

- `--version <version>`
- `--force`

### 更新

```bash
clawhub update <slug>
clawhub update --all
```

### 查看已安装列表

```bash
clawhub list
```

### 发布

```bash
clawhub publish ./my-skill --slug my-skill --name "My Skill" --version 1.0.0 --tags latest
```

### 同步本地 skills

```bash
clawhub sync --all
```

这一套命令才是当前项目文档里的正式分发链路。

## ClawHub 和 OpenClaw 的衔接方式

流程其实很直白：

1. 你用 `clawhub install` 把 skill 安到工作区 `skills/`
2. OpenClaw 在下一个会话里扫描 `<workspace>/skills`
3. Skill 出现在可用 skills 列表里

也就是说，ClawHub 并不替代 OpenClaw 的 skill loader；它负责的是**分发和同步**。

## 发布一个 skill 的当前正确姿势

### 第一步：先准备好 skill 文件夹

核心要求是：

- 目录里有 `SKILL.md`
- frontmatter 合法
- 描述清楚依赖和使用方式

### 第二步：发布

```bash
clawhub publish ./my-skill \
  --slug my-skill \
  --name "My Skill" \
  --version 1.0.0 \
  --tags latest
```

### 第三步：持续同步

如果你在本地维护多个 skill，可以直接：

```bash
clawhub sync --all
```

## 当前 CLI 里的重要选项

官方文档列出的全局参数包括：

- `--workdir <dir>`
- `--dir <dir>`
- `--site <url>`
- `--registry <url>`
- `--no-input`

认证相关命令：

```bash
clawhub login
clawhub login --token <token>
clawhub logout
clawhub whoami
```

这说明当前 ClawHub 已经是完整的 registry + CLI 体系，不是单纯静态索引。

## 本地状态保存在哪里

当前文档提到两个本地状态文件：

- 已安装技能锁文件：`.clawhub/lock.json`
- CLI 认证/配置文件：可通过 `CLAWHUB_CONFIG_PATH` 覆盖

这也是为什么 `clawhub update --all` 能知道你本地装过哪些东西。

## 环境变量

当前 ClawHub 文档列出的常用环境变量包括：

- `CLAWHUB_SITE`
- `CLAWHUB_REGISTRY`
- `CLAWHUB_CONFIG_PATH`
- `CLAWHUB_WORKDIR`
- `CLAWHUB_DISABLE_TELEMETRY=1`

## 和旧文档最大差别

当前正确表述应该是：

- skills 本体是 `SKILL.md` 目录
- 安装、更新、发布用 `clawhub`
- OpenClaw 只负责从 `skills/` 目录加载它们

## 本章小结

- ClawHub 是当前 OpenClaw 的官方 Skills 注册中心
- 搜索、安装、更新、发布的主命令是 `clawhub ...`
- Skills 的发布单位是一个包含 `SKILL.md` 的目录
- 安装后通常落在工作区 `skills/`，由 OpenClaw 在后续会话中加载

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
- [第十九章：skills —— 技能系统核心概念与开发指南](./19-skills.md)
- 第二十章：ClawHub —— 技能市场如何分享和获取技能 👈 当前位置
- [第二十一章：Canvas A2UI —— 实时可视化协作 workspace](./../04-client-ux/21-canvas.md) 👉 下一章
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
