---
title: "第二章：环境搭建与基础配置"
date: 2026-04-18
author: "Your Name"
category: "GStack入门"
tags: ["gstack", "installation", "configuration", "claude-code"]
excerpt: "本文介绍GStack的安装步骤和基础配置。"
wechat_title: "第二章：环境搭建与基础配置"
wechat_cover: "images/chapter-02/cover.jpg"
---

# 第二章：环境搭建与基础配置

第一章解决的是“GStack 是什么”，这一章解决的是“怎么把它装好并真正跑起来”。这里会把安装、验证和最小配置一次讲清楚。

## 安装前准备

开始之前，先确认本机具备以下条件：

- **Claude Code**：GStack 的主要运行环境
- **Git**：用于获取技能仓库
- **Node.js 或 Bun**：安装脚本和部分工具依赖会用到

如果这三项都已具备，安装过程通常只需要几分钟。

## 安装 GStack

推荐使用官方仓库直接安装：

```bash
git clone --single-branch --depth 1 https://github.com/garrytan/gstack.git ~/.claude/skills/gstack
cd ~/.claude/skills/gstack && ./setup
```

这两条命令分别完成两件事：

- 第一条命令把 GStack 技能仓库拉到本地技能目录
- 第二条命令执行初始化脚本，补齐运行所需的依赖和配置

其中 `--single-branch --depth 1` 的作用是只拉取最新内容，安装更快，也更适合作为本地技能包使用。

## 验证安装是否成功

安装完成后，不要急着继续配置，先做最小验证：

```bash
claude
/office-hours
```

如果 Claude Code 能正常启动，并且 `/office-hours` 可以被识别，就说明核心技能已经装好。

## 基础配置

GStack 默认已经能用，但为了后续实战更顺畅，建议先完成两项基础配置。

### 1. 环境变量

如果后续技能会依赖 API Key 或其他敏感配置，可以先准备 `.env` 文件：

```bash
cp ~/.claude/skills/gstack/.env.example .env
nano .env
```

并不是所有场景都必须立刻配置 `.env`，但如果你的工作流依赖第三方服务，最好在一开始就把配置项整理好。

### 2. 技能预加载

如果你有几个每天都会用到的技能，可以考虑预加载：

```bash
export PRELOAD_SKILLS="office-hours,review"
```

这样做的目的不是“功能更多”，而是减少高频技能的首次加载开销。

## 常见问题排查

### `./setup` 执行失败

优先检查运行时依赖是否存在：

```bash
node --version
bun --version
```

通常问题集中在以下几类：

- 本地没有安装 Node.js 或 Bun
- 网络环境导致依赖下载失败
- 当前目录权限不正确

### Claude Code 找不到技能

先确认安装目录是否存在：

```bash
ls -la ~/.claude/skills/gstack/
```

如果目录缺失或内容异常，重新进入目录执行一次安装脚本：

```bash
cd ~/.claude/skills/gstack && ./setup
```

### `/browse` 启动失败

`/browse` 依赖 Playwright 对浏览器进行控制。如果浏览器依赖未安装，可以手动执行：

```bash
npx playwright install chromium
```

## 完成本章后，你应该具备什么？

到这里为止，你应该已经完成了四件事：

- 明确本机是否满足 GStack 的运行前提
- 成功安装 GStack 技能仓库
- 用最小命令验证技能是否可用
- 配好后续实战所需的基础环境

这一步很重要，因为后面的项目实战默认你已经具备一个可工作的本地环境。

---

**下一篇预告**：第三章《第一个 GStack 项目》，我们会用一个最小但完整的项目，把需求梳理、设计、实现、审查、测试和交付串成一条真实流程。
