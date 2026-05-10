# 第十章：Agent Loop —— Harness的心跳

如果说 Harness 是 Agent 的身体，那 **Agent Loop** 就是心跳。没有循环，Agent 就是个一问一答的 chatbot。这一章深入 Agent Loop 的每一个细节。

## 什么是 Agent Loop

Agent Loop 是一个连续的执行周期：

```
┌────────────────────────────────────────┐
│           The Agent Loop               │
│                                        │
│  1. OBSERVE  — 收集当前状态            │
│       ↓                                │
│  2. THINK    — 模型推理 + 选择行动     │
│       ↓                                │
│  3. ACT      — 执行工具调用            │
│       ↓                                │
│  4. FEEDBACK — 结果注入上下文          │
│       ↓                                │
│  (回到 1，直到目标完成或达到上限)      │
└────────────────────────────────────────┘
```

## 最小实现

```python
import anthropic

def agent_loop(task: str, tools: list[dict], max_turns: int = 50):
    client = anthropic.Anthropic()
    messages = [{"role": "user", "content": task}]

    for turn in range(max_turns):
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=load_system_prompt(),
            messages=messages,
            tools=tools,
        )

        # 模型给出最终回答 → 任务完成
        if response.stop_reason == "end_turn":
            return response.content[0].text

        # 模型请求调用工具 → 执行
        for block in response.content:
            if block.type == "tool_use":
                result = execute_tool(block.name, block.input)
                messages.append({
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    }]
                })

    raise MaxTurnsExceeded(f"任务在 {max_turns} 轮内未完成")
```

这 25 行就是 Agent Loop 的本质。但生产级的 Loop 有更多考量。

## Auto-Inject：每轮注入什么

生产级 Harness（Claude Code、Codex、OpenHarness）每轮都自动注入：

```python
def build_context(turn: int):
    return {
        # 系统上下文（始终注入）
        "system_prompt": load_claude_md(),      # CLAUDE.md / 规则
        "git_status": git_status_snapshot(),     # 当前分支/变更
        "directory": os.getcwd(),                # 当前工作目录

        # 动态上下文（按需注入）
        "todo_list": todo_write_status(),        # 任务进度
        "available_tools": tool_list(),           # 可用工具列表
        "skills_loaded": active_skills(),        # 已激活技能

        # 历史上下文（选择性注入）
        "recent_turns": messages[-20:],          # 最近 N 轮对话
        "key_decisions": extract_decisions(),    # 关键决策摘要
    }
```

### 为什么 Auto-Inject 比"让模型问"好？

```
方案 A（让模型问）:
  User: 修复 auth bug
  Agent: 当前在哪个分支？    ← 浪费 1 轮
  User: main
  Agent: 有没有 CLAUDE.md？  ← 浪费 2 轮
  User: 有，内容是...
  Agent: git status 是什么？ ← 浪费 3 轮

方案 B（Auto-Inject）:
  User: 修复 auth bug
  [系统自动注入: 你在 main 分支，CLAUDE.md 说用 JWT，当前有 3 个修改文件...]
  Agent: 好的，我先读 auth.py...  ← 直接开始工作
```

Auto-inject 每轮多花 500-2000 tokens，但**省了 2-5 轮探索式对话**。对于复杂任务（30+ 轮），总 token 效率更高。

## 退出条件：什么时候停下来

Agent 需要知道什么时候任务完成了：

| 退出条件 | 示例 | 风险 |
|---------|------|------|
| **纯文本无工具** | 模型返回文本，不调工具 | 模型过早"以为"完成了 |
| **显式 done 工具** | `task_complete(summary="...")` | 需要额外工具定义 |
| **用户中断** | Ctrl+C | 依赖用户判断 |
| **轮次上限** | `max_turns=50` | 复杂任务可能不够 |
| **Token 预算耗尽** | 上下文 98% 满 | 可能在关键时刻截断 |

生产级 Harness 通常组合使用：**纯文本 + 轮次上限 + Token 预算**。

```python
def should_stop(turn: int, response, context_usage: float):
    if response.stop_reason == "end_turn":
        return StopReason.COMPLETED
    if turn >= max_turns:
        return StopReason.MAX_TURNS
    if context_usage > 0.98:
        return StopReason.CONTEXT_FULL
    return StopReason.CONTINUE
```

## 并行工具调用

某些工具没有依赖关系，可以并行执行：

```python
# 串行（浪费）
read_file("src/auth.py")     # 等 100ms
grep("TODO", "src/")         # 等 200ms
glob("*.test.ts")            # 等 150ms
# 总耗时: 450ms

# 并行（高效）
await asyncio.gather(
    read_file("src/auth.py"),
    grep("TODO", "src/"),
    glob("*.test.ts"),
)
# 总耗时: 200ms（最慢的那个）
```

模型需要能够判断哪些工具调用之间没有依赖——这取决于模型的推理能力。Kimi K2.5 是已知最早支持原生并行工具调用的模型之一。

## 流式 vs 批处理

```
流式:
  User: 修复这个 bug
  Agent: 让我先... [实时显示思考过程]
         读取 src/auth.py... [工具调用]
         发现问题在第 42 行... [分析]
         修改为... [编辑]
         完成! [总结]

批处理:
  User: 修复这个 bug
  [等待 30 秒...]
  Agent: 好的，我已经读取了文件、定位了问题、修改了代码。完成。
```

几乎所有现代 Harness 都选择流式——用户实时看到进展，等待的焦虑感大大降低。而且流式让用户可以**提前中断**错误的执行方向。

## 错误恢复

工具执行可能失败。Harness 需要优雅处理：

```python
def execute_tool(name: str, params: dict) -> str:
    try:
        result = tool_registry[name](**params)
        return format_success(result)
    except FileNotFoundError as e:
        return f"错误: 文件不存在 - {e}\n请检查路径是否正确。"
    except PermissionDenied as e:
        return f"错误: 权限不足 - {e}\n此操作需要用户确认。"
    except Exception as e:
        return f"错误: {e}\n请尝试其他方法。"
```

**关键原则**：工具失败时返回**可操作的错误信息**——不仅说"失败了"，还要给模型足够的上下文来**修正**。

## 实际数据：一轮 Loop 的 token 消耗

以 Claude Code 为例，典型的一轮循环：

| 组件 | Token 数 |
|------|---------|
| System prompt (CLAUDE.md + 规则) | ~2,000 |
| Git status snapshot | ~300 |
| 工具定义列表 | ~1,500 |
| 最近 10 轮对话 | ~8,000 |
| 当前用户消息 | ~100 |
| **输入总计** | **~11,900** |
| 模型输出 (推理 + 工具调用) | ~800 |
| 工具执行结果注入 | ~2,000 |
| **本轮总计** | **~14,700** |

30 轮任务 ≈ 44 万 tokens ≈ $1.3 (Sonnet 4) / $0.33 (Haiku 4.5)

## 本章小结

- Agent Loop = observe → think → act → feedback 的持续循环
- 最小实现仅需 25 行 Python——但生产级需要 auto-inject、错误处理、并行、流式
- Auto-inject 策略：多花 tokens 在上下文注入上，省掉探索式对话，总效率更高
- 退出条件组合使用：纯文本 + 轮次上限 + token 预算
- 并行工具调用可将执行时间减少 50%+
- 流式输出对用户体验至关重要——实时反馈 > 快速完成
- 下一章：工具系统——Harness如何分发和执行工具

---

**系列目录**：
- [第九章：开源Harness生态全景](../03-implementations/09-open-source-harness-ecosystem.md)
- 第十章：Agent Loop —— Harness的心跳 👈 当前位置
- [第十一章：工具系统 —— 从Bash到MCP的工具分发](./11-tool-system.md) 👉 下一章
- [第十二章：权限系统 —— deny→ask→allow的安全边界](./12-permission-system.md)
- [第十三章：上下文管理 —— 自动注入、压缩与惰性加载](./13-context-management.md)
- [第十四章：MCP集成 —— 扩展Harness的能力边界](./14-mcp-integration.md)
- [第十五章：技能系统 —— 按需注入领域知识](./15-skills-system.md)
