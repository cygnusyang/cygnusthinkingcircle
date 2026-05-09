#!/usr/bin/env python3
"""
内容多平台生成脚本
从 cygnusyang.github.io/_posts/ 的已发布文章生成各平台适配版本
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Optional

from utils import parse_frontmatter, extract_frontmatter_value

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# 路径配置
BASE_DIR = Path(__file__).parent.parent
POSTS_DIR = BASE_DIR / "cygnusyang.github.io" / "_posts"
PLATFORMS_DIR = BASE_DIR / "tools" / "templates"
OUTPUT_DIR = BASE_DIR / "tools" / "output"

# 常量定义
SECTION_PROBLEM = "核心问题"
SECTION_MODEL = "核心模型"


def extract_sections(content: str) -> Dict[str, str]:
    """提取文章各部分"""
    sections: Dict[str, str] = {}
    lines = content.split('\n')

    current_section: Optional[str] = None
    current_content: list[str] = []

    for line in lines:
        if line.startswith('##'):
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = line.replace('##', '').strip()
            current_content = []
        else:
            current_content.append(line)

    if current_section:
        sections[current_section] = '\n'.join(current_content).strip()

    return sections


def generate_xiaohongshu(title: str, sections: Dict[str, str]) -> str:
    """生成小红书版本"""
    try:
        template_path = PLATFORMS_DIR / "xiaohongshu" / "template.md"
        template = template_path.read_text()
        content = template.replace("## 痛点描述", sections.get(SECTION_PROBLEM, ""))
        return content.replace("## 为什么会这样？\n\n[用简单模型解释]", sections.get(SECTION_MODEL, ""))
    except Exception as e:
        logger.error(f"生成小红书版本失败: {e}")
        return ""


def generate_douyin(title: str, sections: Dict[str, str]) -> str:
    """生成抖音版本"""
    try:
        template_path = PLATFORMS_DIR / "douyin" / "template.md"
        return template_path.read_text()
    except Exception as e:
        logger.error(f"生成抖音版本失败: {e}")
        return ""


def generate_wechat(title: str, sections: Dict[str, str]) -> str:
    """生成微信版本"""
    try:
        template_path = PLATFORMS_DIR / "wechat" / "template.md"
        template = template_path.read_text()
        content = template.replace("### 核心问题", f"### 核心问题\n\n{sections.get(SECTION_PROBLEM, '')}")
        return content.replace("### 核心模型", f"### 核心模型\n\n{sections.get(SECTION_MODEL, '')}")
    except Exception as e:
        logger.error(f"生成微信版本失败: {e}")
        return ""


def generate_baijiahao(title: str, sections: Dict[str, str]) -> str:
    """生成百家号版本"""
    try:
        template_path = PLATFORMS_DIR / "baijiahao" / "template.md"
        template = template_path.read_text()
        content = template.replace("## 痛点描述", sections.get(SECTION_PROBLEM, ""))
        return content.replace("## 核心原因分析", sections.get(SECTION_MODEL, ""))
    except Exception as e:
        logger.error(f"生成百家号版本失败: {e}")
        return ""


def generate_summary(title: str, sections: Dict[str, str]) -> str:
    """生成摘要"""
    try:
        template_path = BASE_DIR / "tools" / "summary.md"
        template = template_path.read_text()
        return template.replace("## [标题]", f"## {title}")
    except Exception as e:
        logger.error(f"生成摘要失败: {e}")
        return ""


def process_post(post_file: Path, platform_keys: set[str]) -> bool:
    """处理单篇文章"""
    logger.info(f"处理: {post_file.name}")

    try:
        content = post_file.read_text()
    except (IOError, UnicodeDecodeError) as e:
        logger.error(f"  错误: 无法读取文件 - {e}")
        return False

    frontmatter, body = parse_frontmatter(content)
    sections = extract_sections(body)

    # 提取标题
    title = extract_frontmatter_value(frontmatter, "title") or post_file.stem

    generators = {
        "xiaohongshu": (OUTPUT_DIR / "xiaohongshu" / f"{post_file.stem}.md", generate_xiaohongshu),
        "douyin": (OUTPUT_DIR / "douyin" / f"{post_file.stem}.md", generate_douyin),
        "wechat": (OUTPUT_DIR / "wechat" / f"{post_file.stem}.md", generate_wechat),
        "baijiahao": (OUTPUT_DIR / "baijiahao" / f"{post_file.stem}.md", generate_baijiahao),
        "summary": (OUTPUT_DIR / "summary.md", generate_summary),
    }

    outputs = []
    for platform_key in platform_keys:
        item = generators.get(platform_key)
        if not item:
            logger.warning(f"  跳过未知平台: {platform_key}")
            continue
        output_path, generator = item
        outputs.append((output_path, generator(title, sections)))

    success = True
    for output_path, output_content in outputs:
        if not output_content:
            continue
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(output_content)
            logger.info(f"  生成: {output_path.relative_to(BASE_DIR)}")
        except IOError as e:
            logger.error(f"  错误: 无法写入文件 {output_path} - {e}")
            success = False

    return success


def main() -> None:
    """主函数"""
    if len(sys.argv) < 4 or sys.argv[1] != "--platform":
        logger.info("此旧脚本不会默认生成任何平台内容。")
        logger.info("用法: python tools/generate.py --platform xiaohongshu,wechat <post-file.md>")
        logger.info("或: python tools/generate.py --platform xiaohongshu,wechat all")
        logger.info("推荐使用: python tools/make.py build --platform xiaohongshu,wechat <article.md>")
        return

    platform_keys = {item.strip() for item in sys.argv[2].split(",") if item.strip()}
    if not platform_keys:
        logger.error("请通过 --platform 指定至少一个平台")
        return

    arg = sys.argv[3]

    if arg == "all":
        # 处理所有文章
        count = 0
        try:
            for post_file in POSTS_DIR.glob("*.md"):
                if process_post(post_file, platform_keys):
                    count += 1
            logger.info(f"\n完成：处理了 {count} 篇文章")
        except Exception as e:
            logger.error(f"处理所有文章时出错: {e}")
    else:
        # 处理指定文件
        post_file = POSTS_DIR / arg
        if not post_file.exists():
            # 尝试不带路径
            post_file = next(POSTS_DIR.glob(f"*{arg}*"), None)
        if post_file and post_file.exists():
            process_post(post_file, platform_keys)
        else:
            logger.error(f"错误: 文章不存在: {arg}")
            available = [f.name for f in POSTS_DIR.glob('*.md')]
            logger.info(f"可用文章: {available}")


if __name__ == "__main__":
    main()
