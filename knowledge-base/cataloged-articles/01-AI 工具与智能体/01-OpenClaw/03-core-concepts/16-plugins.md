# 第十六章：plugins —— 插件系统开发指南

OpenClaw 设计了强大的插件系统，让你可以扩展核心功能，添加新的聊天渠道、模型提供者、工具、技能等。本章我们讲解插件系统架构，以及如何开发自己的插件。

## 什么是插件

插件就是**一个独立的代码模块**，扩展 OpenClaw 核心功能，不用改核心代码就能添加新能力：

- 添加新的聊天渠道（比如一个新的聊天 App）
- 添加新的模型认证提供者
- 添加新的 agent 工具
- 添加新的 CLI 命令
- 添加后台服务
- 打包技能分享给其他人

插件**进程内加载**，和 Gateway 一起运行，性能好，开发简单。

## 插件清单文件 `openclaw.plugin.json`

**每个插件必须**有一个 `openclaw.plugin.json` 在插件根目录。OpenClaw 用它来验证配置，不需要运行插件代码就能验证。

### 必需字段

这段配置写在**插件根目录**的 `./openclaw.plugin.json`：

```json
{
  "id": "voice-call",
  "configSchema": {
    "type": "object",
    "additionalProperties": false,
    "properties": {}
  }
}
```

| 字段 | 必需 | 说明 |
|------|------|------|
| `id` | ✅ | 插件唯一 ID |
| `configSchema` | ✅ | 配置的 JSON Schema，即使插件不需要配置也要给个空 schema `{"type": "object", "additionalProperties": false}` |

### 可选字段

| 字段 | 说明 |
|------|------|
| `kind` | 插件类型（比如 `"memory"`） |
| `channels` | 插件注册的渠道 ID 列表 |
| ` providers` | 插件注册的模型提供者 ID 列表 |
| `skills` | 技能目录，相对于插件根目录 |
| `name` | 插件显示名称 |
| `description` | 插件简介 |
| `uiHints` | UI 提示，给配置字段加标签、占位符、标记敏感 |
| `version` | 插件版本 |

## 常用 CLI 命令

```bash
# 列出所有插件
openclaw plugins list

# 查看插件详情
openclaw plugins info <id>

# 启用插件
openclaw plugins enable <id>

# 禁用插件
openclaw plugins disable <id>

# 安装插件（从 npm）
openclaw plugins install <npm-package>
openclaw plugins install ./local-path  # 本地开发
openclaw plugins install ./local-path -l  # 链接不复制，开发用

# 卸载插件
openclaw plugins uninstall <id>

# 更新插件
openclaw plugins update <id>
openclaw plugins update --all  # 更新所有

# 检查插件健康
openclaw plugins doctor
```

## 插件配置

配置示例（写在**你的主配置文件** `~/.openclaw/openclaw.json`）：

```json5
{
  plugins: {
    enabled: true,            // 总开关，默认 true
    allow: ["voice-call"],    // 允许列表
    deny: ["untrusted-plugin"], // 拒绝列表，deny 优先
    load: { paths: ["~/my-plugin"] }, // 额外加载路径
    entries: {
      "voice-call": {
        enabled: true,
        config: { provider: "twilio" }, // 插件配置，按照你的 JSON Schema 验证
      },
    },
    slots: { // 排他插槽，同一时间只能有一个启用
      memory: "memory-lancedb", // 记忆插件只能选一个
    },
  },
}
```

**配置修改后必须重启 Gateway**。

## 插件插槽（排他分类）

有些插件分类是**排他**的，同一时间只能激活一个（比如长时记忆插件只能用一个）。用 `slots` 配置：

```json5
{
  plugins: {
    slots: {
      memory: "memory-lancedb", // 只有这个会加载，其他同类禁用
      // 填 "none" 禁用这个分类
    },
  },
}
```

## 发现顺序

OpenClaw 按这个顺序搜索插件：

1. 配置里 `plugins.load.paths`
2. 工作区 `.openclaw/extensions/`
3. 全局 `~/.openclaw/extensions/`
4. 核心自带扩展（默认禁用，需要手动启用）

如果多个插件 ID 冲突，先找到的生效。

## 插件开发

### 插件入口

插件导出一个注册函数，写在插件的**入口 TypeScript 文件**，通常是 `./src/index.ts`（相对插件根目录）：

```typescript
export default function register(api) {
  // 在这里注册各种扩展
  // api 提供了各种注册方法和运行时工具
}
```

或者导出一个对象：

```typescript
export default {
  id: "my-plugin",
  name: "My Plugin",
  configSchema: { /* ... */ },
  register(api) {
    // ...
  },
}
```

### 注册渠道插件（新增聊天渠道）

渠道插件就是添加一个新的聊天平台支持，比如 WhatsApp、Telegram、Discord 官方核心已经有了，如果你想加一个新平台，开发一个渠道插件。

最小示例，写在插件入口文件 `./src/index.ts`：

```typescript
const plugin = {
  id: "acmechat",
  meta: {
    id: "acmechat",
    label: "Acme Chat",
    selectionLabel: "Acme Chat (API)",
    docsPath: "/channels/acmechat",
    blurb: "AcmeChat  messaging.",
    aliases: ["acme"],
  },
  capabilities: {
    chatTypes: ["direct"],
  },
  config: {
    listAccountIds: (cfg) => Object.keys(cfg.channels?.acmechat?.accounts ?? {}),
    resolveAccount: (cfg, accountId) =>
      cfg.channels?.acmechat?.accounts?.[accountId ?? "default"] ?? {
        accountId,
      },
  },
  outbound: {
    deliveryMode: "direct",
    sendText: async ({ text }) => {
      // 发送文本到渠道
      return { ok: true };
    },
  },
};

export default function (api) {
  api.registerChannel({ plugin });
}
```

配置存在用户配置的 `channels.<id>` 下面，不是 `plugins.entries`，所以用户配置渠道更方便。

**完整步骤**：

1. 定义渠道 ID 和元数据（名称、描述、别名）
2. 实现配置查询接口（列出账号、解析账号配置）
3. 实现发送消息接口
4. 可选：添加更多功能（状态检查、mention 处理、流媒体等）
5. `api.registerChannel` 注册

### 注册工具插件

插件可以注册 Agent 工具，让 AI 调用：

详见 [Plugin agent tools](https://docs.openclaw.ai/plugins/agent-tools)。

### 注册钩子

插件可以注册钩子，在特定事件发生时运行，代码写在插件入口文件 `./src/index.ts`：

```typescript
export default function register(api) {
  api.registerHook(
    "command:new",
    async () => {
      // 每次 /new 清空会话后运行
    },
    {
      name: "my-plugin.command-new",
      description: "Runs when /new is invoked",
    }
  );
}
```

钩子通过插件启用/禁用控制，不能单独开关。

### 注册模型提供者认证

插件可以添加新的模型提供者认证流程，代码写在插件入口文件：

```typescript
api.registerProvider({
  id: "acme",
  label: "Acme AI",
  auth: [
    {
      id: "oauth",
      label: "OAuth",
      kind: "oauth",
      run: async (ctx) => {
        // 执行 OAuth 流程，返回凭证
        return {
          profiles: [{
            profileId: "acme:default",
            credential: { ... },
          }],
          defaultModel: "acme/opus-1",
        };
      },
    },
  ],
});
```

### 注册自定义命令

插件可以注册斜杠命令，**不经过 AI 直接执行**，适合状态查询、开关操作等，代码写在插件入口文件：

```typescript
api.registerCommand({
  name: "mystatus",
  description: "Show my plugin status",
  acceptsArgs: true,
  requireAuth: true,
  handler: async (ctx) => {
    // ctx 包含 senderId, channel, args, config
    return { text: "Plugin is running!" };
  },
});
```

- 命令在 AI 之前处理，匹配到就不发给 AI
- 不能覆盖核心命令（help/status/reset 等）
- 不区分大小写

### 注册后台服务

插件可以注册后台服务，Gateway 启动时运行，停止时关闭，代码写在插件入口文件：

```typescript
export default function (api) {
  api.registerService({
    id: "my-service",
    start: () => api.logger.info("service started"),
    stop: () => api.logger.info("service stopped"),
  });
}
```

### 注册 Gateway RPC 方法

插件可以添加 Gateway RPC 方法，代码写在插件入口文件：

```typescript
export default function (api) {
  api.registerGatewayMethod("myplugin.status", ({ respond }) => {
    respond(true, { ok: true });
  });
}
```

## 安全注意事项

插件进程内运行，**所以插件代码就是你的 Gateway 代码**，安全责任你自己承担：

1. **只安装你信任的插件** —— 插件能访问你的配置、文件、API 密钥
2. **使用 allowlist** —— `plugins.allow` 只允许明确信任的插件
3. **修改后重启** —— 配置改完必须重启 Gateway 才生效
4. **npm install 安全** —— `openclaw plugins install` 安装依赖时用 `--ignore-scripts`，不运行 postinstall 脚本

## 分发插件

推荐方式：

- 核心插件：放在 OpenClaw 源代码 `extensions/` 目录，默认禁用，用户手动启用
- 社区插件：发布到 npm，包名 `@openclaw/your-plugin`，用户 `openclaw plugins install` 直接安装

package.json 需要声明扩展入口，写在 `./package.json`（npm 包根目录）：

```json
{
  "name": "@openclaw/voice-call",
  "openclaw": {
    "extensions": ["./src/voice-call.ts"]
  }
}
```

一个 npm 包可以包含多个扩展，每个扩展是一个独立插件。

## 社区插件提交

想让你的插件列在官方社区插件页面？需要满足：

1. npm 上发布
2. GitHub 公开仓库
3. 有使用文档
4. 有维护者，活跃更新

提交 PR 到 OpenClaw，添加到 [plugins/community.md](https://github.com/openclaw/openclaw/blob/main/docs/plugins/community.md) 即可。

## 开发新渠道插件 vs 核心内置

什么时候做插件，什么时候合并到核心：

- **插件**：小众平台、第三方集成、实验性功能 —— 插件更灵活，不影响核心大小
- **核心**：主流平台、稳定功能 —— 核心内置，用户不用额外安装

## 本章小结

- OpenClaw 插件系统支持扩展渠道、提供者、工具、命令、服务
- 每个插件必须有 `openclaw.plugin.json` 描述，包含 JSON Schema 验证配置
- 插件进程内加载，性能好，开发简单
- 支持排他插槽（比如记忆插件只能选一个）
- 安全提示：只装信任插件，用 allowlist 控制
- 社区插件通过 npm 分发，用户一键安装

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
- 第十六章：plugins —— 插件系统开发指南 👈 当前位置
- [第十七章： refactor —— OpenClaw 重构原则与工作流](./17-refactor.md) 👉 下一章
- [第十八章：reference —— 完整配置、模板、CLI 命令参考](./18-reference.md)
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
