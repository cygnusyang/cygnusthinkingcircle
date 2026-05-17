# 贡献指南

欢迎为教程贡献内容！

## 📝 如何贡献

### 1. 报告问题

如果发现教程中有错误或不清楚的地方：

1. 在主仓库创建 Issue
2. 描述问题所在
3. 提供截图或错误信息

### 2. 改进内容

如果你有改进建议：

```bash
# 1. 创建分支
git checkout -b docs/improve-tutorial-name

# 2. 编辑教程文件
vim tutorials/01-system-architecture.md

# 3. 提交更改
git add tutorials/01-system-architecture.md
git commit -m "docs: improve system architecture tutorial"

# 4. 推送并创建 PR
git push origin docs/improve-tutorial-name
```

### 3. 添加新教程

如果你想要添加新的教程：

1. 创建新的 Markdown 文件
2. 遵循现有格式
3. 在 `README.md` 中添加链接
4. 提交 PR

## 📐 教程格式

### 标题

使用层级标题：

```markdown
# 主标题（01-07 使用）
## 二级标题
### 三级标题
#### 四级标题
```

### 代码块

指定语言：

```markdown
```bash
# Bash 命令
```

```python
# Python 代码
```

```toml
# 配置文件
```
```

### 提示框

使用 emoji 区分不同类型：

```markdown
💡 提示：有用的建议

⚠️ 警告：需要注意的地方

❌ 错误：不要这样做

✅ 正确：推荐的做法

🎯 目标：本节要达到的目标

🚀 开始：步骤开始

🔧 工具：使用的工具

📝 说明：详细说明

📚 参考：参考资料

💡 下一步：后续学习
```

### 链接

使用相对链接：

```markdown
[系统架构](./01-system-architecture.md)
[GitHub Pages](./04-github-pages-setup.md)
```

### 图片

如果需要图片：

1. 将图片放在 `tutorials/images/` 目录
2. 使用相对路径引用：

```markdown
![图片说明](./images/example.png)
```

## ✅ 检查清单

提交前请确保：

- [ ] 文档格式正确
- [ ] 代码示例可以运行
- [ ] 链接有效
- [ ] 没有拼写错误
- [ ] 遵循现有风格
- [ ] 更新了 README.md（如果添加了新教程）

## 🎨 风格指南

### 语言

- 使用清晰、简洁的中文
- 技术术语使用英文
- 代码注释使用中文

### 标点符号

- 中文使用中文标点：，。、：；！？
- 英文和数字使用英文标点：, . : ; ! ?
- 避免混用

### 空格

- 中英文之间加空格
- 代码块前后加空行
- 列表项之间加空行

### 命名

- 文件名使用 kebab-case：`quick-start.md`
- 章节编号：`01-`, `02-`, 等

## 🤝 审查流程

1. 提交 PR
2. 等待维护者审查
3. 根据反馈修改
4. 合并到主分支

## 📞 联系方式

如有问题，请通过以下方式联系：

- 创建 GitHub Issue
- 发送邮件到项目维护者

感谢你的贡献！🎉