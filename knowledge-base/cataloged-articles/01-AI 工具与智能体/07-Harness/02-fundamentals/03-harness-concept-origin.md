# 第三章：Harness概念溯源 —— "模型是大脑，Harness是身体"

前两章我们回顾了 Agent 从符号 AI 到 LLM 时代的演进。现在，我们正式进入本书的核心概念：**Harness**。

## Harness 这个词从哪来

### 英语里的 Harness

Harness 在英语里原意是**马具**——套在马身上的缰绳、鞍具，让骑手能够指挥马的方向和力量。

```
骑手 (用户) → Harness (缰绳/鞍具) → 马 (力量/能力)
```

这个隐喻精确地描述了 AI Agent 中的 Harness：

```
用户 (目标) → Harness (基础设施) → 模型 (能力)
```

**Harness 不提供力量，它提供控制**。

### AI 语境下的 Harness

2025 年 2 月，swyx（Shawn Wang）在 AI Engineer Summit 上的演讲中给出了最经典的定义：

> "The model is the brain. The harness is the body."

完整拆解：

| 隐喻 | AI 对应 | 职责 |
|------|---------|------|
| Brain（大脑） | LLM 模型 | 推理、决策、规划、生成 |
| Body（身体） | Harness | 执行、感知、记忆、约束 |
| Nervous System（神经系统） | Agent Loop | 传递信息、连接脑和身体 |
| Environment（环境） | 代码库/文件系统/网络 | Agent 的操作空间 |

### Anthropic 官方的定义

Anthropic 在 Claude Code 文档中这样描述 Harness：

> "The harness is what turns a language model into a capable coding agent."

翻译过来：**模型是原材料，Harness 是加工厂**。

## 为什么需要 Harness？

### 一个裸模型能做什么？

给你一个裸的 Claude API：

```python
import anthropic

client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    messages=[{"role": "user", "content": "帮我修复 src/auth.py 里的 bug"}]
)
print(response.content[0].text)
```

输出：
```
我无法直接访问您的文件系统。请您将 src/auth.py 的内容粘贴给我，
我可以帮您分析并建议修复方案。
```

模型很聪明，但它**没有手**——不能读文件、不能搜代码、不能改代码、不能跑测试。

### 加了工具之后呢？

```python
# 定义工具
tools = [
    {"name": "read_file", "parameters": {"path": "string"}},
    {"name": "grep", "parameters": {"pattern": "string"}},
    {"name": "write_file", "parameters": {"path": "string", "content": "string"}},
    {"name": "run_shell", "parameters": {"command": "string"}},
]
```

现在模型可以：
1. 决定"我需要先读这个文件"
2. 调用 `read_file("src/auth.py")`
3. 获得文件内容
4. 分析问题
5. 调用 `write_file("src/auth.py", fixed_content)`

它可以**做事**了。但问题也随之而来：

- 模型读了敏感文件（`.env`）怎么办？→ **权限系统**
- 10 轮对话后上下文满了怎么办？→ **上下文管理**
- 模型陷入了"读文件→改→读→改→读"的死循环怎么办？→ **循环控制**
- 任务太复杂需要分解怎么办？→ **规划系统**
- 需要调用 Jira API 怎么办？→ **MCP 集成**

每一个"怎么办"都是一个 Harness 子系统。**Harness 就是所有这些问题答案的集合**。

## Harness 不是什么

### Harness ≠ LangChain

LangChain 是 Agent **框架**：它提供预定义的链、Agent 类型、工具抽象。问题在于，LangChain 的代码**编排了 Agent 的决策流**——什么时候调什么工具、怎么组合，都由代码决定。

Harness 的理念相反：**让模型做决策**。代码只提供"能力"（工具、权限、上下文），不提供"判断"。

```
LangChain:  代码决定流程 → 模型执行步骤
Harness:    模型决定流程 → 代码提供能力
```

### Harness ≠ Prompt Engineering

Prompt Engineering 是通过精心设计的提示词来"引导"模型行为。它有效，但脆弱——换一个模型版本、换一个上下文，prompt 可能就失效了。

Harness Engineering 是**结构性约束**：不是"告诉模型不要做 X"，而是"让模型根本做不了 X"。

```python
# Prompt Engineering 方式
"请不要读取 .env 文件，里面有机密信息"

# Harness Engineering 方式
permission_rules = [
    {"pattern": ".env", "action": "deny"},
    {"pattern": "*.key", "action": "deny"},
]
```

前者是建议，后者是规则。建议可以被忽略，规则不能被绕过。

## Harness 的核心哲学

### 1. 分离决策与执行

```
模型的职责:  理解目标 → 制定计划 → 选择工具 → 解读结果 → 调整策略
Harness的职责: 提供工具 → 执行操作 → 返回结果 → 管理上下文 → 执行权限
```

模型**想**，Harness**做**。这个分离让双方各司其职。

### 2. 从说服到约束

传统方式：写 prompt 说服模型不要做坏事。
Harness 方式：让坏事的执行根本不可能。

| 传统方式（说服） | Harness 方式（约束） |
|----------------|-------------------|
| "请不要删除重要文件" | 设置 `rm -rf` 命令黑名单 |
| "请保护用户隐私" | 阻止读取 `.env` 和密钥文件 |
| "请控制成本" | 设置 token 预算上限 |
| "请保持专注" | 限制上下文窗口，自动压缩 |

### 3. 模型是司机，Harness 是车

你要从北京开到上海：
- **模型（司机）**：决定走哪条路、在哪休息、怎么超车
- **Harness（车）**：引擎、刹车、方向盘、安全带、油量显示
- **没有司机**：车不跑
- **没有车**：司机哪也去不了
- **好司机 + 破车**：能到，但危险
- **普通司机 + 好车**：安全到，慢一点

**最好的组合**：好司机 + 好车。但如果你只能改进一个，**改进车（Harness）的性价比远高于改进司机（模型）**。

## 本章小结

- Harness 原意是"马具"——控制力量不提供力量
- AI 语境下的定义：**模型是大脑，Harness 是身体**（swyx, 2025）
- Harness 不是 LangChain（框架），不是 Prompt Engineering（技巧），而是一种**结构性基础设施**
- 核心哲学：分离决策与执行、用约束代替说服、模型是司机 Harness 是车
- 下一章：Harness 的四层架构模型

---

**系列目录**：
- [第一章：从符号AI到深度学习 —— Agent的70年简史](../01-history/01-agent-70-years-history.md)
- [第二章：LLM时代的Agent革命 —— 2023-2026爆发期](../01-history/02-llm-era-agent-revolution.md)
- 第三章：Harness概念溯源 —— "模型是大脑，Harness是身体" 👈 当前位置
- [第四章：Harness的核心架构 —— 四层模型详解](./04-harness-core-architecture.md) 👉 下一章
- [第五章：Harness vs Agent vs Model —— 三者关系辨析](./05-harness-agent-model-relationship.md)
