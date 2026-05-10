# 第十七章：Harness是Agent的操作系统

这一章展开一个核心类比：**Harness 之于 Agent，就像操作系统之于进程**。

## 操作系统类比

```
计算机世界:                      Agent 世界:
─────────────────────────────────────────────────
应用程序 (App)                   Agent (智能体)
    ↓                                ↓
操作系统 (OS)                    Harness (基础设施)
    ↓                                ↓
硬件 (CPU/内存/磁盘/网络)        模型 (LLM)
```

这个类比不是修辞——它精确地描述了 Harness 的每一个职责。

## 操作系统职责 → Harness 对应

| OS 职责 | 含义 | Harness 对应 | 含义 |
|---------|------|-------------|------|
| **进程管理** | 创建、调度、终止进程 | Agent 生命周期管理 | 启动、循环、终止 Agent |
| **内存管理** | 分配、回收、虚拟内存 | 上下文管理 | Auto-inject、压缩、MEMORY.md |
| **文件系统** | 读写文件、权限 | 文件工具 | Read/Write/Edit + 路径权限 |
| **I/O 管理** | 设备驱动、中断处理 | 工具系统 | 工具分发 + 结果格式化 |
| **安全/权限** | 用户权限、ACL | 权限管道 | deny → ask → allow |
| **进程间通信** | IPC、管道、socket | 多 Agent 通信 | 子 Agent 生成 + 结果回传 |
| **网络栈** | TCP/IP、HTTP | MCP 集成 | 外部工具调用 |
| **系统调用** | API for 应用程序 | 工具 API | Tool Schema + Execute |
| **资源管理** | CPU/内存配额 | Token 预算 | 轮次上限 + 上下文限制 |
| **驱动加载** | 按需加载设备驱动 | 惰性加载 | MCP + Skills 按需激活 |

## 深入几个关键类比

### 进程管理 ↔ Agent 生命周期

```c
// 操作系统创建进程
pid_t pid = fork();
if (pid == 0) {
    // 子进程: 执行程序
    execve("/bin/program", args, env);
}
// 父进程: 监控子进程
waitpid(pid, &status, 0);
```

```python
# Harness 创建 Agent
agent = Agent.spawn(
    task="修复 auth bug",
    tools=[...],
    context={...},
)
# 主 Harness: 监控 Agent
result = await agent.run()
if result.status == "completed":
    deliver(result)
elif result.status == "max_turns":
    ask_user_to_continue()
```

### 虚拟内存 ↔ 上下文管理

```
操作系统的虚拟内存:
  程序以为有 64GB 连续内存 → 实际只有 16GB → OS 用分页/交换来管理

Harness 的上下文管理:
  Agent 以为有无限上下文 → 实际只有 200K tokens → Harness 用压缩来管理
```

**分页 (Paging)** ↔ **Compaction**：
- 不常用的页 → 交换到磁盘
- 不重要的对话历史 → 压缩成摘要

### 系统调用 ↔ 工具 API

```c
// 应用程序调用 OS 服务
int fd = open("/path/to/file", O_RDONLY);
read(fd, buffer, 1024);
close(fd);
```

```python
# Agent 调用 Harness 工具
# (模型输出 tool_use，Harness 执行)
read_file("/path/to/file", offset=0, limit=1024)
```

都是**标准化的接口**——应用程序/Agent 不需要知道底层实现。

### 权限模型 ↔ 安全边界

```
OS:  用户 alice 不能读 /etc/shadow (除非是 root)
Harness: Agent 不能读 .env (除非用户确认)
```

```
OS:   sudo 提权需要密码
Harness: Bash 执行需要用户确认
```

### 驱动模型 ↔ MCP + 惰性加载

```
OS:   插入 USB 设备 → 加载驱动 → 设备可用
Harness: Agent 需要数据库 → 加载 PostgreSQL MCP → 工具可用
```

```
OS:   不需要时不加载驱动（省内存）
Harness: 不需要时不加载 MCP schema（省上下文）
```

## 这个类比的工程意义

### 1. 稳定性来自基础设施

一个 App crash 不应该让 OS crash。同样——一个 Agent 的失败不应该让 Harness 崩溃。

```python
try:
    result = await agent.run(task)
except AgentError as e:
    # Agent 失败了，但 Harness 继续运行
    log_error(e)
    await inform_user(f"任务失败: {e}")
    # 可以重试、换模型、降级处理...
```

### 2. 隔离是安全的基础

OS 用进程隔离保证 App 之间互不影响。Harness 用**上下文隔离**保证 Agent 之间互不影响。

```
进程隔离:    App A 不能访问 App B 的内存
Agent 隔离: 子 Agent A 的上下文不污染子 Agent B
```

这就是为什么 Claude Code 的子 Agent 有独立上下文窗口——不是设计偏好，是**安全需求**。

### 3. 资源管理是可靠性的前提

OS 不给一个进程无限内存。Harness 不给一个 Agent 无限上下文。

```
OS:   memory_limit = 2GB per process
Harness: max_turns = 50, max_tokens = window_size
```

### 4. 接口标准化带来生态

POSIX 标准让同一套代码可以在 Linux/macOS/BSD 上运行。MCP 协议让同一个 MCP Server 可以在 Claude Code/Codex/OpenClaw 上使用。

标准接口 → 繁荣生态 → 网络效应。

## 本章小结

- Harness 之于 Agent = 操作系统之于进程——两者职责映射精确
- 每个 OS 子系统都在 Harness 中有对应：进程管理→Agent 生命周期、虚拟内存→上下文管理、系统调用→工具 API、驱动→MCP
- 这个类比的工程意义：稳定性、隔离、资源管理、接口标准化
- MCP 就是 Agent 世界的 POSIX——标准接口带来繁荣生态
- 下一章：Agent-Harness 协作模式详解

---

**系列目录**：
- [第十六章：Agent的生命周期](./16-agent-lifecycle.md)
- 第十七章：Harness是Agent的操作系统 👈 当前位置
- [第十八章：Agent-Harness协作模式](./18-agent-harness-collaboration.md) 👉 下一章
- [第十九章：多智能体架构模式](../06-multi-agent/19-multi-agent-architectures.md)
