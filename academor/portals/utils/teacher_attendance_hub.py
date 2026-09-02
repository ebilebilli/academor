"""Teacher attendance overview — group-scoped stats and weekly schedule counts."""

from __future__ import annotations

from django.db.models import Count, Prefetch, Q

from portals.models import Attendance, Schedule, StudentProfile, StudyGroup
from portals.utils.cache_utils import cached_query
from portals.utils.queries import serialize_student, teacher_attendance_queryset
from portals.utils.teacher_courses import teacher_groups_queryset


def _empty_summary():
    return {'present': 0, 'absent': 0, 'late': 0, 'marked': 0}


def _summary_from_counts(row):
    return {
        'present': int(row.get('present') or 0),
        'absent': int(row.get('absent') or 0),
        'late': int(row.get('late') or 0),
        'marked': int(row.get('marked') or 0),
    }


def _merge_summaries(*summaries):
    total = _empty_summary()
    for summary in summaries:
        for key in total:
            total[key] += int(summary.get(key) or 0)
    return total


def _attendance_rate(summary):
    marked = summary.get('marked') or 0
    if not marked:
        return None
    return round(100 * summary['present'] / marked, 1)


def _hub_stats_from_summary(summary, *, student_count, needs_attention):
    return {
        'student_count': student_count,
        'weekly_sessions': summary.get('weekly_sessions', 0),
        'sessions_marked': summary['marked'],
        'present': summary['present'],
        'absent': summary['absent'],
        'late': summary['late'],
        'needs_attention': needs_attention,
        'attendance_rate': _attendance_rate(summary),
    }


@cached_query(timeout='CACHE_TIMEOUT_SHORT')
def build_teacher_attendance_hub(teacher_id):
    teacher_groups = teacher_groups_queryset(teacher_id, active_only=True)
    if not teacher_groups.exists():
        empty = _hub_stats_from_summary(_empty_summary(), student_count=0, needs_attention=0)
        return {'groups': [], 'students': [], 'stats': {'all': empty}}

    weekly_by_group = {
        row['group_id']: row['weekly_sessions']
        for row in Schedule.objects.filter(group__in=teacher_groups)
        .values('group_id')
        .annotate(weekly_sessions=Count('id'))
    }

    stats_rows = (
        teacher_attendance_queryset(teacher_id)
        .values('student_id', 'schedule__group_id')
        .annotate(
            present=Count('id', filter=Q(status=Attendance.Status.PRESENT)),
            absent=Count('id', filter=Q(status=Attendance.Status.ABSENT)),
            late=Count('id', filter=Q(status=Attendance.Status.LATE)),
            marked=Count('id'),
        )
    )
    stats_by_student_group = {}
    for row in stats_rows:
        student_id = row['student_id']
        group_id = row['schedule__group_id']
        stats_by_student_group.setdefault(student_id, {})[group_id] = _summary_from_counts(row)

    teacher_group_ids = list(teacher_groups.values_list('pk', flat=True))
    students_qs = (
        StudentProfile.objects.filter(groups__in=teacher_groups)
        .distinct()
        .select_related('user')
        .prefetch_related(
            Prefetch(
                'groups',
                queryset=StudyGroup.objects.filter(pk__in=teacher_group_ids).order_by('name'),
            ),
        )
        .order_by('user__username', 'id')
    )

    students = []
    all_summaries_for_hub = []
    needs_attention_all = 0

    for student in students_qs:
        member_groups = list(student.groups.all())
        group_ids = [group.pk for group in member_groups]
        per_group = {}
        group_summaries = []
        for group_id in group_ids:
            summary = stats_by_student_group.get(student.pk, {}).get(group_id, _empty_summary())
            per_group[str(group_id)] = summary
            group_summaries.append(summary)
        summary_all = _merge_summaries(*group_summaries) if group_summaries else _empty_summary()
        if summary_all['absent'] > 0:
            needs_attention_all += 1
        all_summaries_for_hub.append(summary_all)

        weekly_all = sum(weekly_by_group.get(group_id, 0) for group_id in group_ids)
        weekly_by_scope = {'all': weekly_all}
        for group_id in group_ids:
            weekly_by_scope[str(group_id)] = weekly_by_group.get(group_id, 0)

        students.append({
            **serialize_student(student),
            'group_ids': group_ids,
            'group_names': [group.name for group in member_groups],
            'summary_by_group': {
                'all': summary_all,
                **per_group,
            },
            'weekly_sessions_by_group': weekly_by_scope,
            'summary': summary_all,
            'weekly_sessions': weekly_all,
            'attendance_rate': _attendance_rate(summary_all),
        })

    groups = []
    group_stats_map = {}
    students_by_group = {}
    for row in students:
        for group_id in row['group_ids']:
            students_by_group.setdefault(group_id, []).append(row)

    for group in teacher_groups.order_by('name'):
        group_students = students_by_group.get(group.pk, [])
        summaries = [row['summary_by_group'][str(group.pk)] for row in group_students]
        group_summary = _merge_summaries(*summaries) if summaries else _empty_summary()
        group_summary['weekly_sessions'] = weekly_by_group.get(group.pk, 0)
        needs_attention = sum(
            1 for row in group_students if row['summary_by_group'][str(group.pk)]['absent'] > 0
        )
        group_stats = _hub_stats_from_summary(
            group_summary,
            student_count=len(group_students),
            needs_attention=needs_attention,
        )
        group_stats_map[str(group.pk)] = group_stats
        groups.append({
            'id': group.pk,
            'name': group.name,
            'weekly_sessions': weekly_by_group.get(group.pk, 0),
            'student_count': len(group_students),
            'stats': group_stats,
        })

    all_summary = _merge_summaries(*all_summaries_for_hub) if all_summaries_for_hub else _empty_summary()
    all_summary['weekly_sessions'] = sum(weekly_by_group.values())
    stats_all = _hub_stats_from_summary(
        all_summary,
        student_count=len(students),
        needs_attention=needs_attention_all,
    )

    return {
        'groups': groups,
        'students': students,
        'stats': {
            'all': stats_all,
            **group_stats_map,
        },
    }


def build_today_attendance_sessions(teacher_id):
    """Today's class sessions with live mark progress. Not cached."""
    from datetime import timedelta

    from django.utils import timezone

    from portals.utils.teacher_schedule import build_teacher_week_calendar

    today = timezone.localdate()
    week_start = today - timedelta(days=today.weekday())
    calendar = build_teacher_week_calendar(teacher_id, week_start=week_start)
    today_day = next((day for day in calendar['days'] if day['is_today']), None)
    raw_sessions = list(today_day['sessions']) if today_day else []
    if not raw_sessions:
        return []

    schedule_ids = [session['schedule_id'] for session in raw_sessions]
    group_ids = [session['group_id'] for session in raw_sessions]
    student_counts = dict(
        StudyGroup.objects.filter(pk__in=group_ids)
        .annotate(n=Count('students', distinct=True))
        .values_list('pk', 'n')
    )
    marked_counts = {
        row['schedule_id']: row['n']
        for row in Attendance.objects.filter(
            schedule_id__in=schedule_ids,
            session_date=today,
        )
        .values('schedule_id')
        .annotate(n=Count('id'))
    }

    sessions = []
    for session in raw_sessions:
        student_count = int(student_counts.get(session['group_id']) or 0)
        marked_count = int(marked_counts.get(session['schedule_id']) or 0)
        sessions.append({
            **session,
            'student_count': student_count,
            'marked_count': marked_count,
            'is_complete': student_count > 0 and marked_count >= student_count,
            'is_partial': 0 < marked_count < student_count,
        })
    return sessions
