"""Teacher weekly schedule calendar helpers."""

from datetime import date, datetime, timedelta

from django.urls import reverse
from django.utils import timezone

from portals.models import Schedule
from portals.utils.teacher_courses import teacher_groups_queryset


def parse_week_start(raw_value):
    if raw_value:
        try:
            parsed = date.fromisoformat(str(raw_value).strip())
            return parsed - timedelta(days=parsed.weekday())
        except ValueError:
            pass
    today = timezone.localdate()
    return today - timedelta(days=today.weekday())


def date_for_weekday(week_start, weekday):
    return week_start + timedelta(days=int(weekday))


def schedule_visible_on_date(schedule, session_date):
    """True when the concrete session date is on or after the slot's active-from date."""
    effective_from = getattr(schedule, 'effective_from', None)
    if not effective_from:
        return True
    return session_date >= effective_from


def active_schedules_for_day(schedules, weekday, day_date):
    """Return one schedule per group/time — latest effective_from wins."""
    best_by_slot = {}
    for schedule in schedules:
        if schedule.weekday != weekday:
            continue
        if not schedule_visible_on_date(schedule, day_date):
            continue
        key = (schedule.group_id, schedule.start_time)
        current = best_by_slot.get(key)
        if current is None or schedule.effective_from > current.effective_from:
            best_by_slot[key] = schedule
    return sorted(
        best_by_slot.values(),
        key=lambda row: (row.start_time, row.group_id, row.pk),
    )


def common_group_ids_for_students(student_ids, teacher_id):
    """Group IDs (teacher-owned) that contain all given students."""
    if not student_ids:
        return None
    from portals.models import StudyGroup

    student_set = set(student_ids)
    common = []
    groups = (
        StudyGroup.objects.filter(
            teacher_id=teacher_id,
            is_active=True,
            students__pk__in=student_ids,
        )
        .prefetch_related('students')
        .distinct()
    )
    for group in groups:
        member_ids = {student.pk for student in group.students.all()}
        if student_set.issubset(member_ids):
            common.append(group.pk)
    return common


def build_teacher_week_calendar(
    teacher_id,
    week_start=None,
    *,
    group_ids=None,
    student_ids=None,
    session_url_name='portals:teacher-attendance-session',
):
    week_start = week_start or parse_week_start(None)
    week_end = week_start + timedelta(days=6)
    today = timezone.localdate()

    if student_ids:
        group_ids = common_group_ids_for_students(student_ids, teacher_id)
        if not group_ids:
            group_ids = []

    schedules_qs = Schedule.objects.filter(
        group__in=teacher_groups_queryset(teacher_id, active_only=True),
    ).select_related('group')

    if group_ids is not None:
        if group_ids:
            schedules_qs = schedules_qs.filter(group_id__in=group_ids)
        else:
            schedules_qs = schedules_qs.none()

    schedules = schedules_qs.order_by('weekday', 'start_time', 'id')

    student_query = ''
    if student_ids:
        student_query = '&students=' + ','.join(str(sid) for sid in student_ids)

    weekday_labels = dict(Schedule.Weekday.choices)
    days = []

    for weekday in range(7):
        day_date = week_start + timedelta(days=weekday)
        sessions = []
        for schedule in active_schedules_for_day(schedules, weekday, day_date):
            sessions.append(
                {
                    'schedule_id': schedule.pk,
                    'group_id': schedule.group_id,
                    'group_name': schedule.group.name,
                    'start_time': schedule.start_time,
                    'duration_min': schedule.duration_min,
                    'room_or_link': schedule.room_or_link,
                    'session_date': day_date,
                    'session_date_iso': day_date.isoformat(),
                    'mark_url': (
                        f'{reverse(session_url_name)}'
                        f'?schedule={schedule.pk}&date={day_date.isoformat()}{student_query}'
                    ),
                },
            )
        days.append(
            {
                'weekday': weekday,
                'label': weekday_labels.get(weekday, str(weekday)),
                'date': day_date,
                'date_label': day_date.strftime('%d.%m'),
                'is_today': day_date == today,
                'is_weekend': weekday >= 5,
                'sessions': sessions,
            },
        )

    return {
        'week_start': week_start,
        'week_end': week_end,
        'prev_week': (week_start - timedelta(days=7)).isoformat(),
        'next_week': (week_start + timedelta(days=7)).isoformat(),
        'days': days,
        'has_sessions': any(day['sessions'] for day in days),
    }


def build_student_week_calendar(student_id, week_start=None):
    from portals.utils.queries import get_student_group_ids

    week_start = week_start or parse_week_start(None)
    week_end = week_start + timedelta(days=6)
    today = timezone.localdate()
    group_ids = get_student_group_ids(student_id)

    schedules = (
        Schedule.objects.filter(group_id__in=group_ids)
        .select_related('group')
        .prefetch_related('group__courses')
        .order_by('weekday', 'start_time', 'id')
    )

    weekday_labels = dict(Schedule.Weekday.choices)
    days = []

    for weekday in range(7):
        day_date = week_start + timedelta(days=weekday)
        sessions = []
        for schedule in active_schedules_for_day(schedules, weekday, day_date):
            sessions.append(
                {
                    'schedule_id': schedule.pk,
                    'group_id': schedule.group_id,
                    'group_name': schedule.group.name,
                    'course_type_label': ', '.join(schedule.group.get_service_labels()) or '—',
                    'start_time': schedule.start_time,
                    'duration_min': schedule.duration_min,
                    'room_or_link': schedule.room_or_link,
                    'session_date': day_date,
                    'session_date_iso': day_date.isoformat(),
                },
            )
        days.append(
            {
                'weekday': weekday,
                'label': weekday_labels.get(weekday, str(weekday)),
                'date': day_date,
                'date_label': day_date.strftime('%d.%m'),
                'is_today': day_date == today,
                'is_weekend': weekday >= 5,
                'sessions': sessions,
            },
        )

    return {
        'week_start': week_start,
        'week_end': week_end,
        'prev_week': (week_start - timedelta(days=7)).isoformat(),
        'next_week': (week_start + timedelta(days=7)).isoformat(),
        'days': days,
        'has_sessions': any(day['sessions'] for day in days),
    }


def _agenda_slot(session, now):
    start = timezone.make_aware(
        datetime.combine(session['session_date'], session['start_time']),
        timezone.get_current_timezone(),
    )
    end = start + timedelta(minutes=session['duration_min'] or 0)
    room = (session['room_or_link'] or '').strip()
    is_link = room.startswith(('http://', 'https://'))
    course = session['course_type_label']
    return {
        'group_name': session['group_name'],
        'details': ' · '.join(part for part in (course if course != '—' else '', '' if is_link else room) if part),
        'date': session['session_date'],
        'start_time': start.strftime('%H:%M'),
        'end_time': end.strftime('%H:%M'),
        'duration_min': session['duration_min'],
        'join_url': room if is_link else '',
        'is_now': start <= now < end,
        'is_done': now >= end,
    }


def build_student_today_agenda(student_id, now=None):
    """Today's sessions for the student dashboard, and the next one when none is left today.

    Read live on every request: the "now" and "done" marks go stale in any cache.
    """
    now = timezone.localtime(now) if now else timezone.localtime()
    today = now.date()
    week_start = today - timedelta(days=today.weekday())

    today_slots = []
    next_slot = None
    for offset in (0, 7):
        calendar = build_student_week_calendar(student_id, week_start=week_start + timedelta(days=offset))
        for day in calendar['days']:
            if day['date'] < today:
                continue
            for session in day['sessions']:
                slot = _agenda_slot(session, now)
                if day['date'] == today:
                    today_slots.append(slot)
                if next_slot is None and not slot['is_done'] and not slot['is_now'] and day['date'] > today:
                    next_slot = slot
        if next_slot is not None:
            break

    upcoming_today = [slot for slot in today_slots if not slot['is_done']]
    return {
        'today_schedule': today_slots,
        'today_remaining': len(upcoming_today),
        # the next lesson is only worth a line when nothing is left today
        'next_session': None if upcoming_today else next_slot,
    }
