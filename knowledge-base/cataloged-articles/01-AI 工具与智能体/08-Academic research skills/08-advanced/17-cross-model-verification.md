# 跨模型验证：用 GPT 审 Claude

AI 模型有各自的"盲点"和"偏好"。同一个模型既写论文又审论文，即使有 Generator-Evaluator 合约和 Sprint Contract 预防后见之明偏误，仍可能存在**模型家族内的系统性盲区**——某个模式在 Claude 的评估中看起来合理，但换成 GPT 或 Gemini 的视角就暴露了问题。

跨模型验证（Cross-Model Verification）是 ARS 对这个问题的答案：**可选地启用第二 AI 模型，作为独立审查者验证 Claude 的输出。**

## 原理

当你设置 `ARS_CROSS_MODEL=1` 环境变量时，ARS 在关键节点的诚信检查中调用第二模型：

1. **诚信抽样验证**：Stage 2.5 的 30% 声明抽样中，部分声明由第二模型独立验证，然后与 Claude 的验证结果对比
2. **独立 DA 批评**：在 Stage 3 的魔鬼代言人评审中，第二模型对论文的核心论点进行独立攻击，然后与 Claude DA 的攻击对比
3. **分歧标注**：如果两个模型在同一问题上得出不同结论，这个分歧被显式标注而非被"平均掉"

**未设置此变量时，零开销**。第二模型的 API 调用只在标志启用时发生。

## 为什么是"标注分歧"而不是"投票决定"？

一个自然的问题：如果两个模型意见不一致，为什么不投票？让第三个模型来打破平局？

ARS 的设计选择是：**标注分歧，但不自动解决分歧**。原因：

1. **对齐不确定性**：不同 AI 模型有不同的对齐训练，对"什么是好论文"的判断本身就不同
2. **模型能力差异**：在某些学术领域，一个模型可能比另一个模型更可靠——但这不是全局的
3. **人类决策留存**：分歧的意义是"这里有值得你注意的不确定性"，而不是"AI 帮你选了一个"

分歧被标注为 `cross_model_divergence`，写入诚信报告，由人类研究者在 checkpoint 确认时阅读和判断。

## 协作深度观察员中的跨模型分歧

v3.5.0 的 Collaboration Depth Observer 在跨模型模式下同时运行在两个模型上。如果任一维度上两个模型的评分差异 > 2 分：

```
cross_model_divergence:
  dimension: "Cognitive Vigilance"
  claude_score: 7
  cross_model_score: 4
  note: "GPT 认为用户在 Zone 3（完全外包认知），Claude 认为在 Zone 2（部分依赖）。分歧源：GPT 将用户的连续同意解读为放弃思考，Claude 将同一信号解读为被引导后的认可。"
```

跨模型分歧是**最值得人类注意的信号**——它标识出了 AI 之间也无法达成一致的地方。

## 成本控制

跨模型验证的成本：
- 完整 pipeline 增量：+~$0.60–1.10
- 主要由外部模型的 API 调用驱动（GPT-5.4 Pro 或 Gemini 3.1 Pro）

可以通过 `ARS_CROSS_MODEL_SAMPLE_INTERVAL` 调低采样频率来控制成本。

## 与 Codex Audit 的关系

ARS v3.6.7 的 codex audit prompt 模板（`shared/templates/codex_audit_multifile_template.md`）定义了跨模型审计的七个维度。`run_codex_audit.sh` 脚本可以将 ARS 的产出物发送到外部模型做独立审计。

v3.7.0 试图将 codex audit 集成为 hook（SubagentStop → 自动触发审计），但因以下原因被延期：
1. **Contract gap**：hook payload 没有携带 stage/deliverable 信息，审计脚本无法知道自己在审计什么
2. **Invoker boundary**：审计脚本禁止同 session 内 LLM 调用，而 hook 在产出交付物的 LLM session 内触发

真正的 audit-hook 集成等待 ARS 有 stage/deliverable propagation contract 后在后续版本实现。

## 适用场景

| 场景 | 推荐 |
|------|------|
| 课程作业或初步探索 | 不需要跨模型验证 |
| 投稿前自查 | 建议启用——$1 左右的增量成本换来第二意见 |
| 高影响力期刊投稿 | 强烈建议启用——审稿人会做比这更严格的审查 |
| 评估 ARS 本身的输出品质 | 必须启用——了解两个模型的共识和分歧范围 |

---

下一篇我们将探讨[苏格拉底导师与 SCR 协议](18-socratic-mentor-scr.md)——理解 ARS 如何通过 State-Challenge-Reflect 循环在对话中引导研究者反思。

**参考来源**：
- `source/academic-research-skills/shared/cross_model_verification.md`
- `source/academic-research-skills/shared/templates/codex_audit_multifile_template.md`
- `source/academic-research-skills/shared/collaboration_depth_rubric.md`
