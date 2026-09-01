"""Shared helpers for Qrup Excel → portal import (JSON + management command)."""

from __future__ import annotations

from datetime import timedelta

IELTS_COURSE_SLUGS = ('ielts-course', 'ielts')
IELTS_COURSE_NAMES = ('ielts course',)

ENGLISH_LANGUAGE_COURSE_SLUGS = (
    'english-language-course',
    'english-language',
    'general-english',
)
ENGLISH_LANGUAGE_COURSE_NAMES = ('english language course', 'english language')

IELTS_DEFAULT_ENROLLMENT_SLUGS = IELTS_COURSE_SLUGS + ENGLISH_LANGUAGE_COURSE_SLUGS

IELTS_GROUP_COURSE_SLUGS = ('ielts', 'general-english')


def normalize_course_slug(slug):
    slug = (slug or '').strip().lower()
    if slug in ('foundation-ielts', 'foundation_ielts'):
        return 'ielts'
    return slug


def is_ielts_track(subject='', course_slug=''):
    subject_l = (subject or '').strip().lower()
    slug = normalize_course_slug(course_slug)
    if slug == 'ielts' or 'ielts' in slug:
        return True
    return subject_l in ('ielts', 'foundation ielts') or 'ielts' in subject_l


def group_course_slugs(subject='', course_slug=''):
    slug = normalize_course_slug(course_slug)
    if is_ielts_track(subject, slug):
        return list(IELTS_GROUP_COURSE_SLUGS)
    if slug:
        return [slug]
    return []


def student_course_enrollment_slugs(subject='', course_slug=''):
    slug = normalize_course_slug(course_slug or subject)
    if is_ielts_track(subject, slug):
        return list(IELTS_DEFAULT_ENROLLMENT_SLUGS)
    if slug:
        return [slug]
    return []


def parse_lessons_participation(lessons_str, month_val):
    """Parse Excel '8/12' + month number into attendance import payload."""
    import re

    text = (lessons_str or '').strip()
    if not text:
        return None
    match = re.match(r'(\d+)\s*/\s*(\d+)', text)
    if not match:
        return None
    attended = int(match.group(1))
    per_month = int(match.group(2))
    if per_month <= 0:
        return None

    month_number = 1
    if month_val is not None and str(month_val).strip().lower() not in ('', 'nan', 'none'):
        try:
            month_number = max(1, int(float(month_val)))
        except (TypeError, ValueError):
            month_number = 1

    return {
        'lessons_attended': attended,
        'lessons_per_month': per_month,
        'month_number': month_number,
        'total_sessions': per_month * month_number,
    }


def iter_group_sessions(group, start_date, *, max_sessions):
    """Chronological (schedule, session_date) slots from start_date."""
    from portals.utils.teacher_schedule import schedule_visible_on_date

    if not start_date or max_sessions <= 0:
        return []

    schedules = list(group.schedules.order_by('weekday', 'start_time', 'id'))
    if not schedules:
        return []

    results = []
    day = start_date
    for _ in range(366 * 3):
        if len(results) >= max_sessions:
            break
        for schedule in schedules:
            if schedule.weekday == day.weekday() and schedule_visible_on_date(schedule, day):
                results.append((schedule, day))
                if len(results) >= max_sessions:
                    break
        day += timedelta(days=1)
    return results


def sync_student_participation(student, group, participation, *, start_date):
    """Mark the first N generated sessions as present (Excel iştirak sayı)."""
    from portals.models import Attendance

    if not participation or not start_date:
        return 0

    per_month = int(participation.get('lessons_per_month') or 0)
    month_number = int(participation.get('month_number') or 1)
    attended = int(participation.get('lessons_attended') or 0)
    if per_month <= 0 or month_number <= 0 or attended <= 0:
        return 0

    total_sessions = per_month * month_number
    attended = min(attended, total_sessions)
    sessions = iter_group_sessions(group, start_date, max_sessions=total_sessions)
    if not sessions:
        return 0

    schedule_ids = {schedule.pk for schedule, _ in sessions}
    Attendance.objects.filter(student=student, schedule_id__in=schedule_ids).delete()

    saved = 0
    for schedule, session_date in sessions[:attended]:
        Attendance.objects.update_or_create(
            schedule=schedule,
            student=student,
            session_date=session_date,
            defaults={'status': Attendance.Status.PRESENT},
        )
        saved += 1
    return saved
