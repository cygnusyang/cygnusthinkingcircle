# 第十六章：Exec 系统 —— 安全沙箱执行的深层设计

Codex 的执行系统是其安全性的核心，由多个专门的 crate 组成，每层都有特定的职责。

## 执行相关 Crates

```
codex-rs/
├── exec/              # Headless CLI，用于自动化
├── execpolicy/        # 执行策略定义
├── linux-sandbox/     # Linux 沙箱实现
├── shell-escalation/  # 权限提升
└── (macOS sandbox 嵌入在 core 中)
```

## 三层沙箱模型

### 1. execpolicy —— 策略定义

定义沙箱的安全策略：
- 可读路径
- 可写路径
- 可执行路径
- 网络访问权限
- 等等...

### 2. 平台特定实现

- **macOS**: Seatbelt sandbox（内置在 core 中）
- **Linux**: Landlock + bubblewrap
- **Windows**: Windows sandbox

### 3. shell-escalation —— 权限提升

处理需要更高权限的场景。

## 沙箱模式

Codex 支持三种沙箱模式：

### 1. read-only（默认）
- 仅允许读取文件
- 无网络访问
- 最安全

### 2. workspace-write
- 允许读写当前工作区
- 仍无网络访问
- `.git` 目录保持只读

### 3. danger-full-access
- 完全访问权限
- 仅在容器/隔离环境中使用
- 有警告

## 命令行选择沙箱

```bash
codex --sandbox read-only
codex --sandbox workspace-write
codex --sandbox danger-full-access
```

或者在配置中持久化：
```toml
sandbox_mode = "workspace-write"
```

## 测试沙箱

Codex 提供命令测试沙箱：

```bash
# macOS
codex sandbox macos ls

# Linux
codex sandbox linux ls

# Windows
codex sandbox windows dir
```

## Linux 沙箱细节

Linux 沙箱实现很精巧：
- 优先使用 PATH 中找到的第一个 `bwrap`（不在当前工作目录中）
- 如果 `bwrap` 存在但太旧不支持 `--argv0`，继续使用系统 bubblewrap 并切换到无 `--argv0` 兼容路径
- 如果 `bwrap` 缺失，回退到编译进二进制的 vendored bubblewrap
- WSL2 使用正常的 Linux bubblewrap 路径
- WSL1 不支持 bubblewrap 沙箱

## macOS Seatbelt 细节

macOS 使用原生的 Seatbelt sandbox：
- sandbox-exec 配置
- 可写根目录配置
- `.git` 保持只读
- 遗留的用户偏好读取权限

## exec crate —— Headless 模式

`exec` crate 提供无 UI 的执行模式：
- 用于自动化场景
- `codex exec` 命令的实现
- 支持从 stdin 读取输入
- 支持 --ephemeral 不保存会话

## 本章小结

**一句话记住**：Exec 系统是多层安全设计 —— 策略定义 + 平台特定沙箱 + 权限提升，三种安全级别可选。

---

**系列目录**：
- [第一章：Codex 是什么 —— OpenAI 的本地编码代理](./../01-intro/01-what-is-codex.md)
- [第二章：安装与上手 —— npm/brew/二进制三种方式](./../01-intro/02-installation-setup.md)
- [第三章：认证与配置 —— ChatGPT 账号 vs API Key](./../01-intro/03-authentication.md)
- [第四章：TUI 基础 —— 终端 UI 的交互方式](./../02-core/04-tui-basics.md)
- [第五章：codex exec —— 非交互式编程执行](./../02-core/05-codex-exec.md)
- [第六章：沙箱系统 —— 安全执行命令](./../02-core/06-sandbox.md)
- [第七章：MCP 客户端 —— 连接外部工具](./../03-cli/07-mcp-client.md)
- [第八章：架构概览 —— 100+ Crates 的模块化设计](./08-architecture-overview.md)
- [第九章：TUI 深入 —— Ratatui 应用的构建方式](./09-tui-in-depth.md)
- [第十三章：Memories 系统 —— AI 的长期记忆](./13-memories-system.md)
- [第十四章：State 系统 —— SQLite 数据库持久化](./14-state-system.md)
- [第十五章：Tools 系统 —— 从 codex-core 独立出的工具原语](./15-tools-system.md)
- 第十六章：Exec 系统 —— 安全沙箱执行的深层设计 👈 当前位置
- [第十章：技能系统 —— 给 AI 注入专业知识](./../05-plugins/10-skills-system.md)
- [第十二章：Hooks 系统 —— 事件驱动的自动化](./../05-plugins/12-hooks-system.md)
- [第十一章：开发工作流 —— 如何构建和测试 Codex](./../06-enterprise/11-development-workflow.md)
