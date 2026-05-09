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
    """查找 knowledge-base 中所有文章（排除 template.md、README 等非文章文件）。

    对于 collection 项目目录（NN- 开头的目录），只处理 blog/ 子目录下的文件，
    避免误包含源码、文档等其他类型的 .md 文件。
    """
    articles_dir = kb_dir / "articles"
    if not articles_dir.exists():
        return []

    exclude = {"template.md", "README.md", "TODO.md", "_index.md"}
    result = []
    for f in sorted(articles_dir.rglob("*.md")):
        if f.name in exclude:
            continue
        rel = f.relative_to(articles_dir)
        parent_dirs = rel.parts[:-1]
        # 检查是否在 collection 项目目录内
        is_in_collection = any(
            p.startswith("NN-") or (len(p) >= 3 and p[:2].isdigit() and p[2] == "-")
            for p in parent_dirs
        )
        if is_in_collection and "blog" not in parent_dirs:
            continue  # 集合目录下只处理 blog/ 内的文件
        result.append(f)
    return result


def extract_local_images(body: str, article_path: Path) -> list[tuple[str, str]]:
    """从文章正文中提取所有本地图片链接。

    返回: [(original_markdown_link, absolute_local_path), ...]
    只匹配相对路径的本地图片，不匹配完整 URL。
    """
    # 匹配 ![...](path) 形式的图片链接
    # 捕获括号内的路径部分
    import re
    # 匹配不以 http:// 或 https:// 开头的路径（即本地相对路径）
    image_pattern = r'!\[.*?\]\(([^\)][^\)]*)\)'
    matches = re.findall(image_pattern, body)

    result = []
    for rel_path in matches:
        rel_path = rel_path.strip()
        # 跳过已经是 / 开头的绝对路径链接
        if rel_path.startswith('/') or rel_path.startswith('http://') or rel_path.startswith('https://'):
            continue
        # 构造绝对路径
        abs_path = article_path.parent / rel_path
        if abs_path.exists():
            result.append((rel_path, str(abs_path)))
    return result


def generate_output_path(article_path: Path, kb_dir: Path, content_dir: Path) -> Path:
    """根据源文件路径生成 Hugo 输出路径。

    支持多层嵌套分类：
    - knowledge-base/articles/YYYY-MM-DD-title.md → content/posts/YYYY-MM-DD-title.md
    - knowledge-base/articles/category/YYYY-MM-DD-title.md → content/posts/category/YYYY-MM-DD-title.md
    - knowledge-base/articles/category/subcategory/YYYY-MM-DD-title.md → content/posts/category/subcategory/YYYY-MM-DD-title.md
    """
    articles_dir = kb_dir / "articles"
    rel_path = article_path.relative_to(articles_dir)
    return content_dir / "posts" / rel_path


def derive_categories(article_path: Path, kb_dir: Path) -> list[str]:
    """从文件路径推导分类列表。

    knowledge-base/articles/category/sub/article.md → ["category", "sub"]
    最后一个是文件名，不计入分类。
    """
    articles_dir = kb_dir / "articles"
    rel_path = article_path.relative_to(articles_dir)
    # 分类是父目录路径
    parts = list(rel_path.parts[:-1])
    # 把连字符替换成空格
    return [p.replace("-", " ").replace("_", " ") for p in parts]
