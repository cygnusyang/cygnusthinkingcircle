# 06. 完整工作流

## 🎯 本教程目标

演示从零开始创建并发布一篇文章的完整流程。

## 📝 场景

我们要创建一篇关于 **"Hugo 博客优化"** 的技术文章，并发布到博客。

## 🚀 完整步骤

### 步骤 1: 准备环境

```bash
# 进入项目目录
cd cygnusthinkingcircle

# 激活虚拟环境
source .venv/bin/activate

# 确认依赖已安装
python tools/make.py config
```

输出示例：

```
⚙️  配置
============================================================

🔌 LLM 提供商: anthropic
   API Key:     sk-ant-...xxxx
   Model:       claude-sonnet-4-20250514
   Base URL:    (SDK默认)

📂 目录:
   知识库:      /Users/xxx/cygnusthinkingcircle/knowledge-base
   博客输出:    /Users/xxx/cygnusthinkingcircle/cygnusyang.github.io/content/posts
   平台输出:    /Users/xxx/cygnusthinkingcircle/tools/output
   Prompts:     /Users/xxx/cygnusthinkingcircle/tools/prompts

📋 可用平台 (7 个):
   blog              - 博客（直接发布）
   xiaohongshu       - 小红书：种草+实操
   zhihu             - 知乎：深度专业+SEO
   wechat            - 微信：私域+品牌
   toutiao           - 今日头条：深度内容
   baijiahao         - 百家号：百度SEO
   douyin            - 抖音：短视频脚本
```

### 步骤 2: 创建文章

```bash
python tools/make.py new "Hugo 博客性能优化实战"
```

输出：

```
📁 创建目录: knowledge-base/articles
✅ 创建文章: knowledge-base/articles/2026-05-17-hugo-博客性能优化实战.md
   用编辑器打开编辑内容后，运行: make.py build 2026-05-17-hugo-博客性能优化实战.md
```

### 步骤 3: 编辑文章

用你喜欢的编辑器打开文件，编辑内容：

```bash
# VS Code
code knowledge-base/articles/2026-05-17-hugo-博客性能优化实战.md

# 或 Vim
vim knowledge-base/articles/2026-05-17-hugo-博客性能优化实战.md
```

填写内容：

```markdown
---
title: "Hugo 博客性能优化实战"
date: 2026-05-17
tags: ["Hugo", "性能优化", "Web"]
category: "技术"
summary: "本文介绍 Hugo 博客的性能优化方法，包括图片压缩、缓存策略、代码分割等实用技巧"
keywords: ["Hugo", "性能", "优化", "静态站点"]
platforms: ["blog"]
---

## 背景

Hugo 是一个快速的静态站点生成器，但默认配置下还有很多优化空间。本文分享我在优化 Hugo 博客时积累的经验。

## 核心概念

### Hugo 的构建流程

Hugo 的构建流程包括：
1. 读取 content 目录下的 Markdown 文件
2. 应用主题和模板
3. 生成静态 HTML、CSS、JS
4. 输出到 public 目录

### 性能瓶颈

常见的性能瓶颈：
- 未压缩的资源
- 大尺寸图片
- 未利用缓存
- 冗余的 CSS/JS

## 实战

### 1. 启用资源压缩

在 `hugo.toml` 中配置：

```toml
[minify]
  disableSVG = false
  [minify.tdewolff]
    [minify.tdewolff.html]
      keepDocumentTags = true
      keepEndTags = true
```

### 2. 图片优化

使用 Hugo Pipes 处理图片：

```html
{{ $image := resources.Get "images/large.jpg" }}
{{ $resized := $image.Resize "800x webp" }}
<img src="{{ $resized.RelPermalink }}" alt="描述">
```

### 3. 启用缓存

在服务器配置中启用缓存：

```nginx
# nginx 配置
location / {
  expires 1y;
  add_header Cache-Control "public, immutable";
}
```

### 4. 代码分割

异步加载非关键 JavaScript：

```html
<script async src="/js/analytics.js"></script>
```

## 判断

性能优化是一个持续的过程，需要结合实际场景选择合适的策略。以上方法可以显著提升 Hugo 博客的加载速度。
```

### 步骤 4: 本地预览

```bash
# 构建文章
python tools/make.py build 2026-05-17-hugo-博客性能优化实战.md
```

输出：

```
📄 处理: 2026-05-17-hugo-博客性能优化实战.md
✅ 完成：处理了 1 篇文章
📂 博客内容: cygnusyang.github.io/content/posts
💡 下一步: make.py publish  # 发布到 GitHub Pages
```

启动本地预览：

```bash
cd cygnusyang.github.io
hugo server
```

访问 `http://localhost:1313` 查看效果。

### 步骤 5: 生成多平台内容（可选）

```bash
# 生成小红书和知乎版本
cd ..
python tools/make.py build --platform xiaohongshu,zhihu 2026-05-17-hugo-博客性能优化实战.md
```

输出：

```
📄 处理: 2026-05-17-hugo-博客性能优化实战.md
  🤖 LLM 适配各平台...
    生成 小红书...
    生成 知乎...
✅ 完成：处理了 1 篇文章
📂 平台内容: tools/output
📂 博客内容: cygnusyang.github.io/content/posts
```

查看生成的内容：

```bash
# 小红书版本
cat tools/output/xiaohongshu/2026-05-17-hugo-博客性能优化实战.md

# 知乎版本
cat tools/output/zhihu/2026-05-17-hugo-博客性能优化实战.md
```

### 步骤 6: 检查状态

```bash
python tools/make.py status
```

输出：

```
============================================================
📊 内容状态总览
============================================================

源文章 (1 篇):
  📝 Hugo 博客性能优化实战
     日期: 2026-05-17 | 平台: blog

平台输出:
  📭 小红书: 1 篇
  📭 知乎: 1 篇
  📭 博客: content/posts/): 1 篇
```

### 步骤 7: 发布到 GitHub Pages

```bash
python tools/make.py publish
```

输出：

```
📤 发布到 GitHub Pages...
[main f3d2a1c] post: publish 1 articles
 1 file changed, 100 insertions(+)
To github.com:cygnusyang/cygnusyang.github.io.git
   abc1234..f3d2a1c  main -> main
✅ 发布完成！稍后访问 https://cygnusyang.github.io/
```

### 步骤 8: 在线查看

等待几分钟（GitHub Pages 通常需要 1-3 分钟部署），访问你的博客：

```
https://你的用户名.github.io/posts/2026/05/17/hugo-博客性能优化实战/
```

## 🔄 完整工作流图

```
┌─────────────────────────────────────────────────────────────┐
│ 1. 创作阶段                                                  │
│ ─────────────────────────────────────────────────────────   │
│ python tools/make.py new "标题"                            │
│ ↓                                                           │
│ 编辑 knowledge-base/articles/YYYY-MM-DD-slug.md            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. 构建阶段                                                  │
│ ─────────────────────────────────────────────────────────   │
│ python tools/make.py build article.md                      │
│ ↓                                                           │
│ ┌─────────────┐      ┌──────────────┐                      │
│ │ Hugo 博客   │      │  多平台内容   │                      │
│ │ content/    │      │  tools/output/ │                      │
│ └─────────────┘      └──────────────┘                      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. 预览阶段                                                  │
│ ─────────────────────────────────────────────────────────   │
│ cd cygnusyang.github.io && hugo server                     │
│ ↓                                                           │
│ 访问 http://localhost:1313                                  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. 发布阶段                                                  │
│ ─────────────────────────────────────────────────────────   │
│ python tools/make.py publish                               │
│ ↓                                                           │
│ GitHub Pages 自动部署                                       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. 访问阶段                                                  │
│ ─────────────────────────────────────────────────────────   │
│ https://你的用户名.github.io/                              │
└─────────────────────────────────────────────────────────────┘
```

## 📚 集合文章工作流

### 创建集合

```bash
# 1. 创建集合目录
mkdir -p "knowledge-base/articles/10-Hugo实战"

# 2. 创建集合封面
cat > "knowledge-base/articles/10-Hugo实战/README.md" << 'EOF'
---
title: "Hugo 实战"
date: 2026-05-17
summary: "从入门到精通的 Hugo 博客教程"
weight: 1
---

本系列文章介绍 Hugo 博客的完整搭建和优化流程。
EOF
```

### 添加集合文章

```bash
# 创建集合中的文章
python tools/make.py new "第一章：快速入门" --category "10-Hugo实战"
```

### 构建集合

```bash
# 构建整个集合
python tools/make.py collection build 10-Hugo实战
```

### 发布集合

```bash
python tools/make.py publish
```

## 🤖 使用 Claude Code 辅助

### 创建文章

启动 Claude Code：

```bash
claude
```

输入指令：

```
帮我创建一篇关于 "Docker 容器化最佳实践" 的文章，参考 template.md 的格式
```

Claude Code 会：
1. 分析项目结构
2. 创建新文章
3. 填充内容框架

### 代码审查

```
审查 tools/lib/publisher.py 的代码，找出可以改进的地方
```

### 调试

```
发布功能报错了，错误信息是 "Git operation failed"，帮我排查
```

## 💡 效率提升技巧

### 1. 批量操作

```bash
# 批量构建所有文章
python tools/make.py build --all --incremental
```

### 2. Shell 别名

在 `~/.zshrc` 或 `~/.bashrc` 添加：

```bash
alias kb="cd ~/cygnusthinkingcircle"
alias kb-new="python tools/make.py new"
alias kb-build="python tools/make.py build --all"
alias kb-publish="python tools/make.py publish"
alias kb-preview="cd cygnusyang.github.io && hugo server"
```

使用：

```bash
kb
kb-new "新文章标题"
kb-build
kb-publish
kb-preview
```

### 3. 自动化脚本

创建 `publish.sh`：

```bash
#!/bin/bash
set -e

python tools/make.py build --all
python tools/make.py publish

echo "✅ 发布完成！"
```

使用：

```bash
chmod +x publish.sh
./publish.sh
```

## 📊 工作流统计

```bash
# 查看内容统计
python tools/make.py stats

# JSON 格式（用于脚本）
python tools/make.py stats --json > stats.json
```

## 🎓 进阶工作流

### 1. 自动部署

配置 GitHub Actions，实现自动部署（参考 04-github-pages-setup.md）。

### 2. 内容审核流程

```
草稿 → 团队评审 → 修改 → 技术审查 → 发布
```

### 3. 版本管理

```
feature/article-x → develop → main → 发布
```

## 💡 下一步

- [07. 故障排查](./07-troubleshooting.md) - 常见问题解决