"""集合转换模块 —— 将 knowledge-base 项目目录批量转换为 Hugo 集合"""

import re
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

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
        # title 也带上章节编号，确保 Hugo 渲染时标题有"第NN章"前缀
        display_title = f"第{chapter_counter:02d}章 {title}"
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
        safe_title = _sanitize_filename_part(title)
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
        icon = _derive_card_icon(project_slug)
        index_content = _generate_index_md(titled_display_name, date, icon)
        (output_dir / "_index.md").write_text(index_content, encoding="utf-8")
        logger.info(f"  [{project_slug}] _index.md")

    # 更新首页卡片：替换"敬请期待"为文章数，更新标题带编号
    if count > 0:
        index_path = content_dir / "_index.md"
        if index_path.exists():
            _update_index_cards(index_path, project_slug, count, kb_dir)
            _sync_pinned_categories(index_path, project_slug)
            _resort_cards(index_path, kb_dir)

    return count


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
    pushed_slugs: set[str] = set()
    if pages_dir and pages_dir.exists():
        posts_dir = pages_dir / "content" / "posts"
        if posts_dir.exists():
            for entry in posts_dir.iterdir():
                if entry.is_dir() and (entry / "_index.md").exists():
                    # 用 directory name 匹配 slug 的最后一段
                    pushed_slugs.add(entry.name)

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
        # 显示路径：所有项目都带 NN 前缀，单层项目显示 NN-项目名；嵌套项目显示 PP-CC-项目名
        nn_str = "-".join(f"{n:02d}" for n, _ in nn_chain)
        display_path = f"{nn_str}-{nn_chain[-1][1]}"

        # 检查是否已推送到 GitHub Pages：嵌套项目检查父级目录，单层项目直接匹配
        pushed = False
        if pushed_slugs:
            slug_parts = slug.split("/")
            last_part = slug_parts[-1]
            # 单层项目直接匹配，嵌套项目匹配最后一段
            pushed = last_part in pushed_slugs

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
    - 带 NN 前缀的显示名: "01-openclaw", "04-01-电机控制"
    - 裸 slug: "openclaw", "工程那些事/电机控制"
    - 部分匹配: "电机控制"

    Returns:
        匹配到的项目 slug，未找到返回 None
    """
    projects = _discover_projects(kb_dir)

    # 1. 精确匹配 slug
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
        nn_str = "-".join(f"{n:02d}" for n, _ in nn_chain)
        display_path = f"{nn_str}-{nn_chain[-1][1]}"
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


# 项目 slug → _index.md 卡片 aria-label 映射
# 用于在构建集合后自动更新首页卡片状态，以及 add-card 时自动推导显示名
_CARD_ARIA_LABELS: dict[str, str] = {
    "openclaw": "OpenClaw",
    "gstack": "GStack",
    "gbrain": "GBrain",
    "claudecode": "Claude Code",
    "codex": "Codex",
    "mcp": "MCP",
    "harness": "Harness",
    "academic-research-skills": "Academic research skills",
}

# 已知项目的默认图标映射（emoji）
_CARD_ICONS: dict[str, str] = {
    "openclaw": "🤖",
    "gstack": "📚",
    "gbrain": "🧠",
    "claudecode": "⌨️",
    "codex": "📖",
    "mcp": "🔌",
    "harness": "⚙️",
    "academic-research-skills": "🔬",
}


def _update_index_cards(index_path: Path, project_slug: str, count: int, kb_dir: Path) -> bool:
    """更新 _index.md 中对应项目的卡片：替换"敬请期待"为文章数，修正链接，更新标题带编号。

    通过 aria-label 定位卡片，更新 badge 文字和 href。
    """
    if project_slug not in _CARD_ARIA_LABELS:
        return False

    label = _CARD_ARIA_LABELS[project_slug]
    nn = _get_project_nn(project_slug, kb_dir)
    html = index_path.read_text(encoding="utf-8")

    # 匹配卡片: <a href="..." class="category-card" aria-label="LABEL">
    #            <span class="category-card-badge">TEXT</span>
    #            <div ...></div>
    #            <h3 ...>TITLE</h3>
    card_re = re.compile(
        r'(<a\s+href=")[^"]*("\s+class="category-card"\s+aria-label="'
        + re.escape(label)
        + r'">)\s*(<span\s+class="category-card-badge">)([^<]*)(</span>)\s*(<div\s+class="category-card-icon">.*?</div>)\s*(<h3\s+class="category-card-title">)([^<]*)(</h3>)'
    )

    match = card_re.search(html)
    if not match:
        return False

    old_badge = match.group(4)
    new_href = f"/posts/{project_slug}/"
    new_badge = f"{count} 篇"

    # 更新标题：添加 NN- 前缀
    old_title = match.group(8)
    display_name = label
    titled_display_name = f"{nn:02d}-{display_name}"

    if old_badge == new_badge and old_title == titled_display_name:
        return False  # 无需更新

    # 使用回调函数避免 f-string 中 backreference 的转义问题
    def _replace(m: re.Match) -> str:
        return (
            m.group(1) + new_href + m.group(2) + "\n"
            + "          " + m.group(3) + new_badge + m.group(5) + "\n"
            + "      " + m.group(6) + "\n"
            + "      " + m.group(7) + titled_display_name + m.group(9) + "\n"
        )

    updated = card_re.sub(_replace, html)

    if updated != html:
        index_path.write_text(updated, encoding="utf-8")
        if old_badge != new_badge:
            logger.info(f"  [首页卡片] {label}: \"{old_badge}\" → \"{new_badge}\"")
        if old_title != titled_display_name:
            logger.info(f"  [首页卡片] {label}: 标题更新 → \"{titled_display_name}\"")
        return True

    return False


def _derive_display_name(slug: str) -> str:
    """从项目 slug 推导卡片显示名。

    优先查 _CARD_ARIA_LABELS 映射，回退时按连字符分词后首字母大写。
    """
    if slug in _CARD_ARIA_LABELS:
        return _CARD_ARIA_LABELS[slug]
    words = re.split(r"[-_]", slug)
    return " ".join(w.capitalize() for w in words)


def _derive_card_icon(slug: str) -> str:
    """获取项目的默认卡片图标。"""
    return _CARD_ICONS.get(slug, "📦")


def _get_project_nn(slug: str, kb_dir: Path) -> int:
    """获取项目在 knowledge-base 中的 NN- 编号。

    用于卡片排序。非项目卡片返回 99（排末尾）。
    """
    projects = _discover_projects(kb_dir)
    if slug not in projects:
        return 99
    dirname = projects[slug].name  # e.g. "02-gstack"
    m = re.match(r"^(\d{2})-", dirname)
    return int(m.group(1)) if m else 99


def _parse_cards_section(html: str) -> tuple[str, list[str], str]:
    """解析 _index.md 中 category-cards 区域。

    使用嵌套计数正确匹配 </div>，避免卡片内部的 <div> 干扰。

    Returns:
        (before, cards_list, after)
        before: 从文件开头到 category-cards 开标签末尾的内容
        cards_list: 每张卡片的完整 HTML 块
        after: 从 category-cards 闭标签开始到文件末尾的内容
    """
    end_tag = '</div>'

    # 用 regex 匹配开标签（可能含 id 等额外属性）
    start_m = re.search(r'<div\s[^>]*class="category-cards"[^>]*>', html)
    if not start_m:
        return "", [], ""
    start_idx = start_m.start()
    start_tag_full = start_m.group(0)

    inner_start = start_idx + len(start_tag_full)

    # 计数嵌套 div 以找到匹配的 </div>
    depth = 1
    pos = inner_start
    inner_end = -1
    while depth > 0:
        next_open = html.find("<div", pos)
        next_close = html.find(end_tag, pos)
        if next_close == -1:
            break
        if next_open != -1 and next_open < next_close:
            depth += 1
            pos = next_open + 4
        else:
            depth -= 1
            if depth == 0:
                inner_end = next_close
                break
            pos = next_close + len(end_tag)

    if inner_end == -1:
        logger.warning("category-cards 区域缺少匹配的 </div>，跳过处理")
        return "", [], ""

    before = html[:inner_start]
    inner = html[inner_start:inner_end]
    after = html[inner_end:]

    # 从 inner 中提取卡片: <a ... class="category-card" ...>...</a>
    card_re = re.compile(
        r"<a\s[^>]*class=\"category-card\"[^>]*>.*?</a>", re.DOTALL
    )
    cards = card_re.findall(inner)

    return before, cards, after


def _card_sort_key(card_html: str, kb_dir: Path) -> tuple[int, str]:
    """从卡片 HTML 中提取排序键：(NN编号, aria-label小写)。"""
    # 提取 aria-label
    label_m = re.search(r'aria-label="([^"]*)"', card_html)
    label = label_m.group(1) if label_m else ""

    # 反查 aria-label → slug
    reverse_map: dict[str, str] = {v: k for k, v in _CARD_ARIA_LABELS.items()}

    slug = None
    if label in reverse_map:
        slug = reverse_map[label]
    else:
        # 尝试直接匹配 knowledge-base 项目 slug
        slug_candidate = label.lower().replace(" ", "-")
        projects = _discover_projects(kb_dir)
        if slug_candidate in projects:
            slug = slug_candidate

    nn = _get_project_nn(slug, kb_dir) if slug else 99
    return (nn, label.lower())


def _resort_cards(index_path: Path, kb_dir: Path) -> None:
    """重新排序 _index.md 中所有 category 卡片。

    按 (NN项目编号, aria-label字母序) 升序排列。
    """
    html = index_path.read_text(encoding="utf-8")
    before, cards, after = _parse_cards_section(html)

    if not cards:
        return

    original = cards[:]
    cards.sort(key=lambda c: _card_sort_key(c, kb_dir))

    if cards == original:
        return

    # 重建整个文件
    inner_text = "\n\n".join(cards)
    new_html = before.rstrip("\n") + "\n" + inner_text + "\n" + after.lstrip("\n")
    try:
        index_path.write_text(new_html, encoding="utf-8")
    except (IOError, OSError) as e:
        logger.error(f"无法写入 {index_path}: {e}")
        return
    logger.info("  [首页卡片] 已重新排序")


def _card_exists(html: str, label: str) -> bool:
    """检查 _index.md 中是否已存在指定 aria-label 的卡片。"""
    return f'aria-label="{label}"' in html


def _sync_pinned_categories(index_path: Path, project_slug: str) -> None:
    """将项目 slug 添加到 _index.md 的 pinned_categories frontmatter 中。"""
    html = index_path.read_text(encoding="utf-8")

    # 匹配 pinned_categories: ["...", "..."]
    pinned_re = re.compile(r'(pinned_categories:\s*\[)([^\]]*)(\])')
    m = pinned_re.search(html)
    if not m:
        # 未找到 pinned_categories，在 title 行后插入
        html = re.sub(
            r"(title:.*\n)",
            rf'\1pinned_categories: ["{project_slug}"]\n',
            html,
            count=1,
        )
    else:
        existing = m.group(2)
        slugs = [s.strip().strip('"\'') for s in existing.split(",") if s.strip()]
        if project_slug in slugs:
            return  # 已存在
        slugs.append(project_slug)
        new_slugs = ", ".join(f'"{s}"' for s in slugs)
        html = pinned_re.sub(rf"\1{new_slugs}\3", html)

    try:
        index_path.write_text(html, encoding="utf-8")
    except (IOError, OSError) as e:
        logger.warning(f"无法更新 pinned_categories: {e}")


def add_project_card(
    project_slug: str,
    kb_dir: Path,
    content_dir: Path,
    icon: str | None = None,
    description: str | None = None,
) -> bool:
    """向 _index.md 添加一张"敬请期待"风格的新卡片。

    Args:
        project_slug: 项目标识 (如 "harness", "newproject")
        kb_dir: knowledge-base 根目录
        content_dir: Hugo content 目录
        icon: 卡片图标 emoji (默认自动推导)
        description: 卡片描述文字 (默认 "技术文档与开发指南")

    Returns:
        True 如果添加成功或已存在
    """
    index_path = content_dir / "_index.md"
    if not index_path.exists():
        logger.error(f"首页文件不存在: {index_path}")
        return False

    display_name = _derive_display_name(project_slug)
    card_icon = icon or _derive_card_icon(project_slug)
    card_desc = description or "技术文档与开发指南"

    html = index_path.read_text(encoding="utf-8")

    # 检查卡片是否已存在
    if _card_exists(html, display_name):
        logger.info(f"  [首页卡片] \"{display_name}\" 已存在，跳过添加")
        return True

    # 获取项目 NN- 编号
    nn = _get_project_nn(project_slug, kb_dir)

    # 标题添加 NN- 前缀
    titled_display_name = f"{nn:02d}-{display_name}"

    # 生成新卡片 HTML（与现有敬请期待卡片风格一致）
    new_card = (
        f'<a href="/posts/{project_slug}/" class="category-card"'
        f' aria-label="{display_name}">\n'
        f'    <span class="category-card-badge">敬请期待</span>\n'
        f'    <div class="category-card-icon">{card_icon}</div>\n'
        f'    <h3 class="category-card-title">{titled_display_name}</h3>\n'
        f'    <p class="category-card-desc">{card_desc}</p>\n'
        f'  </a>'
    )

    # 解析现有卡片区域
    before, cards, after = _parse_cards_section(html)
    if not cards and not before:
        logger.error("未找到 category-cards 区域")
        return False

    # 插入新卡片
    cards.append(new_card)

    # 按 NN-编号 + 字母序重排
    cards.sort(key=lambda c: _card_sort_key(c, kb_dir))

    inner_text = "\n\n".join(cards)
    new_html = before.rstrip("\n") + "\n" + inner_text + "\n" + after.lstrip("\n")
    try:
        index_path.write_text(new_html, encoding="utf-8")
    except (IOError, OSError) as e:
        logger.error(f"无法写入 {index_path}: {e}")
        return False

    # 同步 pinned_categories
    _sync_pinned_categories(index_path, project_slug)

    logger.info(
        f"  [首页卡片] 添加 \"{display_name}\""
        f" (icon={card_icon}, NN={nn:02d})"
    )
    return True
