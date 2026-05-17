# AGENTS.md - Project Guide File / 项目引导文件

This file provides guidance to AI assistants (like Codex, Claude, etc.) when working with code in this repository.
此文件为 AI 助手（如 Codex、Claude 等）在此代码库中工作时提供指导。

## Table of Contents / 目录
- [Project Overview](#project-overview--项目概述)
- [Unified Entry Point](#unified-entry-point--统一入口)
- [Architecture](#architecture--架构)
- [Key Points](#key-points--关键要点)

## Project Overview / 项目概述

**Technical Influence System: Cross-Platform Content Distribution Platform**  
**技术影响力系统：跨平台内容分发平台**

A content distribution platform that uses knowledge-base as the single source of truth, automatically adapting content to 7 platforms through LLM pipelines.  
以 knowledge-base 为唯一真相源，通过 LLM 管道自动适配 7 个平台的内容分发系统。

Access: https://cygnusyang.github.io/

## Unified Entry Point / 统一入口

```bash
# Create new article / 创建新文章
python tools/make.py new "Article Title"

# Generate blog + all platforms / 生成博客+所有平台
python tools/make.py build article.md

# Generate all articles / 生成所有文章
python tools/make.py build --all

# Platform-specific generation / 平台特定生成
python tools/make.py build --platform xiaohongshu,zhihu article.md

# Publish to GitHub Pages / 发布到 GitHub Pages
python tools/make.py publish

# Check article status / 查看文章状态
python tools/make.py status

# View configuration / 查看配置
python tools/make.py config
```

## Architecture / 架构

```
cygnusthinkingcircle/
├── knowledge-base/                    # ★ Single Source of Truth / 唯一真相源
│   └── articles/                      # Source articles / 源文章
├── cygnusyang.github.io/              # Hugo GitHub Pages / Hugo GitHub Pages
│   └── content/posts/                 # Blog posts (Hugo) / 博客文章 (Hugo)
├── tools/
│   ├── make.py                        # ★ Unified CLI entry / 统一入口 CLI
│   ├── lib/                           # Core libraries / 核心库 (article, platforms, llm, publisher)
│   ├── prompts/                       # LLM strategies for 7 platforms / 7个平台的 LLM 策略 prompt
│   └── output/                        # Generated platform content / 生成的平台内容
└── .env.example                       # Environment example / 环境变量示例
```

## Key Points / 关键要点

- Use `tools/make.py` as the unified entry point / 使用 `tools/make.py` 作为统一入口
- Articles publish to Hugo's `content/posts/` (not Jekyll's `_posts/`) / 文章发布到 Hugo 的 `content/posts/`（不是 Jekyll 的 `_posts/`）
- LLM adaptation requires `ANTHROPIC_API_KEY` environment variable / LLM 适配需要 `ANTHROPIC_API_KEY` 环境变量
- Follow existing code conventions and patterns when making changes / 修改代码时遵循现有的代码约定和模式
- Check the project's README.md for more detailed usage instructions / 查看项目的 README.md 获取更详细的使用说明
