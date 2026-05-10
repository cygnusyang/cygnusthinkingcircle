"""集合转换模块 —— 将 knowledge-base 项目目录批量转换为 Hugo 集合"""

import re
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional
import yaml

from .article import parse_frontmatter
from .publisher import process_local_images

logger = logging.getLogger(__name__)


def _has_articles(project_dir: Path, max_depth: int = 2) -> bool:
    """检查目录下是否有可发布的 .md 文章（限制扫描深度，避免误包含子项目）。"""
    exclude = {"README.md", "TODO.md", "CLAUDE.md", "_index.md"}
    for f in project_dir.rglob("*.md"):
        if f.name in exclude:
            continue
        if len(f.relative_to(project_dir).parts) <= max_depth:
            return True
    return False


def _discover_projects(kb_dir: Path) -> dict[str, Path]:
    """扫描 knowledge-base/articles/ 下的项目目录。

    识别规则：
    1. 目录名以 NN- 开头
    2. 满足以下任一条件：a) 包含 blog/ 子目录  b) 包含可发布的 .md 文章
    3. 按深度从浅到深处理，已识别项目的子目录自动排除

    返回 {slug: path} 映射，slug 为去掉所有 NN- 前缀后的完整相对路径。
    """
    articles_dir = kb_dir / "articles"
    if not articles_dir.exists():
        return {}

    catalog_path = kb_dir / "catalog.yaml"
    if catalog_path.exists():
        data = yaml.safe_load(catalog_path.read_text(encoding="utf-8")) or {}
        projects: dict[str, Path] = {}
        for catalog in data.get("catalogs", []):
            for child in catalog.get("children", []):
                source = child.get("source")
                output = child.get("output")
                if not source or not output:
                    continue
                project_path = articles_dir / source
                if project_path.exists():
                    projects[output] = project_path
        if projects:
            return projects

    # 收集所有 NN- 目录，按深度从浅到深排序
    candidates = []
    for entry in articles_dir.rglob("*"):
        if entry.is_dir() and re.match(r"^\d{2}-", entry.name):
            rel = entry.relative_to(articles_dir)
            candidates.append((len(rel.parts), entry))
    candidates.sort(key=lambda x: x[0])  # shallow first

    projects: dict[str, Path] = {}
    project_paths: set[Path] = set()

    for _depth, entry in candidates:
        # 跳过已识别项目的子目录
        if any(str(entry).startswith(str(p) + "/") for p in project_paths):
            continue

        has_blog = (entry / "blog").is_dir()
        has_md = _has_articles(entry) if not has_blog else True

        if not has_blog and not has_md:
            continue

        project_paths.add(entry)

        # 生成 slug：完整相对路径，每个部分都去掉 NN- 前缀
        rel_path = entry.relative_to(articles_dir)
        parts = list(rel_path.parts)
        slug_parts = []
        for part in parts:
            m = re.match(r"^\d{2}-(.+)", part)
            if m:
                slug_parts.append(m.group(1))
            else:
                slug_parts.append(part)
        slug = "/".join(slug_parts)
        projects[slug] = entry

    return projects


_CHINESE_NUMS = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}


def _sort_key_for_blog_file(file_path: Path) -> tuple[int, str]:
    """为 blog 文件生成排序 key。

    优先提取中文章节号（第一章 → 1），无章节号的文件（如总结）排在最后（999）。
    """
    stem = file_path.stem
    m = re.match(r"^第([一二三四五六七八九十]+)章", stem)
    if m:
        chapter_num = _CHINESE_NUMS.get(m.group(1), 999)
        return (chapter_num, stem)
    return (999, stem)


def _find_markdown_files(source_dir: Path) -> list[Path]:
    """递归查找目录下所有 .md 文件（排除非文章文件）。

    返回按章节号排序的文件列表，无章节号的文件排在最后。
    """
    exclude = {"README.md", "TODO.md", "CLAUDE.md", "_index.md"}
    files = []
    for f in source_dir.rglob("*.md"):
        if f.name in exclude:
            continue
        files.append(f)
    files.sort(key=_sort_key_for_blog_file)
    return files


def _extract_chapter_number(filename: str) -> int:
    """从文件名提取章节编号。匹配 NN- 或 --NN- 开头。"""
    m = re.match(r"^[-]*(\d+)[-._]", filename)
    if m:
        return int(m.group(1))
    return 0


def _extract_title_from_body(body: str) -> Optional[tuple[str, str]]:
    """从正文提取第一个一级标题作为标题，返回 (title, body_without_title_line)。"""
    m = re.search(r"^(#\s+.+)$\n?", body, re.MULTILINE)
    if not m:
        return None
    title = m.group(1).lstrip('#').strip()
    # 去掉标题行，保留剩下的正文
    body_without_title = body[m.end():].lstrip('\n')
    return title, body_without_title


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


def _generate_index_md(title: str, date: str, icon: str, sort_by: str = "Weight") -> str:
    """生成 Hugo 集合的 _index.md。"""
    return f"""---
title: {title}
date: {date}
draft: false
icon: {icon}
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
    # 自动探测源目录：先试 source_subdir，不存在则回退到项目根目录
    source_dir = project_dir / source_subdir
    if not source_dir.exists():
        if source_subdir == "blog":
            source_dir = project_dir
        else:
            logger.error(f"源目录不存在: {source_dir}")
            return 0

    md_files = _find_markdown_files(source_dir)
    if not md_files:
        logger.warning(f"未找到 Markdown 文件: {source_dir}")
        return 0

    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    output_dir = content_dir / "posts" / project_slug

    # 构建前先清理该集合的旧文件，避免重复生成
    if output_dir.exists():
        old_count = 0
        for f in list(output_dir.glob("*.md")):
            if f.name == "_index.md":
                continue  # _index.md 最后单独重建
            f.unlink()
            old_count += 1
        if old_count > 0:
            logger.info(f"  清理旧文件: {old_count} 篇")
    output_dir.mkdir(parents=True, exist_ok=True)

    # static 目录在项目根目录的 static
    base_dir = kb_dir.parent
    static_dir = base_dir / "cygnusyang.github.io" / "static"

    count = 0
    chapter_counter = 0
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
            extracted = _extract_title_from_body(body)
            if extracted:
                title, body = extracted
            else:
                title = file_path.stem

        # 处理本地图片，复制到 static 目录并修正链接
        body = process_local_images(body, file_path, static_dir)

        file_date = metadata.get("date", date)

        tags = metadata.get("tags", [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",")]

        summary = metadata.get("summary", "") or metadata.get("excerpt", "")

        # 全局连续编号：避免不同子目录下文件都有 "01-" 前缀导致章节号重复
        chapter_counter += 1
        # 去掉标题中已有的中文章节号前缀（如"第一章："、"第二章 - "），避免与新的"第NN章"前缀重复
        clean_title = re.sub(r"^第[一二三四五六七八九十]+章[\s：:-]*", "", title)
        # title 也带上章节编号，确保 Hugo 渲染时标题有"第NN章"前缀
        display_title = f"第{chapter_counter:02d}章 {clean_title}"
        category = _derive_category(file_path, source_dir)

        # 生成 Hugo frontmatter
        hugo_fm = _generate_hugo_frontmatter(
            title=display_title,
            date=file_date,
            collection=project_slug,
            weight=chapter_counter,
            category=category,
            tags=tags,
            summary=summary,
        )

        # 生成文件名
        ch_prefix = f"第{chapter_counter:02d}章-"
        safe_title = _sanitize_filename_part(clean_title)
        filename = f"{file_date}-{ch_prefix}{safe_title}.md"

        # 写入
        output_path = output_dir / filename
        output_path.write_text(f"{hugo_fm}\n\n{body}\n", encoding="utf-8")

        logger.info(f"  [{project_slug}] {filename}")
        count += 1

    # 生成 _index.md
    if count > 0:
        nn = _get_project_nn(project_slug, kb_dir)
        display_name = _derive_display_name(project_slug)
        titled_display_name = f"{nn:02d}-{display_name} 文档"
        icon = _derive_card_icon(project_slug, kb_dir)
        index_content = _generate_index_md(titled_display_name, date, icon)
        (output_dir / "_index.md").write_text(index_content, encoding="utf-8")
        logger.info(f"  [{project_slug}] _index.md")

    return count


def _get_project_nn(slug: str, kb_dir: Path) -> int:
    """提取项目的 NN 前缀编号，用于 _index.md 标题排序。"""
    catalog_path = kb_dir / "catalog.yaml"
    if catalog_path.exists():
        data = yaml.safe_load(catalog_path.read_text(encoding="utf-8")) or {}
        for catalog in data.get("catalogs", []):
            for child in catalog.get("children", []):
                if child.get("output") == slug:
                    return int(child.get("weight", 99))

    articles_dir = kb_dir / "articles"
    projects = _discover_projects(kb_dir)
    if slug not in projects:
        return 99
    project_path = projects[slug]
    rel_path = project_path.relative_to(articles_dir)
    first_part = rel_path.parts[0]
    m = re.match(r"^(\d{2})-", first_part)
    return int(m.group(1)) if m else 99


def _derive_display_name(slug: str) -> str:
    """从 slug 推导人类可读的显示名称。"""
    last_segment = slug.split("/")[-1]
    last_segment = last_segment.replace("-", " ")
    return last_segment.title()


def _derive_card_icon(slug: str, kb_dir: Path) -> str:
    """从 catalog.yaml 读取图标，fallback 到默认映射。"""
    catalog_path = kb_dir / CATALOG_YAML
    if catalog_path.exists():
        data = yaml.safe_load(catalog_path.read_text(encoding="utf-8")) or {}
        for catalog in data.get("catalogs", []):
            for child in catalog.get("children", []):
                if child.get("output") == slug:
                    icon = child.get("icon")
                    if icon:
                        return icon
    # fallback
    fallback = {
        "openclaw": "🤖", "gstack": "📚", "gbrain": "🧠",
        "claudecode": "⌨️", "codex": "📖", "mcp": "🔌",
        "harness": "⚙️", "academic-research-skills": "📦",
    }
    last_segment = slug.split("/")[-1]
    return fallback.get(last_segment, "📦")


CATALOG_YAML = "catalog.yaml"
HUGO_DATA_CATALOG = "data/catalog.yaml"


def sync_catalog_to_hugo(kb_dir: Path, pages_dir: Path) -> bool:
    """将 knowledge-base/catalog.yaml 同步到 Hugo data/catalog.yaml。

    Returns:
        True if synced, False if source doesn't exist
    """
    source = kb_dir / CATALOG_YAML
    if not source.exists():
        return False
    target = pages_dir / HUGO_DATA_CATALOG
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    logger.info(f"  📋 已同步 catalog.yaml → {target}")
    return True


def normalize_slug(input_slug: str) -> str:
    """规范化 slug：去掉所有路径分段的 NN- 前缀。

    支持：
    - 裸slug: "电机控制" → "电机控制"
    - 完整路径带NN: "05-工程那些事/01-电机控制" → "工程那些事/电机控制"
    - 混合: "工程那些事/01-电机控制" → "工程那些事/电机控制"
    """
    parts = input_slug.split("/")
    normalized_parts = []
    for part in parts:
        m = re.match(r"^\d{2}-(.+)", part)
        if m:
            normalized_parts.append(m.group(1))
        else:
            normalized_parts.append(part)
    return "/".join(normalized_parts)


def list_projects(
    kb_dir: Path,
    pages_dir: Optional[Path] = None,
) -> dict[str, dict]:
    """列出所有可用项目及其统计信息。

    Args:
        kb_dir: knowledge-base 根目录
        pages_dir: Hugo Pages 子模块目录（可选，传入后检测是否已推送）

    Returns:
        {slug: {path, article_count, nn, display_path, pushed_to_pages}}
    """
    articles_dir = kb_dir / "articles"
    projects = _discover_projects(kb_dir)

    # 获取已推送到 Hugo Pages 的项目集合
    # 递归扫描 content/posts/ 下所有带 _index.md 的目录，构建相对路径集合
    pushed_slugs: set[str] = set()
    if pages_dir and pages_dir.exists():
        posts_dir = pages_dir / "content" / "posts"
        if posts_dir.exists():
            for index_file in posts_dir.rglob("*/_index.md"):
                rel = index_file.parent.relative_to(posts_dir)
                pushed_slugs.add(str(rel))

    result = {}
    for slug, path in projects.items():
        # 有 blog/ 的项目文章在 blog/ 下，其余的项目文章在项目根目录下
        source_dir = path / "blog" if (path / "blog").is_dir() else path
        md_files = _find_markdown_files(source_dir)
        md_count = len(md_files)
        # 提取路径各级的 NN 编号
        rel_path = path.relative_to(articles_dir)
        parts = list(rel_path.parts)
        nn_chain = []
        for part in parts:
            m = re.match(r"^(\d{2})-(.+)", part)
            if m:
                nn_chain.append((int(m.group(1)), m.group(2)))
            else:
                nn_chain.append((99, part))
        # nn 用于排序：嵌套项目取顶层 NN，单层项目取自身 NN
        nn = nn_chain[0][0]
        # 显示路径：
        # 单层项目: NN-项目名 (如 01-openclaw)
        # 嵌套项目: 完整路径，每级带 NN 前缀 (如 04-工程那些事/01-电机控制)
        if len(parts) == 1:
            display_path = f"{nn_chain[0][0]:02d}-{nn_chain[0][1]}"
        else:
            display_parts = [f"{n:02d}-{name}" for n, name in nn_chain]
            display_path = "/".join(display_parts)

        # 检查是否已推送到 GitHub Pages：直接匹配 slug 与已推送路径集合
        pushed = False
        if pushed_slugs:
            pushed = slug in pushed_slugs

        result[slug] = {
            "path": path,
            "article_count": md_count,
            "nn": nn,
            "display_path": display_path,
            "pushed_to_pages": pushed,
        }
    return result


def resolve_project_by_input(user_input: str, kb_dir: Path) -> Optional[str]:
    """从用户输入解析为项目 slug。

    支持多种输入格式：
    - 带 NN 前缀的显示名: "01-openclaw", "04-工程那些事/01-电机控制"
    - 裸 slug: "openclaw", "工程那些事/电机控制"
    - 部分匹配: "电机控制"

    Returns:
        匹配到的项目 slug，未找到返回 None
    """
    projects = _discover_projects(kb_dir)

    # 1. 精确匹配 slug（去掉所有 NN- 前缀）
    normalized = normalize_slug(user_input)
    if normalized in projects:
        return normalized

    # 2. 构建 display_path → slug 映射，尝试精确匹配
    for slug in projects:
        rel_path = projects[slug].relative_to(kb_dir / "articles")
        parts = list(rel_path.parts)
        nn_chain = []
        for part in parts:
            m = re.match(r"^(\d{2})-(.+)", part)
            if m:
                nn_chain.append((int(m.group(1)), m.group(2)))
            else:
                nn_chain.append((99, part))
        if len(parts) == 1:
            display_path = f"{nn_chain[0][0]:02d}-{nn_chain[0][1]}"
        else:
            display_parts = [f"{n:02d}-{name}" for n, name in nn_chain]
            display_path = "/".join(display_parts)
        if display_path == user_input:
            return slug

    # 3. 部分匹配：用户输入匹配 slug 最后一段或 display_path 最后一段
    user_lower = user_input.lower()
    candidates = []
    for slug in projects:
        last_segment = slug.split("/")[-1].lower()
        if user_lower in last_segment or last_segment in user_lower:
            candidates.append(slug)
    if len(candidates) == 1:
        return candidates[0]
    if len(candidates) > 1:
        logger.error(f"匹配到多个项目: {', '.join(candidates)}，请使用更精确的名称")
        return None

    return None
