# 第十五章：Tools 系统 —— 从 codex-core 独立出的工具原语

Codex 的 Tools 系统正在进行从 `codex-core` 的独立迁移，是一个正在演进的系统。

## Tools Crate 结构

**位置**：`source/codex/codex-rs/tools/`

```
tools/
├── README.md              # 设计文档（必读！）
└── src/                  # 46 个模块！
```

## 愿景

随着时间推移，这个 crate 应该容纳多个消费者共享的面向工具的原语：
- Schema 和 spec 数据模型
- 工具输入/输出解析助手
- 不依赖 `codex-core` 的工具元数据和兼容性垫片
- 多个 crate 需要的其他小范围实用代码

## 非目标

同样重要的是：
- 不要过早将 `codex-core` 编排移到这里
- 不要将 `Session`/`TurnContext`/批准流/运行时执行逻辑拉到这个 crate，除非这些依赖先被拆分为稳定的共享接口
- 不要将这个 crate 变成无关帮助代码的混杂袋

## 迁移方法

预期的迁移形式是：
1. 将低耦合工具原语移到这里
2. 切换非核心消费者直接依赖 `codex-tools`
3. 在更新下游调用站点时，将兼容性敏感的适配器保留在 `codex-core`
4. 只在 crate 边界清晰且可独立测试后才提取更高级别的工具基础设施

这意味着在过渡期间 `codex-core` 暂时从 `codex-tools` 重新导出类型或助手是正常的。

## 当前包含的内容（从 core 提取的）

### Schema 和 Spec 类型
- `JsonSchema`
- `AdditionalProperties`
- `ToolDefinition`
- `ToolSpec`
- `ConfiguredToolSpec`

### Responses API 工具
- `ResponsesApiTool`
- `FreeformTool`
- `FreeformToolFormat`
- `LoadableToolSpec`
- `ResponsesApiWebSearchFilters`
- `ResponsesApiWebSearchUserLocation`
- `ResponsesApiNamespace`
- `ResponsesApiNamespaceTool`

### Builder
- code-mode `ToolSpec` 适配器和 `exec`/`wait` spec 构建器
- MCP resource、`list_dir`、`test_sync_tool` spec 构建器
- 本地主机工具 spec 构建器：shell/exec/request-permissions/view-image
- 协作和 agent-job `ToolSpec` 构建器：spawn/send/wait/close、`request_user_input`、CSV fanout/reporting
- 可发现工具模型、客户端过滤、`ToolSpec` 构建器：`tool_search` 和 `request_plugin_install`

### 解析和转换
- `parse_tool_input_schema()`
- `parse_dynamic_tool()`
- `parse_mcp_tool()`
- `create_tools_json_for_responses_api()`
- `mcp_call_tool_result_output_schema()`
- `tool_definition_to_responses_api_tool()`
- `dynamic_tool_to_loadable_tool_spec()`
- `dynamic_tool_to_responses_api_tool()`
- `mcp_tool_to_responses_api_tool()`
- `mcp_tool_to_deferred_responses_api_tool()`
- `augment_tool_spec_for_code_mode()`
- `tool_spec_to_code_mode_tool_definition()`

## Crate 约定

这个 crate 应该从一开始就有比 `core/src/tools` 更严格的结构：
- `src/lib.rs` 应该只保持导出
- 业务逻辑应该在命名的模块文件中，如 `foo.rs`
- `foo.rs` 的单元测试应该在同级的 `foo_tests.rs` 中
- 实现文件应该用以下方式连接测试：

```rust
#[cfg(test)]
#[path = "foo_tests.rs"]
mod tests;
```

如果这个 crate 开始积累需要来自 `codex-core` 的运行时状态的代码，那就是一个信号，表明在添加更多之前需要重新审查提取边界。

## 本章小结

**一句话记住**：Tools 系统正在从 codex-core 中提取独立，遵循严格的模块化约定。

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
- 第十五章：Tools 系统 —— 从 codex-core 独立出的工具原语 👈 当前位置
- [第十章：技能系统 —— 给 AI 注入专业知识](./../05-plugins/10-skills-system.md)
- [第十二章：Hooks 系统 —— 事件驱动的自动化](./../05-plugins/12-hooks-system.md)
- [第十一章：开发工作流 —— 如何构建和测试 Codex](./../06-enterprise/11-development-workflow.md)
