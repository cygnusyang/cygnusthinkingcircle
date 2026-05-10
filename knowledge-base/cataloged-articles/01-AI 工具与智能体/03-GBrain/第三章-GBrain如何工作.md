# 第三章：GBrain 如何工作

## 整体架构

GBrain 采用四层架构设计，每层有明确的职责边界。

```mermaid
graph TB
    subgraph User[用户层]
        U1[对话、链接、文件、会议、邮件、推文]
        U2[人类可读输入，无需学习曲线]
    end
    
    subgraph Schedule[调度层]
        S1[定时任务 cron]
        S2[Webhook 事件]
        S3[信号队列]
        S4[确保大脑持续更新]
    end
    
    subgraph Skills[技能层 智能层]
        SK1[25 个技能]
        
        subgraph Always[Always-on]
            A1[signal-detector]
            A2[brain-ops]
        end
        
        subgraph Ingest[摄取]
            I1[idea]
            I2[media]
            I3[meeting]
        end
        
        subgraph Brain[脑操作]
            B1[enrich]
            B2[query]
            B3[maintain]
        end
        
        subgraph Ops[运维]
            O1[tasks]
            O2[cron]
            O3[reports]
        end
        
        subgraph Routing[技能路由]
            R1[RESOLVER.md]
            R2[链式调用机制]
            R3[质量保证规则]
        end
    end
    
    subgraph Engine[引擎层]
        subgraph Engines[引擎]
            E1[PGLite]
            E2[Postgres]
        end
        
        subgraph Interface[BrainEngine 接口 统一契约]
            IF1[getPage, putPage, delete]
            IF2[searchKeyword, searchVector]
            IF3[addLink, getBacklinks]
            IF4[addTimelineEntry]
        end
        
        subgraph Search[混合检索]
            S1[子向量搜索 HNSW]
            S2[子关键词搜索 tsvector]
            S3[子RRF 融合]
            S4[子4 层去重]
        end
    end
    
    subgraph Data[数据层]
        subgraph Git[Git 仓库 人类可读]
            G1[Markdown 页面 = 真实数据源]
            G2[人类可编辑]
            G3[Git 版本控制]
            G4[永远胜]
        end
        
        subgraph DB[数据库 结构化]
            D1[四原语：实体、事件、事实、关系]
            D2[身份解析]
            D3[冲突可见]
            D4[图查询支持]
        end
    end
    
    User --> Schedule --> Skills --> Engine --> Data
    
    style User fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    style Schedule fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    style Skills fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    style Engine fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style Data fill:#fce4ec,stroke:#c62828,stroke-width:2px
```

**层间交互：**
- 用户 → 技能层：人类发起操作
- 技能层 → 引擎层：读写知识
- 调度层 → 技能层：后台自动运行
- 数据层 Git ↔ 数据库：双向同步，Git 优先

## 数据流转周期

GBrain 的核心是数据流转，每个信号都触发一系列处理步骤。

```mermaid
flowchart TD
    subgraph Phase1[阶段 1：信号到达]
        P1[输入类型]
        
        subgraph Inputs[输入类型]
            I1[会议记录]
            I2[邮件到达]
            I3[推文分享]
            I4[链接分享]
            I5[日历事件]
            I6[对话提及]
            I7[语音通话]
        end
        
        subgraph Signal[signal-detector 技能并行运行 异步]
            S1[捕获原创想法]
            S2[提取实体提及]
            S3[存储到信号队列]
            
            subgraph Features[关键特性]
                F1[永不阻塞主流程]
                F2[使用便宜的 Haiku 模型]
                F3[失败不影响主对话]
            end
        end
    end
    
    subgraph Phase2[阶段 2：技能路由与执行]
        R1[RESOLVER.md 决策树]
        R2[根据输入类型路由到合适技能]
        
        subgraph Skill[技能执行 如 idea-ingest]
            SK1[提取和结构化内容]
            SK2[创建/更新脑页]
            SK3[提取实体 作者、公司、主题]
            
            subgraph Chain[链式调用 enrich 技能 每个实体]
                C1[查找或创建实体页]
                C2[根据重要度选择丰富层级]
                C3[Web/社交搜索或深度挖]
                C4[更新时间线和关系]
            end
        end
    end
    
    subgraph Phase3[阶段 3：索引更新]
        subgraph Git[Git 仓库变更]
            G1[git commit 或 push]
            
            subgraph Sync[gbrain sync 自动触发]
                S1[检测变更的文件]
                S2[增量更新数据库 upsert]
                S3[生成/刷新嵌入向量]
                S4[更新搜索索引]
            end
        end
    end
    
    subgraph Phase4[阶段 4：下次查询受益]
        Q1[用户查询：关于 X 的信息]
        
        subgraph Query[query 技能执行混合搜索]
            Q2[向量搜索 + 关键词搜索 + RRF 融合]
            Q3[返回包含时间线的完整上下文]
            
            subgraph Result[结果]
                R1[编译真理：当前理解]
                R2[时间线：完整证据链]
                R3[来源：每个数据点都可追溯]
            end
        end
    end
    
    Phase1 --> Phase2 --> Phase3 --> Phase4
    
    style Phase1 fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    style Phase2 fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    style Phase3 fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    style Phase4 fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
```

**核心特性：**
1. 幂等性：相同的输入产生相同的输出
2. 可追溯：每个信息点都有来源
3. 自动化：信号触发技能，技能触发丰富
4. 持久化：索引更新后，所有查询受益

## 混合检索原理

GBrain 的检索不是单一搜索，而是多通道融合的结果。

```mermaid
flowchart TD
    A[用户查询：如何提高 LLM 推理速度？]
    
    subgraph Step1[步骤 1：意图分类]
        S1[autoDetectDetail query → intent]
        
        subgraph Intents[意图类型]
            I1[entity 实体查询 → 回编译真理块，优先级高]
            I2[temporal 时间查询 → 回时间线，按时间排序]
            I3[event 事件查询 → 回事件相关的页面]
            I4[general 通用查询 → 正常混合搜索]
        end
    end
    
    subgraph Step2[步骤 2：多查询扩展]
        E1[expandQuery query, Haiku → queries]
        
        subgraph Queries[扩展后的查询集]
            Q1[1. 如何提高 LLM 推理速度？]
            Q2[2. LLM 推理加速]
            Q3[3. 大语言模型推理优化]
            Q4[4. 提升 AI 模型推理效率]
        end
        
        N1[每个查询都会嵌入，然后搜索]
    end
    
    subgraph Step3[步骤 3：向量搜索 每个查询]
        subgraph Vector[向量搜索参数]
            V1[模型：text-embedding-3-large]
            V2[索引：HNSW 分层可导航小世界]
            V3[相似度：余弦 Cosine]
            V4[返回：按相似度排序的前 N 个结果]
        end
    end
    
    subgraph Step4[步骤 4：关键词搜索]
        subgraph Keyword[关键词搜索参数]
            K1[技术：PostgreSQL tsvector]
            K2[索引：GIN 索引]
            K3[匹配：全文搜索，支持 trigram]
            K4[返回：按匹配度排序的前 N 个结果]
        end
    end
    
    subgraph Step5[步骤 5：RRF 融合]
        subgraph Formula[RRF 计算公式]
            F1[for each result in allResults]
            F2[vectorRank = positionInVectorList]
            F3[keywordRank = positionInKeywordList]
            F4[rrfScore = 1/60 + vectorRank + 1/60 + keywordRank]
            F5[finalScore = rrfScore]
        end
        
        subgraph Value[RRF 的价值]
            V1[向量和关键词独立打分]
            V2[融合时取两者优势]
            V3[K=60 是可调节的平滑因子]
        end
        
        R1[按 finalScore 排序，返回前 M 个结果]
    end
    
    subgraph Step6[步骤 6：余弦重评分]
        subgraph Rescore[重评分]
            R1[for each result in RRFResults]
            R2[if result.hasEmbedding]
            R3[cosineScore = cosine query, result]
            R4[finalScore = 0.7 * rrfScore + 0.3 * cosineScore]
            R5[重新按 finalScore 排序]
        end
    end
    
    subgraph Step7[步骤 7：4 层去重]
        subgraph Layer1[第 1 层：精确去重]
            L1[移除相同 chunk ID 的结果]
        end
        
        subgraph Layer2[第 2 层：内容去重]
            L2[移除同一 slug 的相似内容结果]
        end
        
        subgraph Layer3[第 3 层：类型平衡]
            L3[限制某类型结果的比例 防止主导]
        end
        
        subgraph Layer4[第 4 层：编译真理保证]
            L4[同一 slug 只返回编译真理 chunk]
        end
    end
    
    Final[最终结果：高质量、去重、可追溯的搜索结果]
    
    A --> Step1 --> Step2 --> Step3 --> Step4 --> Step5 --> Step6 --> Step7 --> Final
    
    style Step1 fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    style Step2 fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    style Step3 fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    style Step4 fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style Step5 fill:#fce4ec,stroke:#c62828,stroke-width:2px
    style Step6 fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    style Step7 fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
```

### RRF 为什么有效

```mermaid
flowchart TD
    A[场景：查询 AI 安全]
    
    subgraph Vector[向量搜索结果]
        V1[#1 AI 安全攻防指南 - 向量排名 1 - RRF 分数 0.517]
        V2[#2 大语言模型安全 - 向量排名 2 - RRF 分数 0.500]
        V3[#3 提示工程最佳实践 - 向量排名 5 - RRF 分数 0.476]
        V4[#4 安全 AI 开发框架 - 向量排名 7 - RRF 分数 0.455]
    end
    
    subgraph Keyword[关键词搜索结果]
        K1[#2 AI 安全攻防指南 - 关键词排名 1 - RRF 分数 0.517]
        K2[#5 安全 AI 开发框架 - 关键词排名 2 - RRF 分数 0.500]
        K3[#10 企业级 AI 安全方案 - 关键词排名 3 - RRF 分数 0.476]
        K4[#15 数据安全与 AI - 关键词排名 4 - RRF 分数 0.455]
    end
    
    subgraph RRF[RRF 融合后]
        R1[#1 AI 安全攻防指南 - 向量排名 1 - 关键词排名 1 - RRF 总分 1.034]
        R2[#2 大语言模型安全 - 向量排名 2 - 关键词排名 - - RRF 总分 0.500]
        R3[#3 安全 AI 开发框架 - 向量排名 7 - 关键词排名 2 - RRF 总分 0.476]
        R4[#4 企业级 AI 安全方案 - 向量排名 - - 关键词排名 3 - RRF 总分 0.476]
    end
    
    subgraph Observations[关键观察]
        O1[RRF 分数 = sum 1/60 + rank]
        O2[两种搜索方式都贡献到最终分]
        O3[向量排名好的项目获得高分，但也保留关键词匹配]
        O4[关键词匹配但在向量中排名低的项目也能获得提升]
        O5[K=60 是平滑因子，K 越小顶部项目提升越大]
    end
    
    A --> Vector
    A --> Keyword
    Vector --> RRF
    Keyword --> RRF
    RRF --> Observations
    
    style Vector fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    style Keyword fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    style RRF fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
```

## 信任边界与安全

GBrain 设计了明确的信任边界，区分可信和不可信的调用者。

```mermaid
flowchart TD
    subgraph Interface[BrainEngine 接口统一定义操作]
        I1[所有操作共享相同的实现路径]
        I2[CLI 和 MCP 服务器使用同一代码]
    end
    
    subgraph Key[关键区别：OperationContext.remote 标志]
        subgraph CLI[CLI 调用 本地]
            C1[remote = false]
            C2[validateUploadPath path, root, strict=false]
            C3[→ 允许任何可访问路径]
            C4[→ 只检查文件是否存在，非符号链接]
            C5[→ 用户拥有文件系统权限]
        end
        
        subgraph MCP[MCP/HTTP 调用 智能体]
            M1[remote = true]
            M2[validateUploadPath path, root, strict=true]
            M3[→ 限制在 root 目录内]
            M4[→ 拒绝所有符号链接]
            M5[→ 检测路径遍历攻击]
            M6[→ 检测 cwd 逃逸]
            M7[→ 智能体不可信，严格安全]
        end
    end
    
    subgraph Security[安全措施]
        S1[1. realpath 解析: 解析所有符号链接，获取真实路径]
        S1a[→ 防止符号链接逃逸]
        
        S2[2. relative 检测: 检查解析后的路径是否在 root 内]
        S2a[→ 防止 ../ 遍历攻击]
        S2b[→ strict 模式下拒绝越界路径]
        
        S3[3. final-component 符号链接拒绝]
        S3a[→ 即使在 cwd 内，文件名本身不能是符号链接]
        
        S4[4. upload 验证器：slug + filename 白名单]
        S4a[→ 限制可接受的模式，防止恶意文件名]
    end
    
    Interface --> Key
    Key --> Security
    
    style CLI fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    style MCP fill:#fce4ec,stroke:#c62828,stroke-width:2px
    style Security fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
```
