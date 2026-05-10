# 第二十一章：Agent间通信协议 —— A2A、Task、Message Passing

Agent 之间怎么"说话"？这一章探讨多 Agent 系统中的通信协议设计。

## 通信的三个层次

```
Level 1: 结果回传 (Result Passing)
  Agent A 完成任务 → 返回结果给主 Agent → 主 Agent 消费

Level 2: 任务委派 (Task Delegation)
  主 Agent 分解任务 → 分配给子 Agent → 子 Agent 返回结果

Level 3: 对等通信 (Peer Communication)
  Agent A ↔ Agent B: 双向、持续的协商和对话
```

## Level 1：结果回传

最简单的通信方式——类似函数调用：

```
主 Agent: spawn_subagent("reviewer", "审查 src/auth.py 的安全性")
子 Agent: [独立工作...]
子 Agent: 返回 {
  "findings": ["SQL注入风险", "硬编码密钥"],
  "severity": "high",
  "recommendations": [...]
}
主 Agent: 收到结果，根据建议修改代码
```

**核心设计原则**：结构化 > 自然语言。JSON 结果比自然语言段落更容易被 Agent 正确解析和使用。

## Level 2：任务委派（Task 协议）

多个 Harness 项目不约而同地采用了类似的 Task 协议：

```json
{
  "task_id": "uuid-xxxx",
  "type": "code_implementation",
  "title": "实现 GitHub OAuth 回调端点",
  "context": {
    "framework": "FastAPI",
    "auth_library": "authlib",
    "related_files": ["src/auth.py", "src/config.py"]
  },
  "acceptance_criteria": [
    "端点 POST /auth/github/callback 正常工作",
    "成功换取 access_token",
    "创建或更新本地用户记录",
    "返回 JWT token"
  ],
  "depends_on": ["task-uuid-yyyy"],  // 依赖的任务
  "assigned_to": "coder-agent",
  "status": "pending"
}
```

Task 协议的关键字段：
- **context**：子 Agent 需要的上下文（不要太多，否则上下文污染）
- **acceptance_criteria**：明确的完成标准（Agent 需要知道"做到什么程度算完成"）
- **depends_on**：任务依赖（调度器用来决定执行顺序）

## Level 3：对等通信

最复杂的通信模式——Agent 之间持续对话：

```
Agent A (作者): "我实现了一个新的缓存层，请审查"
Agent B (审查者): "看了代码，cache.py:42 的 key 生成逻辑有冲突风险"
Agent A (作者): "你说得对，让我修复... 改好了，用 hash 替代了拼接"
Agent B (审查者): "好多了。还有一个问题：没有设置 TTL"
Agent A (作者): "加了 TTL 配置。再看一下？"
Agent B (审查者): "LGTM"
```

实现：

```python
class AgentCommunication:
    def __init__(self, hub: Hub):
        self.hub = hub

    async def send(self, from_agent: str, to_agent: str, message: dict):
        """Agent 间消息"""
        await self.hub.route(from_agent, to_agent, message)

    async def request_review(self, from_agent: str, file: str):
        """请求代码审查"""
        await self.hub.broadcast({
            "type": "review_request",
            "from": from_agent,
            "file": file,
            "status": "awaiting_review"
        })

    async def negotiate(self, agent_a: str, agent_b: str, topic: str):
        """两个 Agent 协商"""
        session = await self.hub.create_session([agent_a, agent_b])
        return session
```

## A2A (Agent-to-Agent) 协议

Google 在 2025 年提出了 A2A 协议标准：

```json
{
  "a2a_version": "1.0",
  "from": "agent://coder-1",
  "to": "agent://reviewer-1",
  "message": {
    "type": "task_request",
    "task": {
      "description": "Review PR #42 for security issues",
      "context_ref": "pr://github.com/myorg/myrepo/42",
      "deadline": "2026-05-06T18:00:00Z"
    }
  },
  "reply_to": "agent://master"
}
```

虽然 A2A 尚未成为行业标准，但它代表了通信协议从"项目自定义"走向"行业标准化"的趋势。就像 MCP 让工具调用标准化一样，A2A 的目标是让 Agent 间通信标准化。

## 通信中的上下文管理

Agent 间通信的一个关键挑战：**传递多少上下文**？

```
太少: 子 Agent 没有足够信息完成任务
太多: 浪费子 Agent 的上下文窗口
```

最佳实践：**洋葱模型**

```
最外层:  任务描述 + 验收标准（最小，必须）
中间层:  相关文件路径 + 关键配置（按需提供）
最内层:  完整文件内容（子 Agent 自己用工具获取）

不要:    把 10 个文件的内容全塞进 task context
```

子 Agent 可以通过工具自己获取需要的信息，不需要在任务分配时全量传递。

## 本章小结

- Agent 通信有三个层次：结果回传 → 任务委派 → 对等通信
- Task 协议的关键字段：context（适量）、acceptance_criteria（明确）、depends_on（依赖）
- A2A 协议代表了 Agent 通信标准化的方向（类比 MCP 之于工具调用）
- 上下文传递遵循洋葱模型：最少必需信息 + Agent 自主获取详情
- 结构化 (JSON) > 自然语言：Agent 解析结构化数据更可靠
- 下一章：从零构建 Mini-Harness

---

**系列目录**：
- [第二十章：子代理隔离与上下文管理](./20-subagent-isolation.md)
- 第二十一章：Agent间通信协议 👈 当前位置
- [第二十二章：从零构建Mini-Harness —— 最小可行循环](../07-build-your-own/22-build-mini-harness.md) 👉 下一章
