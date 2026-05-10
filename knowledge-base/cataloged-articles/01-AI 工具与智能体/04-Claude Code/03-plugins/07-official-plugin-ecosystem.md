# 第七章：官方插件生态 —— 12 个官方插件全解析与使用指南

你刚装完 Claude Code，输入 `/help` 看到的命令只有寥寥几个。但只要装上插件，你的 Claude Code 就能自动提交代码、审查 PR、检测安全漏洞、甚至自主迭代到任务完成。

12 个官方插件（Anthropic 团队维护）覆盖 git 工作流、安全检查、代码审查、功能开发、钩子创建、插件开发、持续学习等场景。这篇文章逐个介绍：**安装什么、做什么、怎么用、装完后你会看到什么**。

## 生态全景

```
简单
  │
  ├─ 单组件型
  │  ├─ commit-commands      3 个命令
  │  ├─ security-guidance    1 个钩子
  │  ├─ explanatory-output-style  1 个钩子
  │  ├─ learning-output-style     1 个钩子
  │  └─ claude-opus-4-5-migration 1 个技能
  │
  ├─ 技能型
  │  └─ frontend-design      1 个技能
  │
  ├─ 多代理型
  │  ├─ code-review          1 命令 + 5 代理
  │  └─ pr-review-toolkit    1 命令 + 6 代理
  │
  ├─ 全组件型
  │  ├─ feature-dev          1 命令 + 3 代理
  │  ├─ agent-sdk-dev        1 命令 + 2 代理
  │  ├─ ralph-wiggum         2 命令 + 1 钩子
  │  ├─ hookify              4 命令 + 1 代理 + 1 技能 + 1 钩子
  │  └─ plugin-dev           1 命令 + 3 代理 + 7 技能
  │
  ↓
复杂
```

通用安装命令格式：`/plugin install 插件名@claude-plugins-official`

### 配置需求速查

| 插件 | 装完即用？ | 额外配置/前置条件 |
|------|-----------|-----------------|
| commit-commands | ✅ 是 | `/commit-push-pr` 需要 `gh` CLI |
| security-guidance | ✅ 是 | 无 |
| explanatory-output-style | ✅ 是 | 无 |
| learning-output-style | ✅ 是 | 无 |
| claude-opus-4-5-migration | ✅ 是 | 无 |
| frontend-design | ✅ 是 | 无 |
| code-review | ⚠️ 需配置 | 需要 `gh` CLI；`--comment` 需 GitHub MCP |
| pr-review-toolkit | ⚠️ 需配置 | 需要 `gh` CLI |
| feature-dev | ✅ 是 | 首次运行需授权开发权限 |
| hookify | ✅ 是 | 规则文件放在项目 `.claude/` 下 |
| plugin-dev | ✅ 是 | 无 |
| agent-sdk-dev | ⚠️ 需配置 | 需要 Node.js 18+ 或 Python 3.8+ + API Key |
| ralph-wiggum | ✅ 是 | Stop 钩子影响全局退出行为 |

---

## 1. commit-commands —— Git 工作流自动化

**安装**：
```bash
/plugin install commit-commands@claude-plugins-official
```

**做什么**：把你最常做的 git 操作封装成三条命令——提交、推送+PR、清理分支。不再手打 `git add -A && git commit -m "..." && git push`。

**包含命令**：

| 命令 | 做什么 | 权限范围 |
|------|--------|---------|
| `/commit` | 分析 diff → 生成 commit message → 提交 | 只能 `git add/status/commit` |
| `/commit-push-pr` | 提交 → 推送 → 创建 PR | 上述 + `git push` + `gh pr create` |
| `/clean_gone` | 清理已删除远程分支的本地引用 | `git remote prune/branch/worktree` |

**怎么用**：
```
> /commit                                    # 自动分析变更并提交
> /commit fix: resolve login timeout         # 提交时指定消息前缀
> /commit-push-pr                            # 提交 → 推送 → 创建 PR，一步到位
> /clean_gone                                # 清理本地过期分支
```

**装完后你会看到**：输入 `/` 时多出 `commit (commit-commands)`、`commit-push-pr (commit-commands)`、`clean_gone (commit-commands)` 三个命令。

**设计亮点**：
- `!\`git diff HEAD\`` 在执行前自动注入 diff 上下文——AI 看到真实变更才写提交消息
- `allowed-tools` 严格限定：`/commit` 不能 push，防止误操作
- "禁言模式"：AI 只输出工具调用，不输出多余解释

**配置**：无需额外配置。装完直接用。如需 `/commit-push-pr` 创建 PR，确保已安装 GitHub CLI（`gh auth login`）。

**使用示例**：

```bash
# 场景 1：改了几个文件，让 AI 自动分析变更并生成提交消息
> /commit
# → AI 执行 `git diff HEAD`，分析变更内容
# → 自动生成符合 conventional commits 的消息，如 "feat: add user login validation"
# → 执行 git add + git commit

# 场景 2：指定提交类型前缀
> /commit fix: resolve login timeout issue
# → AI 使用你指定的前缀，补充完整消息后提交

# 场景 3：提交 + 推送 + 创建 PR，一步到位
> /commit-push-pr
# → 先 commit（同 /commit）
# → 再 git push
# → 最后 gh pr create（需要 gh CLI 已登录）

# 场景 4：清理本地已失效的远程分支
> /clean_gone
# → 执行 git remote prune origin
# → 列出并删除本地对应的分支引用
```

**适合谁**：所有人。这是最简单也最常用的插件，建议第一个安装。

---

## 2. security-guidance —— 自动安全检查

**安装**：
```bash
/plugin install security-guidance@claude-plugins-official
```

**做什么**：每次 AI 编辑文件时自动检测 9 种安全模式。**安装后无需任何操作**——钩子自动生效。

**检测的安全模式**：

| 模式 | 检测什么 | 典型危险代码 |
|------|---------|-------------|
| 命令注入 | 未净化输入拼接命令 | `os.system(user_input)` |
| XSS | 未转义用户输入 | `innerHTML = userInput` |
| eval 使用 | 动态执行代码 | `eval(user_data)` |
| 硬编码密钥 | 代码中的密钥 | `API_KEY = "sk-..."` |
| SQL 注入 | 字符串拼接查询 | `f"SELECT * FROM {table}"` |
| 路径遍历 | 未净化路径 | `open(user_path)` |
| 危险 HTML | 危险标签 | `<iframe src="...">` |
| pickle 反序列化 | 加载不可信数据 | `pickle.loads(data)` |
| os.system 调用 | 直接系统命令 | `os.system("rm -rf")` |

**怎么用**：装完就行。当 AI 要写入包含安全问题的代码时，你会看到它自动收到提醒并重新考虑。

**装完后你会看到**：输入 `/hooks` 时多出一条 `PreToolUse` 钩子，matcher 为 `Edit|Write|MultiEdit`。

**设计亮点**：
- 用 Command hook（正则匹配）而非 Prompt hook：确定性高、零延迟、零 token 消耗
- **提醒而非阻止**：注入 `systemMessage` 让 AI 自行判断，避免误报阻断工作流

**配置**：无需额外配置。PreToolUse 钩子安装后自动生效，每次 AI 编辑文件（Edit/Write/MultiEdit）时自动检查。

**使用示例**：

> **注意**：security-guidance 是钩子插件，**没有命令**。它会在 AI 写代码时自动触发，无需手动调用。

```bash
# 场景 1：让 AI 写一个接收用户输入的 API，钩子自动检测安全问题
> 帮我写一个 Flask 接口接收用户搜索关键词
# → AI 写出代码
# → security-guidance 钩子自动检测 SQL 拼接风险
# → 注入安全提醒：建议使用参数化查询
# → AI 重新考虑，改用参数化查询

# 场景 2：AI 写了一段执行系统命令的代码
> 用 Python 压缩文件
# → AI 可能写出不安全的命令拼接代码
# → 钩子检测到命令注入风险
# → 注入提醒：建议使用 subprocess + 参数列表
# → AI 改用安全的替代方案

# 场景 3：AI 写了一段硬编码密钥的代码
> 帮我写一个调用第三方 API 的函数
# → AI 可能写成 API_KEY = "sk-xxx"
# → 钩子检测到硬编码密钥模式
# → 注入提醒：应使用环境变量

# 验证钩子是否生效
> /hooks
# → 在 PreToolUse 列表中看到 security-guidance 的钩子
# → matcher: Edit|Write|MultiEdit
```

**适合谁**：所有人，尤其是处理用户输入的项目。

---

## 3. code-review —— 5 代理并行 PR 审查

**安装**：
```bash
/plugin install code-review@claude-plugins-official
```

**做什么**：对 PR 做全面质量审查，5 个代理并行工作，每个代理专注不同维度。

**怎么用**：
```
> /code-review              # 审查当前 PR
> /code-review --comment    # 审查并在 PR 上留下评论
```

**5 个代理各做什么**：

| 代理 | 职责 | 模型 |
|------|------|------|
| pr-history | PR 上下文和历史 | Haiku（快速） |
| code-comments | 代码注释质量 | Sonnet |
| bug-detector | Bug 和逻辑错误 | Opus（深度推理） |
| claude-md-compliance | CLAUDE.md 合规性 | Sonnet |
| historical-context | 历史上下文和回归风险 | Opus |

**核心创新——置信度评分**：每个发现附带 0-1 的置信度，低于 0.5 的自动过滤。低置信度问题还会被第二个 Opus 代理**二次验证**，大幅降低误报率。

**工作流**：
1. Haiku 代理检查 PR 是否需要审查（已关闭、草稿、无需审查则跳过）
2. Sonnet 代理汇总 PR 变更
3. 4 个代理**并行**审查代码
4. 发现的问题经过验证后输出

**装完后你会看到**：输入 `/` 时多出 `code-review (code-review)` 命令。

**配置**：
1. **必须安装 GitHub CLI**：`gh auth login`（用于获取 PR 信息）
2. **使用 `--comment` 参数**：如果想直接在 PR 上留下评论，需要配置 GitHub MCP 服务器（提供 `mcp__github_inline_comment__create_inline_comment` 工具）。不加 `--comment` 则只在终端输出结果，无需 MCP。
3. **权限确认**：首次运行时 Claude 会请求 `gh pr view`、`gh pr diff` 等权限，选择 allow 即可

**使用示例**：

```bash
# 前提：在 git 仓库中，有未合并的 PR

# 场景 1：审查当前分支的 PR（终端输出结果）
> /code-review
# → Haiku 代理检查 PR 状态（是否需要审查）
# → Sonnet 代理汇总变更范围
# → 4 个代理并行审查（bug 检测、注释质量、合规性、回归风险）
# → 输出：带置信度评分的问题列表
#   CRITICAL (0.95): SQL 注入风险 in user_handler.py:42
#   HIGH (0.82): 缺少错误处理 in api.py:18
#   MEDIUM (0.61): 冗余注释 in utils.py:7  ← 低置信度已二次验证

# 场景 2：审查并在 PR 上留下评论（需要 GitHub MCP）
> /code-review --comment
# → 同上审查流程
# → 额外：在 PR 的具体代码行上留下 review 评论

# 场景 3：指定审查某个 PR
> /code-review
# → Claude 会问：要审查哪个 PR？输入 PR 编号
# → 或直接：请审查 PR #42
```

**适合谁**：需要高质量 PR 审查的团队。个人开发者如果 PR 较多也推荐。

---

## 4. pr-review-toolkit —— 按维度精细化审查

**安装**：
```bash
/plugin install pr-review-toolkit@claude-plugins-official
```

**做什么**：和 code-review 不同，这个插件让你**选择审查维度**——只看测试、只看错误处理、或者只看简化机会。

**怎么用**：
```
> /review-pr                  # 全部维度审查
> /review-pr tests            # 只审查测试覆盖和质量
> /review-pr errors           # 只审查错误处理
> /review-pr comments         # 只审查注释质量
> /review-pr types            # 只审查类型设计
> /review-pr code             # 只审查代码质量
> /review-pr simplify         # 只找简化机会
> /review-pr all parallel     # 全维度并行审查
```

**6 个代理**：

| 代理 | 专注什么 |
|------|---------|
| `comment-analyzer` | 注释准确性、文档完整性 |
| `pr-test-analyzer` | 测试行为覆盖、关键缺口 |
| `silent-failure-hunter` | 静默失败、隐藏错误 |
| `type-design-analyzer` | 类型封装、不变量表达 |
| `code-reviewer` | 通用代码质量、CLAUDE.md 合规 |
| `code-simplifier` | 代码简化、重构机会 |

**和 code-review 的区别**：

> **重要**：这两个插件是**独立的**，不是包含关系。你可以根据需要选择安装其中一个或两个都装。

| 维度 | code-review | pr-review-toolkit |
|------|-------------|-------------------|
| **代理数量** | 5 个 | 6 个 |
| **审查方式** | 全量审查，一次跑完所有维度 | 按需选择维度，可单独审查某个方面 |
| **使用场景** | 正式 PR 的全面质量检查 | 迭代开发中的增量审查、专项检查 |
| **命令格式** | `/code-review`<br>`/code-review --comment` | `/review-pr [维度]`<br>如：`/review-pr tests` |
| **是否需要 MCP** | `--comment` 需要 GitHub MCP | 不需要 |
| **置信度评分** | 有（0-1 评分，低置信度二次验证） | 无 |
| **并行执行** | 4 个代理并行审查 | 可选择 `all parallel` 并行执行 |
| **专注维度** | Bug 检测、注释质量、合规性、回归风险 | 测试、错误处理、类型设计、代码简化等 |

**配置**：
1. **必须安装 GitHub CLI**：`gh auth login`（插件使用 `gh pr diff`、`gh pr view` 等命令获取变更信息）
2. **权限确认**：首次运行时 Claude 会请求 `Bash(gh:*)` 和 `Task` 权限，选择 allow 即可
3. 无需 MCP 服务器——pr-review-toolkit 不依赖 GitHub MCP

**使用示例**：

```bash
# 场景 1：只想审查测试覆盖——PR 改了业务逻辑，检查测试是否跟上
> /review-pr tests
# → pr-test-analyzer 代理启动
# → 分析 PR 变更的每个函数/类是否有对应测试
# → 输出：未覆盖的关键路径、测试行为是否正确

# 场景 2：审查错误处理——重构了错误处理逻辑
> /review-pr errors
# → silent-failure-hunter 代理启动
# → 扫描 try/catch 块、fallback 逻辑、错误吞没
# → 输出：静默失败风险、不当降级行为

# 场景 3：只看简化机会——代码膨胀了，找重构点
> /review-pr simplify
# → code-simplifier 代理启动
# → 分析重复代码、过度抽象、冗余条件
# → 输出：具体简化建议（保留功能不变）

# 场景 4：全维度并行审查（时间充裕时）
> /review-pr all parallel
# → 6 个代理全部并行启动
# → 每个维度输出各自的问题列表

# 场景 5：类型设计审查——引入了新的数据模型
> /review-pr types
# → type-design-analyzer 代理启动
# → 评估类型封装性、不变量表达、强制程度
# → 输出：0-10 评分 + 改进建议
```

**适合谁**：需要精细控制审查范围的团队，或只想看特定维度（如安全、测试）的开发者。

---

## 5. feature-dev —— 7 阶段结构化开发

**安装**：
```bash
/plugin install feature-dev@claude-plugins-official
```

**做什么**：把"开发一个功能"这件事变成 7 个阶段，3 个专业代理协作完成。不再是一句"帮我实现 XX"然后祈祷结果。

**怎么用**：
```
> /feature-dev 添加用户登录功能
> /feature-dev 重构数据库连接池
```

**7 个阶段**：

```
/feature-dev <功能描述>
  │
  ├─ Phase 1: Discovery    → 理解需求，确认不明确的地方
  ├─ Phase 2: Exploration  → code-explorer 代理分析代码库（2-3 个并行）
  ├─ Phase 3: Questions    → 列出所有模糊点，等用户回答
  ├─ Phase 4: Architecture → code-architect 代理设计方案（多方案对比）
  ├─ Phase 5: Implement    → 按选定的方案写代码
  ├─ Phase 6: Review       → code-reviewer 代理质量检查（3 个并行）
  └─ Phase 7: Summary      → 文档化成果和后续步骤
```

**核心设计**：
- Phase 3 是**强制步骤**——必须先问清楚再做，避免"做了才发现方向错了"
- Phase 4 提供多方案对比（最小改动 vs 清洁架构 vs 折中），你选一个
- 代理之间**不可见**——结果由主代理汇总，避免锚定效应

**装完后你会看到**：输入 `/` 时多出 `feature-dev (feature-dev)` 命令。

**配置**：
1. **无需额外配置**，装完直接用
2. **首次运行时**：Claude 会请求 Read/Write/Edit/Bash/Grep/Glob/WebSearch 等权限——这些是完整开发能力所需的，选择 allow 即可
3. **Phase 3 会主动问你问题**：这是设计如此，不是 bug——请认真回答模糊点，避免方向偏差

**使用示例**：

```bash
# 场景：开发一个用户认证功能
> /feature-dev 添加用户登录和注册功能，使用 JWT

# Phase 1: Discovery
# → AI：我理解你需要用户认证功能。几个确认点：
#   1. 是否需要 OAuth 第三方登录？
#   2. JWT 的过期时间你有偏好吗？
#   3. 是否需要密码重置功能？

# Phase 2: Exploration（2-3 个代理并行）
# → code-explorer 代理 1：分析现有的用户模型和数据库
# → code-explorer 代理 2：检查现有的中间件和路由结构
# → 汇总：当前代码库的架构和约束

# Phase 3: Questions（强制步骤——必须回答）
# → AI：基于代码库分析，以下是模糊点：
#   1. 现有项目使用 Express 还是 Fastify？
#   2. 数据库用 Prisma 还是 TypeORM？
#   3. 测试框架偏好？
# → 你回答后，AI 才继续

# Phase 4: Architecture
# → code-architect 代理提供 3 个方案：
#   方案 A（最小改动）：在现有路由上添加中间件
#   方案 B（清洁架构）：独立的 auth 模块 + 策略模式
#   方案 C（折中）：扩展现有中间件 + 模块化
# → 你选择一个方案

# Phase 5: Implement
# → AI 按选定的方案写代码

# Phase 6: Review（3 个代理并行）
# → code-reviewer 代理：代码质量
# → security-reviewer 代理：安全漏洞检测
# → tdd-guide 代理：测试覆盖率检查

# Phase 7: Summary
# → 输出：变更摘要、后续步骤、已知局限
```

**适合谁**：开发中大型功能的场景。小 bug 修复不需要这个——直接告诉 AI 修就行。

---

## 6. hookify —— 零代码创建钩子规则

**安装**：
```bash
/plugin install hookify@claude-plugins-official
```

**做什么**：用自然语言描述"不该做什么"，自动生成钩子配置。不用写 Python/Bash 脚本，不用编辑 JSON。

**怎么用**：
```
> /hookify                              # 分析对话历史，识别需要阻止的行为
> /hookify 不要使用 console.log 调试     # 直接指定规则
> /hookify:list                         # 列出所有活跃的钩子规则
> /hookify:configure                    # 配置钩子行为
> /hookify:help                         # 帮助信息
```

**工作原理**：
1. 如果你给了参数（如"不要用 console.log"），直接按你的要求生成规则
2. 如果没给参数，`conversation-analyzer` 代理自动分析对话，找出你反复纠正 AI 的行为
3. 将行为转化为 `.claude/hookify.规则名.local.md` 文件
4. 规则**立即生效**，无需重启

**示例——生成一个阻止危险 rm 的规则**：
```
> /hookify 每次用 rm -rf 之前要提醒我
```

生成的 `.claude/hookify.dangerous-rm.local.md`：
```markdown
---
name: warn-dangerous-rm
enabled: true
event: bash
pattern: rm\s+-rf
action: warn
---

⚠️ **Dangerous rm command detected**
你请求在 rm -rf 之前收到提醒。
请确认路径正确。
```

**4 个 Hook 事件全覆盖**：PreToolUse、PostToolUse、Stop、UserPromptSubmit——hookify 可以在任何事件上创建规则。

**配置**：
1. **无需额外配置**，装完直接用
2. **首次运行 `/hookify`**：会自动加载 `writing-rules` 技能来理解规则文件格式，无需手动操作
3. **规则文件位置**：生成的 `.local.md` 规则文件存放在项目的 `.claude/` 目录下，不是插件目录——确保 `.claude/` 目录存在（`mkdir -p .claude`）
4. **规则立即生效**：不需要重启 Claude Code，写完规则文件后下一次工具调用就会触发

**使用示例**：

```bash
# 场景 1：AI 总是用 console.log 调试，你不想每次手动纠正
> /hookify 不要使用 console.log 调试
# → 生成 .claude/hookify.no-console-log.local.md
# → 从现在起，AI 要写 console.log 时会收到提醒

# 场景 2：AI 总是忘记处理错误
> /hookify 每次写 async 函数都要处理错误
# → 生成规则，AI 写 async 函数时自动检查是否有 try/catch

# 场景 3：让 AI 分析对话历史，自动发现你反复纠正的行为
> /hookify
# → conversation-analyzer 代理启动
# → 分析最近的对话
# → 发现你 3 次纠正 AI "不要修改测试文件"
# → 自动生成 .claude/hookify.no-modify-tests.local.md

# 场景 4：列出所有活跃的规则
> /hookify:list
# → 输出当前所有 hookify 规则及其状态

# 场景 5：配置钩子行为（如修改严格级别）
> /hookify:configure
# → 交互式配置界面

# 场景 6：删除不再需要的规则
> 删除 .claude/hookify.no-console-log.local.md
# → 规则文件删除后，下一次工具调用就不再触发
```

**适合谁**：所有人。尤其是发现自己反复纠正 AI 同一个行为的人——让 hookify 帮你自动化。

---

## 7. plugin-dev —— 用插件开发插件的元工具

**安装**：
```bash
/plugin install plugin-dev@claude-plugins-official
```

**做什么**：你想开发自己的 Claude Code 插件？这个插件就是你的开发工具箱——7 个技能覆盖插件开发全流程，3 个代理辅助验证。

**怎么用**：
```
> /plugin-dev:create-plugin    # 启动 8 阶段引导式工作流
```

**7 个技能**（每个是一份深度参考文档）：

| 技能 | 覆盖什么 |
|------|---------|
| `plugin-structure` | 目录结构、清单配置、组件模式 |
| `command-development` | frontmatter、参数、bash 执行 |
| `agent-development` | 触发机制、系统提示词设计 |
| `skill-development` | SKILL.md、渐进式披露 |
| `hook-development` | hooks.json、可移植路径 |
| `mcp-integration` | 四种传输模式、工具命名 |
| `plugin-settings` | .local.md 配置模式 |

**3 个代理**：

| 代理 | 什么时候用 |
|------|-----------|
| `agent-creator` | 根据需求生成代理配置 |
| `plugin-validator` | 验证插件结构和配置是否正确 |
| `skill-reviewer` | 审查技能质量 |

**配置**：
1. **无需额外配置**，装完直接用
2. **运行 `/plugin-dev:create-plugin`**：启动 8 阶段引导式工作流，会逐步询问你要创建什么类型的插件
3. **7 个技能自动可用**：当 Claude 在开发插件时，会自动参考这些技能中的知识（目录结构、命令格式、钩子配置等）

**使用示例**：

```bash
# 场景 1：从零创建一个新插件
> /plugin-dev:create-plugin
# → 8 阶段引导式工作流启动
# → 阶段 1：你想创建什么类型的插件？（命令型/钩子型/全功能型）
# → 阶段 2：插件名称和描述
# → 阶段 3：需要哪些组件？（命令/代理/技能/钩子）
# → ... 逐步完成
# → 最终生成完整的插件目录结构

# 场景 2：让 AI 直接帮你创建插件（不使用向导）
> 帮我创建一个插件，功能是：每次提交前检查 commit message 是否符合 conventional commits 格式
# → AI 自动参考 plugin-structure、hook-development 等技能
# → 生成 plugin.json + hooks/ 目录 + 相应的钩子脚本

# 场景 3：验证插件结构是否正确
> 验证我的插件 /path/to/my-plugin 结构是否正确
# → plugin-validator 代理启动
# → 检查 plugin.json 格式、目录结构、组件完整性
# → 输出：问题列表 + 修复建议

# 场景 4：审查技能质量
> 审查我插件中的技能文件质量
# → skill-reviewer 代理启动
# → 检查技能描述有效性、知识完整性、触发词准确性
```

**适合谁**：想开发自定义插件的人。这是 12 个插件中最复杂的，也是你开发插件旅程的起点。

---

## 8. frontend-design —— 前端设计指导

**安装**：
```bash
/plugin install frontend-design@claude-plugins-official
```

**做什么**：当检测到前端开发工作时自动注入设计指导。**不需要显式调用**——装完就生效。

**核心原则**：**避免通用 AI 美学**。AI 生成的界面往往千篇一律（默认蓝紫色、均匀间距、无个性）。frontend-design 注入的设计原则追求：
- 强烈的排版对比（字重、大小拉开差距）
- 精心选择的色彩方案，拒绝默认蓝紫
- 有意义的动画和微交互
- 细节打磨（阴影层次、圆角统一、间距节奏）

**怎么用**：装完就行。当你让 AI 开发前端界面时，它会自动应用这些设计原则。

**装完后你会看到**：输入 `/help` 时在技能列表里能看到 `frontend-design` 技能已加载。

**配置**：无需额外配置。技能型插件，Claude 检测到前端开发工作（HTML/CSS/React/Vue 等）时自动注入设计指导。

**使用示例**：

> **注意**：frontend-design 是技能型插件，**没有命令**。它会在 AI 做前端开发时自动触发，无需手动调用。

```bash
# 场景 1：让 AI 创建一个登录页面
> 用 React 创建一个登录页面
# → AI 自动应用 frontend-design 的设计原则
# → 不会用默认蓝紫色，而是精心选择色彩
# → 字体大小有明显层级（标题 vs 正文拉开差距）
# → 添加微交互（按钮 hover、输入框 focus 动画）
# → 统一圆角和间距节奏

# 场景 2：对 AI 生成的界面不满意
> 这个界面太普通了，重新设计
# → frontend-design 的知识指导 AI：
#   - 加强排版对比
#   - 添加深度感（阴影层次）
#   - 使用独特的调色板
#   - 添加有意义的动画

# 不需要手动触发——只要你在做前端工作，技能就自动注入
```

**适合谁**：任何做前端开发的场景。尤其是对 AI 生成界面的"千篇一律感"不满意的人。

---

## 9. agent-sdk-dev —— Agent SDK 项目脚手架

**安装**：
```bash
/plugin install agent-sdk-dev@claude-plugins-official
```

**做什么**：帮你创建和验证 Claude Agent SDK 项目。交互式引导，从零到一个可运行的项目。

**怎么用**：
```
> /new-sdk-app              # 交互式创建新 Agent SDK 项目
> /new-sdk-app my-agent     # 指定项目名创建
```

**工作流**：
1. 逐个询问：语言（TypeScript/Python）→ 项目名 → Agent 类型 → 起点选择 → 工具偏好
2. 检查最新 SDK 版本并安装
3. 创建项目文件、配置、示例代码
4. 验证代码能编译/运行
5. 启动验证代理检查 SDK 使用是否正确

**包含代理**：

| 代理 | 职责 |
|------|------|
| `agent-sdk-verifier-py` | 验证 Python SDK 应用 |
| `agent-sdk-verifier-ts` | 验证 TypeScript SDK 应用 |

**配置**：
1. **确保有 Node.js 18+ 或 Python 3.8+**：SDK 需要这些运行时
2. **需要 ANTHROPIC_API_KEY**：Agent SDK 调用 Claude API 需要 API Key，在 `.env` 文件中设置
3. **首次运行 `/new-sdk-app`**：会逐个询问你的偏好（语言、项目名、Agent 类型等），一次只问一个问题

**使用示例**：

```bash
# 场景 1：创建一个 Python Agent SDK 项目
> /new-sdk-app my-customer-support-bot
# → AI 询问：使用什么语言？ → Python
# → AI 询问：Agent 类型？ → Customer Support
# → AI 询问：需要哪些工具？ → web search, knowledge base
# → AI 检查最新 SDK 版本并安装：pip install anthropic
# → 创建项目结构：
#   my-customer-support-bot/
#   ├── .env              # ANTHROPIC_API_KEY
#   ├── agent.py          # 主 Agent 逻辑
#   ├── tools/            # 工具定义
#   └── requirements.txt
# → agent-sdk-verifier-py 代理验证代码可运行

# 场景 2：创建一个 TypeScript Agent SDK 项目
> /new-sdk-app
# → AI 询问：使用什么语言？ → TypeScript
# → AI 询问：项目名？ → data-analyzer
# → AI 安装：npm install @anthropic-ai/sdk
# → 创建项目 + 验证编译通过
# → agent-sdk-verifier-ts 代理检查 SDK 用法正确

# 注意：需要 ANTHROPIC_API_KEY 才能运行创建的 Agent
# 在 .env 文件中设置：
# ANTHROPIC_API_KEY=sk-ant-xxx
```

**适合谁**：想用 Claude Agent SDK 构建 AI Agent 的开发者。

---

## 10. ralph-loop —— 自主迭代循环

**安装**：
```bash
/plugin install ralph-loop@claude-plugins-official
```

> **为什么叫 Ralph Wiggum？**
>
> 这个插件的名字来源于《辛普森一家》中的角色 Ralph Wiggum。Geoffrey Huntley 将这种持续迭代的 AI 开发方法命名为 "Ralph"，寓意着"尽管遇到挫折，也要坚持不懈地尝试"。
>
> Ralph 的核心理念是：**"Ralph is a Bash loop"**——一个简单的 `while true` 循环，反复将同一个 prompt 喂给 AI，让它不断改进自己的工作，直到真正完成。
>
> - **Marketplace 插件名**：`ralph-loop`
> - **源代码目录名**：`ralph-wiggum`（保留了这个有趣的名字）
> - **可用命令**：`/ralph-loop` 和 `/cancel-ralph`
> - **插件页面**：https://claude.com/plugins/ralph-loop

**做什么**：让 Claude 在同一个任务上反复迭代，直到真正完成。核心机制是 Stop 钩子拦截退出信号——AI 觉得做完了？钩子说"再检查一遍"。

**怎么用**：
```
> /ralph-loop 重构认证模块，确保所有测试通过   # 启动迭代循环
> /cancel-ralph                                # 手动终止
```

**工作原理**：
1. `/ralph-loop` 执行 setup 脚本，注册 Stop 钩子
2. AI 开始工作，完成后准备退出
3. Stop 钩子拦截：检查任务是否真正完成
4. 未完成 → 把**同一个 prompt** 重新喂给 AI，AI 看到之前的工作成果继续迭代
5. 完成或 `/cancel-ralph` → 停止

**关键机制——completion-promise**：可以设定完成条件，AI 只能在条件**真正满足**时才能输出完成信号。防止 AI 为了"逃出循环"而虚假声明完成。

```
> /ralph-loop 修复所有 TypeScript 编译错误 --completion-promise "tsc --noEmit 返回 0"
```

**配置**：
1. **无需额外配置**，装完直接用
2. **Bash 权限**：首次运行 `/ralph-loop` 时，Claude 会请求执行 setup 脚本的权限，选择 allow
3. **退出机制**：循环只会因以下条件停止——任务完成（创建 `.claude/ralph-wiggum-done` 标志文件）、你手动 `/cancel-ralph`、或达到最大迭代次数（通过 `--max-iterations N` 设定）
4. **注意**：ralph-wiggum 的 Stop 钩子会影响所有会话退出行为——即使不是用 `/ralph-loop` 启动的会话，Stop 钩子也会检查是否应该继续。如果遇到"无法正常退出"的情况，检查是否安装了此插件

**使用示例**：

```bash
# 场景 1：修复所有 TypeScript 编译错误，完成后自动停止
> /ralph-loop 修复所有 TypeScript 编译错误 --completion-promise "tsc --noEmit 返回 0"
# → AI 开始修复错误
# → 每次修完一轮，Stop 钩子检查 tsc --noEmit 是否返回 0
# → 如果还有错误，AI 继续下一轮
# → 直到 tsc --noEmit 真正成功，循环结束

# 场景 2：重构模块直到所有测试通过
> /ralph-loop 重构 auth 模块，确保所有测试通过
# → AI 开始重构
# → 每轮迭代后检查测试结果
# → 测试失败 → 继续
# → 测试通过 → 停止

# 场景 3：限制最大迭代次数
> /ralph-loop 修复所有 lint 警告 --max-iterations 5
# → 最多迭代 5 轮
# → 5 轮后仍有警告 → 自动停止（避免无限循环）

# 手动终止
> /cancel-ralph
# → 立即停止当前循环

# 注意：completion-promise 是防止 AI "虚假声明完成"的关键机制
# AI 不能只是说"我修好了"，必须通过外部命令验证
```

**适合谁**：复杂任务需要多轮迭代才能完成的场景。简单任务不需要——直接做就行。

---

## 11. claude-opus-4-5-migration —— 模型迁移助手

**安装**：
```bash
/plugin install claude-opus-4-5-migration@claude-plugins-official
```

**做什么**：帮你把代码从旧模型（Sonnet 4.x、Opus 4.1）迁移到 Opus 4.5。自动替换模型字符串、更新 beta headers、调整 prompt。

**怎么用**：技能型插件，无需手动触发。当你让 AI 处理模型相关代码时，它会自动使用迁移知识。

**覆盖的迁移内容**：
- 模型字符串替换（如 `claude-3-5-sonnet` → `claude-opus-4-5`）
- Beta headers 更新
- Prompt 调整以适配新模型特性

**配置**：无需额外配置。技能型插件，当你让 AI 处理模型字符串、API 调用相关代码时自动注入迁移知识。

**使用示例**：

> **注意**：claude-opus-4-5-migration 是技能型插件，**没有命令**。它会在 AI 处理模型相关代码时自动触发，无需手动调用。

```bash
# 场景 1：更新模型字符串
> 把这段代码的模型从 claude-3-5-sonnet 更新到最新版
# → AI 自动参考 claude-opus-4-5-migration 技能
# → 将 claude-3-5-sonnet 替换为 claude-opus-4-5（或当前最新模型 ID）
# → 同时更新 beta headers（如需要）

# 场景 2：迁移 API 调用
> 帮我迁移这个项目到最新的 Claude 模型
# → AI 扫描代码中所有模型字符串引用
# → 逐一替换 + 更新相关配置
# → 提示可能需要调整的 prompt（不同模型特性不同）

# 不需要手动触发——只要你在处理模型相关代码，技能就自动注入
```

> **⚠️ 重要提示：不适用于第三方模型**
>
> 此插件**仅适用于 Anthropic Claude 模型**之间的迁移（Sonnet 4.x、Opus 4.1 → Opus 4.5）。
>
> 如果你的项目使用第三方模型（如 OpenAI GPT、Google Gemini、本地模型等），此插件**不会生效**，原因包括：
>
> - 第三方模型没有 "Opus 4.5" 这个概念
> - API 格式、头部参数、模型标识符完全不同
> - 迁移逻辑基于 Claude 模型的特性变化
>
> 对于第三方模型的版本升级，请查阅对应提供商的官方迁移文档。

**适合谁**：正在从旧模型迁移到 Opus 4.5 的项目。

---

## 12. explanatory-output-style & learning-output-style —— 输出风格定制

**安装**：
```bash
/plugin install explanatory-output-style@claude-plugins-official
/plugin install learning-output-style@claude-plugins-official
```

**做什么**：两个插件改变 AI 的输出风格。都是 SessionStart 钩子，**装完即生效，无需手动触发**。

| 插件 | 效果 | 适合谁 |
|------|------|--------|
| `explanatory-output-style` | AI 在实现时解释**为什么**选择这种方式——不只是写代码，还教你设计决策 | 想在开发中学习的开发者 |
| `learning-output-style` | 在关键决策点要求你**写 5-10 行代码**，同时提供教育性洞察——不只是看 AI 写，还要自己动手 | 正在学习编程或新框架的人 |

**配置**：
1. **无需额外配置**——两者都是 SessionStart 钩子，安装后自动在下一次会话生效
2. **不推荐同时安装**——风格会冲突，选择一个即可
3. **卸载方式**：`/plugin uninstall explanatory-output-style@claude-plugins-official` 或 `/plugin uninstall learning-output-style@claude-plugins-official`

**使用示例**：

> **注意**：这两个插件都是 SessionStart 钩子，**没有命令**。它们会在每次会话开始时自动生效，无需手动触发。

```bash
# ========== explanatory-output-style ==========

# 安装后，AI 的输出风格变为"教学式"
> 帮我实现一个 LRU 缓存
# → AI 不仅写代码，还解释设计决策：
#   ★ Insight ─────────────────────────────────────
#   使用双向链表 + 哈希表实现 O(1) 的 get/put
#   为什么不用单向链表？删除节点需要 O(n) 查找前驱
#   ─────────────────────────────────────────────────
# → 写代码
# → 再解释为什么选择这种实现方式

# ========== learning-output-style ==========

# 安装后，AI 会在关键点让你动手
> 帮我实现一个 LRU 缓存
# → AI 先解释核心概念
# → 然后说：现在请你写 5-10 行代码，实现 get 方法的基本逻辑
# → 你写完后，AI 审查你的代码
# → AI 提供改进建议，同时解释为什么
# → 逐步引导你完成整个实现

# ========== 两者对比 ==========
# explanatory: AI 讲，你听 → 学得快，但动手少
# learning:    AI 引导，你写 → 学得深，但耗时多
# 不推荐同时安装——风格会冲突
```

**两者区别**：explanatory 让 AI 多说话；learning 让你多动手。不推荐同时安装——风格会冲突。

---

## 安装方式

### 方式 1：从 Marketplace 安装（推荐）

在 Claude Code 中直接使用 `/plugin install` 命令：

```bash
# 安装单个插件
/plugin install commit-commands@claude-plugins-official

# 批量安装（逐个执行）
/plugin install commit-commands@claude-plugins-official
/plugin install security-guidance@claude-plugins-official
/plugin install hookify@claude-plugins-official
/plugin install code-review@claude-plugins-official
/plugin install pr-review-toolkit@claude-plugins-official
/plugin install feature-dev@claude-plugins-official
/plugin install plugin-dev@claude-plugins-official
/plugin install agent-sdk-dev@claude-plugins-official
/plugin install ralph-wiggum@claude-plugins-official
/plugin install claude-opus-4-5-migration@claude-plugins-official
/plugin install explanatory-output-style@claude-plugins-official
/plugin install learning-output-style@claude-plugins-official
/plugin install frontend-design@claude-plugins-official

```

### 方式 2：通过 settings.json 配置

在 `~/.claude/settings.json` 中添加插件配置：

```json
{
  "enabledPlugins": {
    "commit-commands@claude-plugins-official": true,
    "security-guidance@claude-plugins-official": true,
    "code-review@claude-plugins-official": true,
    "pr-review-toolkit@claude-plugins-official": true,
    "feature-dev@claude-plugins-official": true,
    "hookify@claude-plugins-official": true,
    "plugin-dev@claude-plugins-official": true,
    "agent-sdk-dev@claude-plugins-official": true,
    "ralph-wiggum@claude-plugins-official": true,
    "claude-opus-4-5-migration@claude-plugins-official": true,
    "explanatory-output-style@claude-plugins-official": true,
    "learning-output-style@claude-plugins-official": true,
    "frontend-design@claude-plugins-official": true
  }
}
```

### 方式 3：本地开发安装

如果你有插件的本地副本：

```bash
# 指定插件目录
claude --plugin-dir /path/to/plugin

# 或在 settings.json 中配置
{
  "pluginDirectories": [
    "/path/to/plugin1",
    "/path/to/plugin2"
  ]
}
```

### 验证安装

```bash
/help    # 查看新注册的命令
/hooks   # 查看钩子是否加载
/mcp     # 查看 MCP 服务器状态
/plugin list  # 列出已安装的插件
```

### 卸载插件

```bash
/plugin uninstall commit-commands@claude-plugins-official
```

---

## 推荐组合

### 个人开发者（起步配置）

```
commit-commands       # Git 工作流 → 每天都用
security-guidance     # 自动安全检查 → 装完不管
feature-dev           # 结构化开发 → 做功能时用
```

### 团队项目

```
commit-commands       # Git 工作流
security-guidance     # 安全防护
code-review           # PR 审查
hookify               # 团队规范自动化
```

### 插件开发者

```
plugin-dev            # 插件开发元工具
hookify               # 快速创建规则
commit-commands       # Git 工作流
```

### 安全敏感项目

```
security-guidance     # 实时安全检查
pr-review-toolkit     # 深度审查（按维度选择）
commit-commands       # Git 工作流
hookify               # 自定义安全规则
```

---

## 本章小结

**一句话记住**：12 个官方插件覆盖了 git 工作流、安全检查、代码审查、功能开发、钩子创建、插件开发、持续学习七大场景。从 `commit-commands` 开始装，它是最简单也最常用的。

**决策规则**：
- 每天用 git → `commit-commands`
- 写了用户输入相关代码 → `security-guidance`
- 团队有 PR 审查流程 → `code-review`
- 要开发完整功能 → `feature-dev`
- 发现自己反复纠正 AI → `hookify`
- 要开发自己的插件 → `plugin-dev`

**最容易踩的坑**：装了所有插件全开，结果 `/` 列出一大堆命令反而不知道用哪个——建议先装 `commit-commands` + `security-guidance` 两个，用熟了再加。

**现在就试**：装完 `commit-commands` 后，做一次 `git commit` 改动，然后输入 `/commit`，感受自动化工作流。

---

## 配置指南

### GitHub CLI 配置（用于 commit-commands、code-review、pr-review-toolkit）

```bash
# 安装 GitHub CLI
# macOS
brew install gh

# Linux
sudo apt install gh  # Ubuntu/Debian
sudo yum install gh  # CentOS/RHEL

# Windows (使用 winget)
winget install --id GitHub.cli

# 登录 GitHub
gh auth login

# 验证登录
gh auth status
```

### GitHub MCP 服务器配置（用于 code-review --comment 功能）

```bash
# 安装 GitHub MCP 服务器
npm install -g @modelcontextprotocol/server-github

# 在 ~/.claude/settings.json 中添加 MCP 配置
cat >> ~/.claude/settings.json << 'EOF'
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "your_github_token_here"
      }
    }
  }
}
EOF

# 创建 GitHub Personal Access Token
# 访问 https://github.com/settings/tokens
# 需要的权限：repo, read:org, read:user
```

### Node.js 配置（用于 agent-sdk-dev）

```bash
# 安装 Node.js 18+ (使用 nvm)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc  # 或 source ~/.zshrc
nvm install 18
nvm use 18

# 验证安装
node --version  # 应该 >= 18.0.0
npm --version
```

### Python 配置（用于 agent-sdk-dev）

```bash
# 安装 Python 3.8+
# macOS
brew install python@3.11

# Linux
sudo apt install python3.11 python3.11-venv  # Ubuntu/Debian
sudo yum install python3.11  # CentOS/RHEL

# 验证安装
python3 --version  # 应该 >= 3.8.0
```

### Anthropic API Key 配置（用于 agent-sdk-dev）

```bash
# 在项目目录创建 .env 文件
cat > .env << 'EOF'
ANTHROPIC_API_KEY=your_api_key_here
EOF

# 或在 ~/.claude/settings.json 中配置
cat >> ~/.claude/settings.json << 'EOF'
{
  "env": {
    "ANTHROPIC_API_KEY": "your_api_key_here"
  }
}
EOF

# 获取 API Key
# 访问 https://console.anthropic.com/settings/keys
```

### Hookify 规则目录配置

```bash
# 在项目中创建 .claude 目录
mkdir -p .claude

# 验证目录权限
ls -la .claude
```

### 完整配置检查脚本

```bash
#!/bin/bash

echo "=== Claude Code 插件配置检查 ==="

# 检查 GitHub CLI
if command -v gh &> /dev/null; then
    echo "✅ GitHub CLI 已安装: $(gh --version)"
    gh auth status 2>&1 | grep -q "Logged in" && echo "✅ GitHub CLI 已登录" || echo "⚠️  GitHub CLI 未登录，请运行: gh auth login"
else
    echo "❌ GitHub CLI 未安装，请运行: brew install gh"
fi

# 检查 Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -ge 18 ]; then
        echo "✅ Node.js 已安装: $(node --version)"
    else
        echo "⚠️  Node.js 版本过低 (需要 18+): $(node --version)"
    fi
else
    echo "❌ Node.js 未安装，agent-sdk-dev 需要 Node.js 18+"
fi

# 检查 Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    echo "✅ Python 已安装: $(python3 --version)"
else
    echo "❌ Python 未安装，agent-sdk-dev 需要 Python 3.8+"
fi

# 检查 API Key
if [ -f .env ] && grep -q "ANTHROPIC_API_KEY" .env; then
    echo "✅ ANTHROPIC_API_KEY 已配置"
elif grep -q "ANTHROPIC_API_KEY" ~/.claude/settings.json 2>/dev/null; then
    echo "✅ ANTHROPIC_API_KEY 已配置"
else
    echo "⚠️  ANTHROPIC_API_KEY 未配置，agent-sdk-dev 需要"
fi

# 检查 .claude 目录
if [ -d .claude ]; then
    echo "✅ .claude 目录已存在"
else
    echo "⚠️  .claude 目录不存在，hookify 需要: mkdir -p .claude"
fi

echo "=== 检查完成 ==="
```

---

**相关章节**：
- [第八章：插件架构 —— 目录结构、自动发现与清单](./08-plugin-architecture.md)
- [第九章：插件命令开发 —— frontmatter、动态参数、bash 执行](./09-plugin-commands.md)
- [第十五章：社区优秀插件 —— everything-claude-code 与选择方法](./15-community-plugins.md)
- [第二十三章：Marketplace —— 插件发布与分发](./../05-enterprise/24-marketplace.md)
