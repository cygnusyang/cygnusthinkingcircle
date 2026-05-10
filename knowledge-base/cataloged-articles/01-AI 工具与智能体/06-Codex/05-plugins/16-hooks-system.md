# 第十二章：Hooks 系统 —— 事件驱动的自动化

Codex 的 Hooks 系统允许在特定事件发生时自动执行逻辑。

## Hooks Crate 结构

**位置**：`source/codex/codex-rs/hooks/`

```
hooks/
├── src/
│   ├── lib.rs              # 主入口
│   ├── types.rs            # 类型定义
│   ├── events/             # 事件定义
│   │   └── ...
│   ├── engine/             # 执行引擎
│   ├── registry.rs         # 钩子注册表
│   ├── schema.rs           # JSON Schema
│   ├── config_rules.rs     # 配置规则
│   └── legacy_notify.rs    # 兼容旧的 notify
└── bin/
    └── write_hooks_schema_fixtures.rs
```

## 事件类型

Hooks 系统支持多种事件：

### 1. PreToolUse
在工具执行前触发，可用于：
- 验证参数
- 检查安全策略
- 记录日志

### 2. PostToolUse
在工具执行后触发，可用于：
- 处理结果
- 清理资源
- 通知用户

### 3. SessionStart
会话开始时触发。

### 4. SessionEnd
会话结束时触发。

## 钩子类型

### 1. Prompt Hooks
提示词钩子，给 AI 注入额外的上下文。

### 2. Command Hooks
命令钩子，执行外部命令。

## Schema 系统

Hooks 有完整的 JSON Schema 定义，参考 `schema.rs`。

生成 Schema：
```bash
just write-hooks-schema
```

## 配置方式

在 `config.toml` 中配置钩子规则。

## 与 Claude Code 的区别

Codex 的 Hooks 系统与 Claude Code 类似但实现不同，因为 Codex 是 Rust 编写的。

## 本章小结

**一句话记住**：Hooks 是事件驱动的自动化，支持多种事件类型和钩子类型。

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
- 第十六章：Hooks 系统 —— 事件驱动的自动化 👈 当前位置
- [第十七章：Plugin 系统 —— Codex 的扩展机制](./../05-plugins/17-plugin-system.md) 👉 下一章
