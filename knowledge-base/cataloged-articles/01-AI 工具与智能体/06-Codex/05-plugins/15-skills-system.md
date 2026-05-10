# 第十章：技能系统 —— 给 AI 注入专业知识

Codex 的 Skills 系统允许给 AI 注入特定领域的知识。

> **📘 深度阅读**：本文是技能系统的简要介绍。详细的技能系统深入、50+ 内置技能解析和实战场景，请参阅 [技能系统深入 —— 50+ 内置技能与实战场景](./../04-advanced/14-skills-in-depth.md)。

## Skills 是什么

Skills 是预定义的提示词和知识，帮助 AI 更好地完成特定任务。

## Skills Crate

**位置**：`source/codex/codex-rs/skills/`

核心技能定义在这个 crate 中。

## Core Skills

Codex 自带核心技能，参考 `source/codex/codex-rs/core-skills/`。

## 技能类型

### 1. 任务指导技能

帮助 AI 理解如何完成特定类型的任务。

### 2. 领域知识技能

注入特定领域的专业知识。

### 3. 风格指导技能

指导 AI 的输出风格和格式。

## SDK

Codex 提供了 SDK 用于构建自定义技能：

- **TypeScript SDK**：`source/codex/sdk/typescript/`
- **Python SDK**：`source/codex/sdk/python/`
- **Python Runtime**：`source/codex/sdk/python-runtime/`

## 使用技能

技能通过配置或插件加载，AI 在对话中会自动应用相关技能。

## 本章小结

**一句话记住**：Skills 给 AI 注入专业知识，可通过 SDK 自定义。

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
- 第十五章：技能系统 —— 给 AI 注入专业知识 👈 当前位置
- [第十六章：Hooks 系统 —— 事件驱动的自动化](././16-hooks-system.md) 👉 下一章
