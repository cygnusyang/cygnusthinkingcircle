# 01. 系统架构

## 🏗️ 整体架构

```mermaid
graph TB
    subgraph Main["cygnusthinkingcircle/ 主仓库"]
        KB["knowledge-base/<br/>唯一真相源<br/>└─ articles/*.md"]
        Tools["tools/<br/>内容处理与发布引擎<br/>├─ make.py (统一入口)<br/>├─ lib/ (核心库)<br/>├─ prompts/ (平台策略)<br/>└─ output/ (生成内容)"]
        Blog["cygnusyang.github.io/<br/>Hugo 博客<br/>└─ content/posts/"]
        Env[".env (LLM 配置)"]
        Req["requirements.txt (Python 依赖)"]
        
        KB --> Tools
        Tools --> Blog
    end
    
    style Main fill:#f9f9f9,stroke:#333,stroke-width:2px
    style KB fill:#e1f5fe,stroke:#0288d1
    style Tools fill:#fff3e0,stroke:#f57c00
    style Blog fill:#e8f5e9,stroke:#388e3c
```

## 📦 三层结构

### 1. 内容层 (knowledge-base/)

**唯一真相源** - 所有内容从这里开始

```mermaid
graph LR
    Root["knowledge-base/"]
    Articles["articles/<br/>独立文章<br/>├─ template.md<br/>├─ 2026-05-05-article1.md<br/>└─ ..."]
    Collections["项目集合<br/>├─ 01-AI 工具与智能体/<br/>│  └─ 07-Harness/<br/>│     ├─ 01-xxx.md<br/>│     └─ ...<br/>└─ ..."]
    Catalog["catalog.yaml<br/>集合元数据"]
    
    Root --> Articles
    Root --> Collections
    Root --> Catalog
    
    style Root fill:#f9f9f9,stroke:#333,stroke-width:2px
    style Articles fill:#e1f5fe,stroke:#0288d1
    style Collections fill:#fff3e0,stroke:#f57c00
    style Catalog fill:#e8f5e9,stroke:#388e3c
```

**特点：**
- 基于 Markdown，轻量级
- Frontmatter 定义元数据
- 支持项目集合管理
- Git 版本控制

### 2. 处理层 (tools/)

**内容处理与发布引擎**

```mermaid
graph LR
    Root["tools/"]
    Make["make.py<br/>统一入口 CLI"]
    Lib["lib/<br/>├─ article.py (文章解析)<br/>├─ platforms.py (平台配置)<br/>├─ llm.py (LLM 适配)<br/>├─ publisher.py (博客发布)<br/>└─ collection.py (集合管理)"]
    Prompts["prompts/<br/>平台策略<br/>├─ blog.md<br/>├─ xiaohongshu.md<br/>├─ zhihu.md<br/>└─ ..."]
    Output["output/<br/>生成内容<br/>├─ xiaohongshu/<br/>├─ zhihu/<br/>└─ ..."]
    
    Root --> Make
    Root --> Lib
    Root --> Prompts
    Root --> Output
    
    style Root fill:#f9f9f9,stroke:#333,stroke-width:2px
    style Make fill:#e1f5fe,stroke:#0288d1
    style Lib fill:#fff3e0,stroke:#f57c00
    style Prompts fill:#e8f5e9,stroke:#388e3c
    style Output fill:#fce4ec,stroke:#c2185b
```

**核心流程：**

```mermaid
graph TB
    Source["knowledge-base/article.md"]
    
    Direct["[直发]"]
    Hugo["Hugo 博客<br/>content/posts/"]
    
    LLM["[LLM 改写]"]
    Platforms["多平台适配"]
    
    XHS["小红书<br/>prompt: 种草+实操"]
    Zhihu["知乎<br/>prompt: 深度专业+SEO"]
    Wechat["微信<br/>prompt: 私域+品牌"]
    Toutiao["头条<br/>prompt: 科普化表达"]
    Baijiahao["百家号<br/>prompt: SEO优化"]
    Douyin["抖音<br/>prompt: 分镜脚本"]
    
    Source --> Direct
    Direct --> Hugo
    
    Source --> LLM
    LLM --> Platforms
    Platforms --> XHS
    Platforms --> Zhihu
    Platforms --> Wechat
    Platforms --> Toutiao
    Platforms --> Baijiahao
    Platforms --> Douyin
    
    style Source fill:#e1f5fe,stroke:#0288d1
    style Hugo fill:#e8f5e9,stroke:#388e3c
    style Platforms fill:#fff3e0,stroke:#f57c00
    style XHS fill:#fce4ec,stroke:#c2185b
    style Zhihu fill:#f3e5f5,stroke:#7b1fa2
    style Wechat fill:#e0f2f1,stroke:#00796b
    style Toutiao fill:#fff8e1,stroke:#fbc02d
    style Baijiahao fill:#ffebee,stroke:#d32f2f
    style Douyin fill:#e8eaf6,stroke:#3f51b5
```

### 3. 展示层 (cygnusyang.github.io/)

**Hugo GitHub Pages** - 作为 Git 子模块

```mermaid
graph LR
    Root["cygnusyang.github.io/"]
    HugoConfig["hugo.toml<br/>Hugo 配置"]
    Content["content/<br/>└─ posts/<br/>博客文章（由 tools 生成）"]
    Themes["themes/<br/>└─ FixIt<br/>主题"]
    Layouts["layouts/<br/>自定义布局"]
    Static["static/<br/>静态资源"]
    Public["public/<br/>构建输出"]
    
    Root --> HugoConfig
    Root --> Content
    Root --> Themes
    Root --> Layouts
    Root --> Static
    Root --> Public
    
    style Root fill:#f9f9f9,stroke:#333,stroke-width:2px
    style HugoConfig fill:#e1f5fe,stroke:#0288d1
    style Content fill:#e8f5e9,stroke:#388e3c
    style Themes fill:#fff3e0,stroke:#f57c00
    style Layouts fill:#fce4ec,stroke:#c2185b
    style Static fill:#f3e5f5,stroke:#7b1fa2
    style Public fill:#e0f2f1,stroke:#00796b
```

**作为子模块的优势：**
- 独立的 Git 仓库
- 可以单独部署
- 清晰的职责分离

## 🔄 工作流程

```mermaid
graph TB
    Step1["1. 创作<br/>knowledge-base/articles/"]
    Step2["2. 构建<br/>python tools/make.py build --all"]
    Step2a["生成博客<br/>content/posts/"]
    Step2b["生成多平台<br/>tools/output/"]
    Step3["3. 审核<br/>本地预览"]
    Step4["4. 发布<br/>python tools/make.py publish"]
    Step4a["推送到 GitHub Pages"]
    
    Step1 --> Step2
    Step2 --> Step2a
    Step2 --> Step2b
    Step2a --> Step3
    Step2b --> Step3
    Step3 --> Step4
    Step4 --> Step4a
    
    style Step1 fill:#e1f5fe,stroke:#0288d1
    style Step2 fill:#fff3e0,stroke:#f57c00
    style Step2a fill:#e8f5e9,stroke:#388e3c
    style Step2b fill:#fce4ec,stroke:#c2185b
    style Step3 fill:#f3e5f5,stroke:#7b1fa2
    style Step4 fill:#e0f2f1,stroke:#00796b
    style Step4a fill:#fff8e1,stroke:#fbc02d
```

## 🎯 关键设计原则

### 1. 单一真相源 (Single Source of Truth)

所有内容只在 `knowledge-base/` 维护，其他平台内容由工具自动生成。

### 2. 工具驱动

通过 `make.py` 统一入口，简化操作流程。

### 3. 可扩展性

- 新增平台：只需添加 `prompts/xxx.md` 和 `platforms.py` 配置
- 新增集合：按命名约定自动发现

### 4. 版本控制

所有内容通过 Git 管理，支持：
- 历史追溯
- 分支协作
- 回滚恢复

## 🛠️ 技术栈

| 层级 | 技术 | 用途 |
|------|------|------|
| 内容 | Markdown | 文档格式 |
| 处理 | Python 3.x | 自动化脚本 |
| LLM | Anthropic Claude | 内容适配 |
| 博客 | Hugo + FixIt | 静态站点生成器 |
| 托管 | GitHub Pages | 免费网站托管 |
| 版本 | Git | 版本控制 |

## 📊 数据流

```mermaid
graph TB
    Source["知识库文章<br/>.md 文件"]
    
    Make["make.py<br/>├─ 解析 frontmatter<br/>├─ 转换为 Hugo 格式<br/>└─ 调用 LLM 适配（可选）"]
    
    Hugo["Hugo 博客<br/>content/"]
    XHS["小红书<br/>output/"]
    Zhihu["知乎<br/>output/"]
    
    Pages["GitHub Pages<br/>在线访问"]
    
    Source --> Make
    Make --> Hugo
    Make --> XHS
    Make --> Zhihu
    Hugo --> Pages
    
    style Source fill:#e1f5fe,stroke:#0288d1
    style Make fill:#fff3e0,stroke:#f57c00
    style Hugo fill:#e8f5e9,stroke:#388e3c
    style XHS fill:#fce4ec,stroke:#c2185b
    style Zhihu fill:#f3e5f5,stroke:#7b1fa2
    style Pages fill:#e0f2f1,stroke:#00796b
```

## 🚀 扩展可能性

1. **新增平台**
   - 在 `tools/prompts/` 添加策略文件
   - 在 `tools/lib/platforms.py` 注册平台

2. **新增功能**
   - 评论系统 (Waline/Giscus)
   - 访问统计 (百度统计/Google Analytics)
   - 搜索功能 (Lunr.js/Algolia)

3. **自动化**
   - GitHub Actions 自动部署
   - 定时任务同步更新