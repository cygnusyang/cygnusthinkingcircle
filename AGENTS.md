# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## Project Overview

**技术影响力系统：跨平台内容分发平台**

以 knowledge-base 为唯一真相源，通过 LLM 管道自动适配 7 个平台的内容分发系统。

Access: https://cygnusyang.github.io/

## 统一入口

```bash
python tools/make.py new "文章标题"          # 创建新文章
python tools/make.py build article.md        # 生成博客+所有平台
python tools/make.py build --all             # 生成所有文章
python tools/make.py build --platform xiaohongshu,zhihu article.md
python tools/make.py publish                 # 发布到 GitHub Pages
python tools/make.py status                  # 查看文章状态
python tools/make.py config                  # 查看配置
```

## Architecture

```
cygnusthinkingcircle/
├── knowledge-base/                    # ★ 唯一真相源
│   └── articles/                      # 源文章
├── cygnusyang.github.io/              # Hugo GitHub Pages
│   └── content/posts/                 # 博客文章 (Hugo)
├── tools/
│   ├── make.py                        # ★ 统一入口 CLI
│   ├── lib/                           # 核心库 (article, platforms, llm, publisher)
│   ├── prompts/                       # 7个平台的 LLM 策略 prompt
│   └── output/                        # 生成的平台内容
└── .env.example
```

## Key Points

- 使用 `tools/make.py` 作为统一入口
- 文章发布到 Hugo 的 `content/posts/`（不是 Jekyll 的 `_posts/`）
- LLM 适配需要 `ANTHROPIC_API_KEY` 环境变量
