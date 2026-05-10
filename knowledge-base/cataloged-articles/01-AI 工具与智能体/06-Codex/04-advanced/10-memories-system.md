# 第十章：Memories 系统 —— AI 的长期记忆

上周你用 Codex 重构了整个 auth 模块，今天你又要改类似的逻辑。你不记得上次用的具体方案了，但 Codex 记得。这就是 Memories 系统的价值。

Codex 的 Memories 系统允许 AI 从过去的对话中学习，形成长期记忆。这是一个非常精巧的两阶段流水线设计。

## Memories Crates 结构

**位置**：`source/codex/codex-rs/memories/`

```
memories/
├── README.md              # 设计文档（必读！）
├── read/                  # 读路径
│   └── templates/
│       └── memories/
│           └── read_path.md
└── write/                 # 写路径
    └── templates/
        └── memories/
            ├── stage_one_system.md
            ├── stage_one_input.md
            └── consolidation.md
```

**注意**：Phase 1 和 Phase 2 的运行时编排仍在 `codex-core/src/memories/` 中。

## 什么时候触发

记忆流水线在根会话启动时触发，但需要满足：
- 会话不是临时的（ephemeral）
- 记忆功能已启用
- 会话不是子代理会话
- 状态数据库可用

`★ Insight ─────────────────────────────────────`
**记忆触发的精巧设计**
排除子代理会话和临时会话是关键决策。子代理的任务通常是临时性的、特定目标的，不应污染长期记忆。而临时会话（如一次性调试）也不值得持久化。这种过滤机制确保记忆库只保留有价值的、长期的知识积累。
`─────────────────────────────────────────────────`

## 两阶段流水线

### Phase 1: Rollout 提取（每个线程）

Phase 1 从最近的合格 rollouts 中提取结构化记忆。

#### 合格 Rollout 选择规则

从状态数据库使用启动声明规则选择：
- 来自允许的会话源
- 在配置的年龄窗口内
- 空闲足够长时间（避免总结仍活跃的会话）
- 未被其他进行中的 Phase 1 worker 拥有
- 在启动扫描/声明限制内

#### Phase 1 做什么

1. 从状态数据库声明一组有界的 rollout 任务
2. 过滤 rollout 内容到记忆相关的响应项
3. 并行发送每个 rollout 给模型（有并发上限）
4. 期望结构化输出包含：
   - 详细的 `raw_memory`
   - 紧凑的 `rollout_summary`
   - 可选的 `rollout_slug`
5. 从生成的记忆字段中删除敏感信息
6. 将成功的输出存回状态数据库作为 stage-1 输出

#### 并发与协调

- Phase 1 并行运行多个提取任务（有固定并发上限）
- 每个任务在处理前在状态数据库中租用/声明，防止重复工作
- 失败的任务标记有重试退避

#### 任务结果状态

- `succeeded` - 生成了记忆
- `succeeded_no_output` - 有效运行但没生成有用内容
- `failed` - 失败（有重试退避/租用处理）

### Phase 2: 全局整合

Phase 2 将最新的 stage-1 输出整合到文件系统记忆制品中，然后运行专门的整合代理。

#### Phase 2 做什么

1. 在接触记忆根目录前声明单个全局 phase-2 锁（确保只有一个整合工作区）
2. 使用 phase-2 选择规则从状态数据库加载一组有界的 stage-1 输出：
   - 忽略 `last_usage` 超出配置的 `max_unused_days` 窗口的记忆
   - 对于没有 `last_usage` 的记忆，回退到 `generated_at`
   - 优先按 `usage_count` 排序合格记忆，然后按最近的 `last_usage`/`generated_at`
3. 从声明的水印 + 最新输入时间戳计算完成水印
4. 同步记忆根目录下的本地记忆制品：
   - `raw_memories.md` - 合并的原始记忆（按稳定的线程 ID 升序）
   - `rollout_summaries/` - 每个选中 rollout 一个摘要文件
5. 将记忆根目录本身保持为 git-baseline 目录
6. 清理不再选中的过期 rollout 摘要
7. 清理早于扩展保留窗口的记忆扩展资源文件
8. 在记忆根目录中写入 `phase2_workspace_diff.md`，包含 git 风格的差异
9. 如果记忆工作区在制品同步/清理后没有变化，标记任务成功并退出

如果记忆工作区有变化，则继续：
1. 生成内部整合子代理
2. 用生成的工作区差异路径构建 Phase 2 提示词
3. 将代理指向 `phase2_workspace_diff.md` 获取详细差异上下文
4. 无批准、无网络、仅本地写权限运行
5. 禁用该代理的协作模式（防止递归委托）
6. 代理运行时观察代理状态并心跳全局任务租用
7. 代理成功完成后重置记忆 git 基线
8. 在状态数据库中标记 phase-2 任务成功/失败

#### 选择与工作区差异行为

- 成功的 Phase 2 运行将它们消耗的 stage-1 快照标记为 `selected_for_phase2 = 1`
- Phase 1 向上插入保留之前的 `selected_for_phase2` 基线
- Phase 2 仅加载当前 Top-N 选中的 stage-1 输入
- 当选中输入集为空时，删除过期的 `rollout_summaries/` 文件，将 `raw_memories.md` 重写为空输入占位符

#### 水印行为

- 全局 phase-2 锁不使用数据库水印作为脏检查；git 工作区脏度决定是否需要运行代理
- 全局 phase-2 任务行仍跟踪输入水印作为记账
- Phase 2 使用以下最大值重新计算 `new_watermark`：声明的水印、实际加载的 stage-1 输入中最新的 `source_updated_at`
- 成功时，Phase 2 将该完成水印存储在数据库中

## 为什么分成两阶段

- **Phase 1**：跨多个 rollouts 扩展，生成标准化的 per-rollout 记忆记录
- **Phase 2**：序列化全局整合，安全一致地更新共享记忆制品

`★ Insight ─────────────────────────────────────`
**两阶段设计的工程智慧**
将记忆生成拆分为 Phase 1（并行）和 Phase 2（串行）是为了解决一个核心矛盾：并行提取效率 vs 串行整合安全。Phase 1 让多个会话的记忆可以同时提取，大大提高吞吐量；而 Phase 2 的串行整合确保共享制品的一致性。这种设计借鉴了 MapReduce 模式，既保证了性能，又确保了数据完整性。
`─────────────────────────────────────────────────`

## 提示词模板

记忆提示词模板与使用它们的 crate 在一起：
- 未注明日期的模板文件是运行时使用的最新版本
- 在 `codex` 中，直接编辑这些未注明日期的模板文件
- 注明日期的快照复制工作流在单独的 `openai/project/agent_memory/write` harness 仓库中使用，不在这里

## 存储位置

记忆存储在 `~/.codex/memories/`，目录本身是一个 git 仓库，用于基线比较。

## 实际例子

记忆文件长这样（在 `~/.codex/memories/rollout_summaries/` 中）：
```
# 2024-05-04: 重构 auth 模块

## 做了什么
- 将 JWT 验证逻辑抽取到单独的 validate_jwt.rs
- 添加了 refresh token 轮换机制
- 修复了过期 token 没有正确清理的 bug

## 遇到的坑
- 一开始忘了处理 token 中的 nbf（not before）字段
- 测试环境中时间同步问题导致 false positive

## 关键决策
选择 jsonwebtoken crate 而不是自己实现，因为：
1. 它维护活跃
2. 有安全审计历史
3. API 设计清晰
```

## 实战案例：理解记忆的形成

```bash
# 查看记忆根目录的 git 历史
cd ~/.codex/memories
git log --oneline -10

# 查看最新的差异（Phase 2 工作区）
cat phase2_workspace_diff.md

# 查看最近生成的 rollout 摘要
ls -lt rollout_summaries/ | head -5
```

## 避坑指南

### 坑：期待记忆立即生效

❌ **错误理解**：刚结束的对话内容马上在记忆中可用
❌ **原因**：记忆流水线在会话启动时触发，不是结束时
❌ **后果**：新会话可能看不到刚刚生成的内容

✅ **正确理解**：在下次启动 Codex 时，记忆系统会从新的会话中提取

### 坑：手动修改记忆文件

❌ **错误做法**：直接编辑 `~/.codex/memories/raw_memories.md`
❌ **原因**：会被下次 Phase 2 覆盖，且可能破坏 git 基线
❌ **后果**：修改丢失，记忆系统可能异常

✅ **正确做法**：
- 如果需要添加知识，使用[技能系统](./../04-advanced/14-skills-in-depth.md)
- 如果需要调整记忆生成，通过配置文件参数控制

### 坑：记忆内容过于分散

❌ **问题表现**：同一个主题的记忆分散在多个 rollout 中
❌ **原因**：会话粒度太细，没有形成连贯上下文
❌ **后果**：AI 需要合并多个记忆片段，效率低

✅ **正确做法**：
- 使用连贯的会话完成一个完整任务
- 适当使用"继续"保持上下文，而不是频繁新建会话
- Phase 2 会智能合并相关记忆，但输入质量决定输出质量

## 本章小结

**一句话记住**：Memories 是两阶段流水线 — Phase 1 并行提取每个会话的记忆，Phase 2 全局序列化整合到文件系统。

**核心要点**：
1. **触发机制**：会话启动时，排除了子代理和临时会话
2. **两阶段设计**：Phase 1 并行提取，Phase 2 串行整合
3. **Git 基线**：记忆制品通过 git 管理变更
4. **水印追踪**：防止重复处理，确保一致性

**下一步**：了解 State 系统如何持久化这些记忆数据（第十一章）。

---

**系列目录**：
- [第一章：Codex 是什么 —— OpenAI 的本地编码代理](./../01-intro/01-what-is-codex.md)
- [第二章：安装与上手 —— npm/brew/二进制三种方式](./../01-intro/02-installation-setup.md)
- [第三章：认证与配置 —— ChatGPT 账号 vs API Key](./../01-intro/03-authentication.md)
- [第四章：TUI 基础 —— 终端 UI 的交互方式](./../02-core/04-tui-basics.md)
- [第五章：codex exec —— 非交互式编程执行](./../02-core/05-codex-exec.md)
- [第六章：沙箱系统 —— 安全执行命令](./../02-core/06-sandbox.md)
- [第七章：MCP 客户端 —— 连接外部工具](./../03-cli/07-mcp-client.md)
- [第八章：架构概览 —— 100+ Crates 的模块化设计](./../04-advanced/08-architecture-overview.md)
- [第九章：TUI 深入 —— Ratatui 应用的构建方式](./../04-advanced/09-tui-in-depth.md)
- 第十章：Memories 系统 —— AI 的长期记忆 👈 当前位置
- [第十一章：State 系统 —— SQLite 数据库持久化](./../04-advanced/11-state-system.md) 👉 下一章
- [第十二章：Tools 系统 —— 从 codex-core 独立出的工具原语](./../04-advanced/12-tools-system.md)
- [第十三章：Exec 系统 —— 安全沙箱执行的深层设计](./../04-advanced/13-exec-system.md)
- [第十四章：技能系统深入 —— 50+ 内置技能与实战场景](./../04-advanced/14-skills-in-depth.md)
- [第十五章：技能系统 —— 给 AI 注入专业知识](./../05-plugins/15-skills-system.md)
- [第十六章：Hooks 系统 —— 事件驱动的自动化](./../05-plugins/16-hooks-system.md)
- [第十七章：Plugin 系统 —— Codex 的扩展机制](./../05-plugins/17-plugin-system.md)
- [第十八章：开发工作流 —— 如何构建和测试 Codex](./../06-enterprise/18-development-workflow.md)
- [第十九章：配置系统 —— TOML + JSON Schema](./../06-enterprise/19-configuration-system.md)
- [第二十章：安全设计 —— 多层安全防护](./../06-enterprise/20-security.md)
- [第二十一章：架构总结 —— 100+ Crates 的设计哲学](./../06-enterprise/21-architecture-summary.md)
