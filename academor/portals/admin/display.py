from django.utils.html import format_html


ROLE_STYLES = {
    'teacher': ('teacher', 'T'),
    'student': ('student', 'S'),
    'parent': ('parent', 'P'),
    'customer': ('customer', 'C'),
}

COURSE_PILL_STYLES = {
    'ielts': 'ielts',
    'gmat': 'gmat',
    'gre': 'gre',
    'sat': 'sat',
    'speaking': 'speaking',
    'general_english': 'english',
    'study_abroad': 'abroad',
    'yos': 'yos',
    'ales': 'ales',
    'other': 'default',
}


def _initials(display_name: str) -> str:
    text = (display_name or '').strip()
    if not text:
        return ''
    return text[:2].upper()


def portal_person_cell(display_name, subtitle='', role='student', photo_url=None):
    role_class, fallback = ROLE_STYLES.get(role, ('student', '?'))
    initials = _initials(display_name) or fallback
    name = (display_name or '').strip() or '—'
    if photo_url:
        avatar_html = format_html(
            '<img src="{}" alt="" class="portal-person__photo">',
            photo_url,
        )
    else:
        avatar_html = format_html(
            '<span class="portal-person__avatar portal-person__avatar--{}">{}</span>',
            role_class,
            initials,
        )
    return format_html(
        '<div class="portal-person">'
        '{}'
        '<span class="portal-person__meta">'
        '<span class="portal-person__name">{}</span>'
        '{}'
        '</span>'
        '</div>',
        avatar_html,
        name,
        format_html(
            '<span class="portal-person__sub">{}</span>',
            subtitle,
        ) if subtitle else '',
    )


def portal_role_badge(role_label: str, role_key: str = 'student'):
    role_class, _ = ROLE_STYLES.get(role_key, ('student', ''))
    return format_html(
        '<span class="portal-role portal-role--{}">{}</span>',
        role_class,
        role_label,
    )


def portal_course_pill(value: str, label: str):
    css = COURSE_PILL_STYLES.get(value, 'default')
    return format_html(
        '<span class="portal-pill portal-pill--{}">{}</span>',
        css,
        label,
    )


def portal_capacity_bar(current: int, maximum: int):
    maximum = max(maximum, 1)
    current = min(max(current, 0), maximum)
    percent = int(round((current / maximum) * 100))
    tone = 'ok'
    if percent >= 90:
        tone = 'full'
    elif percent >= 70:
        tone = 'warn'
    return format_html(
        '<div class="portal-capacity portal-capacity--{}">'
        '<div class="portal-capacity__track">'
        '<div class="portal-capacity__fill" style="width:{}%"></div>'
        '</div>'
        '<span class="portal-capacity__text">{}/{}</span>'
        '</div>',
        tone,
        percent,
        current,
        maximum,
    )


def portal_day_badge(label: str):
    return format_html(
        '<span class="portal-day">{}</span>',
        label,
    )


def portal_status_dot(is_active: bool):
    if is_active:
        return format_html(
            '<span class="portal-dot portal-dot--on" title="Active">Active</span>',
        )
    return format_html(
        '<span class="portal-dot portal-dot--off" title="Inactive">Inactive</span>',
    )


def portal_count_badge(count: int, label: str, tone: str = 'blue'):
    return format_html(
        '<span class="portal-count portal-count--{}">{} <em>{}</em></span>',
        tone,
        count,
        label,
    )


def portal_score_chip(value, max_value):
    try:
        pct = (float(value) / float(max_value)) * 100 if max_value else 0
    except (TypeError, ValueError, ZeroDivisionError):
        pct = 0
    tone = 'high' if pct >= 80 else 'mid' if pct >= 50 else 'low'
    return format_html(
        '<span class="portal-score portal-score--{}">{}/{}</span>',
        tone,
        value,
        max_value,
    )


def portal_admin_change_link(obj, label=None):
    """Link to a model's Django admin change page (name instead of raw id)."""
    if not obj or not getattr(obj, 'pk', None):
        return '—'
    from django.urls import reverse

    opts = obj._meta
    url = reverse(f'admin:{opts.app_label}_{opts.model_name}_change', args=[obj.pk])
    text = (label if label is not None else str(obj)).strip() or '—'
    return format_html('<a href="{}" class="portal-admin-link">{}</a>', url, text)
