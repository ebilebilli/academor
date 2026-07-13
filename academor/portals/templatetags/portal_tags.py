from datetime import date, datetime

from django import template
from django.utils import timezone
from django.utils.translation import get_language, gettext
import re

register = template.Library()

_PORTAL_WEEKDAY_NAMES = {
    'az': [
        'Bazar ertəsi', 'Çərşənbə axşamı', 'Çərşənbə', 'Cümə axşamı',
        'Cümə', 'Şənbə', 'Bazar',
    ],
    'en': [
        'Monday', 'Tuesday', 'Wednesday', 'Thursday',
        'Friday', 'Saturday', 'Sunday',
    ],
    'ru': [
        'понедельник', 'вторник', 'среда', 'четверг',
        'пятница', 'суббота', 'воскресенье',
    ],
}

_PORTAL_MONTH_NAMES = {
    'az': [
        'Yanvar', 'Fevral', 'Mart', 'Aprel', 'May', 'İyun', 'İyul',
        'Avqust', 'Sentyabr', 'Oktyabr', 'Noyabr', 'Dekabr',
    ],
    'en': [
        'January', 'February', 'March', 'April', 'May', 'June', 'July',
        'August', 'September', 'October', 'November', 'December',
    ],
    'ru': [
        'января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля',
        'августа', 'сентября', 'октября', 'ноября', 'декабря',
    ],
}


def _portal_lang_code():
    lang = (get_language() or 'az').lower().split('-')[0]
    return lang if lang in _PORTAL_MONTH_NAMES else 'az'


def _coerce_portal_date(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return timezone.localtime(value).date() if timezone.is_aware(value) else value.date()
    if isinstance(value, date):
        return value
    return None


def format_portal_calendar_day(value, *, include_year=False):
    day_value = _coerce_portal_date(value)
    if not day_value:
        return '—'
    month = _PORTAL_MONTH_NAMES[_portal_lang_code()][day_value.month - 1]
    if include_year:
        return f'{day_value.day} {month} {day_value.year}'
    return f'{day_value.day} {month}'

_YOUTUBE_ID_RE = re.compile(
    r'(?:youtube\.com/(?:watch\?v=|embed/|shorts/)|youtu\.be/)([\w-]{11})',
)


@register.filter
def prompt_type_label(value):
    code = (value or '').strip().lower()
    labels = {
        'text': gettext('Text'),
        'image': gettext('Image'),
        'video': gettext('Video'),
        'audio': gettext('Audio'),
    }
    return labels.get(code, code or '')


@register.filter
def portal_datetime(value):
    if not value:
        return '—'
    if isinstance(value, datetime):
        dt = timezone.localtime(value) if timezone.is_aware(value) else value
        date_part = format_portal_calendar_day(dt.date(), include_year=True)
        return f'{date_part} {dt.strftime("%H:%M")}'
    return format_portal_calendar_day(value, include_year=True)


@register.filter
def portal_date(value):
    if not value:
        return '—'
    dt = timezone.localtime(value) if timezone.is_aware(value) else value
    return dt.strftime('%d.%m.%Y')


@register.filter
def portal_date_long(value):
    return format_portal_calendar_day(value, include_year=True)


@register.filter
def portal_date_long_weekday(value):
    day_value = _coerce_portal_date(value)
    if not day_value:
        return '—'
    weekday = _PORTAL_WEEKDAY_NAMES[_portal_lang_code()][day_value.weekday()]
    return f'{weekday}, {format_portal_calendar_day(day_value, include_year=True)}'


@register.filter
def format_duration_sec(value):
    try:
        seconds = max(0, int(value or 0))
    except (TypeError, ValueError):
        return '—'
    minutes, secs = divmod(seconds, 60)
    if minutes:
        return f'{minutes}m {secs}s'
    return f'{secs}s'


@register.filter
def format_duration_clock(value):
    """Zero-padded MM:SS for timers and prominent duration displays."""
    try:
        seconds = max(0, int(value or 0))
    except (TypeError, ValueError):
        return '—'
    minutes, secs = divmod(seconds, 60)
    return f'{minutes:02d}:{secs:02d}'


@register.filter
def duration_minutes_part(value):
    try:
        seconds = max(0, int(value or 0))
    except (TypeError, ValueError):
        return 0
    return seconds // 60


@register.filter
def duration_seconds_part(value):
    try:
        seconds = max(0, int(value or 0))
    except (TypeError, ValueError):
        return 0
    return seconds % 60


@register.simple_tag
def portal_week_label(week_start, week_end):
    start = format_portal_calendar_day(week_start)
    end = format_portal_calendar_day(week_end, include_year=True)
    return f'{start} – {end}'


def _portal_today_parts():
    today = timezone.localdate()
    lang = _portal_lang_code()
    return {
        'weekday': _PORTAL_WEEKDAY_NAMES[lang][today.weekday()],
        'day': today.day,
        'month': _PORTAL_MONTH_NAMES[lang][today.month - 1],
        'year': today.year,
    }


@register.simple_tag
def portal_today_long():
    """Localized long date for dashboard headers, e.g. «Cümə, 4 İyul 2026»."""
    parts = _portal_today_parts()
    return f'{parts["weekday"]}, {parts["day"]} {parts["month"]} {parts["year"]}'


@register.simple_tag
def portal_today_weekday():
    return _portal_today_parts()['weekday']


@register.simple_tag
def portal_today_day():
    return _portal_today_parts()['day']


@register.simple_tag
def portal_today_month():
    return _portal_today_parts()['month']


@register.simple_tag
def portal_today_year():
    return _portal_today_parts()['year']


@register.simple_tag
def portal_today_month_year():
    parts = _portal_today_parts()
    return f'{parts["month"]} {parts["year"]}'


@register.simple_tag
def duration_compare_meta(duration_sec, avg_sec, max_sec):
    """Return CSS class + short label comparing one attempt to class averages."""
    try:
        duration = max(0, int(duration_sec or 0))
        average = max(0, int(avg_sec or 0))
        peak = max(0, int(max_sec or 0))
    except (TypeError, ValueError):
        return {'css': '', 'label': ''}
    if duration <= 0:
        return {'css': '', 'label': ''}
    if peak and duration >= peak:
        return {'css': 'is-peak', 'label': gettext('Longest attempt')}
    if average and duration > average * 1.15:
        return {'css': 'is-slow', 'label': gettext('Above average')}
    if average and duration < average * 0.85:
        return {'css': 'is-fast', 'label': gettext('Below average')}
    return {'css': '', 'label': gettext('Typical pace')}


@register.filter
def css_num(value):
    """Locale-independent number for CSS custom properties (e.g. --score-pct)."""
    if value is None:
        return '0'
    try:
        num = float(value)
    except (TypeError, ValueError):
        return '0'
    text = f'{num:.10f}'.rstrip('0').rstrip('.')
    return text or '0'


@register.filter
def performance_tier_label(tier):
    labels = {
        'excellent': gettext('Excellent'),
        'good': gettext('Good'),
        'fair': gettext('Average'),
        'low': gettext('Weak'),
    }
    return labels.get((tier or '').strip().lower(), '')


@register.filter
def format_quiz_score(value):
    if value is None:
        return '—'
    try:
        num = float(value)
    except (TypeError, ValueError):
        return value
    if num == int(num):
        return str(int(num))
    text = f'{num:.2f}'.rstrip('0').rstrip('.')
    return text or '0'


@register.filter
def score_percent(value, max_value):
    try:
        score = float(value)
        maximum = float(max_value)
    except (TypeError, ValueError):
        return 0
    if maximum <= 0:
        return 0
    return min(100, max(0, round(100 * score / maximum)))


@register.filter
def duration_bar_percent(value, max_value):
    try:
        duration = max(0, int(value or 0))
        maximum = max(0, int(max_value or 0))
    except (TypeError, ValueError):
        return 0
    if maximum <= 0:
        return 0 if duration <= 0 else 100
    return min(100, max(0, round(100 * duration / maximum)))


@register.filter
def quiz_option_letter(index):
    """Map 0 → a, 1 → b, … for quiz answer keys."""
    try:
        value = int(index)
    except (TypeError, ValueError):
        return ''
    if value < 0 or value > 25:
        return ''
    return chr(97 + value)


@register.filter
def youtube_embed_url(value):
    if not value:
        return ''
    match = _YOUTUBE_ID_RE.search(str(value))
    if not match:
        return ''
    return f'https://www.youtube.com/embed/{match.group(1)}'


@register.inclusion_tag('portals/includes/page_heading.html', takes_context=False)
def portal_page_heading(
    icon='bi-speedometer2',
    eyebrow='',
    title='',
    subtitle='',
    raw_title='',
    raw_subtitle='',
    actions='',
):
    return {
        'icon': icon,
        'eyebrow': gettext(eyebrow) if eyebrow else '',
        'title': raw_title or (gettext(title) if title else ''),
        'subtitle': raw_subtitle or (gettext(subtitle) if subtitle else ''),
        'actions': actions,
    }
