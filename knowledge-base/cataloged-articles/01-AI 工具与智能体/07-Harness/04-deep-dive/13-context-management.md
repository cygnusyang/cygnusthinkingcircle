# 第十三章：上下文管理 —— 自动注入、压缩与惰性加载

上下文窗口是 Agent 最稀缺的资源。当前顶级模型的窗口约 200K tokens——看起来很多，但一次复杂任务（30+ 轮，每轮 ~15K tokens）轻易就能填满。上下文管理是 Harness 的**记忆系统**。

## 上下文都消耗在哪

一次典型的 Agent 会话的上下文构成：

```
完整上下文窗口 (200K tokens)
├── System Prompt:        3,000  (CLAUDE.md, 规则, 工具定义)
├── Auto-Inject 每轮:     1,500  (git status, todo, 环境信息)
├── 模型输出:             800/轮  (推理 + 工具调用)
├── 工具结果:             2,000/轮 (文件内容, 命令输出)
├── 用户消息:             100/轮
└── 对话历史:             累积

30轮总计: ~140K tokens（占 200K 窗口的 70%）
50轮总计: ~230K tokens（超出窗口！需要压缩）
```

## 策略一：Auto-Inject（主动注入）

每轮自动注入必要的环境信息，避免模型浪费轮次去"探索"。

```python
def build_auto_inject() -> str:
    return f"""
## 当前环境
- 工作目录: {os.getcwd()}
- Git 分支: {git_branch()}
- 未暂存变更: {git_diff_summary()}
- 最近提交: {git_log_recent(5)}

## 任务进度
{todo_write_status()}

## 项目规则
{load_claude_md()}
"""
```

Auto-inject 每轮消耗 1,500-3,000 tokens，但省去了模型 2-5 轮"现在是什么状态？"的探索。对于 30+ 轮的任务，净收益显著。

## 策略二：Compaction（上下文压缩）

当上下文接近窗口上限时（通常是 95-98%），触发压缩：

### 压缩算法

```
输入: 完整的对话历史 [msg1, msg2, msg3, ..., msg100]

步骤:
1. 保留: 最近的 N 条消息（通常是最后 10-15 轮）
2. 保留: 系统消息 (system prompt, auto-inject 模板)
3. 摘要: 早期消息 → LLM 生成压缩摘要
4. 保留关键信息:
   - 重要工具调用结果（文件内容, 错误信息）
   - 已完成的关键决策点
   - TodoWrite 状态
5. 丢弃: 中间推理步骤, 失败尝试的细节, 冗余输出
```

### 压缩示例

```
压缩前 (15K tokens):
  轮1: User: "修复 auth bug"
  轮2: Agent: "让我先了解项目结构" → read_file("README.md") → [内容]
  轮3: Agent: "看一下认证相关文件" → grep("auth", "src/") → [5个文件]
  轮4: Agent: "读 auth.py" → read_file("src/auth.py") → [200行代码]
  轮5: Agent: "发现问题，第42行 JWT 验证未处理过期" → edit(...)
  ...

压缩后 (3K tokens):
  [早期摘要] 用户在修复认证bug。已确认问题在 src/auth.py:42，
  JWT 验证未处理 token 过期。已完成修改。

  轮5: Agent: "发现问题，第42行..." → edit(...)
  轮6: Agent: "现在更新测试..." → write_file(...)
  ...
```

**压缩比通常在 3-5×**（15K → 3K 是 5× 压缩）。

## 策略三：Lazy Loading（惰性加载）

不一次性加载所有能力，按需激活：

```
会话启动时:
  ✅ 加载: 核心工具定义（仅名称 + 一句话描述）
  ✅ 加载: CLAUDE.md
  ❌ 不加载: MCP 工具详情
  ❌ 不加载: 技能文件内容
  ❌ 不加载: 大文件内容索引

当 Agent 说 "我需要查询 Supabase 数据库":
  ✅ 加载: PostgreSQL Skills
  ✅ 加载: Supabase MCP 工具详情

当 Agent 说 "这个 PDF 文件里有什么":
  ✅ 加载: PDF 处理 Skill
```

### MCP 惰性加载的效果

```
传统方式:
  启动时加载 5 个 MCP 服务器的所有工具 → ~50K tokens

惰性加载:
  启动时加载 5 个 MCP 服务器的工具名 → ~2K tokens
  按需加载具体工具的 schema → ~5K tokens/次
```

**节省 95% 的 MCP 启动上下文**。

## 策略四：MEMORY.md（跨会话记忆）

对话结束后，有些信息应该保留到下次会话：

```markdown
# MEMORY.md（由 Agent 自动维护）

## 项目知识
- 本项目使用 JWT 认证，密钥在环境变量 JWT_SECRET
- 数据库迁移使用 Alembic，不要手动修改 schema
- 测试框架是 pytest，运行命令: `pytest -xvs`

## 用户偏好
- 用户偏好中文回复
- 代码注释用英文
- 提交信息用中文

## 经验教训
- 上次修改 auth.py 时没更新测试，导致 CI 失败
- src/utils 目录下有很多被其他模块引用的工具函数，修改需谨慎
```

每次新会话启动时，MEMORY.md 自动注入系统 prompt——让 Agent **带着上次的经验开始工作**。

## 策略五：结构化截断

对于过大的工具输出（如读取一个 5000 行的文件），进行结构化截断：

```python
def truncate_file_content(content: str, max_lines: int = 500) -> str:
    lines = content.split('\n')
    if len(lines) <= max_lines:
        return content

    # 保留头部和尾部
    head = '\n'.join(lines[:300])
    tail = '\n'.join(lines[-200:])
    omitted = len(lines) - 500

    return f"""[文件共 {len(lines)} 行，以下显示前 300 行和后 200 行]

{head}

... ({omitted} 行省略，如需查看请使用 offset 参数指定行号) ...

{tail}"""
```

关键：**告诉模型有内容被截断了**，以及**如何获取完整内容**。

## 上下文管理策略对比

| 策略 | 解决的问题 | 成本 | 效果 |
|------|-----------|------|------|
| Auto-Inject | Agent 不知道环境状态 | 每轮 +1.5K-3K tokens | 省 2-5 轮探索 |
| Compaction | 上下文窗口不够用 | 压缩调用消耗 ~1K tokens | 3-5× 压缩 |
| Lazy Loading | 启动时加载太多 | 按需加载延迟 ~200ms | 省 95% 启动上下文 |
| MEMORY.md | 会话间知识丢失 | 几百行文本 | 跨会话知识持久 |
| 结构化截断 | 大文件占满上下文 | 无额外成本 | 保留关键+告知完整获取方式 |

## 实际效果

以一次典型的 50 轮编码任务为例：

```
无上下文管理:
  总 tokens: ~280K → 超出窗口! → 任务失败

有 Auto-Inject:
  总 tokens: ~230K → 仍超出

有 Auto-Inject + Compaction:
  总 tokens: ~150K → 在窗口内 → 任务成功
  压缩调用: 3 次（每 15 轮左右）

有完整的上下文管理:
  总 tokens: ~120K → 充裕
  压缩调用: 1 次
  + MEMORY.md 跨会话知识
```

## 本章小结

- 上下文窗口是 Agent 最稀缺的资源——200K tokens 轻易就满
- 五大策略：Auto-Inject（主动注入）、Compaction（压缩）、Lazy Loading（惰性加载）、MEMORY.md（跨会话）、结构化截断
- Auto-Inject 多花 tokens 但省探索轮次，净收益为正
- Compaction 可实现 3-5× 压缩，在窗口满时自动触发
- Lazy Loading 节省 95% MCP 启动上下文
- 组合使用效果倍增——单一策略不够
- 下一章：MCP 集成——扩展 Harness 的能力边界

---

**系列目录**：
- [第十二章：权限系统](./12-permission-system.md)
- 第十三章：上下文管理 👈 当前位置
- [第十四章：MCP集成](./14-mcp-integration.md) 👉 下一章
- [第十五章：技能系统](./15-skills-system.md)
