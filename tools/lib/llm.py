"""LLM API 调用封装 —— 支持 Anthropic 兼容和 OpenAI 兼容两种风格

环境变量:
  LLM_PROVIDER   = anthropic | openai        (默认: anthropic)
  LLM_API_KEY    = sk-...                    (API key)
  LLM_BASE_URL   = https://...               (可选，覆盖默认端点)
  LLM_MODEL      = model-name                (可选，覆盖默认模型)

Anthropic 风格默认:  base_url=SDK默认, model=claude-sonnet-4-20250514
OpenAI 风格默认:    base_url=https://api.openai.com/v1, model=gpt-4o
"""

import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    from anthropic import Anthropic
    _has_anthropic = True
except ImportError:
    _has_anthropic = False

try:
    from openai import OpenAI
    _has_openai = True
except ImportError:
    _has_openai = False

DEFAULTS = {
    "anthropic": {"model": "claude-sonnet-4-20250514", "base_url": None},
    "openai": {"model": "gpt-4o", "base_url": "https://api.openai.com/v1"},
}


# deepseek 等其他 Anthropic 兼容端点归一化为 anthropic 风格
_ANTHROPIC_STYLE = {"anthropic", "deepseek"}


def _provider_style() -> str:
    """返回 API 风格: 'anthropic' 或 'openai'"""
    p = os.environ.get("LLM_PROVIDER", "anthropic").lower()
    return "anthropic" if p in _ANTHROPIC_STYLE else "openai"


def _provider() -> str:
    """返回原始提供商名 (用于显示)"""
    return os.environ.get("LLM_PROVIDER", "anthropic").lower()


def _api_key() -> str | None:
    return os.environ.get("LLM_API_KEY")


def _model() -> str:
    style = _provider_style()
    # deepseek 默认模型
    if style == "anthropic" and _provider() == "deepseek":
        return os.environ.get("LLM_MODEL", "deepseek-v4-pro")
    return os.environ.get("LLM_MODEL", DEFAULTS[style]["model"])


def _base_url() -> str | None:
    style = _provider_style()
    # deepseek 默认端点
    if style == "anthropic" and _provider() == "deepseek":
        return os.environ.get("LLM_BASE_URL", "https://api.deepseek.com/anthropic")
    return os.environ.get("LLM_BASE_URL") or DEFAULTS[style]["base_url"]


def _load_prompt(prompt_name: str, prompts_dir: Path) -> str | None:
    prompt_file = prompts_dir / prompt_name
    if not prompt_file.exists():
        logger.error(f"Prompt 文件不存在: {prompt_file}")
        return None
    return prompt_file.read_text(encoding="utf-8")


def adapt_for_platform(
    title: str,
    body: str,
    tags: list[str],
    keywords: list[str],
    summary: str,
    prompt_file: str,
    prompts_dir: Path,
) -> str | None:
    """使用 LLM 将源文章适配为目标平台内容"""
    system_prompt = _load_prompt(prompt_file, prompts_dir)
    if not system_prompt:
        return None

    api_key = _api_key()
    if not api_key:
        logger.error("LLM_API_KEY 未设置")
        return None

    style = _provider_style()
    model = _model()
    base_url = _base_url()

    user_prompt = f"""## 原文标题
{title}

## 原文标签
{", ".join(tags)}

## 原文关键词
{", ".join(keywords)}

## 原文摘要
{summary}

## 原文正文
{body}"""

    long_platforms = {"zhihu.md", "wechat.md", "toutiao.md", "baijiahao.md"}
    max_tokens = 8192 if prompt_file in long_platforms else 4096

    if style == "openai":
        return _call_openai(api_key, model, base_url, system_prompt, user_prompt, max_tokens)
    else:
        return _call_anthropic(api_key, model, base_url, system_prompt, user_prompt, max_tokens)


def _call_anthropic(
    api_key: str,
    model: str,
    base_url: str | None,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int,
) -> str | None:
    if not _has_anthropic:
        logger.error("anthropic SDK 未安装。运行: pip install anthropic")
        return None

    kwargs = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url

    try:
        client = Anthropic(**kwargs)
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        for block in response.content:
            if block.type == "text":
                return block.text
        logger.error("LLM 响应中没有 text block")
        return None
    except Exception as e:
        logger.error(f"LLM 调用失败 ({model}): {e}")
        return None


def _call_openai(
    api_key: str,
    model: str,
    base_url: str | None,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int,
) -> str | None:
    if not _has_openai:
        logger.error("openai SDK 未安装。运行: pip install openai")
        return None

    kwargs = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url

    try:
        client = OpenAI(**kwargs)
        response = client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"LLM 调用失败 ({model}): {e}")
        return None
