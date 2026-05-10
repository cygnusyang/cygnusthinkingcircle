# 第二十三章：添加工具系统与权限控制

上一章我们构建了 100 行的 Mini-Harness。这一章升级它的工具系统和权限控制。

## 扩展工具系统

### 添加更多工具

```python
def add_git_tools():
    """添加 Git 相关工具"""
    return [
        {
            "name": "git_status",
            "description": "查看 git 工作区状态",
            "input_schema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "git_diff",
            "description": "查看文件的变更内容",
            "input_schema": {
                "type": "object",
                "properties": {
                    "staged": {
                        "type": "boolean",
                        "description": "true=已暂存变更, false=未暂存变更"
                    }
                }
            }
        },
    ]

def add_web_tools():
    """添加网络搜索工具"""
    return [
        {
            "name": "web_search",
            "description": "搜索网络获取最新信息",
            "input_schema": {
                "type": "object",
                "required": ["query"],
                "properties": {
                    "query": {"type": "string", "description": "搜索关键词"}
                }
            }
        },
    ]
```

### 工具注册表

用注册模式让添加工具变得简单：

```python
class ToolRegistry:
    def __init__(self):
        self._tools = {}

    def register(self, name: str, description: str, schema: dict, handler: callable):
        self._tools[name] = {
            "name": name,
            "description": description,
            "input_schema": schema,
            "handler": handler,
        }

    def get_anthropic_format(self) -> list[dict]:
        """转为 Anthropic API 格式"""
        return [
            {"name": t["name"], "description": t["description"],
             "input_schema": t["input_schema"]}
            for t in self._tools.values()
        ]

    def execute(self, name: str, params: dict) -> str:
        if name not in self._tools:
            return f"未知工具: {name}"
        return self._tools[name]["handler"](params)


# 使用
registry = ToolRegistry()

registry.register(
    "read_file",
    "读取文件内容",
    {"type": "object", "required": ["path"], "properties": {...}},
    lambda p: open(p["path"]).read()
)

registry.register(
    "write_file",
    "写入文件",
    {"type": "object", "required": ["path", "content"], "properties": {...}},
    lambda p: _write_file(p["path"], p["content"])
)
```

## 升级权限系统

从简单的 deny 规则升级到完整的三级管道：

```python
from enum import Enum
import fnmatch

class Permission(Enum):
    DENY = "deny"
    ASK = "ask"
    ALLOW = "allow"

class PermissionEngine:
    def __init__(self):
        self.rules = {
            Permission.DENY: [],
            Permission.ASK: [],
            Permission.ALLOW: [],
        }

    def add_rule(self, perm: Permission, tool_pattern: str,
                 path_pattern: str = "*", cmd_pattern: str = "*"):
        self.rules[perm].append({
            "tool": tool_pattern,     # 支持通配符: "*" 匹配所有工具
            "path": path_pattern,     # 支持 glob: "**/.env"
            "cmd": cmd_pattern,       # 支持子串匹配: "*rm -rf*"
        })

    def check(self, tool_name: str, path: str = "",
              command: str = "") -> Permission:
        # DENY 优先
        for rule in self.rules[Permission.DENY]:
            if self._match(rule, tool_name, path, command):
                return Permission.DENY

        # ASK
        for rule in self.rules[Permission.ASK]:
            if self._match(rule, tool_name, path, command):
                return Permission.ASK

        # ALLOW
        for rule in self.rules[Permission.ALLOW]:
            if self._match(rule, tool_name, path, command):
                return Permission.ALLOW

        # 默认: 需要确认
        return Permission.ASK

    def _match(self, rule: dict, tool: str, path: str, cmd: str) -> bool:
        return (
            fnmatch.fnmatch(tool, rule["tool"]) and
            fnmatch.fnmatch(path, rule["path"]) and
            (rule["cmd"] == "*" or rule["cmd"] in cmd)
        )


# 配置权限
engine = PermissionEngine()

# DENY: 永远阻止
engine.add_rule(Permission.DENY, "*", "**/.env")
engine.add_rule(Permission.DENY, "*", "**/*.key")
engine.add_rule(Permission.DENY, "run_command", "*", "*rm -rf*")
engine.add_rule(Permission.DENY, "run_command", "*", "*sudo*")

# ALLOW: 只读操作自动通过
engine.add_rule(Permission.ALLOW, "read_file")
engine.add_rule(Permission.ALLOW, "git_status")
engine.add_rule(Permission.ALLOW, "git_diff")
engine.add_rule(Permission.ALLOW, "run_command", "*", "ls*")
engine.add_rule(Permission.ALLOW, "run_command", "*", "cat*")

# ASK: 写入操作需要确认
engine.add_rule(Permission.ASK, "write_file")
engine.add_rule(Permission.ASK, "run_command", "*", "git commit*")
```

### 用户确认流程

```python
def execute_with_permission(tool_name: str, params: dict) -> str:
    path = params.get("path", "")
    command = params.get("command", "")

    perm = engine.check(tool_name, path, command)

    if perm == Permission.DENY:
        return f"❌ 安全规则阻止了此操作: {tool_name}"
    elif perm == Permission.ASK:
        print(f"\n⚠️  Agent 想执行: {tool_name}")
        print(f"   参数: {json.dumps(params, ensure_ascii=False)}")
        answer = input("   允许? [y/N] ")
        if answer.lower() != "y":
            return "❌ 用户拒绝了此操作。"
    # else: ALLOW，直接执行

    return execute_tool(tool_name, params)
```

## 集成到 Agent Loop

```python
def agent_loop_v2(task: str) -> str:
    client = anthropic.Anthropic()
    messages = [{"role": "user", "content": task}]

    for turn in range(1, MAX_TURNS + 1):
        print(f"\n--- Turn {turn} ---")

        # Auto-inject 当前状态
        system = f"""{SYSTEM_PROMPT}
## 当前环境
- 工作目录: {WORK_DIR}
- Git 分支: {get_git_branch()}
- 可用工具: {len(registry._tools)} 个
"""

        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=system,
            messages=messages,
            tools=registry.get_anthropic_format(),
        )

        if response.stop_reason == "end_turn":
            return response.content[0].text

        for block in response.content:
            if block.type == "tool_use":
                print(f"  🔧 {block.name}(...)")
                # 权限检查 + 执行
                result = execute_with_permission(block.name, block.input)

                messages.append({
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    }]
                })

    return "⚠️ 任务未完成。"
```

## 从硬编码到可配置

最终，权限规则应该从配置文件读取，而不是硬编码：

```yaml
# harness.config.yaml
permissions:
  deny:
    - tools: ["*"]
      paths: ["**/.env", "**/*.key", "**/*.pem"]
    - tools: ["run_command"]
      commands: ["rm -rf", "sudo", "chmod 777"]
  ask:
    - tools: ["write_file", "run_command"]
  allow:
    - tools: ["read_file", "git_status", "git_diff", "web_search"]
```

```python
def load_permissions(config_path: str) -> PermissionEngine:
    with open(config_path) as f:
        config = yaml.safe_load(f)

    engine = PermissionEngine()
    for perm_type, rules in config["permissions"].items():
        perm = Permission(perm_type)
        for rule in rules:
            for tool in rule.get("tools", ["*"]):
                for path in rule.get("paths", ["*"]):
                    for cmd in rule.get("commands", ["*"]):
                        engine.add_rule(perm, tool, path, cmd)
    return engine
```

## 本章小结

- 工具注册表模式让添加新工具像注册回调函数一样简单
- 权限引擎从简单的 deny 规则升级为 deny→ask→allow 三级管道
- deny 优先原则不变——安全第一
- 权限规则从配置文件加载，项目级可覆盖全局默认
- Auto-inject 让 Agent 始终知道环境状态
- 下一章：添加 MCP 与多智能体支持

---

**系列目录**：
- [第二十二章：从零构建Mini-Harness](./22-build-mini-harness.md)
- 第二十三章：添加工具系统与权限控制 👈 当前位置
- [第二十四章：添加MCP与多智能体支持](./24-adding-mcp-and-multi-agent.md) 👉 下一章
