# 第十九章：安全设计 —— 多层安全防护

Codex 从设计之初就考虑了安全，采用多层防护策略。

## 安全边界

参考：[Agent approvals & security](https://developers.openai.com/codex/agent-approvals-security)

## 多层安全模型

### Layer 1: 沙箱执行（Sandbox）
- **macOS**: Seatbelt sandbox
- **Linux**: Landlock + bubblewrap
- **Windows**: Windows sandbox
- 三种模式：read-only / workspace-write / danger-full-access

### Layer 2: 批准机制（Approvals）
- 工具执行前的用户确认
- 可配置的批准策略
- 会话级别的信任

### Layer 3: 网络控制（Network Controls）
- 默认禁止网络访问
- 显式启用需要的网络访问
- 沙箱内网络隔离

### Layer 4: 秘密管理（Secrets）
- 不在日志中记录敏感信息
- 记忆生成时删除敏感信息
- 安全的 API Key 存储

### Layer 5: 协作安全（Collaboration）
- 多用户场景的权限控制
- 会话隔离
- 代理委托限制

## 报告安全问题

通过 Bugcrowd 报告：[https://bugcrowd.com/engagements/openai](https://bugcrowd.com/engagements/openai)

## 安全最佳实践

1. 默认使用 `read-only` 沙箱模式
2. 只在需要时使用 `workspace-write`
3. 绝不在非隔离环境中使用 `danger-full-access`
4. 定期审查 `~/.codex/memories/` 中的敏感信息
5. 使用 ChatGPT 账号而不是 API Key（更安全）

## 本章小结

**一句话记住**：Codex 采用多层安全模型 —— 沙箱 + 批准 + 网络控制 + 秘密管理 + 协作安全。

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
- [第十九章：配置系统 —— TOML + JSON Schema](././19-configuration-system.md)
- 第二十章：安全设计 —— 多层安全防护 👈 当前位置
- [第二十一章：架构总结 —— 100+ Crates 的设计哲学](././21-architecture-summary.md) 👉 下一章
