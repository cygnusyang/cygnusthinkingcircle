# 第二十二章：从零构建Mini-Harness —— 最小可行循环

前面讲了那么多理论，这一章我们动手——用不到 **100 行 Python** 构建一个可运行的 Mini-Harness。

## 目标

一个最小但完整的 Harness：
1. Agent Loop（observe → think → act 循环）
2. 三个基本工具（Read、Write、Bash）
3. 简单的权限检查
4. 真正能完成编码任务

## 完整代码

```python
"""
mini_harness.py — 100行构建一个可运行的 AI 编码 Agent
依赖: pip install anthropic
"""

import os
import json
import subprocess
import anthropic

# ============================================================
# 配置
# ============================================================
MODEL = "claude-sonnet-4-20250514"
MAX_TURNS = 30
WORK_DIR = os.getcwd()

# ============================================================
# 工具定义
# ============================================================
TOOLS = [
    {
        "name": "read_file",
        "description": "读取文件内容。用于理解代码、配置或文档。",
        "input_schema": {
            "type": "object",
            "required": ["path"],
            "properties": {
                "path": {
                    "type": "string",
                    "description": "相对于项目根目录的文件路径"
                }
            }
        }
    },
    {
        "name": "write_file",
        "description": "写入或覆盖文件内容。用于创建新文件或修改现有文件。",
        "input_schema": {
            "type": "object",
            "required": ["path", "content"],
            "properties": {
                "path": {"type": "string", "description": "文件路径"},
                "content": {"type": "string", "description": "要写入的内容"}
            }
        }
    },
    {
        "name": "run_command",
        "description": "执行 shell 命令。用于运行测试、安装依赖、查看 git 状态等。",
        "input_schema": {
            "type": "object",
            "required": ["command"],
            "properties": {
                "command": {"type": "string", "description": "要执行的命令"}
            }
        }
    },
]

# ============================================================
# 权限规则
# ============================================================
DENY_PATTERNS = [
    (["write_file", "run_command"], ".env"),
    (["write_file", "run_command"], "*.key"),
    (["run_command"], "rm -rf"),
    (["run_command"], "sudo"),
]

def check_permission(tool_name: str, params: dict) -> bool:
    """检查操作是否被禁止"""
    param_str = json.dumps(params)
    for tools, pattern in DENY_PATTERNS:
        if tool_name in tools and pattern.lower() in param_str.lower():
            return False
    return True

# ============================================================
# 工具执行
# ============================================================
def execute_tool(tool_name: str, params: dict) -> str:
    """执行工具调用并返回结果"""
    if not check_permission(tool_name, params):
        return f"❌ 权限拒绝: 操作 '{tool_name}' 匹配安全规则，已被阻止。"

    try:
        if tool_name == "read_file":
            path = os.path.join(WORK_DIR, params["path"])
            with open(path, "r") as f:
                content = f.read()
            if len(content) > 5000:
                content = content[:5000] + f"\n...(截断，共 {len(content)} 字符)"
            return content

        elif tool_name == "write_file":
            path = os.path.join(WORK_DIR, params["path"])
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                f.write(params["content"])
            return f"✅ 文件已写入: {params['path']} ({len(params['content'])} 字符)"

        elif tool_name == "run_command":
            result = subprocess.run(
                params["command"], shell=True, capture_output=True,
                text=True, timeout=30, cwd=WORK_DIR
            )
            output = result.stdout or result.stderr
            if len(output) > 3000:
                output = output[:3000] + f"\n...(截断，共 {len(output)} 字符)"
            return f"退出码: {result.returncode}\n{output}"

    except Exception as e:
        return f"❌ 工具执行错误: {e}"

# ============================================================
# System Prompt
# ============================================================
SYSTEM_PROMPT = f"""你是一个 AI 编码助手，运行在 Harness 中。

当前工作目录: {WORK_DIR}

你有以下工具:
- read_file: 读取文件
- write_file: 写入文件
- run_command: 执行命令

工作方式:
1. 理解用户需求
2. 读取相关文件了解现状
3. 修改代码
4. 运行测试验证
5. 完成后做简要总结

如果不需要使用工具，直接给出文本回复。"""

# ============================================================
# Agent Loop
# ============================================================
def agent_loop(task: str) -> str:
    client = anthropic.Anthropic()
    messages = [{"role": "user", "content": task}]

    for turn in range(1, MAX_TURNS + 1):
        print(f"\n--- Turn {turn} ---")

        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=messages,
            tools=TOOLS,
        )

        # 模型返回文本 → 任务完成
        if response.stop_reason == "end_turn":
            return response.content[0].text

        # 处理工具调用
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                print(f"  🔧 {block.name}({json.dumps(block.input, ensure_ascii=False)})")
                result = execute_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                })

        # 将结果反馈给 Agent
        messages.append({
            "role": "user",
            "content": tool_results,
        })

    return "⚠️ 达到最大轮次上限，任务未完成。"

# ============================================================
# 入口
# ============================================================
if __name__ == "__main__":
    import sys
    task = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else input("任务: ")
    result = agent_loop(task)
    print(f"\n{'='*60}\n{result}")
```

## 运行

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
python mini_harness.py "帮我创建一个简单的 Flask web 应用，有一个 /hello 端点"
```

## 这段代码做了什么

1. **定义工具**：Read、Write、Bash——最小可用集合
2. **定义安全规则**：阻止读写 `.env`、阻止 `rm -rf` 和 `sudo`
3. **Agent Loop**：标准 observe → think → act 循环
4. **权限检查**：每个工具调用前检查 deny 规则
5. **输出截断**：大文件/大输出自动截断

这就是 learn-claude-code 所说的：**"One loop & Bash is all you need."**

## 从 100 行到生产级

这 100 行是一个完整 Harness 的骨架。生产级需要加上：

| 100 行版 | 生产级 |
|---------|--------|
| 3 个工具 | 20-40 个工具 |
| 简单 deny 规则 | deny→ask→allow 管道 + 分类器 |
| 无压缩 | 98% 窗口自动压缩 |
| 无多 Agent | 子 Agent 生成 + worktree 隔离 |
| 无 MCP | MCP Client + 惰性加载 |
| 无技能 | 按需技能注入 |
| 无记忆 | MEMORY.md 跨会话持久化 |
| 无流式 | 流式输出 |

但**核心循环是一样的**——每加一个功能，都是在这 100 行的骨架上长肉。

## 本章小结

- 不到 100 行 Python 就能构建一个完整可运行的 Agent Harness
- 核心：工具定义 + Agent Loop + 权限检查
- "One loop & Bash is all you need" 不是口号——这 100 行真的能完成编码任务
- 从 100 行到生产级的每一步，都是在骨架上的增量
- 下一章：添加工具系统与权限控制

---

**系列目录**：
- [第二十一章：Agent间通信协议](../06-multi-agent/21-agent-communication.md)
- 第二十二章：从零构建Mini-Harness 👈 当前位置
- [第二十三章：添加工具系统与权限控制](./23-adding-tools-and-permissions.md) 👉 下一章
- [第二十四章：添加MCP与多智能体支持](./24-adding-mcp-and-multi-agent.md)
