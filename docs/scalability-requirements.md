# 技术影响力网站 — 规模化改进需求文档

> **站点：** cygnusyang.github.io
> **Hugo 版本：** v0.161.1 extended
> **主题：** FixIt
> **当前规模：** 179 篇文章，13 个分类目录，public 目录 67MB，search.json 4.3MB
> **目标规模：** 500-1000+ 篇文章
> **创建日期：** 2026-05-10

---

## 需求总览

| 编号 | 需求标题 | 优先级 | 工作量 | 状态 |
|------|---------|--------|--------|------|
| REQ-001 | 首页分类卡片动态化 | P0 | 中 | ✅ 已完成 |
| REQ-002 | 搜索索引优化（search.json 瘦身） | P0 | 小 | ✅ 已完成 |
| REQ-003 | `/posts/` 列表页分页或两级浏览 | P0 | 小 | 待开发 |
| REQ-004 | 文章文件命名与 URL 规范化 | P1 | 中 | 待开发 |
| REQ-005 | 启用 Hugo 分类法（tags/categories） | P1 | 中 | 待开发 |
| REQ-006 | 侧边栏导航按需渲染 | P1 | 中 | 待开发 |
| REQ-007 | 内容创建管道自动化 | P1 | 中 | 待开发 |
| REQ-008 | 启用输出压缩（minify） | P2 | 小 | 待开发 |
| REQ-009 | 统一目录命名语言（URL 美化） | P2 | 中 | 待开发 |
| REQ-010 | 相关文章推荐优化 | P2 | 小 | 待开发 |
| REQ-011 | 图片处理与资源管道 | P2 | 中 | 待开发 |
| REQ-012 | CI/CD 自动化构建与校验 | P2 | 中 | 待开发 |

---

## REQ-001：首页分类卡片动态化

### 问题描述

`content/_index.md` 中所有分类卡片均为硬编码 HTML，包括：
- 图标（emoji）、标题、描述文案
- 文章篇数（badge）
- 链接地址
- `pinned_categories` 列表

每次新增或修改分类都需要手动编辑 `_index.md`，且篇数会随文章增减而过时。

### 目标

将首页卡片改为 Hugo 模板动态生成，从 `/posts` 下的子目录自动读取分类信息。

### 需求详情

| 字段 | 要求 |
|------|------|
| **分类图标** | 从各分类 `_index.md` 的 `icon` frontmatter 读取 |
| **分类标题** | 从 `_index.md` 的 `title` frontmatter 读取，去除数字前缀 |
| **文章篇数** | 动态计算 `len .PagesRecursive` |
| **描述文案** | 从 `_index.md` 的 `description` frontmatter 读取 |
| **链接地址** | 自动使用 `.RelPermalink` |
| **排序** | 按 `weight` 或标题数字前缀排序 |
| **新增分类** | 在 posts 下新建目录即可自动出现在首页 |

### 涉及文件

- `cygnusyang.github.io/content/_index.md`（删除硬编码 HTML）
- `cygnusyang.github.io/layouts/index.html`（新建或修改首页模板）
- 各分类目录的 `_index.md`（补充 `description` frontmatter）

### 验收标准

1. 新增一个分类目录后，首页自动出现对应卡片
2. 文章增删后，卡片篇数自动更新（重新构建即可）
3. 首页卡片排序正确
4. 保留现有的展开/收起交互和响应式布局

### 风险与注意事项

- 当前首页还包含 GitHub 工程卡片、关于、捐赠等区块，这些仍保留硬编码，仅替换分类卡片部分
- `category-popup.html` shortcode 可能需要扩展或合并到首页模板中

---

## REQ-002：搜索索引优化（search.json 瘦身）

### 问题描述

当前 `search.json` 已达 **4.3MB**（179 篇文章）。Fuse.js 是客户端全文搜索，需要将整个 JSON 下载到浏览器后才能建立索引。

按当前增长率，500 篇时预计 12-15MB，1000 篇时预计 25-30MB，移动端基本不可用。

### 目标

将搜索索引体积控制在合理范围内（500 篇时 < 5MB）。

### 方案选择

#### 方案 A：优化现有 Fuse.js 搜索（短期）

在 `hugo.toml` 中调整搜索参数：

```toml
[params.search]
  contentLength = 1000        # 从默认 4000 降到 1000
```

**优点：** 改动最小，一行配置
**缺点：** 超过 500 篇仍会过大；搜索精度下降

#### 方案 B：切换到 Algolia（中期，500+ 篇时）

使用 Algolia 服务端搜索，Hugo 构建时生成 Algolia 格式的 JSON 并上传。

**优点：** 搜索质量好，支持 faceted search，无客户端体积负担
**缺点：** 需要外部服务，有免费额度限制（10,000 次查询/月）

#### 方案 C：Pagefind 静态搜索（中期，推荐）

Pagefind 是专为静态站点设计的搜索引擎，将索引分片加载，首屏仅加载元数据。

**优点：** 纯静态、无外部服务、支持分片加载、搜索质量好
**缺点：** 需要集成 Hugo 模块或外部构建步骤

### 需求详情（当前先执行方案 A）

| 配置项 | 当前值 | 建议值 | 说明 |
|--------|--------|--------|------|
| `contentLength` | 4000（默认） | 1000 | 每段索引内容最大字符数 |
| `anchorify` | true | false | 关闭分段索引，每篇文章只有一条索引 |
| `summaryLength` | - | 200 | 搜索结果摘要长度 |

### 涉及文件

- `cygnusyang.github.io/hugo.toml`
- 主题搜索索引模板（如需自定义）

### 验收标准

1. 构建后 `search.json` 体积减少至少 50%
2. 搜索功能仍能正常检索标题和关键词
3. 搜索页面 UI 无异常

---

## REQ-003：`/posts/` 列表页分页或两级浏览

### 问题描述

`layouts/posts/section.html` 将所有分类和所有文章一次性渲染到页面。179 篇文章已全部展开在 DOM 中。1000 篇时页面 DOM 节点将超过 3000 个，影响渲染性能和移动端体验。

### 目标

优化列表页的渲染策略，控制单次加载的文章数量。

### 方案

**两级浏览模式（推荐）：**
1. 默认只显示分类列表（当前已用 `<details>` 折叠，但所有文章仍在 DOM 中）
2. 展开某个分类时，通过 Hugo 的 `{{ with }}` 条件渲染或客户端 JavaScript 懒加载该分类下的文章
3. 每个分类最多显示 20 篇，超出部分用"查看更多"链接到分类页

### 需求详情

| 行为 | 要求 |
|------|------|
| **默认状态** | 所有分类折叠，不渲染子文章列表的 DOM |
| **展开分类** | 渲染该分类下最多 20 篇文章 |
| **超出 20 篇** | 显示"查看全部 N 篇"链接，跳转到分类列表页 |
| **展开/折叠** | 保留现有的"全部展开"/"全部折叠"按钮 |
| **排序** | 保持按 `weight` 排序 |

### 涉及文件

- `cygnusyang.github.io/layouts/posts/section.html`
- 可能需要客户端 JavaScript 懒加载配合

### 验收标准

1. 页面初始 DOM 节点数 < 100（仅分类标题）
2. 展开分类后文章列表正确显示
3. 排序正确
4. "全部展开"功能仍然可用

---

## REQ-004：文章文件命名与 URL 规范化

### 问题描述

当前文章文件名格式：
```
2026-05-09-第01章-第一章OpenClaw-是什么.md
```

问题：
1. 文件名嵌入日期 + 章节号 + 标题，插入新文章需重命名后续所有文件
2. URL 中带有日期和编号前缀，不美观且难以记忆
3. 中文文件名 URL encode 后非常长

### 目标

将排序逻辑从文件名迁移到 frontmatter 的 `weight` 字段，使用干净的英文 slug 作为文件名。

### 迁移方案

| 当前格式 | 目标格式 |
|---------|---------|
| `2026-05-09-第01章-xxx.md` | `what-is-openclaw.md` |
| 文件名中的顺序 | `weight: 1` frontmatter |
| URL: `/posts/openclaw/2026-05-09-第01章-xxx/` | URL: `/posts/openclaw/what-is-openclaw/` |

### 需求详情

| 步骤 | 操作 |
|------|------|
| 1 | 为每篇文章提取章节号作为 `weight` 值 |
| 2 | 将文件名改为英文 slug（基于标题拼音或意译） |
| 3 | 在 `_index.md` 中配置 `paginate = 20`（可选） |
| 4 | 生成 301 重定向映射（旧 URL -> 新 URL） |
| 5 | 检查并更新所有内部链接和交叉引用 |

### 涉及文件

- 所有 `content/posts/**/*.md` 文章文件
- `cygnusyang.github.io/hugo.toml`（URL 配置）
- 可能需要迁移脚本（Python）

### 验收标准

1. 所有文章 URL 为干净的英文路径
2. 旧 URL 通过 redirect 正确跳转到新 URL
3. 排序与迁移前一致
4. 所有内部链接正常

### 风险

- 这是一个破坏性变更，影响所有已有 URL 的书签和外部链接
- 需要完整的 301 重定向配置
- 建议在低峰期执行，并保留旧文件名备份

---

## REQ-005：启用 Hugo 分类法（tags/categories）

### 问题描述

当前所有文章的 `tags: []` 为空，`categories` 仅用于冗余的 collection 标识。无法做跨系列的内容检索（如"所有关于 Agent 的文章"跨越 OpenClaw、Harness、GBrain 三个系列）。

### 目标

建立两级分类体系：
- **分类（categories）：** 对应现有目录结构（系列/专栏）
- **标签（tags）：** 跨系列的主题标签（如 `AI Agent`、`LLM`、`部署`、`安全`）

### 需求详情

| 分类法 | 用途 | 示例 |
|--------|------|------|
| `categories` | 系列归属 | `OpenClaw`, `Claude Code`, `电机控制` |
| `tags` | 主题标签 | `AI Agent`, `LLM`, `部署`, `安全`, `架构` |
| `series` | 章节系列（可选） | `OpenClaw 从入门到精通` |

### 标签词表（初步）

```
AI Agent / LLM / 部署 / 安全 / 架构 / 教程 / 实战 /
插件 / 技能 / 钩子 / MCP / 多智能体 / 自动化 /
代码质量 / 测试 / CI-CD / 前端 / 后端 /
电机控制 / FOC / SVPWM / 嵌入式
```

### 涉及文件

- `cygnusyang.github.io/hugo.toml`（启用 taxonomy 配置）
- `cygnusyang.github.io/content/posts/**/*`（所有文章补充 tags）
- `cygnusyang.github.io/layouts/_default/terms.html`（标签列表页，使用主题默认）
- `cygnusyang.github.io/layouts/_default/taxonomy.html`（标签详情页）
- 可能需要批量标签推荐脚本

### 验收标准

1. `/tags/` 页面列出所有标签及文章数
2. `/tags/ai-agent/` 等标签页列出相关文章
3. 文章页显示标签列表，可点击跳转
4. 相关文章推荐基于标签匹配度

---

## REQ-006：侧边栏导航按需渲染

### 问题描述

FixIt 主题的 `aside-collection` 侧边栏在每个页面渲染完整的文章树形导航（177 篇文章全部展开），存储在每页 HTML 中。1000 篇时每页多出 100KB+ 的导航标记。

### 目标

侧边栏仅渲染当前路径相关的节点，其余按需加载。

### 方案

**服务端裁剪（推荐）：**
- 在侧边栏模板中，只渲染：当前文章所在分支 + 同级分类 + 父级节点
- 其他分类只显示名称，不展开文章列表
- 用户点击分类后再加载该分类的文章列表

**客户端懒加载（备选）：**
- 初始渲染折叠所有分类
- 展开时通过 JavaScript 请求 JSON 数据填充

### 需求详情

| 行为 | 要求 |
|------|------|
| **默认渲染** | 当前文章所属分类的全部文章列表 + 其他分类仅显示分类名和篇数 |
| **点击切换** | 点击其他分类名，展开/折叠该分类的文章列表 |
| **移动端** | 保持当前行为（680px 以下隐藏侧边栏） |
| **状态保持** | 折叠状态存入 localStorage |

### 涉及文件

- `cygnusyang.github.io/layouts/_partials/site-sidebar-nav-node.html`
- `cygnusyang.github.io/layouts/_partials/site-sidebar-nav-assets.html`
- 可能需要新增一个 JavaScript 模块

### 验收标准

1. 非当前分类的侧边栏不渲染文章列表 DOM
2. 点击分类名可展开/折叠
3. 当前分类的文章列表完整显示
4. 页面 HTML 体积减少 40%+

---

## REQ-007：内容创建管道自动化

### 问题描述

当前使用 `archetypes/default.md` 作为唯一模板，缺少：
- 正确的 frontmatter 字段（weight、collections、icon 等）
- 章节号自动递增
- 不同内容类型（docs vs blog）的区分
- 文件创建后自动更新引用

### 目标

建立自动化的内容创建管道，支持一键创建符合规范的文章文件。

### 需求详情

#### 7.1 专用 Archetypes

| 文件 | 用途 |
|------|------|
| `archetypes/docs.md` | 系列文档（带 weight、collections、章节模板） |
| `archetypes/blog.md` | 独立博客文章（无需章节编号） |

#### 7.2 CLI 命令扩展

在 `tools/make.py` 中新增命令：

```bash
python tools/make.py new article --category openclaw --chapter 35 "文章标题"
python tools/make.py new article --category motor-control --slug "brushless-motor-basics" "标题"
python tools/make.py new article --blog "独立博客文章标题"
```

自动完成：
- 创建到正确目录，文件名使用英文 slug
- 自动分配下一个可用的 `weight`
- 生成正确的 frontmatter
- 复制文章模板内容
- 输出新文件路径

#### 7.3 校验规则

```bash
python tools/make.py validate
```

检查：
- frontmatter 字段完整性
- weight 连续性
- 重复标题
- 损坏的内部链接
- 文件大小异常（> 50KB 警告）

### 涉及文件

- `cygnusyang.github.io/archetypes/docs.md`（新建）
- `cygnusyang.github.io/archetypes/blog.md`（新建）
- `tools/make.py`（扩展 new 子命令）
- `tools/lib/article.py`（扩展现有逻辑）

### 验收标准

1. 一条命令创建格式正确的文章
2. weight 自动递增且不重复
3. 校验命令能检测常见问题
4. 创建后 Hugo 构建无错误

---

## REQ-008：启用输出压缩（minify）

### 问题描述

当前 `hugo.toml` 未配置 `minify`，public 目录 67MB 未压缩。HTML、CSS、JS 均保留空白和注释。

### 目标

启用 Hugo 内置的 minify 功能，减少输出文件体积。

### 需求详情

```toml
[minify]
  disableSVG = false
  [minify.tdewolff]
    [minify.tdewolff.html]
      keepDocumentTags = true
      keepEndTags = true
      keepQuotes = false
      keepWhitespace = false
    [minify.tdewolff.js]
      keepVarNames = false
      precision = 0
    [minify.tdewolff.css]
      precision = 0
```

### 涉及文件

- `cygnusyang.github.io/hugo.toml`

### 验收标准

1. 构建后 HTML/CSS/JS 文件无多余空白
2. public 目录体积减少 20%+
3. 页面功能正常（minify 不应破坏 JavaScript）

---

## REQ-009：统一目录命名语言（URL 美化）

### 问题描述

当前分类目录混合英文和中文：

| 英文目录 | 中文目录 |
|---------|---------|
| `openclaw` | `工程那些事` |
| `claudecode` | `研发那些事` |
| `academic-research-skills` | `电机控制`（嵌套在 `工程那些事/` 下）|

中文目录的 URL 会被 percent-encode，如：
```
/posts/%E5%B7%A5%E7%A8%8B%E9%82%A3%E4%BA%9B%E4%BA%8B/%E7%94%B5%E6%9C%BA%E6%8E%A7%E5%88%B6/
```

### 目标

所有目录统一使用英文 slug，中文标题通过 frontmatter 的 `title` 字段展示。

### 迁移映射

| 当前目录 | 建议英文名 | 说明 |
|---------|-----------|------|
| `工程那些事` | `engineering` | 工程实践类内容 |
| `工程那些事/电机控制` | `engineering/motor-control` | |
| `研发那些事` | `dev-practice` | 研发思考类 |
| `研发那些事/研发绩效体系` | `dev-practice/performance-system` | |

### 涉及文件

- 目录重命名（`git mv`）
- 各 `_index.md` 的 `title` 保留中文
- `content/_index.md` 中 `pinned_categories` 更新
- `hugo.toml` 中任何硬编码路径
- 生成 301 重定向

### 验收标准

1. 所有分类 URL 为纯英文路径
2. 页面标题仍显示中文
3. 旧 URL 正确重定向到新路径
4. 内部链接全部更新

---

## REQ-010：相关文章推荐优化

### 问题描述

当前使用 Hugo 内置的 `RelatedPages`，由于 tags 和 categories 为空，推荐仅基于正文关键词重叠度，准确度低。

### 目标

基于标签（REQ-005）和分类的匹配度，提供更精准的相关文章推荐。

### 需求详情

| 匹配维度 | 权重 | 说明 |
|---------|------|------|
| 相同 tags | 高 | 标签完全匹配的文章优先推荐 |
| 相同分类 | 中 | 同系列文章 |
| 关键词重叠 | 低 | 保留现有的关键词匹配 |
| 排除当前文章 | 必须 | 不推荐自己 |
| 推荐数量 | 5 篇 | 底部显示最多 5 篇相关文章 |

### 涉及文件

- `cygnusyang.github.io/hugo.toml`（相关度配置）
- `cygnusyang.github.io/layouts/posts/single.html`（相关文章渲染）

### 验收标准

1. 相关文章与当前文章主题相关
2. 同系列文章优先出现
3. 最多显示 5 篇
4. 无相关文章时不显示区块

---

## REQ-011：图片处理与资源管道

### 问题描述

- 当前所有文章不含图片资源（content 目录 2.1MB 纯文本）
- `hugo.toml` 未配置 `imaging` 默认参数
- 文章中的图片如果使用外部链接，存在失效风险
- 无 WebP/AVIF 自动格式转换

### 目标

建立图片处理管道，支持：
1. 文章图片本地化管理（Page Bundles）
2. 自动缩放到多个分辨率
3. WebP 格式自动转换
4. Lazy loading

### 需求详情

| 配置项 | 建议值 | 说明 |
|--------|--------|------|
| `imaging.quality` | 85 | 输出图片质量 |
| `imaging.resampleFilter` | CatmullRom | 缩放算法 |
| `imaging.anchor` | Smart | 裁剪锚点 |

### 涉及文件

- `cygnusyang.github.io/hugo.toml`（imaging 配置）
- `cygnusyang.github.io/layouts/posts/single.html`（图片渲染 shortcode）
- 可能需要自定义 `figure` shortcode

### 验收标准

1. 插入图片后自动生成分辨率适配版本
2. 输出 WebP 格式
3. 图片 lazy loading 生效
4. 文章引用图片方式向后兼容

---

## REQ-012：CI/CD 自动化构建与校验

### 问题描述

当前构建和发布流程：
1. 本地运行 `hugo` 构建
2. 手动 commit public 目录（通过子模块）
3. 推送到 GitHub Pages

无自动化校验环节，frontmatter 错误、链接断裂等问题只能在构建后发现。

### 目标

建立 GitHub Actions 自动化流程：

### 需求详情

#### 12.1 构建校验（PR 触发）

```yaml
# .github/workflows/build-check.yml
on: [pull_request]
```

执行：
- Hugo 构建（验证无错误）
- 链接检查（检查内部链接是否断裂）
- Frontmatter 校验（必填字段、weight 连续性）
- HTML 合法性检查（可选）

#### 12.2 自动部署（main 分支推送触发）

```yaml
# .github/workflows/deploy.yml
on:
  push:
    branches: [main]
```

执行：
- Hugo 构建
- 部署到 GitHub Pages
- 构建产物缓存

#### 12.3 链接检查（定期）

```yaml
# .github/workflows/link-check.yml
on:
  schedule:
    - cron: '0 3 * * 1'  # 每周一凌晨
```

执行：
- 全站链接检查
- 发现死链时创建 Issue

### 涉及文件

- `.github/workflows/build-check.yml`（新建）
- `.github/workflows/deploy.yml`（新建）
- `.github/workflows/link-check.yml`（新建）
- `tools/make.py validate`（依赖 REQ-007）

### 验收标准

1. PR 提交后自动运行构建检查
2. 构建失败时 PR 状态标记为失败
3. main 分支推送后自动部署到 GitHub Pages
4. 链接检查每周自动运行，发现死链创建 Issue

---

## 实施路线图

### Phase 1：紧急修复（当前即可开始）

| 需求 | 说明 |
|------|------|
| REQ-001 | 首页卡片动态化 — 解决每次新增分类手动改文件的问题 |
| REQ-002 | 搜索索引优化 — 一行配置，立竿见影 |
| REQ-003 | 列表页分页 — 防止 DOM 膨胀 |
| REQ-008 | 启用压缩 — 一行配置，减少 20% 体积 |

### Phase 2：可维护性提升（Phase 1 完成后）

| 需求 | 说明 |
|------|------|
| REQ-007 | 内容创建管道 — 让新增文章规范化 |
| REQ-005 | 分类法启用 — 为相关推荐和搜索打基础 |
| REQ-010 | 相关文章优化 — 基于标签的精准推荐 |
| REQ-012 | CI/CD 自动化 — 保障质量门禁 |

### Phase 3：URL 与性能优化（Phase 2 完成后）

| 需求 | 说明 |
|------|------|
| REQ-004 | 文件命名规范化 — 需要迁移脚本和 301 重定向 |
| REQ-009 | 目录英文名统一 — 需要迁移和重定向 |
| REQ-006 | 侧边栏按需渲染 — 减少每页 HTML 体积 |
| REQ-011 | 图片处理管道 — 如果开始使用配图 |

---

## 优先级定义

| 级别 | 含义 | 说明 |
|------|------|------|
| P0 | 阻塞 | 不解决无法安全扩展到 500+ 篇 |
| P1 | 重要 | 显著影响可维护性和用户体验 |
| P2 | 优化 | 锦上添花，建议但有条件时再做 |
