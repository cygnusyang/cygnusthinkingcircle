# 第三章：认证与配置 —— ChatGPT 账号 vs API Key

Codex 支持两种认证方式，各有优劣。

## 方式一：ChatGPT 账号（推荐）

### 优点
- 简单，直接用现有 ChatGPT 账号
- 包含在 Plus/Pro/Business/Enterprise 订阅里
- 不需要管理 API Key

### 登录流程

1. 运行 `codex`
2. 选择 "Sign in with ChatGPT"
3. 浏览器打开，授权登录
4. 回到终端，开始使用

### 适用场景
- 个人使用，有 ChatGPT 订阅
- 不想管理 API Key
- 企业用户用 ChatGPT Enterprise

## 方式二：API Key

### 优点
- 更灵活，可以控制使用量
- 适合自动化/CI 环境
- 不需要浏览器交互

### 配置步骤

1. 去 platform.openai.com 创建 API Key
2. 配置 Codex 使用 API Key

### 配置文件

配置文件在 `~/.config/codex/config.toml`：

```toml
# API Key 配置示例
[auth]
type = "api_key"
api_key = "sk-..."  # 你的 API Key
```

或者用环境变量：

```bash
export OPENAI_API_KEY="sk-..."
codex
```

## 配置项详解

参考 `source/codex/docs/config.md` 和 `source/codex/docs/example-config.md`，主要配置项：

```toml
[core]
# 核心配置

[auth]
# 认证配置

[exec]
# 执行相关配置

[ui]
# UI 配置
```

## 沙箱配置

Codex 支持沙箱执行，相关配置在 `source/codex/docs/sandbox.md`。

## 本章小结

**一句话记住**：个人用 ChatGPT 账号登录，自动化用 API Key。

**决策规则**：
- 日常使用 → ChatGPT 账号
- CI/自动化 → API Key
- 企业部署 → ChatGPT Enterprise + MDM

**现在就试**：选择一种方式认证 → 运行 `codex` → 输入"帮我看看当前目录有什么文件"

---

**系列目录**：
- [第一章：Codex 是什么 —— OpenAI 的本地编码代理](./01-what-is-codex.md)
- [第二章：安装与上手 —— npm/brew/二进制三种方式](./02-installation-setup.md)
- 第三章：认证与配置 —— ChatGPT 账号 vs API Key 👈 当前位置
