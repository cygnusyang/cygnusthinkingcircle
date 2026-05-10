# 第十五章：社区优秀插件 —— everything-claude-code 与选择方法

官方插件适合做稳定基线；社区插件适合探索更激进、更完整、更贴近日常开发的工作流。两者不是替代关系：官方插件负责可信的基础能力，社区插件负责把这些能力组合成更大的生产力系统。

这一章先用 `everything-claude-code` 作为代表案例，再给出选择社区插件时应该检查的维度。

## 为什么单独讲社区插件？

社区插件和官方插件的风险边界不同。

官方插件通常更克制：每个插件解决一个清晰问题，例如 git 提交、安全提醒、PR 审查、功能开发、插件开发。

社区插件往往更大胆：一个插件可能同时包含 commands、agents、skills、hooks、MCP 配置和本地自动化脚本。能力更完整，安装后对 Claude Code 行为的影响也更大。

所以社区插件不应该塞在官方插件清单里一笔带过。它们需要单独评估：

| 评估项 | 要看什么 |
|--------|----------|
| 维护者 | 谁维护、是否持续更新、是否有清晰 README |
| 组件范围 | 包含 commands、agents、skills、hooks、MCP 中哪些部分 |
| 权限边界 | 是否会执行 shell、改文件、访问网络、调用 MCP |
| 命令冲突 | 是否和官方插件或本地命令重名 |
| 可关闭性 | 是否能按需禁用高风险 hooks 或可选能力 |
| 团队可解释性 | 团队成员能不能理解它为什么触发、触发后做了什么 |

## everything-claude-code：社区巨星全功能插件

**安装**：

```bash
/plugin install everything-claude-code@everything-claude-code
```

**做什么**：这是 Anthropic 黑客松获奖者 Affaan Mustafa 历时 10 个月打磨的社区插件，覆盖 Claude Code 的每一个组件：28 个代理、136 个技能、59 个命令、20+ 个钩子。它不是“一个小插件”，而是一整套开发工作流系统。

**为什么叫 everything**：因为它几乎包含了日常开发中需要的完整链路：规划、TDD、代码审查、构建修复、文档更新、会话管理、持续学习、质量门禁。

## 28 个代理

按功能分为 5 大类。

### 架构与规划

| 代理 | 职责 |
|------|------|
| `planner` | 实现计划、需求分析、风险识别 |
| `architect` | 系统设计、架构决策 |
| `doc-updater` | 文档更新、codemap 生成 |

### 代码审查

| 代理 | 语言 | 专注什么 |
|------|------|---------|
| `typescript-reviewer` | TypeScript/JS | 类型安全、异步正确性、Node 安全 |
| `python-reviewer` | Python | PEP 8、类型提示、安全 |
| `go-reviewer` | Go | 惯用模式、并发安全 |
| `rust-reviewer` | Rust | 所有权、生命周期、unsafe |
| `java-reviewer` | Java/Spring | 分层架构、JPA 模式 |
| `kotlin-reviewer` | Kotlin/Android | 空安全、协程、Clean Architecture |
| `cpp-reviewer` | C++ | 内存安全、现代惯用法 |
| `flutter-reviewer` | Flutter/Dart | Widget 最佳实践、状态管理 |
| `database-reviewer` | PostgreSQL | 查询优化、Schema 设计 |
| `security-reviewer` | 全语言 | OWASP Top 10、漏洞检测 |
| `code-reviewer` | 通用 | 代码质量、可维护性 |

### 构建修复

| 代理 | 修复什么 |
|------|---------|
| `build-error-resolver` | 自动检测语言并修复构建错误 |
| `go-build-resolver` | Go 构建、go vet |
| `rust-build-resolver` | Rust cargo build、借用检查 |
| `java-build-resolver` | Java/Maven/Gradle |
| `kotlin-build-resolver` | Kotlin/Gradle |
| `cpp-build-resolver` | C++ CMake、链接器 |
| `pytorch-build-resolver` | PyTorch CUDA、张量形状 |

### 测试与质量

| 代理 | 职责 |
|------|------|
| `tdd-guide` | 测试驱动开发：写测试、实现、重构 |
| `e2e-runner` | Playwright 端到端测试 |
| `refactor-cleaner` | 死代码清理、重复代码合并 |
| `harness-optimizer` | 分析并优化 harness 配置 |

### 运维与自动化

| 代理 | 职责 |
|------|------|
| `loop-operator` | 操作自主代理循环、安全干预 |
| `chief-of-staff` | 多渠道消息分诊 |
| `docs-lookup` | Context7 文档查询 |

## 59 个命令

最常用的是下面几类。

### 核心工作流

| 命令 | 做什么 | 使用示例 |
|------|--------|---------|
| `/plan` | 需求分析、风险评估、步骤计划，等你确认才动手 | `/plan 重构认证模块` |
| `/tdd` | 强制 TDD 流程：写失败测试、实现、验证覆盖率 | `/tdd` |
| `/code-review` | 全量代码质量审查 | `/code-review` |
| `/build-fix` | 自动检测语言并修复构建错误 | `/build-fix` |
| `/verify` | 完整验证循环：build、lint、test、type-check | `/verify` |

### 语言专属审查与构建

| 命令 | 语言 |
|------|------|
| `/python-review`、`/go-review`、`/rust-review`、`/kotlin-review`、`/cpp-review` | 代码审查 |
| `/go-build`、`/rust-build`、`/kotlin-build`、`/cpp-build`、`/gradle-build` | 构建修复 |
| `/go-test`、`/rust-test`、`/kotlin-test`、`/cpp-test` | TDD 测试 |

### 会话管理

| 命令 | 做什么 |
|------|--------|
| `/save-session` | 保存当前会话状态 |
| `/resume-session` | 恢复最近保存的会话 |
| `/sessions` | 浏览、搜索会话历史 |
| `/checkpoint` | 标记检查点 |
| `/aside` | 快速回答副问题，不丢失当前任务上下文 |
| `/context-budget` | 分析上下文窗口使用量 |

### 学习与进化

| 命令 | 做什么 |
|------|--------|
| `/learn` | 从当前会话提取可复用模式 |
| `/learn-eval` | 提取模式并自评质量 |
| `/evolve` | 分析学到的模式，建议进化方向 |
| `/instinct-status` | 显示项目级和全局级本能 |
| `/skill-create` | 分析 git 历史，生成可复用技能 |
| `/rules-distill` | 扫描技能，提取原则，蒸馏成规则 |

## 20+ 个钩子

钩子系统覆盖 Claude Code 的完整生命周期。

| 事件 | 钩子 | 做什么 |
|------|------|--------|
| PreToolUse (Bash) | `block-no-verify` | 阻止 `--no-verify` 等 git 钩子绕过 |
| PreToolUse (Bash) | `auto-tmux-dev` | 自动在 tmux 中启动开发服务器 |
| PreToolUse (Bash) | `git-push-reminder` | git push 前提醒检查变更 |
| PreToolUse (Bash) | `commit-quality` | 提交前检查 lint、提交消息、console.log、密钥 |
| PreToolUse (Edit\|Write) | `suggest-compact` | 在逻辑间隔建议手动压缩 |
| PreToolUse (Write\|Edit\|MultiEdit) | `config-protection` | 阻止修改 linter/formatter 配置 |
| PreToolUse (*) | `continuous-learning` | 异步捕获工具使用观察，持续学习 |
| PreToolUse (*) | `mcp-health-check` | 检查 MCP 服务器健康状态 |
| PostToolUse (Bash) | `pr-created` | PR 创建后输出 URL 和审查命令 |
| PostToolUse (Edit) | `format` | 编辑后自动格式化 JS/TS |
| PostToolUse (Edit) | `typecheck` | 编辑 `.ts`/`.tsx` 后运行 TypeScript 检查 |
| PostToolUse (Edit\|Write) | `quality-gate` | 文件编辑后运行质量门禁 |
| Stop | `check-console-log` | 响应结束后检查修改文件中的 console.log |
| Stop | `session-end` | 持久化会话状态 |
| Stop | `evaluate-session` | 评估会话可提取的模式 |
| Stop | `cost-tracker` | 追踪 token 和成本指标 |
| Stop | `desktop-notify` | 任务完成时推送桌面通知 |
| SessionStart | `session-start` | 加载上次上下文，检测包管理器 |
| SessionEnd | `session-end-marker` | 会话结束生命周期标记 |

## 136 个技能

技能是 Claude 自动参考的领域知识库。

| 类别 | 数量 | 典型技能 |
|------|------|---------|
| 语言模式 | 30+ | `python-patterns`、`golang-patterns`、`rust-patterns`、`kotlin-patterns`、`swiftui-patterns` |
| 测试 | 15+ | `python-testing`、`golang-testing`、`rust-testing`、`cpp-testing`、`kotlin-testing` |
| 框架 | 20+ | `django-patterns`、`springboot-patterns`、`laravel-patterns`、`nextjs-turbopack`、`nuxt4-patterns` |
| 安全 | 10+ | `django-security`、`laravel-security`、`springboot-security`、`perl-security` |
| 基础设施 | 10+ | `docker-patterns`、`deployment-patterns`、`mcp-server-patterns` |
| 行业垂直 | 15+ | `healthcare-emr-patterns`、`healthcare-phi-compliance`、`logistics-exception-management` |
| 开发工作流 | 10+ | `git-workflow`、`tdd-workflow`、`agentic-engineering`、`ai-first-engineering` |
| 其他 | 25+ | `article-writing`、`deep-research`、`market-research`、`video-editing`、`visa-doc-translate` |

## 配置与启用

基础功能装完即用：代理、命令、技能会自动加载。高级能力可以通过环境变量开启。

| 环境变量 | 作用 | 默认 |
|---------|------|------|
| `ECC_ENABLE_INSAITS` | 启用 AI 安全监控，需要 `pip install insa-its` | 未启用 |
| `ECC_GOVERNANCE_CAPTURE` | 捕获治理事件，例如密钥泄露、策略违规 | 未启用 |
| `ECC_FLAGS` | 控制钩子严格级别：`minimal`、`standard`、`strict` | `standard,strict` |

```json
{
  "env": {
    "ECC_ENABLE_INSAITS": "1",
    "ECC_GOVERNANCE_CAPTURE": "1",
    "ECC_FLAGS": "standard,strict"
  }
}
```

`minimal` 只启用核心功能，例如安全检查和基础格式化；`standard` 加入提交质量检查、git push 提醒、配置保护；`strict` 再加入 console.log 检测、TypeScript 检查、桌面通知。

## 使用示例

```text
> /plan 重构认证模块，从 JWT 迁移到 session
# 输出需求理解、风险评估、实现步骤，等你确认

> /tdd
# 先写失败测试，再实现，最后验证覆盖率

> /code-review
# 分析最近代码变更，输出 CRITICAL/HIGH/MEDIUM/LOW 问题

> /build-fix
# 检测项目语言，自动修复编译或构建错误

> /save-session
# 状态保存到 ~/.claude/session-data/

> /resume-session
# 加载上次上下文，从断点继续

> /aside React useEffect 的 cleanup 函数什么时候执行？
# 回答副问题后继续当前任务
```

## 和官方插件的关系

`everything-claude-code` 可以和官方插件同时安装，但要注意命令重名。

| 组合方式 | 适合谁 | 注意点 |
|----------|--------|--------|
| 只装官方插件 | 团队基线、低风险环境 | 能力更克制，组合更可控 |
| 只装 `everything-claude-code` | 想要一套完整个人工作流 | 命令和钩子很多，需要理解触发边界 |
| 官方插件 + `everything-claude-code` | 熟悉 Claude Code 插件机制的人 | `/code-review` 等命令可能冲突 |

建议从一个社区插件开始，不要同时安装多个“全家桶”插件。先观察 `/`、`/hooks`、`/mcp` 里新增了什么，再决定是否保留。

## 社区插件选择清单

安装社区插件前，至少做一遍这几个检查：

1. 看 README：是否写清楚安装方式、包含组件、权限需求、卸载方法。
2. 看 hooks：是否有 PreToolUse、PostToolUse、Stop 这类自动触发逻辑。
3. 看 commands：是否和已有命令重名，尤其是 `/code-review`、`/commit`、`/test` 这类常见名称。
4. 看 MCP：是否会启用网络搜索、浏览器、GitHub、数据库等外部能力。
5. 看本地脚本：是否会执行 shell、改 git 状态、写入配置文件。
6. 先在个人项目试用，再推广到团队项目。

## 本章小结

社区插件的价值不在于“更多命令”，而在于把 Claude Code 的 commands、agents、skills、hooks、MCP 组合成完整工作流。`everything-claude-code` 是典型代表：能力覆盖面极广，适合个人开发者快速获得一套完整生产力系统。

但社区插件越强，越要重视权限边界和命令冲突。官方插件适合做稳定基线；社区插件适合在理解风险后逐步引入。

---

**相关章节**：
- [第七章：官方插件生态 —— 12 个官方插件全解析与使用指南](./07-official-plugin-ecosystem.md)
- [第八章：插件架构 —— 目录结构、自动发现与清单](./08-plugin-architecture.md)
- [第十四章：插件配置 —— .local.md 模式与 YAML frontmatter](./14-plugin-settings.md)
- [第二十三章：Marketplace —— 插件发布与分发](./../05-enterprise/24-marketplace.md)
