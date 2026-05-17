# 02. 快速开始

## ⚡ 5 分钟上手

### 前置条件

- **Python 3.8+** 已安装
- **Git** 已安装
- **GitHub 账号** （用于 Pages 托管）

### 步骤 1: 克隆项目

```bash
# 克隆主仓库
git clone git@github.com:cygnusyang/cygnusthinkingcircle.git
cd cygnusthinkingcircle

# 初始化子模块（博客）
git submodule update --init --recursive
```

### 步骤 2: 安装依赖

```bash
# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装 Python 依赖
pip install -r requirements.txt

# 安装 Hugo
# macOS
brew install hugo

# Linux
wget https://github.com/gohugoio/hugo/releases/download/v0.132.2/hugo_extended_0.132.2_linux-amd64.deb
sudo dpkg -i hugo_extended_0.132.2_linux-amd64.deb

# Windows (使用 scoop 或手动下载)
scoop install hugo-extended
```

### 步骤 3: 配置 API Key

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件
# 填入你的 Anthropic API Key
```

`.env` 文件内容：

```env
# Anthropic Claude API
LLM_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
LLM_PROVIDER=anthropic
LLM_MODEL=claude-sonnet-4-20250514
```

> **提示**：API Key 可在 [Anthropic Console](https://console.anthropic.com/) 获取

### 步骤 4: 创建第一篇文章

```bash
# 使用模板创建新文章
python tools/make.py new "Hello World - 我的第一篇文章"
```

这会在 `knowledge-base/articles/` 生成：

```
2026-05-17-hello-world.md
```

### 步骤 5: 编辑文章

打开生成的文件，编辑内容：

```markdown
---
title: "Hello World - 我的第一篇文章"
date: 2026-05-17
tags: ["test"]
category: ""
summary: "测试文章"
keywords: []
platforms: ["blog"]
---

## 背景

这是我的第一篇文章！

## 核心概念

Markdown 是一种轻量级标记语言。

## 实战

```python
print("Hello, World!")
```

## 判断

写博客是沉淀知识的最好方式。
```

### 步骤 6: 生成博客

```bash
# 构建所有文章（只生成博客）
python tools/make.py build --all
```

输出：

```
📄 处理: 2026-05-17-hello-world.md
✅ 完成：处理了 1 篇文章
📂 博客内容: cygnusyang.github.io/content/posts
💡 下一步: make.py publish  # 发布到 GitHub Pages
```

### 步骤 7: 本地预览

```bash
cd cygnusyang.github.io
hugo server
```

访问 `http://localhost:1313` 查看效果。

### 步骤 8: 发布到 GitHub Pages

```bash
# 回到主目录
cd ..

# 发布（会自动 commit + push 到博客子模块）
python tools/make.py publish
```

稍等几分钟，访问 `https://你的用户名.github.io/` 查看在线效果。

## 🎉 恭喜！

你已经成功搭建了个人知识库系统！

## 📋 常用命令速查

```bash
# 文章管理
python tools/make.py new "文章标题"                    # 创建文章
python tools/make.py build 2026-05-17-article.md      # 构建单篇
python tools/make.py build --all                      # 构建所有

# 集合管理
python tools/make.py collection list                  # 列出集合
python tools/make.py collection build 01-openclaw     # 构建集合

# 发布与查看
python tools/make.py publish                          # 发布博客
python tools/make.py status                           # 查看状态

# 本地预览
cd cygnusyang.github.io && hugo server                # 启动预览

# 多平台适配（需要 API Key）
python tools/make.py build --platform xiaohongshu,zhihu 2026-05-17-article.md
```

## 🔍 下一步

- [03. 知识库搭建](./03-knowledge-base-setup.md) - 深入了解知识库结构
- [04. GitHub Pages 搭建](./04-github-pages-setup.md) - 配置个人博客
- [05. Claude Code 安装与使用](./05-claude-code.md) - 智能开发助手