---
title: "第八章：GStack的learnings与跨会话经验"
date: 2026-04-18
author: "Your Name"
category: "智能体技术基础"
tags: ["gstack", "learn", "learnings", "memory", "claude-code"]
excerpt: "基于官方仓库，解释 GStack 如何通过 learnings 机制把跨会话经验、偏好和项目模式沉淀下来。"
wechat_title: "第八章：GStack的learnings与跨会话经验"
wechat_cover: "images/chapter-08/cover.jpg"
---

# 第八章：GStack的learnings与跨会话经验

## 引言

前一章讲的是 GStack 如何连接真实网页和外部环境。这一章继续回答另一个很关键的问题：当一次会话结束后，GStack 是怎样把经验留下来的？

官方仓库给出的答案，是一套更具体、也更实用的机制：**learnings**。

## `/learn` 在官方文档里的定义

官方 `docs/skills.md` 把 `/learn` 定义成 **institutional memory mode**。

它的核心含义是：GStack 会把每次会话中积累出来的模式、坑点、偏好和架构决策沉淀下来，并在后续会话里重新用起来。

官方文档明确写到，这些内容会存到：

```text
~/.gstack/projects/$SLUG/learnings.jsonl
```

这说明 GStack 的“记忆”首先不是一个抽象 AI 模型内部结构，而是项目级、可管理、可检查、可清理的 learnings 文件。

## learnings 里记录什么？

按照官方 `docs/skills.md`，典型的 learnings 包括：

- 项目中的固定模式
- 常见坑点
- 用户偏好
- 架构决策
- 与具体文件相关的经验

这类信息并不是为了让 AI“像人一样拥有长期记忆”，而是为了让它在后续会话里减少重复试错，优先采用已经在项目里验证过的做法。

## 官方行为：其他技能会主动搜索 learnings

`/learn` 本身只是查看和管理入口，真正重要的是其他技能会使用这些内容。

官方文档明确说明：

- 其他技能会在给建议前自动搜索 learnings
- 当某条历史经验被应用时，会显示类似 “Prior learning applied” 的提示

这意味着 learnings 不是孤立的备忘录，而是整个 GStack 工作流会反复调用的项目知识层。

## 一条最贴近官方的理解方式

如果用最保守、最符合官方文档的方式去理解，GStack 的 learnings 机制更像三件事的组合：

- 项目级经验库
- 跨会话偏好存档
- 供其他技能调用的历史上下文

它的目标不是构造一个抽象“全知记忆大脑”，而是让团队化工作流具备连续性。

## `/learn` 能做什么？

根据官方 `docs/skills.md`，`/learn` 提供的能力包括：

- 查看当前项目已经积累了多少 learnings
- 搜索某类模式或经验
- 识别引用文件已经失效的陈旧条目
- 清理过期 learnings
- 导出 learnings 供团队共享

这很像一个项目知识面板：它不是只为了“记住更多”，而是为了把已经学到的东西维持在可用状态。

## learnings 为什么重要？

如果没有这层机制，每个会话几乎都要重新学习一遍项目的隐性规则，例如：

- API 返回格式的约定
- 测试辅助函数放在哪里
- 数据库访问是否必须经过 repository 层
- 某些目录里的代码风格和结构惯例

有了 learnings，这些信息就可以在后续会话里被优先提取出来，从而减少重复探索。

## 官方描述中的 learnings 结构

官方 `docs/skills.md` 明确写到，每条 learning 至少具备这些属性：

- confidence score
- source attribution
- files it references

这说明 learnings 并不是随便写一句笔记，而是带有可信度、来源和文件关联的记录。

这也解释了为什么 `/learn` 可以判断某些条目已经过时：因为它知道这些经验原来对应哪些文件。

## 与技能 preamble 的关系

官方 `ARCHITECTURE.md` 还提到，很多技能在运行前会经过统一 preamble，其中包含 learnings 相关逻辑。

文档里明确说到：

- 会统计当前项目加载了多少 learnings
- 当条目足够多时，会自动做一次简短搜索

这说明 learnings 已经嵌进技能运行前的公共准备过程，而不是用户必须每次手动调用 `/learn` 才能生效。

## GStack 的“记忆”首先体现为项目经验沉淀

从官方仓库看，GStack 当前明确公开的“记忆”能力，核心就是 learnings 机制。它关注的是把项目中的模式、偏好、坑点和决策沉淀下来，并在后续会话里继续使用。

## 一个更贴近官方的结构图

下面这张图表达的是官方文档能明确支持的最小链路：

```mermaid
graph LR
    A[Session work] --> B[Project learnings.jsonl]
    B --> C[/learn]
    B --> D[Other gstack skills]
    D --> E[Prior learning applied]
```

它表示的是：

- 会话中积累出的经验进入项目 learnings
- `/learn` 负责查看、搜索、清理和导出
- 其他技能会自动检索并应用这些 learnings

## 这一章里的关键结论

GStack 官方当前明确公开的“跨会话经验机制”，核心就是 `/learn` 和项目级 learnings 文件。

它的价值不在于抽象理论，而在于非常具体的三件事：

- 让经验能留下来
- 让后续技能能读到这些经验
- 让陈旧经验可以被清理和维护

这让 GStack 的工作流不只是一次性执行，而是能够随着项目推进逐步积累上下文。

---

**下一篇预告**：第九章《GStack 的跨代理协作与并行工作》，继续看官方仓库里真正公开的多 AI 协作方式是什么。
