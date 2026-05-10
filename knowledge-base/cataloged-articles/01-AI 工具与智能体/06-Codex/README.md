# Codex 博客系列目录

这个系列从浅入深讲解 OpenAI Codex CLI，共 20 章，涵盖从入门到架构设计的全部内容。

## 第一部分：入门（01-intro）

1. [Codex 是什么 —— OpenAI 的本地编码代理](./01-intro/01-what-is-codex.md)
2. [安装与上手 —— npm/brew/二进制三种方式](./01-intro/02-installation-setup.md)
3. [认证与配置 —— ChatGPT 账号 vs API Key](./01-intro/03-authentication.md)

## 第二部分：核心概念（02-core）

4. [TUI 基础 —— 终端 UI 的交互方式](./02-core/04-tui-basics.md)
5. [codex exec —— 非交互式编程执行](./02-core/05-codex-exec.md)
6. [沙箱系统 —— 安全执行命令](./02-core/06-sandbox.md)

## 第三部分：CLI 使用（03-cli）

7. [MCP 客户端 —— 连接外部工具](./03-cli/07-mcp-client.md)

## 第四部分：深入架构（04-advanced）

8. [架构概览 —— 100+ Crates 的模块化设计](./04-advanced/08-architecture-overview.md)
9. [TUI 深入 —— Ratatui 应用的构建方式](./04-advanced/09-tui-in-depth.md)
10. [Memories 系统 —— AI 的长期记忆](./04-advanced/10-memories-system.md)
11. [State 系统 —— SQLite 数据库持久化](./04-advanced/11-state-system.md)
12. [Tools 系统 —— 从 codex-core 独立出的工具原语](./04-advanced/12-tools-system.md)
13. [Exec 系统 —— 安全沙箱执行的深层设计](./04-advanced/13-exec-system.md)

## 第五部分：扩展系统（05-plugins）

15. [技能系统 —— 给 AI 注入专业知识](./05-plugins/15-skills-system.md)
16. [Hooks 系统 —— 事件驱动的自动化](./05-plugins/16-hooks-system.md)
17. [Plugin 系统 —— Codex 的扩展机制](./05-plugins/17-plugin-system.md)

## 第六部分：开发与部署（06-enterprise）

18. [开发工作流 —— 如何构建和测试 Codex](./06-enterprise/18-development-workflow.md)
19. [配置系统 —— TOML + JSON Schema](./06-enterprise/19-configuration-system.md)
20. [安全设计 —— 多层安全防护](./06-enterprise/20-security.md)
21. [架构总结 —— 100+ Crates 的设计哲学](./06-enterprise/21-architecture-summary.md)

---

## 源码参考

所有源码都在 `source/codex/` 目录：
- `codex-rs/` — Rust 核心，100+ crates
- `codex-cli/` — Node.js CLI 包装
- `sdk/` — TypeScript/Python SDK
- `docs/` — 官方文档

## 关键文档

- `AGENTS.md` — 开发原则和约定（必读！）
- `justfile` — 开发命令
- `docs/contributing.md` — 贡献指南（邀请制）
- `codex-rs/memories/README.md` — 记忆系统设计文档

## 核心设计亮点

1. **100+ 小 Crates**: 极致模块化，每个职责单一
2. **抵制 Core 膨胀**: 主动向外拆代码，core 只保留必要的编排
3. **两阶段记忆流水线**: Phase 1 并行提取，Phase 2 全局序列化整合
4. **多层沙箱安全**: 每个平台用最佳方案（macOS Seatbelt / Linux Landlock + bubblewrap / Windows）
5. **Schema 从代码生成**: 单一事实源，避免文档与代码脱节
6. **邀请制贡献**: 保证代码质量和一致性
7. **Dogfooding**: Codex 用自己开发自己

---

*本博客系列基于 OpenAI Codex 官方源代码撰写，仅供学习参考。*
