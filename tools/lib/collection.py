"""集合转换模块 —— 将 knowledge-base 项目目录批量转换为 Hugo 集合"""

import re
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from .article import parse_frontmatter

logger = logging.getLogger(__name__)


def _discover_projects(kb_dir: Path) -> dict[str, Path]:
    """扫描 knowledge-base/articles/ 下的项目目录。

    匹配 NN-projectname/ 格式的目录，返回 {slug: path} 映射。
    slug 为去掉 NN- 前缀后的项目名。
    """
    articles_dir = kb_dir / "articles"
    if not articles_dir.exists():
        return {}

    projects: dict[str, Path] = {}
    for entry in sorted(articles_dir.iterdir()):
        if not entry.is_dir():
            continue
        m = re.match(r"^\d{2}-(.+)", entry.name)
        if m:
            projects[m.group(1)] = entry
    return projects


def _find_markdown_files(source_dir: Path) -> list[Path]:
    """递归查找目录下所有 .md 文件（排除非文章文件）。"""
    exclude = {"README.md", "TODO.md", "CLAUDE.md", "_index.md"}
    files = []
    for f in sorted(source_dir.rglob("*.md")):
        if f.name in exclude:
            continue
        files.append(f)
    return files


def _extract_chapter_number(filename: str) -> int:
    """从文件名提取章节编号。匹配 NN- 或 --NN- 开头。"""
    m = re.match(r"^[-]*(\d+)[-._]", filename)
    if m:
        return int(m.group(1))
    return 0


def _extract_title_from_body(body: str) -> Optional[str]:
    """从正文提取第一个一级标题作为标题。"""
    m = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
    if m:
        return m.group(1).strip()
    return None


def _derive_category(file_path: Path, source_dir: Path) -> str:
    """从文件相对于 source_dir 的路径推导分类。

    blog/01-intro/01-xxx.md → "01 intro"
    blog/chapters/01-xxx.md   → ""（扁平结构无分类）
    """
    try:
        rel = file_path.relative_to(source_dir)
    except ValueError:
        return ""
    parts = rel.parts
    if len(parts) >= 2:
        return parts[-2].replace("-", " ").replace("_", " ")
    return ""


def _generate_hugo_frontmatter(
    title: str,
    date: str,
    collection: str,
    weight: int,
    category: str = "",
    tags: list[str] | None = None,
    summary: str = "",
) -> str:
    """生成 Hugo 集合文章的 frontmatter。"""
    lines = ["---"]
    escaped = title.replace("\\", "\\\\").replace('"', '\\"')
    lines.append(f'title: "{escaped}"')
    lines.append(f"date: {date}")
    if category:
        escaped_cat = category.replace("\\", "\\\\").replace('"', '\\"')
        lines.append(f'category: "{escaped_cat}"')
    if tags:
        tags_str = ", ".join(f'"{t.replace(chr(34), chr(92)+chr(34))}"' for t in tags)
        lines.append(f"tags: [{tags_str}]")
    else:
        lines.append("tags: []")
    lines.append(f'collections: ["{collection}"]')
    lines.append(f"weight: {weight}")
    if summary:
        escaped_sum = summary.replace("\\", "\\\\").replace('"', '\\"')
        lines.append(f'description: "{escaped_sum}"')
    lines.append("---")
    return "\n".join(lines)


def _generate_index_md(title: str, date: str, sort_by: str = "Weight") -> str:
    """生成 Hugo 集合的 _index.md。"""
    return f"""---
title: {title}
date: {date}
draft: false
sort_by: {sort_by}
sort_order: asc
layout: docs
---
"""


def _sanitize_filename_part(text: str) -> str:
    """将标题转为文件名安全片段。"""
    safe = re.sub(r"[^\w\u4e00-\u9fff\s-]", "", text)
    return safe.strip().replace(" ", "-")[:60]


def build_collection(
    project_slug: str,
    kb_dir: Path,
    content_dir: Path,
    source_subdir: str = "blog",
    date: str | None = None,
) -> int:
    """构建单个项目的 Hugo 集合。

    Args:
        project_slug: 项目标识 (如 "gstack", "openclaw")
        kb_dir: knowledge-base 根目录
        content_dir: Hugo content 目录
        source_subdir: 项目目录下的源子目录名
        date: 发布日期 (YYYY-MM-DD)，默认今天

    Returns:
        生成的文章数量
    """
    projects = _discover_projects(kb_dir)
    if project_slug not in projects:
        logger.error(f"项目不存在: {project_slug}")
        available = ", ".join(projects.keys())
        if available:
            logger.info(f"可用项目: {available}")
        return 0

    project_dir = projects[project_slug]
    source_dir = project_dir / source_subdir

    if not source_dir.exists():
        logger.error(f"源目录不存在: {source_dir}")
        return 0

    md_files = _find_markdown_files(source_dir)
    if not md_files:
        logger.warning(f"未找到 Markdown 文件: {source_dir}")
        return 0

    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    output_dir = content_dir / "posts" / project_slug
    output_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    for file_path in md_files:
        try:
            content = file_path.read_text(encoding="utf-8")
        except (IOError, UnicodeDecodeError) as e:
            logger.warning(f"跳过无法读取的文件 {file_path}: {e}")
            continue

        # 解析或生成 frontmatter
        metadata, body = parse_frontmatter(content)

        title = metadata.get("title", "")
        if not title:
            title = _extract_title_from_body(body) or file_path.stem

        file_date = metadata.get("date", date)

        tags = metadata.get("tags", [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",")]

        summary = metadata.get("summary", "") or metadata.get("excerpt", "")

        chapter_num = _extract_chapter_number(file_path.name)
        category = _derive_category(file_path, source_dir)

        # 生成 Hugo frontmatter
        hugo_fm = _generate_hugo_frontmatter(
            title=title,
            date=file_date,
            collection=project_slug,
            weight=chapter_num or count + 1,
            category=category,
            tags=tags,
            summary=summary,
        )

        # 生成文件名
        ch_prefix = f"第{chapter_num:02d}章-" if chapter_num else ""
        safe_title = _sanitize_filename_part(title)
        filename = f"{file_date}-{ch_prefix}{safe_title}.md"

        # 写入
        output_path = output_dir / filename
        output_path.write_text(f"{hugo_fm}\n\n{body}\n", encoding="utf-8")

        logger.info(f"  [{project_slug}] {filename}")
        count += 1

    # 生成 _index.md
    if count > 0:
        display_name = project_slug.replace("-", " ").title()
        index_content = _generate_index_md(f"{display_name} 文档", date)
        (output_dir / "_index.md").write_text(index_content, encoding="utf-8")
        logger.info(f"  [{project_slug}] _index.md")

    return count


def list_projects(kb_dir: Path) -> dict[str, dict]:
    """列出所有可用项目及其统计信息。

    Returns:
        {slug: {path, article_count, has_blog}}
    """
    projects = _discover_projects(kb_dir)
    result = {}
    for slug, path in projects.items():
        blog_dir = path / "blog"
        md_count = len(_find_markdown_files(blog_dir)) if blog_dir.exists() else 0
        result[slug] = {
            "path": path,
            "article_count": md_count,
            "has_blog": blog_dir.exists(),
        }
    return result
