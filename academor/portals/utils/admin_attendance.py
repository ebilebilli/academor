"""Admin attendance hub and student overview helpers."""

from __future__ import annotations

from datetime import date

from django.db.models import Count, Q
from django.utils import timezone

from portals.models import Attendance, Schedule, StudentProfile, StudyGroup, TeacherProfile
from portals.utils.queries import serialize_attendance
from portals.utils.teacher_attendance import save_session_attendance
from portals.utils.teacher_schedule import active_schedules_for_day


def admin_teacher_choices():
    return list(
        TeacherProfile.objects.select_related('user')
        .order_by('user__username')
        .values_list('pk', 'user__username')
    )


def admin_groups_for_teacher(teacher_id):
    if not teacher_id:
        return StudyGroup.objects.none()
    return (
        StudyGroup.objects.filter(teacher_id=teacher_id, is_active=True)
        .annotate(student_count=Count('students', distinct=True))
        .order_by('name')
    )


def schedules_for_group_on_date(group, session_date):
    schedules = list(
        group.schedules.select_related('group').order_by('start_time', 'id')
    )
    weekday = session_date.weekday()
    return active_schedules_for_day(schedules, weekday, session_date)


def build_admin_attendance_hub_context(*, teacher_id=None, group_id=None, session_date=None, schedule_id=None):
    session_date = session_date or timezone.localdate()
    teachers = admin_teacher_choices()
    groups = admin_groups_for_teacher(teacher_id) if teacher_id else StudyGroup.objects.none()
    group = None
    schedule = None
    students = []
    existing = {}
    schedule_choices = []

    if group_id:
        group = (
            StudyGroup.objects.filter(pk=group_id, is_active=True)
            .select_related('teacher__user')
            .first()
        )
        if group:
            if not teacher_id:
                teacher_id = group.teacher_id
            schedule_choices = schedules_for_group_on_date(group, session_date)
            if schedule_id:
                schedule = next((row for row in schedule_choices if row.pk == int(schedule_id)), None)
            if not schedule and len(schedule_choices) == 1:
                schedule = schedule_choices[0]
            if schedule:
                students = list(
                    group.students.select_related('user').order_by('user__username', 'id')
                )
                existing = {
                    row.student_id: row.status
                    for row in Attendance.objects.filter(
                        schedule=schedule,
                        session_date=session_date,
                    )
                }

    return {
        'teachers': teachers,
        'teacher_id': teacher_id,
        'groups': groups,
        'group': group,
        'group_id': group_id,
        'session_date': session_date,
        'schedule': schedule,
        'schedule_id': schedule.pk if schedule else schedule_id,
        'schedule_choices': schedule_choices,
        'students': students,
        'existing': existing,
        'status_choices': Attendance.Status.choices,
    }


def get_student_attendance_overview(student: StudentProfile):
    records_qs = (
        Attendance.objects.filter(student=student)
        .select_related('schedule', 'schedule__group', 'schedule__group__teacher__user', 'student__user')
        .order_by('-session_date', '-marked_at', 'id')
    )
    records = [serialize_attendance(row) for row in records_qs]
    summary = {'present': 0, 'absent': 0, 'late': 0, 'total': len(records)}
    for row in records:
        key = row['status']
        if key in summary:
            summary[key] += 1

    lessons_per_month = student.lessons_per_month
    program_month = student.program_month or 0
    expected_total = None
    if lessons_per_month and program_month:
        expected_total = lessons_per_month * program_month

    attended = summary['present'] + summary['late']
    groups = list(
        student.groups.filter(is_active=True)
        .select_related('teacher__user')
        .order_by('name')
    )

    return {
        'student': student,
        'groups': groups,
        'summary': summary,
        'records': records,
        'lessons_per_month': lessons_per_month,
        'program_month': program_month,
        'expected_total': expected_total,
        'attended_count': attended,
        'absent_count': summary['absent'],
    }


def save_admin_group_attendance(schedule, session_date, student_status_map):
    return save_session_attendance(schedule, session_date, student_status_map)
