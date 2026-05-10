# 第十五章：技能系统 —— 按需注入领域知识

Skill（技能）是 Harness 的**知识注入机制**——在需要时，给 Agent 加载特定领域的专业知识。

## 为什么需要技能

一个裸 Agent 的知识来自模型的训练数据。但训练数据有时效性和覆盖面的限制：

- 不知道你项目的内部约定
- 不了解某个特定框架的最新 API
- 不熟悉你使用的内部工具
- 对特定领域（医疗、法律、金融）的知识不够精确

Skills 解决了这个问题：**把专业知识写成 Markdown，Agent 在需要时自动加载**。

## Skill 的结构

```markdown
---
name: postgres-patterns
description: PostgreSQL database patterns for query optimization,
  schema design, indexing, and security. Use when writing SQL,
  creating migrations, designing schemas, or troubleshooting
  database performance.
---

# PostgreSQL Patterns

## Query Optimization

### Use EXPLAIN ANALYZE
Always run EXPLAIN ANALYZE before finalizing a query:
```sql
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';
```

### Index Strategy
- B-tree indexes for equality and range queries
- GIN indexes for full-text search
- Partial indexes for filtered queries
...

## Schema Design
...
```

### Frontmatter 字段

| 字段 | 用途 |
|------|------|
| `name` | 技能唯一标识 |
| `description` | **触发条件**——Agent 根据这个判断是否加载 |
| `version` | 版本号（可省略） |

**最关键的是 `description` 字段**——Agent 通过它来判断"我现在需要这个技能吗？"

## 技能的加载机制

```
Agent Loop 每一轮:
    1. Agent 推理: "我需要处理数据库查询"
    2. Agent 检查可用技能: "postgres-patterns? 描述说 'when writing SQL...'"
    3. Agent 决定: 需要加载
    4. Skill 内容注入到当前轮次的 system prompt
    5. Agent 基于 Skill 内容工作
```

与传统方式对比：

```
传统方式（全部加载）:
  System prompt = CLAUDE.md + PostgreSQL Patterns + Python Patterns
  + Security Guidelines + Git Workflow + Testing + ... = 50K tokens

技能方式（按需加载）:
  System prompt = CLAUDE.md = 3K tokens
  当需要 SQL 时 → +PostgreSQL Patterns = +5K tokens
  当需要写测试时 → +Testing Patterns = +3K tokens
  ...
  任何时候 context 只包含当前任务需要的技能
```

## 技能系统关键设计

### 1. 描述即触发器

```markdown
# ✅ 好的描述（Agent 能准确判断何时加载）
description: PostgreSQL database patterns for query optimization,
  schema design, indexing, and security. Use when writing SQL,
  creating migrations, designing schemas, or troubleshooting
  database performance.

# ❌ 坏的描述（太模糊，Agent 无法判断）
description: Database stuff

# ❌ 太宽泛（每轮都会加载）
description: Programming best practices and patterns for all languages
```

### 2. 技能可堆叠

当任务涉及多个领域时，Agent 可以同时加载多个技能：

```
任务: "为新的 API 端点写一个带有测试的 PostgreSQL 迁移"

加载的技能:
  ✅ postgres-patterns (涉及数据库迁移)
  ✅ python-testing (需要写测试)
  ✅ api-design (需要设计 API)
```

### 3. 技能分层

```
全局技能 (~/.claude/skills/):
  跨项目通用，如 PostgreSQL、Docker、Git Workflow

项目技能 (.claude/skills/):
  项目特定，如内部框架、团队约定

社区技能 (ClawHub/Registry):
  从社区获取，如 @madebywild/agent-harness-framework 的预设
```

### 4. 技能的热加载

技能不需要重启 Harness——文件变更即时生效：

```python
class SkillManager:
    def get_skill(self, name: str) -> str:
        # 每次都从磁盘重新读取
        path = self.skill_paths[name]
        return path.read_text()  # 始终是最新版本

    def list_skills(self) -> list[dict]:
        # 扫描技能目录，返回 name + description
        return [
            {"name": s.name, "description": s.description}
            for s in self.scan()
        ]
```

## 技能 vs MCP 工具

| 维度 | Skill | MCP 工具 |
|------|-------|---------|
| **提供的是** | 知识（怎么做好） | 能力（能做什么） |
| **格式** | Markdown 文本 | JSON Schema + 函数 |
| **作用** | 增强模型的推理 | 扩展模型的行动 |
| **示例** | PostgreSQL 最佳实践 | 执行 SQL 查询 |
| **执行者** | Agent 自己理解 | MCP Server 执行 |

Skill 回答"怎么做是对的"，MCP 工具回答"能做什么"。两者互补。

## 实际案例

以 Claude Code 的 PostgreSQL Skill 为例：

```
无 Skill:
  Agent: "CREATE TABLE users (id INT, name VARCHAR(255))"
  问题: 没有用 UUID, 没有 timestamps, 没有索引

有 Skill:
  Agent: "根据 PostgreSQL 最佳实践，我使用 UUID 主键，
         添加 created_at/updated_at 时间戳，
         在 email 列上创建唯一索引..."
  CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
  );
  CREATE UNIQUE INDEX idx_users_email ON users(email);
```

**同样的模型，同样的工具——唯一区别是 Skill 提供了领域知识**。

## 本章小结

- Skill = Markdown 文件 + 描述触发器——Agent 按需加载领域知识
- 核心设计：描述是触发器（Agent 通过描述判断是否加载），内容是知识
- 按需加载 vs 全部加载：节省 80%+ 系统 prompt 空间
- Skill 提供"怎么做是对的"（知识），MCP 提供"能做什么"（能力），两者互补
- 分层管理：全局技能 → 项目技能 → 社区技能
- 下一章：Agent 的生命周期——从 prompt 到执行完成

---

**系列目录**：
- [第十四章：MCP集成](./14-mcp-integration.md)
- 第十五章：技能系统 👈 当前位置
- [第十六章：Agent的生命周期](../05-agent-harness/16-agent-lifecycle.md) 👉 下一章
- [第十七章：Harness是Agent的操作系统](../05-agent-harness/17-harness-as-os.md)
- [第十八章：Agent-Harness协作模式](../05-agent-harness/18-agent-harness-collaboration.md)
