# 第二章：安装与上手 —— 从 curl 到第一个命令

10 分钟后你就能让 AI 帮你提交代码。但在那之前，先把环境搞定。

## 前置条件

### 必需

- **Node.js 18+**：Claude Code 基于 Node.js 运行
- **Anthropic 账号**：需要有 API 访问权限或 Claude Pro/Max 订阅

### 推荐

- **Git**：版本控制集成需要
- **GitHub CLI（gh）**：PR 工作流需要

## 安装方式

### macOS / Linux（推荐）

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

这是官方推荐的安装方式，一条命令搞定。

### Homebrew（macOS / Linux）

```bash
brew install --cask claude-code
```

### Windows（推荐）

```powershell
irm https://claude.ai/install.ps1 | iex
```

### WinGet（Windows）

```powershell
winget install Anthropic.ClaudeCode
```

### npm（已弃用）

```bash
npm install -g @anthropic-ai/claude-code
```

> **注意**：npm 安装方式已被官方标记为 deprecated，建议使用上面的原生安装方式。

源码 README 中的原始说明：

> "Installation via npm is deprecated. Use one of the recommended methods below."

## 认证

首次运行需要认证。Claude Code 支持两种认证方式：

1. **Claude Pro/Max 订阅**：浏览器登录，OAuth 认证
2. **API Key**：设置 `ANTHROPIC_API_KEY` 环境变量

```bash
# 使用 API Key
export ANTHROPIC_API_KEY=sk-ant-xxxxx
claude
```

## 第一个命令

安装完成后，进入你的项目目录：

```bash
cd your-project
claude
```

你会看到 Claude Code 的交互界面：

```
╭─────────────────────────────────────╮
│  Claude Code                         │
│  Agentic coding tool by Anthropic    │
╜─────────────────────────────────────╯

>
```

试试第一个指令：

```
> 这个项目是做什么的？
```

Claude Code 会自动读取项目文件（README、package.json、源代码等），理解项目结构后给你回答。

再试一个：

```
> 帮我找到所有 TODO 注释
```

它会用 Grep 工具搜索整个代码库，列出所有 TODO。

## 5 分钟快速成就感

安装完了，别急着学高级功能。先跟着做这三步，感受 Claude Code 的能力边界：

```
第 1 步：让 AI 读懂你的项目
> 这个项目的目录结构是什么？核心模块有哪些？

第 2 步：让 AI 帮你干活
> 找到所有 console.log 调试语句，列出来

第 3 步：让 AI 操作 Git
> 帮我把当前的改动提交了
```

这三步覆盖了 Claude Code 的三个核心能力：**理解代码库 → 执行搜索任务 → 操作工具**。之后你遇到任何编码工作，都可以想想：这能不能让 AI 做第一步？

## 内置斜杠命令

Claude Code 自带一些有用的斜杠命令：

| 命令 | 作用 |
|------|------|
| `/help` | 查看所有可用命令 |
| `/bug` | 报告 bug |
| `/config` | 查看和修改配置 |
| `/mcp` | 查看 MCP 服务器状态 |
| `/hooks` | 查看已加载的钩子 |
| `/compact` | 压缩上下文 |
| `/clear` | 清空对话 |

## IDE 集成

### VS Code

Claude Code 有官方 VS Code 扩展：

1. 在 VS Code 扩展市场搜索 "Claude Code"
2. 安装后侧边栏会出现 Claude 面板
3. 可以直接在 IDE 里和 AI 对话

优势：AI 能直接看到你打开的文件、光标位置，上下文更精准。

### JetBrains

类似 VS Code，在 JetBrains 插件市场安装即可。

## 命令行选项

Claude Code 支持多种启动方式：

```bash
# 交互模式（默认）
claude

# 单次命令模式
claude "帮我写一个单元测试"

# 从 stdin 读取
echo "解释这个函数" | claude

# 指定模型
claude --model claude-sonnet-4-6

# 调试模式（查看工具调用细节）
claude --debug

# 加载插件目录
claude --plugin-dir /path/to/plugin

# 快速模式（Claude Opus 4.6 加速输出）
claude --fast
```

## 项目配置

在项目根目录创建 `.claude/` 目录来自定义行为：

```bash
mkdir -p .claude/commands    # 项目级斜杠命令
```

### CLAUDE.md

`.claude/CLAUDE.md` 是项目的 AI 上下文文件，Claude Code 启动时自动加载：

```markdown
# 项目约定

- 使用 TypeScript strict 模式
- 测试覆盖率 80%+
- 提交信息遵循 conventional commits
- 所有 API 需要 rate limiting
```

### 自定义命令

在 `.claude/commands/` 下创建 `.md` 文件就是自定义斜杠命令：

```markdown
<!-- .claude/commands/review.md -->
---
description: 代码审查
---

审查当前暂存的代码变更，关注：
- 安全漏洞
- 性能问题
- 代码风格
- 测试覆盖
```

然后在 Claude Code 里：

```
> /review
```

## 个人命令 vs 项目命令

| 类型 | 位置 | 作用域 | /help 标签 |
|------|------|--------|-----------|
| 项目命令 | `.claude/commands/` | 当前项目 | (project) |
| 个人命令 | `~/.claude/commands/` | 所有项目 | (user) |
| 插件命令 | `plugin/commands/` | 插件安装后 | (plugin-name) |

## 常见问题

### 安装后找不到 claude 命令

检查 PATH 是否包含安装路径。curl 安装通常放在 `~/.claude/bin/`：

```bash
echo $PATH | grep claude
# 如果没有，添加到 shell 配置：
export PATH="$HOME/.claude/bin:$PATH"
```

### Node.js 版本不对

```bash
node --version
# 需要 v18 或更高

# 使用 nvm 切换：
nvm install 18
nvm use 18
```

### 认证失败

- 确认 API Key 正确：`echo $ANTHROPIC_API_KEY`
- 如果用订阅登录，确保浏览器能打开 OAuth 页面
- 公司网络可能需要配置代理

### 调试模式

遇到问题时用 `--debug` 启动，可以看到详细的工具调用、MCP 连接、钩子执行等日志：

```bash
claude --debug
```

## 本章小结

**一句话记住**：一条命令安装 → 三步获得成就感 → 然后再学高级功能。

**决策规则**：
- macOS/Linux → `curl -fsSL https://claude.ai/install.sh | bash`
- Windows → `irm https://claude.ai/install.ps1 | iex`
- npm 安装已弃用，别用了

**遇到问题**：`claude --debug` 能看到所有工具调用、MCP 连接、钩子执行的详细日志——90% 的问题都能从这里找到线索。

**最容易踩的坑**：安装完不知道干什么——跑一遍"5 分钟快速成就感"的三步（理解项目 → 搜索代码 → 提交 Git），确认环境正常后再学高级功能。

**现在就试**：安装后跑一遍"5 分钟快速成就感"的三步，确认环境正常。

👉 接下来我们学权限模型——控制 AI 能做什么、不能做什么

---

**系列目录**：
- [第一章：Claude Code 是什么 —— 终端里的 AI 编码伙伴](./01-what-is-claude-code.md)
- 第二章：安装与上手 —— 从 curl 到第一个命令 👈 当前位置
- [第三章：权限模型 —— ask/allow/deny 与沙箱](./03-permission-model.md) 👉 下一章
- [第四章：斜杠命令 —— 自定义提示词的标准化方法](./../02-core/04-slash-commands.md)
- [第五章：Hooks 系统 —— 事件驱动的自动化引擎](./../02-core/05-hooks-system.md)
- [第六章：两种钩子对比 —— Prompt 钩子 vs Command 钩子](./../02-core/06-prompt-hooks-vs-command-hooks.md)
- [第七章：插件架构 —— 目录结构、自动发现与清单](./../03-plugins/07-plugin-architecture.md)
- [第八章：插件命令开发 —— frontmatter、动态参数、bash 执行](./../03-plugins/08-plugin-commands.md)
- [第九章：插件代理开发 —— 触发机制、系统提示词设计](./../03-plugins/09-plugin-agents.md)
- [第十章：插件技能开发 —— 渐进式披露与 SKILL.md](./../03-plugins/10-plugin-skills.md)
- [第十一章：插件钩子开发 —— hooks.json 与可移植路径](./../03-plugins/11-plugin-hooks.md)
- [第十二章：MCP 集成 —— stdio/SSE/HTTP/WebSocket 四种模式](./../03-plugins/12-mcp-integration.md)
- [第十三章：插件配置 —— .local.md 模式与 YAML frontmatter](./../03-plugins/13-plugin-settings.md)
- [第十六章：commit-commands —— 最简命令插件](./../04-plugin-deep-dives/16-commit-commands.md)
- [第十七章：security-guidance —— 安全钩子实战](./../04-plugin-deep-dives/17-security-guidance.md)
- [第十八章：code-review —— 多代理并行审查](./../04-plugin-deep-dives/18-code-review.md)
- [第十九章：feature-dev —— 7 阶段功能开发工作流](./../04-plugin-deep-dives/19-feature-dev.md)
- [第二十章：hookify —— 零代码创建钩子规则](./../04-plugin-deep-dives/20-hookify.md)
- [第二十一章：plugin-dev —— 用插件开发插件的元工具](./../04-plugin-deep-dives/21-plugin-dev-toolkit.md)
- [第二十二章：设置层级 —— 企业/用户/项目三层配置](./../05-enterprise/22-settings-hierarchy.md)
- [第二十三章：MDM 部署 —— Jamf/Intune/Group Policy 推送](./../05-enterprise/23-mdm-deployment.md)
- [第二十四章：Marketplace —— 插件发布与分发](./../05-enterprise/24-marketplace.md)
- [第二十五章：多代理模式 —— 并行代理编排与工作流](./../06-advanced/25-multi-agent-patterns.md)
- [第二十六章：Hookify 进阶 —— 多条件规则与操作符](./../06-advanced/26-hookify-advanced-rules.md)
- [第二十七章：从零构建完整插件 —— 端到端实战](./../06-advanced/27-building-complete-plugin.md)
