"""Admin: visual monthly attendance overview per teacher (Attendance → Teachers' attendance).

Reuses the teacher portal's monthly register so the admin sees exactly what the teacher sees.
"""

from __future__ import annotations

import calendar
from datetime import date

from django.db.models import Count, Q
from django.db.models.functions import Coalesce

from portals.models import Attendance, TeacherProfile
from portals.utils.teacher_attendance_register import (
    build_teacher_attendance_register,
    month_key,
    shift_month,
)
from portals.utils.teacher_courses import teacher_groups_queryset

STATUSES = ('present', 'late', 'absent')


def _rate(present, late, absent):
    """Share of marked sessions the student came to (late counts as attended), or None."""
    total = present + late + absent
    if not total:
        return None
    return round((present + late) * 100 / total)


def _tone(rate):
    if rate is None:
        return 'none'
    if rate >= 85:
        return 'good'
    if rate >= 70:
        return 'warn'
    return 'bad'


def _month_bounds(year, month):
    return date(year, month, 1), date(year, month, calendar.monthrange(year, month)[1])


def teacher_month_summaries(year, month):
    """One row per teacher with this month's present / late / absent totals."""
    start, end = _month_bounds(year, month)
    counts = (
        Attendance.objects.filter(session_date__range=(start, end))
        .annotate(teacher_id=Coalesce('group__teacher_id', 'schedule__group__teacher_id'))
        .exclude(teacher_id=None)
        .values('teacher_id', 'status')
        .annotate(n=Count('id'))
    )
    by_teacher = {}
    for row in counts:
        by_teacher.setdefault(row['teacher_id'], dict.fromkeys(STATUSES, 0))[row['status']] = row['n']

    teachers = (
        TeacherProfile.objects.select_related('user')
        .annotate(
            group_count=Count('groups', filter=Q(groups__is_active=True), distinct=True),
            student_count=Count('groups__students', filter=Q(groups__is_active=True), distinct=True),
        )
        .order_by('user__username', 'id')
    )
    rows = []
    for teacher in teachers:
        c = by_teacher.get(teacher.pk, dict.fromkeys(STATUSES, 0))
        rate = _rate(c['present'], c['late'], c['absent'])
        rows.append({
            'id': teacher.pk,
            'name': teacher.full_name,
            'initials': (teacher.full_name[:2] or '?').upper(),
            'groups': teacher.group_count,
            'students': teacher.student_count,
            'marks': sum(c.values()),
            'rate': rate,
            'tone': _tone(rate),
            **c,
        })
    return rows


def teacher_month_detail(teacher, year, month):
    """KPIs, a per-day chart and one register grid per active group for the teacher."""
    groups = list(
        teacher_groups_queryset(teacher.pk, active_only=True, include_register_only=True)
        .order_by('is_register_only', 'name', 'id')
    )
    totals = dict.fromkeys(STATUSES, 0)
    per_day = {}
    grids = []
    days = []
    people = 0
    for group in groups:
        register = build_teacher_attendance_register(teacher, year=year, month=month, group=group)
        days = [d for d in register['days'] if d['in_month']]
        g_totals = dict.fromkeys(STATUSES, 0)
        rows = []
        for person in register['students']:
            cells = [
                {**c, 'is_weekend': date.fromisoformat(c['iso']).weekday() >= 5}
                for c in person['cells'] if c['iso']
            ]
            for cell in cells:
                if cell['status'] in totals:
                    per_day.setdefault(cell['iso'], dict.fromkeys(STATUSES, 0))[cell['status']] += 1
            p, l, a = person['present_count'], person['late_count'], person['absent_count']
            g_totals['present'] += p
            g_totals['late'] += l
            g_totals['absent'] += a
            rate = _rate(p, l, a)
            rows.append({**person, 'cells': cells, 'rate': rate, 'tone': _tone(rate)})
        for key in STATUSES:
            totals[key] += g_totals[key]
        people += len(rows)
        g_rate = _rate(g_totals['present'], g_totals['late'], g_totals['absent'])
        grids.append({
            'id': group.pk,
            'name': group.name,
            'course_label': register['group']['course_label'] if register['group'] else '',
            'is_register_only': group.is_register_only,
            'rows': rows,
            'rate': g_rate,
            'tone': _tone(g_rate),
            **g_totals,
        })

    if not days:
        start, end = _month_bounds(year, month)
        days = [{'n': n, 'iso': date(year, month, n).isoformat(), 'is_weekend': date(year, month, n).weekday() >= 5,
                 'weekday_short': '', 'is_today': False} for n in range(1, end.day + 1)]

    peak = max((sum(v.values()) for v in per_day.values()), default=0)
    chart = []
    for d in days:
        c = per_day.get(d['iso'], dict.fromkeys(STATUSES, 0))
        total = sum(c.values())
        chart.append({
            **d,
            'total': total,
            # bar heights as % of the busiest day, one segment per status
            'h_present': round(c['present'] * 100 / peak) if peak else 0,
            'h_late': round(c['late'] * 100 / peak) if peak else 0,
            'h_absent': round(c['absent'] * 100 / peak) if peak else 0,
            **c,
        })

    rate = _rate(totals['present'], totals['late'], totals['absent'])
    return {
        'groups': grids,
        'days': days,
        'chart': chart,
        'rate': rate,
        'tone': _tone(rate),
        'lesson_days': sum(1 for d in chart if d['total']),
        'people': people,
        **totals,
    }


def build_teacher_attendance_overview(*, teacher_id=None, year, month):
    prev_y, prev_m = shift_month(year, month, -1)
    next_y, next_m = shift_month(year, month, 1)
    teachers = teacher_month_summaries(year, month)
    selected = None
    if teacher_id:
        selected = TeacherProfile.objects.select_related('user').filter(pk=teacher_id).first()
    if selected is None and teachers:
        # default to the busiest teacher this month, so the page never opens empty
        best = max(teachers, key=lambda t: (t['marks'], t['groups']))
        selected = TeacherProfile.objects.select_related('user').filter(pk=best['id']).first()
    return {
        'year': year,
        'month': month,
        'month_date': date(year, month, 1),
        'month_key': month_key(year, month),
        'prev_month': month_key(prev_y, prev_m),
        'next_month': month_key(next_y, next_m),
        'teachers': teachers,
        'teacher': selected,
        'detail': teacher_month_detail(selected, year, month) if selected else None,
    }
