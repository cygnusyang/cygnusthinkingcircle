# 技术影响力系统

跨平台内容分发平台 —— 写一次，默认生成博客，显式指定时再适配外部平台。

**knowledge-base 源文章 → 博客；按需 LLM 适配 → 小红书/知乎/微信/头条/百家号/抖音**

## 快速开始

```bash
# 1. 创建虚拟环境并安装依赖
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. 配置 API key
cp .env.example .env
# 编辑 .env，填入 LLM_API_KEY

# 3. 创建第一篇文章
python tools/make.py new "你的文章标题"

# 4. 编辑文章
# → knowledge-base/articles/ 下找到刚生成的文件，写内容

# 5. 生成博客
python tools/make.py build --all

# 6. 审核 + 发布博客
python tools/make.py publish
```

## 命令一览

| 命令 | 作用 |
|------|------|
| `make.py new "标题"` | 从模板创建新文章 |
| `make.py build article.md` | 只生成博客 |
| `make.py build --all` | 为所有文章生成博客 |
| `make.py build --platform xh,zhihu article.md` | 只生成指定平台 |
| `make.py collection list` | 列出所有可用项目集合 |
| `make.py collection build <项目>` | 批量转换项目为 Hugo Pages |
| `make.py collection build --all` | 构建所有项目集合 |
| `make.py collection add-card <项目>` | 添加首页"敬请期待"卡片 |
| `make.py publish` | 推送博客到 GitHub Pages |
| `make.py status` | 查看文章和输出状态 |
| `make.py config` | 查看当前配置 |

## 目录结构

```
├── knowledge-base/articles/   ← 唯一真相源，在这里写文章
├── cygnusyang.github.io/      ← Hugo GitHub Pages
├── tools/
│   ├── make.py                ← 统一入口
│   ├── lib/                   ← 核心库
│   ├── prompts/               ← 7个平台的 LLM 策略
│   ├── output/                ← 生成的平台内容
│   └── requirements.txt
└── .env                       ← LLM 配置 (gitignore)
```

## 平台策略

| 平台 | 定位 | 字数 |
|------|------|------|
| 博客 | SEO长尾，完整长文 | 2000-5000 |
| 小红书 | 种草+实操 | 800-1200 |
| 知乎 | 深度专业+SEO | 2000-5000 |
| 微信公众号 | 私域+搜一搜 | 1500-3000 |
| 今日头条 | 深度内容 | 1500-3000 |
| 百家号 | 百度SEO | 1500-3000 |
| 抖音 | 短视频脚本 | 200-500 |

## 原理

```
knowledge-base/article.md          ← 你写的源文章
        │
        ├──→ [直发] → 博客
        │
        └──→ [LLM 改写] ─┬── 小红书 prompt → 种草风格
                          ├── 知乎 prompt   → 深度分析风
                          ├── 微信 prompt   → 社交传播风
                          ├── 头条 prompt   → 科普化表达
                          ├── 百家号 prompt → SEO优化风
                          └── 抖音 prompt   → 分镜脚本风
```

每个平台的改写策略在 `tools/prompts/` 中独立管理，修改策略不需要改代码。

## 项目集合工具

将 `knowledge-base/articles/` 下的项目目录批量转换为 Hugo GitHub Pages。

```bash
# 列出所有可用的项目集合
python tools/make.py collection list

# 构建单个项目
python tools/make.py collection build openclaw
python tools/make.py collection build gstack

# 构建所有项目
python tools/make.py collection build --all

# 指定源子目录（非 blog/ 的情况）
python tools/make.py collection build gstack --source blog/chapters

# 指定发布日期
python tools/make.py collection build gbrain --date 2026-05-01
```

**工作流程：**
```
knowledge-base/articles/02-gstack/blog/chapters/*.md
        │
        ├── 解析 frontmatter（或提取 # 标题）
        ├── 生成 Hugo frontmatter（collections, weight, tags）
        ├── 自动编号（从文件名 01-xxx.md 提取）
        │
        ▼
cygnusyang.github.io/content/posts/gstack/
        ├── _index.md
        ├── 2026-04-18-第01章-xxx.md
        └── ...
```

项目目录按 `NN-projectname/` 命名约定自动发现，无需手动配置映射表。

## 访问统计

网站已配置 **百度统计** + Google Analytics 4 双重统计。

### 本地验证百度统计

```bash
cd cygnusyang.github.io
hugo server
# 访问 http://localhost:1313
# 打开浏览器开发者工具 → Network 面板
# 查找 hm.baidu.com/hm.gif 请求，确认状态码 200
```

### 线上验证

1. 访问 [百度统计后台](https://tongji.baidu.com/) → 实时访客
2. 打开你的网站 `https://cygnusyang.github.io/`
3. 刷新百度统计页面，应能看到实时访问记录

### 配置

```toml
# cygnusyang.github.io/hugo.toml
[params.analytics]
  enable = true
  [params.analytics.baidu]
    id = "ca9a2cee6f2d47d57d75201cf14c2e15"  # 百度统计 ID
  [params.analytics.google]
    id = ""  # Google Analytics 4 ID（可选）
```

> **注意：** 百度统计在国内网络环境下稳定，Google Analytics 4 在国内可能加载较慢或失败。建议优先使用百度统计查看国内用户数据。
