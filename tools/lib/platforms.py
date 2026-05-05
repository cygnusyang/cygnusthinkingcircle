"""平台配置：定义各平台的内容策略参数"""

from dataclasses import dataclass


@dataclass(frozen=True)
class PlatformConfig:
    """单个平台的生成配置"""

    key: str
    name: str
    description: str
    word_count_range: tuple[int, int]  # (min, max)
    content_style: str
    output_dir: str
    prompt_file: str

    # 平台定位 (来自策略研究)
    traffic_source: str = ""  # 流量来源
    viral_potential: str = ""  # 爆发能力
    conversion_potential: str = ""  # 转化能力


PLATFORMS: dict[str, PlatformConfig] = {
    "blog": PlatformConfig(
        key="blog",
        name="博客",
        description="GitHub Pages 技术长文 —— 深度原创，SEO长尾",
        word_count_range=(2000, 5000),
        content_style="深度技术长文，完整代码示例，理论+实战结合",
        output_dir="blog",
        prompt_file="blog.md",
        traffic_source="Google/Bing 搜索",
        viral_potential="⭐⭐",
        conversion_potential="⭐⭐⭐",
    ),
    "xiaohongshu": PlatformConfig(
        key="xiaohongshu",
        name="小红书",
        description="种草+高客单 —— AI编程教程，实操干货",
        word_count_range=(800, 1200),
        content_style="标题数字+对比+情绪；步骤拆解清晰；代码截图；结尾有CTA；带热门标签",
        output_dir="xiaohongshu",
        prompt_file="xiaohongshu.md",
        traffic_source="搜索+推荐",
        viral_potential="⭐⭐⭐⭐",
        conversion_potential="⭐⭐⭐⭐",
    ),
    "zhihu": PlatformConfig(
        key="zhihu",
        name="知乎",
        description="深度专业+SEO —— 热点嫁接技术视角",
        word_count_range=(2000, 5000),
        content_style="前150字埋核心关键词；深度分析+案例拆解；可运行代码块；结尾引导评论互动",
        output_dir="zhihu",
        prompt_file="zhihu.md",
        traffic_source="搜索+推荐",
        viral_potential="⭐⭐⭐",
        conversion_potential="⭐⭐⭐⭐",
    ),
    "wechat": PlatformConfig(
        key="wechat",
        name="微信公众号",
        description="私域沉淀+品牌 —— 搜一搜SEO，社交传播",
        word_count_range=(1500, 3000),
        content_style="标题痛点场景+数据背书；开头钩子；25%/50%/75%位置埋转发钩子；文末CTA引导关注；原创度>70%",
        output_dir="wechat",
        prompt_file="wechat.md",
        traffic_source="搜一搜+社交推荐",
        viral_potential="⭐⭐",
        conversion_potential="⭐⭐⭐⭐⭐",
    ),
    "toutiao": PlatformConfig(
        key="toutiao",
        name="今日头条",
        description="深度内容红利 —— 科普化技术表达",
        word_count_range=(1500, 3000),
        content_style="开头3秒抓注意力；科普化技术表达，降低理解门槛；深度长文有独立冷启动流量池；SCQA框架",
        output_dir="toutiao",
        prompt_file="toutiao.md",
        traffic_source="算法推荐+主动搜索读者",
        viral_potential="⭐⭐⭐⭐",
        conversion_potential="⭐⭐⭐",
    ),
    "baijiahao": PlatformConfig(
        key="baijiahao",
        name="百家号",
        description="百度SEO长尾 —— 实用干货+搜索优化",
        word_count_range=(1500, 3000),
        content_style="标题前13字含核心关键词；SCQA框架（情境-冲突-问题-答案）；段落≤4行；图片ALT含关键词；小标题密度≥1个/300字",
        output_dir="baijiahao",
        prompt_file="baijiahao.md",
        traffic_source="百度搜索",
        viral_potential="⭐⭐⭐",
        conversion_potential="⭐⭐",
    ),
    "douyin": PlatformConfig(
        key="douyin",
        name="抖音",
        description="爆款引流 —— 30-60秒短视频脚本",
        word_count_range=(200, 500),
        content_style="30-60秒分镜脚本；开场3秒钩子；痛点展示→模型拆解→解决方案→效果对比→CTA；带热门话题标签",
        output_dir="douyin",
        prompt_file="douyin.md",
        traffic_source="算法推荐",
        viral_potential="⭐⭐⭐⭐⭐",
        conversion_potential="⭐⭐⭐⭐⭐",
    ),
}


def get_platform(key: str) -> PlatformConfig | None:
    """获取平台配置"""
    return PLATFORMS.get(key)


def list_platforms() -> list[PlatformConfig]:
    """列出所有平台"""
    return list(PLATFORMS.values())


def get_non_blog_platforms() -> list[PlatformConfig]:
    """列出非博客平台（需要 LLM 适配的）"""
    return [p for p in PLATFORMS.values() if p.key != "blog"]
