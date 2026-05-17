# 04. GitHub Pages 搭建

## 🌐 什么是 GitHub Pages

GitHub Pages 是 GitHub 提供的免费静态网站托管服务，支持：

- ✅ 免费托管
- ✅ 自定义域名
- ✅ HTTPS 自动配置
- ✅ 全球 CDN
- ✅ 自动部署

## 📦 博客架构

本系统使用 **Hugo + FixIt 主题**：

```
cygnusyang.github.io/
├── hugo.toml              # Hugo 配置文件
├── content/
│   ├── posts/             # 博客文章（由 tools 生成）
│   │   ├── 2026-05-17-xxx.md
│   │   └── openclaw/      # 集合目录
│   │       ├── _index.md
│   │       └── 2026-05-17-xxx.md
│   └── _index.md          # 首页
├── themes/
│   └── FixIt              # 主题（Git 子模块）
├── layouts/               # 自定义布局
├── static/                # 静态资源
│   └── images/
├── data/                  # 数据文件
├── assets/                # 资源文件
└── public/                # 构建输出（.gitignore）
```

## 🚀 从零搭建

### 步骤 1: 创建 GitHub 仓库

1. 访问 [GitHub 新建仓库](https://github.com/new)
2. 仓库名：`你的用户名.github.io`（必须匹配）
3. 设置为 Public（公开）
4. 不要初始化 README
5. 点击 "Create repository"

### 步骤 2: 初始化 Hugo 博客

```bash
# 本地创建目录
mkdir 你的用户名.github.io
cd 你的用户名.github.io

# 初始化 Git 仓库
git init

# 初始化 Hugo
hugo new site . --force

# 添加 FixIt 主题
git submodule add https://github.com/Lruihao/FixIt.git themes/FixIt

# 复制主题配置
cp themes/FixIt/hugo.toml.example hugo.toml

# 创建必要目录
mkdir -p content/posts static/images layouts data assets
```

### 步骤 3: 配置 hugo.toml

```toml
baseURL = "https://你的用户名.github.io/"
languageCode = "zh-CN"
title = "你的博客标题"
theme = "FixIt"

# 时区
timeZone = "Asia/Shanghai"

# 允许 markdown 中嵌入原始 HTML
[markup.goldmark.renderer]
  unsafe = true

# 分页
[pagination]
  pagerSize = 10

# 构建设置
[build]
  writeStats = true

# 主题配置
[params]
  description = "你的博客描述"
  [params.author]
    name = "你的名字"
    email = "your@email.com"

  # 主题模式
  defaultTheme = "auto"

  # 显示阅读时间和字数
  showReadingTime = true
  showWordCount = true

  # 页面配置
  [params.page]
    # 目录
    [params.page.toc]
      enable = true
      auto = true
      position = "right"

    # 相关文章
    [params.page.related]
      enable = true
      count = 5
```

### 步骤 4: 创建首页

```bash
# 创建首页
cat > content/_index.md << 'EOF'
---
title: "首页"
---

欢迎来到我的博客！
EOF
```

### 步骤 5: 首次部署

```bash
# 生成静态文件
hugo

# 提交到 Git
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin git@github.com:你的用户名/你的用户名.github.io.git
git push -u origin main
```

等待几分钟，访问 `https://你的用户名.github.io/` 查看效果。

### 步骤 6: 配置 GitHub Actions（可选）

创建 `.github/workflows/hugo.yml`：

```yaml
name: Hugo

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v3
        with:
          submodules: true
          fetch-depth: 0

      - name: Setup Hugo
        uses: peaceiris/actions-hugo@v2
        with:
          hugo-version: latest
          extended: true

      - name: Build
        run: hugo --minify

      - name: Deploy
        uses: peaceiris/actions-gh-pages@v3
        if: github.ref == 'refs/heads/main'
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./public
```

提交后，每次 push 都会自动部署。

## 🔧 配置主题

### 1. 更新主题子模块

```bash
cd cygnusyang.github.io
git submodule update --remote --merge
```

### 2. 自定义样式

创建 `assets/css/custom.css`：

```css
/* 自定义样式 */
body {
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
}

/* 自定义代码块样式 */
.highlight {
  background-color: #f5f5f5;
}
```

### 3. 自定义布局

在 `layouts/` 目录下覆盖主题模板：

```
layouts/
├── _default/
│   └── single.html       # 自定义文章页
├── partials/
│   └── footer.html       # 自定义页脚
└── shortcodes/
    └── youtube.html      # 自定义 Shortcode
```

## 🎨 功能增强

### 1. 评论系统

**Waline (推荐):**

1. 部署 Waline 到 Vercel
2. 在 `hugo.toml` 添加配置：

```toml
[params.comments]
  enable = true
  type = "waline"

  [params.comments.waline]
    serverURL = "https://your-waline.vercel.app"
```

**Giscus:**

```toml
[params.comments]
  enable = true
  type = "giscus"

  [params.comments.giscus]
    repo = "username/repo"
    repoId = "R_xxx"
    category = "Announcements"
    categoryId = "DIC_xxx"
    mapping = "pathname"
```

### 2. 访问统计

**百度统计:**

```toml
[params.analytics]
  enable = true
  [params.analytics.baidu]
    id = "你的百度统计ID"
```

**Google Analytics:**

```toml
[params.analytics]
  enable = true
  [params.analytics.google]
    id = "G-XXXXXXXXXX"
```

### 3. 搜索功能

**Lunr.js (本地搜索):**

```toml
[params.search]
  enable = true
  type = "lunr"
```

**Algolia (云端搜索):**

```toml
[params.search]
  enable = true
  type = "algolia"
  [params.search.algolia]
    appId = "YOUR_APP_ID"
    apiKey = "YOUR_SEARCH_API_KEY"
    indexName = "YOUR_INDEX_NAME"
```

## 🌍 自定义域名

### 步骤 1: 购买域名

从阿里云、腾讯云、Namecheap 等购买域名。

### 步骤 2: 配置 DNS

添加 DNS 记录：

| 类型 | 名称 | 值 |
|------|------|-----|
| CNAME | www | 你的用户名.github.io |
| A | @ | 185.199.108.153 |
| A | @ | 185.199.109.153 |
| A | @ | 185.199.110.153 |
| A | @ | 185.199.111.153 |

### 步骤 3: GitHub 设置

1. 进入仓库 Settings → Pages
2. 在 Custom domain 填入你的域名
3. 勾选 Enforce HTTPS

### 步骤 4: 更新 baseURL

```toml
baseURL = "https://yourdomain.com/"
```

## 📊 本地预览

```bash
cd cygnusyang.github.io

# 启动开发服务器
hugo server

# 指定端口
hugo server --port 1314

# 构建并预览
hugo server --buildDrafts
```

访问 `http://localhost:1313` 查看效果。

## 🚨 常见问题

### Q: 主题不显示？

```bash
# 确保子模块已初始化
git submodule update --init --recursive
```

### Q: 图片不显示？

- 确保图片在 `static/images/` 目录
- 使用相对路径：`![图片](/images/your-image.png)`

### Q: 部署后 404？

- 检查 `hugo.toml` 中的 `baseURL`
- 确保仓库分支是 `main`（不是 `master`）

### Q: 子模块更新问题？

```bash
# 重新初始化子模块
git submodule deinit -f cygnusyang.github.io
git rm -f cygnusyang.github.io
git submodule add git@github.com:你的用户名/你的用户名.github.io.git cygnusyang.github.io
```

## 💡 下一步

- [05. Claude Code 安装与使用](./05-claude-code.md) - 智能开发助手
- [06. 完整工作流](./06-complete-workflow.md) - 端到端演示