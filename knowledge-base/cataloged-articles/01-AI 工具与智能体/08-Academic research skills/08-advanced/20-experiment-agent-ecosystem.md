# Experiment Agent 生态与未来展望

在 ARS 的 pipeline 中，Stage 1（Research）和 Stage 2（Writing）之间有一个隐含的空白：如果你的研究需要**跑实验**（代码实验或人工研究）来产生数据，这部分工作不属于 Deep Research（它是文献调研，不跑代码），也不属于 Academic Paper（它是写作，不产生新数据）。

[Experiment Agent](https://github.com/Imbad0202/experiment-agent) 就是填补这个空白的技能——它不替代 ARS 的任何组件，而是在 Stage 1 和 Stage 2 之间插入一个可选的实验执行与管理层。

这篇收官之作不仅介绍 Experiment Agent 如何与 ARS 对接，也讨论了 ARS 的社区生态现状和未来方向。

## Experiment Agent：填补 Stage 1→2 的空白

### 定位

```
ARS Stage 1: RESEARCH     →  RQ Brief + Methodology Blueprint
           ↓
  experiment-agent         →  执行/管理实验 → 验证结果
           ↓
ARS Stage 2: WRITE         →  用验证过的实验数据撰写论文
```

### 功能

**代码实验管理**：
- 执行 Python、R 等语言的实验代码并实时监控
- 检测 11 种统计谬误（如 p-hacking、HARKing、多重比较未校正、选择性报告等）
- 可复现性验证——确保相同的代码和输入产生相同的输出

**人工研究管理**：
- 管理研究 protocol 和 IRB 伦理审查
- 数据收集进度追踪
- 参与者管理和知情同意文档

### 与 ARS 的对接

Experiment Agent 和 ARS 是两个独立的 Claude Code Skill，通过 **Material Passport 协议** 对接：

1. ARS Stage 1 完成后，产出 RQ Brief + Methodology Blueprint → 用户将 Material Passport 传给 Experiment Agent session
2. Experiment Agent 根据 Methodology Blueprint 设计实验、执行、验证结果
3. 实验完成后的结果（数据、分析、验证报告）写回 Material Passport
4. ARS Stage 2 消费更新后的 Material Passport，用验证过的实验数据撰写论文

**ARS 本身不需要任何修改**——对接是通过 Material Passport 这个中间层完成的，两个 Skill 各自独立运行。

这体现了 ARS 架构的核心理念：**组合优于集成**。新功能通过协议对接加入生态，而非修改现有代码。

---

## ARS 的版本演进：从 v1.0 到 v3.7.0

回顾 ARS 的版本历史，可以看到一条清晰的设计思路演进：

| 版本 | 关键创新 | 设计主题 |
|------|---------|---------|
| v1.0 (2026-02) | 4 Skill 初版发布 | 基础功能覆盖 |
| v2.0 (2026-02) | 5→9 阶段 Pipeline、魔鬼代言人 | 管线化 + 质疑机制 |
| v2.6–2.9 (2026-03) | SCR 协议、风格校准、写作品质检查 | 反思 + 学习 |
| v3.0 (2026-04) | 反谄媚系统、跨模型验证 | 行为约束 + 外部纠偏 |
| v3.1 (2026-04) | 抗 Context Rot、认知框架 | 系统健壮性 |
| v3.2 (2026-04) | Lu 2026 7 类失败模式 | 学术诚信基础设施 |
| v3.3 (2026-04) | PaperOrchestra 技术整合 | 外部验证取代内部信任 |
| v3.4–3.5 (2026-04) | Compliance Agent + 协作深度观察 | 合规 + 元认知 |
| v3.6.2–3.6.8 (2026-04/05) | Sprint Contract + Generator-Evaluator 合约 | 预承诺防偏误 |
| v3.7.0 (2026-05) | Claude Code Plugin 打包 | 分发方式升级 |

一条贯穿的主题：**从"让 AI 做更多"到"让 AI 做得更可信"**。早期版本的焦点是功能覆盖（更多 Agent、更多模式）；后期版本的焦点几乎全部在诚实性基础设施上——预承诺协议、反谄媚系统、失败模式检测、跨模型验证。

---

## 社区贡献

ARS 是开源项目（CC BY-NC 4.0），接受社区贡献：

- **[@aspi6246](https://github.com/aspi6246)**：v3.1 的设计灵感来自其 [Claude-Code-Skills-for-Academics](https://github.com/aspi6246/Claude-Code-Skills-for-Academics) 项目的三个原则：唯读约束、Anti-Pattern 作为一等公民、认知框架方法
- **[@mchesbro1](https://github.com/mchesbro1)**：提出并撰写了 IS Basket of 8 期刊清单
- **[@cloudenochcsis](https://github.com/cloudenochcsis)**：将 IS 期刊列表从 Basket of 8 扩展为完整的 Senior Scholars' Basket of 11

---

## 已知限制与未来方向

### 当前限制

1. **LLM 输出的非确定性**：ARS 不保证完全相同的输入产生完全相同的输出。`repro_lock` 是文档，不是可执行重播。

2. **Pipeline 编排器的单 session 局限**：ARS 依赖 Material Passport 做跨 session 恢复，但没有自己的持久化编排器状态。

3. **跨模型验证的可选性**：设为可选环境变量意味着大多数用户不会使用它。

4. **Codex Audit Hook 的延迟**：v3.7.0 因技术 contract gap 而推迟了自动跨模型审计的集成。

5. **文献库集成的 partial coverage**：`citation_compliance_agent` 的 corpus 集成被推迟到 v3.6.6+。

### 未来方向

从 ARS 的版本路线图和文档中的 forward notes 来看，以下方向可能在未来版本中出现：

1. **更广泛的 Plugin Agent 覆盖**：v3.7.0 只暴露了 3 个 plugin agent。更多的下游 agent 可能在未来版本中被暴露为 plugin-shipped agent。

2. **Stage/Deliverable Propagation Contract**：v3.7.0 的 codex audit hook 延期正是因为缺乏这个 contract。一旦实现了阶段和交付物的传播协议，自动审计就可以在 hook 层面集成。

3. **Generator-Evaluator 合约的扩面**：v3.6.8 的合约目前仅在 `academic-paper full` 模式中启用。未来可能扩展到更多模式。

4. **跨语言支持改善**：虽然意图匹配使得 Socratic 和 Plan 模式在任何语言下都能工作，但 Skill 触发关键词仍以英文和繁中为主。更多语言的触发关键词支持可以改善访问性。

5. **与外部工具更深的集成**：Zotero 的 live sync（而非 export-import）、Overleaf 的 API 集成、institutional repository 的直接对接——这些是社区讨论中提到但尚未实现的方向。

---

## 系列终章：一些关于人机协作的思考

本系列从 Lu 等人（2026）的全自动 AI 研究系统出发，以 20 篇文章的篇幅剖析了一个选择人机协作路线的学术研究工具。回到最初的问题：

**AI 应该替研究者做多少？**

ARS 的回答是：AI 应该做那些它可以**做得更准确**的事——验证引用是否存在、检查方法论是否自洽、识别数据与论文之间的不一致。但 AI 不应该做那些需要**人类判断**的事——定义什么问题是值得研究的、选择什么方法是适合的、解释数据对理论和实践的意义。

这个边界在实践中是模糊的。ARS 的 10 个人类决策 checkpoint、2 个诚信闸门、4 类预承诺协议——这些机制的本质，就是在模糊的边界上反复确认：**这是你应该做的决定，不是 AI 应该做的决定。**

ARS 的设计者说得好："AI 是你的副驾驶，不是机长。"工具帮你处理苦工，但论文中那句"我认为"后面是什么，仍然是你在写。

---

**全系列完。**

感谢阅读。如果你发现任何错误或有改进建议，欢迎在 [GitHub](https://github.com/Imbad0202/academic-research-skills) 上提出 Issue 或 PR。

**参考来源**：
- `source/academic-research-skills/CHANGELOG.md`（完整版本历史）
- `source/academic-research-skills/CONTRIBUTING.md`
- [Experiment Agent](https://github.com/Imbad0202/experiment-agent)
- Lu et al. (2026). *Nature* 651, 914-919
