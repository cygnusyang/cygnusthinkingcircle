# 快速参考卡片

## 🚀 常用命令

### 文章操作

```bash
# 创建文章
python tools/make.py new "文章标题"

# 创建集合文章
python tools/make.py new "章节标题" --category "集合名"

# 构建文章
python tools/make.py build 文件名.md
python tools/make.py build --all

# 增量构建
python tools/make.py build --all --incremental

# 多平台适配
python tools/make.py build --platform xiaohongshu,zhihu 文件名.md
```

### 集合操作

```bash
# 列出集合
python tools/make.py collection list

# 构建集合
python tools/make.py collection build 集合名
python tools/make.py collection build --all

# 预览构建
python tools/make.py collection build 集合名 --dry-run
```

### 发布与查看

```bash
# 发布到 GitHub Pages
python tools/make.py publish

# 查看状态
python tools/make.py status

# 查看统计
python tools/make.py stats

# 查看配置
python tools/make.py config
```

### Hugo 操作

```bash
# 本地预览
cd cygnusyang.github.io && hugo server

# 构建静态文件
hugo

# 清理缓存
rm -rf resources public .hugo_build.lock
```

## 📁 目录结构

```
cygnusthinkingcircle/
├── knowledge-base/         # 知识库
│   ├── articles/          # 文章（独立+集合）
│   └── catalog.yaml       # 集合元数据
│
├── cygnusyang.github.io/  # 博客（子模块）
│   ├── content/posts/     # 博客文章
│   ├── hugo.toml          # 配置文件
│   └── themes/FixIt/      # 主题
│
├── tools/                 # 工具
│   ├── make.py           # 统一入口
│   ├── lib/              # 核心库
│   ├── prompts/          # 平台策略
│   └── output/           # 生成内容
│
├── .env                   # 环境配置
└── requirements.txt       # Python 依赖
```

## 📝 Frontmatter 模板

```yaml
---
title: "文章标题"
date: 2026-05-17
tags: ["标签1", "标签2"]
category: "分类"
summary: "文章摘要"
keywords: ["关键词"]
platforms: ["blog"]
---

## 标题

内容...
```

## 🎨 平台列表

| 平台 | key | 描述 |
|------|-----|------|
| 博客 | blog | 直接发布 |
| 小红书 | xiaohongshu | 种草+实操 |
| 知乎 | zhihu | 深度专业+SEO |
| 微信 | wechat | 私域+品牌 |
| 头条 | toutiao | 深度内容 |
| 百家号 | baijiahao | 百度SEO |
| 抖音 | douyin | 短视频脚本 |

## 🔧 环境变量

```env
# .env 文件
LLM_API_KEY=sk-ant-xxxxxxxx
LLM_PROVIDER=anthropic
LLM_MODEL=claude-sonnet-4-20250514
```

## 🐛 常见问题快速修复

| 问题 | 解决方案 |
|------|---------|
| 子模块未初始化 | `git submodule update --init --recursive` |
| 构建后未更新 | `rm -rf public/ && hugo` |
| 依赖缺失 | `pip install -r requirements.txt` |
| 虚拟环境未激活 | `source .venv/bin/activate` |
| Hugo 缓存问题 | `rm -rf resources public .hugo_build.lock` |

## 📊 Shell 别名

添加到 `~/.zshrc` 或 `~/.bashrc`：

```bash
# 别名
alias kb="cd ~/cygnusthinkingcircle"
alias kb-new="python tools/make.py new"
alias kb-build="python tools/make.py build --all"
alias kb-publish="python tools/make.py publish"
alias kb-preview="cd cygnusyang.github.io && hugo server"
alias kb-status="python tools/make.py status"
```

使用：

```bash
kb                          # 进入项目
kb-new "标题"               # 创建文章
kb-build                    # 构建文章
kb-publish                  # 发布博客
kb-preview                  # 本地预览
kb-status                   # 查看状态
```

## 🌐 重要链接

- [Hugo 官方文档](https://gohugo.io/documentation/)
- [FixIt 主题文档](https://fixit.lruihao.cn/)
- [Claude Code 文档](https://claude.ai/code)
- [Anthropic API 文档](https://docs.anthropic.com/)
- [GitHub Pages 文档](https://docs.github.com/en/pages)

## 💡 工作流速记

```
创作 → 构建 → 预览 → 发布
```

```
知识库 → tools → Hugo → GitHub Pages
```