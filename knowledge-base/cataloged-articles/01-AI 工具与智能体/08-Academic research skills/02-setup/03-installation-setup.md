# 30 秒安装与五种部署方式

ARS v3.7.0 引入 Claude Code Plugin 打包后，安装简化到了一行命令。但它的部署方式远不止一种——从全局可用到单项目隔离，从命令行到 VS Code，每种方式各有适用场景。本文梳理全部五种部署路径及其优劣。

## 前置条件

无论选择哪种安装方式，都需要：

1. **Claude Code CLI**（建议最新版本；plugin 打包需要较新版本）
   ```bash
   # macOS / Linux
   curl -fsSL https://claude.ai/install.sh | bash
   ```
2. **Anthropic API Key**：从 [console.anthropic.com](https://console.anthropic.com/) 获取，`export ANTHROPIC_API_KEY=sk-ant-xxxxx`

如果你只需要 Markdown 输出，以上两个条件就足够了。PDF 输出需要额外安装 tectonic 和字体，DOCX 直接生成需要 Pandoc——但这些都不是必需的。

---

## 方式一：Plugin 安装（v3.7.0+，推荐）

```text
/plugin marketplace add Imbad0202/academic-research-skills
/plugin install academic-research-skills
```

安装后验证：

```text
/ars-plan
```

然后描述你正在写的论文，ARS 会用苏格拉底对话帮你规划章节结构。

**这是最推荐的方式**，因为它：
- 一行命令完成，无需手动管理文件
- 自动注册 10 个 `/ars-*` slash command
- 自动暴露 3 个 plugin-shipped agent
- SessionStart 时注入可用命令列表
- 跨项目可用，无需为每个项目单独安装

### Plugin 安装后的额外能力

通过 plugin 安装后，ARS 额外提供：

- **10 个 slash commands**：`/ars-full`、`/ars-plan`、`/ars-outline`、`/ars-revision`、`/ars-revision-coach`、`/ars-abstract`、`/ars-lit-review`、`/ars-format-convert`、`/ars-citation-check`、`/ars-disclosure`
- **模型路由**：`/ars-full` 和 `/ars-revision-coach` 自动使用 Opus（深度推理需求），其余 8 个使用 Sonnet（效率优先）
- **3 个 plugin agent**：`synthesis_agent`、`research_architect_agent`、`report_compiler_agent`，使用 `model: inherit` 继承父 session 的模型

---

## 方式二：Symlink 到全局 skills 目录

这是 v3.7.0 之前的标准安装方式，Plugin 发布后仍然可用：

```bash
git clone https://github.com/Imbad0202/academic-research-skills.git
ln -s "$(pwd)/academic-research-skills/skills/academic-paper" ~/.claude/skills/academic-paper
ln -s "$(pwd)/academic-research-skills/skills/academic-paper-reviewer" ~/.claude/skills/academic-paper-reviewer
ln -s "$(pwd)/academic-research-skills/skills/academic-pipeline" ~/.claude/skills/academic-pipeline
ln -s "$(pwd)/academic-research-skills/skills/deep-research" ~/.claude/skills/deep-research
```

**优势**：
- 全局可用——任何目录下启动 Claude Code 都能使用
- 直接编辑 repo 中的文件即可定制 skill
- `git pull` 即可更新

**劣势**：
- 需要手动管理 symlink
- 没有 slash command 注册和 SessionStart announce

---

## 方式三：Symlink 到项目 skills 目录

将 skill 安装到单个项目的 `.claude/skills/` 下：

```bash
cd your-paper-project
mkdir -p .claude/skills
ln -s /path/to/academic-research-skills/skills/academic-paper .claude/skills/academic-paper
# ... 依此类推
```

**优势**：
- 项目级别隔离——不同项目可以使用不同版本的 ARS
- 团队成员可以通过 git 统一管理 `.claude/skills/` 配置

---

## 方式四：claude.ai Project 注入

在 claude.ai 上创建 Project 时，将 ARS skill 文件内容粘贴到 Project Knowledge 中。

**优势**：无需本地安装，适合 Web 端使用场景

**劣势**：Project Knowledge 有长度限制，无法容纳完整的 skill 文件；功能会因截断而受限

---

## 方式五：完整 Repo Clone（开发者模式）

直接 clone 整个 ARS 仓库，在 Claude Code 中打开使用：

```bash
git clone https://github.com/Imbad0202/academic-research-skills.git
cd academic-research-skills
claude
```

**适合**：想要阅读源码、修改 skill 行为、或贡献代码的开发者

---

## 可选组件安装

### DOCX 输出

```bash
brew install pandoc   # macOS
sudo apt-get install pandoc  # Linux
```

没有 Pandoc 时，formatter 回退为 Markdown + DOCX 转换说明。

### PDF 输出（APA 7.0）

```bash
brew install tectonic  # macOS
# 字体：Times New Roman（通常已安装）+ 思源宋體 TC VF + Courier New
```

需要安装**思源宋體 TC VF**（Source Han Serif TC），从 [Google Fonts](https://fonts.google.com/specimen/Noto+Serif+TC) 或 [Adobe GitHub](https://github.com/adobe-fonts/source-han-serif) 下载。

> 如果只需要 Markdown 输出或 DOCX 转换说明，完全不需要安装这些。

### 跨模型验证（可选）

设置环境变量启用 GPT 或 Gemini 作为第二模型进行独立审查：

```bash
export ARS_CROSS_MODEL=1
```

未设置时此功能零开销。详见[第十七篇：跨模型验证](../08-advanced/17-cross-model-verification.md)。

### Material Passport Adapter（v3.6.4+，可选）

如果你使用 Zotero、Obsidian 或文件夹管理文献，可以通过 adapter 将文献库导入 Material Passport，让 ARS 在搜索外部数据库之前先使用你的文献：

```bash
pip install pyyaml jsonschema
python scripts/adapters/zotero.py --input ~/my_library.json --output passport.yaml
```

三个 reference adapter 随 ARS 发布，但你通常需要根据自己使用的文献管理工具编写自定义 adapter。详见[第十六篇：Material Passport](../07-pipeline/16-material-passport.md)。

---

## 验证安装

无论选择哪种方式，验证安装是否成功：

1. 在 Claude Code 中运行 `/ars-plan`，描述你的论文——应该触发苏格拉底式对话
2. 或运行 `/ars-lit-review "你的主题"` 做快速单次测试

如果 skill 没有被触发，检查：
- Plugin 方式：`/plugin list` 确认 `academic-research-skills` 在列表中
- Symlink 方式：确认 symlink 指向正确的路径且目标目录存在
- 确认 `SKILL.md` 文件中的 trigger keywords 包含了你的语言

---

## 不同方式的适用场景

| 场景 | 推荐方式 |
|------|---------|
| 大多数用户 | Plugin 安装（方式一） |
| 需要自定义 skill 内容 | Symlink + 直接编辑（方式二） |
| 团队协作、版本锁定 | 项目 skills 目录（方式三） |
| 仅 Web 端使用 | claude.ai Project 注入（方式四） |
| 贡献代码或深度定制 | 完整 Clone（方式五） |

---

下一篇我们将讨论 ARS 的 [Token 预算与成本控制](04-performance-cost.md)，了解各模式的 token 消耗和完整 pipeline 约 $4–6 的成本构成。

**参考来源**：
- `source/academic-research-skills/docs/SETUP.md`
- `source/academic-research-skills/QUICKSTART.md`
