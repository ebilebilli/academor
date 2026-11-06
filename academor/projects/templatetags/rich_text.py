"""Tidy rich text written in the admin editor (CKEditor) before it is shown on the site.

Text pasted from Word / Google Docs brings empty paragraphs, runs of <br>, non-breaking spaces
and inline font sizes, line heights, margins and justified alignment. On the site that shows up
as big gaps between lines and words. `tidy_rich_text` removes that noise and keeps the content:
headings, bold/italic, lists, links, images and colours stay as they are.
"""

import re

from django import template
from django.utils.safestring import mark_safe

register = template.Library()

_BLANK = r'(?:\s|&nbsp;|&#160;| |<br\s*/?>)*'
_EMPTY_BLOCK = re.compile(rf'<(p|div|h[1-6])(?:\s[^>]*)?>{_BLANK}(?:<(span|strong|b|em|i)(?:\s[^>]*)?>{_BLANK}</\2>{_BLANK})*</\1>', re.I)
_BR_RUN = re.compile(r'(?:<br\s*/?>\s*){2,}', re.I)
_BR_EDGE = re.compile(rf'(<(?:p|div|li|h[1-6])(?:\s[^>]*)?>){_BLANK}|{_BLANK}(</(?:p|div|li|h[1-6])>)', re.I)
_NBSP = re.compile(r'(?:&nbsp;|&#160;| )+')
_STYLE = re.compile(r'\sstyle\s*=\s*("([^"]*)"|\'([^\']*)\')', re.I)
# layout properties that fight the site's typography; colours and weights are kept
_DROP = re.compile(
    r'^\s*(font-size|font-family|line-height|margin(-[a-z]+)?|padding(-[a-z]+)?|text-indent|'
    r'text-align|white-space|letter-spacing|word-spacing|height|min-height|width|max-width)\s*:',
    re.I,
)


def _clean_style(match):
    css = match.group(2) if match.group(2) is not None else match.group(3)
    kept = [d.strip() for d in css.split(';') if d.strip() and not _DROP.match(d)]
    return f' style="{"; ".join(kept)}"' if kept else ''


def _edge(match):
    return match.group(1) or match.group(2) or ''


@register.filter(is_safe=True)
def tidy_rich_text(html):
    if not html:
        return ''
    text = str(html)
    text = _STYLE.sub(_clean_style, text)
    text = _NBSP.sub(' ', text)
    text = _BR_RUN.sub('<br>', text)
    text = _BR_EDGE.sub(_edge, text)
    previous = None
    while previous != text:  # nested empty wrappers
        previous = text
        text = _EMPTY_BLOCK.sub('', text)
    return mark_safe(text.strip())
