#!/usr/bin/env python3
"""
make.py —— 统一内容制作入口

knowledge-base 源文章 → 博客；显式指定时再生成多平台适配内容

用法:
  make.py new <title>              创建新文章
  make.py build <article.md>       只生成博客
  make.py build --all              生成所有文章
  make.py build --platform xiaohongshu,zhihu  只生成指定平台
  make.py publish                  发布博客到 GitHub Pages
  make.py status                   查看文章状态
  make.py config                   查看/设置配置
"""

import argparse
import logging
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# Shell completion support (requires: pip install argcomplete)
try:
    import argcomplete
    HAS_ARGCOMPLETE = True
except ImportError:
    HAS_ARGCOMPLETE = False

# 确保 tools/ 在 sys.path 中
TOOLS_DIR = Path(__file__).parent
sys.path.insert(0, str(TOOLS_DIR.parent))

from tools.lib.article import (
    load_article,
    find_articles,
)
from tools.lib.platforms import (
    PLATFORMS,
    get_platform,
    list_platforms,
)
from tools.lib.publisher import publish_to_blog, save_platform_output
from tools.lib.llm import adapt_for_platform
from tools.lib.collection import build_collection, list_projects, resolve_project_by_input
from tools.lib.validator import validate_article, validate_collection_posts, Issue

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
PAGES_DIR = BASE_DIR / "cygnusyang.github.io"  # Hugo 子模块目录


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

    # 确定目标目录
    resolved_slug = None
    project_dir = None
    if args.category:
        resolved_slug = resolve_project_by_input(args.category, KB_DIR)
        if not resolved_slug:
            logger.error(f"集合不存在: {args.category}")
            _show_available_projects()
            return
        from tools.lib.collection import _discover_projects
        discovered = _discover_projects(KB_DIR)
        project_dir = discovered.get(resolved_slug)
        if not project_dir:
            logger.error(f"无法找到集合目录: {resolved_slug}")
            return

    # 确定模板：优先集合专属模板，其次指定模板，最后通用模板
    if args.template:
        template_name = args.template if args.template.endswith(".md") else f"{args.template}.md"
        template_path = KB_DIR / "articles" / template_name
        # 如果指定了集合，也尝试在集合中找
        if not template_path.exists() and project_dir:
            collection_template = project_dir / "blog" / template_name
            if collection_template.exists():
                template_path = collection_template
        if not template_path.exists():
            logger.error(f"模板文件不存在: {template_path}")
            return
    elif project_dir:
        # 优先集合专属模板
        collection_template = project_dir / "blog" / "template.md"
        if collection_template.exists():
            template_path = collection_template
        else:
            template_path = KB_DIR / "articles" / "template.md"
        if not template_path.exists():
            logger.error(f"模板文件不存在: {template_path}")
            return
    else:
        template_path = KB_DIR / "articles" / "template.md"
        if not template_path.exists():
            logger.error(f"模板文件不存在: {template_path}")
            return

    template = template_path.read_text(encoding="utf-8")
    escaped_title = _escape_yaml(title)
    content = template.replace('title: ""', f'title: "{escaped_title}"')
    content = re.sub(r"date:\s*[\d-]+", f"date: {date}", content)

    # 确定输出路径和文件名
    if project_dir:
        # 在集合的 blog/ 子目录下创建
        blog_dir = project_dir / "blog"
        if not blog_dir.exists():
            blog_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"📁 创建目录: {blog_dir}")

        # 自动检测下一个可用的章节号
        existing_files = [
            f for f in sorted(blog_dir.rglob("*.md"))
            if f.name not in {"README.md", "TODO.md", "CLAUDE.md", "_index.md", "template.md"}
        ]
        max_chapter = 0
        for ef in existing_files:
            ch = _extract_chapter_from_filename(ef.name)
            if ch > max_chapter:
                max_chapter = ch
        next_chapter = max_chapter + 1

        slug = title.lower().replace(" ", "-")[:80]
        filename = f"{next_chapter:02d}-{slug}.md"
        output_path = blog_dir / filename
    else:
        slug = title.lower().replace(" ", "-")[:80]
        filename = f"{date}-{slug}.md"
        output_path = KB_DIR / "articles" / filename
        next_chapter = None

    if output_path.exists():
        logger.error(f"文章已存在: {output_path}")
        return

    output_path.write_text(content, encoding="utf-8")

    if project_dir:
        logger.info(f"✅ 创建文章: {output_path}")
        logger.info(f"   集合: {args.category} | 章节号: 第{next_chapter:02d}章")
        logger.info(f"   用编辑器打开编辑内容后，运行: make.py collection build {args.category}")
    else:
        logger.info(f"✅ 创建文章: {output_path}")
        logger.info(f"   用编辑器打开编辑内容后，运行: make.py build {filename}")


def _extract_chapter_from_filename(filename: str) -> int:
    """从文件名提取章节号（NN- 开头的数字）。"""
    m = re.match(r"^(\d+)[-_]", filename)
    if m:
        return int(m.group(1))
    return 0


def _show_available_projects() -> None:
    """列出可用的集合项目。"""
    projects = list_projects(KB_DIR, PAGES_DIR)
    sorted_items = sorted(projects.items(), key=lambda x: (x[1]["nn"], x[1]["display_path"]))
    if sorted_items:
        logger.info("可用集合:")
        for slug, info in sorted_items:
            if info["article_count"] > 0:
                logger.info(f"  {info['display_path']} ({info['article_count']} 篇)")


def cmd_build(args: argparse.Namespace) -> None:
    """构建文章 —— 默认只生成博客；指定 --platform 时才生成对应平台内容。"""
    _load_env()

    # 增量构建状态
    incremental = getattr(args, 'incremental', False) and not getattr(args, 'force', False)
    build_cache = TOOLS_DIR / ".build-state.json"
    build_state = None
    if incremental:
        from tools.lib.build_state import BuildState
        build_state = BuildState(build_cache)

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

    # 增量模式：过滤未变更的文章
    if incremental and build_state:
        changed = []
        for ap in article_paths:
            if build_state.needs_build(ap):
                changed.append(ap)
        skipped = len(article_paths) - len(changed)
        if skipped > 0:
            logger.info(f"⏭️  跳过 {skipped} 篇未变更的文章")
        if not changed:
            logger.info("✅ 所有文章都是最新的，无需构建")
            build_state.save()
            return
        article_paths = changed
        logger.info(f"📄 需要构建: {len(article_paths)} 篇")

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
        if not platforms:
            logger.error("没有有效平台，已停止。可用平台请运行: make.py config")
            return
    else:
        platforms = [get_platform("blog")]

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
            if build_state:
                build_state.mark_built(article_path, bp.key)

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
                    if build_state:
                        build_state.mark_built(article_path, platform.key)
                else:
                    logger.warning(f"    {platform.name} 生成失败")

        total += 1

    # 保存构建状态
    if build_state:
        build_state.save()

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
        if args.message:
            msg = args.message
        else:
            # 自动根据变更内容生成 commit 消息
            result = subprocess.run(
                ["git", "-C", str(pages_dir), "diff", "--cached", "--name-only"],
                capture_output=True, text=True, check=True,
            )
            added_files = result.stdout.strip().split("\n") if result.stdout.strip() else []
            # 提取集合目录名或文章文件名
            collection_dirs = set()
            article_names = []
            for f in added_files:
                f = f.strip()
                if not f:
                    continue
                rel = f.replace("content/posts/", "", 1) if f.startswith("content/posts/") else f
                parts = rel.split("/")
                if len(parts) >= 2 and parts[0]:
                    collection_dirs.add(parts[0])
                    article_names.append(parts[-1])
            if collection_dirs:
                dir_list = ", ".join(sorted(collection_dirs))
                msg = f"post: update {dir_list} collection ({len(article_names)} articles)"
            elif article_names:
                msg = f"post: publish {len(article_names)} articles"
            else:
                msg = "post: publish new articles"
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

        # 更新父仓库子模块引用
        if args.update_submodule:
            _update_parent_submodule(BASE_DIR)

    except subprocess.CalledProcessError as e:
        logger.error(f"Git 操作失败: {e}")


def _update_parent_submodule(base_dir: Path) -> None:
    """更新父仓库的子模块引用并推送。"""
    import subprocess

    parent_dir = base_dir
    submodule_path = "cygnusyang.github.io"

    logger.info("📦 更新父仓库子模块引用...")

    try:
        # 检查父仓库是否有变更
        result = subprocess.run(
            ["git", "-C", str(parent_dir), "diff", "--cached", "--quiet", submodule_path],
            capture_output=True,
        )
        # 如果子模块未暂存，先 add
        if result.returncode != 0:
            subprocess.run(
                ["git", "-C", str(parent_dir), "add", submodule_path],
                check=True,
            )

        # 再次检查是否有变更
        result = subprocess.run(
            ["git", "-C", str(parent_dir), "diff", "--cached", "--quiet"],
            capture_output=True,
        )
        if result.returncode == 0:
            logger.info("  父仓库无变更，跳过提交")
            return

        subprocess.run(
            ["git", "-C", str(parent_dir), "commit", "-m", "chore: update submodule cygnusyang.github.io"],
            check=True,
        )

        subprocess.run(
            ["git", "-C", str(parent_dir), "push"],
            check=True,
        )

        logger.info("✅ 父仓库子模块引用已更新并推送")

    except subprocess.CalledProcessError as e:
        logger.warning(f"⚠️  父仓库更新失败（子模块推送成功）: {e}")


def cmd_validate(args: argparse.Namespace) -> None:
    """校验内容完整性。"""
    posts_dir = CONTENT_DIR / "posts"

    if args.article:
        # 校验单篇
        article_path = KB_DIR / "articles" / args.article
        if not article_path.exists():
            logger.error(f"文章不存在: {article_path}")
            return
        issues = validate_article(article_path)
        source = f"源文章 {args.article}"
    else:
        # 校验所有 posts
        issues = validate_collection_posts(posts_dir)
        source = "全部 posts"

    _report_issues(issues, source)


def _report_issues(issues: list[Issue], source: str) -> None:
    """按严重级别分类显示校验结果。"""
    errors = [i for i in issues if i.severity == "error"]
    warnings = [i for i in issues if i.severity == "warning"]

    logger.info("=" * 60)
    logger.info(f"🔍 内容校验 — {source}")
    logger.info("=" * 60)

    if not issues:
        logger.info("\n✅ 校验通过！未发现任何问题。")
        return

    if errors:
        logger.info(f"\n❌ 错误 ({len(errors)} 个):")
        for issue in errors:
            logger.info(f"  - [{issue.file}] {issue.message}")

    if warnings:
        logger.info(f"\n⚠️  警告 ({len(warnings)} 个):")
        for issue in warnings:
            logger.info(f"  - [{issue.file}] {issue.message}")

    logger.info(f"\n📊 总计: {len(errors)} 个错误, {len(warnings)} 个警告")
    if errors:
        logger.info("  请先修复错误后再构建")
    else:
        logger.info("  警告不影响构建")


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


def cmd_stats(args: argparse.Namespace) -> None:
    """内容统计报表。"""
    import json
    from collections import defaultdict

    posts_dir = CONTENT_DIR / "posts"
    kb_articles = find_articles(KB_DIR)

    # 收集 posts 数据
    collection_stats: dict[str, dict] = defaultdict(lambda: {"count": 0, "words": 0, "images": 0, "latest": ""})
    total_posts = 0
    total_words = 0
    total_images = 0
    monthly: dict[str, int] = defaultdict(int)

    if posts_dir.exists():
        for md_file in sorted(posts_dir.rglob("*.md")):
            if md_file.name == "_index.md":
                continue

            try:
                content = md_file.read_text(encoding="utf-8")
            except (IOError, UnicodeDecodeError):
                continue

            # 集合归属
            try:
                rel = md_file.relative_to(posts_dir)
                collection = rel.parts[0] if len(rel.parts) > 1 else "root"
            except ValueError:
                collection = "root"

            collection_stats[collection]["count"] += 1
            total_posts += 1

            # 字数
            word_count = len(content)
            collection_stats[collection]["words"] += word_count
            total_words += word_count

            # 图片数
            image_count = len(re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', content))
            collection_stats[collection]["images"] += image_count
            total_images += image_count

            # 日期（从文件名提取 YYYY-MM-DD）
            m = re.match(r"(\d{4}-\d{2}-\d{2})", md_file.name)
            if m:
                date_str = m.group(1)
                if date_str > collection_stats[collection]["latest"]:
                    collection_stats[collection]["latest"] = date_str
                # 月度统计（YYYY-MM）
                month = date_str[:7]
                monthly[month] += 1

    # 过滤单个集合
    if args.collection and args.collection in collection_stats:
        collection_stats = {args.collection: collection_stats[args.collection]}

    # JSON 输出
    if args.json:
        stats_data = {
            "total_posts": total_posts,
            "total_collections": len(collection_stats),
            "total_words": total_words,
            "total_images": total_images,
            "collections": {k: dict(v) for k, v in collection_stats.items()},
            "monthly": dict(sorted(monthly.items())),
        }
        print(json.dumps(stats_data, ensure_ascii=False, indent=2))
        return

    # 文本输出
    logger.info("=" * 60)
    logger.info("📈 内容统计报表")
    logger.info("=" * 60)

    # 总量
    logger.info(f"\n📊 总量:")
    logger.info(f"  Posts 总数:      {total_posts} 篇")
    logger.info(f"  集合数:          {len(collection_stats)} 个")
    logger.info(f"  KB 源文章:       {len(kb_articles)} 篇")
    logger.info(f"  总字数:          {total_words / 1000:.1f}K")
    logger.info(f"  图片引用:        {total_images} 张")

    # 按集合
    logger.info(f"\n📁 按集合:")
    sorted_collections = sorted(collection_stats.items(), key=lambda x: x[1]["count"], reverse=True)
    for name, stats in sorted_collections:
        latest = stats["latest"] or "N/A"
        words_k = stats["words"] / 1000
        logger.info(f"  {name:30s}  {stats['count']:>4d} 篇  {words_k:>6.1f}K 字  {stats['images']:>3d} 图  最新: {latest}")

    # 按时间（最近 6 个月）
    logger.info(f"\n📅 月度趋势 (最近 6 个月):")
    sorted_months = sorted(monthly.keys(), reverse=True)[:6]
    for month in reversed(sorted_months):
        bar = "█" * monthly[month]
        logger.info(f"  {month}  {monthly[month]:>3d} 篇  {bar}")

    # 按平台
    logger.info(f"\n📱 按平台:")
    for platform in list_platforms():
        output_dir = OUTPUT_DIR / platform.output_dir
        if output_dir.exists():
            count = len(list(output_dir.glob("*.md")))
            logger.info(f"  {platform.name:15s}  {count:>3d} 篇")
        else:
            logger.info(f"  {platform.name:15s}  未生成")


def _collection_dry_run(slugs: list[str], source_subdir: str) -> None:
    """预览集合构建结果，不实际写入文件。"""
    from tools.lib.collection import (
        _discover_projects,
        _find_markdown_files,
        _extract_title_from_body,
    )
    from tools.lib.article import parse_frontmatter

    projects = _discover_projects(KB_DIR)
    total = 0

    for slug in slugs:
        if slug not in projects:
            logger.warning(f"  ⚠️  项目不存在: {slug}")
            continue

        project_dir = projects[slug]
        source_dir = project_dir / source_subdir
        if not source_dir.exists():
            if source_subdir == "blog":
                source_dir = project_dir
            else:
                logger.warning(f"  ⚠️  源目录不存在: {source_dir}")
                continue

        md_files = _find_markdown_files(source_dir)
        if not md_files:
            logger.warning(f"  ⚠️  未找到 Markdown 文件: {source_dir}")
            continue

        logger.info(f"\n📦 预览构建: {slug}")
        logger.info(f"  源目录: {source_dir}")
        logger.info(f"  目标目录: {CONTENT_DIR / 'posts' / slug}")
        logger.info("")

        chapter_counter = 0
        for file_path in md_files:
            content = file_path.read_text(encoding="utf-8")
            metadata, body = parse_frontmatter(content)
            title = metadata.get("title", "")
            if not title:
                extracted = _extract_title_from_body(body)
                if extracted:
                    title = extracted[0]
                else:
                    title = file_path.stem

            chapter_counter += 1
            safe_title = title.lower().replace(" ", "-")[:60]
            target_filename = f"{datetime.now().strftime('%Y-%m-%d')}-第{chapter_counter:02d}章-{safe_title}.md"

            rel = file_path.relative_to(source_dir)
            logger.info(f"  {rel} → {target_filename}")

        logger.info(f"\n  预期生成: {chapter_counter} 篇文章")
        logger.info(f"  + _index.md (集合元数据)")
        total += chapter_counter

    logger.info(f"\n✅ 总计: {total} 篇文章将被生成")
    logger.info("  (dry-run 模式，未写入任何文件)")
    logger.info("  确认无误后运行: make.py collection build --all")


def cmd_collection(args: argparse.Namespace) -> None:
    """管理知识库项目集合 —— 批量转换为 Hugo Pages"""
    if args.collection_command == "list":
        projects = list_projects(KB_DIR, PAGES_DIR)
        if not projects:
            logger.info("knowledge-base/articles/ 中没有项目目录。")
            return

        logger.info("=" * 70)
        logger.info("📚 可用项目集合")
        logger.info("=" * 70)
        logger.info(f"  {'项目':<35s}  {'文章':>6s}  {'GitHub Pages'}")
        logger.info("  " + "-" * 55)
        # 按 NN 编号排序（主要按编号，编号相同按路径字母序）
        sorted_items = sorted(projects.items(), key=lambda x: (x[1]["nn"], x[1]["display_path"]))
        max_len = max(len(info["display_path"]) for _, info in sorted_items) if sorted_items else 30
        for slug, info in sorted_items:
            status = f"{info['article_count']} 篇" if info["article_count"] > 0 else "无文章"
            pages_status = "已推送" if info["pushed_to_pages"] else "未推送"
            logger.info(f"  {info['display_path']:{max_len}s}  {status:>6s}  {pages_status}")

    elif args.collection_command == "build":
        if args.all:
            projects = list_projects(KB_DIR, PAGES_DIR)
            slugs = [s for s, i in projects.items() if i["article_count"] > 0]
            if not slugs:
                logger.error("没有可构建的项目。")
                return
            logger.info(f"构建所有项目: {', '.join(slugs)}")
        elif args.project:
            # 从用户输入解析项目 slug（支持带 NN 前缀、裸 slug、部分匹配）
            resolved = resolve_project_by_input(args.project, KB_DIR)
            if resolved:
                slugs = [resolved]
            else:
                logger.error(f"项目不存在: {args.project}")
                projects = list_projects(KB_DIR, PAGES_DIR)
                logger.info("可用项目:")
                sorted_items = sorted(projects.items(), key=lambda x: (x[1]["nn"], x[1]["display_path"]))
                for slug, info in sorted_items:
                    if info["article_count"] > 0:
                        pages_mark = "✓" if info["pushed_to_pages"] else "✗"
                        logger.info(f"  {info['display_path']} ({info['article_count']} 篇) [{pages_mark}]")
                return
        else:
            logger.error("请指定项目名或使用 --all")
            return

        # dry-run 模式：预览不写入
        if getattr(args, 'dry_run', False):
            _collection_dry_run(slugs, args.source or "blog")
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
  # 文章构建
  make.py new "我的新文章标题"                 创建新文章
  make.py build 2026-05-05-my-article.md     只生成博客
  make.py build --all                        为所有文章生成博客
  make.py build --platform xiaohongshu,zhihu 2026-05-05-my-article.md
                                                只生成指定平台

  # 集合管理
  make.py collection list                      查看可用项目
  make.py collection build 01-openclaw         构建单个集合
  make.py collection build 04-工程那些事/01-电机控制   构建嵌套集合
  make.py collection build --all               构建所有集合

  # 发布与配置
  make.py publish                              发布到 GitHub Pages
  make.py status                               查看文章状态
  make.py config                               查看配置
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # new
    parser_new = subparsers.add_parser("new", help="创建新文章")
    parser_new.add_argument("title", help="文章标题")
    parser_new.add_argument("--category", help="目标集合目录 (如 01-openclaw, 04-工程那些事/01-电机控制)")
    parser_new.add_argument("--template", help="模板名称 (默认使用通用模板或集合专属模板)")

    # build
    parser_build = subparsers.add_parser("build", help="构建文章")
    parser_build.add_argument("article", nargs="?", help="文章文件名")
    parser_build.add_argument("--all", action="store_true", help="处理所有文章")
    parser_build.add_argument("--incremental", action="store_true", help="只处理变更的文章")
    parser_build.add_argument("--force", action="store_true", help="强制重新构建")
    parser_build.add_argument(
        "--platform",
        help="指定平台，逗号分隔 (如 xiaohongshu,zhihu)",
    )

    # publish
    parser_publish = subparsers.add_parser("publish", help="发布到 GitHub Pages")
    parser_publish.add_argument("-m", "--message", help="自定义 commit 消息")
    parser_publish.add_argument("--update-submodule", action="store_true", help="同步更新父仓库的子模块引用并推送")

    # collection
    parser_collection = subparsers.add_parser("collection", help="管理项目集合")
    collection_subs = parser_collection.add_subparsers(dest="collection_command")

    parser_col_list = collection_subs.add_parser("list", help="列出可用项目")
    parser_col_build = collection_subs.add_parser("build", help="构建集合")
    parser_col_build.add_argument("project", nargs="?", help="项目标识 (如 01-openclaw, 04-工程那些事/01-电机控制)")
    parser_col_build.add_argument("--all", action="store_true", help="构建所有项目")
    parser_col_build.add_argument("--dry-run", action="store_true", help="预览模式，不实际写入文件")
    parser_col_build.add_argument("--source", help="源子目录 (默认 blog)")
    parser_col_build.add_argument("--date", help="发布日期 YYYY-MM-DD (默认今天)")

    # validate
    parser_validate = subparsers.add_parser("validate", help="校验内容完整性")
    parser_validate.add_argument("--article", help="校验单篇文章")

    # stats
    parser_stats = subparsers.add_parser("stats", help="内容统计报表")
    parser_stats.add_argument("--json", action="store_true", help="JSON 格式输出")
    parser_stats.add_argument("--collection", help="过滤单个集合")

    # status
    subparsers.add_parser("status", help="查看文章状态")

    # config
    subparsers.add_parser("config", help="查看配置")

    # 注册 shell 补全 (需要 argcomplete: pip install argcomplete)
    if HAS_ARGCOMPLETE:
        # 动态补全：项目名、平台名
        def _complete_project_names(prefix, parsed_args, **kwargs):
            """补全 collection 命令的项目名"""
            projects = list_projects(KB_DIR, PAGES_DIR)
            return [info["display_path"] for _, info in sorted(projects.items(), key=lambda x: (x[1]["nn"], x[1]["display_path"]))]

        def _complete_platform_names(prefix, parsed_args, **kwargs):
            """补全 build 命令的平台名"""
            return [p.key for p in list_platforms()]

        def _complete_article_files(prefix, parsed_args, **kwargs):
            """补全 build 命令的文章文件名"""
            articles = find_articles(KB_DIR)
            return [f.name for f in articles]

        # 为相应参数设置补全函数
        for parser_obj in [parser_col_build]:
            for action in parser_obj._actions:
                if action.dest == "project":
                    action.completer = _complete_project_names
        for action in parser_build._actions:
            if action.dest == "platform":
                action.completer = _complete_platform_names
            if action.dest == "article":
                action.completer = _complete_article_files

        argcomplete.autocomplete(parser)

    args = parser.parse_args()

    if args.command == "new":
        cmd_new(args)
    elif args.command == "build":
        cmd_build(args)
    elif args.command == "publish":
        cmd_publish(args)
    elif args.command == "collection":
        cmd_collection(args)
    elif args.command == "validate":
        cmd_validate(args)
    elif args.command == "stats":
        cmd_stats(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "config":
        cmd_config(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
