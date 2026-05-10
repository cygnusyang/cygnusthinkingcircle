# 第三十三章：成本优化 —— 如何用模型分级降低总成本

OpenClaw 原生支持多模型，你可以用**模型分级**把成本降下来，同时保持体验差不多。本章分享实战成本优化技巧。

## 核心思想：模型分级，按任务分配模型

不是什么任务都用最强最贵的模型：

| 模型等级 | 典型模型 | 成本 | 适用任务 |
|----------|----------|------|----------|
| **顶级** | Claude Opus 4.6 / GPT-5 | 最贵 | 复杂推理、深度思考、核心生成 |
| **中级** | Claude Sonnet 4.6 / GPT-4o | 中等 | 工具调用、总结、常规任务 |
| **入门** | Claude Haiku / GPT-4o-mini | 便宜 | 分类、提取、简单问答 |
| **本地** | Llama 3.3 / Qwen 2.5 | 免费 | 简单任务、敏感数据 |

**原则**：能用便宜模型完成的任务，就不用贵的模型。

大多数场景，80% 的任务能用中级和入门模型完成，只有 20% 复杂任务需要顶级模型，总成本能降到原来的 1/3 到 1/5。

## OpenClaw 怎么实现分级

### 1. 不同 Agent 用不同模型

配置写在你的**主配置文件** `~/.openclaw/openclaw.json` 的 `agents.list[]` 下：

```json5
{
  agents: {
    list: [
      {
        id: "main",
        model: {
          primary: "anthropic/claude-opus-4-6",
          fallbacks: ["anthropic/claude-sonnet-4-6"],
        },
      },
      {
        id: "summarizer",
        model: {
          primary: "anthropic/claude-sonnet-4-6",
          fallbacks: ["anthropic/claude-haiku"],
        },
      },
      {
        id: "classifier",
        model: {
          primary: "anthropic/claude-haiku",
          fallbacks: ["ollama/llama3.3:70b"],
        },
      },
    ],
  },
}
```

- 主 Agent 用顶级模型处理复杂对话
- 总结 Agent 用中级
- 分类 Agent 用入门/本地

多智能体架构天然适合成本分级。

### 2. 任务路由，自动选模型

OpenClaw 可以自动判断任务复杂度，选合适模型：

```yaml
- 简单问答 → Haiku / 本地
- 工具调用 → Sonnet
- 复杂推理 → Opus
```

你配置路由规则，系统自动选，不用你每次选。

### 3. 提示缓存省大钱

Anthropic 提示缓存能省很多钱，配置写在你的**主配置文件** `~/.openclaw/openclaw.json` 的 `agents.defaults.models` 下：

```json5
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-opus-4-6": {
          params: {
            cacheRetention: "short", // 或者 "long"
          },
        },
      },
    },
  },
}
```

- 系统提示、常用上下文缓存住
- 只有增量部分收费
- 重复对话省 50-80% 成本

默认已经开了，不用你手动弄。

## 具体场景优化技巧

### 场景 1：多轮对话

**做法：**
- 第一轮用户提问，顶级模型理解意图
- 后续总结上下文用中级模型
- 最后输出顶级模型润色

比全程顶级省 30-40%。

### 场景 2：网页内容总结

**做法：**
- 提取文本 → 本地模型或者 Haiku 分块总结
- 汇总分块总结 → Sonnet
- 输出最终 → 可选 Opus 润色

整个页面总结下来，比直接用 Opus 省 70% 成本，质量差不多。

### 场景 3：批量分类

**做法：**
- 每个项目分类 → Haiku / 本地 足够
- 只有置信度低的拿 Sonnet 重分类

大多数分类 Haiku 准够，成本差 10 倍。

### 场景 4：代码评审

**做法：**
- 提取 diff → Haiku 分类哪些文件需要认真看
- 需要认真看的 → Sonnet 逐文件评审
- 汇总意见 → Opus 整理

省不少，因为很多文件就是简单修改，不用顶级模型。

### 场景 5：实时对话

**做法：**
- 短回答 → 中级模型，响应快成本低
- 长文深度思考 → 顶级模型

不用每次都顶级。

## 本地模型什么时候用

完全免费，适合：

- 简单任务（分类、提取、总结）
- 敏感数据，不能出网
- 批处理任务，量大，云端成本高

配置，写在你的**主配置文件** `~/.openclaw/openclaw.json` 的 `agents.defaults.models` 下：

```json5
{
  agents: {
    defaults: {
      models: {
        "ollama/llama3.3:70b": {
          // 免费，不用配密钥
        },
      },
    },
  },
}
```

70B 本地跑效果接近 GPT-4，成本 0，简单任务尽管用。

## 提示缓存优化

Anthropic 提示缓存真的能省很多钱：

| 不缓存 | 缓存 | 节省 |
|--------|------|------|
| 每次全量收费 | 只有增量收费 | 50-80% |

什么时候用 `long` 缓存（1 小时）：
- 系统提示不变
- 常用工作流上下文重复
- 多轮对话

默认 `short`（5 分钟）对大多数场景够用了。

## 监控成本

OpenClaw 内置成本统计：

```bash
openclaw models cost
```

显示：
- 今天花了多少
- 这个月花了多少
- 每个模型花了多少
- 估计月底会花多少

帮你掌握成本情况，超预算提醒你。

配置告警，写在你的**主配置文件** `~/.openclaw/openclaw.json` 的根级别：

```json5
{
  cost: {
    alerts: [
      {
        monthlyBudget: 50, // 美元
        alertWhenPercent: 80, // 到 80% 告警
      },
    ],
  },
}
```

到点通知你，不会不小心超预算。

## 最佳实践总结

1. **分级**：不同任务不同等级模型，贵的只做难事
2. **缓存**：开提示缓存，重复上下文不重复花钱
3. **本地**：简单任务放本地，完全免费
4. **监控**：看账单，哪个模型费钱，调整分配
5. ** fallback**：故障转移不代表要一直用，主模型好了切回去

## 能省多少钱

举个实例：

| 方案 | 日均成本 | 月成本 |
|------|----------|--------|
| 全程 Opus | $2.5 / 天 | $75 / 月 |
| 分级优化 | $0.6 / 天 | $18 / 月 |

省了 75%，体验下降不到 5%，非常划算。

## 常见问题

**Q: 分级会不会影响质量？**  
A: 大多数任务，便宜模型已经够好，只有真正复杂的才需要顶级。你可以路由，复杂的自动升顶级，体验不影响，成本下来。

**Q: 本地模型性能够吗？**  
A: 现在 70B 模型在 M-series Mac 跑很快，简单任务延迟比云端还低，质量够够用。

**Q: 提示缓存会影响什么吗？**  
A: 没有坏影响，就是省钱，OpenClaw 默认已经开了，直接受益。

## 本章小结

- 模型分级是最有效的成本优化方法：按任务复杂度分配不同模型
- 顶级模型做难事，便宜模型做简单事，总成本能降到 1/3-1/5
- 配合提示缓存、本地模型，进一步省钱
- 内置成本监控和预算告警，不会超支
- 多智能体架构天然适合分级，不同 Agent 用不同模型刚好

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
- [第三十二章：调试技巧 —— 如何排查 OpenClaw 问题](./32-debugging.md)
- 第三十三章：成本优化 —— 如何用模型分级降低总成本 👈 当前位置
- [第三十四章：部署运维 —— OpenClaw 网关生产环境最佳实践](./34-deployment.md) 👉 下一章
