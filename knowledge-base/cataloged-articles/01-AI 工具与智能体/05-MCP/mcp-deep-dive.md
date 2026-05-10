# MCP 开发者指南：从零构建你的第一个 MCP Server

> 本文站在开发者视角，带你从"写一个最简单的 MCP Server"开始，逐步理解核心概念，最终掌握完整的开发实践。

---

## 目录

1. [快速上手：5 分钟写出第一个 MCP Server](#1-快速上手5-分钟写出第一个-mcp-server)
2. [理解 Tools：让 AI 调用你的函数](#2-理解-tools让-ai-调用你的函数)
3. [理解 Resources：为 AI 提供背景数据](#3-理解-resources为-ai-提供背景数据)
4. [理解 Prompts：为用户预设交互模板](#4-理解-prompts为用户预设交互模板)
5. [深入核心：架构与协议](#5-深入核心架构与协议)
6. [传输选择：stdio vs Streamable HTTP](#6-传输选择stdio-vs-streamable-http)
7. [进阶实践：认证、日志、进度追踪](#7-进阶实践认证日志进度追踪)
8. [配置与部署：在 Claude 中使用](#8-配置与部署在-claude-中使用)

---

## 1. 快速上手：5 分钟写出第一个 MCP Server

让我们直接开始——先写出一个能运行的 MCP Server，然后再理解它是怎么工作的。

### 1.1 选择你的语言

MCP 官方提供了多个语言的 SDK，我们先用 **Python**（最简单）：

```bash
pip install mcp
# 或使用 uv
uv add mcp
```

### 1.2 第一个 Server：天气查询

创建 `weather_server.py`：

```python
from mcp.server.fastmcp import FastMCP

# 第一步：创建 Server 实例
mcp = FastMCP("天气助手")

# 第二步：定义一个 Tool（让 AI 可以调用的函数）
@mcp.tool()
def get_weather(city: str) -> dict:
    """获取指定城市的天气信息"""
    weather_db = {
        "北京": {"temperature": "22°C", "condition": "晴转多云"},
        "上海": {"temperature": "26°C", "condition": "多云"},
        "深圳": {"temperature": "28°C", "condition": "晴"},
    }
    return weather_db.get(city, {"error": f"暂不支持城市: {city}"})

# 第三步：运行 Server
if __name__ == "__main__":
    mcp.run()
```

### 1.3 测试你的 Server

使用 MCP Inspector 调试：

```bash
npx @modelcontextprotocol/inspector python weather_server.py
```

你会看到一个 Web 界面，可以：
- 查看 Server 提供了哪些 Tool
- 手动调用 Tool 测试
- 查看请求和响应的原始数据

### 1.4 发生了什么？

恭喜！你刚写了一个完整的 MCP Server。让我们拆解一下：

| 部分 | 作用 |
|------|------|
| `FastMCP("天气助手")` | 创建 Server，命名为"天气助手" |
| `@mcp.tool()` | 装饰器：把函数注册为 MCP Tool |
| `def get_weather(...)` | 实际的业务逻辑 |
| `mcp.run()` | 启动 Server，默认用 stdio 传输 |

**关键概念：什么是 MCP？**

MCP（Model Context Protocol）是一个**标准协议**，它让你的代码（Server）可以被 AI 应用（Host，如 Claude Desktop）以统一的方式调用。

```
┌─────────────────┐         标准协议          ┌─────────────────┐
│  Claude Desktop │ ◄───────────────────────► │  你的 Server   │
│   (Host)        │   JSON-RPC over stdio    │  (weather.py)  │
└─────────────────┘                           └─────────────────┘
```

---

## 2. 理解 Tools：让 AI 调用你的函数

Tool 是 MCP 最常用的原语——它是**AI 模型可以自主决定调用的函数**。

### 2.1 Tool 的工作流程

```
用户提问："北京天气怎么样？"
    │
    ▼
Claude 分析问题 → "需要调用 get_weather 工具"
    │
    ▼
Claude 调用 Tool（通过 MCP 协议）
    │
    ▼
你的 Server 执行函数 → 返回结果
    │
    ▼
Claude 用结果回答用户
```

### 2.2 写好 Tool 的要点

**要点 1：文档字符串很重要**

```python
@mcp.tool()
def get_weather(city: str) -> dict:
    """获取指定城市的天气信息

    Args:
        city: 城市中文名，如"北京"、"上海"、"深圳"
    """
    # AI 靠这个文档字符串理解：
    # 1. 这个工具是做什么的
    # 2. 参数应该传什么
```

**要点 2：参数类型要明确**

```python
# FastMCP 会自动从类型注解生成 JSON Schema
@mcp.tool()
def search_products(
    keyword: str,              # 必填字符串
    category: str = "all",     # 可选，默认值
    limit: int = 10,           # 可选整数
    in_stock: bool = True      # 可选布尔值
) -> list:
    """搜索产品"""
    pass
```

**要点 3：返回值要结构化**

```python
# 推荐返回 dict 或 list，方便 AI 理解
@mcp.tool()
def get_user(id: str) -> dict:
    return {
        "id": id,
        "name": "张三",
        "email": "zhangsan@example.com",
        "is_active": True
    }
```

### 2.3 更多 Tool 示例

**示例 1：数据库查询**

```python
@mcp.tool()
def query_users(min_age: int = 0, max_age: int = 150) -> list:
    """查询指定年龄范围的用户"""
    sql = "SELECT * FROM users WHERE age BETWEEN ? AND ?"
    return db.execute(sql, [min_age, max_age]).fetchall()
```

**示例 2：文件操作（带安全检查）**

```python
import os
from pathlib import Path

ALLOWED_ROOT = Path("/safe/directory")

@mcp.tool()
def read_file(path: str) -> str:
    """读取文件内容（仅限安全目录）"""
    file_path = (ALLOWED_ROOT / path).resolve()

    # 安全检查：防止路径遍历攻击
    if not str(file_path).startswith(str(ALLOWED_ROOT)):
        return "错误：禁止访问该路径"

    if not file_path.exists():
        return "错误：文件不存在"

    return file_path.read_text()
```

**示例 3：调用外部 API**

```python
import httpx

@mcp.tool()
def search_github(keyword: str, limit: int = 5) -> list:
    """搜索 GitHub 仓库"""
    response = httpx.get(
        "https://api.github.com/search/repositories",
        params={"q": keyword, "per_page": limit}
    )
    items = response.json()["items"]
    return [
        {
            "name": item["full_name"],
            "description": item["description"],
            "url": item["html_url"],
            "stars": item["stargazers_count"]
        }
        for item in items
    ]
```

---

## 3. 理解 Resources：为 AI 提供背景数据

Resource 是**提供给 AI 作为上下文的只读数据**——就像给 AI 一份参考材料。

### 3.1 Resource vs Tool：什么时候用哪个？

| 场景 | 用 Tool | 用 Resource |
|------|--------|------------|
| 需要执行操作（写数据库、发邮件） | ✅ | ❌ |
| 提供背景信息（配置、文档） | ❌ | ✅ |
| AI 决定何时调用 | ✅ | 通常由用户/应用决定 |
| 可能有副作用 | ✅ | ❌（只读） |

### 3.2 定义 Resource

```python
@mcp.resource("config://app-settings")
def get_app_config() -> str:
    """提供应用配置作为上下文"""
    return """
# 应用配置
- 数据库：PostgreSQL (localhost:5432)
- 缓存：Redis (localhost:6379)
- 环境：生产
"""
```

### 3.3 参数化 Resource（URI 模板）

Resource 支持 URI 模板，可以动态获取数据：

```python
@mcp.resource("user://{user_id}/profile")
def get_user_profile(user_id: str) -> str:
    """获取指定用户的个人资料"""
    user = db.get_user(user_id)
    return f"""
用户 ID: {user_id}
姓名: {user.name}
邮箱: {user.email}
注册时间: {user.created_at}
"""
```

### 3.4 Resource 完整示例：项目文档助手

```python
from mcp.server.fastmcp import FastMCP
from pathlib import Path

mcp = FastMCP("项目文档助手")
PROJECT_ROOT = Path("/my/project")

# ─── Resource：提供 README ───
@mcp.resource("doc://README")
def get_readme() -> str:
    """项目 README 文档"""
    readme = PROJECT_ROOT / "README.md"
    return readme.read_text() if readme.exists() else "无 README"

# ─── Resource：提供目录结构 ───
@mcp.resource("project://structure")
def get_project_structure() -> str:
    """项目目录结构"""
    tree = []
    for path in sorted(PROJECT_ROOT.rglob("*")):
        if ".git" in path.parts:
            continue
        rel = path.relative_to(PROJECT_ROOT)
        indent = "  " * (len(rel.parts) - 1)
        prefix = "📁" if path.is_dir() else "📄"
        tree.append(f"{indent}{prefix} {rel.name}")
    return "\n".join(tree)

# ─── Tool：搜索代码 ───
@mcp.tool()
def search_code(keyword: str) -> list[str]:
    """在代码库中搜索"""
    results = []
    for path in PROJECT_ROOT.rglob("*.py"):
        if keyword in path.read_text():
            results.append(str(path.relative_to(PROJECT_ROOT)))
    return results
```

---

## 4. 理解 Prompts：为用户预设交互模板

Prompt 是**可复用的交互模板**——帮助用户快速触发常用的 AI 工作流。

### 4.1 什么时候用 Prompt？

- 代码审查
- 翻译
- 文档生成
- 数据总结
- 任何标准化的交互流程

### 4.2 定义 Prompt

```python
@mcp.prompt()
def code_review(code: str, language: str = "python") -> str:
    """代码审查模板"""
    return f"""请审查以下 {language} 代码，从以下方面给出建议：

1. 🔒 安全性：有没有安全漏洞？
2. ⚡ 性能：有没有性能问题？
3. 📝 代码风格：是否符合最佳实践？
4. 🐛 潜在 Bug：有没有逻辑错误？

代码：
```{language}
{code}
```
"""
```

### 4.3 Prompt 的使用方式

在 Claude Desktop 中，用户会看到 Prompt 作为菜单选项：
1. 用户选择"代码审查"
2. 界面弹出表单让用户填写 `code` 和 `language`
3. 提交后，Prompt 生成的消息自动发送给 Claude

### 4.4 多轮对话 Prompt

Prompt 可以返回多轮对话消息：

```python
from mcp.types import TextContent, Message

@mcp.prompt()
def pair_programming(task: str) -> list[Message]:
    """结对编程助手（多轮对话）"""
    return [
        Message(
            role="user",
            content=TextContent(
                type="text",
                text=f"我们一起完成这个任务：{task}"
            )
        ),
        Message(
            role="assistant",
            content=TextContent(
                type="text",
                text="好的！让我先了解一下项目结构..."
            )
        )
    ]
```

---

## 5. 深入核心：架构与协议

现在我们已经会写代码了，让我们深入理解 MCP 的工作原理。

### 5.1 核心架构

```
┌─────────────────────────────────────────────────────────┐
│          Host (Claude Desktop / Claude Code)            │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Client 1   │  │   Client 2   │  │   Client 3   │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
└─────────┼─────────────────┼─────────────────┼───────────┘
          │                 │                 │
          │ 1:1 连接        │ 1:1 连接        │ 1:1 连接
          ▼                 ▼                 ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│  Weather Server  │ │  GitHub Server   │ │  File Server     │
└──────────────────┘ └──────────────────┘ └──────────────────┘
```

| 角色 | 作用 |
|------|------|
| **Host** | AI 应用（Claude Desktop），管理整个生态 |
| **Client** | Host 创建，每个 Client 只连一个 Server |
| **Server** | 你的代码，提供 Tools/Resources/Prompts |

**关键点：1:1 隔离**

每个 Client-Server 对是独立的——这是安全设计，防止 Server 之间互相访问数据。

### 5.2 协议基础：JSON-RPC 2.0

MCP 使用 **JSON-RPC 2.0** 作为通信格式。

你不需要手写 JSON，但理解它会帮助你调试：

```json
// Client → Server：列出所有 Tool
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list",
  "params": {}
}

// Server → Client：返回 Tool 列表
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tools": [
      {
        "name": "get_weather",
        "description": "获取指定城市的天气信息",
        "inputSchema": {
          "type": "object",
          "properties": {
            "city": { "type": "string" }
          },
          "required": ["city"]
        }
      }
    ]
  }
}
```

### 5.3 生命周期

MCP 会话有明确的三个阶段：

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│  初始化     │ ─────→  │  运行中     │ ─────→  │  关闭       │
│ Initialize  │         │  Operation  │         │  Shutdown   │
└─────────────┘         └─────────────┘         └─────────────┘
```

**初始化阶段：能力协商**

这是最重要的一步——Client 和 Server 互相告诉对方："我支持什么功能"。

```python
# 你不需要手写这段代码，SDK 会处理
# 但理解它很有帮助

# Client → Server
{
  "method": "initialize",
  "params": {
    "protocolVersion": "2025-03-26",
    "capabilities": {
      "sampling": {},        // Client 支持让 AI 生成内容
      "roots": {}            // Client 支持根目录管理
    },
    "clientInfo": { "name": "Claude Desktop", "version": "1.0" }
  }
}

# Server → Client
{
  "result": {
    "protocolVersion": "2025-03-26",
    "capabilities": {
      "tools": {},          // Server 提供 Tool
      "resources": {},      // Server 提供 Resource
      "prompts": {}         // Server 提供 Prompt
    },
    "serverInfo": { "name": "天气助手", "version": "1.0" }
  }
}
```

---

## 6. 传输选择：stdio vs Streamable HTTP

MCP 支持多种传输方式，选择合适的取决于你的部署场景。

### 6.1 stdio：本地工具首选

```python
# 默认就是 stdio
mcp.run()
# 或显式指定
mcp.run(transport="stdio")
```

**工作原理**：
- Host 启动你的 Server 作为子进程
- 通过 stdin/stdout 交换 JSON-RPC 消息

**适用场景**：
- 本地工具（CLI、桌面应用集成）
- 个人使用的 Server
- 开发调试

**优点**：
- 简单，零配置
- 安全（本地信任）
- 不需要网络

### 6.2 Streamable HTTP：生产环境推荐

```python
mcp.run(
    transport="streamable-http",
    host="0.0.0.0",
    port=8000,
    stateless_http=True,    # 无状态，支持水平扩展
    json_response=True      # 简化客户端
)
```

**工作原理**：
- 所有通信通过单个 HTTP 端点
- 响应可以是 JSON 或 SSE 流

**适用场景**：
- 远程部署的 Server
- 团队共享的 Server
- 生产环境

**优点**：
- 支持水平扩展
- 支持 OAuth 认证
- 可远程访问

### 6.3 选择指南

```
                    你的场景？
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│  个人工具     │ │  团队共享     │ │  生产服务     │
│  本地开发     │ │  远程 Server  │ │  高可用部署   │
│               │ │               │ │               │
│   ┌───────┐  │ │  ┌─────────┐ │ │  ┌─────────┐  │
│   │ stdio │  │ │  │  HTTP   │ │ │  │  HTTP   │  │
│   └───────┘  │ │  └─────────┘ │ │  └─────────┘  │
│               │ │               │ │               │
│ • 简单可靠   │ │ • 可远程访问 │ │ • 支持 OAuth  │
│ • 零配置     │ │ • 团队共享   │ │ • 水平扩展    │
└───────────────┘ └───────────────┘ └───────────────┘
```

---

## 7. 进阶实践：认证、日志、进度追踪

### 7.1 日志：让 Server 告诉 Host 发生了什么

```python
from mcp.server.fastmcp import Context

@mcp.tool()
async def process_large_data(ctx: Context, data: list) -> str:
    """处理大量数据"""
    await ctx.info("开始处理数据...")

    for i, item in enumerate(data):
        await ctx.debug(f"处理第 {i+1} 项: {item}")
        # ... 处理逻辑

    await ctx.warning("注意：有 3 项数据格式异常")
    await ctx.info("处理完成！")
    return "success"
```

### 7.2 进度追踪：长时间操作的用户体验

```python
@mcp.tool()
async def batch_import(ctx: Context, items: list[str]) -> str:
    """批量导入数据"""
    total = len(items)
    success_count = 0

    for i, item in enumerate(items):
        # ... 导入逻辑
        success_count += 1

        # 报告进度
        await ctx.report_progress(
            progress=i + 1,
            total=total,
            message=f"已导入 {success_count}/{total}"
        )

    return f"成功导入 {success_count} 项"
```

### 7.3 OAuth 2.1 认证（HTTP 传输）

对于远程 Server，你可能需要认证：

```python
from mcp.server.fastmcp import FastMCP
from mcp.server.auth.provider import AccessToken, TokenVerifier
from mcp.server.auth.settings import AuthSettings
from pydantic import AnyHttpUrl

class MyTokenVerifier(TokenVerifier):
    async def verify_token(self, token: str) -> AccessToken | None:
        # 验证 JWT token
        # 调用你的认证服务
        # 返回有效的 token 信息
        pass

mcp = FastMCP(
    "安全服务",
    token_verifier=MyTokenVerifier(),
    auth=AuthSettings(
        issuer_url=AnyHttpUrl("https://auth.your-company.com"),
        resource_server_url=AnyHttpUrl("https://mcp.your-company.com"),
        required_scopes=["read", "write"],
    ),
)
```

**注意**：stdio 传输不需要 OAuth——它依赖本地信任，可以从环境变量获取凭据。

---

## 8. 配置与部署：在 Claude 中使用

### 8.1 Claude Desktop 配置

编辑配置文件：

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "天气助手": {
      "command": "python",
      "args": ["/path/to/weather_server.py"]
    },
    "GitHub": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_TOKEN": "ghp_你的token" }
    },
    "远程服务": {
      "url": "https://mcp.your-company.com"
    }
  }
}
```

### 8.2 Claude Code 配置

编辑 `~/.claude/settings.json`：

```json
{
  "mcpServers": {
    "weather": {
      "command": "python",
      "args": ["/path/to/weather_server.py"]
    }
  }
}
```

### 8.3 完整示例：项目全栈 Server

让我们写一个综合的 Server，用于项目开发：

```python
from mcp.server.fastmcp import FastMCP, Context
from pathlib import Path
import subprocess
import json

mcp = FastMCP("项目开发助手")
PROJECT_ROOT = Path("/my/project")

# ─── Resource：项目结构 ───
@mcp.resource("project://structure")
def get_project_structure() -> str:
    """项目目录结构"""
    tree = []
    for path in sorted(PROJECT_ROOT.rglob("*")):
        if ".git" in path.parts:
            continue
        rel = path.relative_to(PROJECT_ROOT)
        indent = "  " * (len(rel.parts) - 1)
        prefix = "📁" if path.is_dir() else "📄"
        tree.append(f"{indent}{prefix} {rel.name}")
    return "\n".join(tree)

# ─── Resource：README ───
@mcp.resource("doc://README")
def get_readme() -> str:
    """项目 README"""
    readme = PROJECT_ROOT / "README.md"
    return readme.read_text() if readme.exists() else "无 README"

# ─── Tool：运行测试 ───
@mcp.tool()
async def run_tests(ctx: Context, file: str | None = None) -> str:
    """运行项目测试

    Args:
        file: 指定测试文件，留空则运行全部测试
    """
    await ctx.info("开始运行测试...")

    cmd = ["python", "-m", "pytest"]
    if file:
        cmd.append(str(PROJECT_ROOT / file))

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        await ctx.info("✅ 测试通过！")
    else:
        await ctx.warning("❌ 测试失败")

    return f"""
退出码: {result.returncode}

标准输出:
{result.stdout}

标准错误:
{result.stderr}
"""

# ─── Tool：搜索代码 ───
@mcp.tool()
def search_code(keyword: str) -> list[str]:
    """在代码库中搜索"""
    results = []
    for path in PROJECT_ROOT.rglob("*.py"):
        if keyword in path.read_text():
            results.append(str(path.relative_to(PROJECT_ROOT)))
    return results

# ─── Prompt：代码审查 ───
@mcp.prompt()
def review_file(path: str) -> str:
    """审查指定文件的代码"""
    file = PROJECT_ROOT / path
    code = file.read_text() if file.exists() else f"文件不存在: {path}"

    return f'''请审查以下代码文件：{path}

\``` {file.suffix.lstrip('.')}
{code}
\```

请从以下方面审查：
1. 安全性问题
2. 代码质量
3. 可维护性
4. 性能建议
'''

# ─── 运行 ───
if __name__ == "__main__":
    mcp.run()
```

---

## 总结

### 核心概念回顾

| 概念 | 作用 | 谁控制 |
|------|------|--------|
| **Tool** | AI 可调用的函数 | 模型 |
| **Resource** | 背景数据 | 应用/用户 |
| **Prompt** | 交互模板 | 用户 |

### 开发流程

1. **从简单开始**：先写一个 Tool，用 Inspector 测试
2. **逐步添加**：根据需要添加 Resource 和 Prompt
3. **测试验证**：用 Inspector 和 Claude Desktop 测试
4. **部署配置**：配置到 Host 中使用

### 下一步

- 查看官方示例：https://github.com/modelcontextprotocol/servers
- 阅读协议规范：https://modelcontextprotocol.io
- 加入社区讨论！

---

> **开始动手**：用 `@mcp.tool()` 写你的第一个函数，运行 `npx @modelcontextprotocol/inspector python your_server.py` 调试。5 分钟就能跑通！
