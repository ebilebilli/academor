"""Daily student scores (0–10 per day) — teacher grading helpers.

Scores used to be weekly; the helpers keep their ``weekly`` names so callers stay the
same, but every score is for one day (``WeeklyStudentScore.score_date``). The teacher
scores today by default and may pick an earlier day; never a future one. A student
without a group gets one row of their own (``group_id`` None).
"""

from datetime import date, timedelta
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.utils.translation import gettext as _

from portals.models import StudyGroup, WeeklyStudentScore
from portals.models.score_models import WEEKLY_SCORE_MAX
from portals.utils.cache_utils import cached_query, invalidate_model_cache
from portals.utils.queries import get_teacher_weekly_score_students
from portals.utils.teacher_access import get_teacher_student
from portals.utils.teacher_courses import teacher_groups_queryset

NO_GROUP_KEY = 'none'


def serialize_weekly_score(row):
    from portals.utils.quiz_stats import quiz_average_score_tier, quiz_score_percent

    pct = quiz_score_percent(float(row.score), WEEKLY_SCORE_MAX)
    group_name = ''
    if row.study_group_id and getattr(row, 'study_group', None):
        group_name = row.study_group.name
    return {
        'id': row.pk,
        'student_id': row.student_id,
        'student_name': row.student.full_name,
        'teacher_id': row.teacher_id,
        'teacher_name': row.teacher.full_name,
        'study_group_id': row.study_group_id,
        'group_name': group_name,
        'score_date': row.score_date,
        'score': float(row.score),
        'max_score': WEEKLY_SCORE_MAX,
        'tier': quiz_average_score_tier(pct),
        'comment': row.comment,
        'updated_at': row.updated_at,
        'date': row.score_date,
    }


def today():
    return timezone.localdate()


def parse_score_date(raw_value):
    """The scored day: the given ISO date, today when missing/invalid, never in the future."""
    if isinstance(raw_value, date):
        parsed = raw_value
    else:
        parsed = parse_date(str(raw_value).strip()) if raw_value else None
    current = today()
    if parsed is None or parsed > current:
        return current
    return parsed


def build_score_day_calendar(score_date=None):
    day = parse_score_date(score_date)
    current = today()
    return {
        'date': day,
        'is_today': day == current,
        'max_date': current,
        'prev_day': (day - timedelta(days=1)).isoformat(),
        'next_day': (day + timedelta(days=1)).isoformat() if day < current else '',
    }


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


def _row_key(student_id, group_id):
    return f"{student_id}_{group_id if group_id else NO_GROUP_KEY}"


def _expand_weekly_score_rows(students):
    """One grading card per student-group membership; one card for a student without a group."""
    rows = []
    for student in students:
        group_ids = student.get('group_ids') or []
        group_names = student.get('group_names') or []
        base = {
            key: value
            for key, value in student.items()
            if key not in ('group_ids', 'group_names')
        }
        if not group_ids:
            rows.append({
                **base,
                'row_key': _row_key(student['id'], None),
                'group_id': None,
                'group_name': '',
                'group_ids': [],
                'group_names': [],
            })
            continue
        for group_id, group_name in zip(group_ids, group_names):
            rows.append({
                **base,
                'row_key': _row_key(student['id'], group_id),
                'group_id': group_id,
                'group_name': group_name,
                'group_ids': [group_id],
                'group_names': [group_name],
            })
    return rows


def _build_group_tabs_for_teacher(teacher_id, all_rows):
    students_by_group = {}
    for row in all_rows:
        group_id = row.get('group_id')
        if group_id:
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
    no_group_rows = [row for row in all_rows if not row.get('group_id')]
    if no_group_rows:
        groups.append({
            'id': NO_GROUP_KEY,
            'name': _('Qrupsuz'),
            'student_count': len(no_group_rows),
            'scored_count': sum(1 for row in no_group_rows if row.get('score') is not None),
        })
    return groups


def _weekly_score_lookup(teacher_id, score_date, student_ids, group_ids):
    """(student_id, group_id or None) -> score row of that day."""
    if not student_ids:
        return {}
    return {
        (row.student_id, row.study_group_id): row
        for row in WeeklyStudentScore.objects.filter(
            teacher_id=teacher_id,
            score_date=score_date,
            student_id__in=student_ids,
        ).select_related('student', 'teacher', 'study_group')
        if row.study_group_id is None or row.study_group_id in group_ids
    }


@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_teacher_weekly_score_board(teacher_id, score_date_iso):
    score_date = parse_score_date(score_date_iso)
    students = get_teacher_weekly_score_students(teacher_id)
    if not students:
        calendar = build_score_day_calendar(score_date)
        return {
            'calendar': calendar,
            'rows': [],
            'groups': [],
            'scored_count': 0,
            'student_count': 0,
            'progress_percent': 0,
        }

    expanded_rows = _expand_weekly_score_rows(students)
    student_ids = {row['id'] for row in expanded_rows}
    group_ids = {row['group_id'] for row in expanded_rows if row['group_id']}
    existing = _weekly_score_lookup(teacher_id, score_date, student_ids, group_ids)

    rows = []
    scored_count = 0
    for student_row in expanded_rows:
        record = existing.get((student_row['id'], student_row['group_id']))
        if record:
            scored_count += 1
        rows.append({
            **student_row,
            'weekly_score_id': record.pk if record else None,
            'is_locked': record is not None,
            'score': float(record.score) if record else None,
            'comment': record.comment if record else '',
            'updated_at': record.updated_at if record else None,
        })

    student_count = len(rows)
    return {
        'calendar': build_score_day_calendar(score_date),
        'rows': rows,
        'groups': _build_group_tabs_for_teacher(teacher_id, rows),
        'scored_count': scored_count,
        'student_count': student_count,
        'progress_percent': round(100 * scored_count / student_count) if student_count else 0,
    }


def build_teacher_weekly_score_view(teacher_id, score_date_iso=None, group_id=None):
    score_date = parse_score_date(score_date_iso)
    board = get_teacher_weekly_score_board(teacher_id, score_date.isoformat())
    active_group = str(group_id or 'all')
    rows = board['rows']
    if active_group == NO_GROUP_KEY:
        rows = [row for row in rows if not row.get('group_id')]
    elif active_group != 'all':
        try:
            selected_group_id = int(active_group)
        except (TypeError, ValueError):
            selected_group_id = None
        if selected_group_id:
            rows = [row for row in rows if row.get('group_id') == selected_group_id]

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
        'day_value': board['calendar']['date'].isoformat(),
        'has_editable_rows': editable_count > 0,
        'has_any_editable_rows': total_editable_count > 0,
    }


@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_student_weekly_scores(student_id):
    qs = (
        WeeklyStudentScore.objects.filter(student_id=student_id)
        .select_related('student', 'teacher', 'teacher__user', 'study_group')
        .order_by('-score_date', '-updated_at', '-id')[:52]
    )
    return [serialize_weekly_score(row) for row in qs]


@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_teacher_weekly_scores_list(teacher_id):
    qs = (
        WeeklyStudentScore.objects.filter(teacher_id=teacher_id)
        .select_related('student', 'teacher', 'teacher__user', 'student__user', 'study_group')
        .order_by('-score_date', '-updated_at', '-id')[:200]
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
        .select_related('student', 'teacher', 'teacher__user', 'study_group')
        .order_by('-score_date', '-updated_at', '-id')[:52]
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


def _existing_scored_pairs(teacher_id, score_date, rows):
    if not rows:
        return set()
    student_ids = {row['id'] for row in rows}
    return set(
        WeeklyStudentScore.objects.filter(
            teacher_id=teacher_id,
            score_date=score_date,
            student_id__in=student_ids,
        ).values_list('student_id', 'study_group_id')
    )


def rows_open_for_scoring(rows, *, teacher_id, score_date):
    """Return board rows that may still receive a score for that day."""
    if not rows:
        return []
    score_date = parse_score_date(score_date)
    scored_pairs = _existing_scored_pairs(teacher_id, score_date, rows)
    return [
        row for row in rows
        if (row['id'], row['group_id']) not in scored_pairs
    ]


def _resolve_teacher_group(teacher_id, student_id, group_id):
    return StudyGroup.objects.filter(
        pk=group_id,
        teacher_id=teacher_id,
        students__pk=student_id,
    ).first()


def _student_has_teacher_group(teacher_id, student_id):
    return StudyGroup.objects.filter(
        teacher_id=teacher_id,
        is_active=True,
        is_main_register=False,
        students__pk=student_id,
    ).exists()


def save_teacher_weekly_scores(*, teacher_id, score_date, entries):
    """
    Create daily scores for teacher-owned students (one per student per group per day).

    ``score_date`` is today or an earlier day the teacher picked; a future day is refused.
    Existing scores cannot be changed or removed through the teacher portal.
    """
    if isinstance(score_date, date):
        requested = score_date
    else:
        requested = parse_date(str(score_date or '').strip())
    if requested is None:
        raise ValidationError(_('Choose a valid day.'))
    if requested > today():
        raise ValidationError(_('You cannot score a future day.'))
    score_date = requested
    saved = 0
    skipped = 0
    errors = []

    with transaction.atomic():
        for entry in entries:
            student_id = entry.get('student_id')
            group_id = entry.get('group_id') or None
            if not student_id:
                continue
            if not get_teacher_student(teacher_id, student_id):
                errors.append(_('You cannot score this student.'))
                continue
            if group_id is None:
                # a score without a group is for a student who has none with this teacher
                if _student_has_teacher_group(teacher_id, student_id):
                    errors.append(_('You cannot score this student for the selected group.'))
                    continue
            elif not _resolve_teacher_group(teacher_id, student_id, group_id):
                errors.append(_('You cannot score this student for the selected group.'))
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
                study_group_id=group_id,
                score_date=score_date,
            ).first()

            if existing:
                if score_value is None:
                    skipped += 1
                    continue
                if _entry_touches_locked_score(existing, score_value, comment):
                    errors.append(_('This score is already saved and cannot be changed.'))
                else:
                    skipped += 1
                continue

            if score_value is None:
                continue

            record = WeeklyStudentScore(
                teacher_id=teacher_id,
                student_id=student_id,
                study_group_id=group_id,
                score_date=score_date,
                score=score_value,
                comment=comment,
            )
            try:
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


def parse_weekly_score_post(request_post, rows):
    entries = []
    for row in rows:
        row_key = row['row_key']
        entries.append({
            'student_id': row['id'],
            'group_id': row['group_id'],
            'score': request_post.get(f'score_{row_key}', ''),
            'comment': request_post.get(f'comment_{row_key}', ''),
        })
    return entries


# Backwards-compatible alias for callers/tests.
student_ids_open_for_scoring = rows_open_for_scoring
