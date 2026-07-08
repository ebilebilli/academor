"""Weekly student scores (0–10 per week) — teacher grading helpers."""

from datetime import date, timedelta
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils.translation import gettext as _

from portals.models import WeeklyStudentScore
from portals.models.score_models import WEEKLY_SCORE_MAX
from portals.utils.cache_utils import cached_query, invalidate_model_cache
from portals.utils.queries import get_teacher_weekly_score_students
from portals.utils.teacher_access import get_teacher_student
from portals.utils.teacher_courses import teacher_groups_queryset
from portals.utils.teacher_schedule import parse_week_start


def serialize_weekly_score(row):
    from portals.utils.quiz_stats import quiz_average_score_tier, quiz_score_percent

    week_end = row.week_start + timedelta(days=6)
    pct = quiz_score_percent(float(row.score), WEEKLY_SCORE_MAX)
    return {
        'id': row.pk,
        'student_id': row.student_id,
        'student_name': row.student.full_name,
        'teacher_id': row.teacher_id,
        'teacher_name': row.teacher.full_name,
        'week_start': row.week_start,
        'week_end': week_end,
        'score': float(row.score),
        'max_score': WEEKLY_SCORE_MAX,
        'tier': quiz_average_score_tier(pct),
        'comment': row.comment,
        'updated_at': row.updated_at,
        'date': row.week_start,
    }


def current_week_start():
    return parse_week_start(None)


def is_current_week(week_start):
    return _normalize_week_start(week_start) == current_week_start()


def build_weekly_score_calendar(week_start=None):
    week_start = _normalize_week_start(week_start) if week_start else current_week_start()
    week_end = week_start + timedelta(days=6)
    return {
        'week_start': week_start,
        'week_end': week_end,
        'prev_week': (week_start - timedelta(days=7)).isoformat(),
        'next_week': (week_start + timedelta(days=7)).isoformat(),
    }


def _normalize_week_start(week_start):
    if isinstance(week_start, date):
        parsed = week_start
    else:
        parsed = parse_week_start(str(week_start) if week_start else None)
    if parsed.weekday() != 0:
        parsed = parsed - timedelta(days=parsed.weekday())
    return parsed


def _parse_score_value(raw_value):
    if raw_value is None:
        return None
    text = str(raw_value).strip()
    if not text:
        return None
    try:
        value = Decimal(text)
    except (InvalidOperation, ValueError):
        raise ValidationError(_('Enter a valid score between 0 and 10.'))
    if value < 0 or value > WEEKLY_SCORE_MAX:
        raise ValidationError(_('Score must be between 0 and 10.'))
    return value.quantize(Decimal('0.1'))


def _build_group_tabs_for_teacher(teacher_id, all_rows):
    students_by_group = {}
    for row in all_rows:
        for group_id in row.get('group_ids', []):
            students_by_group.setdefault(group_id, []).append(row)

    groups = []
    for group in teacher_groups_queryset(teacher_id, active_only=True).order_by('name'):
        group_rows = students_by_group.get(group.pk, [])
        groups.append({
            'id': group.pk,
            'name': group.name,
            'student_count': len(group_rows),
            'scored_count': sum(1 for row in group_rows if row.get('score') is not None),
        })
    return groups


@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_teacher_weekly_score_board(teacher_id, week_start_iso):
    week_start = _normalize_week_start(week_start_iso)
    students = get_teacher_weekly_score_students(teacher_id)
    if not students:
        calendar = build_weekly_score_calendar(week_start)
        return {
            'calendar': calendar,
            'rows': [],
            'groups': [],
            'scored_count': 0,
            'student_count': 0,
            'progress_percent': 0,
        }

    student_ids = [row['id'] for row in students]
    existing = {
        row.student_id: row
        for row in WeeklyStudentScore.objects.filter(
            teacher_id=teacher_id,
            week_start=week_start,
            student_id__in=student_ids,
        ).select_related('student', 'teacher')
    }

    rows = []
    scored_count = 0
    for student in students:
        record = existing.get(student['id'])
        if record:
            scored_count += 1
        rows.append({
            **student,
            'weekly_score_id': record.pk if record else None,
            'is_locked': record is not None,
            'score': float(record.score) if record else None,
            'comment': record.comment if record else '',
            'updated_at': record.updated_at if record else None,
        })

    student_count = len(rows)
    return {
        'calendar': build_weekly_score_calendar(week_start),
        'rows': rows,
        'groups': _build_group_tabs_for_teacher(teacher_id, rows),
        'scored_count': scored_count,
        'student_count': student_count,
        'progress_percent': round(100 * scored_count / student_count) if student_count else 0,
    }


def build_teacher_weekly_score_view(teacher_id, week_start_iso=None, group_id=None):
    week_start = _normalize_week_start(week_start_iso) if week_start_iso else current_week_start()
    board = get_teacher_weekly_score_board(teacher_id, week_start.isoformat())
    active_group = str(group_id or 'all')
    rows = board['rows']
    if active_group != 'all':
        try:
            selected_group_id = int(active_group)
        except (TypeError, ValueError):
            selected_group_id = None
        if selected_group_id:
            rows = [row for row in rows if selected_group_id in row.get('group_ids', [])]

    scored_count = sum(1 for row in rows if row.get('score') is not None)
    student_count = len(rows)
    editable_count = sum(
        1 for row in rows
        if not row.get('is_locked') and not row.get('weekly_score_id')
    )
    total_editable_count = sum(
        1 for row in board['rows']
        if not row.get('is_locked') and not row.get('weekly_score_id')
    )
    return {
        **board,
        'rows': rows,
        'active_group': active_group,
        'scored_count': scored_count,
        'student_count': student_count,
        'editable_count': editable_count,
        'total_editable_count': total_editable_count,
        'total_scored_count': board['scored_count'],
        'total_student_count': board['student_count'],
        'progress_percent': round(100 * scored_count / student_count) if student_count else 0,
        'week_value': board['calendar']['week_start'].isoformat(),
        'is_current_week': True,
        'has_editable_rows': editable_count > 0,
        'has_any_editable_rows': total_editable_count > 0,
    }


@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_student_weekly_scores(student_id):
    qs = (
        WeeklyStudentScore.objects.filter(student_id=student_id)
        .select_related('student', 'teacher', 'teacher__user')
        .order_by('-week_start', '-updated_at', '-id')[:52]
    )
    return [serialize_weekly_score(row) for row in qs]


@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_teacher_weekly_scores_list(teacher_id):
    qs = (
        WeeklyStudentScore.objects.filter(teacher_id=teacher_id)
        .select_related('student', 'teacher', 'teacher__user', 'student__user')
        .order_by('-week_start', '-updated_at', '-id')[:200]
    )
    return [serialize_weekly_score(row) for row in qs]


@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_teacher_student_weekly_scores(teacher_id, student_id):
    if not get_teacher_student(teacher_id, student_id):
        return []
    qs = (
        WeeklyStudentScore.objects.filter(
            teacher_id=teacher_id,
            student_id=student_id,
        )
        .select_related('student', 'teacher', 'teacher__user')
        .order_by('-week_start', '-updated_at', '-id')[:52]
    )
    return [serialize_weekly_score(row) for row in qs]


def _entry_touches_locked_score(existing, score_value, comment):
    if score_value is None:
        return False
    if float(existing.score) != float(score_value):
        return True
    if (existing.comment or '').strip() != comment:
        return True
    return False


def _existing_weekly_score_ids(teacher_id, week_start, student_ids):
    if not student_ids:
        return set()
    return set(
        WeeklyStudentScore.objects.filter(
            teacher_id=teacher_id,
            week_start=week_start,
            student_id__in=student_ids,
        ).values_list('student_id', flat=True)
    )


def student_ids_open_for_scoring(rows, *, teacher_id, week_start):
    """Return student IDs that may receive a new weekly score (DB-backed, not cache)."""
    if not rows:
        return []
    week_start = _normalize_week_start(week_start)
    row_ids = [row['id'] for row in rows]
    scored_ids = _existing_weekly_score_ids(teacher_id, week_start, row_ids)
    return [student_id for student_id in row_ids if student_id not in scored_ids]


def save_teacher_weekly_scores(*, teacher_id, week_start, entries):
    """
    Create weekly scores for teacher-owned students (one save per student per week).

    Existing scores cannot be changed or removed through the teacher portal.
    """
    week_start = _normalize_week_start(week_start)
    if not is_current_week(week_start):
        raise ValidationError(_('You can only score students for the current week.'))
    saved = 0
    skipped = 0
    errors = []

    with transaction.atomic():
        for entry in entries:
            student_id = entry.get('student_id')
            if not student_id:
                continue
            if not get_teacher_student(teacher_id, student_id):
                errors.append(_('You cannot score this student.'))
                continue

            try:
                score_value = _parse_score_value(entry.get('score'))
            except ValidationError as exc:
                errors.append(str(exc.messages[0] if exc.messages else exc))
                continue

            comment = (entry.get('comment') or '').strip()
            existing = WeeklyStudentScore.objects.filter(
                teacher_id=teacher_id,
                student_id=student_id,
                week_start=week_start,
            ).first()

            if existing:
                if score_value is None:
                    skipped += 1
                    continue
                if _entry_touches_locked_score(existing, score_value, comment):
                    errors.append(_('This weekly score is already saved and cannot be changed.'))
                else:
                    skipped += 1
                continue

            if score_value is None:
                continue

            record = WeeklyStudentScore(
                teacher_id=teacher_id,
                student_id=student_id,
                week_start=week_start,
                score=score_value,
                comment=comment,
            )
            try:
                # Savepoint so a concurrent insert (unique constraint on
                # student+teacher+week) is skipped instead of 500ing.
                with transaction.atomic():
                    record.full_clean()
                    record.save()
            except IntegrityError:
                skipped += 1
                continue
            saved += 1
            from portals.utils.notifications import create_weekly_score_published_notifications
            create_weekly_score_published_notifications(record)

    if errors:
        raise ValidationError(errors[0])

    invalidate_model_cache('WeeklyStudentScore')
    invalidate_model_cache('PortalNotification')
    return {'saved': saved, 'removed': 0, 'skipped': skipped}


def parse_weekly_score_post(request_post, student_ids):
    entries = []
    for student_id in student_ids:
        entries.append({
            'student_id': student_id,
            'score': request_post.get(f'score_{student_id}', ''),
            'comment': request_post.get(f'comment_{student_id}', ''),
        })
    return entries
