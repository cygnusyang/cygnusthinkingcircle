# 第一章：GBrain 是什么

## 从问题说起

### 传统知识管理为什么失败

知识管理软件已经存在 30 年，但绝大多数人仍然无法有效维护自己的知识库。为什么？

```mermaid
flowchart TD
    A[用户维护知识] --> B[需要持续的人力投入]
    A --> C[需要记住更新交叉引用]
    A --> D[容易产生信息孤岛]
    
    B --> E[知识库很快过时]
    C --> F[重要信息被遗忘]
    D --> G[维护成本高于使用价值]
    
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style E fill:#f66,stroke:#333,stroke-width:1px
    style F fill:#f66,stroke:#333,stroke-width:1px
    style G fill:#f66,stroke:#333,stroke-width:1px
```

```mermaid
flowchart TD
    A[AI 智能体处理知识] --> B[非常聪明，能处理复杂问题]
    A --> C[但没有长期记忆]
    A --> D[每次会话都是从零开始]
    
    B --> E[无法从过去经验中学习]
    C --> F[无法积累知识]
    D --> G[重复回答相同的问题]
    
    style A fill:#9f9,stroke:#333,stroke-width:2px
    style E fill:#f66,stroke:#333,stroke-width:1px
    style F fill:#f66,stroke:#333,stroke-width:1px
    style G fill:#f66,stroke:#333,stroke-width:1px
```

### GBrain 的核心洞察

**将知识管理的维护成本降至近乎零，让维护成为正常操作的副作用。**

```mermaid
flowchart LR
    A[人力维护] -->|高成本，不可持续| B[知识腐烂]
    C[自动化维护] -->|零边际成本，可持续| D[知识生长]
    
    style A fill:#f66,stroke:#333,stroke-width:2px
    style C fill:#6f6,stroke:#333,stroke-width:2px
    style B fill:#999,stroke:#333,stroke-width:1px
    style D fill:#6f6,stroke:#333,stroke-width:1px
```

## 核心定位

GBrain 是为 AI 智能体提供个人知识大脑能力的模块化系统。它不只是一个存储系统，而是一个让知识能够**自我生长**的智能基础设施。

### 三层定位

```mermaid
graph TB
    subgraph GBrain[GBrain 定位层次]
        direction TB
        
        subgraph L1[第一层：存储引擎]
            L1A[Postgres + pgvector]
            L1B[向量检索<br/>语义理解]
            L1C[关系存储<br/>实体关联]
            L1D[全文搜索<br/>精确匹配]
            
            L1A --> L1B
            L1A --> L1C
            L1A --> L1D
        end
        
        subgraph L2[第二层：检索智能]
            L2A[混合搜索<br/>向量+关键词+RRF 融合]
            L2B[意图分类]
            L2C[多查询扩展]
            L2D[去重机制]
            
            L2A --> L2B
            L2A --> L2C
            L2A --> L2D
        end
        
        subgraph L3[第三层：工作流编排]
            L3A[25 个可组合技能]
            L3B[技能路由系统]
            L3C[自动触发机制]
            L3D[链式调用]
            
            L3A --> L3B
            L3A --> L3C
            L3A --> L3D
        end
        
        L1 --> L2 --> L3
    end
    
    style L1 fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    style L2 fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    style L3 fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
```

## 实际应用案例

### 生产环境规模

GBrain 不是一个概念产品，它正在为 Y Combinator CEO 的实际 AI 智能体提供生产级支持。

```mermaid
mindmap
  root((生产环境数据规模<br/>单实例))
    知识库规模
      17,888 个页面
        人物: 4,383 人
        公司: 723 家
        交易: 1,200+ 笔
        概念: 8,500+ 条
    运行状态
      21 个定时任务在自主运行
        会议同步
        邮件监控
        社交媒体追踪
        健康检查
    构建时间
      原版: 12 天构建完成
      部署: 约 30 分钟完成配置
      维护: 零人力成本，自动运行
```

### 实际工作流示例

```mermaid
sequenceDiagram
    participant U as 用户
    participant A as AI 智能体
    participant G as GBrain
    participant S as 技能系统
    
    U->>A: "准备一下我和 Alice 的会议"
    
    Note over A,S: Brain-ops 技能触发
    A->>G: 搜索 people/alice
    
    Note over G: 执行混合搜索
    G-->>A: 返回 Alice 的完整信息
    
    Note over A: 获得编译真理 + 时间线
    
    par signal-detector 并行运行
        A->>S: 捕获实体: DeepMind, Bob, RAG
    end
    
    Note over S: enrich 技能自动触发
    S->>G: 为 Bob 创建/更新人物页
    S->>G: 为 DeepMind 创建/更新公司页
    S->>G: 建立 Alice → Bob 关系
    S->>G: 建立 Alice → RAG 主题链接
    
    Note over U,A: 知识库被动增长
```

## 技术基础

### 引擎对比

GBrain 支持两种引擎，满足不同场景的需求。

| 特性 | PGLite（默认） | Postgres（可选） |
|------|----------------|------------------|
| **技术** | 嵌入式 PostgreSQL 17.5 WASM | PostgreSQL + pgvector 扩展 |
| **存储** | ~/.gbrain/brain.pglite | Supabase Pro 或自托管 |
| **配置** | 零配置，开箱即用 | DATABASE_URL 环境变量 |
| **就绪时间** | 2 秒 | 需要数据库连接时间 |
| **适用规模** | 单设备，1000+ 文件前 | 多设备同步，无限规模 |
| **成本** | 免费 | Supabase Pro $25/月 |

**数据迁移：**
- PGLite → Postgres：`gbrain migrate --to supabase`
- Postgres → PGLite：`gbrain migrate --to pglite`

### 混合检索技术栈

```mermaid
flowchart TD
    subgraph Vector[向量检索]
        V1[模型: OpenAI text-embedding-3-large]
        V2[索引: HNSW 分层可导航小世界]
        V3[相似度: 余弦相似度]
        V4[优势: 语义理解，能找到概念相似的内容]
    end
    
    subgraph Keyword[关键词检索]
        K1[技术: PostgreSQL tsvector]
        K2[索引: GIN 索引]
        K3[匹配: 全文搜索，支持 trigram]
        K4[优势: 精确匹配，能找到完全相同的短语]
    end
    
    subgraph RRF[RRF 融合]
        R1[Reciprocal Rank Fusion]
        R2[score = sum/1/60 + rank]
        R3[向量和关键词独立排名，然后融合]
        R4[兼顾语义理解和精确匹配]
    end
    
    Vector --> RRF
    Keyword --> RRF
    
    style Vector fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    style Keyword fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    style RRF fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
```

**为什么需要混合检索？**

纯向量搜索的问题：
- 查询 "Steve Jobs" → 可能找到 "科技企业家列表"但错过精确姓名
- 查询 "2024 年" → 可能找到 "财务报告"但错过具体数字

纯关键词搜索的问题：
- 查询 "创业公司应该做什么" → 找不到 "Do Things That Don't Scale"
- 查询 "AI 安全" → 找不到 "LLM 对抗攻击"

## 核心价值主张

| 传统问题 | GBrain 的解决方案 |
|----------|------------------|
| **知识维护需要持续人力投入**<br/>容易忘，需要手动提醒更新 | **AI 智能体自动维护，无需人力干预**<br/>每个信号都触发丰富流水线 |
| **信息分散在不同地方**<br/>难以建立关联，知识库成为信息孤岛 | **自动建立交叉引用和实体关系**<br/>关系图支持图查询，"我认识谁也认识 X？" |
| **知识检索效率低下**<br/>关键词搜索错过概念匹配<br/>向量搜索错过精确匹配 | **混合检索兼顾语义理解和精确匹配**<br/>向量搜索解决语义鸿沟<br/>RRF 融合取两者优势 |
| **AI 无法从过去经验中学习**<br/>每次会话都是从零开始<br/>重复回答相同的问题 | **持久化记忆让知识随时间积累**<br/>编译真理预计算，直接获取综合结果<br/>时间线记录完整证据链 |
| **知识库很快过时**<br/>维护成本高于使用价值 | **知识库在睡眠中自我增长**<br/>维护成本为零，边际效益递增 |

### 关键差异化特性

1. **编译真理预计算**
   - 传统 RAG：每次查询都从头合成知识
   - GBrain：合成已预计算，直接返回
   - 优势：响应更快，质量更一致

2. **自动丰富而非手动维护**
   - 传统系统：需要记得去更新相关页面
   - GBrain：触及实体时自动触发
   - 优势：永远不会遗漏更新

3. **MECE 目录结构**
   - 传统系统：同一知识可能存在多个地方
   - GBrain：每个知识片段有一个主要归属
   - 优势：无歧义，无重复

4. **技能系统而非硬编码逻辑**
   - 传统系统：固定的工作流，难以扩展
   - GBrain：25 个可组合技能，易于定制
   - 优势：灵活，社区可贡献
