"""内容校验模块 —— 检查 frontmatter、链接、图片等完整性"""

import re
from pathlib import Path
from typing import NamedTuple

from .article import parse_frontmatter, find_articles


class Issue(NamedTuple):
    """校验问题。"""
    severity: str  # "error" | "warning"
    file: str
    message: str


def validate_article(file_path: Path) -> list[Issue]:
    """校验单篇文章。"""
    issues = []
    try:
        content = file_path.read_text(encoding="utf-8")
    except (IOError, UnicodeDecodeError) as e:
        return [Issue("error", str(file_path), f"无法读取文件: {e}")]

    metadata, body = parse_frontmatter(content)

    # 1. frontmatter 必填字段
    if not metadata.get("title"):
        issues.append(Issue("error", str(file_path), "缺少 title 字段"))
    if not metadata.get("date"):
        issues.append(Issue("error", str(file_path), "缺少 date 字段"))

    # 2. 空正文
    if not body or not body.strip():
        issues.append(Issue("warning", str(file_path), "正文为空"))

    # 3. 文件大小异常 (> 50KB)
    size_kb = file_path.stat().st_size / 1024
    if size_kb > 50:
        issues.append(Issue("warning", str(file_path), f"文件较大 ({size_kb:.1f}KB)"))

    # 4. 图片引用失效
    _check_image_references(file_path, body, issues)

    # 5. 损坏的内部链接（Markdown 链接指向不存在的 .md 文件）
    _check_internal_links(file_path, body, issues)

    return issues


def validate_collection_posts(posts_dir: Path) -> list[Issue]:
    """校验整个 posts 目录下的集合文章。"""
    issues = []

    if not posts_dir.exists():
        return [Issue("error", str(posts_dir), "posts 目录不存在")]

    # 按集合分组检查
    collection_files: dict[str, list[tuple[Path, dict]]] = {}
    for md_file in sorted(posts_dir.rglob("*.md")):
        if md_file.name == "_index.md":
            continue
        try:
            content = md_file.read_text(encoding="utf-8")
            metadata, _ = parse_frontmatter(content)
        except (IOError, UnicodeDecodeError):
            continue

        # 确定所属集合
        try:
            rel = md_file.relative_to(posts_dir)
            collection = rel.parts[0] if len(rel.parts) > 1 else "root"
        except ValueError:
            collection = "root"

        collection_files.setdefault(collection, []).append((md_file, metadata))

    # 检查每个集合
    for collection_name, files in collection_files.items():
        _check_weight_continuity(collection_name, files, issues)
        _check_duplicate_titles(collection_name, files, issues)

    return issues


def _check_image_references(file_path: Path, body: str, issues: list[Issue]) -> None:
    """检查 Markdown 图片引用是否有效。"""
    # 匹配 ![alt](path) 和 [alt]: path 格式的引用
    image_refs = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', body)

    for alt, img_path in image_refs:
        # 跳过外部 URL
        if img_path.startswith(("http://", "https://", "//")):
            continue

        # 解析相对路径
        if img_path.startswith("/"):
            # 绝对路径：相对于 static 目录
            full_path = file_path.parent.parent.parent / "static" / img_path.lstrip("/")
        else:
            full_path = file_path.parent / img_path

        if not full_path.exists():
            issues.append(Issue("error", str(file_path), f"图片不存在: {img_path}"))


def _check_internal_links(file_path: Path, body: str, issues: list[Issue]) -> None:
    """检查内部 Markdown 链接是否有效。"""
    # 匹配 [text](path) 但不匹配图片 ![alt](path)
    links = re.findall(r'(?<!!)\[([^\]]*)\]\(([^)#]+)(?:#[^)]*)?\)', body)

    for text, link_path in links:
        # 跳过外部 URL 和锚点
        if link_path.startswith(("http://", "https://", "//", "#")):
            continue

        full_path = file_path.parent / link_path
        if not full_path.exists():
            issues.append(Issue("error", str(file_path), f"内部链接不存在: {link_path}"))


def _check_weight_continuity(collection_name: str, files: list[tuple[Path, dict]], issues: list[Issue]) -> None:
    """检查集合内 weight 连续性。"""
    weights = []
    for f, meta in files:
        w = meta.get("weight")
        if w is not None:
            try:
                weights.append((int(w), f))
            except (ValueError, TypeError):
                pass

    if len(weights) < 2:
        return

    weights.sort(key=lambda x: x[0])
    for i in range(1, len(weights)):
        prev_w, prev_f = weights[i - 1]
        curr_w, curr_f = weights[i]
        if curr_w - prev_w > 1:
            issues.append(Issue(
                "warning", str(curr_f),
                f"集合 [{collection_name}] weight 不连续: {prev_w} → {curr_w}"
            ))


def _check_duplicate_titles(collection_name: str, files: list[tuple[Path, dict]], issues: list[Issue]) -> None:
    """检查集合内重复标题。"""
    titles: dict[str, list[Path]] = {}
    for f, meta in files:
        title = meta.get("title", "")
        if title:
            titles.setdefault(title, []).append(f)

    for title, paths in titles.items():
        if len(paths) > 1:
            issues.append(Issue(
                "warning", str(paths[0]),
                f"集合 [{collection_name}] 重复标题: '{title}' ({len(paths)} 篇)"
            ))
