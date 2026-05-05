# 网站访问统计实施指南

## 概述

为 Hugo 网站配置双重统计系统，同时使用 **百度统计** 和 **Google Analytics 4**，以获得更全面的访问数据分析。

## 为什么同时使用两个统计服务？

| 特性 | 百度统计 | Google Analytics 4 |
|------|----------|---------------------|
| **国内访问** | ✅ 稳定快速 | ⚠️ 可能不稳定 |
| **全球访问** | ⚠️ 功能有限 | ✅ 完整支持 |
| **功能深度** | 基础统计 | 深度分析 |
| **实时数据** | ✅ 支持 | ✅ 支持 |
| **用户画像** | 国内用户为主 | 全球用户 |
| **免费额度** | 无限制 | 无限制 |

**优势互补：**
- 百度统计：确保国内用户数据不丢失
- Google Analytics：提供更深入的分析和全球视角

## 配置文件

已配置 [`cygnusyang.github.io/hugo.toml`](../cygnusyang.github.io/hugo.toml:162)：

```toml
# 统计分析（支持多个统计服务同时使用）
[params.analytics]
  enable = true
  
  # Google Analytics 4
  [params.analytics.google]
    id = ""  # 请替换为你的 Google Analytics Measurement ID (格式: G-XXXXXXXXXX)
  
  # 百度统计
  [params.analytics.baidu]
    id = ""  # 请替换为你的百度统计代码 ID (格式: xxxxxxxx)
```

## 实施步骤

### 步骤 1: 注册 Google Analytics 4

1. 访问 [Google Analytics](https://analytics.google.com/)
2. 使用 Google 账号登录
3. 创建新的 GA4 属性
4. 选择"网站"作为数据流类型
5. 输入网站 URL: `https://cygnusyang.github.io/`
6. 获取 Measurement ID（格式: `G-XXXXXXXXXX`）

### 步骤 2: 注册百度统计

1. 访问 [百度统计](https://tongji.baidu.com/)
2. 使用百度账号登录
3. 点击"新增网站"
4. 填写网站信息：
   - 网站域名: `cygnusyang.github.io`
   - 网站名称: `Cygnus Tech Blog`
   - 网站首页: `https://cygnusyang.github.io/`
   - 行业分类: 选择合适的分类
5. 获取统计代码 ID（格式: `xxxxxxxx`）

### 步骤 3: 填入配置文件

将获取的两个 ID 分别填入 [`cygnusyang.github.io/hugo.toml`](../cygnusyang.github.io/hugo.toml:162)：

```toml
[params.analytics]
  enable = true
  [params.analytics.google]
    id = "G-XXXXXXXXXX"  # 替换为实际的 GA4 Measurement ID
  [params.analytics.baidu]
    id = "xxxxxxxx"      # 替换为实际的百度统计 ID
```

### 步骤 4: 本地测试

```bash
cd cygnusyang.github.io
hugo server --buildDrafts
```

**测试 Google Analytics：**
1. 打开浏览器开发者工具 → Network 面板
2. 刷新页面
3. 查找 `collect?v=2&tid=G-XXXXXXXXXX` 请求
4. 确认请求成功（状态码 200）

**测试百度统计：**
1. 打开浏览器开发者工具 → Network 面板
2. 刷新页面
3. 查找 `hm.baidu.com/hm.gif` 请求
4. 确认请求成功（状态码 200）

### 步骤 5: 部署到 GitHub Pages

```bash
git add cygnusyang.github.io/hugo.toml
git commit -m "Add Google Analytics 4 and Baidu Analytics"
git push
```

### 步骤 6: 验证数据上报

**验证 Google Analytics：**
1. 访问 GA4 后台
2. 进入"实时"报告
3. 刷新网站页面
4. 确认看到实时访问数据

**验证百度统计：**
1. 访问百度统计后台
2. 进入"实时访客"
3. 刷新网站页面
4. 确认看到实时访问数据

## 查看统计数据

### Google Analytics 查看方法

访问 https://analytics.google.com/

**实时数据（立即生效）：**
- 点击 **"报告"** → **"实时"**
- 查看当前在线用户、实时页面浏览、地理位置、设备类型

**标准报告（24-48 小时后）：**
- **获取** - 流量来源分析
- **互动** - 用户行为分析
- **留存** - 用户留存分析
- **用户** - 人口统计、技术信息、地理位置

### 百度统计查看方法

访问 https://tongji.baidu.com/

**实时数据（立即生效）：**
- 点击 **"实时访客"**
- 查看当前在线用户、实时访问页面、地理位置

**标准报告（24 小时后）：**
- **趋势分析** - 访问量趋势
- **来源分析** - 流量来源
- **页面分析** - 各页面访问量
- **访客分析** - 访客属性、地域分布
- **设备分析** - 设备类型、浏览器、操作系统

## 数据对比分析

### 建议的对比维度

1. **访问量对比**
   - 百度统计 vs Google Analytics 的 PV/UV 差异
   - 分析差异原因（如国内用户占比）

2. **地域分布对比**
   - 百度统计：国内用户分布更准确
   - Google Analytics：全球用户分布更全面

3. **流量来源对比**
   - 百度搜索 vs Google 搜索
   - 社交媒体来源差异

4. **设备类型对比**
   - 两个平台的设备识别可能略有差异
   - 综合分析更准确

### 数据差异说明

两个统计平台的数据可能存在差异，这是正常的：

- **统计口径不同**：不同平台对"用户"、"会话"的定义略有差异
- **时区差异**：百度统计使用北京时间，Google Analytics 可配置时区
- **过滤规则不同**：不同平台的机器人过滤规则不同
- **网络环境**：国内用户访问 Google Analytics 可能失败

## 注意事项

### 隐私合规

- 考虑添加 Cookie 同意横幅
- 在隐私政策中说明使用统计服务
- Google Analytics 默认不记录 IP 地址
- 百度统计也支持 IP 匿名化

### 性能影响

- 两个统计脚本都异步加载，对页面性能影响最小
- FixIt 主题已优化加载顺序

### 调试技巧

**Google Analytics：**
- 使用 Google Tag Assistant 浏览器扩展
- 使用 GA4 DebugView 进行实时调试

**百度统计：**
- 使用百度统计调试工具
- 检查浏览器控制台是否有错误

## 后续优化

### Google Analytics 优化

- 设置自定义事件（如文章阅读完成）
- 配置转化目标
- 设置受众群体
- 集成 Google Search Console
- 创建自定义仪表板

### 百度统计优化

- 设置热力图
- 配置转化目标
- 设置访客分群
- 创建自定义报告

## 替代方案

如果需要更多统计服务，FixIt 主题还支持：

- **Cloudflare Analytics** - 无需额外脚本，隐私友好
- **Plausible** - 开源，隐私友好
- **Umami** - 自托管，完全控制数据
- **Fathom** - 简单易用，隐私友好

配置示例：

```toml
[params.analytics]
  enable = true
  [params.analytics.google]
    id = "G-XXXXXXXXXX"
  [params.analytics.baidu]
    id = "xxxxxxxx"
  [params.analytics.cloudflare]
    token = "your-cloudflare-token"
  [params.analytics.plausible]
    data_domain = "cygnusyang.github.io"
```

## 参考资料

- [Google Analytics 4 文档](https://support.google.com/analytics/answer/9304153)
- [百度统计帮助中心](https://tongji.baidu.com/web/help/)
- [FixIt 主题文档 - Analytics](https://fixit.lruihao.cn/advanced/analytics/)
- [Hugo 内置模板](https://gohugo.io/templates/internal/)
