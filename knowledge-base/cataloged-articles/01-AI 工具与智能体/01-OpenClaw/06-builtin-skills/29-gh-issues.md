# 第二十九章：gh-issues —— GitHub Issues 自动修复编排

想象一下这样的场景：你的开源项目仓库里堆积了 50+ 个待处理的 bug 报告，每个都需要你手动分析、定位问题、编写修复代码、创建 PR、等待 review、再根据反馈修改……这听起来是不是很让人头疼？

更糟糕的是，其中很多问题其实是重复的、简单的，或者可以通过自动化方式解决的。你把大量时间花在这些重复性工作上，真正需要你深度思考的核心功能开发反而被挤占了。

如果有一个工具能够：
- 自动拉取 GitHub issues
- 智能分析每个问题
- 派发专门的子代理编写修复代码
- 自动创建 PR 并提交
- 持续监控 review comments 并处理反馈

你会不会觉得这简直是开发者的福音？

好消息是，OpenClaw 内置的 `gh-issues` skill 就能帮你实现这一切。

## `gh-issues` 是什么

当前内置 `gh-issues` 的描述是：

> 拉取 GitHub issues，派发 sub-agent 实现修复并打开 PR，然后持续监控并处理 review comments。

这说明它不是一个通用"分类工具"，而是一个**GitHub issue 编排 skill**。

## 当前依赖

这个 skill 在 frontmatter 里要求本机具备：

- `curl`
- `git`
- `gh`

并且需要：

```text
GH_TOKEN
```

作为主要认证环境变量。

### 安装 GitHub CLI

如果还没有安装 `gh` CLI，可以通过以下方式安装：

**macOS:**
```bash
brew install gh
```

**Linux:**
```bash
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh
```

**Windows:**
```powershell
winget install --id GitHub.cli
```

### 配置认证

安装完成后，需要认证：

```bash
gh auth login
```

或者直接设置环境变量：

```bash
export GH_TOKEN="your_github_personal_access_token"
```

## 当前支持的参数风格

skill 描述里直接给出了命令风格：

```text
/gh-issues [owner/repo] [--label bug] [--limit 5] [--milestone v1.0] [--assignee @me] [--fork user/repo] [--watch] [--interval 5] [--reviews-only] [--cron] [--dry-run] [--model glm-5] [--notify-channel -1002381931352]
```

这也说明它更像一个工作编排器，而不是聊天里临时批量分个类。

## 如何使用

`gh-issues` 是一个 OpenClaw 内置 skill，通过斜杠命令触发。你需要在**与 OpenClaw Gateway 连接的聊天客户端**中输入这些命令。

### 支持的聊天平台

OpenClaw 支持 25+ 聊天平台，你可以在以下任意平台中使用：

- **Telegram** - 通过 Telegram Bot 与 OpenClaw 交互
- **Discord** - 通过 Discord Bot 与 OpenClaw 交互
- **Slack** - 通过 Slack App 与 OpenClaw 交互
- **WebChat** - 通过内置的 WebSocket 聊天界面
- **其他平台** - 参见[第四章：多渠道接入](./../01-intro/04-multi-channel-inbox.md)

### 使用前提

在使用 `/gh-issues` 命令之前，需要确保：

1. **OpenClaw Gateway 已启动** - Gateway 服务正在运行
2. **已配置聊天平台** - 至少配置了一个聊天平台连接
3. **已完成配对** - 你的聊天账号已与 OpenClaw 配对（参见[第七章：安全模型](./../01-intro/07-security-model.md)）
4. **已安装依赖** - 本机已安装 `curl`、`git`、`gh` CLI
5. **已配置认证** - 已设置 `GH_TOKEN` 环境变量

### 命令格式

在聊天中输入的命令格式为：

```
/gh-issues [参数]
```

注意前面的 `/` 符号，这表示这是一个 skill 命令。

### 使用示例

在 Telegram 中使用：

```
你: /gh-issues openclaw/openclaw --label bug --limit 3

OpenClaw: 正在获取 openclaw/openclaw 仓库中标签为 bug 的 issues...
找到 5 个符合条件的 issues：
1. #123 - 修复登录页面崩溃问题
2. #124 - API 响应超时
3. #125 - 数据库连接池泄漏
4. #126 - 缓存失效问题
5. #127 - 内存泄漏

请确认要处理哪些 issues（输入编号，用逗号分隔，或输入 all 处理全部）：
```

在 Discord 中使用：

```
你: /gh-issues openclaw/openclaw --milestone v1.0 --dry-run

OpenClaw: [试运行模式] 将处理以下 issues：
- #100 - 实现用户认证
- #101 - 添加权限管理
- #102 - 完善日志系统

不会实际执行任何操作。如需执行，请移除 --dry-run 参数。
```

## 参数详解

### 必需参数

- `[owner/repo]` - 目标仓库，例如 `openclaw/openclaw`

### 可选参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--label` | 按标签筛选 issues | `--label bug` |
| `--limit` | 限制处理的 issue 数量 | `--limit 5` |
| `--milestone` | 按里程碑筛选 | `--milestone v1.0` |
| `--assignee` | 指定指派人 | `--assignee @me` |
| `--fork` | 指定 fork 仓库 | `--fork user/repo` |
| `--watch` | 持续监控模式 | `--watch` |
| `--interval` | 监控间隔（分钟） | `--interval 5` |
| `--reviews-only` | 仅处理 review comments | `--reviews-only` |
| `--cron` | 定时任务模式 | `--cron` |
| `--dry-run` | 试运行模式 | `--dry-run` |
| `--model` | 指定使用的模型 | `--model glm-5` |
| `--notify-channel` | 通知频道 ID | `--notify-channel -1002381931352` |

## 当前 skill 的工作流重点

从 `SKILL.md` 看，它的核心阶段包括：

1. **解析参数** - 解析用户输入的命令行参数
2. **调 GitHub API 拉取 issues** - 使用 GitHub API 获取符合条件的 issues
3. **展示并确认要处理哪些 issue** - 列出找到的 issues，等待用户确认
4. **跑 git / remote / token 预检** - 检查 git 配置、远程仓库和认证信息
5. **派发子代理处理代码修复** - 为每个 issue 派发独立的子代理进行修复
6. **跟进 PR review comments** - 持续监控 PR 的 review comments 并处理

## 快速开始

### 基础用法

处理指定仓库的 bug 标签 issues：

```bash
/gh-issues openclaw/openclaw --label bug --limit 3
```

### 指定里程碑

处理特定里程碑的 issues：

```bash
/gh-issues openclaw/openclaw --milestone v1.0 --limit 5
```

### 指派给自己

处理指派给自己的 issues：

```bash
/gh-issues openclaw/openclaw --assignee @me --limit 10
```

### 试运行模式

先看看会处理哪些 issues，不实际执行：

```bash
/gh-issues openclaw/openclaw --label bug --dry-run
```

### 持续监控模式

持续监控并处理新的 issues：

```bash
/gh-issues openclaw/openclaw --label bug --watch --interval 10
```

## 实际工作流程

### 完整修复流程

```mermaid
graph TD
    A[用户发起命令] --> B[解析参数并验证]
    B --> C[调用 GitHub API 获取 issues]
    C --> D[展示 issues 列表]
    D --> E[用户确认要处理的 issues]
    E --> F[预检 git 配置和认证]
    F --> G[为每个 issue 派发子代理]
    G --> H[子代理分析 issue 并生成修复]
    H --> I[创建 PR]
    I --> J[持续监控 PR review comments]
    J --> K{有新的 review comments?}
    K -->|是| L[根据反馈更新 PR]
    L --> J
    K -->|否| M[完成]
    
    style A fill:#e1f5ff
    style M fill:#c8e6c9
    style K fill:#fff9c4
```

### 子代理工作流程

每个子代理会执行以下步骤：

```mermaid
graph LR
    A[分析 issue<br/>理解问题描述和期望的修复] --> B[探索代码库<br/>找到相关的代码文件]
    B --> C[生成修复方案<br/>创建或修改代码]
    C --> D[测试验证<br/>运行相关测试]
    D --> E{测试通过?}
    E -->|否| C
    E -->|是| F[创建 PR<br/>提交修复并创建 Pull Request]
    F --> G[响应反馈<br/>处理 review comments 并更新]
    G --> H{需要修改?}
    H -->|是| C
    H -->|否| I[完成]
    
    style A fill:#e1f5ff
    style I fill:#c8e6c9
    style E fill:#fff9c4
    style H fill:#fff9c4
```

## 使用场景

### 1. 批量修复简单 bug

```bash
/gh-issues openclaw/openclaw --label "easy-fix" --limit 10
```

### 2. 处理特定里程碑的遗留问题

```bash
/gh-issues openclaw/openclaw --milestone v1.0 --label "backlog" --limit 20
```

### 3. 持续监控新 issues

```bash
/gh-issues openclaw/openclaw --label bug --watch --interval 5 --notify-channel -1002381931352
```

### 4. 仅处理 PR review comments

```bash
/gh-issues openclaw/openclaw --reviews-only --limit 5
```

## 最佳实践

### 1. 使用试运行模式

在正式处理前，先用 `--dry-run` 查看会处理哪些 issues：

```bash
/gh-issues openclaw/openclaw --label bug --dry-run
```

### 2. 限制处理数量

避免一次性处理太多 issues，建议从小数量开始：

```bash
/gh-issues openclaw/openclaw --label bug --limit 3
```

### 3. 使用标签筛选

通过标签精确控制处理范围：

```bash
/gh-issues openclaw/openclaw --label "good-first-issue" --limit 5
```

### 4. 指定合适的模型

根据任务复杂度选择合适的模型：

```bash
/gh-issues openclaw/openclaw --label bug --model glm-4 --limit 5
```

### 5. 设置通知

在持续监控模式下设置通知，及时了解处理进度：

```bash
/gh-issues openclaw/openclaw --label bug --watch --notify-channel -1002381931352
```

## 常见问题

### Q1: 为什么没有处理任何 issues？

可能的原因：
- 没有符合条件的 issues
- GitHub token 权限不足
- 网络连接问题

解决方法：
- 使用 `--dry-run` 查看找到的 issues
- 检查 `GH_TOKEN` 是否有足够的权限
- 检查网络连接

### Q2: 子代理创建的 PR 质量不好怎么办？

可以：
- 使用更强大的模型：`--model glm-5`
- 减少同时处理的 issues 数量：`--limit 2`
- 手动 review PR 后再合并

### Q3: 如何停止持续监控模式？

在聊天中发送停止命令，或者直接终止 OpenClaw 进程。

### Q4: 可以处理私有仓库吗？

可以，但需要确保 `GH_TOKEN` 有访问该私有仓库的权限。

### Q5: 如何处理 fork 的 PR？

使用 `--fork` 参数指定 fork 仓库：

```bash
/gh-issues openclaw/openclaw --fork yourname/openclaw --limit 5
```

## 故障排除

### 认证失败

**错误信息：** `Authentication failed`

**解决方法：**
```bash
# 重新认证
gh auth login

# 或者检查环境变量
echo $GH_TOKEN
```

### Git 配置问题

**错误信息：** `Git configuration not found`

**解决方法：**
```bash
# 配置 git 用户信息
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 权限不足

**错误信息：** `Insufficient permissions`

**解决方法：**
- 检查 GitHub token 是否有 `repo` 权限
- 确认你有访问目标仓库的权限

### 网络问题

**错误信息：** `Network error`

**解决方法：**
- 检查网络连接
- 如果使用代理，配置 git 代理：
```bash
git config --global http.proxy http://proxy.example.com:8080
```

## 安全注意事项

1. **保护 GitHub Token**
   - 不要在代码中硬编码 token
   - 使用环境变量或密钥管理工具
   - 定期轮换 token

2. **权限最小化**
   - 只授予必要的权限
   - 使用专门的 service account

3. **审查生成的 PR**
   - 不要自动合并所有 PR
   - 仔细 review 代码变更
   - 运行完整的测试套件

4. **限制处理范围**
   - 使用标签和限制参数
   - 避免处理敏感 issues

## 与其他章节的关联

- **第九章**：`sessions_spawn` - gh-issues 使用子代理协作的核心原语
- **第十章**：协作架构模式 - gh-issues 体现了 Master-Worker 模式
- **第十一章**：隔离设计 - 每个 issue 由独立的子代理处理
- **第十九章**：skills - gh-issues 是内置 skill 的典型示例
- **第二十六章**：Cron 自动化 - gh-issues 的定时任务模式

## 本章小结

- `gh-issues` 是一个用于批量处理 GitHub Issues、派发子代理修复并管理 PR 的内置 skill
- 它围绕 GitHub issues、子代理修复、PR 和 review comment 闭环展开
- 支持丰富的参数配置，可以灵活控制处理范围和行为
- 提供试运行、持续监控等多种工作模式
- 是 OpenClaw 多智能体协作和自动化能力的典型体现

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
- 第二十九章：gh-issues —— GitHub Issues 自动修复编排 👈 当前位置
- [第三十章：coding-agent —— 调用外部编码代理](./30-coding-agent.md) 👉 下一章
- [第三十一章：模型故障转移 (Model Failover) —— 如何提高可用性](./../07-ops-best-practices/31-failover.md)
- [第三十二章：调试技巧 —— 如何排查 OpenClaw 问题](./../07-ops-best-practices/32-debugging.md)
- [第三十三章：成本优化 —— 如何用模型分级降低总成本](./../07-ops-best-practices/33-cost-optimization.md)
- [第三十四章：部署运维 —— OpenClaw 网关生产环境最佳实践](./../07-ops-best-practices/34-deployment.md)
