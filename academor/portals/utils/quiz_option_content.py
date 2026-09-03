import re
from html import unescape

from django.utils.html import strip_tags

_MEDIA_TAG_RE = re.compile(
    r'<(?:img|svg|video|audio|iframe|embed|object|source)\b',
    re.IGNORECASE,
)


def option_has_content(value):
    """True when an option has visible text or embedded media (e.g. SAT Math images)."""
    if value in (None, ''):
        return False
    raw = str(value)
    if _MEDIA_TAG_RE.search(raw):
        return True
    text = unescape(strip_tags(raw)).replace('\xa0', ' ').strip()
    return bool(text)
