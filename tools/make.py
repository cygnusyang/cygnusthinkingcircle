#!/usr/bin/env python3
"""
make.py —— 统一内容制作入口

knowledge-base 源文章 → 博客 + 多平台适配内容

用法:
  make.py new <title>              创建新文章
  make.py build <article.md>       生成博客 + 所有平台内容
  make.py build --all              生成所有文章
  make.py build --platform xiaohongshu,zhihu  只生成指定平台
  make.py publish                  发布博客到 GitHub Pages
  make.py status                   查看文章状态
  make.py config                   查看/设置配置
"""

import argparse
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# 确保 tools/ 在 sys.path 中
TOOLS_DIR = Path(__file__).parent
sys.path.insert(0, str(TOOLS_DIR.parent))

from tools.lib.article import (
    Article,
    load_article,
    generate_hugo_frontmatter,
    find_articles,
)
from tools.lib.platforms import (
    PLATFORMS,
    get_platform,
    list_platforms,
)
from tools.lib.publisher import publish_to_blog, save_platform_output
from tools.lib.llm import adapt_for_platform
from tools.lib.collection import build_collection, list_projects, add_project_card, normalize_slug, resolve_project_by_input

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# 路径配置
BASE_DIR = Path(__file__).parent.parent
KB_DIR = BASE_DIR / "knowledge-base"
CONTENT_DIR = BASE_DIR / "cygnusyang.github.io" / "content"
STATIC_DIR = BASE_DIR / "cygnusyang.github.io" / "static"
OUTPUT_DIR = TOOLS_DIR / "output"
PROMPTS_DIR = TOOLS_DIR / "prompts"
ENV_FILE = BASE_DIR / ".env"


def _load_env() -> None:
    """加载 .env 文件中的环境变量"""
    if ENV_FILE.exists():
        with open(ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                value = value.strip()
                # 去掉行尾注释 (保留值中间的 #)
                if " #" in value:
                    value = value[: value.rindex(" #")].strip()
                os.environ.setdefault(key.strip(), value)


def _escape_yaml(value: str) -> str:
    """转义 YAML 字符串中的特殊字符"""
    return value.replace("\\", "\\\\").replace('"', '\\"')


def cmd_new(args: argparse.Namespace) -> None:
    """创建新文章"""
    title = args.title.strip()
    if not title:
        logger.error("文章标题不能为空")
        return

    date = datetime.now().strftime("%Y-%m-%d")
    slug = title.lower().replace(" ", "-")[:80]
    filename = f"{date}-{slug}.md"

    template_path = KB_DIR / "articles" / "template.md"
    if not template_path.exists():
        logger.error(f"模板文件不存在: {template_path}")
        return

    template = template_path.read_text(encoding="utf-8")
    escaped_title = _escape_yaml(title)
    content = template.replace('title: ""', f'title: "{escaped_title}"')

    import re
    content = re.sub(r"date:\s*[\d-]+", f"date: {date}", content)

    output_path = KB_DIR / "articles" / filename
    if output_path.exists():
        logger.error(f"文章已存在: {output_path}")
        return

    output_path.write_text(content, encoding="utf-8")
    logger.info(f"✅ 创建文章: {output_path}")
    logger.info(f"   用编辑器打开编辑内容后，运行: make.py build {filename}")


def cmd_build(args: argparse.Namespace) -> None:
    """构建文章 —— 生成博客 + 各平台内容"""
    _load_env()

    # 确定要处理的文章列表
    if args.all:
        article_paths = find_articles(KB_DIR)
        if not article_paths:
            logger.error("knowledge-base/articles/ 中没有文章")
            return
    elif args.article:
        article_file = KB_DIR / "articles" / args.article
        if not article_file.exists():
            logger.error(f"文章不存在: {article_file}")
            available = [f.name for f in find_articles(KB_DIR)]
            if available:
                logger.info(f"可用文章: {available}")
            return
        article_paths = [article_file]
    else:
        logger.error("请指定文章文件名或使用 --all 参数")
        logger.info("用法: make.py build <article.md>  或  make.py build --all")
        return

    # 确定要生成的平台
    if args.platform:
        platform_keys = [k.strip() for k in args.platform.split(",")]
        platforms = []
        for key in platform_keys:
            p = get_platform(key)
            if p:
                platforms.append(p)
            else:
                logger.warning(f"未知平台: {key}")
    else:
        platforms = list_platforms()

    blog_platforms = [p for p in platforms if p.key == "blog"]
    non_blog_platforms = [p for p in platforms if p.key != "blog"]

    # 检查 LLM 需求
    use_llm = len(non_blog_platforms) > 0
    if use_llm:
        from tools.lib.llm import _api_key, _provider

        key = _api_key()
        if not key:
            logger.warning(
                f"⚠️  LLM_API_KEY 未设置 (provider={_provider()})。"
                "非博客平台将跳过 LLM 适配，只生成博客。\n"
                "设置: export LLM_API_KEY=sk-..."
                "  或创建 .env 文件 (参考 .env.example)"
            )
            non_blog_platforms = []

    total = 0
    for article_path in article_paths:
        logger.info(f"\n📄 处理: {article_path.name}")
        article = load_article(article_path)
        if not article:
            continue

        # 1. 生成博客版本（直接发布）
        for bp in blog_platforms:
            publish_to_blog(article, KB_DIR, CONTENT_DIR, STATIC_DIR)

        # 2. 生成其他平台版本（LLM 适配）
        if non_blog_platforms:
            logger.info("  🤖 LLM 适配各平台...")
            for platform in non_blog_platforms:
                logger.info(f"    生成 {platform.name}...")
                result = adapt_for_platform(
                    title=article.title,
                    body=article.body,
                    tags=article.tags,
                    keywords=article.keywords,
                    summary=article.summary,
                    prompt_file=platform.prompt_file,
                    prompts_dir=PROMPTS_DIR,
                )
                if result:
                    save_platform_output(
                        result, platform.key, article.slug, OUTPUT_DIR
                    )
                else:
                    logger.warning(f"    {platform.name} 生成失败")

        total += 1

    logger.info(f"\n✅ 完成：处理了 {total} 篇文章")

    if non_blog_platforms:
        logger.info(f"📂 平台内容: {OUTPUT_DIR}")
    if blog_platforms:
        logger.info(f"📂 博客内容: {CONTENT_DIR / 'posts'}")
        logger.info("💡 下一步: make.py publish  # 发布到 GitHub Pages")


def cmd_publish(args: argparse.Namespace) -> None:
    """发布博客到 GitHub Pages"""
    import subprocess

    pages_dir = BASE_DIR / "cygnusyang.github.io"

    if not pages_dir.exists():
        logger.error(f"GitHub Pages 目录不存在: {pages_dir}")
        return

    logger.info("📤 发布到 GitHub Pages...")

    try:
        # git add
        subprocess.run(
            ["git", "-C", str(pages_dir), "add", "content/posts/"],
            check=True,
        )

        # 检查是否有变更
        result = subprocess.run(
            ["git", "-C", str(pages_dir), "diff", "--cached", "--quiet"],
            capture_output=True,
        )
        if result.returncode == 0:
            logger.info("没有新的变更，跳过提交")
            return

        # git commit
        msg = args.message or "post: 发布新文章"
        subprocess.run(
            ["git", "-C", str(pages_dir), "commit", "-m", msg],
            check=True,
        )

        # git push
        subprocess.run(
            ["git", "-C", str(pages_dir), "push"],
            check=True,
        )

        logger.info("✅ 发布完成！稍后访问 https://cygnusyang.github.io/")

    except subprocess.CalledProcessError as e:
        logger.error(f"Git 操作失败: {e}")


def cmd_status(args: argparse.Namespace) -> None:
    """查看文章状态"""
    articles = find_articles(KB_DIR)

    logger.info("=" * 60)
    logger.info("📊 内容状态总览")
    logger.info("=" * 60)

    if not articles:
        logger.info("\nknowledge-base/articles/ 中没有文章。")
        logger.info("运行: make.py new \"你的文章标题\"  创建第一篇")
        return

    logger.info(f"\n源文章 ({len(articles)} 篇):")
    for ap in articles:
        article = load_article(ap)
        if article:
            published = "已发布" if article.platforms else "未发布"
            platforms_str = ", ".join(article.platforms) if article.platforms else "无"
            logger.info(f"  📝 {article.title}")
            logger.info(f"     日期: {article.date} | 平台: {platforms_str}")

    # 检查各平台 output 目录
    logger.info("\n平台输出:")
    for platform in list_platforms():
        output_dir = OUTPUT_DIR / platform.output_dir
        if output_dir.exists():
            files = list(output_dir.glob("*.md"))
            if files:
                logger.info(f"  ✅ {platform.name}: {len(files)} 篇")
            else:
                logger.info(f"  📭 {platform.name}: 0 篇")
        else:
            logger.info(f"  📭 {platform.name}: 未生成")

    # 检查博客目录
    posts_dir = CONTENT_DIR / "posts"
    if posts_dir.exists():
        post_files = list(posts_dir.glob("*.md"))
        logger.info(f"\n博客 (content/posts/): {len(post_files)} 篇")


def cmd_collection(args: argparse.Namespace) -> None:
    """管理知识库项目集合 —— 批量转换为 Hugo Pages"""
    if args.collection_command == "list":
        projects = list_projects(KB_DIR)
        if not projects:
            logger.info("knowledge-base/articles/ 中没有项目目录。")
            return

        logger.info("=" * 60)
        logger.info("📚 可用项目集合")
        logger.info("=" * 60)
        # 按 NN 编号排序（主要按编号，编号相同按路径字母序）
        sorted_items = sorted(projects.items(), key=lambda x: (x[1]["nn"], x[1]["display_path"]))
        max_len = max(len(info["display_path"]) for _, info in sorted_items) if sorted_items else 30
        for slug, info in sorted_items:
            status = f"{info['article_count']} 篇文章" if info["article_count"] > 0 else "无文章"
            logger.info(f"  {info['display_path']:{max_len}s}  {status}")

    elif args.collection_command == "build":
        if args.all:
            projects = list_projects(KB_DIR)
            slugs = [s for s, i in projects.items() if i["article_count"] > 0]
            if not slugs:
                logger.error("没有可构建的项目（需要有 blog 子目录）。")
                return
            logger.info(f"构建所有项目: {', '.join(slugs)}")
        elif args.project:
            # 从用户输入解析项目 slug（支持带 NN 前缀、裸 slug、部分匹配）
            resolved = resolve_project_by_input(args.project, KB_DIR)
            if resolved:
                slugs = [resolved]
            else:
                logger.error(f"项目不存在: {args.project}")
                projects = list_projects(KB_DIR)
                logger.info("可用项目:")
                sorted_items = sorted(projects.items(), key=lambda x: (x[1]["nn"], x[1]["display_path"]))
                for slug, info in sorted_items:
                    if info["article_count"] > 0:
                        logger.info(f"  {info['display_path']} ({info['article_count']} 篇)")
                return
        else:
            logger.error("请指定项目名或使用 --all")
            return

        total = 0
        for slug in slugs:
            logger.info(f"\n📦 构建集合: {slug}")
            count = build_collection(
                project_slug=slug,
                kb_dir=KB_DIR,
                content_dir=CONTENT_DIR,
                source_subdir=args.source or "blog",
                date=args.date,
            )
            total += count

        logger.info(f"\n✅ 完成：生成了 {total} 篇文章到 {CONTENT_DIR / 'posts'}")
        logger.info("💡 下一步: make.py publish  # 发布到 GitHub Pages")

    elif args.collection_command == "add-card":
        if not args.project:
            logger.error("请指定项目名")
            return
        logger.info(f"\n🃏 添加首页卡片: {args.project}")
        success = add_project_card(
            project_slug=args.project,
            kb_dir=KB_DIR,
            content_dir=CONTENT_DIR,
            icon=args.icon,
            description=args.desc,
        )
        if success:
            logger.info("💡 编辑 _index.md 可自定义图标和描述")


def cmd_config(args: argparse.Namespace) -> None:
    """查看/设置配置"""
    _load_env()

    logger.info("=" * 60)
    logger.info("⚙️  配置")
    logger.info("=" * 60)

    # LLM 配置
    from tools.lib.llm import _provider, _api_key, _model, _base_url, DEFAULTS

    provider = _provider()
    logger.info(f"\n🔌 LLM 提供商: {provider}")

    key = _api_key()
    if key and len(key) > 12:
        masked_key = key[:8] + "..." + key[-4:]
    else:
        masked_key = "(未设置)"
    logger.info(f"   API Key:     {masked_key}")

    model = _model()
    logger.info(f"   Model:       {model}")

    base_url = _base_url() or "(SDK默认)"
    logger.info(f"   Base URL:    {base_url}")

    logger.info(f"\n📂 目录:")
    logger.info(f"   知识库:      {KB_DIR}")
    logger.info(f"   博客输出:    {CONTENT_DIR / 'posts'}")
    logger.info(f"   平台输出:    {OUTPUT_DIR}")
    logger.info(f"   Prompts:     {PROMPTS_DIR}")

    logger.info(f"\n📋 可用平台 ({len(PLATFORMS)} 个):")
    for p in list_platforms():
        logger.info(f"   {p.key:20s} - {p.description}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="make.py —— 统一内容制作入口",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  make.py new "我的新文章标题"
  make.py build 2026-05-05-my-article.md
  make.py build --all
  make.py build --platform xiaohongshu,zhihu 2026-05-05-my-article.md
  make.py publish
  make.py status
  make.py config
  make.py collection list
  make.py collection build gstack
  make.py collection build --all
  make.py collection add-card harness
  make.py collection add-card myproject --icon "🚀" --desc "项目描述"
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # new
    parser_new = subparsers.add_parser("new", help="创建新文章")
    parser_new.add_argument("title", help="文章标题")

    # build
    parser_build = subparsers.add_parser("build", help="构建文章")
    parser_build.add_argument("article", nargs="?", help="文章文件名")
    parser_build.add_argument("--all", action="store_true", help="处理所有文章")
    parser_build.add_argument(
        "--platform",
        help="指定平台，逗号分隔 (如 xiaohongshu,zhihu)",
    )

    # publish
    parser_publish = subparsers.add_parser("publish", help="发布到 GitHub Pages")
    parser_publish.add_argument("-m", "--message", help="自定义 commit 消息")

    # collection
    parser_collection = subparsers.add_parser("collection", help="管理项目集合")
    collection_subs = parser_collection.add_subparsers(dest="collection_command")

    parser_col_list = collection_subs.add_parser("list", help="列出可用项目")
    parser_col_build = collection_subs.add_parser("build", help="构建集合")
    parser_col_build.add_argument("project", nargs="?", help="项目标识 (如 gstack, openclaw)")
    parser_col_build.add_argument("--all", action="store_true", help="构建所有项目")
    parser_col_build.add_argument("--source", help="源子目录 (默认 blog)")
    parser_col_build.add_argument("--date", help="发布日期 YYYY-MM-DD (默认今天)")

    parser_col_add = collection_subs.add_parser("add-card", help="添加首页卡片")
    parser_col_add.add_argument("project", help="项目标识 (如 harness, gbrain)")
    parser_col_add.add_argument("--icon", help="卡片图标 emoji (默认自动推导)")
    parser_col_add.add_argument("--desc", help="卡片描述文字 (默认 技术文档与开发指南)")

    # status
    subparsers.add_parser("status", help="查看文章状态")

    # config
    subparsers.add_parser("config", help="查看配置")

    args = parser.parse_args()

    if args.command == "new":
        cmd_new(args)
    elif args.command == "build":
        cmd_build(args)
    elif args.command == "publish":
        cmd_publish(args)
    elif args.command == "collection":
        cmd_collection(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "config":
        cmd_config(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
