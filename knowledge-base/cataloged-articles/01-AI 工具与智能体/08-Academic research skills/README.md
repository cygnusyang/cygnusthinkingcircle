# 学术研究 AI 协作文具：从原理到实践

一套 20 篇的深度剖析，解读 [Academic Research Skills (ARS)](https://github.com/Imbad0202/academic-research-skills) —— Claude Code 上最完整的学术研究技能包。从人机协作的底层哲学出发，到 13 个 Agent 的分布式研究、12 个 Agent 的论文撰写、7 个审查者的多视角同行评议，再到 10 阶段管线的调度与诚信保障。

## 适合谁读

- 想理解 **AI 辅助学术研究的边界与可能** 的研究者
- 正在使用或准备尝试 ARS 的研究生和学术工作者
- 对多 Agent 协作系统架构感兴趣的技术读者

每篇文章 2000–4000 字，独立可读，也适合按顺序通读。

## 目录

### 第一部分：理念与哲学

| # | 文章 | 简介 |
|---|------|------|
| 01 | [为什么是人机协作，而非全自动？](01-philosophy/01-why-human-ai-collaboration.md) | 从 Lu 等人（2026）*Nature* 论文出发，讨论全自动 AI 研究系统的结构性失败模式，以及"研究者 + AI"为何是更优路径 |
| 02 | [AI 研究的七类失败模式](01-philosophy/02-ai-research-failure-modes.md) | 详解 ARS 识别的 7 类阻断式检查清单：实施错误、幻觉结果、取巧依赖、错误包装、方法伪造、框架锁定、引用幻觉 |

### 第二部分：安装与配置

| # | 文章 | 简介 |
|---|------|------|
| 03 | [30 秒安装与五种部署方式](02-setup/03-installation-setup.md) | Plugin 安装、symlink 部署、claude.ai Project 注入等五种方式的完整指南，含前置条件与验证 |
| 04 | [Token 预算与成本控制](02-setup/04-performance-cost.md) | 各模式 token 消耗估算、完整 pipeline 约 $4–6 的成本拆解、Skip Permissions 与 Agent Team 配置建议 |

### 第三部分：架构总览

| # | 文章 | 简介 |
|---|------|------|
| 05 | [Pipeline 架构全景](03-architecture/05-pipeline-architecture.md) | 10 阶段管线流程图解、阶段×维度矩阵、数据访问层级（raw/redacted/verified_only）、Skill 依赖图 |
| 06 | [四大技能一览](03-architecture/06-four-skills-overview.md) | Deep Research、Academic Paper、Academic Paper Reviewer、Academic Pipeline 各自定位、输入输出与协作关系 |

### 第四部分：Deep Research 深度研究

| # | 文章 | 简介 |
|---|------|------|
| 07 | [13 个 Agent 的研究团队](04-deep-research/07-13-agents-team.md) | 逐一剖析每个 Agent 的职责与交互：从 RQ 定义到报告编译的完整链路 |
| 08 | [七种研究模式实战](04-deep-research/08-seven-modes-in-action.md) | full / quick / socratic / systematic-review / fact-check / lit-review / review 模式的选择指南与使用场景 |

### 第五部分：Academic Paper 论文撰写

| # | 文章 | 简介 |
|---|------|------|
| 09 | [12 个 Agent 的写作团队](05-academic-paper/09-12-agents-writing-team.md) | 从 intake 到 formatter，12 个 Agent 如何分工协作完成论文初稿 |
| 10 | [十种写作模式详解](05-academic-paper/10-ten-modes-in-action.md) | full / plan / outline-only / revision / revision-coach / abstract-only / lit-review / format-convert / citation-check / disclosure |
| 11 | [风格校准与写作品质](05-academic-paper/11-style-calibration-quality.md) | 通过历史论文学习个人写作风格、5 大类 AI 写作品质检查、反泄漏协议与 VLM 图表验证 |

### 第六部分：Academic Paper Reviewer 论文审查

| # | 文章 | 简介 |
|---|------|------|
| 12 | [七个审查 Agent 的多视角评审](06-reviewer/12-7-reviewer-agents.md) | EIC + 3 位动态评审 + 魔鬼代言人 + 编辑综合者的角色设计、互动机制与 0-100 品质量表 |
| 13 | [六种审查模式与 Sprint Contract](06-reviewer/13-six-review-modes.md) | full / re-review / quick / methodology-focus / guided / calibration 模式详解，以及 v3.6.2 引入的预承诺协议 |

### 第七部分：Academic Pipeline 调度器

| # | 文章 | 简介 |
|---|------|------|
| 14 | [10 阶段编排详解](07-pipeline/14-10-stage-orchestration.md) | 从 Stage 1 研究到 Stage 6 过程记录的完整流转，含 checkpoint 机制与决策分支 |
| 15 | [诚信闸门：Stage 2.5 与 Stage 4.5](07-pipeline/15-integrity-gates.md) | 不可跳过的 7 类失败模式检查、100% 声明验证、Compliance Agent 与 PRISMA-trAIce 整合 |
| 16 | [Material Passport：跨会话的状态护照](07-pipeline/16-material-passport.md) | Schema 9 设计、literature_corpus[] 输入端口、adapter 体系、reset boundary 重置机制与 repro_lock |

### 第八部分：进阶话题

| # | 文章 | 简介 |
|---|------|------|
| 17 | [跨模型验证：用 GPT 审 Claude](08-advanced/17-cross-model-verification.md) | `ARS_CROSS_MODEL` 的底层协议：30% 抽样检查、独立 DA 批评、跨模型分歧标注 |
| 18 | [苏格拉底导师与 SCR 协议](08-advanced/18-socratic-mentor-scr.md) | State-Challenge-Reflect 反思循环、意图侦测（探索型 vs. 目标型）、对话健康度监控 |
| 19 | [反谄媚系统：让 AI 学会说不](08-advanced/19-anti-sycophancy.md) | 魔鬼代言人让步门槛（≥4/5）、攻击强度保持、框架锁定侦测、AI 自我反思报告 |
| 20 | [Experiment Agent 生态与未来展望](08-advanced/20-experiment-agent-ecosystem.md) | Experiment Agent 如何填补 Stage 1→2 实验空白、与 ARS 的协议对接、社区贡献与路线图 |

## 阅读建议

- **快速了解 ARS**：01 → 05 → 06，约 30 分钟
- **准备使用 ARS**：03 → 04 → 07 → 08 → 12 → 14，约 90 分钟
- **深入理解设计**：全部 20 篇顺序阅读，约 6 小时
- **针对特定技能**：直接跳转到对应章节（第四至第八部分）

## 版本说明

所有文章基于 **ARS v3.7.0**（2026-05-05 发布）。文章之间通过相对链接互相关联，克隆本仓库后即可在本地 Markdown 阅读器中导航。
