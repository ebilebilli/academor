"""Monthly attendance register (paper-book grid) for teachers."""

from __future__ import annotations

import calendar
from datetime import date

from django.db.models import Count, Q
from django.utils import timezone
from django.utils.translation import gettext as _

from portals.models import Attendance, AttendanceRegisterGuest, StudentProfile
from portals.utils.teacher_courses import teacher_groups_queryset

REGISTER_STATUSES = frozenset(Attendance.Status.values)
MAX_GUEST_NAME_LEN = 200
MAX_GROUP_NAME_LEN = 200


def weekday_shorts():
    return (
        _('Be'),
        _('Ça'),
        _('Ç'),
        _('Ca'),
        _('C'),
        _('Ş'),
        _('B'),
    )


def parse_register_month(raw_value, today=None):
    today = today or timezone.localdate()
    if raw_value:
        try:
            year_s, month_s = str(raw_value).strip().split('-', 1)
            year, month = int(year_s), int(month_s)
            if 2000 <= year <= 2100 and 1 <= month <= 12:
                return year, month
        except (TypeError, ValueError):
            pass
    return today.year, today.month


def shift_month(year, month, delta):
    month += delta
    year += (month - 1) // 12
    month = (month - 1) % 12 + 1
    return year, month


def month_key(year, month):
    return f'{year:04d}-{month:02d}'


def student_start_date(student, group=None):
    if getattr(student, 'enrollment_date', None):
        return student.enrollment_date
    if group is not None:
        return group.start_date
    return None


def _group_payload(group):
    labels = group.get_course_labels() if group else []
    return {
        'id': group.pk,
        'name': group.name,
        'course_label': ', '.join(labels) if not group.is_register_only else '',
        'start_date': group.start_date,
        'is_register_only': bool(group.is_register_only),
    }


def _person_filter(*, student=None, guest=None):
    if student is not None:
        return Q(student_id=student.pk if hasattr(student, 'pk') else student)
    if guest is not None:
        return Q(guest_id=guest.pk if hasattr(guest, 'pk') else guest)
    return Q(pk__in=[])


def _register_attendance_qs(group, month_start, month_end, *, student_ids=None, guest_ids=None):
    qs = Attendance.objects.filter(
        Q(group_id=group.pk) | Q(schedule__group_id=group.pk),
        session_date__range=(month_start, month_end),
    )
    person_q = Q()
    if student_ids:
        person_q |= Q(student_id__in=student_ids)
    if guest_ids:
        person_q |= Q(guest_id__in=guest_ids)
    if not student_ids and not guest_ids:
        return qs.none()
    return qs.filter(person_q).order_by('marked_at', 'id')


def month_status_counts(*, group, year, month, student=None, guest=None):
    days_in_month = calendar.monthrange(year, month)[1]
    month_start = date(year, month, 1)
    month_end = date(year, month, days_in_month)
    qs = Attendance.objects.filter(
        Q(group_id=group.pk) | Q(schedule__group_id=group.pk),
        session_date__range=(month_start, month_end),
    ).filter(_person_filter(student=student, guest=guest))
    marks = {}
    for row in qs.order_by('marked_at', 'id'):
        marks[row.session_date] = row.status
    present = sum(1 for status in marks.values() if status == Attendance.Status.PRESENT)
    absent = sum(1 for status in marks.values() if status == Attendance.Status.ABSENT)
    late = sum(1 for status in marks.values() if status == Attendance.Status.LATE)
    return {
        'present': present,
        'absent': absent,
        'late': late,
        'attended': present + late,
    }


def _build_cells(days, marks, start=None):
    cells = []
    present = absent = late = 0
    for day in days:
        disabled = not day['in_month']
        reason = 'invalid'
        if not disabled and start and date.fromisoformat(day['iso']) < start:
            disabled = True
            reason = 'before_start'
        elif not disabled:
            reason = ''
        status = ''
        if not disabled:
            status = marks.get(date.fromisoformat(day['iso']), '') or ''
        if status == Attendance.Status.PRESENT:
            present += 1
        elif status == Attendance.Status.ABSENT:
            absent += 1
        elif status == Attendance.Status.LATE:
            late += 1
        cells.append({
            'n': day['n'],
            'iso': day['iso'],
            'status': status,
            'disabled': disabled,
            'reason': reason,
        })
    return cells, present, absent, late


def build_teacher_attendance_register(teacher, *, year, month, group=None, today=None):
    today = today or timezone.localdate()
    groups = list(
        teacher_groups_queryset(teacher.pk, active_only=True, include_register_only=True)
        .prefetch_related('courses')
        .annotate(
            student_count=Count('students', distinct=True),
            guest_count=Count(
                'register_guests',
                filter=Q(register_guests__is_active=True),
                distinct=True,
            ),
        )
        .order_by('is_register_only', 'name', 'id')
    )
    selected = group
    group_ids = {item.pk for item in groups}
    if selected is None or selected.pk not in group_ids:
        selected = groups[0] if groups else None

    days_in_month = calendar.monthrange(year, month)[1]
    month_start = date(year, month, 1)
    month_end = date(year, month, days_in_month)
    prev_year, prev_month = shift_month(year, month, -1)
    next_year, next_month = shift_month(year, month, 1)

    days = []
    shorts = weekday_shorts()
    for day_n in range(1, 32):
        in_month = day_n <= days_in_month
        day_date = date(year, month, day_n) if in_month else None
        weekday = day_date.weekday() if day_date else None
        days.append({
            'n': day_n,
            'iso': day_date.isoformat() if day_date else '',
            'weekday': weekday,
            'weekday_short': shorts[weekday] if weekday is not None else '',
            'is_today': bool(day_date and day_date == today),
            'is_future': bool(day_date and day_date > today),
            'is_weekend': weekday in (5, 6) if weekday is not None else False,
            'in_month': in_month,
        })

    students = []
    if selected:
        students_qs = (
            StudentProfile.objects.filter(groups=selected)
            .select_related('user')
            .order_by('user__username', 'id')
        )
        student_rows = []
        for student in students_qs:
            start = student_start_date(student, selected)
            if start and start > month_end:
                continue
            student_rows.append((student, start))

        guests = list(
            AttendanceRegisterGuest.objects.filter(group=selected, is_active=True)
            .order_by('name', 'id')
        )

        student_marks = {}
        guest_marks = {}
        if student_rows or guests:
            for row in _register_attendance_qs(
                selected,
                month_start,
                month_end,
                student_ids=[student.pk for student, _start in student_rows] or None,
                guest_ids=[guest.pk for guest in guests] or None,
            ):
                if row.student_id:
                    student_marks[(row.student_id, row.session_date)] = row.status
                elif row.guest_id:
                    guest_marks[(row.guest_id, row.session_date)] = row.status

        for student, start in student_rows:
            marks = {
                day: status
                for (sid, day), status in student_marks.items()
                if sid == student.pk
            }
            cells, present, absent, late = _build_cells(days, marks, start=start)
            students.append({
                'id': student.pk,
                'guest_id': None,
                'is_guest': False,
                'name': student.full_name,
                'start_date': start,
                'absent_count': absent,
                'present_count': present,
                'late_count': late,
                'attended_count': present + late,
                'cells': cells,
            })

        for guest in guests:
            marks = {
                day: status
                for (gid, day), status in guest_marks.items()
                if gid == guest.pk
            }
            cells, present, absent, late = _build_cells(days, marks)
            students.append({
                'id': None,
                'guest_id': guest.pk,
                'is_guest': True,
                'name': guest.name,
                'start_date': None,
                'absent_count': absent,
                'present_count': present,
                'late_count': late,
                'attended_count': present + late,
                'cells': cells,
            })

    return {
        'year': year,
        'month': month,
        'month_key': month_key(year, month),
        'month_date': month_start,
        'prev_month': month_key(prev_year, prev_month),
        'next_month': month_key(next_year, next_month),
        'days_in_month': days_in_month,
        'teacher_name': teacher.full_name,
        'group': _group_payload(selected) if selected else None,
        'groups': [
            {
                'id': item.pk,
                'name': item.name,
                'is_register_only': bool(item.is_register_only),
                'student_count': (
                    int(getattr(item, 'student_count', 0) or 0)
                    + int(getattr(item, 'guest_count', 0) or 0)
                ),
            }
            for item in groups
        ],
        'days': days,
        'students': students,
    }


def save_register_mark(*, group, session_date, status, student=None, guest=None):
    status = (status or '').strip()
    if status and status not in REGISTER_STATUSES:
        return {'ok': False, 'error': 'invalid_status'}
    if bool(student) == bool(guest):
        return {'ok': False, 'error': 'invalid_person'}

    if student is not None:
        if not group.students.filter(pk=student.pk).exists():
            return {'ok': False, 'error': 'not_in_group'}
        start = student_start_date(student, group)
        if start and session_date < start:
            return {'ok': False, 'error': 'before_start'}
        person_q = Q(student_id=student.pk)
    else:
        if guest.group_id != group.pk or not guest.is_active:
            return {'ok': False, 'error': 'not_in_group'}
        person_q = Q(guest_id=guest.pk)

    qs = Attendance.objects.filter(
        session_date=session_date,
    ).filter(Q(group_id=group.pk) | Q(schedule__group_id=group.pk)).filter(person_q)

    if not status:
        qs.delete()
        counts = month_status_counts(
            group=group,
            year=session_date.year,
            month=session_date.month,
            student=student,
            guest=guest,
        )
        return {'ok': True, 'status': '', **counts}

    updated = qs.update(status=status)
    if not updated:
        Attendance.objects.create(
            schedule=None,
            group=group,
            student=student,
            guest=guest,
            session_date=session_date,
            status=status,
        )
    counts = month_status_counts(
        group=group,
        year=session_date.year,
        month=session_date.month,
        student=student,
        guest=guest,
    )
    return {'ok': True, 'status': status, **counts}


def add_register_guest(*, group, name):
    cleaned = ' '.join(str(name or '').split())
    if not cleaned:
        return {'ok': False, 'error': 'empty_name'}
    if len(cleaned) > MAX_GUEST_NAME_LEN:
        return {'ok': False, 'error': 'name_too_long'}

    existing = (
        AttendanceRegisterGuest.objects.filter(
            group=group,
            is_active=True,
            name__iexact=cleaned,
        )
        .order_by('id')
        .first()
    )
    if existing:
        return {
            'ok': True,
            'guest': {
                'id': existing.pk,
                'name': existing.name,
                'is_guest': True,
            },
            'created': False,
        }

    guest = AttendanceRegisterGuest.objects.create(group=group, name=cleaned)
    return {
        'ok': True,
        'guest': {
            'id': guest.pk,
            'name': guest.name,
            'is_guest': True,
        },
        'created': True,
    }


def remove_register_guest(*, group, guest):
    if guest.group_id != group.pk:
        return {'ok': False, 'error': 'not_in_group'}
    if guest.is_active:
        AttendanceRegisterGuest.objects.filter(pk=guest.pk).update(is_active=False)
    return {'ok': True, 'guest_id': guest.pk}


def add_register_group(*, teacher, name):
    from portals.models import StudyGroup

    cleaned = ' '.join(str(name or '').split())
    if not cleaned:
        return {'ok': False, 'error': 'empty_name'}
    if len(cleaned) > MAX_GROUP_NAME_LEN:
        return {'ok': False, 'error': 'name_too_long'}

    existing = (
        StudyGroup.objects.filter(
            teacher_id=teacher.pk,
            is_active=True,
            is_register_only=True,
            name__iexact=cleaned,
        )
        .order_by('id')
        .first()
    )
    if existing:
        return {
            'ok': True,
            'group': {
                'id': existing.pk,
                'name': existing.name,
                'is_register_only': True,
            },
            'created': False,
        }

    group = StudyGroup.objects.create(
        teacher=teacher,
        name=cleaned,
        is_register_only=True,
        is_active=True,
        max_students=50,
    )
    return {
        'ok': True,
        'group': {
            'id': group.pk,
            'name': group.name,
            'is_register_only': True,
        },
        'created': True,
    }


def remove_register_group(*, teacher, group):
    if group.teacher_id != teacher.pk or not group.is_register_only:
        return {'ok': False, 'error': 'not_register_group'}
    if group.is_active:
        from portals.models import StudyGroup

        StudyGroup.objects.filter(pk=group.pk).update(is_active=False)
    return {'ok': True, 'group_id': group.pk}
