# 第八章：为什么你需要一个多智能体框架 —— 单智能体的困境

你是否有过这样的经历：

用大模型帮你处理一个比较复杂的任务，一开始进展顺利，但是随着任务推进，模型开始"健忘"——前面已经讨论清楚的设计决策，后面又忘了，需要你反复提醒；改完了 A 部分，又把 B 部分改错了；想让它同时处理需求分析、代码编写、测试用例，结果每个部分都写得马马虎虎。

如果你用过 Claude Code 或者其他 AI 编程助手，你一定深有体会。

## 单智能体的困境

当我们用大模型处理复杂任务时，我们默认都是"单智能体模式"——一个对话窗口，一个模型，从头到尾处理整个任务。这种方式在任务简单的时候工作得很好，但是当任务变得复杂，问题就来了：

### 1. 上下文溢出与健忘症

让我们算一笔账：一个中等复杂度的功能开发，大概需要：

- 需求分析：~1000 tokens
- 架构设计：~2000 tokens  
- 代码编写：~5000 tokens
- 测试用例：~2000 tokens
- 调试修复：~3000 tokens

加起来就已经 **13000 tokens** 了。这还不包括来回的对话。如果你用的是 Claude 3.5 Sonnet（200k context），看起来好像够，但是随着对话进行，上下文会越来越满，模型注意力会被稀释。

更糟糕的是，**上下文窗口不是这样用的**。当整个对话都在一个上下文中，模型需要在回答你的当前问题时，从几万 tokens 里面找相关信息。它不是电脑内存，可以精确寻址——它是靠注意力机制，很容易就"注意"错地方，或者干脆忘了早期重要的决策。

> 我见过太多次：开发者和 AI 聊了两个小时，改了十几轮，最后 AI 把一开始说好的核心设计要求给忘了，从头来了一遍。

### 2. 注意力分散，多任务同时掉线

你让 AI 同时做需求分析 + 代码编写 + 编写测试，会发生什么？

答案是：每个部分都做不好。

因为模型的注意力是有限的。当它需要同时关注多个不同目标时，每个目标分到的注意力就不够了。需求分析不够深入，代码有边界 case 没处理，测试用例覆盖不全——最后你还是得一个个重新检查一遍。

**一个脑袋同时干几件事，每件事都干不好。** 这对人是这样，对当前的大模型也是这样。

### 3. 角色混淆，职责不清

当你需要一个"架构师"和一个"工程师"协作，你能不能在同一个对话里让同一个模型扮演两个角色？

理论上可以，你可以说"现在你扮演架构师...好了，现在你扮演工程师..."，但实践中：

- 模型容易"串戏"——架构师的思考混入工程师的实现
- 无法给不同角色配置不同的模型——架构师可能需要 Opus，工程师可以用 Sonnet，单智能体做不到
- 无法独立并行工作——必须等架构师说完，工程师才能开始，不能同时干活

### 4. 错误传染，一处出错全盘皆输

如果需求分析错了，后面的代码编写、测试全错。在单智能体模式下，所有东西都混在一起，你很难把错误限制在局部，往往需要从头再来。

没有隔离，就没有"容错"。

### 5. 无法并行，等待时间太长

单智能体从头到尾顺序执行，你给它三个任务，它得一个一个来。你只能等着。如果三个任务可以并行，十分钟就完事，顺序执行可能需要三十分钟。

## 分工与协作才是解决之道

其实这个问题人类社会早就解决了——**分工协作**。

一个软件项目不会让一个人干所有活：需求分析师梳理需求，架构师设计架构，工程师写代码，测试工程师写测试用例。每个人专注自己擅长的领域，最后拼在一起。

这个道理对 AI 也一样。

**多智能体协作的本质，就是给 AI 做分工：**

- **专业化**：不同的子任务交给不同的智能体，每个智能体专注做好一件事
- **隔离性**：每个智能体有自己独立的会话上下文，不会互相干扰，出错了也容易定位和修复
- **可并行**：多个子任务可以同时运行，节省时间
- **可配置**：不同智能体可以用不同的模型、不同的思考级别、不同的工具权限，适配任务需求

## OpenClaw 的回答：sessions_spawn

OpenClaw 对这个问题的回答非常简洁——**用 `sessions_spawn` 这个核心原语，让一个智能体可以生成另一个隔离的智能体来干活**。

这就是多智能体协作的起点：

```json
{
  "name": "sessions_spawn",
  "parameters": {
    "task": "帮我 review 这段代码，重点关注安全性和性能",
    "agentId": "code-reviewer",
    "model": "anthropic/claude-3-5-sonnet",
    "thinking": "high",
    "mode": "run"
  }
}
```

就这么简单。主智能体调用 `sessions_spawn` 生成一个子智能体，子智能体在隔离环境中完成任务，完成后自动把结果汇报回来。

## 本章小结

- 单智能体模式在复杂任务下会遇到**上下文溢出、注意力分散、角色混淆、错误传染、无法并行**五大痛点
- 解决之道就是**分工协作**——让专业的人（智能体）干专业的事
- OpenClaw 通过 `sessions_spawn` 这个核心原语，让智能体可以生成隔离的子智能体
- 下一章我们深入讲解 `sessions_spawn` 到底是什么，每个参数是什么意思，什么时候该用什么参数

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
- 第八章：为什么你需要一个多智能体框架 —— 单智能体的困境 👈 当前位置
- [第九章：sessions_spawn —— 多智能体协作的核心原语](./09-sessions-spawn-core-primitive.md) 👉 下一章
- [第十章：协作架构模式 —— 从 Master-Worker 到 Hub-and-Spoke](./10-collaboration-architecture-patterns.md)
- [第十一章：隔离设计 —— 为什么每个子智能体需要独立会话](./11-isolation-design.md)
- [第十二章：嵌套协作 —— 如何实现 Orchestrator-Worker 模式](./12-nested-collaboration.md)
- [第十三章：实践案例 —— 从零构建一个代码评审团队](./13-practical-case-code-review-team.md)
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
- [第三十一章：模型故障转移 (Model Failover) —— 如何提高可用性](./../07-ops-best-practices/31-failover.md)
- [第三十二章：调试技巧 —— 如何排查 OpenClaw 问题](./../07-ops-best-practices/32-debugging.md)
- [第三十三章：成本优化 —— 如何用模型分级降低总成本](./../07-ops-best-practices/33-cost-optimization.md)
- [第三十四章：部署运维 —— OpenClaw 网关生产环境最佳实践](./../07-ops-best-practices/34-deployment.md)
