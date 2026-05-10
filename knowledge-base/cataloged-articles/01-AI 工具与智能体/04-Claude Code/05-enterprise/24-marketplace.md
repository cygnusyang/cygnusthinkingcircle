# 第二十四章：Marketplace —— 插件发布与分发

插件写好了，怎么分享给别人？Claude Code 的 Marketplace 系统就是答案。

## Marketplace 是什么

Marketplace 是 Claude Code 的插件分发平台。你可以把插件发布到 Marketplace，其他用户一条命令就能安装。

```mermaid
graph LR
    A[开发者编写插件] --> B[发布到 Marketplace]
    B --> C[用户搜索/浏览]
    C --> D["/plugin install 安装"]
    D --> E[Claude Code 自动加载]
```

## Marketplace 清单格式

源码中的 `marketplace.json` 定义了整个市场的插件目录：

```json
{
  "$schema": "https://json.schemastore.org/claude-code-marketplace.json",
  "name": "claude-code-plugins",
  "version": "1.0.0",
  "description": "Bundled plugins for Claude Code",
  "owner": {
    "name": "Anthropic",
    "email": "support@anthropic.com"
  },
  "plugins": [
    {
      "name": "plugin-name",
      "description": "What this plugin does",
      "version": "1.0.0",
      "author": {
        "name": "Author Name",
        "email": "author@example.com"
      },
      "source": "./plugins/plugin-name",
      "category": "development"
    }
  ]
}
```

### 清单字段

| 字段 | 必需 | 说明 |
|------|------|------|
| `name` | 是 | Marketplace 名称 |
| `version` | 是 | Marketplace 版本 |
| `description` | 是 | 市场描述 |
| `owner` | 是 | 市场所有者信息 |
| `plugins` | 是 | 插件列表 |

### 插件条目字段

| 字段 | 必需 | 说明 |
|------|------|------|
| `name` | 是 | 插件名（kebab-case） |
| `description` | 是 | 插件描述 |
| `version` | 否 | 插件版本 |
| `author` | 否 | 作者信息 |
| `source` | 是 | 插件目录路径（相对） |
| `category` | 否 | 分类 |

### 分类体系

源码中使用的分类：

| 分类 | 含义 | 示例插件 |
|------|------|---------|
| `development` | 开发工具 | agent-sdk-dev, feature-dev, plugin-dev |
| `productivity` | 生产力 | commit-commands, code-review, hookify |
| `learning` | 学习 | explanatory-output-style, learning-output-style |
| `security` | 安全 | security-guidance |

## 官方插件一览

源码中的 12 个官方插件全部发布在 Anthropic 官方 Marketplace：

| 插件 | 分类 | 版本 | 作者 |
|------|------|------|------|
| agent-sdk-dev | development | - | Anthropic |
| claude-opus-4-5-migration | development | 1.0.0 | William Hu |
| code-review | productivity | 1.0.0 | Boris Cherny |
| commit-commands | productivity | 1.0.0 | Anthropic |
| explanatory-output-style | learning | 1.0.0 | Dickson Tsai |
| feature-dev | development | 1.0.0 | Siddharth Bidasaria |
| frontend-design | development | 1.0.0 | Prithvi Rajasekaran & Alexander Bricken |
| hookify | productivity | 0.1.0 | Daisy Hollman |
| learning-output-style | learning | 1.0.0 | Boris Cherny |
| plugin-dev | development | 0.1.0 | Daisy Hollman |
| pr-review-toolkit | productivity | 1.0.0 | Anthropic |
| ralph-wiggum | development | 1.0.0 | Daisy Hollman |
| security-guidance | security | 1.0.0 | David Dworken |

## 安装插件

### 从 Marketplace 安装

```bash
# 在 Claude Code 中
/plugin install plugin-name@marketplace-name

# 示例
/plugin install hookify@claude-code-marketplace
/plugin install plugin-dev@claude-code-marketplace
```

### 本地安装

```bash
# 指定插件目录
claude --plugin-dir /path/to/plugin

# 开发时使用
cc --plugin-dir /path/to/my-plugin
```

### 通过 settings.json 配置

```json
{
  "plugins": [
    "plugin-name@marketplace-name"
  ]
}
```

## 企业级市场管控

企业可以通过 MDM 限制允许的插件市场：

```json
{
  "strictKnownMarketplaces": ["claude-code-marketplace", "company-internal-marketplace"]
}
```

效果：
- 用户只能从白名单市场安装插件
- 未知市场的插件被阻止
- 空数组 `[]` 表示不限制

## 发布流程

### 1. 准备插件

确保插件结构完整：

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json    # 必需
├── commands/           # 至少有一种组件
├── README.md           # 必需
└── ...
```

### 2. 编写 README

README 应包含：
- 插件用途说明
- 安装方法
- 可用命令/代理/技能/钩子列表
- 使用示例
- 配置说明

### 3. 更新 plugin.json

```json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "description": "What it does",
  "author": {
    "name": "Your Name",
    "email": "you@example.com"
  },
  "homepage": "https://github.com/you/my-plugin",
  "license": "MIT",
  "keywords": ["automation", "workflow"]
}
```

### 4. 提交到 Marketplace

```bash
# 1. Fork Anthropic 官方 marketplace 仓库（在 GitHub 网页上操作）
#    访问 https://github.com/anthropics/claude-code-marketplace 并点击 Fork

# 2. 克隆你 fork 的仓库
git clone https://github.com/YOUR_USERNAME/claude-code-marketplace.git
cd claude-code-marketplace

# 3. 创建并切换到新分支
git checkout -b add-my-plugin

# 4. 复制你的插件到 plugins 目录
cp -r /path/to/my-plugin plugins/

# 5. 更新 marketplace.json，添加你的插件条目
#    使用你喜欢的编辑器编辑 marketplace.json
code marketplace.json
# 或
vim marketplace.json

# 6. 验证 JSON 格式
cat marketplace.json | jq .

# 7. 提交更改
git add plugins/my-plugin marketplace.json
git commit -m "Add my-plugin to marketplace"

# 8. 推送到你的 fork
git push origin add-my-plugin

# 9. 创建 Pull Request（使用 GitHub CLI）
gh pr create --title "Add my-plugin" --body "Description of my plugin"

#    或者在 GitHub 网页上手动创建 PR
```

**注意事项：**
- 确保插件目录包含所有必需文件（`.claude-plugin/plugin.json`、`README.md` 等）
- `marketplace.json` 中的 `source` 路径应指向正确的插件目录
- PR 描述中应包含插件的功能说明和使用示例

### 5. 验证

安装后验证所有组件：

```bash
# 检查插件是否加载
/help   # 查看命令列表
/hooks  # 查看钩子
/mcp    # 查看 MCP 服务器

# 测试命令
/my-command

# 检查代理
# 尝试触发代理的任务

# 检查技能
# 询问技能相关的问题
```

## Marketplace 最佳实践

### 插件质量

- **单一职责**：一个插件解决一类问题
- **清晰命名**：名称要反映功能
- **完整文档**：README 是用户的第一印象
- **版本管理**：遵循 semver

### 安全

- **最小权限**：只申请必要的 allowed-tools
- **无硬编码密钥**：使用环境变量
- **输入验证**：钩子脚本验证所有输入
- **HTTPS only**：MCP 服务器使用安全连接

### 可维护性

- **使用 ${CLAUDE_PLUGIN_ROOT}**：确保可移植
- **测试覆盖**：验证脚本和钩子
- **渐进式披露**：技能用 references/ 存放详细内容
- **清晰更新日志**：版本变更说明

## 本章小结

**一句话记住**：Marketplace 是插件的"npm registry" —— 写好插件一键发布，别人一条命令安装，版本和分类自动管理。

**决策规则**：
- 只是自己用 → `claude --plugin-dir /path/to/plugin` 本地加载即可
- 团队共享私有插件 → 自建 marketplace.json，用 `strictKnownMarketplaces` 限制来源
- 开源给社区 → 提交到官方 Marketplace，走 PR 审核流程
- 企业安全要求高 → MDM 配置 `strictKnownMarketplaces` 白名单，只允许官方市场

**最容易踩的坑**：插件目录结构不完整就提交 —— 缺 `plugin.json` 或 README，安装后静默失败，排查半天才发现是目录格式不对。

**个人开发者也能用**：你不需要发布到官方市场也能享受 Marketplace 的便利。在本地创建一个 `marketplace.json`，把自己常用的几个插件目录列进去，然后通过 `plugin-name@my-local-marketplace` 一键加载。比每次手动指定 `--plugin-dir` 方便得多。此外，浏览官方市场的 12 个插件本身就是最好的学习素材 —— 克隆下来读源码，比任何教程都管用。

**现在就试**：运行 `/plugin install hookify@claude-code-marketplace`，装一个官方插件体验完整的安装流程。

👉 接下来我们进入高级模式，看多代理如何让 AI 团队协作

---

**系列目录**：
- [第一章：Claude Code 是什么 —— 终端里的 AI 编码伙伴](./../01-intro/01-what-is-claude-code.md)
- [第二章：安装与上手 —— 从 curl 到第一个命令](./../01-intro/02-installation-setup.md)
- [第三章：权限模型 —— ask/allow/deny 与沙箱](./../01-intro/03-permission-model.md)
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
- [第二十二章：设置层级 —— 企业/用户/项目三层配置](./22-settings-hierarchy.md)
- [第二十三章：MDM 部署 —— Jamf/Intune/Group Policy 推送](./23-mdm-deployment.md)
- 第二十四章：Marketplace —— 插件发布与分发 👈 当前位置
- [第二十五章：多代理模式 —— 并行代理编排与工作流](./../06-advanced/25-multi-agent-patterns.md) 👉 下一章
- [第二十六章：Hookify 进阶 —— 多条件规则与操作符](./../06-advanced/26-hookify-advanced-rules.md)
- [第二十七章：从零构建完整插件 —— 端到端实战](./../06-advanced/27-building-complete-plugin.md)
