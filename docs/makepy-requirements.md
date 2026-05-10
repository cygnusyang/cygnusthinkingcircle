# make.py CLI 需求文档

> **文件：** `tools/make.py`
> **角色：** 统一内容制作入口（Unified Content CLI）
> **当前版本：** 6 个子命令，依赖 4 个 lib 模块
> **创建日期：** 2026-05-10

---

## 需求总览

| 编号 | 需求标题 | 优先级 | 工作量 | 状态 |
|------|---------|--------|--------|------|
| REQ-M01 | `new` 子命令 — 创建新文章 | P0 | - | 已完成 |
| REQ-M02 | `build` 子命令 — 构建文章（博客 + 多平台） | P0 | - | 已完成 |
| REQ-M03 | `publish` 子命令 — 发布到 GitHub Pages | P0 | - | 已完成 |
| REQ-M04 | `status` 子命令 — 查看文章状态 | P0 | - | 已完成 |
| REQ-M05 | `config` 子命令 — 查看/管理配置 | P0 | - | 已完成 |
| REQ-M06 | `collection list` 子命令 — 列出项目集合 | P0 | - | 已完成 |
| REQ-M07 | `collection build` 子命令 — 构建集合并转换为 Hugo | P0 | - | 已完成 |
| REQ-M08 | `collection add-card` 子命令 — 添加首页卡片 | P0 | - | 已废弃 |
| REQ-M09 | Shell 补全支持（argcomplete） | P2 | - | 已完成 |
| REQ-M10 | `new` 支持 `--category` 指定目录 | P1 | - | 已完成 |
| REQ-M11 | `build` 支持增量构建 | P1 | - | 已完成 |
| REQ-M12 | `collection build` 支持 dry-run 模式 | P2 | - | 已完成 |
| REQ-M13 | `validate` 子命令 — 校验内容完整性 | P1 | - | 已完成 |
| REQ-M14 | `new` 支持从模板集合创建文章 | P1 | - | 已完成 |
| REQ-M15 | `publish` 支持子模块自动更新 | P1 | - | 已完成 |
| REQ-M16 | `stats` 子命令 — 内容统计报表 | P2 | - | 已完成 |

---

## 架构概览

```
tools/
├── make.py                    # CLI 入口（6 个子命令）
├── lib/
│   ├── article.py             # 文章解析、frontmatter、模型
│   ├── collection.py          # 集合发现、转换、首页卡片管理
│   ├── platforms.py           # 7 平台配置和策略
│   ├── publisher.py           # 发布到 GitHub Pages
│   └── llm.py                 # Anthropic/第三方 API 适配
├── prompts/                   # LLM 平台策略 prompt 模板
│   ├── blog.md                # 博客（直接发布，不需 LLM）
│   ├── xiaohongshu.md         # 小红书
│   ├── zhihu.md               # 知乎
│   ├── wechat.md              # 微信公众号
│   ├── toutiao.md             # 今日头条
│   ├── baijiahao.md           # 百家号
│   └── douyin.md              # 抖音
└── output/                    # 平台内容生成输出目录
```

### 核心数据流

```
knowledge-base/articles/
  ├── 01-openclaw/              # 集合项目（NN- 前缀目录）
  │   ├── blog/                 # 源文章
  │   │   └── 01-intro/
  │   │       └── 01-xxx.md
  │   └── README.md
  └── template.md               # 文章模板

       │ collection.build
       ▼

cygnusyang.github.io/content/posts/
  ├── openclaw/                 # Hugo 集合目录
  │   ├── _index.md             # 集合元数据
  │   └── 2026-05-09-第01章-xxx.md
  └── ...

       │ publish
       ▼

GitHub Pages (cygnusyang.github.io 子模块)
  → https://cygnusyang.github.io/
```

---

## REQ-M01：`new` 子命令 — 创建新文章

### 当前实现

```bash
python tools/make.py new "文章标题"
```

**行为：**
1. 以当前日期生成文件名 `YYYY-MM-DD-slug.md`
2. 从 `knowledge-base/articles/template.md` 复制模板
3. 替换模板中的 `title` 和 `date` 字段
4. 输出到 `knowledge-base/articles/` 根目录

**涉及文件：**
- `tools/make.py:cmd_new()` (第 85-115 行)
- `knowledge-base/articles/template.md`

**当前限制：**
- 文章只能创建到根目录，无法指定分类/集合
- slug 生成是简单的 `.lower().replace(" ", "-")`，不支持中文标题
- 无 frontmatter 校验

### 验收标准（当前）

1. 创建的文件包含正确的 YAML frontmatter
2. 日期自动填充为当天
3. 重复文件名检测并报错
4. 提示用户下一步操作

---

## REQ-M02：`build` 子命令 — 构建文章

### 当前实现

```bash
python tools/make.py build article.md                    # 只生成博客
python tools/make.py build --all                         # 生成所有文章博客
python tools/make.py build --platform xiaohongshu,zhihu article.md  # 指定平台
```

**行为：**
1. 加载 `.env` 环境变量（LLM API Key 等）
2. 解析文章 frontmatter（`load_article()`）
3. 博客平台：直接生成 Hugo frontmatter 并输出到 `cygnusyang.github.io/content/posts/`
4. 非博客平台：调用 LLM 根据 prompt 模板适配内容，输出到 `tools/output/{platform}/`
5. 检查 LLM API Key 是否存在，缺失时跳过非博客平台

**涉及文件：**
- `tools/make.py:cmd_build()` (第 118-216 行)
- `tools/lib/article.py` — 文章解析
- `tools/lib/platforms.py` — 平台配置（7 个平台定义）
- `tools/lib/publisher.py:publish_to_blog()` — 博客发布
- `tools/lib/publisher.py:save_platform_output()` — 平台内容保存
- `tools/lib/llm.py:adapt_for_platform()` — LLM 内容适配
- `tools/prompts/*.md` — 各平台 prompt 模板

**平台列表：**

| 平台 Key | 名称 | 需要 LLM | 输出目录 |
|----------|------|----------|---------|
| `blog` | 博客 | 否 | `cygnusyang.github.io/content/posts/` |
| `xiaohongshu` | 小红书 | 是 | `tools/output/xiaohongshu/` |
| `zhihu` | 知乎 | 是 | `tools/output/zhihu/` |
| `wechat` | 微信公众号 | 是 | `tools/output/wechat/` |
| `toutiao` | 今日头条 | 是 | `tools/output/toutiao/` |
| `baijiahao` | 百家号 | 是 | `tools/output/baijiahao/` |
| `douyin` | 抖音 | 是 | `tools/output/douyin/` |

### 验收标准（当前）

1. 博客版本正确生成 Hugo 格式
2. 指定平台时生成对应平台内容
3. `--all` 处理所有文章
4. LLM Key 缺失时给出清晰警告
5. 统计并输出处理结果

---

## REQ-M03：`publish` 子命令 — 发布到 GitHub Pages

### 当前实现

```bash
python tools/make.py publish                          # 自动消息
python tools/make.py publish -m "自定义消息"           # 自定义消息
```

**行为：**
1. 检查 `cygnusyang.github.io/` 目录是否存在
2. `git add content/posts/`
3. 检查是否有变更（`git diff --cached --quiet`）
4. 无变更时跳过提交
5. 有变更时自动生成 commit 消息并推送
   - 集合目录变更：`post: update {dirs} collection ({n} articles)`
6. 推送到远程仓库

**涉及文件：**
- `tools/make.py:cmd_publish()` (第 219-290 行)

**当前限制：**
- 只操作 `cygnusyang.github.io` 子模块，不更新父仓库的子模块引用
- 无 Hugo 构建步骤（假设已手动构建）
- 无发布后验证

### 验收标准（当前）

1. 无变更时不创建空提交
2. commit 消息准确反映变更内容
3. 推送成功提示访问 URL
4. Git 操作失败时清晰报错

---

## REQ-M04：`status` 子命令 — 查看文章状态

### 当前实现

```bash
python tools/make.py status
```

**行为：**
1. 列出 `knowledge-base/articles/` 下所有文章
2. 显示每篇文章的标题、日期、发布状态（已发布/未发布）
3. 检查各平台 output 目录的文章数量
4. 检查博客目录的文章数量

**涉及文件：**
- `tools/make.py:cmd_status()` (第 293-333 行)
- `tools/lib/article.py:find_articles()`
- `tools/lib/platforms.py:list_platforms()`

### 验收标准（当前）

1. 显示所有源文章及其状态
2. 显示各平台输出文章数
3. 显示博客文章数

---

## REQ-M05：`config` 子命令 — 查看配置

### 当前实现

```bash
python tools/make.py config
```

**行为：**
1. 显示 LLM 配置（provider、API Key 脱敏、model、base URL）
2. 显示目录路径（知识库、博客输出、平台输出、prompts）
3. 列出所有可用平台及其描述

**涉及文件：**
- `tools/make.py:cmd_config()` (第 414-449 行)
- `tools/lib/llm.py` — provider/api_key/model/base_url 函数
- `tools/lib/platforms.py` — PLATFORMS 常量

### 验收标准（当前）

1. API Key 脱敏显示（显示前 8 位 + ... + 后 4 位）
2. 列出所有平台及其描述
3. 显示所有目录路径

---

## REQ-M06：`collection list` 子命令 — 列出项目集合

### 当前实现

```bash
python tools/make.py collection list
```

**行为：**
1. 扫描 `knowledge-base/articles/` 下所有 `NN-` 前缀的目录
2. 识别规则：目录名以数字-开头，且包含 `blog/` 子目录或可发布的 `.md` 文章
3. 按深度从浅到深处理，已识别项目的子目录自动排除
4. 显示项目名、文章数、是否已推送到 GitHub Pages

**涉及文件：**
- `tools/make.py:cmd_collection()` — list 分支 (第 337-354 行)
- `tools/lib/collection.py:list_projects()` (第 342-407 行)
- `tools/lib/collection.py:_discover_projects()` (第 28-79 行)

**项目发现逻辑：**
```
knowledge-base/articles/
  ├── 01-openclaw/          ✓ (有 blog/ 子目录)
  ├── 02-gstack/            ✓ (有 blog/ 子目录)
  ├── 03-gbrain/            ✓ (有 .md 文章)
  ├── 04-工程那些事/         ✓ (父级目录)
  │   └── 01-电机控制/       ✓ (有 .md 文章)
  └── README.md             ✗ (不是 NN- 目录)
```

### 验收标准（当前）

1. 正确识别所有 NN- 前缀的项目目录
2. 嵌套项目正确显示完整路径（如 `04-工程那些事/01-电机控制`）
3. 显示文章数和推送状态
4. 按编号排序

---

## REQ-M07：`collection build` 子命令 — 构建集合

### 当前实现

```bash
python tools/make.py collection build 01-openclaw            # 构建单个集合
python tools/make.py collection build 04-工程那些事/01-电机控制  # 构建嵌套集合
python tools/make.py collection build --all                  # 构建所有集合
python tools/make.py collection build --source blog --date 2026-05-09 myproject
```

**行为：**
1. 解析用户输入（支持 NN 前缀、裸 slug、部分匹配）
2. 调用 `build_collection()` 将集合转换为 Hugo 格式
3. 构建过程：
   - 清理该集合的旧文件（避免重复）
   - 扫描源目录下所有 `.md` 文件
   - 对每篇文章：解析/提取标题、处理本地图片、生成 frontmatter
   - 全局连续编号（`第01章`, `第02章`, ...）
   - 生成 `_index.md`（集合元数据）
4. 更新首页卡片（替换"敬请期待"为实际文章数）
5. 同步 `pinned_categories` frontmatter
6. 重新排序首页卡片

**涉及文件：**
- `tools/make.py:cmd_collection()` — build 分支 (第 356-396 行)
- `tools/lib/collection.py:build_collection()` (第 179-320 行)
- `tools/lib/collection.py:resolve_project_by_input()` (第 410-460 行)
- `tools/lib/collection.py:_update_index_cards()` (第 498-557 行)
- `tools/lib/collection.py:_sync_pinned_categories()` (第 721-748 行)
- `tools/lib/collection.py:_resort_cards()` (第 688-713 行)
- `tools/lib/publisher.py:process_local_images()` — 图片处理

**生成文件命名规则：**
```
输入: 01-intro/01-xxx.md
输出: 2026-05-09-第01章-xxx.md
      (日期)-(章节号)-(安全标题).md
```

### 验收标准（当前）

1. 正确解析用户输入的项目名（多种格式）
2. 构建前清理旧文件
3. 文章全局连续编号
4. 生成正确的 `_index.md`
5. 首页卡片自动更新
6. 统计并输出构建结果

---

## REQ-M08：`collection add-card` 子命令 — 添加首页卡片

### 当前实现

```bash
python tools/make.py collection add-card myproject
python tools/make.py collection add-card myproject --icon ⚙️ --desc "自定义描述"
```

**行为：**
1. 检查首页 `_index.md` 中是否已存在该卡片
2. 生成"敬请期待"风格的卡片 HTML
3. 根据项目 NN 编号推导显示名（如 `01-OpenClaw`）
4. 自动推导图标（如果未指定）
5. 插入卡片并重新排序
6. 同步 `pinned_categories` frontmatter

**涉及文件：**
- `tools/make.py:cmd_collection()` — add-card 分支 (第 398-411 行)
- `tools/lib/collection.py:add_project_card()` (第 751-830 行)
- `tools/lib/collection.py:_CARD_ARIA_LABELS` (第 465-476 行) — 项目名映射
- `tools/lib/collection.py:_CARD_ICONS` (第 484-495 行) — 图标映射

### 验收标准（当前）

1. 重复卡片检测并跳过
2. 新卡片正确插入到排序位置
3. `pinned_categories` 自动更新
4. 默认图标和描述合理

---

## REQ-M09：Shell 补全支持

### 当前实现

使用 `argcomplete` 库实现动态补全。

**补全范围：**
- `collection build` / `add-card` 的项目名
- `build --platform` 的平台名
- `build` 的文章文件名

**涉及文件：**
- `tools/make.py:main()` 补全部分 (第 520-548 行)
- 依赖：`pip install argcomplete`

### 验收标准

1. Tab 补全项目名
2. Tab 补全平台名
3. Tab 补全文章文件名
4. argcomplete 未安装时优雅降级

---

## REQ-M10：`new` 支持 `--category` 指定目录

### 问题描述

当前 `new` 命令只能创建到 `knowledge-base/articles/` 根目录，无法指定集合或分类。

### 需求详情

```bash
python tools/make.py new "FOC 控制原理" --category 04-工程那些事/01-电机控制
python tools/make.py new "新文章" --category openclaw
```

| 参数 | 说明 |
|------|------|
| `--category` | 目标集合目录（支持 NN 前缀或裸 slug） |
| 默认行为 | 保持创建到根目录 |

**行为：**
1. 如果指定 `--category`，解析为目标集合目录
2. 在集合的 `blog/` 子目录下创建文件
3. 如果 `blog/` 不存在则创建
4. 自动检测下一个可用的章节号

### 涉及文件

- `tools/make.py:cmd_new()`
- `tools/lib/collection.py:resolve_project_by_input()`（复用现有的解析逻辑）

### 验收标准

1. 指定分类时创建到正确的集合目录
2. 未指定时保持现有行为（根目录）
3. 不存在的集合给出清晰错误提示

---

## REQ-M11：`build` 支持增量构建

### 问题描述

当前 `build --all` 每次都会重新处理所有文章，即使只有少量变更。

### 需求详情

```bash
python tools/make.py build --all --incremental    # 只处理变更的文章
python tools/make.py build article.md --force     # 强制重新构建单篇
```

**检测变更的方式：**
1. 比较源文件的 mtime（修改时间）
2. 或比较已生成输出的 hash
3. 维护一个 `.build-state.json` 缓存文件

**状态文件格式：**
```json
{
  "2026-05-05-my-article.md": {
    "mtime": 1715000000,
    "platforms": {
      "blog": { "built_at": 1715000100, "hash": "abc123" },
      "zhihu": { "built_at": 1715000200, "hash": "def456" }
    }
  }
}
```

### 涉及文件

- `tools/make.py:cmd_build()`
- 新建 `tools/lib/build_state.py`（构建状态管理）

### 验收标准

1. `--incremental` 只处理变更的源文件
2. 状态文件自动更新
3. `--force` 覆盖增量检查
4. 无 `.build-state.json` 时首次全量构建

---

## REQ-M12：`collection build` 支持 dry-run 模式

### 问题描述

构建集合是一个破坏性操作（会清理旧文件），用户希望先预览结果。

### 需求详情

```bash
python tools/make.py collection build 01-openclaw --dry-run
```

**行为：**
1. 扫描并列出将被处理的文件
2. 显示目标路径映射
3. 不实际写入任何文件
4. 显示预期文章数量

### 涉及文件

- `tools/make.py:cmd_collection()` — build 分支
- `tools/lib/collection.py:build_collection()`

### 验收标准

1. dry-run 不修改任何文件
2. 列出所有将被处理的源文件
3. 显示目标文件名
4. 汇总统计

---

## REQ-M13：`validate` 子命令 — 校验内容完整性

### 问题描述

内容在构建前无法验证 frontmatter 完整性、链接有效性等问题，只能在构建后发现。

### 需求详情

```bash
python tools/make.py validate                     # 校验所有内容
python tools/make.py validate --article xxx.md    # 校验单篇
```

**校验项：**

| 校验项 | 严重级别 | 说明 |
|--------|---------|------|
| frontmatter 必填字段 | 错误 | title、date 缺失 |
| weight 连续性 | 警告 | 集合内 weight 不连续 |
| 重复标题 | 警告 | 同集合内有重复标题 |
| 损坏的内部链接 | 错误 | 链接指向不存在的文件 |
| 图片引用失效 | 错误 | Markdown 图片路径不存在 |
| 文件大小异常 | 警告 | 单文件 > 50KB |
| 重复 weight | 错误 | 同一集合内两篇文章相同 weight |
| 空正文 | 警告 | frontmatter 后无内容 |

### 涉及文件

- `tools/make.py:cmd_validate()`（新建）
- `tools/lib/validator.py`（新建）
- `tools/lib/article.py`（复用 load_article）
- `tools/lib/collection.py`（复用项目发现逻辑）

### 验收标准

1. 校验通过时显示成功消息
2. 发现问题时按严重级别分类显示
3. 校验不影响任何文件
4. 支持单篇文章校验

---

## REQ-M14：`new` 支持从模板集合创建文章

### 问题描述

集合项目的文章模板和普通文章模板可能不同（集合文章有章节号、category 等额外字段）。

### 需求详情

```bash
python tools/make.py new "新章节" --category openclaw --template chapter
```

**模板优先级：**
1. 集合目录下的 `blog/template.md`（如果存在）
2. `knowledge-base/articles/template.md`（通用模板）

### 涉及文件

- `tools/make.py:cmd_new()`
- 各集合目录下的 `blog/template.md`（需用户自行创建）

### 验收标准

1. 优先使用集合专属模板
2. 回退到通用模板
3. 自动填充集合相关的 frontmatter 字段

---

## REQ-M15：`publish` 支持子模块自动更新

### 问题描述

当前 `publish` 只操作 `cygnusyang.github.io` 子模块，不更新父仓库的子模块引用。发布后需要手动在父仓库 `git add cygnusyang.github.io && git commit && git push`。

### 需求详情

```bash
python tools/make.py publish --update-submodule    # 发布并更新父仓库引用
```

**行为：**
1. 完成现有的 git add/commit/push 流程
2. 回到父仓库目录
3. `git add cygnusyang.github.io`
4. `git commit -m "chore: 更新子模块引用"`
5. `git push`

### 涉及文件

- `tools/make.py:cmd_publish()`

### 验收标准

1. 默认行为不变（只推送子模块）
2. `--update-submodule` 时同步更新父仓库
3. 父仓库操作失败不阻塞子模块推送

---

## REQ-M16：`stats` 子命令 — 内容统计报表

### 问题描述

用户需要了解内容增长趋势、各集合规模、平台覆盖率等统计数据，当前的 `status` 命令只提供基础状态。

### 需求详情

```bash
python tools/make.py stats                     # 完整统计报表
python tools/make.py stats --json              # JSON 格式输出
python tools/make.py stats --collection openclaw  # 单个集合统计
```

**统计维度：**

| 维度 | 指标 |
|------|------|
| 总量 | 文章总数、集合数、已发布平台数 |
| 按集合 | 每个集合的文章数、最新更新日期 |
| 按时间 | 月度新增趋势（最近 6 个月） |
| 按平台 | 各平台已发布文章数 |
| 字数 | 总字数、平均篇字数 |
| 图片 | 引用图片总数 |

### 涉及文件

- `tools/make.py:cmd_stats()`（新建）
- `tools/lib/stats.py`（新建）

### 验收标准

1. 显示所有统计维度
2. `--json` 输出机器可读格式
3. 支持过滤单个集合
4. 统计不影响任何文件

---

## 依赖关系图

```
REQ-M10 (new --category)  →  依赖 REQ-M01 (new)
REQ-M11 (增量构建)        →  依赖 REQ-M02 (build)
REQ-M12 (dry-run)         →  依赖 REQ-M07 (collection build)
REQ-M13 (validate)        →  独立，但被 REQ-M11 引用
REQ-M14 (集合模板)        →  依赖 REQ-M10
REQ-M15 (子模块更新)      →  依赖 REQ-M03 (publish)
REQ-M16 (stats)           →  扩展 REQ-M04 (status)
```

---

## 实施路线图

### Phase 1：立即（提升日常使用效率）

| 需求 | 说明 |
|------|------|
| REQ-M10 | `new --category` — 创建文章到指定集合 |
| REQ-M13 | `validate` — 构建前校验 |
| REQ-M15 | `publish --update-submodule` — 一键发布 |

### Phase 2：短期（提升可靠性）

| 需求 | 说明 |
|------|------|
| REQ-M11 | 增量构建 — 节省 LLM 调用成本 |
| REQ-M14 | 集合模板 — 支持不同集合的差异化模板 |

### Phase 3：中期（体验优化）

| 需求 | 说明 |
|------|------|
| REQ-M12 | dry-run — 安全预览 |
| REQ-M16 | stats — 数据驱动决策 |
