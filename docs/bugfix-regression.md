# Bugfix 回归测试记录

> 本文档记录所有已修复的 Bug，用于回归测试时快速验证。
> 每条记录包含：问题描述、修复方案、复现步骤、预期结果。

---

## Bug 状态总览

| 编号 | 问题摘要 | 严重级别 | 状态 | 修复 commit | 修复日期 |
|------|---------|---------|------|------------|---------|
| BUG-001 | find_articles 重复计数 collection 文件 | HIGH | ✅ 已修复 | `30428c7` | 2026-05-08 |
| BUG-002 | find_articles 未处理 blog/ 子目录 | HIGH | ✅ 已修复 | `596f097` | 2026-05-10 |
| BUG-003 | collection build 生成 title 缺章节编号 | MEDIUM | ✅ 已修复 | `46d2052` | 2026-05-08 |
| BUG-004 | 多级目录构建时章节编号重复 | HIGH | ✅ 已修复 | `6b852c4` | 2026-05-08 |
| BUG-005 | 多次 build 产生重复文章 | HIGH | ✅ 已修复 | `8461a39` | 2026-05-09 |
| BUG-006 | 嵌套项目推送状态检测失败 | MEDIUM | ✅ 已修复 | `df36427` | 2026-05-09 |
| BUG-007 | 嵌套项目首页卡片识别失败 | MEDIUM | ✅ 已修复 | `77e2c6e` | 2026-05-10 |
| BUG-008 | 文章正文重复 H1 标题 | MEDIUM | ✅ 已修复 | `3b80b1f` | 2026-05-07 |
| BUG-009 | publish commit 消息不准确 | LOW | ✅ 已修复 | `3a5d8ed` | 2026-05-09 |
| BUG-010 | publish 未更新父仓库子模块引用 | HIGH | ✅ 已修复 | `ef9bc31` | 2026-05-10 |
| BUG-011 | make.py 未使用的导入和冗余代码 | LOW | ✅ 已修复 | `323014a` | 2026-05-10 |
| BUG-012 | 卡片点击进入分类页面只显示空状态 | HIGH | ✅ 已修复 | `68915c6` | 2026-05-10 |
| BUG-013 | 左侧导航栏与首页卡片分类不一致 | HIGH | 🚧 待修复 | — | — |

**统计：** 已修复 12/13，待修复 1，修复率 92.3%

---

## BUG-001：find_articles 重复计数 collection 项目文件

**严重级别：** HIGH
**修复 commit：** `30428c7`
**修复日期：** 2026-05-08
**涉及文件：** `tools/lib/article.py`

### 问题描述

`find_articles()` 扫描 `knowledge-base/articles/` 时，将 `NN-` 开头的集合项目目录下的所有 `.md` 文件也计入总数。`status` 命令显示 1718 篇文章，实际包含了 collection 构建产物。

### 修复方案

在 `find_articles()` 中跳过 `NN-` 开头的目录，集合文章应通过 `collection build` 单独处理。

### 复现步骤

1. 在 `knowledge-base/articles/` 下创建 `01-test/README.md`
2. 运行 `python tools/make.py status`
3. 观察文章总数

### 预期结果

文章总数不包含 `01-test/` 目录下的 `.md` 文件。

---

## BUG-002：find_articles 未处理集合目录的 blog/ 子目录

**严重级别：** HIGH
**修复 commit：** `596f097`
**修复日期：** 2026-05-10
**涉及文件：** `tools/lib/article.py`

### 问题描述

集合项目目录（`NN-` 开头）内的文章存储在 `blog/` 子目录下，但 `find_articles()` 直接遍历集合目录时包含了所有 `.md` 文件（包括源码文件、设计文档等），而非仅提取博客文章。

### 修复方案

对 `NN-` 目录，只提取 `blog/` 子目录下的 `.md` 文件；如果不存在 `blog/` 目录，则跳过该集合目录。

### 复现步骤

1. 在 `knowledge-base/articles/01-openclaw/` 下创建 `design.md`（非 blog 目录）
2. 在 `knowledge-base/articles/01-openclaw/blog/` 下创建 `test.md`
3. 运行 `python tools/make.py status`

### 预期结果

只显示 `blog/` 下的 `test.md`，不显示 `design.md`。

---

## BUG-003：collection build 生成的 Hugo title 缺少章节编号

**严重级别：** MEDIUM
**修复 commit：** `46d2052`
**修复日期：** 2026-05-08
**涉及文件：** `tools/lib/collection.py`

### 问题描述

`build_collection()` 生成的 Hugo frontmatter 中 `title` 字段只有原文标题（如 `"无刷电机基础"`），没有章节编号前缀，与文件名中的 `"第01章"` 不一致。

### 修复方案

在生成 title 时拼接全局章节序号：`title: "第01章 无刷电机基础"`。

### 复现步骤

1. 运行 `python tools/make.py collection build 04-工程那些事/01-电机控制`
2. 检查 `cygnusyang.github.io/content/posts/工程那些事/电机控制/` 下生成文件的 frontmatter

### 预期结果

每个文件的 `title` 字段包含 `"第NN章"` 前缀。

---

## BUG-004：多级目录构建时章节编号重复

**严重级别：** HIGH
**修复 commit：** `6b852c4`
**修复日期：** 2026-05-08
**涉及文件：** `tools/lib/collection.py`

### 问题描述

不同子目录下的文件都以 `"01-"` 开头（如 `01-intro/01-xxx.md`、`02-advanced/01-yyy.md`），原逻辑从文件名提取章节号，导致多个文件都变成 `第01章`。

### 修复方案

改用全局连续计数器：文件按路径排序后顺序编号（第01章~第NN章），不再从文件名提取。

### 复现步骤

1. 创建两个子目录：`01-intro/01-a.md` 和 `02-advanced/01-b.md`
2. 运行 `python tools/make.py collection build` 对应集合
3. 检查生成文件的标题

### 预期结果

生成 `第01章 a` 和 `第02章 b`，编号不重复。

---

## BUG-005：collection build 多次执行产生重复文章

**严重级别：** HIGH
**修复 commit：** `8461a39`
**修复日期：** 2026-05-09
**涉及文件：** `tools/lib/collection.py`

### 问题描述

每次 `collection build` 都追加新文件到 Hugo posts 目录，多次执行后产生大量重复文章（同一源文件生成多个不同日期的版本）。

### 修复方案

构建前先清理该集合目录下所有旧的 `.md` 文件（保留 `_index.md` 最后重建）。

### 复现步骤

1. 运行 `python tools/make.py collection build 01-openclaw`
2. 再次运行同一命令
3. 检查 `cygnusyang.github.io/content/posts/01-openclaw/` 下的文件数量

### 预期结果

文件数量不变，无重复文章。

---

## BUG-006：collection list 嵌套项目推送状态检测失败

**严重级别：** MEDIUM
**修复 commit：** `df36427`
**修复日期：** 2026-05-09
**涉及文件：** `tools/lib/collection.py`

### 问题描述

`list_projects()` 检测 GitHub Pages 推送状态时，只检查 `content/posts/` 下的一级目录名。嵌套项目（如 `工程那些事/电机控制`）永远匹配不到，显示为"未推送"。

### 修复方案

递归扫描 `content/posts/` 下所有带 `_index.md` 的目录，构建相对路径集合进行精确匹配。

### 复现步骤

1. 构建嵌套集合：`python tools/make.py collection build 04-工程那些事/01-电机控制`
2. 运行 `python tools/make.py publish`
3. 运行 `python tools/make.py collection list`

### 预期结果

嵌套项目 `04-工程那些事/01-电机控制` 显示为"已推送"。

---

## BUG-007：嵌套项目首页卡片识别失败

**严重级别：** MEDIUM
**修复 commit：** `77e2c6e`
**修复日期：** 2026-05-10
**涉及文件：** `tools/lib/collection.py`

### 问题描述

首页卡片系统使用 `aria-label` 映射识别项目，但嵌套项目（如 `工程那些事/电机控制`）没有在 `_CARD_ARIA_LABELS` 中注册，导致卡片显示默认占位符。

### 修复方案

- `_CARD_ARIA_LABELS` 添加嵌套项目映射
- `_CARD_ICONS` 添加嵌套项目默认图标
- `_update_index_cards` 支持多 label 匹配
- `_slug_from_card_href` 从 href 反推 slug

### 复现步骤

1. 构建嵌套集合
2. 运行 Hugo 本地服务器查看首页
3. 检查对应集合卡片是否显示正确图标和描述

### 预期结果

卡片显示正确的图标（⚙️）和描述文字。

---

## BUG-008：文章正文包含重复 H1 标题

**严重级别：** MEDIUM
**修复 commit：** `3b80b1f`
**修复日期：** 2026-05-07
**涉及文件：** `tools/lib/publisher.py`

### 问题描述

源文章 frontmatter 中已有 `title` 字段，但正文开头仍有 `# 标题`，导致 Hugo 渲染后页面顶部出现两个相同标题。

### 修复方案

添加 `_remove_title_from_body()` 函数，在生成 frontmatter 时检测并移除正文开头与 frontmatter title 相同的 H1 标题。

### 复现步骤

1. 创建文章，正文开头包含 `# 文章标题`
2. frontmatter 中 `title: "文章标题"`
3. 运行 `python tools/make.py build` 该文章
4. 检查生成的 Hugo 文件正文

### 预期结果

生成的文件正文不包含与 frontmatter title 相同的 H1 标题。

---

## BUG-009：publish 命令 commit 消息不准确

**严重级别：** LOW
**修复 commit：** `3a5d8ed`
**修复日期：** 2026-05-09
**涉及文件：** `tools/make.py`

### 问题描述

`publish` 命令使用固定 commit 消息，无法反映实际变更内容。

### 修复方案

使用 `git diff --cached --name-only` 获取变更目录列表，生成动态 commit 消息（如 `post: update openclaw collection (5 articles)`）。

### 复现步骤

1. 修改一篇文章并构建到博客
2. 运行 `python tools/make.py publish`
3. 运行 `git log -1` 查看 commit 消息

### 预期结果

commit 消息包含变更的集合名称和文章数量。

---

## BUG-010：publish 未更新父仓库子模块引用

**严重级别：** HIGH
**修复 commit：** (含在多个 commit 中)
**修复日期：** 2026-05-10
**涉及文件：** `tools/make.py`

### 问题描述

`publish` 只推送 `cygnusyang.github.io` 子模块内部的变更，不更新父仓库的子模块引用。发布后需要手动在父仓库执行 `git add cygnusyang.github.io && git commit && git push`。

### 修复方案

新增 `_update_parent_submodule()` 函数，`publish --update-submodule` 时自动回到父仓库更新引用并推送。

### 复现步骤

1. 修改文章并构建
2. 运行 `python tools/make.py publish --update-submodule`
3. 在父仓库运行 `git log -1`

### 预期结果

父仓库有 `chore: update submodule cygnusyang.github.io` 提交。

---

## BUG-011：make.py 存在未使用的导入和冗余代码

**严重级别：** LOW
**修复 commit：** `323014a`
**修复日期：** 2026-05-10
**涉及文件：** `tools/make.py`

### 问题描述

- `Article`、`generate_hugo_frontmatter`、`normalize_slug` 被导入但未使用
- `_extract_chapter_number` 在 dry_run 中导入但未使用
- `import re` 在 3 个函数内重复导入（应放在模块级别）
- `_update_parent_submodule` 接收 `pages_dir` 参数但未使用

### 修复方案

- 移除未使用的导入
- 将 `import re` 移至模块顶部
- 移除未使用的函数参数

### 复现步骤

1. 运行 `python tools/make.py --help`
2. 运行 `python tools/make.py status`
3. 运行 `python tools/make.py collection list`

### 预期结果

所有命令正常运行，无 import 相关错误。

---

## BUG-012：首页卡片点击进入分类页面只显示"暂无分类目录"

**严重级别：** HIGH
**修复 commit：** (待提交)
**修复日期：** 2026-05-10
**涉及文件：** `cygnusyang.github.io/layouts/posts/section.html`

### 问题描述

首页卡片点击后进入分类页面（如 `/posts/openclaw/`），页面只显示"暂无分类目录。在 `content/posts/` 下创建子目录即可添加分类。"，不展示该分类下的任何文章。

根因：`section.html` 模板通过 `.Sections`（嵌套子目录）判断是否有内容。当分类目录下直接存放文章文件（如 `openclaw/` 下有 34 篇 `.md` 文件）而没有子目录时，`.Sections` 为空，触发空状态分支。

### 修复方案

修改 `section.html` 模板逻辑：
1. 将条件判断从 `if $sections` 改为 `if or $sections $pages`
2. 当有子目录时，按现有逻辑显示子目录分组
3. 当没有子目录但有页面时，直接显示页面列表（按日期倒序）
4. 当两者都没有时，显示空状态

### 复现步骤

1. 启动 Hugo 本地服务器：`hugo server`
2. 打开首页，点击任意项目卡片（如 OpenClaw）
3. 进入分类页面

### 预期结果

分类页面展开显示该分类下的所有文章列表，包含标题、日期和描述。

---

## BUG-013：左侧导航栏分类与首页卡片分类不一致

**严重级别：** HIGH
**修复 commit：** 待修复
**修复日期：** 2026-05-10
**涉及文件：** `cygnusyang.github.io/layouts/_partials/site-sidebar-nav-assets.html`, `cygnusyang.github.io/layouts/shortcodes/category-popup.html`

### 问题描述

首页文章卡片和左侧文档导航栏显示的分类不一致，存在两套平行的目录结构：

- **首页卡片** 链接到扁平目录：`openclaw/`, `gstack/`, `gbrain/`, `claudecode/`, `codex/`, `mcp/`, `harness/`, `academic-research-skills/`
- **左侧导航栏** 显示编号目录：`01-openclaw/`, `02-gstack/`, `03-gbrain/`, `06-claudecode/`, `08-codex/`, `09-harness/`, `10-academic-research-skills/`

根因：`site-sidebar-nav-assets.html` 通过 `.Site.Sections` 遍历所有 section，包括 `01-openclaw/` 等编号目录。而 `category-popup.html`（首页卡片）按 `pinned_categories` 参数匹配 slug，指向的是 `openclaw/` 等扁平目录。两边指向的是不同的路径。

### 约束条件

首页卡片分类、左侧导航栏分类、`content/posts/` 下的实际目录结构三者必须一一对应：

1. `pinned_categories` 中的 slug 必须与 `content/posts/` 下的实际目录名一致
2. 左侧导航栏只显示 `pinned_categories` 中列出的分类
3. 首页卡片点击后的 URL 必须与导航栏中对应分类的 URL 一致
4. 不允许存在两套平行的目录结构（编号目录 vs 扁平目录）

### 复现步骤

1. 打开首页，观察"文章"区域的分类卡片（如 OpenClaw、GStack 等）
2. 点击任意卡片进入分类页面
3. 观察左侧导航栏显示的分类名称
4. 对比两者是否一致

### 预期结果

首页卡片显示的分类与左侧导航栏显示的分类一一对应，名称、顺序、层级关系完全一致。

---

## 回归测试检查清单

每次发布新功能或修复 Bug 后，执行以下检查：

### 基础功能

- [ ] `make.py --help` 正常显示所有子命令
- [ ] `make.py new "测试文章"` 成功创建文件
- [ ] `make.py status` 显示正确的文章总数（不包含集合目录文件）
- [ ] `make.py config` 显示配置信息

### 集合构建

- [ ] `make.py collection list` 正确显示所有集合及推送状态
- [ ] `make.py collection build 01-openclaw` 成功构建
- [ ] 连续执行两次 `collection build` 不产生重复文件
- [ ] 嵌套集合构建编号连续（无重复章节号）
- [ ] `collection build --dry-run` 预览不修改任何文件
- [ ] 生成文件的 frontmatter title 包含章节编号

### 博客构建

- [ ] `make.py build article.md` 只生成博客内容
- [ ] 多平台内容需显式指定 `--platform` 参数
- [ ] `make.py build --all --incremental` 只处理变更文章
- [ ] 生成文件正文不包含与 frontmatter title 重复的 H1 标题

### 发布

- [ ] `make.py publish` 无变更时不创建空提交
- [ ] `make.py publish --update-submodule` 同步更新父仓库
- [ ] commit 消息动态反映变更内容

### 校验与统计

- [ ] `make.py validate` 正确检测 frontmatter 缺失、图片失效等问题
- [ ] `make.py stats` 显示统计报表
- [ ] `make.py stats --json` 输出 JSON 格式

### 代码质量

- [ ] 无未使用的 import
- [ ] 无函数内重复的模块级 import（如 `import re` 在函数内）
- [ ] 无未使用的函数参数
- [ ] `python -m py_compile tools/make.py` 编译通过
