# 第二十一章：架构总结 —— 100+ Crates 的设计哲学

让我们退一步，总结 Codex 的整体架构设计和核心设计哲学。

## 设计原则

### 1. 模块化极致 —— 100+ Crates
Codex 不是一个大的单体应用，而是 100+ 个小 crate 的组合。每个 crate 职责单一，可独立测试和演进。

### 2. 抵制 Core 膨胀 —— AGENTS.md 明确指示
> 抵制向 codex-core 添加代码！

新功能应该考虑：
- 是否有现有其他 crate 适合放
- 是否该创建新 crate

### 3. 优先使用原生 RPITIT 而不是 async-trait
Rust  trait 中避免 `#[async_trait]` 和 `#[allow(async_fn_in_trait)]`，优先使用原生的 RPITIT。

### 4. 测试优先 —— 快照测试 + 单元测试
- TUI 使用 insta 快照测试
- 每个模块有对应的 `*_tests.rs`
- 集成测试使用 core-test-support

### 5. Schema 从代码生成 —— 单一事实源
- config schema: `just write-config-schema`
- app-server schema: `just write-app-server-schema`
- hooks schema: `just write-hooks-schema`

## 核心 Crate 图谱

### 用户界面层
- **tui**: Ratatui 终端 UI
- **cli**: 命令行入口（codex / codex exec / codex mcp / codex sandbox）
- **app-server**: IDE 集成后端

### 业务逻辑层
- **core**: 核心编排（但尽量少加代码！）
- **state**: SQLite 状态持久化
- **thread-store**: 对话存储

### 能力层
- **tools**: 工具原语（从 core 提取中）
- **skills**: 技能注入
- **plugin**: 插件系统
- **hooks**: 事件钩子
- **memories/read**: 记忆读路径
- **memories/write**: 记忆写路径

### 执行层
- **exec**: Headless 执行
- **execpolicy**: 执行策略
- **sandboxing**: 沙箱抽象
- **linux-sandbox**: Linux 沙箱
- **windows-sandbox-rs**: Windows 沙箱
- **shell-escalation**: 权限提升

### 协议与集成层
- **protocol**: 核心协议
- **app-server-protocol**: App Server v2 协议
- **app-server-client**: App Server 客户端
- **app-server-transport**: App Server 传输
- **app-server-test-client**: App Server 测试客户端
- **codex-mcp**: MCP 集成
- **mcp-server**: MCP 服务器模式
- **rmcp-client**: RMCP 客户端
- **backend-client**: 后端客户端
- **chatgpt**: ChatGPT 集成

## 工作流示例：一个对话如何流过系统

```
用户输入
  ↓
TUI (tui crate)
  ↓
Core 编排 (core crate)
  ↓
├─→ Skills 注入 (skills crate)
├─→ Tools 调用 (tools crate)
├─→ Hooks 触发 (hooks crate)
├─→ Exec 执行 (exec/execpolicy crate)
│   └─→ 平台沙箱 (linux-sandbox / Seatbelt)
├─→ MCP 集成 (codex-mcp crate)
└─→ Memory 流水线 (memories/read + memories/write)
     ↓
State DB (state crate)
     ↓
TUI 渲染结果 (tui crate)
     ↓
用户看到输出
```

## 开发准则回顾（来自 AGENTS.md）

1. **Crate 命名**: 前缀 `codex-`，如 `codex-core`
2. **Format!**: 总是内联变量到 `format!`
3. **安装依赖**: 先安装 repo 依赖的命令
4. **不要碰沙箱网络禁用**: `CODEX_SANDBOX_NETWORK_DISABLED`
5. **Collapse if 语句**: 按照 clippy
6. **布尔/Option 参数**: 避免，使用 enum/命名方法/新类型
7. **参数注释 lint**: 透明字面量需要 `/* param */` 注释
8. **Match 穷尽**: 避免 wildcard arms
9. **新 Trait**: 必须有文档注释
10. **Trait 中的异步**: 优先 RPITIT + Send bound
11. **测试**: 优先整个对象相等比较
12. **Config Toml**: 变更后运行 `just write-config-schema`
13. **MCP**: 优先使用 `codex-mcp`
14. **Cargo.toml**: 变更后运行 `just bazel-lock-update`
15. **Bazel build.rs**: 使用 `compile_data`/`build_script_data`
16. **不要创建只引用一次的小助手方法**
17. **避免大模块**: 目标是 <500 行（不含测试），>800 行考虑拆分
18. **修改后运行 just fmt**: 自动格式化，不用批准
19. **修复后不用重跑测试**: 只在实现变更时跑

## 从源码中学到的关键洞见

1. **邀请制贡献**: 降低维护成本，保证质量
2. **dogfooding**: Codex 用自己开发自己
3. **两阶段记忆**: 可扩展 + 安全一致的平衡
4. **Schema 从代码生成**: 避免文档与代码脱节
5. **抵制核心膨胀**: 主动向外拆代码
6. **多沙箱策略**: 每个平台用最佳方案，不是最低公约数

## 本章小结

**一句话记住**：Codex 是 100+ 个小 crate 的模块化组合，遵循严格的设计准则，每个部分都可独立测试和演进。

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
- [第二十章：安全设计 —— 多层安全防护](././20-security.md)
- 第二十一章：架构总结 —— 100+ Crates 的设计哲学 👈 当前位置
