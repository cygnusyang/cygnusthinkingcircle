# 第十一章：State 系统 —— SQLite 数据库持久化

Codex 记住了你上周的 17 个会话，不是存在内存里，而是存在 SQLite 数据库里。重启 Codex 后一切都还在。

Codex 使用 SQLite 数据库来持久化会话状态、记忆、分析等数据。

`★ Insight ─────────────────────────────────────`
**SQLite 的版本化演进艺术**
31个迁移文件不仅记录了数据结构变化，更体现了系统的演进历程。每个迁移文件都是系统成长的"里程碑"，支持零停机升级。这种设计让 Codex 可以在用户不知情的情况下平滑演进，旧数据库自动迁移到新版本。
`─────────────────────────────────────────────────`

## State Crate 结构

**位置**：`source/codex/codex-rs/state/`

```
state/
├── src/                     # 源代码
├── migrations/              # 数据库迁移（31 个！）
└── logs_migrations/         # 日志迁移
```

## 数据库迁移

使用 SQL 迁移文件管理数据库 schema 版本，从 001 到 031，说明这是一个不断演进的系统。

迁移文件例子（简化版）：
```sql
-- 001_initial.up.sql
CREATE TABLE rollouts (
    id TEXT PRIMARY KEY,
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL
);

-- 002_add_memories.up.sql
CREATE TABLE memories (
    id TEXT PRIMARY KEY,
    rollout_id TEXT NOT NULL REFERENCES rollouts(id),
    raw_memory TEXT NOT NULL,
    generated_at INTEGER NOT NULL
);
```

## 日志查看

提供了一个日志客户端：

```bash
just log
```

可以查看状态 SQLite 数据库中的日志。

## 数据模型

从迁移文件数量可以推测，数据库包含：
- 会话（rollouts）
- 记忆（Phase 1、Phase 2）
- 分析数据
- 配置状态
- 等等...

`★ Insight ─────────────────────────────────────`
**State DB 的协调者角色**
State DB 不仅仅是数据存储，更是分布式协调系统。Phase 1 的任务租用和 Phase 2 的全局锁都在这里实现，确保多进程环境下不会产生冲突。这种设计让 Codex 可以安全地运行多个实例，同时共享同一个记忆库。
`─────────────────────────────────────────────────`

## 并发与协调

State DB 用于：
- Phase 1 任务租用（防止重复工作）
- Phase 2 全局锁
- 记忆使用计数和最后使用时间跟踪
- 水印追踪

## 实际例子：数据库位置

数据库文件通常在这里：
- **macOS/Linux**: `~/.codex/state.db`
- **Windows**: `%USERPROFILE%\.codex\state.db`

## 实战案例：查看你的记忆库

```bash
# 查看数据库中的会话数量
sqlite3 ~/.codex/state.db "SELECT COUNT(*) FROM rollouts;"

# 查看最近生成的记忆
sqlite3 ~/.codex/state.db "
SELECT id, generated_at, substr(raw_memory, 1, 100)
FROM memories
ORDER BY generated_at DESC
LIMIT 5;
"
```

## 避坑指南

### 坑：直接修改数据库文件

❌ **错误做法**：用 SQLite GUI 直接编辑 state.db
❌ **原因**：可能损坏正在运行的进程
❌ **后果**：Codex 可能无法启动或数据丢失

✅ **正确做法**：使用只读查询查看数据，修改通过 Codex API

### 坑：备份时忽略数据库

❌ **错误做法**：只备份 `~/.codex/memories/`，不备份 `state.db`
❌ **原因**：缺少协调数据，记忆系统无法恢复
❌ **后果**：记忆系统异常，Phase 1/Phase 2 无法正常运行

✅ **正确做法**：
```bash
# 备份完整状态
tar -czf codex-backup-$(date +%Y%m%d).tar.gz \
  ~/.codex/state.db \
  ~/.codex/memories/ \
  ~/.config/codex/config.toml
```

## 本章小结

**一句话记住**：State 系统使用 SQLite + 迁移来持久化所有数据，包括会话、记忆和协调信息。

**核心要点**：
1. **版本化迁移**：31个迁移文件支持零停机升级
2. **协调功能**：任务租用、全局锁防止并发冲突
3. **数据备份**：记住同时备份 state.db 和 memories/

**下一步**：了解 Tools 系统如何从 core 中独立出来（第十二章）。

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
- 第十一章：State 系统 —— SQLite 数据库持久化 👈 当前位置
- [第十二章：Tools 系统 —— 从 codex-core 独立出的工具原语](./../04-advanced/12-tools-system.md) 👉 下一章
- [第十三章：Exec 系统 —— 安全沙箱执行的深层设计](./../04-advanced/13-exec-system.md)
- [第十四章：技能系统深入 —— 50+ 内置技能与实战场景](./../04-advanced/14-skills-in-depth.md)
- [第十五章：技能系统 —— 给 AI 注入专业知识](./../05-plugins/15-skills-system.md)
- [第十六章：Hooks 系统 —— 事件驱动的自动化](./../05-plugins/16-hooks-system.md)
- [第十七章：Plugin 系统 —— Codex 的扩展机制](./../05-plugins/17-plugin-system.md)
- [第十八章：开发工作流 —— 如何构建和测试 Codex](./../06-enterprise/18-development-workflow.md)
- [第十九章：配置系统 —— TOML + JSON Schema](./../06-enterprise/19-configuration-system.md)
- [第二十章：安全设计 —— 多层安全防护](./../06-enterprise/20-security.md)
- [第二十一章：架构总结 —— 100+ Crates 的设计哲学](./../06-enterprise/21-architecture-summary.md)
