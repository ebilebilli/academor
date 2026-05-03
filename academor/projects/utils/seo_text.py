"""Plain-text excerpts for meta descriptions (strip HTML / normalize whitespace)."""

from __future__ import annotations

import re

from django.utils.html import strip_tags

_WS = re.compile(r"\s+")


def meta_plain_excerpt(html_or_plain: str | None, *, max_len: int = 158, ellipsis: str = "…") -> str:
    if not html_or_plain:
        return ""
    plain = strip_tags(str(html_or_plain))
    plain = _WS.sub(" ", plain).strip()
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
