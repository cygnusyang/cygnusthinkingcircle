---
title: "第九章：GStack的跨代理协作与并行工作"
date: 2026-04-18
author: "Your Name"
category: "前沿探索"
tags: ["gstack", "pair-agent", "codex", "parallel-sprints", "ai-agents"]
excerpt: "基于官方仓库，解释 GStack 如何通过 pair-agent、Codex second opinion 和并行冲刺，把多 AI 协作落到真实工作流里。"
wechat_title: "第九章：GStack的跨代理协作与并行工作"
wechat_cover: "images/chapter-09/cover.jpg"
---

# 第九章：GStack的跨代理协作与并行工作

## 引言

到这一章，重点不再是单个技能怎么工作，而是 GStack 怎样把多个 AI、多个会话、多个工作流组织起来。

如果只看官方仓库，GStack 公开呈现出来的“多代理协作”重点是几种非常具体的协作能力：

- 并行冲刺
- 跨 AI 浏览器共享
- 第二模型复核
- 多会话下的分工推进

## 官方语境里的并行工作

README 里有一节叫 **Parallel sprints**。这个说法很重要，因为它揭示了 GStack 官方对“多代理”最真实的理解：

不是先抽象出一套通用多智能体理论，而是先把多个并行工作流跑起来。

在官方叙述里，GStack 的并行能力来自这些现实前提：

- 不同阶段由不同技能承担
- 浏览器可以成为共享执行环境
- 复核可以由不同模型完成
- 设计、审查、测试、发布都能并行推进

## `/pair-agent`：跨 AI 共享浏览器

官方 README 对 `/pair-agent` 的描述非常具体。它的作用是把浏览器环境共享给其他 AI agent，而不是只让 Claude Code 自己使用。

官方说明包括：

- 一个命令就能建立共享浏览器协作
- 不同 agent 各自获得独立标签页
- 可以同机，也可以远程
- 自动处理 token、tab isolation、rate limiting 和 activity attribution

这说明 GStack 的“多代理协作”首先是从共享外部环境开始的，而不是从抽象控制平面开始的。

### 一条贴近官方描述的协作链路

```mermaid
graph TD
    A[Claude Code] --> B[/pair-agent]
    B --> C[GStack Browser]
    C --> D[Agent Tab 1]
    C --> E[Agent Tab 2]
    C --> F[Agent Tab N]
```

这张图对应的是官方 README 中 `/pair-agent` 的核心能力：多个 agent 在同一浏览器体系里协作，但仍保持隔离。

## OpenClaw 与多会话协作

官方 README 还专门写了 OpenClaw 集成。

这里的重点不是“定义一种新的多代理理论”，而是：

- OpenClaw 可以通过 ACP 生成 Claude Code 会话
- 每个会话都能带着 GStack 技能运行
- 可以根据任务类型，把不同会话路由到不同工作流

比如官方 README 给出的例子包括：

- 安全审计走 `/cso`
- 代码评审走 `/review`
- QA 走 `/qa`
- 端到端构建走 `/autoplan -> implement -> /ship`

这说明 GStack 官方真正强调的是**按任务路由不同会话**。

## `/codex`：第二模型复核

官方还把 `/codex` 定义成 **Second Opinion**。

README 和 `docs/skills.md` 都明确说，这个技能的意义是让 OpenAI Codex CLI 对同一份改动做独立复核，然后和 Claude 的 `/review` 结果对照。

这是一种非常务实的多模型协作方式：

- 同一份代码
- 两个不同模型
- 两套不同盲点
- 最后看重叠问题和差异问题

它体现的是一种围绕真实工程任务设计出来的多模型协作方式。

## `/autoplan`：把多轮 review 串成一条自动流水线

官方 `docs/skills.md` 对 `/autoplan` 的定义也非常关键。

它不是一个普通的计划技能，而是：

- 顺序运行 `/plan-ceo-review`
- `/plan-design-review`
- `/plan-eng-review`

也就是说，它把多个专业角色的规划和审查串成一条自动流水线。

这种协作方式不是“多个 agent 同时对话”，但它确实是多角色协同的一种非常实际的工程实现。

## GStack 官方公开的“多代理能力”有哪些？

如果只根据官方 README 和 `docs/skills.md`，可以把这部分能力概括成四类：

### 1. 多角色顺序协作

由 `/autoplan` 和整条 sprint 流程体现。

### 2. 多模型复核

由 `/codex` 和 `/review` 的交叉分析体现。

### 3. 多会话任务路由

由 OpenClaw 集成和技能路由体现。

### 4. 多 agent 共享浏览器

由 `/pair-agent` 体现。

## 为什么这比“通用多智能体理论”更有价值？

因为官方 GStack 关注的是实际交付：

- 谁来规划
- 谁来审查
- 谁来测试
- 谁来共享环境
- 谁来给第二意见

这让“多代理协作”不再停留在概念层，而是直接映射到真实工程工作流。

## 这一章里的关键结论

GStack 当前公开出来的“多代理协作”，本质上是一套围绕真实工程流程设计的协作机制：

- `/pair-agent` 共享浏览器
- `/codex` 提供第二模型视角
- `/autoplan` 串联多角色规划
- OpenClaw 等集成把不同任务路由到不同会话

这些能力共同构成了 GStack 当前公开出来的跨代理协作方式。

---

**下一篇预告**：第十章《GStack 的发布自动化与持续监控》，继续看 GStack 如何把交付、部署、监控和复盘串成闭环。
