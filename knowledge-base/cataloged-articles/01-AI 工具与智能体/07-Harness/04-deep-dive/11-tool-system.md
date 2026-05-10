# 第十一章：工具系统 —— 从Bash到MCP的工具分发

工具系统是 Harness 的**双手**——决定 Agent 能做什么。这一章深入工具的设计、分发、执行和反馈。

## 工具的本质

一个工具 = 一个**函数签名** + 一个**执行环境**：

```typescript
interface Tool {
  name: string;              // 工具名（模型用来选择）
  description: string;       // 自然语言描述（告诉模型何时使用）
  inputSchema: JSONSchema;   // 参数格式（模型用来填参数）
  execute: (params) => Promise<string>;  // 执行逻辑
  permission: Permission;    // 权限要求
}
```

关键洞察：**工具 Schema 是模型和代码之间的 API 契约**。

## 工具分类

### 按照操作性质分类

| 类别 | 示例 | 性质 |
|------|------|------|
| **只读** | Read, Grep, Glob, Git Status | 安全，可自动允许 |
| **写入** | Write, Edit, Git Commit | 需要确认 |
| **执行** | Bash, Shell | 高风险，需要沙箱 |
| **网络** | WebFetch, WebSearch, API Call | SSRF 风险 |
| **管理** | TaskCreate, AgentSpawn | 影响 Agent 行为 |

### 按照信息来源分类

```
内置工具:
├── 文件: Read, Write, Edit, Glob, Grep
├── 命令: Bash
├── 版本: Git (status, diff, log, commit, branch)
├── 任务: TodoWrite, TaskCreate
└── 网络: WebFetch, WebSearch

扩展工具:
├── MCP: 外部服务通过 MCP 协议提供的工具
└── LSP: 语言服务器提供的语义工具
```

## 工具 Schema 设计原则

### 1. 描述要告诉模型"何时用"，而非"怎么用"

```json
// 坏的描述
"description": "Read a file"

// 好的描述
"description": "Read the contents of a file from the local filesystem.
Use this when you need to understand a file's code, configuration,
or documentation. For searching across multiple files, prefer Grep."
```

### 2. 参数要精确

```json
// 模糊的参数
"parameters": {
  "path": {"type": "string"}
}

// 精确的参数
"parameters": {
  "type": "object",
  "required": ["file_path"],
  "properties": {
    "file_path": {
      "type": "string",
      "description": "The absolute path to the file to read"
    },
    "offset": {
      "type": "integer",
      "description": "Line number to start reading from. Defaults to 1."
    },
    "limit": {
      "type": "integer",
      "description": "Maximum number of lines to read."
    }
  }
}
```

### 3. 错误要可操作

```python
# 坏的错误
def execute(path):
    try:
        return read(path)
    except:
        return "Error"  # 模型不知道发生了什么

# 好的错误
def execute(path):
    try:
        return read(path)
    except FileNotFoundError:
        return f"文件 '{path}' 不存在。请用 Glob 搜索正确路径。"
    except IsADirectoryError:
        return f"'{path}' 是目录不是文件。请用 ls 查看内容。"
    except PermissionError:
        return f"没有读取 '{path}' 的权限。请检查文件权限。"
```

## 工具执行的生命周期

```
模型输出 tool_use
    │
    ▼
┌──────────────────┐
│ 1. 解析 tool_use │  提取 name + input
└──────────────────┘
    │
    ▼
┌──────────────────┐
│ 2. 权限检查       │  deny? ask? allow?
└──────────────────┘
    │ (通过)
    ▼
┌──────────────────┐
│ 3. 参数验证       │  Schema validation
└──────────────────┘
    │ (通过)
    ▼
┌──────────────────┐
│ 4. 执行           │  调用实际函数
└──────────────────┘
    │
    ▼
┌──────────────────┐
│ 5. 结果格式化     │  截断、结构化、错误包装
└──────────────────┘
    │
    ▼
┌──────────────────┐
│ 6. 注入上下文     │  作为 tool_result 消息
└──────────────────┘
```

## 执行环境：为什么需要隔离

| 方式 | 示例 | 安全等级 |
|------|------|---------|
| 直接执行 | 进程内调用 | 无保护 |
| 子进程 | `subprocess.run(cmd)` | 同一用户权限 |
| 权限包装 | 专用用户执行 | 有限保护 |
| 容器 | Docker 隔离 | 较好隔离 |
| OS 沙箱 | Seatbelt/Landlock | 强隔离 |

Codex 选择了 OS 沙箱（最安全），Claude Code 选择了权限管道（最灵活）。没有对错——取决于场景需求。

## 工具输出的处理

工具输出需要经过处理才能返回给模型：

```python
def format_tool_result(raw: str, tool_name: str) -> str:
    # 1. 截断过大的输出
    if len(raw) > 100_000:
        raw = raw[:50_000] + f"\n... (截断，共 {len(raw)} 字符)"

    # 2. 结构化包装
    return f"""工具: {tool_name}
结果:
{raw}

---
以上是工具 '{tool_name}' 的执行结果。
请基于此结果继续你的工作。"""
```

关键原则：
- **截断要告知**：告诉模型内容被截断了，让它能决定是否要更精确地查询
- **返回上下文**：提醒模型这是哪个工具的结果（多工具并行时很重要）

## 本章小结

- 一个工具 = Schema（模型看的）+ Execute（代码跑的）+ Permission（安全网关）
- 工具描述要告诉模型"何时用"，参数要精确，错误要可操作
- 工具执行生命周期：解析 → 权限 → 验证 → 执行 → 格式化 → 注入
- 执行环境的隔离等级决定了 Agent 的安全边界
- 工具输出需要截断和结构化，帮助模型高效利用
- 下一章：权限系统——deny→ask→allow 的安全边界

---

**系列目录**：
- [第十章：Agent Loop —— Harness的心跳](./10-agent-loop.md)
- 第十一章：工具系统 —— 从Bash到MCP的工具分发 👈 当前位置
- [第十二章：权限系统 —— deny→ask→allow的安全边界](./12-permission-system.md) 👉 下一章
- [第十三章：上下文管理](./13-context-management.md)
- [第十四章：MCP集成](./14-mcp-integration.md)
- [第十五章：技能系统](./15-skills-system.md)
