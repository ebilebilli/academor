"""Inline SVG icons + static copy for study-abroad advantage cards."""

from django.utils import translation
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

# Keys: Font Awesome 5 class without style prefix (e.g. fa-graduation-cap).
STUDY_ABROAD_ADVANTAGE_SVGS = {
    'fa-graduation-cap': (
        '<svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true" focusable="false">'
        '<path fill="currentColor" d="M12 3 1 9l4 2.18V17l7 4 7-4v-5.82L23 9 12 3zm0 2.27 6.99 3.81L12 12.9 5.01 9.08 12 5.27zM7 11.18l5 2.73 5-2.73v3.82L12 17.73 7 15v-3.82z"/>'
        '</svg>'
    ),
    'fa-briefcase': (
        '<svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true" focusable="false">'
        '<path fill="currentColor" d="M10 2h4a2 2 0 0 1 2 2h3a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h3a2 2 0 0 1 2-2zm4 2h-4v2h4V4zM5 8v12h14V8H5zm3 3h8v2H8v-2z"/>'
        '</svg>'
    ),
    'fa-comments': (
        '<svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true" focusable="false">'
        '<path fill="currentColor" d="M4 2h12a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H8.83L5 20.83V17H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2zm14 5h3a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2h-2.83L15 20.83V18h-2a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2z"/>'
        '</svg>'
    ),
    'fa-users': (
        '<svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true" focusable="false">'
        '<path fill="currentColor" d="M9 11a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7zm7.5 0a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM2 19.5C2 16.5 5.5 15 9 15s7 1.5 7 4.5V21H2v-1.5zM15.5 15.8c2.1.6 4.5 2.1 4.5 5.2V21h6v-1.5c0-2.8-3.4-4.4-6-4.7-.8.5-1.8.9-3 .9s-2.2-.4-3-.9c-.5.1-1 .2-1.5.4z"/>'
        '</svg>'
    ),
}

_DEFAULT_SVG = (
    '<svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true" focusable="false">'
    '<path fill="currentColor" d="M12 2l2.4 7.4H22l-6 4.6 2.3 7-6.3-4.6L5.7 21l2.3-7-6-4.6h7.6L12 2z"/>'
    '</svg>'
)

# Static advantages row (home + /abroad/). msgid values must match locale django.po entries.
STUDY_ABROAD_ADVANTAGE_STATIC_ITEMS = (
    {'icon': 'fa-graduation-cap', 'title_msgid': 'International Diploma'},
    {'icon': 'fa-briefcase', 'title_msgid': 'Career Opportunities'},
    {'icon': 'fa-comments', 'title_msgid': 'Language Skills'},
    {'icon': 'fa-users', 'title_msgid': 'Global Network'},
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


def build_static_study_abroad_advantages_block(lang='az'):
    """Return heading + four static advantage items for the given language."""
    with translation.override(lang):
        return {
            'title': _('Advantages of Studying Abroad'),
            'items': [
                {
                    'icon': row['icon'],
                    'icon_svg': resolve_study_abroad_advantage_icon(row['icon']),
                    'title': _(row['title_msgid']),
                }
                for row in STUDY_ABROAD_ADVANTAGE_STATIC_ITEMS
            ],
        }
