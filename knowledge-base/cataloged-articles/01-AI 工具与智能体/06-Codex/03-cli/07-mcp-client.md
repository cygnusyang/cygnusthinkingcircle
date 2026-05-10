# 第七章：MCP 客户端 —— 连接外部工具

Codex 是一个 **MCP（Model Context Protocol）客户端**，可以连接各种 MCP 服务器。

## 什么是 MCP

MCP（Model Context Protocol）是一个开放协议，让 AI 代理能够连接外部工具和数据源。

## 配置 MCP 服务器

在 `~/.config/codex/config.toml` 里配置：

```toml
[mcp-servers]
[mcp-servers.my-server]
command = "node"
args = ["/path/to/server.js"]
```

## 管理 MCP 服务器

Codex 提供了 `codex mcp` 命令来管理：

```bash
# 列出已配置的 MCP 服务器
codex mcp list

# 添加 MCP 服务器
codex mcp add my-server "node /path/to/server.js"

# 移除 MCP 服务器
codex mcp remove my-server
```

## Codex 作为 MCP 服务器

Codex 也可以作为 MCP 服务器运行：

```bash
codex mcp-server
```

这样其他 MCP 客户端就能用 Codex 作为工具了。

## 测试 MCP 服务器

用 MCP Inspector 测试：

```bash
npx @modelcontextprotocol/inspector codex mcp-server
```

## 本章小结

**一句话记住**：Codex 既是 MCP 客户端（连接外部工具），也可以作为 MCP 服务器（给别人用）。

---

**系列目录**：
- [第一章：Codex 是什么 —— OpenAI 的本地编码代理](./../01-intro/01-what-is-codex.md)
- [第二章：安装与上手 —— npm/brew/二进制三种方式](./../01-intro/02-installation-setup.md)
- [第三章：认证与配置 —— ChatGPT 账号 vs API Key](./../01-intro/03-authentication.md)
- [第四章：TUI 基础 —— 终端 UI 的交互方式](./../02-core/04-tui-basics.md)
- [第五章：codex exec —— 非交互式编程执行](./../02-core/05-codex-exec.md)
- [第六章：沙箱系统 —— 安全执行命令](./../02-core/06-sandbox.md)
- 第七章：MCP 客户端 —— 连接外部工具 👈 当前位置
