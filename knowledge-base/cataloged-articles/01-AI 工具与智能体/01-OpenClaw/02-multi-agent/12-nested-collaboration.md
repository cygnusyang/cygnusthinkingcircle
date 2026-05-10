# 第十二章：嵌套协作 —— 如何实现 Orchestrator-Worker 模式

前面我们说到，OpenClaw 默认 `maxSpawnDepth: 1`，也就是主智能体可以 spawn 子智能体，但子智能体不能再 spawn 子子智能体。

但是如果你打开 `maxSpawnDepth: 2`，就可以支持**两层嵌套**：

```text
Depth 0: Main Hub (orchestrator)
  ↳ spawn Depth 1: Team Coordinator
    ↳ spawn Depth 2: Worker
```

这就是 **Orchestrator-Worker 模式**（或者叫两层编排模式）。什么时候需要这个？本文来讲清楚。

## 什么场景需要嵌套

你有一个比较大的任务，比如：**调研 10 篇论文，总结它们的核心贡献**。

这个任务可以拆成：

1. **Team Coordinator**：拿到 10 篇论文列表，给每篇论文分配一个 Worker 去阅读总结
2. **Worker**：只读一篇论文，总结它的核心贡献
3. **Team Coordinator**：收集所有 Worker 的总结，汇总成一份完整的调研报告
4. **返回**给 Main Hub

如果不嵌套，Main Hub 要自己做拆分，自己 spawn 10 个 Worker，自己汇总。这在深度 1 也能做。

那什么时候需要嵌套？**当你的任务满足这两个条件**：

1. **任务可以二级拆分**：大任务拆成中任务，中任务拆成小任务
2. **二级拆分需要动态进行**：拆分逻辑本身需要 AI 理解，不能预先写死

这时候，把二级拆分逻辑交给一个深度 1 的 Orchestrator，让它去 spawn 深度 2 的 Workers，主 Hub 只需要等结果就行。

## OpenClaw 嵌套规则

OpenClaw 对嵌套有清晰的规则，核心就一条：

### 核心规则

**当 `当前深度 == maxSpawnDepth` 时，这个深度就是叶子节点，不能再 spawn 了**。

深度从 `0` 开始计数。我们以最常用的 `maxSpawnDepth = 2` 为例：

| Depth | 会话标识 | 可以 spawn 吗？ | 权限 |
|-------|----------|----------------|------|
| 0 | `agent:<id>:main` | ✅ 总是可以 spawn | 完整权限 |
| 1 | `agent:<id>:subagent:<uuid>` | ✅ 可以继续 spawn（因为 `1 < 2`） | 只开放 `sessions_spawn` 等必要会话工具 |
| 2 | `agent:<id>:subagent:<uuid>:subagent:<uuid>` | ❌ 不能再往下 spawn（因为 `2 == 2`，已是叶子节点） | 叶子节点，只执行任务 |

> **关于"叶子节点"**：这是树形结构的术语——树的最末端节点，没有子节点了。在这里就是指最底层负责执行具体任务的智能体，它不需要也不能再 spawn 更深的子智能体。

### 不同配置举例

| 你配置的 `maxSpawnDepth` | 允许的嵌套链路 | 哪个深度是叶子节点（不能 spawn） |
|-------------------------|----------------|---------------------------------|
| `1`（默认） | Depth 0 → Depth 1 | Depth 1 ❌ |
| `2`（推荐开嵌套） | Depth 0 → Depth 1 → Depth 2 | Depth 2 ❌ |
| `5`（不推荐） | Depth 0 → Depth 1 → Depth 2 → Depth 3 → Depth 4 → Depth 5 | Depth 5 ❌ |

> `maxSpawnDepth` 最大支持 5，但官方**强烈建议不要超过 2**。越深越容易上下文漂移。

### 会话标识格式规律

如果你真的需要开到深度 5，会话标识的规律是：**每往下一层，就多拼一段 `:subagent:<uuid>`**。完整格式示例（只展示路径长什么样，能不能 spawn 仍遵循上面的规则）：

| Depth | 会话标识格式 |
|-------|-------------|
| 0 | `agent:<id>:main` |
| 1 | `agent:<id>:subagent:<uuid>` |
| 2 | `agent:<id>:subagent:<uuid>:subagent:<uuid>` |
| 3 | `agent:<id>:subagent:<uuid>:subagent:<uuid>:subagent:<uuid>` |
| 4 | `agent:<id>:subagent:<uuid>:subagent:<uuid>:subagent:<uuid>:subagent:<uuid>` |
| 5 | `agent:<id>:subagent:<uuid>:subagent:<uuid>:subagent:<uuid>:subagent:<uuid>:subagent:<uuid>` |

简单记：**Depth = N，就有 N 个 `subagent` 段**。

## 结果回传链

嵌套的结果是自动回传的，不用你操心：

```mermaid
%%{init: {'theme':'base','themeVariables': {'primaryColor':'#f1f5f9','primaryBorderColor':'#0f4c81','primaryTextColor':'#0f172a','secondaryColor':'#f1f5f9','secondaryBorderColor':'#0f4c81','secondaryTextColor':'#0f172a','tertiaryColor':'#fbbf24','tertiaryBorderColor':'#fbbf24','tertiaryTextColor':'#0f172a','background':'#f8fafc','fontFamily':'Inter, system-ui, sans-serif','fontSize':'14px','textColor':'#0f172a','lineColor':'#334155','edgeLabelBackground':'#ffffff','actorBorderColor':'#0f4c81','actorTextColor':'#0f172a','actorFill':'#f1f5f9'}}}%%
graph TD
  W[Depth 2 Worker 完成] -->|announce| O[Depth 1 Orchestrator]
  O[Orchestrator 汇总完成] -->|announce| M[Depth 0 Main Hub]
```

每一层只处理它直接孩子的结果。逻辑清晰，不会乱。

## 权限自动适配

OpenClaw 会根据深度自动适配权限：

- **Depth 1（当 `maxSpawnDepth >= 2`）**：会开放 `sessions_spawn`、`subagents`、`sessions_list`、`sessions_history`，让它能管理自己的孩子
- **Depth 2**：永远不给 `sessions_spawn` 权限，不能再嵌套了

这是自动的，不用你配置。

## 级联停止

如果你要停止一个上层会话，所有它 spawn 的下层会话都会被自动停止：

- `/stop` 在主会话 → 停止所有深度 1，级联停止所有深度 2
- `/subagents kill <id>` → 停止这个深度 1，级联停止它所有深度 2

不会留下僵尸会话。

## 一个完整例子：调研多篇论文

我们来看一个实际例子：

### 配置

嵌套深度配置写在你的**主配置文件** `~/.openclaw/openclaw.json` 的 `agents.defaults.subagents` 下：

```json5
{
  agents: {
    defaults: {
      subagents: {
        maxSpawnDepth: 2,      // 允许两层嵌套
        maxChildrenPerAgent: 10, // 每个 orchestrator 最多 10 个并发工人
        maxConcurrent: 8,      // 全局最多 8 个并发
      },
    },
  },
}
```

### 执行流程

```typescript
// Depth 0: Main Hub
// 用户说：帮我调研这 10 篇论文，总结核心贡献
sessions_spawn({
  task: `这里有 10 篇论文 URLs，请你：
1. 给每篇论文分配一个 worker
2. 让每个 worker 下载论文，提取核心贡献
3. 收集所有结果，按论文排序输出总结
`,
  agentId: "paper-research-orchestrator",
  mode: "run",
  label: "Paper research orchestration",
});

// Depth 1: paper-research-orchestrator
// 拆分任务，给每篇论文 spawn 一个 worker
for (const paper of papers) {
  sessions_spawn({
    task: `下载这篇论文 ${paper.url}，阅读它，总结核心贡献，不超过 300 字`,
    agentId: "paper-reader-worker",
    mode: "run",
  });
}

// 等待所有 workers 完成，汇总结果
// announce 回传给 Main Hub
```

就是这么简单。

## 什么时候该开 maxSpawnDepth = 2

**打开**当且仅当：你需要一个中间编排层来动态拆分任务。

常见场景：

- ✅ 批量处理多个相似任务（比如多篇论文、多个 PR、多个文件）
- ✅ 二级任务拆分（编排器负责拆分，工人负责执行）
- ✅ Map-Reduce 模式（Map 并行，Reduce 汇总）

**不要打开**当：

- ❌ 你只是主 Hub 直接 spawn 几个专家 → 深度 1 足够
- ❌ 你觉得越深越牛 → 越深风险越大，上下文漂移概率越高
- ❌ 尝试三层以上嵌套 → OpenClaw 允许但不推荐，生产环境尽量避免

## 嵌套的成本和风险

### 成本

- 多一层嵌套，就多一层上下文传递，多一点 token 消耗
- Orchestrator 也要占一个并发位置

### 风险

**上下文漂移**：每多一层，需求就可能走形一点。比如：

```
Main: "我要一个能排序的链表"
  ↳ Orchestrator 理解："用户需要一个高效的有序数据结构"
    ↳ Worker 实现："红黑树，因为它保证 O(log n) 复杂度"
```

最后回来一个红黑树，但其实用户只要一个简单的数组插入排序就能满足需求。

** mitigation 方法**：

1. **尽量不要超过两层** —— 两层足够绝大多数场景
2. **需求描述在每一层都要保留原文** —— Orchestrator 把用户原文传给 Worker，不要自己重写
3. **结果回传的时候，Orchestrator 不要修改 Worker 结果，只汇总** —— 减少信息变形

## 最佳实践总结

| 项目 | 建议 |
|------|------|
| `maxSpawnDepth` | 默认 1，真需要再开 2，不要超过 2 |
| `maxChildrenPerAgent` | 默认 5，批量任务可以开到 10，不要太多 |
| `maxConcurrent` | 根据你的网关 capacity 调整，默认 8 |
| 需求传递 | 尽量传原文，减少中间层理解变形 |
| 结果汇总 | Orchestrator 少加工，保持原始结果 |

## 本章小结

- 嵌套协作就是 Orchestrator 再 spawn Worker，实现二级拆分
- OpenClaw 有清晰的深度规则和权限自动适配
- 结果回传和停止都是自动级联的，不用你操心
- 生产环境推荐最大深度 2，不要更深
- 适合批量处理、Map-Reduce、动态二级拆分场景

---

---

**系列目录**：
- [第一章：OpenClaw 是什么 —— 自托管个人 AI 助手的终极形态](./../01-intro/01-what-is-openclaw.md)
- [第二章：核心架构总览 —— Gateway 为什么是中心控制平面](./../01-intro/02-architecture-overview.md)
- [第三章：Gateway —— 核心网关服务到底做了什么](./../01-intro/03-gateway.md)
- [第四章：多渠道接入 —— 如何支持 25+ 聊天平台](./../01-intro/04-multi-channel-inbox.md)
- [第五章：ACP —— 如何对接外部 AI 客户端](./../01-intro/05-acp.md)
- [第六章：消息路由 —— 消息如何正确送到对的会话](./../01-intro/06-routing.md)
- [第七章：安全模型 —— 配对白名单如何保护你](./../01-intro/07-security-model.md)
- [第八章：为什么你需要一个多智能体框架 —— 单智能体的困境](./08-why-you-need-multi-agent-framework.md)
- [第九章：sessions_spawn —— 多智能体协作的核心原语](./09-sessions-spawn-core-primitive.md)
- [第十章：协作架构模式 —— 从 Master-Worker 到 Hub-and-Spoke](./10-collaboration-architecture-patterns.md)
- [第十一章：隔离设计 —— 为什么每个子智能体需要独立会话](./11-isolation-design.md)
- 第十二章：嵌套协作 —— 如何实现 Orchestrator-Worker 模式 👈 当前位置
- [第十三章：实践案例 —— 从零构建一个代码评审团队](./13-practical-case-code-review-team.md) 👉 下一章
- [第十四章：platforms —— 全平台安装部署指南](./../03-core-concepts/14-platforms.md)
- [第十五章：providers —— 各大模型提供者配置大全](./../03-core-concepts/15-providers.md)
- [第十六章：plugins —— 插件系统开发指南](./../03-core-concepts/16-plugins.md)
- [第十七章： refactor —— OpenClaw 重构原则与工作流](./../03-core-concepts/17-refactor.md)
- [第十八章：reference —— 完整配置、模板、CLI 命令参考](./../03-core-concepts/18-reference.md)
- [第十九章：skills —— 技能系统核心概念与开发指南](./../03-core-concepts/19-skills.md)
- [第二十章：ClawHub —— 技能市场如何分享和获取技能](./../03-core-concepts/20-clawhub.md)
- [第二十一章：Canvas A2UI —— 实时可视化协作 workspace](./../04-client-ux/21-canvas.md)
- [第二十二章：语音唤醒 (Voice Wake) —— 语音交互体验](./../04-client-ux/22-voice-wake.md)
- [第二十三章：WebChat —— Gateway WebSocket 聊天界面](./../04-client-ux/23-webchat.md)
- [第二十四章：工具系统 (Tools) —— OpenClaw 工具调用框架设计](./../05-tools-automation/24-tools.md)
- [第二十五章：内置浏览器 —— 网页抓取和交互](./../05-tools-automation/25-browser.md)
- [第二十六章：Cron 自动化 —— 定时任务自动化](./../05-tools-automation/26-cron.md)
- [第二十七章：Onboarding —— 新手引导流程设计](./../05-tools-automation/27-onboarding.md)
- [第二十八章：blogwatcher —— 博客与 RSS 更新监控](./../06-builtin-skills/28-live-covers.md)
- [第二十九章：gh-issues —— GitHub Issues 自动修复编排](./../06-builtin-skills/29-gh-issues.md)
- [第三十章：coding-agent —— 调用外部编码代理](./../06-builtin-skills/30-coding-agent.md)
- [第三十一章：模型故障转移 (Model Failover) —— 如何提高可用性](./../07-ops-best-practices/31-failover.md)
- [第三十二章：调试技巧 —— 如何排查 OpenClaw 问题](./../07-ops-best-practices/32-debugging.md)
- [第三十三章：成本优化 —— 如何用模型分级降低总成本](./../07-ops-best-practices/33-cost-optimization.md)
- [第三十四章：部署运维 —— OpenClaw 网关生产环境最佳实践](./../07-ops-best-practices/34-deployment.md)
