"""Teacher weekly schedule calendar helpers."""

from datetime import date, timedelta

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
        for schedule in schedules:
            if schedule.weekday != weekday:
                continue
            if not schedule_visible_on_date(schedule, day_date):
                continue
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
        for schedule in schedules:
            if schedule.weekday != weekday:
                continue
            if not schedule_visible_on_date(schedule, day_date):
                continue
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
