# 第十二章：权限系统 —— deny→ask→allow的安全边界

权限系统是 Harness 的**免疫系统**——决定 Agent 能做什么、不能做什么、什么需要用户确认。

## 为什么权限系统至关重要

裸 Agent 拥有所有用户权限。这意味着：
- 它可以 `rm -rf /`（如果用户权限允许）
- 它可以读取 `.env` 中的 API 密钥
- 它可以 `git push --force` 覆盖远程仓库
- 它可以 `curl` 上传文件到外部服务器

**Agent 没有恶意，但它可能犯错**。权限系统不是为了防恶意，是为了防事故。

## 三级管道模型

```
每个 tool_call
    │
    ▼
┌─────────┐
│  DENY   │  永远拒绝
│  规则   │  ──── match → BLOCK ────
└─────────┘
    │ no match
    ▼
┌─────────┐
│  ASK    │  需要确认
│  规则   │  ──── match → 弹出确认 → 用户接受? → Yes: EXECUTE
└─────────┘                                    → No: BLOCK
    │ no match
    ▼
┌─────────┐
│  ALLOW  │  自动允许
│  规则   │  ──── match → EXECUTE
└─────────┘
    │ no match
    ▼
  DEFAULT (通常是 ASK)
```

核心设计原则：**Deny 永远优先**。即使一个操作同时匹配 allow 和 deny 规则，deny 胜出。

## 规则配置

```yaml
permissions:
  # === DENY 规则（安全底线） ===
  deny:
    # 敏感文件
    - pattern: "**/.env"
      tools: ["Read", "Write", "Edit", "Bash"]
    - pattern: "**/*.key"
      tools: ["Read"]
    - pattern: "**/*.pem"
      tools: ["Read"]

    # 危险命令
    - pattern: "rm -rf /*"
      tools: ["Bash"]
    - pattern: "sudo *"
      tools: ["Bash"]
    - pattern: "git push --force *"
      tools: ["Bash"]

    # 隐私数据
    - pattern: "**/.ssh/**"
      tools: ["Read"]

  # === ASK 规则（需要确认） ===
  ask:
    # 写入操作
    - pattern: "**/*"
      tools: ["Write", "Edit"]

    # 网络操作
    - pattern: "*"
      tools: ["WebFetch"]

    # Git 写操作
    - pattern: "*"
      tools: ["Bash"]
      sub_pattern: "git (commit|push|branch -D)"

  # === ALLOW 规则（自动通过） ===
  allow:
    # 只读操作
    - pattern: "**/*"
      tools: ["Read", "Grep", "Glob"]

    # Git 只读
    - pattern: "*"
      tools: ["Bash"]
      sub_pattern: "git (status|diff|log|branch[^-])"

    # 安全命令
    - pattern: "*"
      tools: ["Bash"]
      sub_pattern: "ls|cat|head|tail|wc|find|which|echo|pwd|whoami|date"
```

## 匹配优先级

```python
def check_permission(tool_name: str, params: dict) -> PermissionResult:
    # 1. DENY 规则优先检查
    for rule in deny_rules:
        if rule.matches(tool_name, params):
            return PermissionResult.DENY

    # 2. ASK 规则
    for rule in ask_rules:
        if rule.matches(tool_name, params):
            return PermissionResult.ASK

    # 3. ALLOW 规则
    for rule in allow_rules:
        if rule.matches(tool_name, params):
            return PermissionResult.ALLOW

    # 4. 默认
    return PermissionResult.ASK
```

**为什么是 deny → ask → allow 这个顺序？**
- 先 deny：安全规则不可绕过，即使 later allow 也不生效
- 再 ask：需要确认的高于自动允许
- 最后 allow：剩下的才是安全的

## Auto Mode 与分类器

Claude Code 2026 年 3 月引入了 Auto Mode：

```
模糊的工具调用
    │
    ▼
┌───────────────────┐
│ 后台分类器          │  ← 运行在 Sonnet 4.6
│ （只看到工具调用）   │
└───────────────────┘
    │
    ▼
  自动判断: allow / ask / deny
```

关键安全设计：分类器**看不到 Agent 的推理文本**（prose），只能看到工具调用本身。这防止了 prompt injection——即使 Agent 被诱导写出危险操作的理由，分类器也不受影响。

## 路径模式匹配

权限规则中最重要的是路径匹配：

```python
def path_matches(pattern: str, actual_path: str) -> bool:
    """
    pattern 支持:
    - **: 匹配任意层级
    - *: 匹配单层
    - 精确路径
    """
    # "**/.env" 匹配 "/project/.env" 和 "/project/subdir/.env"
    # "src/**" 匹配 "src/" 下所有文件
    # "*.key" 匹配所有 .key 文件
```

## 权限系统的工程权衡

| 维度 | 宽松 | 严格 |
|------|------|------|
| 用户体验 | 流畅，少打断 | 打断多，但安全 |
| 安全 | 信任模型判断 | 用户每次确认 |
| 适合场景 | 个人项目 | 企业/生产环境 |
| 疲劳度 | 低 | 高（确认疲劳） |

**最佳实践**：分层配置——个人项目可以宽松，工作项目可以严格。Claude Code 支持项目级 `.claude/settings.json` 和全局 `~/.claude/settings.json`：

```json
// ~/.claude/settings.json（全局严格默认）
{
  "permissions": {
    "defaultMode": "ask"
  }
}

// ~/work/production-project/.claude/settings.json（工作项目更严格）
{
  "permissions": {
    "defaultMode": "ask",
    "deny": ["rm -rf", "sudo", "**/.env", "**/*.key"],
    "requireConfirmationFor": ["Write", "Edit", "Bash"]
  }
}
```

## 本章小结

- 权限系统是防事故，不是防恶意——Agent 会犯错，不会故意破坏
- 三级管道 deny → ask → allow，deny 永远优先
- 规则基于：工具类型 + 文件路径 + 命令模式
- Auto Mode 分类器**故意不看到** Agent 推理文本——防 prompt injection
- 分层配置：全局默认 + 项目覆盖
- 下一章：上下文管理——自动注入、压缩与惰性加载

---

**系列目录**：
- [第十一章：工具系统](./11-tool-system.md)
- 第十二章：权限系统 —— deny→ask→allow的安全边界 👈 当前位置
- [第十三章：上下文管理](./13-context-management.md) 👉 下一章
- [第十四章：MCP集成](./14-mcp-integration.md)
- [第十五章：技能系统](./15-skills-system.md)
