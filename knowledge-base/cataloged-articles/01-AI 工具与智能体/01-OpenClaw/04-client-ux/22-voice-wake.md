# 第二十二章：语音唤醒 (Voice Wake) —— 语音交互体验

语音唤醒是 OpenClaw 的 **always-ready** 交互模式，设备一直监听，你说唤醒词就直接响应，不用手动点按钮。本章介绍语音唤醒的配置、工作原理和最佳实践。

## 什么是语音唤醒

语音唤醒 = **离线监听 + 关键词触发 + 语音对话**：

- **离线监听**：关键词检测在本地运行，不上传云端，保护隐私
- **低功耗**：待机功耗很低，可以一直开着
- **一键触发**：说"Hi Claude"（自定义关键词）就唤醒开始对话
- **语音转文字 + 文字转语音**：全链路语音交互

解放双手，场景对了效率比打字高很多。

## 使用场景

### 1. 智能家居中控

你在家里走动，随口问：
- "今天天气怎么样？"
- "把客厅灯调到 50% 亮度"
- "帮我点一杯咖啡到公司"

不用找手机，不用开 APP，张口就来。

### 2. 编程时查资料

手上沾着键盘：
- "这个错误 `NullPointerException` 一般是什么原因？"
- "帮我写一个快排的 Go 实现"
- "OpenClaw 怎么配置 fallback？"

不用停下来洗手摸鼠标，直接问。

### 3. 开车时助手

导航、发消息、查日程：
- "导航到最近的加油站"
- "明天早上 9 点开会提醒我"
- "回短信说'我十分钟到'"

安全驾驶，不用动手。

### 4. 厨房做菜

查菜谱、计时：
- "300 克面粉是多少毫升？"
- "帮我计 5 分钟计时器"
- "这个菜放盐还是放糖？"

手沾着面粉不用碰屏幕。

## 配置

### 硬件要求

- **麦克风**：可用就行，普通笔记本麦克风够用
- **性能**：关键词检测占用不到 10% CPU，现代设备都没问题
- **网络**：唤醒后语音识别需要网络，离线识别也支持但准确度低一点

### 快速开启

```bash
# 交互式配置
openclaw onboard voice-wake
```

跟着向导走：
1. 选择语音识别提供者（OpenAI Whisper / OpenClaw 离线 / 第三方）
2. 训练唤醒词（说三遍，让模型适应你的声音）
3. 设置灵敏度
4. 启动监听

就好了。

### 配置文件示例

语音唤醒配置写在你的**主配置文件** `~/.openclaw/openclaw.json` 的 `plugins.entries` 下：

```json5
{
  plugins: {
    entries: {
      "voice-wake": {
        enabled: true,
        config: {
          // 唤醒词
          wakePhrase: "Hi Claude",
          // 灵敏度 0-1，越高越容易唤醒，但误唤醒也多
          sensitivity: 0.5,
          // 监听模式
          mode: "continuous", // continuous | push-to-talk
          // 连续监听模式下，听多久超时
          idleTimeoutSeconds: 30,
          // 语音识别
          asr: {
            provider: "openai/whisper", // 或者 "whisper-local" 离线
            model: "whisper-1",
          },
          // 文字转语音
          tts: {
            provider: "openai",
            voice: "alloy",
          },
        },
      },
    },
  },
}
```

### 两种模式

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| `continuous` | 一直监听，唤醒词触发 | 家居中控、一直开着 |
| `push-to-talk` | 按键说话，不持续监听 | 隐私敏感，偶尔用 |

### 自定义唤醒词

你可以改成任何关键词：

- "OK Computer"
- "Hey Assistant"
- "Jarvis"
- 中文也支持："你好小爪"（OpenClaw → 小爪）

训练：

```bash
openclaw voice-wake train "你好小爪"
```

按照提示说三遍，生成个性化模型。

## 工作原理

### 分层架构

```
麦克风音频流 → 本地 VAD 检测 → 唤醒词检测 → 唤醒 → ASR 转文字 → Gateway 处理 → TTS 转语音 → 扬声器播放
```

**VAD**：语音活动检测，检测有没有人说话，没人说话不处理，省功耗。

**唤醒词检测**：本地运行小模型，只检测关键词，不是关键词直接丢，不上传。

只有检测到唤醒词才会：
1. 开始录音整段话
2. 上传做 ASR 识别
3. 处理完 TTS 返回播放

所以**大部分时间数据都不出去，隐私友好**。

### 本地 vs 云端

| 选项 | 唤醒词检测 | ASR 识别 | TTS | 优点 | 缺点 |
|------|------------|-----------|-----|------|------|
| 全云端 | ❌ 云端 | 云端 | 云端 | 准确，省本地功耗 | 必须联网，延迟高，隐私差 |
| 混合（推荐） | ✅ 本地 | 云端 | 云端 | 隐私好，唤醒快，识别准 | 需要联网才能识别 |
| 全本地 | ✅ 本地 | ✅ 本地 | ✅ 本地 | 完全离线，隐私最好 | 需要较大内存，准确度低一点 |

OpenClaw 默认混合模式，平衡隐私和体验。

## 最佳实践

### 1. 选择合适的灵敏度

- **环境安静**：灵敏度可以高一点 (0.6-0.7)
- **环境嘈杂**：灵敏度低一点 (0.3-0.4)
- **误唤醒多**：降灵敏度，或者换更特别的唤醒词
- **唤不醒**：升灵敏度，或者训练的时候发音清楚一点

### 2. 唤醒词选择技巧

- ✅ 两到三个音节，太短容易误触发，太长难记
- ✅ 不常用词，日常对话很少说到，减少误唤醒
- ✅ 发音清晰，每个音节反差大，容易检测
- ❌ 太短（一个音节），容易误触发
- ❌ 太长（五个音节以上），说起来累

**好例子**："Hi Claude"（2音节）、"你好小爪"（4音节）

### 3. 摆放麦克风

- 朝向你说话的方向
- 离空调、冰箱、抽油烟机等噪音源远一点
- 笔记本内置麦克风够用，想要更好体验可以外接麦克风

### 4. 语音对话技巧

- 一句话说清楚需求，不要停顿太久
- 环境噪音大的时候靠近一点说
- 说完停顿一下，等检测结束，不用抢话

## 隐私说明

语音唤醒设计隐私优先：

1. **唤醒词检测完全本地**——音频不离开设备
2. **只有唤醒后**才会上传整段语音做识别
3. **识别完删除原音频**——OpenClaw 不存储你的语音
4. **推送说话模式**——不用时候不监听，完全隐私

如果你选全本地模式，**语音数据从来不离开你的设备**，真正隐私彻底保护。

## 故障排查

**问题：频繁误唤醒**
- 解决：降低灵敏度，换一个不常用的唤醒词，麦克风远离喇叭播放音乐的地方

**问题：总是唤不醒**
- 解决：提高灵敏度，重新训练唤醒词（发音清楚一点），麦克风靠近一点

**问题：唤醒了但识别不对**
- 解决：检查网络，换更大的 ASR 模型，说话慢一点清楚一点

**问题：CPU 占用太高**
- 解决：检查是不是用了太大的本地模型，唤醒词检测本身不占资源，大模型才占

## 本章小结

- 语音唤醒提供 hands-free 全链路语音交互
- 混合架构设计：本地检测唤醒词，云端做识别合成，平衡隐私和体验
- 支持自定义唤醒词，两种模式（持续监听/按键说话）
- 适合智能家居、做饭、开车、双手不空等场景
- 隐私设计优先，默认不上传音频，全本地模式可选

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
- [第二十一章：Canvas A2UI —— 实时可视化协作 workspace](./21-canvas.md)
- 第二十二章：语音唤醒 (Voice Wake) —— 语音交互体验 👈 当前位置
- [第二十三章：WebChat —— Gateway WebSocket 聊天界面](./23-webchat.md) 👉 下一章
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
