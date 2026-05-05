# 技术影响力系统

跨平台内容分发平台 —— 写一次，分发到 7 个平台。

**knowledge-base 源文章 → LLM 适配 → 博客 + 小红书/知乎/微信/头条/百家号/抖音**

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

# 5. 生成所有平台
python tools/make.py build --all

# 6. 审核 + 发布博客
python tools/make.py publish
```

## 命令一览

| 命令 | 作用 |
|------|------|
| `make.py new "标题"` | 从模板创建新文章 |
| `make.py build article.md` | 生成博客 + 所有平台 |
| `make.py build --all` | 生成所有文章 |
| `make.py build --platform xh,zhihu article.md` | 只生成指定平台 |
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
