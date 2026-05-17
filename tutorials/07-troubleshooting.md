# 07. 故障排查

## 🚨 常见问题

### 文章构建问题

#### 问题：`make.py` 找不到文章

**现象：**

```
❌ 文章不存在: knowledge-base/articles/2026-05-17-article.md
```

**原因：** 文件名拼写错误或文件不存在

**解决：**

```bash
# 查看所有文章
ls knowledge-base/articles/

# 列出所有可用文章
python tools/make.py status

# 使用正确的文件名
python tools/make.py build 正确的文件名.md
```

---

#### 问题：Frontmatter 格式错误

**现象：**

```
❌ 解析 frontmatter 失败
```

**原因：** YAML 格式错误

**解决：**

检查 frontmatter 格式：

```yaml
---
title: "文章标题"          # 标题需要引号
date: 2026-05-17          # 日期格式 YYYY-MM-DD
tags: ["tag1", "tag2"]    # 列表格式
category: "分类"
summary: "摘要"
keywords: ["关键词"]
platforms: ["blog"]       # 列表格式
---
```

使用 YAML 验证工具检查：

```bash
# 在线工具
# https://www.yamllint.com/
```

---

#### 问题：构建后博客未更新

**现象：**

```
✅ 完成：处理了 1 篇文章
```

但访问博客还是旧内容。

**原因：**
1. Hugo 缓存
2. 浏览器缓存
3. 文件未保存

**解决：**

```bash
# 1. 清理 Hugo 缓存
cd cygnusyang.github.io
rm -rf resources public .hugo_build.lock

# 2. 重新构建
cd ..
python tools/make.py build --all --force

# 3. 清理浏览器缓存
# Chrome: Cmd+Shift+R (Mac) / Ctrl+Shift+R (Windows)
```

---

### GitHub Pages 问题

#### 问题：404 Not Found

**现象：**

访问 `https://你的用户名.github.io/` 显示 404

**原因：**
1. 仓库名不正确
2. 分支不是 `main`
3. `public/` 目录为空

**解决：**

```bash
# 1. 检查仓库名
# 必须是 "用户名.github.io"

# 2. 检查分支
cd cygnusyang.github.io
git branch  # 应该是 * main

# 3. 检查内容
ls public/  # 应该有 HTML 文件

# 4. 重新构建
hugo
git add public
git commit -m "Update public"
git push
```

---

#### 问题：子模块未初始化

**现象：**

```
❌ fatal: not a git repository
```

**原因：** 子模块未初始化

**解决：**

```bash
# 初始化子模块
git submodule update --init --recursive

# 如果还有问题，重新添加
git submodule deinit -f cygnusyang.github.io
git rm -f cygnusyang.github.io
git submodule add git@github.com:你的用户名/你的用户名.github.io.git cygnusyang.github.io
```

---

#### 问题：部署后 5-10 分钟才生效

**现象：**

刚推送代码，但网站还是旧内容

**原因：** GitHub Pages 部署需要时间

**解决：**

- 正常等待 5-10 分钟
- 查看部署状态：仓库 → Actions
- 使用 GitHub Actions 可以看到详细日志

---

### LLM 适配问题

#### 问题：LLM 适配失败

**现象：**

```
⚠️ LLM_API_KEY 未设置
```

**原因：** 环境变量未配置

**解决：**

```bash
# 检查 .env 文件
cat .env

# 确保 API Key 已设置
echo "LLM_API_KEY=sk-ant-xxxx" >> .env

# 或设置环境变量
export LLM_API_KEY=sk-ant-xxxx
```

---

#### 问题：适配内容质量差

**现象：**

生成的小红书/知乎内容不符合预期

**原因：** Prompt 配置不当

**解决：**

1. 查看并修改 prompt 文件：

```bash
# 编辑小红书 prompt
cat tools/prompts/xiaohongshu.md
```

2. 添加具体要求：

```markdown
# 小红书 Prompt 模板

你是一个小红书内容专家，请将以下技术文章改写为小红书风格。

## 要求：
1. 标题要吸睛，使用数字、表情符号
2. 内容要有情绪共鸣
3. 使用emoji增强可读性
4. 添加话题标签 #...

## 原文：
{{title}}

{{body}}
```

---

### Hugo 主题问题

#### 问题：主题样式不显示

**现象：**

博客页面乱码或样式缺失

**原因：** 主题未正确加载

**解决：**

```bash
# 1. 检查主题子模块
cd cygnusyang.github.io
git submodule status

# 2. 如果不是 "FixIt"，更新子模块
git submodule update --remote --merge

# 3. 检查 hugo.toml 中的 theme 配置
cat hugo.toml | grep theme
# 应该是 theme = "FixIt"
```

---

#### 问题：主题更新后报错

**现象：**

```
Error: Error building site: failed to render pages
```

**原因：** 主题更新导致配置不兼容

**解决：**

```bash
# 1. 查看主题更新日志
cd themes/FixIt
git log --oneline -10

# 2. 回退到稳定版本
git checkout v0.3.0

# 3. 或在父仓库锁定版本
cd ../..
git submodule update --init --recursive
```

---

### Python 环境问题

#### 问题：依赖安装失败

**现象：**

```
ERROR: Could not find a version that satisfies the requirement xxx
```

**原因：**
1. Python 版本过低
2. 网络问题
3. pip 版本过旧

**解决：**

```bash
# 1. 检查 Python 版本（需要 3.8+）
python --version

# 2. 升级 pip
pip install --upgrade pip

# 3. 使用国内镜像（如果网络问题）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 4. 重新创建虚拟环境
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

#### 问题：`make.py` 找不到模块

**现象：**

```
ModuleNotFoundError: No module named 'anthropic'
```

**原因：** 虚拟环境未激活

**解决：**

```bash
# 激活虚拟环境
source .venv/bin/activate

# 确认激活成功（提示符前面有 (.venv)）
python tools/make.py config
```

---

### Claude Code 问题

#### 问题：Claude Code 无法连接

**现象：**

```
Error: Failed to connect to Claude API
```

**原因：**
1. API Key 无效
2. 网络问题
3. 未登录

**解决：**

```bash
# 1. 检查登录状态
claude --whoami

# 2. 重新登录
claude logout
claude login

# 3. 检查网络连接
ping api.anthropic.com
```

---

#### 问题：权限被拒绝

**现象：**

```
Permission denied: /path/to/file
```

**原因：** 文件权限不足

**解决：**

```bash
# 修改文件权限
chmod 644 /path/to/file

# 或使用 sudo（不推荐）
sudo claude
```

---

## 🔍 调试技巧

### 1. 启用详细日志

```bash
# 设置日志级别
export LOG_LEVEL=DEBUG

# 或在代码中修改
# tools/make.py
logging.basicConfig(level=logging.DEBUG)
```

### 2. 检查构建状态

```bash
# 查看构建缓存
cat tools/.build-state.json

# 清除缓存
rm tools/.build-state.json
```

### 3. 查看文件变更

```bash
# 查看未提交的更改
git status

# 查看具体差异
git diff knowledge-base/articles/
```

### 4. 测试单个功能

```bash
# 只测试文章解析
python -c "from tools.lib.article import load_article; print(load_article('knowledge-base/articles/xxx.md'))"

# 只测试 LLM 调用
python -c "from tools.lib.llm import adapt_for_platform; print(adapt_for_platform('title', 'body', [], [], '', 'xiaohongshu.md'))"
```

## 📞 获取帮助

### 日志收集

报告问题时，请提供：

1. **系统信息：**

```bash
python --version
hugo version
claude --version
```

2. **错误日志：**

```bash
# 运行命令并保存输出
python tools/make.py build --all 2>&1 | tee error.log
```

3. **配置文件：**

```bash
# 删除敏感信息后提供
cat .env | grep -v API_KEY
cat hugo.toml
```

### 常用资源

- [Hugo 官方文档](https://gohugo.io/documentation/)
- [FixIt 主题文档](https://fixit.lruihao.cn/)
- [Claude Code 文档](https://claude.ai/code)
- [Anthropic API 文档](https://docs.anthropic.com/)

## ✅ 问题解决清单

- [ ] 检查文件是否存在
- [ ] 检查文件格式是否正确
- [ ] 检查依赖是否安装
- [ ] 检查环境变量是否设置
- [ ] 检查网络连接
- [ ] 清理缓存重试
- [ ] 查看错误日志
- [ ] 搜索类似问题

## 💡 预防措施

1. **定期备份**

```bash
# 定期备份配置文件
cp .env .env.backup
cp hugo.toml hugo.toml.backup
```

2. **版本控制**

```bash
# 提交前检查状态
git status
git diff

# 提交配置变更
git add .env.example hugo.toml
git commit -m "chore: update config"
```

3. **测试环境**

```bash
# 在测试分支实验
git checkout -b test/new-feature

# 实验成功后再合并
git checkout main
git merge test/new-feature
```

---

🎉 你已经完成了所有教程的学习！

现在你已经掌握了：
- ✅ 系统架构
- ✅ 快速开始
- ✅ 知识库搭建
- ✅ GitHub Pages 配置
- ✅ Claude Code 使用
- ✅ 完整工作流
- ✅ 故障排查

开始创建你的个人知识库吧！