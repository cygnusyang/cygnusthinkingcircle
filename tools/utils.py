#!/usr/bin/env python3
"""
共用工具函数
"""

import re
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


def parse_frontmatter(content: str) -> Tuple[Optional[str], str]:
    """解析 Jekyll frontmatter"""
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            return parts[1], parts[2]
    return None, content


def extract_frontmatter_value(frontmatter: Optional[str], key: str) -> Optional[str]:
    """从 frontmatter 提取指定键的值"""
    if not frontmatter:
        return None
    match = re.search(rf'{key}:\s*(.+)', frontmatter)
    if match:
        return match.group(1).strip().strip('"\'')
    return None


def sanitize_filename(title: str) -> str:
    """清理标题生成安全的文件名

    保留中文、英文、数字、空格和短横线，转换空格为短横线
    """
    safe_title = re.sub(r'[^\w\u4e00-\u9fff\s-]', '', title).strip()
    return safe_title.replace(' ', '-')
