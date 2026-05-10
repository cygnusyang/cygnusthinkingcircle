# 第三十二章：调试技巧 —— 如何排查 OpenClaw 问题

OpenClaw 出问题了怎么快速定位？本章汇总常用调试技巧，帮你快速找到问题解决问题。

## 第一步：运行健康检查

不管什么问题，先跑这个：

```bash
openclaw doctor
```

`doctor` 会自动检查：

- 配置文件格式对不对
- 必需配置项有没有填
- API 密钥能不能用
- 网络通不通各个提供者
- 插件依赖满足不满足
- 端口被不被占用

很多问题 `doctor` 直接告诉你哪里错了，甚至自动修复。

**修复问题：**

```bash
openclaw doctor --fix
```

自动修复常见问题（比如配置格式迁移）。

## 看日志

大部分问题日志里都有错误信息。

### 看最近日志

```bash
openclaw logs
```

显示 Gateway 最近的日志，从最新开始。

### 过滤关键词

```bash
openclaw logs --grep "error"
openclaw logs --grep "anthropic"
openclaw logs --grep "failover"
```

### 实时跟踪日志

```bash
openclaw logs --follow
```

实时输出新日志，方便调试正在发生的问题。

### 服务日志（systemd）

如果你用 systemd 跑服务：

```bash
journalctl -u openclaw -f
```

## 常见问题分类排查

### 问题 1：Gateway 启动失败

**排查：**

1. `openclaw doctor` 先看配置错了吗
2. 看端口是不是被占了：`lsof -i :18789`
3. 看日志：`openclaw logs` 找错误信息
4. 权限问题：`~/.openclaw/` 目录权限对不对，是不是 openclaw 用户能读写

**常见原因：**
- JSON 语法错了（少逗号、引号）
- 端口被别的程序占了
- 权限不够读配置文件
- 依赖没装全（`pnpm install` 没跑完）

### 问题 2：AI 不响应，一直转圈

**排查：**

1. 看模型认证：`openclaw models status`
   - 密钥过期了？
   - 额度用完了？
2. 看网络通不通：`curl https://api.anthropic.com/v1/models`
   - 是不是网络被墙了？
   - 代理配置对不对？
3. 看日志找错误：`openclaw logs --grep "anthropic\|openai"`
   - 401 → 密钥错
   - 429 → 限流
   - 500 → 云端宕机，等一会或者切 fallback

**解决：**
- 密钥错了重新配：`openclaw models auth setup-token --provider anthropic`
- 限流等一会，或者开故障转移切备用模型
- 网络问题检查代理配置

### 问题 3：配对不上，收不到批准请求

**排查：**

1. Gateway 在线吗？`openclaw gateway status`
2. 渠道对不对？`openclaw channels status`
3. 看日志：`openclaw logs --grep "pairing"`
4. 你的 bot token 对不对？

**常见原因：**
- bot 配置错了 token
- Gateway 没启动，或者没连上网
- 安全组没放行端口
- Webhook 地址错了

### 问题 4：工具调用失败

**排查：**

1. 工具启用了吗？`openclaw tools list`
2. 权限配置对不对？看文件系统白名单
3. 命令在白名单里吗？
4. 看日志：`openclaw logs --grep "tool"`

**常见原因：**
- 路径不在允许列表 → 调整配置权限
- 命令不在白名单 → 添加命令到白名单
- 文件不存在 → 路径对不对

### 问题 5：插件加载失败

**排查：**

1. `openclaw plugins doctor` 检查插件健康
2. `openclaw plugins list` 看插件状态
3. 依赖都装了吗？插件目录 `node_modules` 存在吗

**解决：**
- `openclaw plugins reinstall <plugin-id>` 重新装

### 问题 6：Cron 任务没触发

**排查：**

1. `openclaw cron list` 看任务是不是 `enabled: true`
2. 时区对不对？`timezone: "Asia/Shanghai"` 对吗
3. cron 表达式写对了吗？https://crontab.guru/ 可以验证
4. 看日志：`openclaw logs --grep "cron"`

## 开启调试日志

想要更详细日志，在配置开 debug，写在你的**主配置文件** `~/.openclaw/openclaw.json` 的根级别：

```json5
{
  logging: {
    level: "debug", // trace > debug > info > warn > error
  },
}
```

重启 Gateway 就有详细日志，开发排查问题有用。生产环境开 info 够了。

## 网络问题排查

### 测试 API 连通

```bash
# 测试 Anthropic API
curl -i https://api.anthropic.com/v1/models \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01"
```

```bash
# 测试 OpenAI API
curl -i https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### 检查代理

如果你用代理，检查环境变量：

```bash
echo $HTTP_PROXY
echo $HTTPS_PROXY
```

OpenClaw 会读取环境变量代理，也可以配置，写在你的**主配置文件** `~/.openclaw/openclaw.json` 的根级别：

```json5
{
  network: {
    proxy: "http://proxy:port",
  },
}
```

## 获取帮助

实在找不到问题，可以这样提 issue：

1. `openclaw --version` 输出版本号
2. 把错误日志贴出来（去掉密钥！）
3. 说一下你做了什么，期望发生什么，实际发生什么
4. 说一下你的操作系统、Node.js 版本

更快得到帮助。

## 调试 checklist

```
- [ ] 跑了 openclaw doctor 吗？
- [ ] 看了日志找到错误信息了吗？
- [ ] 检查配置语法对吗？JSON5 语法对吗？
- [ ] 检查密钥对不对，过期没？
- [ ] 检查网络通不通API？
- [ ] 检查端口有没有被占？
- [ ] 检查权限对不对，文件能读吗？
```

按顺序来，90% 的问题都能快速找到。

## 本章小结

- 出问题先跑 `openclaw doctor`，自动检查常见问题
- 善用日志：`openclaw logs` 过滤关键词找错误
- 按分类排查：启动失败、不响应、配对失败、工具失败各有套路
- 开启 debug 日志拿更多信息
- 本文 checklist 按顺序查，大部分问题很快找到

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
- [第十四章：platforms —— 全平台安装部署指南](./../03-core-concepts/14-platforms.md)
- [第十五章：providers —— 各大模型提供者配置大全](./../03-core-concepts/15-providers.md)
- [第十六章：plugins —— 插件系统开发指南](./../03-core-concepts/16-plugins.md)
- [第十七章： refactor —— OpenClaw 重构原则与工作流](./../03-core-concepts/17-refactor.md)
- [第十八章：reference —— 完整配置、模板、CLI 命令参考](./../03-core-concepts/18-reference.md)
- [第十九章：skills —— 技能系统核心概念与开发指南](./../03-core-concepts/19-skills.md)
- [第二十章：ClawHub —— 技能市场如何分享和获取技能](./../03-core-concepts/20-clawhub.md)
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
- [第三十一章：模型故障转移 (Model Failover) —— 如何提高可用性](./31-failover.md)
- 第三十二章：调试技巧 —— 如何排查 OpenClaw 问题 👈 当前位置
- [第三十三章：成本优化 —— 如何用模型分级降低总成本](./33-cost-optimization.md) 👉 下一章
- [第三十四章：部署运维 —— OpenClaw 网关生产环境最佳实践](./34-deployment.md)
