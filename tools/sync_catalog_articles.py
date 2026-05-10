#!/usr/bin/env python3
"""Create a catalog-organized mirror of knowledge-base articles.

The original knowledge-base/articles tree stays untouched. This script reads
knowledge-base/catalog.yaml and writes a navigable article mirror to
knowledge-base/cataloged-articles.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "knowledge-base" / "catalog.yaml"
SOURCE_ROOT = ROOT / "knowledge-base" / "articles"
DEST_ROOT = ROOT / "knowledge-base" / "cataloged-articles"

EXCLUDED_DIRS = {
    ".git",
    ".github",
    ".claude",
    ".vscode",
    "node_modules",
    "source",
}

EXCLUDED_FILES = {
    ".DS_Store",
}


def numbered_name(weight: int, title: str) -> str:
    return f"{weight:02d}-{title.replace('/', '-')}"


def copy_tree(src: Path, dst: Path) -> None:
    if src.is_dir():
        if src.name in EXCLUDED_DIRS:
            return
        dst.mkdir(parents=True, exist_ok=True)
        for child in sorted(src.iterdir(), key=lambda p: p.name):
            copy_tree(child, dst / child.name)
        return

    if src.name in EXCLUDED_FILES:
        return
    if src.suffix.lower() != ".md":
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def preferred_article_root(source_dir: Path) -> Path:
    blog_dir = source_dir / "blog"
    return blog_dir if blog_dir.is_dir() else source_dir


def write_catalog_readme(catalog_dir: Path, catalog: dict) -> None:
    lines = [
        f"# {catalog['title']}",
        "",
        catalog.get("description", ""),
        "",
        "## 系列",
        "",
    ]
    for child in sorted(catalog.get("children", []), key=lambda c: c.get("weight", 99)):
        lines.append(f"- {child['weight']:02d}-{child['title']}: `{child['source']}` -> `{child['output']}`")
    lines.append("")
    (catalog_dir / "README.md").write_text("\n".join(lines), encoding="utf-8")


def sync() -> None:
    data = yaml.safe_load(CATALOG_PATH.read_text(encoding="utf-8"))
    catalogs = sorted(data.get("catalogs", []), key=lambda c: c.get("weight", 99))

    if DEST_ROOT.exists():
        shutil.rmtree(DEST_ROOT)
    DEST_ROOT.mkdir(parents=True, exist_ok=True)

    summary_lines = [
        "# Cataloged Articles",
        "",
        "此目录由 `tools/sync_catalog_articles.py` 根据 `knowledge-base/catalog.yaml` 生成。",
        "原始 `knowledge-base/articles` 不会被移动或删除。",
        "",
    ]

    for catalog in catalogs:
        catalog_dir = DEST_ROOT / numbered_name(int(catalog["weight"]), catalog["title"])
        catalog_dir.mkdir(parents=True, exist_ok=True)
        write_catalog_readme(catalog_dir, catalog)
        summary_lines.append(f"## {catalog['weight']:02d}-{catalog['title']}")
        summary_lines.append("")

        children = sorted(catalog.get("children", []), key=lambda c: c.get("weight", 99))
        for index, child in enumerate(children, start=1):
            source_dir = SOURCE_ROOT / child["source"]
            dest_dir = catalog_dir / numbered_name(index, child["title"])
            if not source_dir.exists():
                summary_lines.append(f"- MISSING `{child['source']}`")
                continue
            article_root = preferred_article_root(source_dir)
            copy_tree(article_root, dest_dir)
            summary_lines.append(f"- `{dest_dir.relative_to(ROOT)}`")
        summary_lines.append("")

    (DEST_ROOT / "README.md").write_text("\n".join(summary_lines), encoding="utf-8")


if __name__ == "__main__":
    sync()
