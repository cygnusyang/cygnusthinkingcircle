# 第十一章：开发工作流 —— 如何构建和测试 Codex

虽然 Codex 主要是邀请制贡献，但了解它的开发工作流仍然很有价值。

## 构建系统

Codex 使用两个构建系统：

### 1. Cargo（本地开发）

标准的 Rust/Cargo 工作流。

### 2. Bazel（CI 和发布）

用于官方构建和发布。

## Just 命令

`justfile` 提供了便捷的开发命令：

| 命令 | 作用 |
|-----|------|
| `just codex` | 运行 Codex |
| `just exec` | 运行 codex exec |
| `just fmt` | 格式化代码 |
| `just fix` | 自动修复 clippy 警告 |
| `just test` | 运行测试（使用 cargo-nextest） |
| `just write-config-schema` | 生成配置 JSON Schema |
| `just write-app-server-schema` | 生成 app-server 协议 Schema |

## 开发工作流（受邀贡献者）

参考 `docs/contributing.md`：

### 1. 创建 Topic Branch

```bash
git checkout -b feat/your-feature main
```

### 2. 编写代码

遵循 `AGENTS.md` 中的指导原则：
- 保持 crate 小而专注
- 不要往 `codex-core` 加东西（抗拒！）
- 使用原生 RPITIT 而不是 `async-trait`
- 保持 match 语句详尽
- 使用 `just fmt` 格式化
- 写测试

### 3. 运行测试

```bash
# 运行特定 crate 的测试
cargo test -p codex-tui

# 运行所有测试
just test
```

### 4. 检查 Lint

```bash
just fix -p codex-tui
```

### 5. 生成 Schema（如需要）

```bash
# 更新配置 schema
just write-config-schema

# 更新 app-server schema
just write-app-server-schema
```

### 6. 提交 PR

- 原子提交（每个 commit 能编译，测试通过）
- 填写 PR 模板：What? Why? How?
- 确保 CI 检查通过

## 特殊 Lint：Argument Comment

Codex 有一个自定义 lint 要求透明字面量参数加注释：

```rust
// 错误
foo(false, None, 42);

// 正确
foo(/* enable_cache */ false, /* max_retries */ None, /* timeout_secs */ 42);
```

运行检查：
```bash
just argument-comment-lint
```

## 快照测试

TUI 使用 `insta` 进行快照测试：

```bash
# 运行测试生成新快照
cargo test -p codex-tui

# 检查待处理的快照
cargo insta pending-snapshots -p codex-tui

# 接受快照
cargo insta accept -p codex-tui
```

## Codex 辅助开发

有趣的是，Codex 自己也用于开发 Codex！这是一个 dogfooding 的典型案例。

## 本章小结

**一句话记住**：用 Cargo 本地开发，Bazel 官方构建，just 命令简化工作流。

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
- [第十章：技能系统 —— 给 AI 注入专业知识](./../05-plugins/10-skills-system.md)
- 第十一章：开发工作流 —— 如何构建和测试 Codex 👈 当前位置
