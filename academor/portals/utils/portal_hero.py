"""Headline numbers for the student and customer dashboard heroes."""

from django.utils.translation import gettext as _


def _pct(value):
    return f'{round(value)}%' if value is not None else '—'


def student_hero_stats(data: dict, agenda: dict) -> list[dict]:
    quiz_average = data.get('quiz_average') or {}
    attendance = data.get('attendance_stats') or {}
    return [
        {'value': len(agenda.get('today_schedule') or []), 'label': _('Lessons today')},
        {'value': _pct(quiz_average.get('avg_score_pct')), 'label': _('Quiz average')},
        {'value': _pct(attendance.get('attendance_rate')), 'label': _('Attendance')},
    ]


def customer_hero_stats(sections: list[dict]) -> list[dict]:
    stats = [
        {'value': section['credits'], 'label': _('%(program)s credits') % {'program': section['label']}}
        for section in sections
    ]
    stats.append({
        'value': sum(section.get('completed_count', 0) for section in sections),
        'label': _('Completed mocks'),
    })
    return stats


def teacher_hero_stats(data: dict, agenda: dict, pending_reviews: int) -> list[dict]:
    groups = data.get('groups') or []
    return [
        {'value': len(agenda.get('today_schedule') or []), 'label': _('Lessons today')},
        {'value': sum(1 for group in groups if group.get('is_active', True)), 'label': _('Active groups')},
        {'value': pending_reviews, 'label': _('Awaiting review')},
    ]
