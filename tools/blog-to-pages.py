#!/usr/bin/env python3
"""
从 IdealZero/knowledgebase 的 blog 文件夹发布文章到 GitHub Pages
"""

import os
import re
import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List

from utils import sanitize_filename

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# 路径配置
BASE_DIR = Path(__file__).parent.parent
IDEALZERO_BASE = Path(os.environ.get("IDEALZERO_PATH", "/Users/cygnus/work/IdealZero/knowledgebase"))
POSTS_DIR = BASE_DIR / "cygnusyang.github.io" / "_posts"

# 可用的 blog 文件夹
BLOG_FOLDERS = {
    "openclaw": "01 openclaw",
    "gstack": "02 gstack",
    "gbrain": "03 gbrain",
    "claudecode": "06 claudecode",
}


def extract_title_from_content(content: str) -> Optional[str]:
    """从文章内容中提取标题"""
    # 先尝试提取第一个一级标题
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if match:
        title = match.group(1).strip()
        # 移除章节标记（如"第一章："、"第X节："）
        title = re.sub(r'^第[一二三四五六七八九十]+\s*[章节：]\s*', '', title)
        # 移除前导的冒号（如果有）
        if title.startswith('：'):
            title = title[1:].strip()
        return title

    # 如果没有找到，返回 None
    return None


def extract_title_from_path(path: Path) -> str:
    """从文件路径中提取标题"""
    # 从文件名提取：04-client-ux/23-webchat.md -> 23-webchat
    return path.stem


def generate_frontmatter(title: str, date: str, category: Optional[str] = None, tags: Optional[List[str]] = None) -> str:
    """生成 Jekyll frontmatter"""
    frontmatter = ['---']
    frontmatter.append(f'title: {title}')
    frontmatter.append(f'date: {date}')
    if category:
        frontmatter.append(f'category: {category}')
    if tags:
        frontmatter.append(f'tags: [{", ".join(tags)}]')
    frontmatter.append('---')
    return '\n'.join(frontmatter)


def process_article(article_file: Path, blog_folder_name: str) -> bool:
    """处理单篇文章"""
    logger.info(f"处理: {article_file.relative_to(IDEALZERO_BASE)}")

    try:
        content = article_file.read_text()
    except (IOError, UnicodeDecodeError) as e:
        logger.error(f"  错误: 无法读取文件 - {e}")
        return False

    # 提取标题
    title = extract_title_from_content(content)
    if not title:
        title = extract_title_from_path(article_file)
    if not title:
        title = article_file.stem

    logger.info(f"  标题: {title}")

    # 使用今天的日期
    date = datetime.now().strftime("%Y-%m-%d")

    # 从路径推断分类
    category_parts = article_file.relative_to(IDEALZERO_BASE).parts
    category: Optional[str] = None
    if len(category_parts) >= 2:
        # 路径格式：XX 项目名/blog/分类/文件名.md
        category = category_parts[2].replace('-', ' ')

    # 推断标签
    tags: List[str] = []
    if category:
        tags.append(category)

    # 生成 frontmatter
    frontmatter = generate_frontmatter(title, date, category, tags)

    # 生成文件名：YYYY-MM-DD-标题.md
    safe_title = sanitize_filename(title)
    filename = f"{date}-{safe_title}.md"

    # 合并 frontmatter 和内容
    full_content = frontmatter + '\n\n' + content

    # 写入 _posts
    output_path = POSTS_DIR / filename
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(full_content)
    except IOError as e:
        logger.error(f"  错误: 无法写入文件 - {e}")
        return False

    logger.info(f"  生成: {filename}")
    return True


def main() -> None:
    """主函数"""
    if len(sys.argv) < 2:
        logger.info("用法: python tools/blog-to-pages.py <blog-folder>")
        logger.info(f"可用的 blog 文件夹: {', '.join(BLOG_FOLDERS.keys())}")
        return

    blog_key = sys.argv[1]

    if blog_key not in BLOG_FOLDERS:
        logger.error(f"错误: 未知的 blog 文件夹 '{blog_key}'")
        logger.info(f"可用的 blog 文件夹: {', '.join(BLOG_FOLDERS.keys())}")
        return

    # 构建 blog 文件夹路径
    blog_folder_name = BLOG_FOLDERS[blog_key]
    blog_folder = IDEALZERO_BASE / blog_folder_name / "blog"

    if not blog_folder.exists():
        logger.error(f"错误: blog 文件夹不存在: {blog_folder}")
        logger.info("你可以通过设置环境变量 IDEALZERO_PATH 来指定正确的路径")
        return

    # 找到所有 Markdown 文件
    try:
        md_files = list(blog_folder.glob("**/*.md"))
    except Exception as e:
        logger.error(f"错误: 无法搜索文件 - {e}")
        return

    if not md_files:
        logger.info(f"没有找到 Markdown 文件在: {blog_folder}")
        return

    logger.info(f"找到 {len(md_files)} 篇文章")

    # 处理每篇文章
    count = 0
    for article_file in sorted(md_files):
        if process_article(article_file, blog_folder_name):
            count += 1

    logger.info(f"\n完成：处理了 {count} 篇文章")
    logger.info(f"文章位置: {POSTS_DIR}")


if __name__ == "__main__":
    main()
