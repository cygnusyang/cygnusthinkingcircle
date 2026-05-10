# 为什么是人机协作，而非全自动？

2025 年 3 月，Lu 等人在 *Nature* 上发表了一篇引发广泛讨论的论文：**The AI Scientist**——第一个通过同行盲审的端到端全自动 AI 研究系统。它独立完成了从研究构思、实验设计、代码编写、结果分析到论文撰写的全过程，其生成的论文在 ICLR 2025 workshop 的盲审中获得了 6.33/10 的评分（workshop 平均分 4.87）。

这听起来像是 AI 取代研究者的序幕。但 Lu 等人自己写了这篇论文的 **Limitations（局限性）** 章节，其中列出的一系列结构性失败模式，恰恰为"为什么我们仍然需要人在回路中"提供了最有力的论据。

## 全自动的诱惑与陷阱

全自动 AI 研究系统解决了一个真实痛点：学术写作中大量重复性劳动——文献检索、格式排版、引用管理、数据验证——消耗了研究者本应用于思考的时间。如果能把这些交给 AI，研究者就能专注于定义问题、选择方法、解释数据的意义。

但 Lu 等人的实验暴露了一类更隐蔽的失败：**看起来像好研究的坏研究**。

一个包含幻觉实验结果的论文，读起来和真实论文一模一样。一个利用了取巧特征（而非真正学会泛化）的模型，在数值指标上可能表现优异。一个描述从未实际运行的实验的 Method 段落，措辞上与忠实记录无从区分。

传统学术质量控制的两个支柱——同行评审和可复现性——在面对这类失败时都显得力不从心。同行评审者看不到底层代码和实验日志，无法区分"声称的实验"和"实际运行的实验"。可复现性依赖于作者诚实发布数据和代码，但一个看似合理的假结果可能在被质疑之前已经进入了文献。

## ARS 的答案：在每一步设置人类确认点

Academic Research Skills (ARS) 的设计前提是：**人类研究者 + AI 的组合，比纯自动或纯人工都更能避开这些失败模式**。

这不仅仅是"AI 干活，人类检查"的流水线。ARS 的 pipeline 设计将人类确认嵌入到了每一个关键决策点：

- **Stage 1（研究）**：AI 提出研究问题和方法论蓝图，**你**确认方向
- **Stage 2（写作）**：AI 撰写大纲和初稿，**你**批准大纲后才开始动笔
- **Stage 2.5（诚信审查）**：AI 对论文执行 7 类失败模式检查，**你**审阅诚信报告并决定是否通过
- **Stage 3（同行评审）**：AI 模拟多视角评审，**你**做出编辑决定（接受/小修/大修/退稿）
- **Stage 4.5（最终诚信审查）**：AI 以零容忍标准重新验证，**你**做最终确认

关键设计在于：**AI 不能跳过任何人机交互检查点**。Stage 2.5 和 Stage 4.5 的诚信闸门在代码层面是不可绕过的——即使你说了"我相信 AI 的判断"，系统仍然要求你逐条审阅检查结果。

## 不是遮掩，而是把关

市面上有一些"AI humanizer"工具，专门用于改写 AI 生成的文本，使其看起来像是人类写的。这类工具的隐含前提是：使用 AI 辅助写作是需要隐藏的事情。

ARS 的立场完全不同。它不仅不帮你隐藏 AI 参与的事实，还提供了针对特定期刊（Nature、Science、ICLR、NeurIPS、ACL、EMNLP）的 **AI 使用揭露声明生成器**（/ars-disclosure），让研究者合规、诚实地报告 AI 在论文创作中的角色。

> ARS v3.1 的灵感来自 [aspi6246/Claude-Code-Skills-for-Academics](https://github.com/aspi6246/Claude-Code-Skills-for-Academics) 的三个设计原则：唯读约束（reviewer 不能修改论文原稿）、Anti-Pattern 作为一等公民设计（明确列出"不要做什么"而非仅说"要做什么"）、以及认知框架方法（教 Agent "如何思考"而非只是步骤清单）。

在风格校准（Style Calibration）方面，ARS 走了另一个方向：它从你过去的论文中**学习你的写作风格**——句子节奏、词汇偏好、引用整合方式——然后在写作时作为软性指引使用。但优先级系统是：学科规范（硬性）> 期刊惯例（强）> 个人风格（软性）。风格校准的目的是让 AI 的协助更贴合你的声音，而非让你隐藏 AI 的参与。

## PaperOrchestra 的启发

ARS v3.3 的多个技术强化来自 [PaperOrchestra](https://arxiv.org/abs/2604.05018)（Song, Song, Pfister & Yoon, 2026, Google）：

- **Semantic Scholar API 验证**：用程序化方式批量验证引用的存在性（标题 Levenshtein 匹配 ≥0.70、DOI 一致性检查），而非依赖 LLM 的"记忆"
- **反泄漏协议**：知识隔离——优先使用 session 内材料，缺失内容标记为 `[MATERIAL GAP]` 而非让 LLM 用训练数据填补
- **VLM 图表验证**：用视觉模型对生成的图表做 10 项闭环保真检查

这些技术的共同特征：**用外部验证取代内部信任**。程序化检查不相信 AI 的判断，API 调用不相信 AI 的记忆，视觉模型不相信 AI 生成的图表——每一个 AI 产出都由另一个独立的系统交叉验证。

## 人机协作的边界在哪里？

ARS 的设计并不回避一个重要问题：人机协作的质量取决于人类的学术判断力。如果你跳过了诚信闸门中的每一条警告，如果你在魔鬼代言人指出方法论缺陷时一律选择"忽略"，如果你在所有 checkpoint 都机械地点击"继续"——那么 ARS 最终输出的论文质量，不会比全自动系统更好。

这也是为什么 ARS 在 v3.5.0 中加入了 **协作深度观察员（Collaboration Depth Observer）**：一个纯咨询性的 Agent，在每次 checkpoint 时评估你与 AI 的协作模式——你是真正在思考（Zone 1）、部分依赖（Zone 2）、还是完全将认知责任外包给了 AI（Zone 3）。它从不阻止 pipeline 推进，但会将评估写入最终的 Stage 6 过程记录中。

换言之，ARS 不会阻止你做出糟糕的学术决策。但它会记录这些决策，让你在最后面对一份诚实的协作评估报告。

## 下一步

理解了"为什么是人机协作"之后，下一篇我们将深入剖析 Lu 等人识别的 7 类 AI 研究失败模式，看 ARS 如何在 Stage 2.5 和 Stage 4.5 的诚信闸门中逐一设防。

[下一节：AI 研究的七类失败模式](02-ai-research-failure-modes.md)

---

**参考来源**：
- Lu et al. (2026). Towards end-to-end automation of AI research. *Nature* 651, 914-919
- Song, Song, Pfister & Yoon (2026). PaperOrchestra. arXiv:2604.05018
- `source/academic-research-skills/academic-pipeline/references/ai_research_failure_modes.md`
- `source/academic-research-skills/shared/style_calibration_protocol.md`
- `source/academic-research-skills/shared/anti_leakage_protocol.md`
