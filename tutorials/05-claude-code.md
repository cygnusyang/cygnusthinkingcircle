# 05. Claude Code 安装与使用

## 🤖 什么是 Claude Code

Claude Code 是 Anthropic 官方推出的 **AI 编程助手**，能够：

- ✅ 理解整个代码库
- ✅ 自动执行开发任务
- ✅ 使用工具（Git、文件编辑、Bash 等）
- ✅ 集成 MCP 服务器扩展功能
- ✅ 支持多种模型（Haiku、Sonnet、Opus）

## 📥 安装

### macOS

```bash
# 使用 Homebrew 安装
brew install claude-code

# 验证安装
claude --version
```

### Linux

```bash
# 下载二进制文件
wget https://github.com/anthropics/claude-code/releases/latest/download/claude-code-linux-amd64
chmod +x claude-code-linux-amd64
sudo mv claude-code-linux-amd64 /usr/local/bin/claude

# 验证安装
claude --version
```

### Windows

```bash
# 使用 Scoop 安装
scoop bucket add claude-code
scoop install claude-code

# 验证安装
claude --version
```

## 🔑 认证

### 步骤 1: 创建 API Key

访问 [Anthropic Console](https://console.anthropic.com/) 创建 API Key。

### 步骤 2: 登录

```bash
# 启动认证流程
claude login

# 浏览器会打开，完成授权
# 或在终端输入授权码
```

### 步骤 3: 验证

```bash
# 测试连接
claude --ping
```

## 🚀 基本使用

### 启动交互式会话

```bash
# 在项目目录启动
cd /path/to/your/project
claude

# 或指定模型
claude --model claude-sonnet-4-20250514
```

### 常用命令

| 命令 | 说明 |
|------|------|
| `/help` | 显示帮助 |
| `/clear` | 清空上下文 |
| `/fast` | 切换到快速模式 |
| `/exit` | 退出会话 |
| `/! <命令>` | 在本地 shell 执行命令 |

### 示例对话

```
User: 解释这个文件是做什么的？
Claude: [分析代码，给出解释]

User: 帮我添加一个登录功能
Claude: [分析项目，创建登录功能]

User: 检查最近的代码更改
Claude: [运行 git diff，给出分析]
```

## 🛠️ 权限管理

### 配置文件

配置文件位于 `~/.claude/settings.json`：

```json
{
  "permissions": {
    "default": "auto",
    "allowedTools": ["Read", "Write", "Edit", "Bash"],
    "autoConfirm": {
      "fileRead": true,
      "fileWrite": false
    }
  },
  "model": "claude-sonnet-4-20250514"
}
```

### 权限模式

| 模式 | 说明 |
|------|------|
| `auto` | 自动允许（推荐） |
| `ask` | 每次询问 |
| `never` | 拒绝所有 |

## 🧩 插件与 Skills

### MCP 服务器

MCP (Model Context Protocol) 允许扩展 Claude Code 功能。

**安装插件：**

```bash
# 通过配置文件添加
cat >> ~/.claude/settings.json << EOF
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/directory"]
    }
  }
}
EOF
```

### Skills

Skills 是可重用的任务模板。

**列出可用 skills：**

```
/skills
```

**使用 skill：**

```
/skill python-patterns
```

## 🎯 在本项目中的应用

### 1. 自动生成文章

```
User: 根据 knowledge-base/articles/template.md 创建一篇关于 Docker 的文章
Claude: [创建文件，填充内容]
```

### 2. 代码审查

```
User: 审查 tools/lib/article.py 的代码
Claude: [分析代码，给出改进建议]
```

### 3. 调试

```
User: 发布功能有问题，帮我检查
Claude: [运行调试，找出问题]
```

### 4. 文档生成

```
User: 为 tools/lib/ 下的所有模块生成文档
Claude: [读取代码，生成文档]
```

## 💡 最佳实践

### 1. 清晰的指令

❌ 不好的指令：
```
帮我修复代码
```

✅ 好的指令：
```
tools/make.py 在发布时出现错误，错误信息是 "submodule not initialized"。帮我找出问题并修复。
```

### 2. 上下文管理

Claude Code 会记住整个会话上下文，但要注意：

- 上下文有大小限制
- 复杂任务可以分阶段完成
- 使用 `/clear` 开始新的上下文

### 3. 权限控制

对于涉及文件修改的操作，建议：

```json
{
  "autoConfirm": {
    "fileRead": true,
    "fileWrite": false  // 写操作需要确认
  }
}
```

### 4. 模型选择

| 任务 | 推荐模型 |
|------|---------|
| 日常编码 | Haiku 4.5（快速、便宜） |
| 复杂重构 | Sonnet 4.6（平衡） |
| 架构设计 | Opus 4.7（最强推理） |

## 🔧 高级功能

### 1. Hooks

Hooks 允许在工具执行前后自动运行命令。

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "pattern": "**/*.py",
        "command": "black --check ${file}"
      }
    ]
  }
}
```

### 2. 自动完成

为常用命令设置别名：

```json
{
  "aliases": {
    "review": "code-review",
    "test": "pytest"
  }
}
```

### 3. 工作流

创建工作流自动化复杂任务：

```json
{
  "workflows": {
    "deploy": [
      "python tools/make.py build --all",
      "python tools/make.py publish"
    ]
  }
}
```

## 📊 使用统计

查看使用情况：

```bash
claude --stats
```

## 🔐 安全建议

1. **不要在代码中硬编码 API Key**
2. **使用环境变量管理敏感信息**
3. **定期审查权限设置**
4. **不要在生产环境自动执行高风险操作**

## 🆘 故障排查

### Q: 连接失败？

```bash
# 检查 API Key
claude --whoami

# 重新登录
claude logout
claude login
```

### Q: 权限错误？

```bash
# 检查配置文件
cat ~/.claude/settings.json

# 重置权限
claude --reset-permissions
```

### Q: 上下文超限？

```bash
# 清空上下文
/clear

# 或使用分阶段方法完成任务
```

## 💡 下一步

- [06. 完整工作流](./06-complete-workflow.md) - 端到端演示
- [07. 故障排查](./07-troubleshooting.md) - 常见问题解决