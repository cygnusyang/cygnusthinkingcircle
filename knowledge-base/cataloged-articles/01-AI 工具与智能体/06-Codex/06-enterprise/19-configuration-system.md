# 第十八章：配置系统 —— TOML + JSON Schema

你的团队需要 Codex 默认使用 workspace-write 沙箱，并且在项目根目录的 `refactor` 技能。编辑 `~/.config/codex/config.toml` 就可以做到。

Codex 使用 TOML 配置文件，配合自动生成的 JSON Schema 提供类型安全的配置。

## 配置文件位置

- **macOS/Linux**: `~/.config/codex/config.toml`
- **Windows**: `%APPDATA%\codex\config.toml`

## 配置 Schema

Codex 从 Rust 类型自动生成 JSON Schema：

```bash
just write-config-schema
```

这保证了配置文档与实际代码始终同步。

## 完整的配置例子

```toml
# ~/.config/codex/config.toml

# 沙箱模式
sandbox_mode = "workspace-write"  # 可选: "read-only", "workspace-write", "danger-full-access"

# 认证配置
[auth]
# 使用 ChatGPT 账号时不需要额外配置
# 使用 API Key 时:
# type = "api-key"
# api_key = "sk-..."

# UI 配置
[ui]
# 主题配置
# theme = "dark"

# 执行配置
[exec]
# 超时设置
# timeout_seconds = 60

# MCP 服务器配置
[mcp-servers]
# GitHub MCP
[mcp-servers.github]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-github"]

# 文件系统 MCP（有限访问）
[mcp-servers.filesystem]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/dir"]

# 自定义 MCP
[mcp-servers.my-team-tools]
command = "uvx"
args = ["my-team-mcp-server"]
```

## 配置层级

Codex 支持多级别配置，优先级从高到低：

1. **命令行参数**（如 `codex --sandbox workspace-write`）
2. **环境变量**（如 `CODEX_CONFIG=...`）
3. **项目级配置**（工作区根目录的 `.codex/config.toml`）
4. **全局配置**（`~/.config/codex/config.toml`）
5. **默认值**

这允许团队共享基础配置，同时个人可以覆盖特定选项。

## MCP 服务器配置

在 `config.toml` 中配置 MCP 服务器：

```toml
[mcp-servers.my-server]
command = "node"
args = ["/path/to/server.js"]
```

也可以用 CLI 管理：
```bash
codex mcp add my-server "node /path/to/server.js"
codex mcp list
codex mcp remove my-server
```

列出已配置的 MCP 服务器：
```
$ codex mcp list
github          enabled
filesystem      enabled
my-team-tools   disabled
```

## 官方配置文档

- [基础配置](https://developers.openai.com/codex/config-basic)
- [高级配置](https://developers.openai.com/codex/config-advanced)
- [完整配置参考](https://developers.openai.com/codex/config-reference)
- [示例配置](https://developers.openai.com/codex/config-sample)

## 本章小结

**一句话记住**：Codex 使用 TOML 配置 + 自动生成的 JSON Schema，支持多级别配置和 MCP 服务器管理。

---

**系列目录**：
- [第一章：Codex 是什么 —— OpenAI 的本地编码代理](./../01-intro/01-what-is-codex.md)
- [第二章：安装与上手 —— npm/brew/二进制三种方式](./../01-intro/02-installation-setup.md)
- [第三章：认证与配置 —— ChatGPT 账号 vs API Key](./../01-intro/03-authentication.md)
- [第四章：TUI 基础 —— 终端 UI 的交互方式](./../02-core/04-tui-basics.md)
- [第五章：codex exec —— 非交互式编程执行](./../02-core/05-codex-exec.md)
- [第六章：沙箱系统 —— 安全执行命令](./../02-core/06-sandbox.md)
- [第七章：MCP 客户端 —— 连接外部工具](./../03-cli/07-mcp-client.md)
- [第八章：架构概览 —— 100+ Crates 的模块化设计](./../04-advanced/08-architecture-overview.md)
- [第九章：TUI 深入 —— Ratatui 应用的构建方式](./../04-advanced/09-tui-in-depth.md)
- [第十章：Memories 系统 —— AI 的长期记忆](./../04-advanced/10-memories-system.md)
- [第十一章：State 系统 —— SQLite 数据库持久化](./../04-advanced/11-state-system.md)
- [第十二章：Tools 系统 —— 从 codex-core 独立出的工具原语](./../04-advanced/12-tools-system.md)
- [第十三章：Exec 系统 —— 安全沙箱执行的深层设计](./../04-advanced/13-exec-system.md)
- [第十四章：技能系统深入 —— 50+ 内置技能与实战场景](./../04-advanced/14-skills-in-depth.md)
- [第十五章：技能系统 —— 给 AI 注入专业知识](./../05-plugins/15-skills-system.md)
- [第十六章：Hooks 系统 —— 事件驱动的自动化](./../05-plugins/16-hooks-system.md)
- [第十七章：Plugin 系统 —— Codex 的扩展机制](./../05-plugins/17-plugin-system.md)
- [第十八章：开发工作流 —— 如何构建和测试 Codex](././18-development-workflow.md)
- 第十九章：配置系统 —— TOML + JSON Schema 👈 当前位置
- [第二十章：安全设计 —— 多层安全防护](././20-security.md) 👉 下一章
- [第二十一章：架构总结 —— 100+ Crates 的设计哲学](././21-architecture-summary.md)
