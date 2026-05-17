"""Plain-text excerpts for meta descriptions (strip HTML / normalize whitespace)."""

from __future__ import annotations

import html as html_stdlib
import re

from django.utils.html import strip_tags

_WS = re.compile(r"\s+")
# Block-ish tags: insert boundary space before strip_tags so words do not concatenate.
_BLOCK_BOUNDARY = re.compile(
    r"</(?:p|div|h[1-6]|li|tr|td|th|blockquote|section|article|header|footer|pre)\s*>",
    re.I,
)
_BR = re.compile(r"<br\s*/?>", re.I)


def richtext_plain_text(html_or_plain: str | None) -> str:
    """CKEditor / rich HTML → single-line plain text suitable for cards and excerpts."""
    if not html_or_plain:
        return ""
    raw = str(html_or_plain).strip()
    if not raw:
        return ""
    text = _BR.sub(" ", raw)
    text = _BLOCK_BOUNDARY.sub(" ", text)
    plain = strip_tags(text)
    plain = html_stdlib.unescape(plain)
    plain = plain.replace("\xa0", " ")
    plain = _WS.sub(" ", plain).strip()
    return plain


def truncate_words_plain(plain: str, max_words: int, *, ellipsis: str = "…") -> str:
    if not plain or max_words < 1:
        return ""
    words = plain.split()
    if len(words) <= max_words:
        return plain
    return " ".join(words[:max_words]) + ellipsis


def blog_intro_plain(html_or_plain: str | None, *, max_words: int = 42) -> str:
    """First paragraph-worth of plain text for article lead / dek under the title."""
    return truncate_words_plain(richtext_plain_text(html_or_plain), max_words)


def meta_plain_excerpt(html_or_plain: str | None, *, max_len: int = 158, ellipsis: str = "…") -> str:
    plain = richtext_plain_text(html_or_plain)
    if not plain:
        return ""
    if len(plain) <= max_len:
        return plain
    trimmed = plain[: max_len - len(ellipsis)].rstrip()
    return trimmed + ellipsis if trimmed else plain[:max_len]


def topic_overview_preview(overview_paragraphs: tuple[str, ...], *, max_len: int = 158) -> str:
    if not overview_paragraphs:
        return ""
    return meta_plain_excerpt("\n".join(overview_paragraphs), max_len=max_len)
