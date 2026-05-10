# 第十七章：Plugin 系统 —— Codex 的扩展机制

Codex 有完整的插件系统架构，虽然与 Claude Code 不同，但设计思想类似。

## Plugin Crate

**位置**：`source/codex/codex-rs/plugin/`

插件加载、管理和执行的核心逻辑。

## App Server 协议族

IDE 集成通过 App Server 实现，有一系列专门的 crate：

```
app-server/              # 服务器实现
app-server-client/       # 客户端
app-server-protocol/     # 协议定义
app-server-transport/    # 传输层
app-server-test-client/  # 测试客户端
```

## 协议版本

App Server 协议有 v1 和 v2 两个版本：
- **v1**: 遗留版本
- **v2**: 活跃开发版本，所有新 API 都在这里

### v2 协议约定

- 有效负载命名一致：`*Params` 用于请求，`*Response` 用于响应，`*Notification` 用于通知
- RPC 方法暴露为 `<resource>/<method>`，资源保持单数
- 在线上总是使用 camelCase 字段，配合 `#[serde(rename_all = "camelCase")]`
- 例外：配置 RPC 有效负载使用 snake_case 以镜像 config.toml 键
- 总是在 v2 请求/响应/通知类型上设置 `#[ts(export_to = "v2/")]`
- 从不为 v2 API 有效负载字段使用 `#[serde(skip_serializing_if = "Option::is_none")]`
- 例外：客户端到服务器请求，如果有意没有参数，可以使用
- 保持 Rust 和 TS 重命名一致
- 对于区分联合，在两个序列化器中使用显式标记

### 开发工作流

- API 行为变化时更新文档/示例（至少 `app-server/README.md`）
- API 形状变化时重新生成 schema 固定文件：`just write-app-server-schema`
- 使用 `cargo test -p codex-app-server-protocol` 验证

## 可发现工具

插件系统支持工具发现：
- `tool_search` 工具
- `request_plugin_install` 工具

## 协作模式

支持多用户协作：
- spawn/send/wait/close 工具
- `request_user_input` 工具
- CSV fanout/reporting 工具

## 与 Claude Code 插件的区别

Codex 的插件系统更集成在核心中，而 Claude Code 有独立的插件架构。但两者都支持：
- 自定义工具
- MCP 集成
- 技能注入

## 本章小结

**一句话记住**：Codex 的 Plugin 系统与 App Server 协议配合，支持 IDE 集成和扩展。

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
- 第十七章：Plugin 系统 —— Codex 的扩展机制 👈 当前位置
- [第十八章：开发工作流 —— 如何构建和测试 Codex](./../06-enterprise/18-development-workflow.md) 👉 下一章
