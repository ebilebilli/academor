"""Inline SVG icons for study-abroad advantage cards (no Font Awesome CDN dependency)."""

from django.utils.safestring import mark_safe

# Keys: Font Awesome 5 class without style prefix (e.g. fa-certificate).
STUDY_ABROAD_ADVANTAGE_SVGS = {
    'fa-certificate': (
        '<svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true" focusable="false">'
        '<path fill="currentColor" d="M14 2H6a2 2 0 0 0-2 2v16l4-2 4 2 4-2 4 2V8l-6-6zm-1 2.5L18.5 10H15V4.5zM8 12h8v1.5H8V12zm0 3h6v1.5H8V15z"/>'
        '</svg>'
    ),
    'fa-briefcase': (
        '<svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true" focusable="false">'
        '<path fill="currentColor" d="M10 2h4a2 2 0 0 1 2 2h3a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h3a2 2 0 0 1 2-2zm4 2h-4v2h4V4zM5 8v12h14V8H5zm3 3h8v2H8v-2z"/>'
        '</svg>'
    ),
    'fa-language': (
        '<svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true" focusable="false">'
        '<path fill="currentColor" d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm-1 4.1A12.9 12.9 0 0 0 5.1 11H3.1a8 8 0 0 1 7.9-4.9zM3.1 13h2a12.9 12.9 0 0 0 5.9 4.9A8 8 0 0 1 3.1 13zm9.9 4.9A12.9 12.9 0 0 0 18.9 13h2a8 8 0 0 1-7.9 4.9zM20.9 11h-2a12.9 12.9 0 0 0-5.9-4.9A8 8 0 0 1 20.9 11zM12 6.5c1.4 1.6 2.3 3.4 2.6 5.5h-5.2c.3-2.1 1.2-3.9 2.6-5.5z"/>'
        '</svg>'
    ),
    'fa-globe-americas': (
        '<svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true" focusable="false">'
        '<path fill="currentColor" d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm7.9 9H16.8a15.5 15.5 0 0 0-1.2-4.7A8 8 0 0 1 19.9 11zM12 4c.9 1.2 1.6 2.7 2 4.5H10c.4-1.8 1.1-3.3 2-4.5zM8.4 6.3A15.5 15.5 0 0 0 7.2 11H4.1a8 8 0 0 1 4.3-4.7zM4.1 13h3.1c.3 1.7.9 3.2 1.7 4.5A8 8 0 0 1 4.1 13zm7.9 6.5c-.9-1.2-1.6-2.7-2-4.5h4c-.4 1.8-1.1 3.3-2 4.5zm3.6-4.5a15.5 15.5 0 0 0 1.2 4.5 8 8 0 0 1-4.3-4.5h3.1zm1.5 0H19.9a8 8 0 0 1-4.3 4.5c.8-1.3 1.4-2.8 1.7-4.5z"/>'
        '</svg>'
    ),
    'fa-hand-holding-usd': (
        '<svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true" focusable="false">'
        '<path fill="currentColor" d="M11.8 10.9c-2.3-.6-3-1.2-3-2.2 0-1.1 1-2 2.6-2 1.5 0 2.4.7 2.7 1.8l2.1-.6c-.5-1.8-2-3.2-4.8-3.2-2.9 0-4.9 1.7-4.9 4.1 0 2.4 1.6 3.5 4.3 4.1 2.5.6 3.2 1.4 3.2 2.5 0 .9-.8 1.9-2.7 1.9-2 0-3-.9-3.3-2.2l-2.2.5c.4 2.2 2.1 3.7 5.4 3.7 3.2 0 5.3-1.7 5.3-4.3.1-2.5-1.5-3.6-4.4-4.1zM4 11V4h3V2h10v2h3v7h-2V6H6v5H4zm14 9H6v-2h12v2z"/>'
        '</svg>'
    ),
    'fa-passport': (
        '<svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true" focusable="false">'
        '<path fill="currentColor" d="M4 4h16a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2zm2 4v2h2V8H6zm0 4v2h6v-2H6zm8-4v6h6V8h-6z"/>'
        '</svg>'
    ),
}

_DEFAULT_SVG = (
    '<svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true" focusable="false">'
    '<path fill="currentColor" d="M12 2l2.4 7.4H22l-6 4.6 2.3 7-6.3-4.6L5.7 21l2.3-7-6-4.6h7.6L12 2z"/>'
    '</svg>'
)


def normalize_study_abroad_advantage_icon(icon: str = '') -> str:
    """Return a Font Awesome 5 class key (fa-*) for lookup."""
    value = (icon or 'fa-star').strip()
    if value.startswith('fa '):
        value = value.replace('fa ', 'fa-', 1).replace(' ', '')
    for prefix in ('fas ', 'far ', 'fab ', 'fal ', 'fad '):
        if value.startswith(prefix):
            parts = value.split()
            value = next((p for p in parts if p.startswith('fa-')), 'fa-star')
            break
    if value.startswith('fa-'):
        return value
    if value.startswith('fa'):
        return value.replace('fa', 'fa-', 1) if len(value) > 2 else 'fa-star'
    return f'fa-{value}' if value else 'fa-star'


def resolve_study_abroad_advantage_icon(icon: str = '') -> str:
    """Safe inline SVG markup for templates (mark_safe in serializer)."""
    key = normalize_study_abroad_advantage_icon(icon)
    return mark_safe(STUDY_ABROAD_ADVANTAGE_SVGS.get(key, _DEFAULT_SVG))
