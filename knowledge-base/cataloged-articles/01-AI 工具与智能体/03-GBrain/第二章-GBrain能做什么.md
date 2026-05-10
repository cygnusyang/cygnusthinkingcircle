# 第二章：GBrain 能做什么

## 核心能力全景

GBrain 不是单一功能工具，而是一个完整的能力矩阵，覆盖知识管理的全生命周期。

```mermaid
flowchart LR
    subgraph Input[输入层]
        I1[多模态输入]
        I2[链接/文章]
        I3[推文/社交]
        I4[视频/音频]
        I5[PDF/书籍]
        I6[会议记录]
        I7[邮件/日历]
        I8[对话提及]
        
        I1 --> I2
        I1 --> I3
        I1 --> I4
        I1 --> I5
        I1 --> I6
        I1 --> I7
        I1 --> I8
    end
    
    subgraph Process[处理层]
        P1[25 个技能编排]
        P2[路由系统]
        P3[链式调用]
        P4[自动触发]
        P5[质量保证]
        
        P1 --> P2
        P1 --> P3
        P1 --> P4
        P1 --> P5
    end
    
    subgraph Output[输出层]
        O1[可检索的知识]
        O2[结构化页面]
        O3[交叉引用]
        O4[时间线记录]
        O5[实体关系]
        O6[版本控制]
        
        O1 --> O2
        O1 --> O3
        O1 --> O4
        O1 --> O5
        O1 --> O6
    end
    
    Input --> Process --> Output
    
    Process -.->|"始终能力"| Output
    
    style Input fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    style Process fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    style Output fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
```

在此过程中，知识库被动增长

## 信号捕获：总是开启

### signal-detector 技能

这是 GBrain 的"神经系统"——在每条消息上运行，捕获智能体可能错过的信息。

```mermaid
flowchart TD
    A[用户发送消息到智能体]
    
    subgraph Main["主对话流程<br/>同步 快速"]
        B[智能体思考并响应]
    end
    
    subgraph Signal["signal-detector 技能<br/>并行 异步"]
        C[spawn Haiku model]
        D[捕获原创想法]
        E[提取实体提及]
        F[存储到信号队列]
        
        C --> D --> E --> F
    end
    
    A --> Main
    A --> Signal
    
    F --> G["下次查询时<br/>这些信号会被自动处理"]
    
    style Main fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    style Signal fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
```

**设计要点：**
1. 永不阻塞主流程：用户等待响应时，信号检测器在后台运行
2. 使用便宜的 Haiku 模型：每个信号成本极低
3. 并行处理：不会因为信号捕获而变慢
4. 从不干扰：即使信号捕获失败，主对话照常进行

### brain-ops 技能

任何脑读/写/查找/引用操作都会触发 brain-ops 技能，执行"读-丰富-写循环"。

```mermaid
flowchart TD
    A["用户请求：<br/>告诉我关于 Alice 的情况"]
    
    B[智能体首先执行 brain-ops 技能]
    
    C["查询大脑<br/>gbrain search Alice"]
    
    D[返回 people/alice 页面]
    
    subgraph Truth["编译真理"]
        T1["Alice Wang, AI 研究员"]
        T2[公司: DeepMind CTO]
        T3["上次见面: 2024-11-15"]
        T4[共同项目: 3 个]
        T5[开放线程]
        T6["AI 安全项目进度<br/>上次更新：2025-06"]
        T7["教育合作提案<br/>待讨论"]
    end
    
    subgraph Timeline["时间线"]
        L1["2024-11-15: 首次会面"]
        L2["2025-01-20: 介绍 Bob 认识"]
        L3["2025-03-10: 讨论 AI 安全项目"]
        L4["2025-06-05: 合作发表 RAG 论文"]
    end
    
    E[根据编译真理形成回答]
    
    F["Alice Wang 是 DeepMind 的 CTO<br/>你们上次在 2024 年 11 月见面..."]
    
    A --> B --> C --> D --> Truth
    D --> Timeline
    Truth --> E --> F
    
    style Truth fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    style Timeline fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
```

**关键特性：**
1. 脑优先：从不对外部 API，先查大脑
2. 读-丰富-写：查询后如果有新信息，自动更新
3. 来源引用：每个数据点都有来源，可追溯
4. 诚实地回答：大脑没有信息时，明确说"不知道"

## 内容摄取：多模态统一

### idea-ingest 技能

处理链接、文章、推文等文本内容，自动分析并建立关联。

```mermaid
flowchart TD
    A["用户分享：<br/>https://arxiv.org/abs/2501.12345"]
    
    B[idea-ingest 技能触发]
    
    C[获取并分析内容]
    D["提取标题、摘要、作者、关键概念"]
    
    E[创建论文脑页]
    E1["slug: papers/2501-12345"]
    E2["title: RAG 的局限性"]
    E3["source: arxiv.org"]
    
    F[为每个作者触发 enrich 技能]
    F1["author: Alice Wang"]
    F2[查找或创建 people/alice 页面]
    F3[更新时间线：发表这篇论文]
    
    G[建立交叉引用]
    G1["论文 → 作者"]
    G2["论文 → 关键概念"]
    
    H[为关键概念触发 enrich 技能]
    H1[如果概念是新实体，创建概念页]
    
    I["结果：一次操作，知识库增加了论文页 + 可能的作者页 + 概念页"]
    
    A --> B --> C --> D --> E
    E --> E1
    E --> E2
    E --> E3
    E --> F --> F1 --> F2 --> F3
    E --> G --> G1
    G --> G2
    E --> H --> H1
    F3 --> I
    H1 --> I
    
    style E fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    style F fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    style G fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
```

### media-ingest 技能

处理视频、音频、PDF、书籍等非文本内容。

```mermaid
flowchart TD
    A["用户分享：<br/>会议录音.mp4 或 PDF 书籍"]
    
    B[media-ingest 技能触发]
    
    subgraph Video["视频/音频"]
        V1["音频转录<br/>Groq Whisper"]
        V2["大文件自动分段<br/>>/25MB"]
        V3[得到完整转录文本]
        V4["实体提取<br/>Haiku"]
        V5[提取人名、公司名、主题]
        V6[创建脑页]
        V7["slug: media/meeting-2024-11-15"]
        V8["content: 转录文本"]
        V9["metadata: 时长、参与者"]
        V10[反向链接传播]
        V11["页面中提到的所有实体 ← backlink ← 页面"]
        
        V1 --> V2 --> V3 --> V4 --> V5 --> V6
        V6 --> V7
        V6 --> V8
        V6 --> V9
        V6 --> V10 --> V11
    end
    
    subgraph PDF["PDF/书籍"]
        P1["内容提取<br/>支持 OCR"]
        P2[章节识别与结构化]
        P3[实体提取]
        P4[创建带章节结构的脑页]
        
        P1 --> P2 --> P3 --> P4
    end
    
    A --> B
    B --> Video
    B --> PDF
    
    style Video fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    style PDF fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
```

### meeting-ingestion 技能

会议记录处理是 GBrain 的核心用例之一，展示自动丰富能力。

```mermaid
flowchart TD
    A["会议纪要到达<br/>来源：Circleback/日历"]
    
    B[meeting-ingestion 技能触发]
    
    C[创建会议页面]
    C1["slug: meetings/2024-11-15-deepmind-kickoff"]
    C2["content: 会议纪要、决策、行动项"]
    C3["attendees: Alice, Bob, Carol"]
    
    D[为每个参会者会触发 enrich 技能]
    
    subgraph Alice["Alice"]
        A1[查找/创建 people/alice]
        A2[更新时间线：参加本次会议]
        A3[提取公司：DeepMind]
        A4[为公司触发 enrich]
        A5[创建/更新 companies/deepmind]
        A6[添加 Alice 到员工列表]
        A7[添加会议到公司时间线]
        A8[建立 Alice → 会议的关系链接]
        
        A1 --> A2 --> A3 --> A4 --> A5 --> A6 --> A7 --> A8
    end
    
    subgraph Others["Bob, Carol"]
        O1[同样流程]
    end
    
    E[建立会议页面与所有实体的交叉引用]
    E1["会议 → Alice, Bob, Carol"]
    E2["会议 → DeepMind"]
    
    F["结果：一条会议记录，自动更新 3 个人页 + 1 公司页"]
    
    A --> B --> C
    C --> C1
    C --> C2
    C --> C3
    C --> D --> Alice
    D --> Others
    Alice --> E
    Others --> E
    E --> E1
    E --> E2
    E --> F
    
    style Alice fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    style Others fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
```

**价值：**
- 一次录入，所有关联实体都被更新
- 无需手动"记得去更新 Alice 的页面"
- 知识库始终保持一致状态

## 知识检索：混合搜索

### query 技能

三层搜索带引用合成，确保结果可追溯且不产生幻觉。

```mermaid
flowchart TD
    A["用户查询：<br/>我们上次讨论了什么关于 RAG 的事？"]
    
    B[query 技能执行]
    
    C[意图分类]
    C1["检测意图：entity/temporal/event/general"]
    C2[查询 RAG → entity 查询模式]
    
    D[多查询扩展]
    D1[原始查询：RAG]
    D2["Haiku 扩展：<br/>RAG, 检索增强生成,<br/>Retrieval Augmented Generation"]
    
    E[向量搜索 + 关键词搜索]
    
    subgraph Vector["向量结果<br/>语义匹配"]
        V1["meetings/2024-11-15<br/>0.91"]
        V2["papers/2501-12345<br/>0.87"]
    end
    
    subgraph Keyword["关键词结果<br/>精确匹配"]
        K1["meetings/2024-11-15<br/>0.88"]
        K2["concepts/rag-definition<br/>0.75"]
    end
    
    F[RRF 融合]
    F1["score = sum/1/60 + rank"]
    F2[去除重复，保留最高分结果]
    
    subgraph Results[结果]
        R1["meetings/2024-11-15<br/>0.92"]
        R1a[DeepMind kickoff 会议]
        R1b["时间: 2024-11-15"]
        R1c["参: Alice, Bob, Carol"]
        R1d[摘要: 讨论 RAG 的局限性]
        
        R2["papers/2501-12345<br/>0.88"]
        R2a[RAG 的局限性]
        R2b["作者: Alice Wang"]
        R2c["来源: arxiv.org"]
    end
    
    G["综合回答<br/>带引用"]
    
    H["根据大脑记录，我们上次讨论 RAG 主要是在 DeepMind kickoff 会议中..."]
    H1["会议记录：meetings/2024-11-15，讨论 RAG 的局限性"]
    H2["相关论文：papers/2501-12345，RAG 的局限性，Alice Wang 著"]
    
    A --> B --> C --> C1 --> C2
    C --> D --> D1 --> D2
    D --> E --> Vector
    E --> Keyword
    Vector --> F
    Keyword --> F
    F --> F1 --> F2
    F --> Results
    Results --> R1 --> R1a --> R1b --> R1c --> R1d
    Results --> R2 --> R2a --> R2b --> R2c
    Results --> G --> H
    H --> H1
    H --> H2
    
    style Vector fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    style Keyword fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    style Results fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
```

## 实体丰富：分层自动

### enrich 技能

这是 GBrain 最核心的技能，实现分层丰富策略，确保重要实体获得深度信息。

```mermaid
flowchart TD
    A["实体被提及<br/>来源：任何信号"]
    
    B[enrich 技能触发]
    
    C["评估实体重要度<br/>提及次数 + 来源多样性"]
    
    subgraph Tier3["Tier 3<br/>一次提及 单一来源"]
        T3a[动作：创建存根页面]
        T3b["slug: people/alice"]
        T3c["title: Alice Wang"]
        T3d["tags: mentioned"]
        T3e[时间线：首次提及记录]
        
        T3a --> T3b --> T3c --> T3d --> T3e
    end
    
    subgraph Tier2["Tier 2<br/>3 次提及 不同来源"]
        T2a[动作：Web + 社交丰富]
        T2b["Web 搜索：Alice Wang"]
        T2c["社交搜索：@alice_xyz"]
        T2d[LinkedIn 查找]
        T2e[提取：头像、简介、公司、教育背景]
        T2f[更新页面，添加 Web 信息]
        
        T2a --> T2b
        T2a --> T2c
        T2a --> T2d
        T2b --> T2e
        T2c --> T2e
        T2d --> T2e
        T2e --> T2f
    end
    
    subgraph Tier1["Tier 1<br/>会议或 8+ 次提及"]
        T1a[动作: 完整流水线]
        T1b["公司深挖<br/>新闻、融资、产品"]
        T1c[社交历史分析]
        T1d[学术成果搜索]
        T1e[构建完整时间线]
        T1f[建立所有关系链接]
        
        T1a --> T1b
        T1a --> T1c
        T1a --> T1d
        T1a --> T1e
        T1a --> T1f
    end
    
    D["大脑自动学习谁重要<br/>无需显式告诉'去查一下这个人'"]
    
    A --> B --> C
    C --> Tier3
    C --> Tier2
    C --> Tier1
    Tier3 --> D
    Tier2 --> D
    Tier1 --> D
    
    style Tier3 fill:#f5f5f5,stroke:#666,stroke-width:2px
    style Tier2 fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    style Tier1 fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
```

**为什么要分层？**

1. 成本控制：不每个人都花 Tier 1 的成本
2. 演进机制：重要度提升后，下次自动升级
3. 避免垃圾：一次性提及的实体不会浪费 API 配额
4. 渐进深度：随时间推移，重要实体自然获得更完整信息

## 技能系统：可组合的工作流

### 技能链式调用

GBrain 的技能不是孤立的，而是可以相互调用，形成复杂工作流。

```mermaid
flowchart TD
    A[用户分享一条推文]
    
    subgraph Idea["idea-ingest 技能"]
        I1[创建推文脑页]
        I2["提取作者: Alice Wang"]
    end
    
    subgraph En["链式调用 enrich 技能<br/>作者"]
        E1[更新/创建 people/alice 页面]
        E2[添加推文到时间线]
        E3["提取公司: DeepMind"]
    end
    
    subgraph En2["链式调用 enrich 技能<br/>公司"]
        E4[更新/创建 companies/deepmind]
        E5[添加推文到公司时间线]
        E6[提取竞争对手列表]
    end
    
    subgraph En3["链式调用 enrich<br/>每个竞争对手"]
        E7[创建/更新竞争对手页面]
        E8[建立竞争关系链接]
    end
    
    subgraph Links["建立交叉引用"]
        L1["推文 → Alice"]
        L2["推文 → DeepMind"]
        L3["推文 → 竞争对手 A, B, C"]
    end
    
    R["结果：一条推文触发完整的关系网络构建"]
    
    A --> Idea
    Idea --> I1
    I1 --> I2
    I2 --> En
    En --> E1
    E1 --> E2
    E2 --> E3
    E3 --> En2
    En2 --> E4
    E4 --> E5
    E5 --> E6
    E6 --> En3
    En3 --> E7
    E7 --> E8
    E8 --> Links
    Links --> L1
    Links --> L2
    Links --> L3
    L3 --> R
    
    style Idea fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    style En fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    style En2 fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    style En3 fill:#f5f5f5,stroke:#666,stroke-width:2px
```

**链式调用的优势：**
1. 一次触发，完整处理：用户不需要分步操作
2. 自动深度：智能判断需要调用哪些技能
3. 幂等性：相同的操作幂等地产生相同结果
4. 可追溯：整个链式调用有清晰的审计日志

### 技能路由系统

RESOLVER.md 定义了技能与触发条件的映射，确保每个请求找到最合适的技能。

```mermaid
flowchart TD
    A[用户请求进入系统]
    
    B[检查 RESOLVER.md 中的路由规则]
    
    C{是否有明确的 URL？}
    
    C -->|是| D{检查内容类型}
    C -->|否| E{是否提及明确的人物/公司？}
    
    D -->|视频/音频| F[media-ingest]
    D -->|PDF/|G[idea-ingest]
    
    E -->|是| H{检查操作类型}
    E -->|否| I{通用请求}
    
    H -->|创建/|J[enrich]
    H -->|查询| K[query]
    
    I -->|有文件？| L[ingest 薄路由]
    I -->|有查询？| M[query]
    I -->|都没有| N[提示用户]
    
    O[路由原则]
    O1[特异性优先：meeting-ingestion 优于通用 ingest]
    O2[内容类型路由：按输入类型选择最合适的技能]
    O3[无法确定：询问用户意图]
    O4[支持链式：一个技能可以触发另一个技能]
    
    A --> B --> C
    C --> D
    C --> E
    D --> F
    D --> G
    E --> H
    E --> I
    H --> J
    H --> K
    I --> L
    I --> M
    I --> N
    
    style C fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    style D fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    style E fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    style H fill:#f5f5f5,stroke:#666,stroke-width:2px
    style I fill:#fce4ec,stroke:#c62828,stroke-width:2px
```
