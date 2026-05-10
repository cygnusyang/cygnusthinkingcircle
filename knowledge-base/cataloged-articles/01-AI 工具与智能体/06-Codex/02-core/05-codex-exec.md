# 第五章：codex exec —— 非交互式编程执行

除了交互式 TUI，Codex 还支持非交互式执行：`codex exec`。

## 基本用法

```bash
codex exec "帮我重构这个 Python 脚本"
```

## 从 stdin 读取

```bash
echo "这个输出是什么意思？" | codex exec "分析一下"
```

或者结合起来：

```bash
git diff | codex exec "帮我写一个提交消息"
```

## 不保存会话（Ephemeral）

```bash
codex exec --ephemeral "快速任务"
```

这样不会在磁盘上保存会话记录。

## 实际例子

### 例子 1：代码审查

```bash
git diff HEAD~1 HEAD | codex exec "审查这些改动有没有问题"
```

### 例子 2：生成文档

```bash
codex exec "给 src/ 目录下的所有文件生成文档"
```

### 例子 3：修复 bug

```bash
codex exec "tests/ 目录下的测试失败了，帮我看看是什么问题"
```

## 日志输出

设置 `RUST_LOG` 环境变量看详细日志：

```bash
RUST_LOG=debug codex exec "任务"
```

## 本章小结

**一句话记住**：`codex exec` 用于自动化脚本和一次性任务。

---

**系列目录**：
- [第一章：Codex 是什么 —— OpenAI 的本地编码代理](./../01-intro/01-what-is-codex.md)
- [第二章：安装与上手 —— npm/brew/二进制三种方式](./../01-intro/02-installation-setup.md)
- [第三章：认证与配置 —— ChatGPT 账号 vs API Key](./../01-intro/03-authentication.md)
- [第四章：TUI 基础 —— 终端 UI 的交互方式](./04-tui-basics.md)
- 第五章：codex exec —— 非交互式编程执行 👈 当前位置
