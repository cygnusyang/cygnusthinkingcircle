"""发布模块 —— 将生成的内容发布到 GitHub Pages"""

import shutil
import logging
import hashlib
from pathlib import Path

from .article import (
    Article,
    generate_hugo_frontmatter,
    extract_local_images,
    generate_output_path,
    derive_categories,
)

logger = logging.getLogger(__name__)


def copy_local_image(
    source_path: str,
    article_path: Path,
    static_dir: Path,
) -> str | None:
    """复制本地图片到 Hugo static 目录。

    图片存储为: static/images/YYYY-MM/[hash]-filename.ext
    返回新的 URL 路径。
    """
    source = Path(source_path)
    if not source.exists():
        logger.warning(f"    图片不存在: {source}")
        return None

    # 读取文件内容计算 hash 用于缓存
    content = source.read_bytes()
    file_hash = hashlib.md5(content).hexdigest()[:8]
    ext = source.suffix
    name = source.stem

    # 按年月组织
    from datetime import datetime
    year_month = datetime.now().strftime("%Y-%m")
    target_dir = static_dir / "images" / year_month
    target_dir.mkdir(parents=True, exist_ok=True)

    target_filename = f"{file_hash}-{name}{ext}"
    target_path = target_dir / target_filename

    try:
        shutil.copy2(source, target_path)
    except IOError as e:
        logger.error(f"    复制图片失败: {e}")
        return None

    # 返回 Hugo 静态资源 URL 路径
    return f"/images/{year_month}/{target_filename}"


def process_local_images(
    body: str,
    article_path: Path,
    static_dir: Path,
) -> str:
    """处理文章正文中的本地图片，复制到 static 目录并修正链接。"""
    images = extract_local_images(body, article_path)
    if not images:
        return body

    processed = body
    for original_link, abs_path in images:
        new_url = copy_local_image(abs_path, article_path, static_dir)
        if new_url:
            processed = processed.replace(f"({original_link})", f"({new_url})")
            logger.info(f"    图片: {original_link} → {new_url}")

    return processed


def publish_to_blog(
    article: Article,
    kb_dir: Path,
    content_dir: Path,
    static_dir: Path,
) -> Path | None:
    """将文章发布到 Hugo content/posts 目录

    支持多层嵌套分类结构，自动处理本地图片复制。

    Args:
        article: 源文章对象
        kb_dir: knowledge-base 根目录
        content_dir: Hugo content 目录 (如 cygnusyang.github.io/content)
        static_dir: Hugo static 目录 (如 cygnusyang.github.io/static)

    Returns:
        输出文件路径，失败返回 None
    """
    # 从文件路径推导分类信息
    categories = derive_categories(article.file_path, kb_dir)
    if categories and not article.category:
        # 如果文章没有手动设置 category，使用路径推导的最顶层分类
        article.category = categories[0]

    # 处理本地图片，复制到 static 目录并修正链接
    processed_body = process_local_images(article.body, article.file_path, static_dir)

    # 生成输出路径（支持多层嵌套）
    output_path = generate_output_path(article.file_path, kb_dir, content_dir)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 如果目录为空，生成 _index.md
    if output_path.parent != content_dir / "posts":
        # 检查 _index.md 是否已经存在
        index_path = output_path.parent / "_index.md"
        if not index_path.exists():
            # 从父目录名称生成标题
            dir_name = output_path.parent.name.replace("-", " ").replace("_", " ").title()
            from datetime import datetime
            date = datetime.now().strftime("%Y-%m-%d")
            index_content = f"""---
title: {dir_name}
date: {date}
draft: false
---
"""
            try:
                index_path.write_text(index_content, encoding="utf-8")
                logger.info(f"  生成分类索引: {index_path.relative_to(content_dir)}")
            except IOError as e:
                logger.warning(f"  生成分类索引失败: {e}")

    # 生成 frontmatter + 正文
    frontmatter = generate_hugo_frontmatter(article)
    full_content = f"{frontmatter}\n\n{processed_body}\n"

    try:
        output_path.write_text(full_content, encoding="utf-8")
        logger.info(f"  博客: {output_path.relative_to(content_dir)}")
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
