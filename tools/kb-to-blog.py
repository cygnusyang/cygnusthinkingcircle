#!/usr/bin/env python3
"""
知识库到博客的转换脚本
从 knowledge-base/articles/ 转换文章到 cygnusyang.github.io/_posts/
"""

import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from utils import parse_frontmatter, extract_frontmatter_value, sanitize_filename

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# 路径配置
BASE_DIR = Path(__file__).parent.parent
KB_DIR = BASE_DIR / "knowledge-base" / "articles"
POSTS_DIR = BASE_DIR / "cygnusyang.github.io" / "_posts"


def process_article(article_file: Path) -> bool:
    """处理单篇文章"""
    logger.info(f"处理: {article_file.name}")

    # 如果是模板文件，跳过
    if article_file.name == "template.md":
        logger.info("  跳过模板文件")
        return False

    try:
        content = article_file.read_text()
    except (IOError, UnicodeDecodeError) as e:
        logger.error(f"  错误: 无法读取文件 - {e}")
        return False

    # 解析元数据
    frontmatter, body = parse_frontmatter(content)

    # 提取标题和日期
    title = extract_frontmatter_value(frontmatter, "title") or article_file.stem
    date = extract_frontmatter_value(frontmatter, "date")

    # 如果没有日期，使用今天
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    else:
        # 清理日期格式
        date = date.strip().split()[0]

    # 生成文件名：YYYY-MM-DD-标题.md
    safe_title = sanitize_filename(title)
    filename = f"{date}-{safe_title}.md"

    # 写入 _posts
    output_path = POSTS_DIR / filename
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content)
    except IOError as e:
        logger.error(f"  错误: 无法写入文件 - {e}")
        return False

    logger.info(f"  生成: {filename}")
    return True


def main() -> None:
    """主函数"""
    if len(sys.argv) < 2:
        logger.info("用法: python tools/kb-to-blog.py <article-file.md>")
        logger.info("或: python tools/kb-to-blog.py all  # 转换所有文章")
        return

    arg = sys.argv[1]

    if arg == "all":
        # 转换所有文章
        count = 0
        try:
            for article_file in KB_DIR.glob("*.md"):
                if article_file.name != "template.md":
                    if process_article(article_file):
                        count += 1
            logger.info(f"\n完成：转换了 {count} 篇文章")
        except Exception as e:
            logger.error(f"转换所有文章时出错: {e}")
    else:
        # 转换指定文件
        article_file = KB_DIR / arg
        if article_file.exists():
            process_article(article_file)
        else:
            logger.error(f"错误: 文章不存在: {article_file}")


if __name__ == "__main__":
    main()
