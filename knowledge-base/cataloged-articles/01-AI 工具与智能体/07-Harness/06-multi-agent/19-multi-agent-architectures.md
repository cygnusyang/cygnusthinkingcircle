# 第十九章：多智能体架构模式 —— Master-Worker、Hub-Spoke、Pipeline

当单个 Agent 面对复杂任务时，分解并委托给多个"专家"Agent 是自然的解法。这一章详解三种主流多 Agent 架构模式。

## 为什么需要多 Agent

单个 Agent 的限制：
- **上下文限制**：一个 Agent 的记忆有限，大型任务超出窗口
- **注意力稀释**：处理多种不同类型的子任务时，Agent 容易"分心"
- **专长深度**：一个通用 Agent 不如多个专精 Agent 在各自领域表现好

多 Agent 的核心价值：**分散复杂度，隔离上下文**。

## 模式一：Master-Worker（主从模式）

```
        ┌─────────────┐
        │   Master    │  制定计划、分配任务、整合结果
        │  (Orchestrator) │
        └──────┬──────┘
       ┌───────┼───────┐
       ▼       ▼       ▼
  ┌────────┐┌────────┐┌────────┐
  │Worker 1││Worker 2││Worker 3│  各自独立执行
  │搜索/研究││写代码  ││写测试  │  独立上下文
  └────────┘└────────┘└────────┘
```

### 特点

- Master 不执行具体任务，只做**编排**
- 每个 Worker 有独立上下文，互不干扰
- Master → Worker：单向任务分配
- Worker → Master：结果回传

### 适用场景

- 任务可明确分解为独立子任务
- 子任务类型不同（搜索 vs 编码 vs 测试）
- 不需要 Worker 之间直接通信

### 实现示例

```python
async def master_worker(task: str):
    # Master 分解任务
    plan = await master.plan(task)
    # plan = [
    #   {"role": "researcher", "task": "搜索最佳实践"},
    #   {"role": "coder", "task": "实现核心逻辑"},
    #   {"role": "tester", "task": "编写测试"},
    # ]

    # 并行执行
    results = await asyncio.gather(*[
        spawn_worker(item["role"], item["task"])
        for item in plan
    ])

    # Master 整合结果
    final = await master.integrate(task, results)
    return final
```

Claude Code 的子代理、Codex 的 sub-agent 都使用这种模式。

## 模式二：Hub-and-Spoke（星型模式）

```
              ┌─────────┐
              │   Hub   │  消息路由 + 状态管理
              └────┬────┘
       ┌───────────┼───────────┐
       ▼           ▼           ▼
  ┌─────────┐ ┌─────────┐ ┌─────────┐
  │ Agent A │ │ Agent B │ │ Agent C │  可以对等通信
  │ 前端专家 │ │ 后端专家 │ │ 安全专家 │  (通过 Hub)
  └─────────┘ └─────────┘ └─────────┘
```

### 特点

- Hub 是一个**消息路由器**，不一定是"上级"
- Agent 之间可以通过 Hub **对等通信**
- Hub 维护全局状态
- 更像一个"团队聊天室"而非"老板和员工"

### 适用场景

- 需要 Agent 之间持续协商（如代码审查：作者 ↔ 审查者）
- 任务执行过程中需要动态调整分工
- 全局状态需要被所有 Agent 感知

### 实现示例

```python
class Hub:
    def __init__(self):
        self.agents = {}
        self.broadcast_channel = []

    async def route(self, from_agent: str, to_agent: str, message: str):
        """Agent 间消息路由"""
        await self.agents[to_agent].receive(from_agent, message)

    async def broadcast(self, message: str):
        """全局通知"""
        for agent in self.agents.values():
            await agent.receive("hub", message)
```

OpenClaw 的 Gateway 本质上就是 Hub-and-Spoke 模式——Gateway 是 Hub，各渠道和 Agent 是 Spoke。

## 模式三：Pipeline（流水线模式）

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│ Agent 1 │───▶│ Agent 2 │───▶│ Agent 3 │───▶│ Agent 4 │
│ 需求分析 │    │ 方案设计 │    │ 编码实现 │    │ 测试验证 │
└─────────┘    └─────────┘    └─────────┘    └─────────┘
```

### 特点

- 严格的**顺序依赖**——Agent 2 必须等 Agent 1 完成
- 每个 Agent 的输出是下一个 Agent 的输入
- 类似工厂流水线

### 适用场景

- 任务有清晰的阶段依赖（分析 → 设计 → 实现 → 验证）
- 每个阶段有明确的**交付物**（分析报告 → 设计文档 → 代码 → 测试结果）
- 对质量要求高，需要多阶段把关

### 实现示例

```python
async def pipeline(task: str):
    stages = [
        ("analyst", "分析需求"),
        ("designer", "设计方案"),
        ("coder", "编码实现"),
        ("tester", "测试验证"),
    ]

    context = {"task": task}
    for role, instruction in stages:
        agent = spawn_agent(role)
        context = await agent.execute(instruction, context)
        # 每个阶段产出被下一阶段消费

    return context["final_output"]
```

Chachamaru127 的 `claude-code-harness` 就是 Pipeline 模式——Plan → Work → Review 严格顺序。

## 模式对比与选型

| 维度 | Master-Worker | Hub-Spoke | Pipeline |
|------|--------------|-----------|----------|
| **结构** | 层级 | 对等 | 顺序 |
| **通信** | 单向 (M→W) | 双向 (任意) | 单向 (上一级→下一级) |
| **并行性** | 高（Worker 并行） | 中 | 低（串行） |
| **灵活性** | 中 | 高 | 低 |
| **复杂度** | 低 | 高 | 低 |
| **适用** | 可分解的独立任务 | 需要协商的任务 | 有阶段门控的任务 |

### 组合使用

实际项目中常常组合使用：

```
Pipeline（整体）
    ├── Stage 1: Master-Worker（需求分析 + 技术调研并行）
    ├── Stage 2: Master-Worker（编码 + 测试并行）
    └── Stage 3: Hub-Spoke（代码审查: 作者 + 审查者 + 安全审查）
```

## 本章小结

- 多 Agent 的核心价值：分散复杂度，隔离上下文
- Master-Worker：层级结构，适合独立子任务（最常用）
- Hub-Spoke：对等结构，适合需要协商的任务
- Pipeline：顺序结构，适合有阶段门控的任务
- 实际项目常组合使用多种模式
- 下一章：子代理隔离与上下文管理

---

**系列目录**：
- [第十八章：Agent-Harness协作模式](../05-agent-harness/18-agent-harness-collaboration.md)
- 第十九章：多智能体架构模式 👈 当前位置
- [第二十章：子代理隔离与上下文管理](./20-subagent-isolation.md) 👉 下一章
- [第二十一章：Agent间通信协议](./21-agent-communication.md)
