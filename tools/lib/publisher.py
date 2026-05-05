"""发布模块 —— 将生成的内容发布到 GitHub Pages"""

import shutil
import logging
from pathlib import Path

from .article import Article, generate_hugo_frontmatter

logger = logging.getLogger(__name__)


def publish_to_blog(
    article: Article,
    content_dir: Path,
) -> Path | None:
    """将文章发布到 Hugo content/posts 目录

    Args:
        article: 源文章对象
        content_dir: Hugo content 目录 (如 cygnusyang.github.io/content)

    Returns:
        输出文件路径，失败返回 None
    """
    posts_dir = content_dir / "posts"
    posts_dir.mkdir(parents=True, exist_ok=True)

    # 生成 frontmatter + 正文
    frontmatter = generate_hugo_frontmatter(article)
    full_content = f"{frontmatter}\n\n{article.body}\n"

    output_path = posts_dir / article.filename
    try:
        output_path.write_text(full_content, encoding="utf-8")
        logger.info(f"  博客: {output_path}")
        return output_path
    except IOError as e:
        logger.error(f"  写入博客失败: {e}")
        return None


def save_platform_output(
    content: str,
    platform_key: str,
    article_slug: str,
    output_base: Path,
) -> Path | None:
    """保存平台适配内容到 output 目录

    Args:
        content: 适配后的内容
        platform_key: 平台标识 (如 xiaohongshu)
        article_slug: 文章 slug
        output_base: output 根目录

    Returns:
        输出文件路径
    """
    output_dir = output_base / platform_key
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"{article_slug}.md"
    try:
        output_path.write_text(content, encoding="utf-8")
        logger.info(f"  {platform_key}: {output_path}")
        return output_path
    except IOError as e:
        logger.error(f"  写入 {platform_key} 失败: {e}")
        return None
