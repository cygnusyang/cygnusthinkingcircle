# 内容制作工作流程

## 快速开始

```bash
# 1. 配置 API key
cp .env.example .env
# 编辑 .env，填入 ANTHROPIC_API_KEY

# 2. 创建新文章
python tools/make.py new "我的新文章标题"

# 3. 编辑文章
# 打开 knowledge-base/articles/ 下生成的文件，按要求填写

# 4. 生成博客
python tools/make.py build 2026-05-05-my-article.md

# 5. 审核生成的内容
ls tools/output/

# 6. 发布博客
python tools/make.py publish
```

## 完整工作流程

### 第一步：创建源文章

```bash
python tools/make.py new "OpenClaw Gateway 核心架构深度解析"
```

这会在 `knowledge-base/articles/` 下生成文章文件。打开编辑：
- 填写 frontmatter 元数据（tags、category、keywords、summary）
- 默认只生成博客；外部平台必须通过命令行 `--platform` 显式指定
- 在正文中编写完整的技术长文（2000-5000字）

### 第二步：生成内容

```bash
# 默认只生成博客
python tools/make.py build 2026-05-05-openclaw-gateway.md

# 只生成指定平台
python tools/make.py build --platform xiaohongshu,zhihu 2026-05-05-openclaw-gateway.md

# 批量为所有文章生成博客
python tools/make.py build --all
```

生成的内容：
- `cygnusyang.github.io/content/posts/` - 博客原文，默认生成
- `tools/output/xiaohongshu/` - 小红书版本，仅指定 `--platform xiaohongshu` 时生成
- `tools/output/zhihu/` - 知乎版本，仅指定 `--platform zhihu` 时生成
- `tools/output/wechat/` - 微信公众号版本，仅指定 `--platform wechat` 时生成
- `tools/output/toutiao/` - 今日头条版本，仅指定 `--platform toutiao` 时生成
- `tools/output/baijiahao/` - 百家号版本，仅指定 `--platform baijiahao` 时生成
- `tools/output/douyin/` - 抖音脚本版本，仅指定 `--platform douyin` 时生成

### 第三步：人工审核

检查各平台版本：
- **小红书**：调整标题、标签、emoji
- **知乎**：确认关键词布局、代码正确性
- **微信**：检查转发钩子、CTA引导
- **头条**：确认科普化表达
- **百家号**：优化关键词密度、SEO元素
- **抖音**：调整分镜节奏、字幕

### 第四步：发布

```bash
# 发布博客到 GitHub Pages
python tools/make.py publish
```

各平台内容手动复制发布到对应平台。

## 平台策略速查

| 平台 | 字数 | 核心公式 | 关键指标 |
|------|------|---------|---------|
| 博客 | 2000-5000 | 完整长文 | SEO收录 |
| 小红书 | 800-1200 | 数字标题+步骤拆解 | 点赞收藏 |
| 知乎 | 2000-5000 | 前150字关键词+热点嫁接 | 收藏量 |
| 微信 | 1500-3000 | 痛点场景+转发钩子 | 完读率>50% |
| 头条 | 1500-3000 | SCQA+科普化 | 完读率+评论 |
| 百家号 | 1500-3000 | 标题13字关键词+SCQA | 百度收录 |
| 抖音 | 200-500 | 3秒钩子+分镜 | 完播率 |

## 平台分工

**抖音负责放大，小红书负责说服，知乎负责权威，微信负责赚钱，百家号+头条负责捡漏，博客负责沉淀。**

## AI 内容策略

- LLM 生成 70-80% 的初稿
- 人工做 20-30% 的灵魂注入（鲜活案例、情绪价值、专业判断）
- AI 纯复制粘贴的内容会被各平台识别为低质
- 每篇文章的 LLM prompt 在 `tools/prompts/` 中，可根据效果持续调优

## 查看状态

```bash
python tools/make.py status
python tools/make.py config
```
