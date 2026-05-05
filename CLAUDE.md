# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**技术影响力系统：跨平台内容分发平台**

以 knowledge-base 为唯一真相源，通过 LLM 管道自动适配 7 个平台的内容分发系统。

**三层结构：**
- 内容层：knowledge-base/（知识池，唯一真相源）
- 展示层：cygnusyang.github.io/（Hugo GitHub Pages）
- 流量层：小红书、知乎、微信公众号、今日头条、百家号、抖音

Access: https://cygnusyang.github.io/

## 统一入口

```bash
# 所有操作通过 make.py 完成
python tools/make.py new "文章标题"          # 创建新文章
python tools/make.py build article.md        # 生成博客+所有平台
python tools/make.py build --all             # 生成所有文章
python tools/make.py build --platform xiaohongshu,zhihu article.md  # 指定平台
python tools/make.py publish                 # 发布到 GitHub Pages
python tools/make.py status                  # 查看文章状态
python tools/make.py config                  # 查看配置
```

## Architecture

```
cygnusthinkingcircle/
├── knowledge-base/                    # ★ 唯一真相源 (Single Source of Truth)
│   └── articles/                      # 源文章（frontmatter + 正文）
│       ├── template.md                # 文章模板
│       └── 2026-05-05-my-article.md   # 具体文章
│
├── cygnusyang.github.io/              # Hugo GitHub Pages
│   ├── hugo.toml
│   └── content/posts/                 # Hugo 文章目录
│
├── tools/
│   ├── make.py                        # ★ 统一入口 CLI
│   ├── lib/                           # 核心库
│   │   ├── article.py                 # 文章解析、元数据管理
│   │   ├── platforms.py               # 7个平台的配置和策略
│   │   ├── llm.py                     # Anthropic Claude API 封装
│   │   └── publisher.py               # 发布到 GitHub Pages
│   ├── prompts/                       # LLM 平台策略 prompts
│   │   ├── blog.md                    # 博客（直接发布，不需LLM）
│   │   ├── xiaohongshu.md             # 小红书：种草+实操
│   │   ├── zhihu.md                   # 知乎：深度专业+SEO
│   │   ├── wechat.md                  # 微信：私域+品牌+搜一搜
│   │   ├── toutiao.md                 # 今日头条：深度内容红利
│   │   ├── baijiahao.md               # 百家号：百度SEO长尾
│   │   └── douyin.md                  # 抖音：30-60秒短视频脚本
│   ├── templates/                     # 旧模板（过渡期保留）
│   ├── output/                        # 生成的平台内容
│   │   ├── xiaohongshu/
│   │   ├── zhihu/
│   │   ├── wechat/
│   │   ├── toutiao/
│   │   ├── baijiahao/
│   │   └── douyin/
│   ├── blog-to-pages.py               # (旧) 从 IdealZero 导入
│   ├── kb-to-blog.py                  # (旧) 知识库→博客
│   ├── generate.py                    # (旧) 博客→平台
│   └── WORKFLOW.md                    # 工作流程文档
│
├── .env.example                       # 环境变量模板
└── CLAUDE.md                          # 本文件
```

## Content Strategy

### 平台分工 (7平台)

| 平台 | 定位 | 核心策略 |
|------|------|---------|
| **博客** (GitHub Pages) | SEO长尾+技术品牌 | 深度长文，原样发布 |
| **小红书** | 种草+高客单 | 数字标题+步骤拆解+情绪共鸣 |
| **知乎** | 深度专业+SEO | 前150字埋关键词+热点嫁接+代码验证 |
| **微信公众号** | 私域沉淀+品牌 | 搜一搜SEO+社交传播+转发钩子 |
| **今日头条** | 深度内容红利 | 科普化表达+SCQA框架+独立流量池 |
| **百家号** | 百度SEO长尾 | 标题关键词+SCQA+图片ALT优化 |
| **抖音** | 爆款引流 | 30-60秒脚本+3秒钩子+分镜设计 |

### 判断标准

**能否沉淀为长期认知资产？**
- YES → 写知识库（主内容）
- NO → 做流量切片 or 不做

## Key Points

- **knowledge-base/** 是唯一真相源，所有内容从这里出发
- **make.py** 是统一入口，不要直接调用旧脚本
- **cygnusyang.github.io/** 使用 Hugo + FixIt 主题（不是 Jekyll）
- 文章发布到 `content/posts/`（不是 `_posts/`）
- LLM 适配需要设置 `ANTHROPIC_API_KEY` 环境变量
- 旧脚本 (blog-to-pages.py, kb-to-blog.py, generate.py) 保留但不再推荐使用
