"""文章解析模块 —— 处理 knowledge-base 源文章"""

import re
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class Article:
    """源文章数据模型"""

    file_path: Path
    title: str
    date: str
    tags: list[str] = field(default_factory=list)
    category: str = ""
    summary: str = ""
    keywords: list[str] = field(default_factory=list)
    platforms: list[str] = field(default_factory=lambda: ["blog"])
    body: str = ""

    @property
    def slug(self) -> str:
        """从标题生成 URL 友好的 slug"""
        safe = re.sub(r"[^\w\u4e00-\u9fff\s-]", "", self.title).strip()
        return safe.replace(" ", "-").lower()[:80]

    @property
    def filename(self) -> str:
        """生成文件名: YYYY-MM-DD-slug.md"""
        return f"{self.date}-{self.slug}.md"

    @property
    def blog_output_path(self) -> Path:
        """博客输出的相对路径"""
        return Path(self.filename)


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """解析 YAML frontmatter，返回 (元数据字典, 正文)

    支持 --- 分隔的 YAML frontmatter 格式。
    如果内容不以 --- 开头，则返回空字典和全文。
    """
    if not content.startswith("---"):
        return {}, content

    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content

    frontmatter_text = parts[1].strip()
    body = parts[2].strip()

    metadata: dict = {}
    for line in frontmatter_text.split("\n"):
        line = line.strip()
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip().strip("\"'")

        # 处理列表值 [a, b, c]
        if value.startswith("[") and value.endswith("]"):
            value = [v.strip().strip("\"'") for v in value[1:-1].split(",") if v.strip()]
        metadata[key] = value

    return metadata, body


def load_article(file_path: Path) -> Article | None:
    """从文件加载文章"""
    try:
        content = file_path.read_text(encoding="utf-8")
    except (IOError, UnicodeDecodeError) as e:
        logger.error(f"无法读取文件 {file_path}: {e}")
        return None

    metadata, body = parse_frontmatter(content)

    title = metadata.get("title", file_path.stem)
    date = metadata.get("date", datetime.now().strftime("%Y-%m-%d"))
    tags = metadata.get("tags", [])
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",")]
    category = metadata.get("category", "")
    summary = metadata.get("summary", "")
    keywords = metadata.get("keywords", [])
    if isinstance(keywords, str):
        keywords = [k.strip() for k in keywords.split(",")]
    platforms = metadata.get("platforms", ["blog"])
    if isinstance(platforms, str):
        platforms = [p.strip() for p in platforms.split(",")]

    return Article(
        file_path=file_path,
        title=title,
        date=date,
        tags=tags,
        category=category,
        summary=summary,
        keywords=keywords,
        platforms=platforms,
        body=body,
    )


def _escape_yaml(value: str) -> str:
    """转义 YAML 字符串中的特殊字符"""
    return value.replace("\\", "\\\\").replace('"', '\\"')


def generate_hugo_frontmatter(article: Article) -> str:
    """生成 Hugo 兼容的 frontmatter"""
    lines = ["---"]
    lines.append(f'title: "{_escape_yaml(article.title)}"')
    lines.append(f"date: {article.date}")
    if article.tags:
        tags_str = ", ".join(f'"{_escape_yaml(t)}"' for t in article.tags)
        lines.append(f"tags: [{tags_str}]")
    if article.category:
        lines.append(f'category: "{_escape_yaml(article.category)}"')
    if article.summary:
        lines.append(f'description: "{_escape_yaml(article.summary)}"')
    lines.append("---")
    return "\n".join(lines)


def find_articles(kb_dir: Path) -> list[Path]:
    """查找 knowledge-base 中所有文章（排除 template.md）"""
    articles_dir = kb_dir / "articles"
    if not articles_dir.exists():
        return []
    return sorted(
        [f for f in articles_dir.glob("*.md") if f.name != "template.md"]
    )
