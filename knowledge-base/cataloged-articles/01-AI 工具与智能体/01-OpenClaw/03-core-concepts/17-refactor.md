# 第十七章： refactor —— OpenClaw 重构原则与工作流

OpenClaw 持续演进，会定期进行大规模重构来保持代码健康。本章我们讲解 OpenClaw 的重构原则、正在进行的主要重构项目，以及重构工作流。

## 重构原则

OpenClaw 重构遵循这些核心原则：

### 1. 渐进式重构，分阶段迁移

不搞"大爆炸"重构，分阶段迁移，保持主分支一直可运行：

- 新代码增量添加
- 旧代码保留，标记 deprecated
- 用户可以平滑迁移
- 随时可以停止迁移，不影响使用

### 2. 严格配置验证

所有配置必须通过 JSON Schema 严格验证：

- 未知配置键直接报错，不静默忽略
- 每个插件必须提供配置 JSON Schema
- `openclaw doctor` 统一检查和修复
- 配置无效时阻止非诊断命令运行，让你尽早发现问题

### 3. 清晰的 API 边界

插件不能直接 import 核心代码，必须通过官方稳定 SDK：

- 插件 SDK 单独分层，稳定版本化
- 核心运行时通过注入 API 访问，不直接导入
- 所有插件依赖 SDK，不依赖内部实现

### 4. 不盲目兼容，主动清理技术债务

- 旧架构发现问题果断重构
- 不保持无维护的兼容
- 迁移文档清晰，用户知道怎么一步步转

## 主要重构项目

### 1. Plugin SDK 重构

**目标**：所有渠道连接器都是插件，使用同一个稳定 SDK，不直接 import 核心代码。

**架构**：两层

| 层 | 作用 |
|-----|------|
| **Plugin SDK** | 编译期，提供类型、帮助工具，稳定版本化 |
| **Plugin Runtime** | 运行时，核心注入 API，插件通过 Runtime 访问核心功能 |

**为什么重构**：

- 以前渠道插件有的直接 import 核心，升级容易破
- 现在统一 SDK，外部插件开发不用跟着核心改
- 外部插件可以独立版本迭代，不依赖核心发布节奏

**迁移计划**（分阶段）：

1. 脚手架：引入 `openclaw/plugin-sdk`
2. 清理小型插件：Zalo、Zalo Personal 先迁移
3. 迁移中型插件：Matrix
4. 迁移大型插件：Microsoft Teams
5. iMessage 转为插件
6. 禁止插件直接 import 核心

### 2. 严格配置验证重构

**目标**：所有配置严格验证，未知键报错，迁移只在 doctor 执行。

**核心规则**：

- 配置必须完全匹配 Schema，未知键就是错误
- 每个插件必须提供 Schema，没有 Schema 拒绝加载
- 不自动迁移旧配置，迁移交给 `openclaw doctor --fix`
- 启动时自动 doctor 检查，配置无效直接报错阻止启动

**好处**：

- 错键拼写出错立刻告诉你，不会静默失败
- 插件配置错误提前发现
- 迁移自动化，用户不用手动改配置

### 3. Clawnet 网络协议重构

**目标**：统一所有客户端（macOS/iOS/Android/CLI）的网络协议，统一认证、配对、TLS。

**当前问题**：

- 两个协议栈：Gateway WebSocket（控制面） + Bridge（节点传输）
- 批准提示出现在节点端，用户不在节点那里就收不到
- TLS pinning 只支持 Bridge，WebSocket 不支持
- 同一个机器可能出现重复身份标识

**方案**：

一个 WebSocket 协议，两种角色：

| 角色 | 作用 |
|------|------|
| **node** | 能力宿主，提供 system.run、camera、canvas 等 |
| **operator** | 控制平面，用户操作界面 |

- 一个设备可以同时开多个连接，不同角色分开
- 统一配对流程：客户端连接 → Gateway 创建配对请求 → Operator 批准 → 签发凭证
- 设备密钥对认证，token 绑定到公钥，更安全
- TLS  everywhere，所有连接都支持 TLS 指纹钉
- 批准集中在 Gateway，Operator UI 弹出提示，用户在哪里都能批准

**好处**：

- 一份代码维护，更少 bug
- 安全更强：TLS  everywhere，密钥绑定
- 用户体验更好：批准提示出现在用户那里，不管节点在哪里
- 身份不重复，同一个设备合并显示

## 重构工作流

OpenClaw 重构工作流是这样的：

### 1. 设计文档

重构开始前先写设计文档（像你现在读的这种），放在 `docs/refactor/` 下面：

- 讲清楚现状问题
- 讲清楚目标架构
- 分阶段迁移计划
- 公开讨论，收集反馈

### 2. 分阶段开发

每个阶段独立分支开发，合并到主分支后用户可以正常使用，部分迁移不影响使用：

- 阶段 0：文档对齐
- 阶段 1：添加新 API/协议
- 阶段 2：迁移小型插件
- 阶段 3：迁移大型插件
- 阶段 4：启用强制检查
- 阶段 5：删除旧代码

### 3. 迁移指南

重构完成后提供清晰的迁移指南：

- 从旧版本怎么迁移到新版本
- 分步命令
- 回滚方案

### 4. 兼容性

- 配置格式变更：doctor 自动迁移
-  Deprecation 警告：旧API可以用但是会警告
- 至少一个稳定版本兼容期，给用户时间迁移

## 用户怎么应对重构

- **跟着迁移向导走**：`openclaw doctor` 会提示你需要迁移什么
- **不用慌**：分阶段迁移，旧功能一直能用直到迁移完成
- **读 release notes**：每个版本会说明重构影响
- **有问题提 issue**：OpenClaw 维护者会帮你

## 本章小结

- OpenClaw 重构遵循渐进原则，分阶段迁移，不搞大爆炸
- 严格配置验证，有错尽早发现
- 清晰 API 边界，插件通过 SDK 访问核心
- 当前主要重构：Plugin SDK 标准化、严格配置验证、Clawnet 网络协议统一
- 重构是为了更好的扩展性和安全性，用户体验只会越来越好

---

---

**系列目录**：
- [第一章：OpenClaw 是什么 —— 自托管个人 AI 助手的终极形态](./../01-intro/01-what-is-openclaw.md)
- [第二章：核心架构总览 —— Gateway 为什么是中心控制平面](./../01-intro/02-architecture-overview.md)
- [第三章：Gateway —— 核心网关服务到底做了什么](./../01-intro/03-gateway.md)
- [第四章：多渠道接入 —— 如何支持 25+ 聊天平台](./../01-intro/04-multi-channel-inbox.md)
- [第五章：ACP —— 如何对接外部 AI 客户端](./../01-intro/05-acp.md)
- [第六章：消息路由 —— 消息如何正确送到对的会话](./../01-intro/06-routing.md)
- [第七章：安全模型 —— 配对白名单如何保护你](./../01-intro/07-security-model.md)
- [第八章：为什么你需要一个多智能体框架 —— 单智能体的困境](./../02-multi-agent/08-why-you-need-multi-agent-framework.md)
- [第九章：sessions_spawn —— 多智能体协作的核心原语](./../02-multi-agent/09-sessions-spawn-core-primitive.md)
- [第十章：协作架构模式 —— 从 Master-Worker 到 Hub-and-Spoke](./../02-multi-agent/10-collaboration-architecture-patterns.md)
- [第十一章：隔离设计 —— 为什么每个子智能体需要独立会话](./../02-multi-agent/11-isolation-design.md)
- [第十二章：嵌套协作 —— 如何实现 Orchestrator-Worker 模式](./../02-multi-agent/12-nested-collaboration.md)
- [第十三章：实践案例 —— 从零构建一个代码评审团队](./../02-multi-agent/13-practical-case-code-review-team.md)
- [第十四章：platforms —— 全平台安装部署指南](./14-platforms.md)
- [第十五章：providers —— 各大模型提供者配置大全](./15-providers.md)
- [第十六章：plugins —— 插件系统开发指南](./16-plugins.md)
- 第十七章： refactor —— OpenClaw 重构原则与工作流 👈 当前位置
- [第十八章：reference —— 完整配置、模板、CLI 命令参考](./18-reference.md) 👉 下一章
- [第十九章：skills —— 技能系统核心概念与开发指南](./19-skills.md)
- [第二十章：ClawHub —— 技能市场如何分享和获取技能](./20-clawhub.md)
- [第二十一章：Canvas A2UI —— 实时可视化协作 workspace](./../04-client-ux/21-canvas.md)
- [第二十二章：语音唤醒 (Voice Wake) —— 语音交互体验](./../04-client-ux/22-voice-wake.md)
- [第二十三章：WebChat —— Gateway WebSocket 聊天界面](./../04-client-ux/23-webchat.md)
- [第二十四章：工具系统 (Tools) —— OpenClaw 工具调用框架设计](./../05-tools-automation/24-tools.md)
- [第二十五章：内置浏览器 —— 网页抓取和交互](./../05-tools-automation/25-browser.md)
- [第二十六章：Cron 自动化 —— 定时任务自动化](./../05-tools-automation/26-cron.md)
- [第二十七章：Onboarding —— 新手引导流程设计](./../05-tools-automation/27-onboarding.md)
- [第二十八章：blogwatcher —— 博客与 RSS 更新监控](./../06-builtin-skills/28-live-covers.md)
- [第二十九章：gh-issues —— GitHub Issues 自动修复编排](./../06-builtin-skills/29-gh-issues.md)
- [第三十章：coding-agent —— 调用外部编码代理](./../06-builtin-skills/30-coding-agent.md)
- [第三十一章：模型故障转移 (Model Failover) —— 如何提高可用性](./../07-ops-best-practices/31-failover.md)
- [第三十二章：调试技巧 —— 如何排查 OpenClaw 问题](./../07-ops-best-practices/32-debugging.md)
- [第三十三章：成本优化 —— 如何用模型分级降低总成本](./../07-ops-best-practices/33-cost-optimization.md)
- [第三十四章：部署运维 —— OpenClaw 网关生产环境最佳实践](./../07-ops-best-practices/34-deployment.md)
