# 第十四章：技能系统深入 —— 50+ 内置技能与实战场景

你用 Codex 写代码时，有没有发现它"懂"某些特定的领域？比如让你生成一张图片，它知道用 DALL-E；问你 OpenAI API 的最新文档，它能给出带引用的准确答案。这不是 AI 的魔法，而是 **Skills 系统在工作**。

Codex 内置了 50+ 个技能，每个技能都是一个"领域专家"。本文带你深入了解这些技能是什么，以及如何在实际场景中使用它们。

`★ Insight ─────────────────────────────────────`
**技能系统的三层加载机制**
技能采用渐进式加载设计：只有元数据（~100 tokens）常驻上下文，技能内容在触发后才加载（<5k tokens），而 scripts/ 和 assets/ 等资源文件按需读取甚至直接执行。这种设计让 Codex 可以携带大量专业领域知识，而不会拖垮核心对话性能。
`─────────────────────────────────────────────────`

## Skills Crate 深度解析

**位置**：`source/codex/codex-rs/skills/`

核心技能系统由两个 crate 组成：

```
codex-rs/
├── skills/              # 技能加载器和渲染引擎
│   ├── src/
│   │   ├── loader.rs    # 技能目录扫描与解析
│   │   ├── render.rs    # 模板渲染（58KB，核心！）
│   │   ├── injection.rs # 注入机制（何时触发技能）
│   │   └── manager.rs   # 技能生命周期管理
│   └── src/assets/samples/  # 内置技能示例
└── core-skills/         # 技能元数据和调用逻辑
    ├── src/
    │   ├── mention_counts.rs # 技能使用频率追踪
    │   └── env_var_dependencies.rs # 技能的环境依赖
```

## 内置技能全景图

### 1. 开发工具类技能

#### skill-creator —— 创造技能的技能

当你说"帮我创建一个处理 PDF 的技能"时，Codex 会触发 skill-creator。

**场景**：你需要团队内部使用一个专门的技能，用于生成符合公司规范的 PR 模板。

**skill-creator 提供什么**：
- 技能目录脚手架（`SKILL.md`, `agents/openai.yaml`）
- 最佳实践指南（ concise is key, progressive disclosure）
- 验证脚本（`quick_validate.py`）
- 前向测试工作流

**实际输出**：
```bash
$ codex "创建一个 pr-template 技能"
# skill-creator 触发，生成：
pr-template/
├── SKILL.md              # 技能定义
├── agents/
│   └── openai.yaml      # UI 元数据
└── scripts/
    └── validate.py      # 自定义验证
```

**核心原则**（来自 SKILL.md）：
1. **Concise is Key** — 上下文是公共资源，只放 Codex 真正需要的知识
2. **渐进式披露** — 元数据常驻，内容按需加载，资源文件按需读取
3. **自由度匹配** — 脆脆的任务用低自由度脚本，灵活的任务用高自由度指导

#### plugin-creator —— 插件脚手架

"创建一个 GitLab 集成插件"会触发 plugin-creator。

**场景**：你需要一个插件，让 Codex 能直接与公司内部的 GitLab 实例交互。

**生成结构**：
```
gitlab-integration/
├── .codex-plugin/
│   └── plugin.json      # 插件清单
├── skills/              # 插件专属技能
├── hooks/               # 钩子
├── mcp/                 # MCP 服务器
└── apps/                # App 服务器
```

#### skill-installer —— 从 GitHub 安装技能

"有哪些可用的技能？"或"安装 datadog 技能"会触发。

**内置来源**：
- 精选列表：`openai/skills/.curated`
- 实验列表：`openai/skills/.experimental`

**工作流**：
1. 调用 `scripts/list-skills.py` 获取列表
2. 用户选择后，调用 `scripts/install-skill-from-github.py`
3. 安装到 `$CODEX_HOME/skills/`
4. 提示用户重启 Codex

### 2. 内容生成类技能

#### imagegen —— 图片生成与编辑

"生成一张产品展示图"或"把这张图的背景去掉"会触发 imagegen。

**两种模式**：

**1. 内置工具模式（默认）**：
- 使用内置的 `image_gen` 工具
- 不需要 `OPENAI_API_KEY`
- 支持生成、编辑、简单透明背景

**2. CLI 回退模式**：
- 当用户明确要求 CLI/API/模型路径时使用
- 需要 `OPENAI_API_KEY`
- 三个子命令：`generate`, `edit`, `generate-batch`

**决策树**：
```
用户请求图片
├─ 有图片要编辑？ → edit 模式
├─ 没有图片？ → generate 模式
├─ 明确要求透明背景？
│  └─ 先用 chroma-key，失败则询问是否回退到 gpt-image-1.5
└─ 需要批量？
   └─ 多次调用内置工具，不自动回退 CLI
```

**保存策略**：
1. 默认保存在 `$CODEX_HOME/generated_images/`
2. 如果项目需要，移动到工作区
3. 只预览不使用，保持原位置
4. 从不覆盖，创建版本化文件名（`hero-v2.png`）

### 3. 文档与 API 类技能

#### openai-docs —— OpenAI 官方文档查询

"GPT-5 的 API 怎么用？"或"最新的模型是什么？"会触发 openai-docs。

**优先级**：
1. MCP 工具（`mcp__openaiDeveloperDocs__*`）- 最高优先
2. 官方文档直接获取
3. 捆绑参考文件（`references/latest-model.md`）

**关键工作流**：

**模型选择**：
```bash
# 用户问：最新的模型是什么？
# openai-docs 流程：
1. 尝试获取 https://developers.openai.com/api/docs/guides/latest-model.md
2. 解析出最新模型 ID
3. 如果用户明确指定模型，保持用户选择
4. 动态升级时运行 node scripts/resolve-latest-model-info.js
```

**模型升级**：
```bash
# 用户说：把项目升级到最新模型
# openai-docs 流程：
1. 获取最新模型信息
2. 获取迁移和提示词指南 URL
3. 只升级：API 模型字符串、相关提示词
4. 不改动：历史文档、示例、eval 基准、提供程序比较
5. 如需 API 表面改动，标记为需要确认
```

**产品快照**（来自技能）：
1. Apps SDK — ChatGPT 应用
2. Responses API — 有状态多模态交互
3. Chat Completions API — 基础对话
4. Codex — 编码代理
5. gpt-oss — 开源推理模型
6. Realtime API — 实时语音
7. Agents SDK — 代理应用工具包

`★ Insight ─────────────────────────────────────`
**MCP 优先的设计哲学**
openai-docs 技能明确要求：对于 OpenAI 相关问题，始终优先使用 MCP 工具而非通用 web 搜索。这体现了 Codex 的设计理念 — 专用工具优于通用工具。MCP 服务器返回的结构化数据可以直接引用，而 web 搜索的结果需要额外解析和验证。
`─────────────────────────────────────────────────`

## 技能的触发机制

### injection.rs 中的触发逻辑

技能不是被动"被调用"，而是基于**意图匹配**主动触发。

**触发因素**：
1. **description 字段** — 主要触发器
2. **用户查询关键词**
3. **上下文线索**
4. **使用频率**（mention_counts）

**示例**（imagegen）：
```yaml
---
name: "imagegen"
description: "Generate or edit raster images when the task benefits from AI-created
bitmap visuals such as photos, illustrations, textures, sprites, mockups, or
transparent-background cutouts. Use when Codex should create a brand-new image..."
---
```

当用户说"帮我做一个 logo"时，Codex 匹配到 "create a brand-new image" → 触发 imagegen。

### 技能使用频率追踪

`mention_counts.rs` 维护每个技能的使用统计：
- 高频技能可能被优先匹配
- 低频或从未使用的技能会被降低优先级
- 帮助优化技能加载策略

## 技能的资源体系

### 1. Scripts（`scripts/`）

**用途**：需要确定性的、重复编写的代码。

**何时使用**：
- 相同代码每次都要重写
- 需要确定性可靠性

**示例**：
- `scripts/rotate_pdf.py` — PDF 旋转
- `scripts/image_gen.py` — 图片生成 CLI
- `scripts/list-skills.py` — 技能列表
- `scripts/validate.py` — 技能验证

**好处**：
- Token 高效
- 可直接执行，不加载上下文
- 可以被 Codex 读取和修改

### 2. References（`references/`）

**用途**：文档和参考资料，按需加载到上下文。

**何时使用**：
- Codex 工作时需要引用的文档
- 大型参考材料

**示例**：
- `references/schema.md` — 数据库模式
- `references/policies.md` — 公司策略
- `references/api_docs.md` — API 规范
- `references/latest-model.md` — 最新模型信息（openai-docs）

**最佳实践**：
- 文件 > 10k 字时，在 SKILL.md 中包含 grep 模式
- 避免与 SKILL.md 重复
- 只在 SKILL.md 中保留核心流程指导

### 3. Assets（`assets/`）

**用途**：不加载到上下文，但在输出中使用的文件。

**何时使用**：
- 技能需要文件用于最终输出

**示例**：
- `assets/logo.png` — 品牌资源
- `assets/slides.pptx` — PowerPoint 模板
- `assets/frontend-template/` — HTML/React 脚手架

**好处**：
- 将输出资源与文档分离
- Codex 可以使用文件而不加载到上下文

## 渐进式披露设计原则

技能使用三层加载系统：

```
┌─────────────────────────────────────────────────────────┐
│ Level 1: Metadata（name + description）                  │
│ - 常驻上下文                                             │
│ - ~100 tokens                                            │
│ - 用于技能匹配和触发                                     │
└─────────────────────────────────────────────────────────┘
                          ↓ 触发后
┌─────────────────────────────────────────────────────────┐
│ Level 2: SKILL.md body                                   │
│ - 技能触发后加载                                         │
│ - <5k tokens                                             │
│ - 核心工作流和指导                                       │
└─────────────────────────────────────────────────────────┘
                          ↓ 按需
┌─────────────────────────────────────────────────────────┐
│ Level 3: Bundled Resources                               │
│ - scripts/ 可直接执行                                    │
│ - references/ 按需加载                                   │
│ - assets/ 输出使用                                       │
│ - 无限制（因为 scripts 不读上下文）                       │
└─────────────────────────────────────────────────────────┘
```

### 渐进式披露模式

**模式 1：高层指导 + 引用**
```markdown
# PDF Processing

## Quick start
Extract text with pdfplumber:
[code example]

## Advanced features
- **Form filling**: See [FORMS.md](FORMS.md)
- **API reference**: See [REFERENCE.md](REFERENCE.md)
- **Examples**: See [EXAMPLES.md](EXAMPLES.md)
```

**模式 2：领域特定组织**
```
bigquery-skill/
├── SKILL.md (overview + navigation)
└── references/
    ├── finance.md (revenue, billing)
    ├── sales.md (opportunities, pipeline)
    ├── product.md (API usage, features)
    └── marketing.md (campaigns, attribution)
```

当用户问销售指标时，只加载 `sales.md`。

**模式 3：条件性细节**
```markdown
# DOCX Processing

## Creating documents
Use docx-js. See [DOCX-JS.md](DOCX-JS.md).

## Editing documents
For simple edits, modify XML directly.
**For tracked changes**: See [REDLINING.md](REDLINING.md)
**For OOXML details**: See [OOXML.md](OOXML.md)
```

`★ Insight ─────────────────────────────────────`
**上下文经济学的应用**
Codex 的技能系统是对"上下文经济学"的绝佳实践。每个技能都是对上下文窗口的"投资"——元数据是固定成本，内容是可变成本。渐进式披露确保只在真正需要时才"支付"这些成本。这种设计让 Codex 可以携带 50+ 个专业领域的知识，而上下文窗口仍然保持高效。
`─────────────────────────────────────────────────`

## 技能文件结构详解

### 最小结构
```
skill-name/
└── SKILL.md (required)
    ├── YAML frontmatter
    │   ├── name: (required)
    │   └── description: (required)
    └── Markdown body
```

### 完整结构
```
skill-name/
├── SKILL.md (required)
├── agents/
│   └── openai.yaml (recommended)
├── scripts/ (optional)
│   └── *.py, *.sh, etc.
├── references/ (optional)
│   └── *.md
└── assets/ (optional)
    └── (output resources)
```

### Frontmatter 关键

```yaml
---
name: skill-creator
description: Guide for creating effective skills. This skill should be
used when users want to create a new skill (or update an existing skill)
that extends Codex's capabilities with specialized knowledge,
workflows, or tool integrations.
metadata:
  short-description: Create or update a skill
---
```

**重要提示**：
- `name` 和 `description` 是 Codex **唯一读取**的字段
- 所有"何时使用"信息必须放在 `description` 中
- Body 中的 "When to Use This Skill" 段落没有帮助，因为 Body 只在触发后加载

### agents/openai.yaml

UI 元数据，用于技能列表和芯片显示：

```yaml
display_name: "Skill Creator"
short_description: "Create or update a skill"
default_prompt: "Create a skill for..."
```

**生成方式**：
```bash
python scripts/generate_openai_yaml.py <skill-folder> \
  --interface display_name="Skill Creator" \
  --interface short_description="Create or update a skill"
```

## 技能命名规范

**规则**：
- 只使用小写字母、数字和连字符
- 用户提供的标题会被规范化为连字符格式
- 长度 < 64 字符
- 首选简短的、动词引导的短语

**示例**：
- "Plan Mode" → `plan-mode`
- "GitHub Issue Commenter" → `gh-issue-commenter`
- "Linear Project Manager" → `linear-project-manager`

**命名空间**：
当工具名称能提高清晰度时，按工具命名：
- `gh-address-comments`
- `linear-address-issue`

## 技能创建完整工作流

### Step 1: 理解技能（具体示例）

跳过前提：使用模式已经清楚。

**示例对话**：
```
用户：我想创建一个 PDF 处理技能
Codex：这个技能应该支持什么功能？编辑、旋转、其他？
用户：主要是旋转和提取文本
Codex：能给我一些使用示例吗？
用户：比如"帮我旋转这个 PDF"或"提取 PDF 中的表格"
```

### Step 2: 规划可复用内容

分析每个示例：
1. 考虑如何从零开始执行
2. 识别哪些 scripts、references、assets 会有帮助

**pdf-editor 技能分析**：
1. 旋转 PDF 每次都重写相同代码
2. `scripts/rotate_pdf.py` 会有帮助

**frontend-webapp-builder 技能分析**：
1. 每次都需要相同的 HTML/React 脚手架
2. `assets/hello-world/` 模板会有帮助

**big-query 技能分析**：
1. 每次都要重新发现表模式
2. `references/schema.md` 会有帮助

### Step 3: 初始化技能

```bash
scripts/init_skill.py <skill-name> \
  --path <output-directory> \
  [--resources scripts,references,assets] \
  [--examples]
```

**示例**：
```bash
scripts/init_skill.py pdf-editor \
  --path ~/.codex/skills \
  --resources scripts,references \
  --examples
```

生成的模板包括：
- SKILL.md with proper frontmatter
- agents/openai.yaml
- 可选的 scripts/, references/, assets/ 目录
- 示例文件（如果使用 `--examples`）

### Step 4: 编辑技能

**从可复用资源开始**：
- 创建并测试 scripts
- 添加 references
- 添加 assets

**更新 SKILL.md**：
- 使用命令式/不定式形式
- Frontmatter 写好 name 和 description
- Body 写工作流和资源使用指导

### Step 5: 验证技能

```bash
scripts/quick_validate.py <path/to/skill-folder>
```

验证：
- YAML frontmatter 格式
- 必需字段
- 命名规则

### Step 6: 迭代

**前向测试工作流**：
1. 在实际任务中使用技能
2. 注意挣扎或低效之处
3. 识别如何更新 SKILL.md 或资源
4. 实现更改并再次测试
5. 如果合理，进行前向测试

## 前向测试

使用子代理来压力测试技能，使用最小上下文。

**决策规则**：
- 倾向于前向测试
- 如果风险高（长时间、需要额外批准、修改生产系统），请求批准

**考虑因素**：
- 为独立传递使用新线程
- 传递技能和请求，类似于用户的方式
- 传递原始工件，不是你的结论
- 避免显示预期答案或预期修复
- 每次迭代后从源工件重建上下文
- 清理子代理的工件以避免污染

**提示词模式**：
```
好: Use $skill-x at /path/to/skill-x to solve problem y
坏: Review the skill at /path/to/skill-x; pretend a user asks you to...
```

## 技能系统架构

### loader.rs 的职责

```rust
// 伪代码
pub struct SkillLoader {
    skill_paths: Vec<PathBuf>,
}

impl SkillLoader {
    pub fn load_skills(&self) -> Result<Vec<Skill>> {
        // 1. 扫描技能目录
        // 2. 解析 SKILL.md frontmatter
        // 3. 提取 name 和 description
        // 4. 验证必需字段
        // 5. 返回技能列表
    }

    pub fn load_skill_body(&self, skill: &Skill) -> Result<String> {
        // 1. 读取 SKILL.md body
        // 2. 返回内容
    }
}
```

### render.rs 的职责（58KB，核心！）

```rust
pub struct SkillRenderer {
    template_engine: TemplateEngine,
}

impl SkillRenderer {
    pub fn render(&self, skill: &Skill, context: &Context) -> Result<String> {
        // 1. 加载 SKILL.md body
        // 2. 应用模板变量
        // 3. 返回渲染后的内容
    }

    pub fn render_reference(&self, path: &Path) -> Result<String> {
        // 1. 读取 references/ 中的文件
        // 2. 返回内容
    }
}
```

### injection.rs 的职责

```rust
pub struct SkillInjector {
    skills: Vec<Skill>,
}

impl SkillInjector {
    pub fn find_relevant_skills(&self, query: &str) -> Vec<Skill> {
        // 1. 匹配 query 与 skill.description
        // 2. 返回相关技能
    }

    pub fn inject_skills(&self, prompt: &str, skills: &[Skill]) -> String {
        // 1. 将技能元数据注入 prompt
        // 2. 返回增强后的 prompt
    }
}
```

### manager.rs 的职责

```rust
pub struct SkillManager {
    loader: SkillLoader,
    renderer: SkillRenderer,
    injector: SkillInjector,
}

impl SkillManager {
    pub async fn process_request(&mut self, request: &Request) -> Response {
        // 1. 查找相关技能
        // 2. 注入技能元数据
        // 3. 发送到模型
        // 4. 如果需要，加载技能 body
        // 5. 如果需要，加载 references
    }
}
```

## 技能存储位置

**技能搜索路径**（按优先级）：
1. `$CODEX_HOME/skills/`
2. `~/.codex/skills/`（当 CODEX_HOME 未设置）
3. `<repo-root>/.codex/skills/`
4. 内置技能（`.system/`）

**.system 技能预安装**：
位于 `openai/skills/.system` 的技能已预安装，不需要用户安装。

## 实战场景

### 场景 1：创建团队专用 PR 模板技能

**需求**：团队有特定的 PR 模板格式，包含必需字段。

**对话**：
```
你：创建一个 pr-template 技能
Codex：[skill-creator 触发]
     这个技能应该支持什么？
你：生成符合公司规范的 PR 模板
Codex：能给我一个模板示例吗？
你：需要包含：类型、描述、测试计划、审查人
```

**技能结构**：
```
pr-template/
├── SKILL.md
│   ├── description: "生成公司 PR 模板..."
│   └── body: 模板生成工作流
├── references/
│   └── template.md  # 公司 PR 模板
└── assets/
    └── template.md  # 输出模板
```

**使用**：
```
你：为新功能创建 PR
Codex：[使用 pr-template 技能生成]
     # PR: 新功能 XXX

     ## 类型
     feat: 添加 XXX 功能

     ## 描述
     ...

     ## 测试计划
     - [ ] 单元测试
     - [ ] 集成测试

     ## 审查人
     @user1 @user2
```

### 场景 2：批量生成网站图标

**需求**：为新项目生成一套统一的图标。

**对话**：
```
你：生成一套电商网站的图标，5个：购物车、用户、搜索、收藏、客服
Codex：[imagegen 触发]
     我将生成5个图标...
```

**imagegen 工作流**：
1. 决定模式：内置工具（5次调用）
2. 意图：generate
3. 输出：项目需要，移动到 `assets/icons/`
4. 策略：多次内置调用，不使用 batch
5. 收集输入：风格统一、256x256、PNG

**输出**：
```
$CODEX_HOME/generated_images/
├── cart.png
├── user.png
├── search.png
├── favorite.png
└── support.png

# Codex 移动到项目
assets/icons/
├── cart.png
├── user.png
...
```

### 场景 3：查询最新 OpenAI API 文档

**需求**：了解 GPT-5 的最新 API 用法。

**对话**：
```
你：GPT-5 怎么用？
Codex：[openai-docs 触发]
     使用 MCP 工具查询...
```

**openai-docs 工作流**：
1. 澄清请求：模型选择/文档查询
2. 尝试 MCP 工具：
   - `mcp__openaiDeveloperDocs__search_openai_docs`
   - 查询 "GPT-5 API"
3. 获取结果，引用文档
4. 如果 MCP 失败：
   - 提示用户安装 MCP 服务器
   - 或回退到 bundled references

**输出**：
```
根据 OpenAI 官方文档：

GPT-5 是最新的推理模型，支持：
- 上下文窗口：200k tokens
- 工具调用：native
- 多模态：text, image, audio

示例请求：
```
[代码示例]
```

来源：https://developers.openai.com/api/docs/models/gpt-5
```

### 场景 4：创建 GitLab 集成插件

**需求**：让 Codex 能与公司 GitLab 交互。

**对话**：
```
你：创建一个 GitLab 集成插件
Codex：[plugin-creator 触发]
     你想要哪些功能？
你：创建 issue、合并请求、查询项目
```

**plugin-creator 生成**：
```
gitlab-integration/
├── .codex-plugin/
│   └── plugin.json
├── skills/
│   ├── gitlab-issue/
│   └── gitlab-merge-request/
├── mcp/
│   └── gitlab-server/
└── scripts/
    └── gitlab-auth.py
```

**用户编辑**：
1. 更新 `plugin.json` 中的 `[TODO: ...]`
2. 实现 MCP 服务器
3. 编写技能

**最终使用**：
```
你：为 bug #123 创建 issue
Codex：[使用 gitlab-issue 技能]
     已创建 issue #456: Fix bug #123
     https://gitlab.company.com/project/issues/456
```

## 技能 vs 插件 vs Hooks

| 特性 | Skills | Plugins | Hooks |
|------|--------|---------|-------|
| 目的 | 注入领域知识 | 扩展 Codex 功能 | 事件驱动自动化 |
| 结构 | SKILL.md + 资源 | plugin.json + 文件夹 | shell 脚本 |
| 触发 | 意图匹配 | 命令或配置 | 事件（PreToolUse 等） |
| 位置 | 技能目录 | 插件目录 | settings.json |
| 优先级 | 上下文注入 | 系统扩展 | 自动化 |

## 本章小结

**一句话记住**：Skills 是 Codex 的"领域专家"系统，50+ 内置技能覆盖开发、内容生成、文档查询等领域，采用三层渐进式加载，高效利用上下文窗口。

**核心要点**：
1. **技能结构**：SKILL.md（必需）+ scripts/references/assets（可选）
2. **触发机制**：基于 description 的意图匹配
3. **渐进式披露**：元数据常驻、内容按需、资源按需
4. **核心技能**：skill-creator、plugin-creator、imagegen、openai-docs、skill-installer
5. **创建流程**：理解 → 规划 → 初始化 → 编辑 → 验证 → 迭代

**下一步**：了解 Hooks 系统如何实现事件驱动的自动化（第十五章）。

---

**系列目录**：
- [第一章：Codex 是什么 —— OpenAI 的本地编码代理](./../01-intro/01-what-is-codex.md)
- [第二章：安装与上手 —— npm/brew/二进制三种方式](./../01-intro/02-installation-setup.md)
- [第三章：认证与配置 —— ChatGPT 账号 vs API Key](./../01-intro/03-authentication.md)
- [第四章：TUI 基础 —— 终端 UI 的交互方式](./../02-core/04-tui-basics.md)
- [第五章：codex exec —— 非交互式编程执行](./../02-core/05-codex-exec.md)
- [第六章：沙箱系统 —— 安全执行命令](./../02-core/06-sandbox.md)
- [第七章：MCP 客户端 —— 连接外部工具](./../03-cli/07-mcp-client.md)
- [第八章：架构概览 —— 100+ Crates 的模块化设计](./08-architecture-overview.md)
- [第九章：TUI 深入 —— Ratatui 应用的构建方式](./09-tui-in-depth.md)
- [第十章：Memories 系统 —— AI 的长期记忆](./10-memories-system.md)
- [第十一章：State 系统 —— SQLite 数据库持久化](./11-state-system.md)
- [第十二章：Tools 系统 —— 从 codex-core 独立出的工具原语](./12-tools-system.md)
- [第十三章：Exec 系统 —— 安全沙箱执行的深层设计](./13-exec-system.md)
- 第十四章：技能系统深入 —— 50+ 内置技能与实战场景 👈 当前位置
- [第十五章：Hooks 系统 —— 事件驱动的自动化](./../05-plugins/15-hooks-system.md) 👉 下一章
- [第十六章：Plugin 系统 —— Codex 的扩展机制](./../05-plugins/16-plugin-system.md)
- [第十七章：开发工作流 —— 如何构建和测试 Codex](./../06-enterprise/17-development-workflow.md)
- [第十八章：配置系统 —— TOML + JSON Schema](./../06-enterprise/18-configuration-system.md)
- [第十九章：安全设计 —— 多层安全防护](./../06-enterprise/19-security.md)
- [第二十章：架构总结 —— 100+ Crates 的设计哲学](./../06-enterprise/20-architecture-summary.md)
