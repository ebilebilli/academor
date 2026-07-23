"""
Cached reads and serializers for the student / teacher / parent portal.

Register new @cached_query consumers in portals.signals when models change.
"""
from django.db.models import Count, F, Prefetch, Q
from django.urls import reverse

from portals.utils.cache_utils import cached_page_data, cached_query
from portals.models import (
    Attendance,
    Lesson,
    ParentProfile,
    CustomerProfile,
    Quiz,
    QuizCategory,
    QuizQuestion,
    QuizResult,
    Schedule,
    Score,
    StudentProfile,
    StudyGroup,
    TeacherProfile,
    VideoRecord,
)
from portals.utils.portal_services import expand_course_types_to_service_slugs
from portals.utils.quiz_category_services import (
    category_has_portal_code,
    quiz_categories_for_portal_codes,
    quiz_category_primary_portal_code,
    quiz_category_slugs_for_portal_codes,
)
from portals.utils.student_courses import get_student_course_type_codes
from portals.utils.teacher_courses import get_teacher_course_type_codes, teacher_groups_queryset


def teacher_attendance_queryset(teacher_id):
    """Attendance for a teacher's groups without courses M2M join (avoids duplicate rows)."""
    groups = teacher_groups_queryset(teacher_id)
    if not groups.exists():
        return Attendance.objects.none()
    return Attendance.objects.filter(schedule__group__in=groups)


# ---------------------------------------------------------------------------
# Role helpers (not cached — tied to request.user)
# ---------------------------------------------------------------------------

_ROLE_CACHE_ATTR = '_portal_role_cache'


def get_portal_role(user):
    if not user.is_authenticated:
        return None
    # Called several times per request (mixins, context processors, views);
    # memoize on the user instance, which lives for one request.
    cached = getattr(user, _ROLE_CACHE_ATTR, '')
    if cached != '':
        return cached
    if TeacherProfile.objects.filter(user_id=user.pk).exists():
        role = 'teacher'
    elif StudentProfile.objects.filter(user_id=user.pk).exists():
        role = 'student'
    elif ParentProfile.objects.filter(user_id=user.pk).exists():
        role = 'parent'
    elif CustomerProfile.objects.filter(user_id=user.pk).exists():
        role = 'customer'
    else:
        role = None
    try:
        setattr(user, _ROLE_CACHE_ATTR, role)
    except AttributeError:
        pass
    return role


def get_teacher_profile(user):
    if not user.is_authenticated:
        return None
    return (
        TeacherProfile.objects.select_related('user')
        .filter(user_id=user.pk)
        .first()
    )


def get_student_profile(user):
    if not user.is_authenticated:
        return None
    return (
        StudentProfile.objects.select_related('user')
        .prefetch_related('groups')
        .filter(user_id=user.pk)
        .first()
    )


def get_parent_profile(user):
    if not user.is_authenticated:
        return None
    return (
        ParentProfile.objects.select_related('user')
        .prefetch_related('students')
        .filter(user_id=user.pk)
        .first()
    )


def get_customer_profile(user):
    if not user.is_authenticated:
        return None
    return (
        CustomerProfile.objects.select_related('user', 'teacher', 'teacher__user')
        .filter(user_id=user.pk)
        .first()
    )


def serialize_customer(profile):
    return {
        'id': profile.pk,
        'username': _profile_username(profile),
        'phone': profile.phone or '',
        'mock_credits': profile.mock_credits,
        'ielts_mock_credits': profile.ielts_mock_credits,
        'sat_mock_credits': profile.sat_mock_credits,
        'teacher_id': profile.teacher_id,
        'teacher_name': profile.teacher.full_name if profile.teacher_id else '',
        'full_name': profile.full_name,
    }


# ---------------------------------------------------------------------------
# Serializers
# ---------------------------------------------------------------------------

def _profile_photo_url(image_field):
    if not image_field:
        return None
    try:
        return image_field.url
    except (ValueError, AttributeError):
        return None


def _profile_username(profile):
    if profile.user_id:
        return profile.user.get_username()
    return ''


def serialize_teacher(profile):
    labels = profile.get_course_type_labels()
    username = _profile_username(profile)
    return {
        'id': profile.pk,
        'username': username,
        'full_name': username,
        'specialization': profile.specialization or ', '.join(labels),
        'course_type_codes': profile.get_course_type_codes(),
        'course_type_labels': labels,
        'bio': profile.bio,
        'phone': profile.phone,
        'photo_url': _profile_photo_url(profile.profile_image),
        'instagram': profile.instagram,
        'facebook': profile.facebook,
        'linkedin': profile.linkedin,
        'youtube': profile.youtube,
    }


def serialize_student(profile):
    username = _profile_username(profile)
    return {
        'id': profile.pk,
        'username': username,
        'full_name': username,
        'phone': profile.phone,
        'bio': profile.bio,
        'enrollment_date': profile.enrollment_date,
        'photo_url': _profile_photo_url(profile.profile_image),
        'group_ids': list(profile.groups.values_list('id', flat=True)),
        'instagram': profile.instagram,
        'facebook': profile.facebook,
        'linkedin': profile.linkedin,
        'youtube': profile.youtube,
    }


def serialize_parent(profile):
    username = _profile_username(profile)
    students = [
        serialize_student(student)
        for student in profile.students.select_related('user').order_by('user__username', 'id')
    ]
    return {
        'id': profile.pk,
        'username': username,
        'full_name': username,
        'phone': profile.phone,
        'students': students,
    }


def serialize_group(group):
    from portals.utils.group_services import (
        study_group_portal_display_labels,
        study_group_teaching_portal_codes,
    )

    labels = study_group_portal_display_labels(group)
    codes = study_group_teaching_portal_codes(group)
    primary_label = ', '.join(labels) if labels else '—'
    annotated_count = getattr(group, 'student_count', None)
    if isinstance(annotated_count, int):
        student_count = annotated_count
    elif getattr(group, '_prefetched_objects_cache', None) and 'students' in group._prefetched_objects_cache:
        student_count = len(group.students.all())
    elif hasattr(group, 'students'):
        student_count = group.students.count()
    else:
        student_count = 0
    return {
        'id': group.pk,
        'name': group.name,
        'course_type': codes[0] if codes else '',
        'course_type_codes': codes,
        'course_type_labels': labels,
        'course_type_label': primary_label,
        'start_date': group.start_date,
        'max_students': group.max_students,
        'is_active': group.is_active,
        'teacher_id': group.teacher_id,
        'teacher_name': group.teacher.full_name if group.teacher_id else '',
        'student_count': student_count,
    }


def serialize_schedule(schedule):
    from datetime import timedelta

    from django.utils import timezone

    from portals.utils.teacher_schedule import schedule_visible_on_date

    today = timezone.localdate()
    week_start = today - timedelta(days=today.weekday())
    session_date = week_start + timedelta(days=schedule.weekday)
    if not schedule_visible_on_date(schedule, session_date):
        session_date = None
    return {
        'id': schedule.pk,
        'group_id': schedule.group_id,
        'group_name': schedule.group.name,
        'weekday': schedule.weekday,
        'weekday_label': schedule.get_weekday_display(),
        'start_time': schedule.start_time,
        'duration_min': schedule.duration_min,
        'room_or_link': schedule.room_or_link,
        'effective_from': schedule.effective_from,
        'session_date_this_week': session_date,
        'session_date_iso': session_date.isoformat() if session_date else '',
    }


def serialize_lesson(lesson):
    from portals.utils.lesson_media import build_lesson_media
    from portals.utils.group_services import lesson_effective_subject
    from portals.utils.portal_services import resolve_course_type_label

    media = build_lesson_media(lesson)
    subject = lesson_effective_subject(lesson)
    return {
        'id': lesson.pk,
        'name': lesson.display_name,
        'description': lesson.description,
        'subject': subject,
        'subject_label': resolve_course_type_label(subject) if subject else '',
        'category_id': lesson.category_id,
        'category_name': lesson.category.name if lesson.category_id else '',
        'group_id': lesson.group_id,
        'group_name': lesson.group.name,
        'lesson_date': lesson.lesson_date,
        'created_at': lesson.created_at,
        **media,
    }


def serialize_classroom(classroom):
    from portals.utils.media_cache_bust import media_url
    from portals.utils.group_services import (
        study_group_portal_display_labels,
        study_group_teaching_portal_codes,
    )

    pdf_url = media_url(classroom.pdf_file) if classroom.pdf_file else ''
    group = getattr(classroom, 'group', None)
    if group and group.pk:
        service_slugs = study_group_teaching_portal_codes(group)
        service_labels = study_group_portal_display_labels(group)
    else:
        service_slugs = classroom.get_service_slugs()
        service_labels = classroom.get_service_labels()
    return {
        'id': classroom.pk,
        'name': classroom.display_name,
        'description': classroom.description or '',
        'pdf_url': pdf_url,
        'has_pdf': bool(pdf_url),
        'created_at': classroom.created_at,
        'group_id': classroom.group_id,
        'group_name': group.name if group else '',
        'teacher_id': classroom.teacher_id,
        'services': service_slugs,
        'service_labels': service_labels,
        'services_csv': ','.join(service_slugs),
        'primary_service': service_slugs[0] if service_slugs else '',
        'primary_service_label': service_labels[0] if service_labels else '',
    }


def build_classroom_group_tabs(classrooms):
    from django.utils.translation import gettext as _

    counts = {}
    for room in classrooms:
        group_id = room.get('group_id')
        if group_id:
            counts[group_id] = counts.get(group_id, 0) + 1
    tabs = [{
        'code': 'all',
        'label': _('All groups'),
        'count': len(classrooms),
    }]
    seen = {}
    for room in classrooms:
        group_id = room.get('group_id')
        if not group_id or group_id in seen:
            continue
        seen[group_id] = room.get('group_name') or str(group_id)
    for group_id in sorted(seen, key=lambda pk: seen[pk].lower()):
        tabs.append({
            'code': str(group_id),
            'label': seen[group_id],
            'count': counts.get(group_id, 0),
        })
    return tabs


def build_classroom_service_tabs(classrooms):
    from django.utils.translation import gettext as _

    from portals.utils.portal_services import get_active_services_queryset, localized_service_name

    label_map = {
        service.slug: localized_service_name(service)
        for service in get_active_services_queryset()
        if service.slug
    }
    counts = {}
    for room in classrooms:
        for slug in room.get('services') or []:
            counts[slug] = counts.get(slug, 0) + 1
    tabs = [{
        'code': 'all',
        'label': _('All services'),
        'count': len(classrooms),
    }]
    for slug in sorted(counts):
        tabs.append({
            'code': slug,
            'label': label_map.get(slug, slug),
            'count': counts[slug],
        })
    return tabs


def _classroom_queryset():
    from portals.models import Classroom

    return (
        Classroom.objects.select_related('group', 'teacher')
        .prefetch_related('services')
        .order_by('name', 'id')
    )


def get_teacher_classrooms(teacher_id):
    from portals.utils.student_courses import classroom_visible_to_teacher
    from portals.utils.teacher_courses import teacher_groups_queryset

    group_ids = list(
        teacher_groups_queryset(teacher_id, active_only=True).values_list('pk', flat=True)
    )
    qs = _classroom_queryset().filter(group_id__in=group_ids)
    visible = [row for row in qs if classroom_visible_to_teacher(row, teacher_id)]
    return [serialize_classroom(row) for row in visible]


def get_student_classrooms(student_id):
    from portals.models import StudyGroup
    from portals.utils.student_courses import classroom_visible_to_student

    group_ids = list(
        StudyGroup.objects.filter(
            students__pk=student_id,
            is_active=True,
        ).values_list('pk', flat=True).distinct()
    )
    if not group_ids:
        return []
    group_id_set = set(group_ids)
    qs = _classroom_queryset().filter(group_id__in=group_ids)
    visible = [
        row for row in qs
        if classroom_visible_to_student(row, student_id, student_group_ids=group_id_set)
    ]
    return [serialize_classroom(row) for row in visible]


def get_parent_classrooms(parent_id, student_id=None):
    if student_id:
        return get_student_classrooms(student_id)

    from portals.models import ParentProfile

    student_ids = list(
        ParentProfile.objects.filter(pk=parent_id)
        .values_list('students__pk', flat=True)
        .distinct()
    )
    classrooms = []
    seen = set()
    for sid in student_ids:
        if not sid:
            continue
        for row in get_student_classrooms(sid):
            if row['id'] not in seen:
                seen.add(row['id'])
                classrooms.append(row)
    return classrooms


def get_classroom_detail(pk, *, role, profile_id):
    from portals.models import Classroom
    from portals.utils.student_courses import (
        classroom_visible_to_parent,
        classroom_visible_to_student,
        classroom_visible_to_teacher,
    )

    row = _classroom_queryset().filter(pk=pk).first()
    if not row:
        return None
    if role == 'teacher' and not classroom_visible_to_teacher(row, profile_id):
        return None
    if role == 'student' and not classroom_visible_to_student(row, profile_id):
        return None
    if role == 'parent' and not classroom_visible_to_parent(row, profile_id):
        return None
    return serialize_classroom(row)


def get_lesson_detail(lesson):
    if not lesson:
        return None
    data = serialize_lesson(lesson)
    teacher = getattr(lesson, 'teacher', None)
    data['teacher_name'] = teacher.full_name if teacher else ''
    return data


def get_student_lesson(student_id, lesson_id):
    group_ids = get_student_group_ids(student_id)
    if not group_ids:
        return None
    return (
        Lesson.objects.filter(
            pk=lesson_id,
            group_id__in=group_ids,
            teacher_id=F('group__teacher_id'),
        )
        .select_related('group', 'teacher')
        .prefetch_related('attachments')
        .first()
    )


def serialize_lesson_homework(homework):
    from portals.utils.media_cache_bust import media_url
    from portals.utils.group_services import lesson_effective_subject

    file_url = media_url(homework.file) if homework.file else None
    student = getattr(homework, 'student', None)
    lesson = getattr(homework, 'lesson', None)
    subject = ''
    if lesson:
        subject = lesson_effective_subject(lesson) or (lesson.subject or '')
    return {
        'id': homework.pk,
        'lesson_id': homework.lesson_id,
        'lesson_name': lesson.display_name if lesson else '',
        'lesson_date': lesson.lesson_date if lesson else None,
        'subject': subject,
        'category_id': lesson.category_id if lesson else None,
        'group_id': lesson.group_id if lesson else None,
        'group_name': lesson.group.name if lesson and lesson.group_id else '',
        'student_id': homework.student_id,
        'student_name': student.full_name if student else '',
        'text': homework.text or '',
        'file_url': file_url,
        'original_filename': homework.original_filename or '',
        'file_kind': homework.file_kind or '',
        'file_kind_label': homework.get_file_kind_display() if homework.file_kind else '',
        'has_file': bool(file_url),
        'has_text': bool((homework.text or '').strip()),
        'submitted_at': homework.submitted_at,
        'created_at': homework.created_at,
    }


def get_student_lesson_homework(student_id, lesson_id):
    from portals.models import LessonHomework

    return (
        LessonHomework.objects.filter(student_id=student_id, lesson_id=lesson_id)
        .select_related('student', 'student__user', 'lesson', 'lesson__group')
        .first()
    )


def get_student_lesson_homeworks(student_id):
    from portals.models import LessonHomework

    qs = (
        LessonHomework.objects.filter(student_id=student_id)
        .select_related('student', 'student__user', 'lesson', 'lesson__group')
        .order_by('-submitted_at', 'id')
    )
    return [serialize_lesson_homework(row) for row in qs]


def get_student_homework(student_id, homework_id):
    from portals.models import LessonHomework

    return (
        LessonHomework.objects.filter(pk=homework_id, student_id=student_id)
        .select_related('student', 'student__user', 'lesson', 'lesson__group', 'lesson__teacher')
        .first()
    )


def get_lesson_homeworks_for_teacher(lesson):
    from portals.models import LessonHomework

    if not lesson:
        return []
    qs = (
        LessonHomework.objects.filter(lesson_id=lesson.pk, student__groups=lesson.group_id)
        .select_related('student', 'student__user', 'lesson', 'lesson__group')
        .order_by('-submitted_at', 'id')
        .distinct()
    )
    return [serialize_lesson_homework(row) for row in qs]


def build_lesson_subject_tabs(lessons, allowed_codes=None):
    from django.utils.translation import gettext as _

    from portals.utils.portal_services import get_course_type_label_map, normalize_portal_course_type

    labels = get_course_type_label_map()
    allowed = {code for code in (allowed_codes or []) if code}
    counts = {}
    visible_lessons = 0
    for lesson in lessons:
        code = normalize_portal_course_type(lesson.get('subject') or '') or (lesson.get('subject') or '')
        if not code:
            continue
        if allowed and code not in allowed:
            continue
        counts[code] = counts.get(code, 0) + 1
        visible_lessons += 1
    tabs = [{
        'code': 'all',
        'label': _('All topics'),
        'count': visible_lessons if allowed else len(lessons),
    }]
    for code in sorted(counts):
        tabs.append({
            'code': code,
            'label': labels.get(code, code),
            'count': counts[code],
        })
    return tabs


def build_teacher_lesson_group_tabs(teacher_id, lessons):
    """Group filter chips for teacher lesson lists (scoped to each group's linked courses)."""
    from portals.utils.group_services import (
        study_group_portal_display_labels,
        study_group_teaching_portal_codes,
    )

    groups = []
    for group in (
        teacher_groups_queryset(teacher_id, active_only=True)
        .prefetch_related('courses')
        .order_by('name')
    ):
        service_codes = study_group_teaching_portal_codes(group)
        service_labels = study_group_portal_display_labels(group)
        groups.append({
            'id': group.pk,
            'name': group.name,
            'total_count': sum(1 for lesson in lessons if lesson.get('group_id') == group.pk),
            'service_codes': service_codes,
            'service_codes_csv': ','.join(service_codes),
            'service_label': ', '.join(service_labels) if service_labels else '',
        })
    return groups


def lesson_subject_codes_for_group(group_meta):
    return list(group_meta.get('service_codes') or [])


LESSON_PERIOD_CHOICES = ('all', 'week', 'month', 'year')
LESSON_PERIOD_TAB_ORDER = ('week', 'month', 'year', 'all')


def _normalize_lesson_date(value):
    if not value:
        return None
    if hasattr(value, 'date') and callable(value.date):
        return value.date()
    return value


def build_lesson_period_tabs(lessons):
    """Time-range tabs for lesson lists (client-side filtering by lesson_date)."""
    from datetime import timedelta

    from django.utils import timezone
    from django.utils.translation import gettext as _

    today = timezone.localdate()
    thresholds = {
        'week': today - timedelta(days=7),
        'month': today - timedelta(days=30),
        'year': today - timedelta(days=365),
    }
    labels = {
        'all': _('Hamısı'),
        'week': _('Bu həftə'),
        'month': _('Bu ay'),
        'year': _('Bu il'),
    }
    counts = {code: 0 for code in LESSON_PERIOD_CHOICES}
    counts['all'] = len(lessons)
    for lesson in lessons:
        lesson_date = _normalize_lesson_date(lesson.get('lesson_date'))
        if not lesson_date:
            continue
        for code, start in thresholds.items():
            if lesson_date >= start:
                counts[code] += 1
    return [
        {'code': code, 'label': labels[code], 'count': counts[code]}
        for code in LESSON_PERIOD_TAB_ORDER
    ]


def _normalize_score_date(value):
    return _normalize_lesson_date(value)


def build_score_period_tabs(*score_lists):
    """Time-range tabs for score lists (client-side filtering by score date)."""
    from datetime import timedelta

    from django.utils import timezone
    from django.utils.translation import gettext as _

    scores = []
    for rows in score_lists:
        scores.extend(rows or [])

    today = timezone.localdate()
    thresholds = {
        'week': today - timedelta(days=7),
        'month': today - timedelta(days=30),
        'year': today - timedelta(days=365),
    }
    labels = {
        'all': _('Hamısı'),
        'week': _('Bu həftə'),
        'month': _('Bu ay'),
        'year': _('Bu il'),
    }
    counts = {code: 0 for code in LESSON_PERIOD_CHOICES}
    counts['all'] = len(scores)
    for row in scores:
        score_date = _normalize_score_date(row.get('date'))
        if not score_date:
            continue
        for code, start in thresholds.items():
            if score_date >= start:
                counts[code] += 1
    return [
        {'code': code, 'label': labels[code], 'count': counts[code]}
        for code in LESSON_PERIOD_TAB_ORDER
    ]


def resolve_score_group_param(request, groups):
    if not groups:
        return None
    default = str(groups[0]['id'])
    raw = (request.GET.get('group') or '').strip()
    if not raw:
        return default
    valid = {str(group['id']) for group in groups}
    return raw if raw in valid else default


def prepare_student_scores_with_groups(student_id, quiz_scores, weekly_scores):
    """Attach group_ids to student score rows and build group filter tabs."""
    from portals.utils.student_groups import build_student_group_maps

    groups, by_teacher, by_service = build_student_group_maps(student_id)

    def enrich_quiz(row):
        service = row.get('course_type') or ''
        return {**row, 'group_ids': by_service.get(service, [])}

    def enrich_weekly(row):
        group_id = row.get('study_group_id')
        if group_id:
            return {**row, 'group_ids': [group_id]}
        teacher_id = row.get('teacher_id')
        return {**row, 'group_ids': by_teacher.get(teacher_id, [])}

    quiz_enriched = [enrich_quiz(row) for row in (quiz_scores or [])]
    weekly_enriched = [enrich_weekly(row) for row in (weekly_scores or [])]

    score_groups = []
    for group in groups:
        group_id = group['id']
        quiz_count = sum(1 for row in quiz_enriched if group_id in row['group_ids'])
        weekly_count = sum(1 for row in weekly_enriched if group_id in row['group_ids'])
        score_groups.append({
            'id': group_id,
            'name': group['name'],
            'quiz_count': quiz_count,
            'weekly_count': weekly_count,
            'total_count': quiz_count + weekly_count,
        })

    return {
        'quiz_scores': quiz_enriched,
        'weekly_scores': weekly_enriched,
        'score_groups': score_groups if len(score_groups) > 1 else [],
    }


def prepare_teacher_scores_with_groups(teacher_id, quiz_scores, weekly_scores):
    """Attach group_ids to score rows and build group filter tabs for teacher results."""
    student_groups = {
        row['id']: row.get('group_ids', [])
        for row in get_teacher_weekly_score_students(teacher_id)
    }

    def enrich(rows):
        return [
            {
                **row,
                'group_ids': (
                    [row['study_group_id']]
                    if row.get('study_group_id')
                    else student_groups.get(row.get('student_id'), [])
                ),
            }
            for row in rows
        ]

    quiz_enriched = enrich(quiz_scores or [])
    weekly_enriched = enrich(weekly_scores or [])

    groups = []
    for group in teacher_groups_queryset(teacher_id, active_only=True).order_by('-id'):
        quiz_count = sum(1 for row in quiz_enriched if group.pk in row['group_ids'])
        weekly_count = sum(1 for row in weekly_enriched if group.pk in row['group_ids'])
        groups.append({
            'id': group.pk,
            'name': group.name,
            'quiz_count': quiz_count,
            'weekly_count': weekly_count,
            'total_count': quiz_count + weekly_count,
        })

    return {
        'quiz_scores': quiz_enriched,
        'weekly_scores': weekly_enriched,
        'score_groups': groups,
        'total_score_count': len(quiz_enriched) + len(weekly_enriched),
    }


def build_lesson_category_tabs(lessons):
    """Category label tabs for lesson lists (client-side filtering by teacher-defined names)."""
    from django.utils.translation import gettext as _

    counts = {}
    uncategorized = 0
    for lesson in lessons:
        category_id = lesson.get('category_id')
        if not category_id:
            uncategorized += 1
            continue
        key = str(category_id)
        if key not in counts:
            counts[key] = {
                'id': category_id,
                'label': lesson.get('category_name') or _('Uncategorized'),
                'count': 0,
            }
        counts[key]['count'] += 1
    if not counts and not uncategorized:
        return []
    tabs = [{
        'code': 'all',
        'label': _('All categories'),
        'count': len(lessons),
    }]
    for key in sorted(counts, key=lambda item: counts[item]['label'].lower()):
        row = counts[key]
        tabs.append({
            'code': row['id'],
            'label': row['label'],
            'count': row['count'],
        })
    if uncategorized:
        tabs.append({
            'code': 'none',
            'label': _('Uncategorized'),
            'count': uncategorized,
        })
    return tabs


def serialize_video_record(record):
    return {
        'id': record.pk,
        'title': record.title,
        'youtube_url': record.youtube_url,
        'lesson_date': record.lesson_date,
        'description': record.description,
        'group_id': record.group_id,
    }


def serialize_attendance(row):
    schedule = row.schedule
    return {
        'id': row.pk,
        'student_id': row.student_id,
        'student_name': row.student.full_name,
        'schedule_id': row.schedule_id,
        'group_id': schedule.group_id,
        'group_name': schedule.group.name,
        'weekday_label': schedule.get_weekday_display(),
        'start_time': schedule.start_time,
        'session_date': row.session_date,
        'status': row.status,
        'status_label': row.get_status_display(),
        'note': row.note,
        'marked_at': row.marked_at,
    }


def serialize_score(row):
    return {
        'id': f"score-{row.pk}",
        'source': 'score',
        'student_id': row.student_id,
        'student_name': row.student.full_name,
        'score_type': row.score_type,
        'score_type_label': row.get_score_type_display(),
        'value': row.value,
        'max_value': row.max_value,
        'date': row.date,
        'comment': row.comment,
        'lesson_id': row.lesson_id,
        'lesson_title': row.lesson.display_name if row.lesson_id else '',
        'quiz_topic': '',
        'is_pending_review': False,
        'grading_mode_label': '',
    }


def _answerable_question_counts(quiz_rows):
    """Typed (reading/listening/speaking) answerable-question counts, one
    query per quiz kind instead of one per quiz (N+1 in list pages)."""
    from portals.models import ListeningQuestion, ReadingQuestion, SpeakingQuestion

    counts = {}
    reading_ids = [q.pk for q in quiz_rows if q.is_reading]
    listening_ids = [q.pk for q in quiz_rows if q.is_listening]
    speaking_ids = [q.pk for q in quiz_rows if q.is_speaking]
    for quiz_id in reading_ids + listening_ids + speaking_ids:
        counts[quiz_id] = 0
    if reading_ids:
        rows = ReadingQuestion.objects.filter(
            passage__quiz_id__in=reading_ids,
        ).select_related('passage', 'group')
        for question in rows:
            if question.is_answerable:
                counts[question.passage.quiz_id] += 1
    if listening_ids:
        rows = ListeningQuestion.objects.filter(
            audio__quiz_id__in=listening_ids,
        ).select_related('audio')
        for question in rows:
            if question.is_answerable:
                counts[question.audio.quiz_id] += 1
    if speaking_ids:
        rows = SpeakingQuestion.objects.filter(
            part__quiz_id__in=speaking_ids,
        ).select_related('part')
        for question in rows:
            if question.is_answerable:
                counts[question.part.quiz_id] += 1
    return counts


def serialize_quiz(quiz, *, question_counts=None):
    from portals.utils.portal_services import resolve_course_type_label
    from portals.utils.student_courses import get_quiz_service_code

    code = get_quiz_service_code(quiz)
    label = resolve_course_type_label(code) if code else ''
    category = getattr(quiz, 'category', None)
    inline_count = quiz.questions.count() if hasattr(quiz, 'questions') else 0
    question_count = inline_count
    if quiz.is_listening or quiz.is_reading or quiz.is_speaking:
        if question_counts is not None:
            typed_count = question_counts.get(quiz.pk, 0)
        elif quiz.is_listening:
            from portals.utils.quiz_listening import get_listening_questions_for_quiz

            typed_count = len(get_listening_questions_for_quiz(quiz))
        elif quiz.is_reading:
            from portals.utils.quiz_reading import get_reading_questions_for_quiz

            typed_count = len(get_reading_questions_for_quiz(quiz))
        else:
            from portals.utils.quiz_speaking import get_speaking_questions_for_quiz

            typed_count = len(get_speaking_questions_for_quiz(quiz))
        question_count = typed_count or inline_count
    return {
        'id': quiz.pk,
        'topic': quiz.topic,
        'course_type': code,
        'course_types': [code] if code else [],
        'course_type_label': label,
        'category_id': quiz.category_id,
        'category_name': category.name if category else '',
        'created_at': quiz.created_at,
        'question_count': question_count,
        'is_listening': quiz.is_listening,
        'is_essay': quiz.is_essay,
        'is_speaking': quiz.is_speaking,
        'is_reading': quiz.is_reading,
        'is_manual_grading': quiz.is_manual_grading,
        'requires_teacher_review': quiz.requires_teacher_review,
        'uses_per_question_text_responses': quiz.uses_per_question_text_responses,
        'is_variant_quiz': quiz.is_variant_quiz,
        'grading_mode': quiz.grading_mode,
        'grading_mode_label': quiz.get_grading_mode_label(),
        'is_time_limited': quiz.is_time_limited,
        'time_limit_minutes': quiz.time_limit_minutes,
        'time_limit_seconds': quiz.time_limit_seconds,
    }


def serialize_quiz_category(category):
    from portals.utils.portal_services import resolve_course_type_label

    quiz_count = getattr(category, 'quiz_count', None)
    if quiz_count is None:
        quiz_count = category.quizzes.count()
    service_code = quiz_category_primary_portal_code(category)
    return {
        'id': category.pk,
        'name': category.name,
        'service': service_code,
        'service_label': resolve_course_type_label(service_code, lang='en') if service_code else '',
        'quiz_count': quiz_count,
    }


def build_quiz_service_tabs(categories):
    from django.utils.translation import gettext as _

    from portals.utils.portal_services import get_course_type_label_map

    labels = get_course_type_label_map(lang='en')
    counts = {}
    for category in categories:
        code = category.get('service') or ''
        if code:
            counts[code] = counts.get(code, 0) + 1
    tabs = [{
        'code': 'all',
        'label': _('All services'),
        'count': len(categories),
    }]
    for code in sorted(counts):
        tabs.append({
            'code': code,
            'label': labels.get(code, code),
            'count': counts[code],
        })
    return tabs


def teacher_can_access_quiz_category(teacher_id, category_id):
    row = QuizCategory.objects.filter(pk=category_id).prefetch_related('services').first()
    if not row:
        return False
    return category_has_portal_code(row, get_teacher_course_type_codes(teacher_id))


def student_can_access_quiz_category(student_id, category_id):
    row = QuizCategory.objects.filter(pk=category_id).prefetch_related('services').first()
    if not row:
        return False
    return category_has_portal_code(row, get_student_course_type_codes(student_id))


def _quiz_categories_with_counts(course_codes):
    """One aggregate query instead of loading every quiz per category.

    Visibility inside a category only depends on the category's service being
    in the caller's course codes, which the filter already guarantees.
    """
    return (
        quiz_categories_for_portal_codes(course_codes)
        .annotate(quiz_count=Count('quizzes', distinct=True))
        .filter(quiz_count__gt=0)
        .order_by('name', 'id')
    )


@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_teacher_quiz_categories(teacher_id):
    course_codes = get_teacher_course_type_codes(teacher_id)
    if not course_codes:
        return []
    return [serialize_quiz_category(row) for row in _quiz_categories_with_counts(course_codes)]


@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_student_quiz_categories(student_id):
    course_codes = get_student_course_type_codes(student_id)
    if not course_codes:
        return []
    return [serialize_quiz_category(row) for row in _quiz_categories_with_counts(course_codes)]


@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_teacher_quiz_category(teacher_id, category_id):
    if not teacher_can_access_quiz_category(teacher_id, category_id):
        return None
    row = QuizCategory.objects.filter(pk=category_id).first()
    if not row:
        return None
    visible = get_teacher_quizzes_for_category(teacher_id, category_id)
    if not visible:
        return None
    data = serialize_quiz_category(row)
    data['quiz_count'] = len(visible)
    return data


@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_student_quiz_category(student_id, category_id):
    if not student_can_access_quiz_category(student_id, category_id):
        return None
    row = QuizCategory.objects.filter(pk=category_id).first()
    if not row:
        return None
    visible = get_student_quizzes_for_category(student_id, category_id)
    if not visible:
        return None
    data = serialize_quiz_category(row)
    data['quiz_count'] = len(visible)
    return data


@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_teacher_quizzes_for_category(teacher_id, category_id):
    from portals.utils.student_courses import quiz_visible_to_teacher

    if not teacher_can_access_quiz_category(teacher_id, category_id):
        return []
    course_codes = get_teacher_course_type_codes(teacher_id)
    qs = (
        Quiz.objects.filter(
            category_id=category_id,
            category__services__slug__in=quiz_category_slugs_for_portal_codes(course_codes),
        )
        .select_related('category')
        .prefetch_related('questions')
        .distinct()
        .order_by('-created_at', 'id')
    )
    visible = [row for row in qs if quiz_visible_to_teacher(row, teacher_id)]
    question_counts = _answerable_question_counts(visible)
    return [serialize_quiz(row, question_counts=question_counts) for row in visible]


def _attach_quiz_attempt_flags(student_id, quizzes):
    from portals.utils.quiz_submit import get_student_quiz_attempt_meta

    if not quizzes:
        return quizzes
    attempt_meta = get_student_quiz_attempt_meta(student_id, [row['id'] for row in quizzes])
    enriched = []
    for row in quizzes:
        meta = attempt_meta.get(row['id'], {})
        has_attempt = row['id'] in attempt_meta
        is_reviewed = bool(meta.get('is_reviewed'))
        is_pending_review = has_attempt and bool(meta.get('is_pending_review'))
        enriched.append({
            **row,
            'has_attempt': has_attempt,
            'result_id': meta.get('result_id'),
            'is_reviewed': is_reviewed,
            'is_pending_review': is_pending_review,
            'can_take_manual_quiz': (
                not row.get('requires_teacher_review') or not has_attempt or is_reviewed
            ),
        })
    return enriched


def _attach_quiz_attempt_summaries(quizzes, quiz_results):
    if not quizzes:
        return quizzes

    results_by_quiz = {}
    for row in quiz_results or []:
        results_by_quiz.setdefault(row.get('quiz_id'), []).append(row)

    enriched = []
    for quiz in quizzes:
        rows = results_by_quiz.get(quiz.get('id'), [])
        graded_scores = [
            row.get('total_score')
            for row in rows
            if not row.get('is_pending_review') and row.get('total_score') is not None
        ]
        last_attempt = rows[0] if rows else None
        enriched.append({
            **quiz,
            'attempt_count': len(rows),
            'last_attempt_at': last_attempt.get('completed_at') if last_attempt else None,
            'last_score': last_attempt.get('total_score') if last_attempt and not last_attempt.get('is_pending_review') else None,
            'last_result_id': last_attempt.get('id') if last_attempt else None,
            'best_score': max(graded_scores) if graded_scores else None,
        })
    return enriched


def get_student_quizzes_for_category(student_id, category_id):
    from portals.utils.quiz_assignments import get_student_quiz_assignment_map
    from portals.utils.student_courses import student_quiz_enrollment_ok

    if not student_can_access_quiz_category(student_id, category_id):
        return []
    course_codes = get_student_course_type_codes(student_id)
    qs = (
        Quiz.objects.filter(
            category_id=category_id,
            category__services__slug__in=quiz_category_slugs_for_portal_codes(course_codes),
        )
        .select_related('category')
        .prefetch_related('questions')
        .distinct()
        .order_by('-created_at', 'id')
    )
    enrolled = [row for row in qs if student_quiz_enrollment_ok(student_id, row)]
    assignment_map = get_student_quiz_assignment_map(
        student_id,
        [row.pk for row in enrolled],
    )
    question_counts = _answerable_question_counts(enrolled)
    quizzes = []
    for row in enrolled:
        data = serialize_quiz(row, question_counts=question_counts)
        is_unlocked = bool(assignment_map.get(row.pk, False))
        data['is_unlocked'] = is_unlocked
        data['is_locked'] = not is_unlocked
        quizzes.append(data)
    quizzes = _attach_quiz_attempt_flags(student_id, quizzes)
    return _attach_quiz_attempt_summaries(
        quizzes,
        get_student_quiz_results(student_id, quiz_ids={quiz['id'] for quiz in quizzes}),
    )


def _quiz_correct_option_letter(question):
    options = question.answer_options or []
    correct = (question.correct_answer or '').strip()
    if correct and correct in options:
        return chr(97 + options.index(correct))
    index = question.correct_option_index
    if 0 <= index < len(options):
        return chr(97 + index)
    return ''


def serialize_quiz_question_for_student(question, *, student_answer: str = ''):
    media_file_url = ''
    if question.media_file:
        try:
            media_file_url = question.media_file.url
        except ValueError:
            media_file_url = ''

    return {
        'id': question.pk,
        'quiz_id': getattr(question, 'quiz_id', None),
        'prompt_type': question.prompt_type,
        'question': question.question,
        'media_file_url': media_file_url,
        'media_url': question.media_url,
        'answer_options': question.answer_options or [],
        'order': getattr(question, 'order', 0),
        'student_answer': student_answer,
    }


def serialize_quiz_question(question):
    media_file_url = ''
    if question.media_file:
        try:
            media_file_url = question.media_file.url
        except ValueError:
            media_file_url = ''

    return {
        'id': question.pk,
        'quiz_id': question.quiz_id,
        'prompt_type': question.prompt_type,
        'question': question.question,
        'media_file_url': media_file_url,
        'media_url': question.media_url,
        'answer_options': question.answer_options or [],
        'correct_option_index': question.correct_option_index,
        'correct_option_letter': _quiz_correct_option_letter(question),
        'correct_answer': question.correct_answer,
        'order': question.order,
    }


def serialize_quiz_result(row):
    from portals.utils.quiz_stats import quiz_average_score_tier, quiz_score_percent

    question_count = getattr(row, 'question_count', None)
    quiz = row.quiz
    # The annotated Count('quiz__questions') only counts inline variant
    # questions; reading/listening questions live in separate tables, so the
    # annotation yields 0 for them. Treat 0 as "unknown" and recount, else
    # max_value comes out as 0 and percentages break.
    if not question_count:
        if quiz.is_reading:
            from portals.utils.quiz_reading import get_reading_questions_for_quiz

            question_count = len(get_reading_questions_for_quiz(quiz))
        elif quiz.is_listening:
            from portals.utils.quiz_listening import get_listening_questions_for_quiz

            question_count = len(get_listening_questions_for_quiz(quiz))
        else:
            question_count = row.quiz.questions.count()
    completion_trigger = getattr(row, 'completion_trigger', 'manual') or 'manual'
    from portals.models import QuizResult as QuizResultModel
    trigger_labels = dict(QuizResultModel.CompletionTrigger.choices)
    time_limit_seconds = quiz.time_limit_seconds or 0
    max_value = quiz.score_max_value(question_count=question_count)
    is_pending_review = row.is_pending_review
    score_pct = (
        None
        if is_pending_review
        else quiz_score_percent(row.total_score, max_value)
    )
    return {
        'id': row.pk,
        'student_id': row.student_id,
        'customer_id': row.customer_id,
        'student_name': (
            row.customer.full_name
            if row.customer_id
            else (row.student.full_name if row.student_id else '')
        ),
        'quiz_id': row.quiz_id,
        'quiz_topic': quiz.topic,
        'grading_mode': quiz.grading_mode,
        'grading_mode_label': quiz.get_grading_mode_label(),
        'is_manual_grading': quiz.is_manual_grading,
        'requires_teacher_review': quiz.requires_teacher_review,
        'total_score': row.total_score,
        'max_value': max_value,
        'score_pct': score_pct,
        'tier': quiz_average_score_tier(score_pct),
        'duration_sec': row.duration_sec,
        'is_time_limited': bool(quiz.is_time_limited and quiz.time_limit_minutes),
        'time_limit_minutes': quiz.time_limit_minutes,
        'time_limit_seconds': time_limit_seconds,
        'completion_trigger': completion_trigger,
        'completion_trigger_label': trigger_labels.get(completion_trigger, completion_trigger),
        'auto_completed': completion_trigger in ('time_limit', 'auto_leave'),
        'timed_out': completion_trigger == 'time_limit',
        'student_submission': row.student_submission,
        'teacher_feedback': row.teacher_feedback,
        'reviewed_at': row.reviewed_at,
        'is_pending_review': is_pending_review,
        'completed_at': row.completed_at,
        'course_type': (
            quiz_category_primary_portal_code(row.quiz.category)
            if row.quiz.category_id
            else ''
        ),
    }


def _attach_attempt_metadata(rows):
    def attempt_label(number):
        last_digit = number % 10
        last_two_digits = number % 100
        if 10 <= last_two_digits <= 19:
            suffix = 'cu'
        elif last_digit in (1, 2, 5, 7, 8):
            suffix = 'ci'
        elif last_digit in (3, 4):
            suffix = 'cu'
        elif last_digit in (6, 9):
            suffix = 'cı'
        else:
            suffix = 'cü'
        return f'{number}-{suffix}'

    counts = {}
    for row in rows:
        quiz_id = row.get('quiz_id')
        counts[quiz_id] = counts.get(quiz_id, 0) + 1

    seen = {}
    enriched = []
    for row in rows:
        quiz_id = row.get('quiz_id')
        seen[quiz_id] = seen.get(quiz_id, 0) + 1
        attempt_count = counts.get(quiz_id, 0)
        attempt_number = attempt_count - seen[quiz_id] + 1
        enriched.append({
            **row,
            'attempt_count': attempt_count,
            'attempt_number': attempt_number,
            'attempt_label': attempt_label(attempt_number),
        })
    return enriched


def latest_quiz_result_per_quiz(rows, *, limit=None):
    latest_rows = []
    seen_quiz_ids = set()
    for row in rows or []:
        quiz_id = row.get('quiz_id')
        if quiz_id in seen_quiz_ids:
            continue
        seen_quiz_ids.add(quiz_id)
        latest_rows.append(row)
        if limit is not None and len(latest_rows) >= limit:
            break
    return latest_rows


def serialize_quiz_result_as_score(row):
    data = serialize_quiz_result(row)
    value = data['total_score']
    if data['is_pending_review']:
        value_label = None
    elif value is None:
        value_label = None
    else:
        value_label = value
    return {
        'id': f"quiz-{data['id']}",
        'result_id': data['id'],
        'source': 'quiz',
        'student_id': data['student_id'],
        'student_name': data['student_name'],
        'score_type': Score.ScoreType.QUIZ,
        'score_type_label': Score.ScoreType.QUIZ.label,
        'value': value_label,
        'max_value': data['max_value'],
        'score_pct': data.get('score_pct'),
        'tier': data.get('tier', 'empty'),
        'date': data['completed_at'],
        'comment': data['teacher_feedback'],
        'lesson_id': None,
        'lesson_title': data['quiz_topic'],
        'quiz_topic': data['quiz_topic'],
        'is_pending_review': data['is_pending_review'],
        'is_manual_grading': data['is_manual_grading'],
        'grading_mode_label': data.get('grading_mode_label', ''),
        'course_type': data.get('course_type') or '',
    }


def _quiz_results_queryset():
    return (
        QuizResult.objects.select_related('student', 'quiz')
        .annotate(question_count=Count('quiz__questions', distinct=True))
        .order_by('-completed_at', '-id')
    )


# ---------------------------------------------------------------------------
# Cached querysets
# ---------------------------------------------------------------------------

@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_teacher_groups(teacher_id):
    qs = (
        teacher_groups_queryset(teacher_id, active_only=True)
        .select_related('teacher')
        .annotate(student_count=Count('students', distinct=True))
        .prefetch_related('students', 'courses')
        .order_by('name', 'id')
    )
    return [serialize_group(g) for g in qs]


@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_teacher_group_detail(teacher_id, group_id):
    group = (
        teacher_groups_queryset(teacher_id, active_only=False)
        .filter(pk=group_id)
        .select_related('teacher')
        .prefetch_related(
            'courses',
            Prefetch('students', queryset=StudentProfile.objects.select_related('user').order_by('user__username', 'id')),
            Prefetch('schedules', queryset=Schedule.objects.order_by('weekday', 'start_time')),
        )
        .first()
    )
    if not group:
        return None
    return {
        **serialize_group(group),
        'students': [serialize_student(s) for s in group.students.all()],
        'schedules': [serialize_schedule(s) for s in group.schedules.all()],
    }


@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_teacher_lessons(teacher_id):
    qs = (
        Lesson.objects.filter(
            teacher_id=teacher_id,
            group__teacher_id=teacher_id,
        )
        .select_related('group', 'teacher', 'category')
        .prefetch_related('group__courses')
        .order_by('-lesson_date', '-created_at', 'id')
    )
    return [serialize_lesson(row) for row in qs]


@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_teacher_attendance(teacher_id):
    if not get_teacher_course_type_codes(teacher_id):
        return []
    qs = (
        teacher_attendance_queryset(teacher_id)
        .select_related('student', 'schedule', 'schedule__group')
        .order_by('-session_date', '-marked_at')[:200]
    )
    return [serialize_attendance(row) for row in qs]


@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_teacher_weekly_score_students(teacher_id):
    """Lightweight student roster for weekly grading (no attendance aggregation)."""
    if not get_teacher_course_type_codes(teacher_id):
        return []

    teacher_groups = teacher_groups_queryset(teacher_id)
    if not teacher_groups.exists():
        return []

    teacher_group_ids = list(teacher_groups.values_list('pk', flat=True))
    students = (
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

    return [
        {
            **serialize_student(student),
            'group_names': [group.name for group in student.groups.all()],
            'group_ids': [group.pk for group in student.groups.all()],
        }
        for student in students
    ]


@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_teacher_attendance_students(teacher_id):
    """Students in teacher groups with attendance summary counts."""
    from django.db.models import Count, Q

    if not get_teacher_course_type_codes(teacher_id):
        return []

    teacher_groups = teacher_groups_queryset(teacher_id)
    if not teacher_groups.exists():
        return []

    stats_qs = (
        teacher_attendance_queryset(teacher_id)
        .values('student_id')
        .annotate(
            present=Count('id', filter=Q(status=Attendance.Status.PRESENT)),
            absent=Count('id', filter=Q(status=Attendance.Status.ABSENT)),
            late=Count('id', filter=Q(status=Attendance.Status.LATE)),
            total=Count('id'),
        )
    )
    stats_map = {row['student_id']: row for row in stats_qs}

    teacher_group_ids = list(teacher_groups.values_list('pk', flat=True))
    students = (
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

    result = []
    for student in students:
        stats = stats_map.get(student.pk, {})
        present = stats.get('present', 0)
        total = stats.get('total', 0)
        result.append({
            **serialize_student(student),
            'group_names': [group.name for group in student.groups.all()],
            'group_ids': [group.pk for group in student.groups.all()],
            'summary': {
                'present': present,
                'absent': stats.get('absent', 0),
                'late': stats.get('late', 0),
                'total': total,
            },
            'attendance_rate': round(100 * present / total, 1) if total else None,
        })
    return result


@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_teacher_student_attendance_detail(teacher_id, student_id):
    from portals.utils.teacher_access import get_teacher_student

    student = get_teacher_student(teacher_id, student_id)
    if not student:
        return None

    course_codes = get_teacher_course_type_codes(teacher_id)
    if not course_codes:
        return None

    teacher_groups = teacher_groups_queryset(teacher_id)
    records_qs = (
        teacher_attendance_queryset(teacher_id)
        .filter(student_id=student_id)
        .select_related('schedule', 'schedule__group', 'student')
        .order_by('-session_date', '-marked_at')
    )
    records = [serialize_attendance(row) for row in records_qs]
    summary = {'present': 0, 'absent': 0, 'late': 0, 'total': len(records)}
    for row in records:
        summary[row['status']] = summary.get(row['status'], 0) + 1

    group_names = list(
        student.groups.filter(pk__in=teacher_groups.values('pk'))
        .order_by('name')
        .values_list('name', flat=True)
        .distinct()
    )

    return {
        'student': serialize_student(student),
        'groups': group_names,
        'summary': summary,
        'records': records,
    }


def get_teacher_scores(teacher_id):
    """Fresh scores list — not cached (LocMem + multi-worker stale after submit)."""
    from portals.utils.student_courses import SCORE_LIST_LIMIT, filter_quiz_results_for_teacher

    course_codes = get_teacher_course_type_codes(teacher_id)
    if not course_codes:
        return []
    quiz_qs = (
        _quiz_results_queryset()
        .filter(
            quiz__category__services__slug__in=quiz_category_slugs_for_portal_codes(course_codes),
            student__groups__teacher_id=teacher_id,
            student__groups__is_active=True,
        )
        .select_related('quiz__category', 'student')
        .distinct()[:500]
    )
    quiz_visible = filter_quiz_results_for_teacher(quiz_qs, teacher_id)
    quiz_rows = [serialize_quiz_result_as_score(row) for row in quiz_visible[:SCORE_LIST_LIMIT]]
    return quiz_rows


def split_teacher_score_rows(rows):
    auto_quiz_scores = []
    manual_quiz_scores = []
    for row in rows:
        if row.get('source') != 'quiz':
            continue
        if row.get('is_manual_grading'):
            if row.get('is_pending_review'):
                continue
            manual_quiz_scores.append(row)
        else:
            auto_quiz_scores.append(row)
    return {
        'auto_quiz_scores': auto_quiz_scores,
        'manual_quiz_scores': manual_quiz_scores,
    }


def split_score_rows_by_source(rows):
    """Split merged score rows into quiz results."""
    return {
        'quiz_scores': [row for row in rows if row.get('source') == 'quiz'],
    }


def resolve_scores_view_param(request, quiz_scores, weekly_scores, mock_attempts=None):
    """Pick active scores tab from query string or sensible default."""
    scores_view = request.GET.get('view')
    if scores_view == 'lesson':
        scores_view = 'weekly'
    valid_views = ('quiz', 'weekly')
    if mock_attempts is not None:
        valid_views = ('quiz', 'weekly', 'mock')
    if scores_view in valid_views:
        return scores_view
    if not quiz_scores and weekly_scores:
        return 'weekly'
    if not quiz_scores and not weekly_scores and mock_attempts:
        return 'mock'
    return 'quiz'


def resolve_mock_program_param(request):
    """Optional exam program filter for mock scores tab (?program=ielts|sat)."""
    from portals.utils.mock_programs import MOCK_EXAM_PROGRAMS

    raw = (request.GET.get('program') or '').strip().lower()
    return raw if raw in MOCK_EXAM_PROGRAMS else None


def filter_mock_attempt_summaries(attempts, *, program=None):
    rows = list(attempts or [])
    if not program:
        return rows
    return [row for row in rows if row.get('exam_program') == program]


def split_student_quiz_results(rows):
    manual_quiz_results = [row for row in rows if row.get('is_manual_grading')]
    auto_quiz_results = [row for row in rows if not row.get('is_manual_grading')]
    return manual_quiz_results, auto_quiz_results


@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_teacher_quizzes(teacher_id):
    from portals.utils.student_courses import quiz_visible_to_teacher

    course_codes = get_teacher_course_type_codes(teacher_id)
    if not course_codes:
        return []
    qs = (
        Quiz.objects.filter(
            category__services__slug__in=quiz_category_slugs_for_portal_codes(course_codes),
        )
        .select_related('category')
        .prefetch_related('questions')
        .distinct()
        .order_by('-created_at', 'id')
    )
    visible = [row for row in qs if quiz_visible_to_teacher(row, teacher_id)]
    question_counts = _answerable_question_counts(visible)
    return [serialize_quiz(row, question_counts=question_counts) for row in visible]


@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_teacher_quiz_detail(teacher_id, quiz_id):
    from portals.utils.student_courses import quiz_visible_to_teacher

    course_codes = get_teacher_course_type_codes(teacher_id)
    if not course_codes:
        return None
    quiz = (
        Quiz.objects.filter(
            pk=quiz_id,
            category__services__slug__in=quiz_category_slugs_for_portal_codes(course_codes),
        )
        .select_related('category')
        .prefetch_related(
            Prefetch('questions', queryset=QuizQuestion.objects.order_by('order', 'id')),
        )
        .first()
    )
    if not quiz or not quiz_visible_to_teacher(quiz, teacher_id):
        return None
    payload = {
        **serialize_quiz(quiz),
        'questions': [serialize_quiz_question(q) for q in quiz.questions.all()],
        'listening_sections': [],
        'reading_sections': [],
        'speaking_sections': [],
    }
    if quiz.is_listening:
        from portals.utils.quiz_listening import build_listening_sections_for_quiz

        payload['listening_sections'] = build_listening_sections_for_quiz(quiz.pk)
        flat_questions = [row for section in payload['listening_sections'] for row in section['questions']]
        payload['response_question_count'] = len(flat_questions)
    elif quiz.is_reading:
        from portals.utils.quiz_reading import build_reading_sections_for_quiz

        payload['reading_sections'] = build_reading_sections_for_quiz(quiz.pk)
        flat_questions = [row for section in payload['reading_sections'] for row in section['questions']]
        payload['response_question_count'] = len(flat_questions)
    elif quiz.is_speaking:
        from portals.utils.quiz_speaking import (
            build_speaking_sections_for_quiz,
            estimate_speaking_quiz_seconds,
        )

        sections = build_speaking_sections_for_quiz(quiz.pk)
        payload['speaking_sections'] = sections
        flat_questions = [row for section in sections for row in section['questions']]
        payload['response_question_count'] = len(flat_questions)
        estimated_total_seconds = estimate_speaking_quiz_seconds(sections)
        payload['estimated_total_seconds'] = estimated_total_seconds
        payload['estimated_total_minutes'] = max(1, round(estimated_total_seconds / 60))
    return payload


def get_student_reading_quiz_take_data(student_id, quiz_id, *, mock_attempt_id: int | None = None):
    from portals.utils.ielts_mock_test import mock_allows_active_section_take
    from portals.utils.student_courses import quiz_visible_to_student, student_quiz_enrollment_ok
    from portals.utils.quiz_reading import (
        build_reading_sections_for_quiz,
        get_reading_questions_for_quiz,
    )

    course_codes = get_student_course_type_codes(student_id)
    if not course_codes:
        return None
    quiz = (
        Quiz.objects.filter(
            pk=quiz_id,
            category__services__slug__in=quiz_category_slugs_for_portal_codes(course_codes),
        )
        .select_related('category')
        .first()
    )
    if not quiz:
        return None
    if mock_attempt_id:
        if not student_quiz_enrollment_ok(student_id, quiz):
            return None
    elif not quiz_visible_to_student(quiz, student_id):
        return None
    if not quiz.is_reading:
        return None
    if not get_reading_questions_for_quiz(quiz):
        return None

    mock_take = mock_allows_active_section_take(student_id, mock_attempt_id, quiz_id)
    if mock_take:
        sections = build_reading_sections_for_quiz(quiz.pk)
        flat_questions = [row for section in sections for row in section['questions']]
        response_ids = [row['id'] for row in flat_questions]
        return {
            **serialize_quiz(quiz),
            'questions': flat_questions,
            'reading_sections': sections,
            'response_question_ids': response_ids,
            'response_question_count': len(response_ids),
            'view_only': False,
            'is_pending_review': False,
            'is_mock_section': True,
        }

    existing = (
        QuizResult.objects.filter(
            student_id=student_id,
            quiz_id=quiz_id,
            ielts_mock_attempt__isnull=True,
        )
        .order_by('-completed_at', '-id')
        .first()
    )
    sections = build_reading_sections_for_quiz(quiz.pk)
    flat_questions = [row for section in sections for row in section['questions']]
    response_ids = [row['id'] for row in flat_questions]
    return {
        **serialize_quiz(quiz),
        'questions': flat_questions,
        'reading_sections': sections,
        'response_question_ids': response_ids,
        'response_question_count': len(response_ids),
        'view_only': False,
        'is_pending_review': False,
        'result_id': existing.pk if existing else None,
    }


def get_student_listening_quiz_take_data(student_id, quiz_id, *, mock_attempt_id: int | None = None):
    from portals.utils.ielts_mock_test import mock_allows_active_section_take
    from portals.utils.student_courses import quiz_visible_to_student, student_quiz_enrollment_ok
    from portals.utils.quiz_listening import (
        build_listening_sections_for_quiz,
        get_listening_questions_for_quiz,
    )

    course_codes = get_student_course_type_codes(student_id)
    if not course_codes:
        return None
    quiz = (
        Quiz.objects.filter(
            pk=quiz_id,
            category__services__slug__in=quiz_category_slugs_for_portal_codes(course_codes),
        )
        .select_related('category')
        .first()
    )
    if not quiz:
        return None
    if mock_attempt_id:
        if not student_quiz_enrollment_ok(student_id, quiz):
            return None
    elif not quiz_visible_to_student(quiz, student_id):
        return None
    if not quiz.is_listening:
        return None
    if not get_listening_questions_for_quiz(quiz):
        return None

    mock_take = mock_allows_active_section_take(student_id, mock_attempt_id, quiz_id)
    if mock_take:
        sections = build_listening_sections_for_quiz(quiz.pk)
        flat_questions = [row for section in sections for row in section['questions']]
        response_ids = [row['id'] for row in flat_questions]
        return {
            **serialize_quiz(quiz),
            'questions': flat_questions,
            'listening_sections': sections,
            'response_question_ids': response_ids,
            'response_question_count': len(response_ids),
            'view_only': False,
            'is_pending_review': False,
            'is_mock_section': True,
        }

    existing = (
        QuizResult.objects.filter(
            student_id=student_id,
            quiz_id=quiz_id,
            ielts_mock_attempt__isnull=True,
        )
        .order_by('-completed_at', '-id')
        .first()
    )
    sections = build_listening_sections_for_quiz(quiz.pk)
    flat_questions = [row for section in sections for row in section['questions']]
    response_ids = [row['id'] for row in flat_questions]
    return {
        **serialize_quiz(quiz),
        'questions': flat_questions,
        'listening_sections': sections,
        'response_question_ids': response_ids,
        'response_question_count': len(response_ids),
        'view_only': False,
        'is_pending_review': False,
        'result_id': existing.pk if existing else None,
    }


def get_student_speaking_quiz_take_data(student_id, quiz_id, *, mock_attempt_id: int | None = None):
    from portals.models import SpeakingRecording
    from portals.utils.ielts_mock_test import mock_allows_active_section_take
    from portals.utils.student_courses import quiz_visible_to_student, student_quiz_enrollment_ok
    from portals.utils.quiz_speaking import (
        build_speaking_sections_for_quiz,
        estimate_speaking_quiz_seconds,
        get_speaking_questions_for_quiz,
    )
    from portals.utils.quiz_submit import student_can_take_manual_quiz

    course_codes = get_student_course_type_codes(student_id)
    if not course_codes:
        return None
    quiz = (
        Quiz.objects.filter(
            pk=quiz_id,
            category__services__slug__in=quiz_category_slugs_for_portal_codes(course_codes),
        )
        .select_related('category')
        .first()
    )
    if not quiz:
        return None
    if mock_attempt_id:
        if not student_quiz_enrollment_ok(student_id, quiz):
            return None
    elif not quiz_visible_to_student(quiz, student_id):
        return None
    if not quiz.is_speaking:
        return None
    if not get_speaking_questions_for_quiz(quiz):
        return None

    mock_take = mock_allows_active_section_take(student_id, mock_attempt_id, quiz_id)
    if mock_take:
        sections = build_speaking_sections_for_quiz(quiz.pk)
        flat_questions = [row for section in sections for row in section['questions']]
        response_ids = [row['id'] for row in flat_questions]
        estimated_total_seconds = estimate_speaking_quiz_seconds(sections)
        return {
            **serialize_quiz(quiz),
            'questions': flat_questions,
            'speaking_sections': sections,
            'response_question_ids': response_ids,
            'response_question_count': len(response_ids),
            'estimated_total_seconds': estimated_total_seconds,
            'estimated_total_minutes': max(1, round(estimated_total_seconds / 60)),
            'view_only': False,
            'is_pending_review': False,
            'is_mock_section': True,
        }

    existing = (
        QuizResult.objects.filter(
            student_id=student_id,
            quiz_id=quiz_id,
            ielts_mock_attempt__isnull=True,
        )
        .order_by('-completed_at', '-id')
        .first()
    )
    can_take = student_can_take_manual_quiz(student_id, quiz_id)

    if existing and existing.is_pending_review:
        recording_map = {
            str(row.question_id): {
                'audio_url': row.audio_url,
                'duration_sec': row.duration_sec,
            }
            for row in SpeakingRecording.objects.filter(result_id=existing.pk).select_related('question')
        }
        sections = build_speaking_sections_for_quiz(quiz.pk, recording_map=recording_map)
        flat_questions = [row for section in sections for row in section['questions']]
        response_ids = [row['id'] for row in flat_questions]
        estimated_total_seconds = estimate_speaking_quiz_seconds(sections)
        return {
            **serialize_quiz(quiz),
            'questions': flat_questions,
            'speaking_sections': sections,
            'response_question_ids': response_ids,
            'response_question_count': len(response_ids),
            'estimated_total_seconds': estimated_total_seconds,
            'estimated_total_minutes': max(1, round(estimated_total_seconds / 60)),
            'view_only': True,
            'is_pending_review': True,
            'result_id': existing.pk,
        }
    if not can_take:
        return None

    sections = build_speaking_sections_for_quiz(quiz.pk)
    flat_questions = [row for section in sections for row in section['questions']]
    response_ids = [row['id'] for row in flat_questions]
    estimated_total_seconds = estimate_speaking_quiz_seconds(sections)
    return {
        **serialize_quiz(quiz),
        'questions': flat_questions,
        'speaking_sections': sections,
        'response_question_ids': response_ids,
        'response_question_count': len(response_ids),
        'estimated_total_seconds': estimated_total_seconds,
        'estimated_total_minutes': max(1, round(estimated_total_seconds / 60)),
        'view_only': False,
        'is_pending_review': False,
        'result_id': existing.pk if existing else None,
    }


def get_student_quiz_take_data(student_id, quiz_id, *, mock_attempt_id: int | None = None):
    from portals.utils.ielts_mock_test import mock_allows_active_section_take
    from portals.utils.student_courses import quiz_visible_to_student, student_quiz_enrollment_ok

    course_codes = get_student_course_type_codes(student_id)
    if not course_codes:
        return None
    quiz = (
        Quiz.objects.filter(
            pk=quiz_id,
            category__services__slug__in=quiz_category_slugs_for_portal_codes(course_codes),
        )
        .select_related('category')
        .prefetch_related(
            Prefetch('questions', queryset=QuizQuestion.objects.order_by('order', 'id')),
        )
        .first()
    )
    if not quiz:
        return None
    if mock_attempt_id:
        if not student_quiz_enrollment_ok(student_id, quiz):
            return None
    elif not quiz_visible_to_student(quiz, student_id):
        return None
    if not quiz.is_variant_quiz:
        return None

    questions = [q for q in quiz.questions.all() if q.is_answerable]
    if not questions:
        return None

    mock_take = mock_allows_active_section_take(student_id, mock_attempt_id, quiz_id)
    if mock_take:
        return {
            **serialize_quiz(quiz),
            'questions': [serialize_quiz_question_for_student(q) for q in questions],
            'view_only': False,
            'is_pending_review': False,
            'is_mock_section': True,
        }

    existing = (
        QuizResult.objects.filter(
            student_id=student_id,
            quiz_id=quiz_id,
            ielts_mock_attempt__isnull=True,
        )
        .order_by('-completed_at', '-id')
        .first()
    )
    return {
        **serialize_quiz(quiz),
        'questions': [serialize_quiz_question_for_student(q) for q in questions],
        'view_only': False,
        'is_pending_review': False,
        'result_id': existing.pk if existing else None,
    }


def get_student_manual_quiz_take_data(student_id, quiz_id, *, mock_attempt_id: int | None = None):
    from portals.utils.ielts_mock_test import mock_allows_active_section_take
    from portals.utils.student_courses import quiz_visible_to_student, student_quiz_enrollment_ok
    from portals.utils.quiz_submit import build_essay_question_responses, student_can_take_manual_quiz

    course_codes = get_student_course_type_codes(student_id)
    if not course_codes:
        return None
    quiz = (
        Quiz.objects.filter(
            pk=quiz_id,
            category__services__slug__in=quiz_category_slugs_for_portal_codes(course_codes),
        )
        .select_related('category')
        .prefetch_related(
            Prefetch('questions', queryset=QuizQuestion.objects.order_by('order', 'id')),
        )
        .first()
    )
    if not quiz:
        return None
    if mock_attempt_id:
        if not student_quiz_enrollment_ok(student_id, quiz):
            return None
    elif not quiz_visible_to_student(quiz, student_id):
        return None
    if not quiz.is_manual_grading:
        return None
    if quiz.is_listening or quiz.is_speaking:
        return None

    questions = [q for q in quiz.questions.all() if q.is_answerable]
    if not questions:
        return None

    mock_take = mock_allows_active_section_take(student_id, mock_attempt_id, quiz_id)
    if mock_take:
        serialized_qs = [serialize_quiz_question_for_student(q) for q in questions]
        response_ids = [q['id'] for q in serialized_qs]
        return {
            **serialize_quiz(quiz),
            'questions': serialized_qs,
            'listening_sections': [],
            'response_question_ids': response_ids,
            'response_question_count': len(response_ids),
            'view_only': False,
            'is_mock_section': True,
        }

    existing = (
        QuizResult.objects.filter(
            student_id=student_id,
            quiz_id=quiz_id,
            ielts_mock_attempt__isnull=True,
        )
        .select_related('quiz')
        .prefetch_related(
            Prefetch('quiz__questions', queryset=QuizQuestion.objects.order_by('order', 'id')),
        )
        .order_by('-completed_at', '-id')
        .first()
    )
    can_take = student_can_take_manual_quiz(student_id, quiz_id)

    if existing and existing.is_pending_review:
        response_map = {
            str(item['id']): item['student_answer']
            for item in build_essay_question_responses(existing)
        }
        single_submission = (existing.student_submission or '').strip()
        serialized_qs = [
            serialize_quiz_question_for_student(
                q,
                student_answer=response_map.get(str(q.pk), single_submission if len(questions) == 1 else ''),
            )
            for q in questions
        ]
        response_ids = [q['id'] for q in serialized_qs]
        return {
            **serialize_quiz(quiz),
            'questions': serialized_qs,
            'listening_sections': [],
            'response_question_ids': response_ids,
            'response_question_count': len(response_ids),
            'view_only': True,
            'is_pending_review': True,
            'result_id': existing.pk,
        }
    if not can_take:
        return None
    serialized_qs = [serialize_quiz_question_for_student(q) for q in questions]
    response_ids = [q['id'] for q in serialized_qs]
    return {
        **serialize_quiz(quiz),
        'questions': serialized_qs,
        'listening_sections': [],
        'response_question_ids': response_ids,
        'response_question_count': len(response_ids),
        'view_only': False,
    }


def serialize_quiz_result_review(row):
    from portals.utils.quiz_submit import build_essay_question_responses
    from portals.utils.ielts_mock_test import find_mock_attempt_for_result, section_for_result_in_attempt

    quiz = row.quiz
    mock_attempt = find_mock_attempt_for_result(row)
    mock_section = section_for_result_in_attempt(mock_attempt, row) if mock_attempt else None
    mock_section_label = ''
    if mock_section:
        from portals.models import IeltsMockTestAttempt

        mock_section_label = dict(IeltsMockTestAttempt.Section.choices).get(mock_section, mock_section)

    data = {
        **serialize_quiz_result(row),
        'student_submission': row.student_submission,
        'teacher_feedback': row.teacher_feedback,
        'grading_mode_label': quiz.get_grading_mode_label(),
        'is_essay': quiz.is_essay,
        'is_listening': quiz.is_listening,
        'is_reading': quiz.is_reading,
        'is_speaking': quiz.is_speaking,
        'mock_attempt_id': mock_attempt.pk if mock_attempt else None,
        'mock_section': mock_section,
        'mock_section_label': mock_section_label,
        'mock_detail_url': (
            reverse('portals:teacher-ielts-mock-detail', kwargs={'pk': mock_attempt.pk})
            if mock_attempt
            else ''
        ),
        'listening_sections': [],
        'reading_sections': [],
        'speaking_sections': [],
        'questions': [serialize_quiz_question(q) for q in quiz.questions.all()],
        'question_responses': [],
        'breakdown': [],
    }
    responses = []
    if quiz.is_listening or quiz.is_essay or quiz.is_speaking or quiz.uses_per_question_text_responses:
        responses = build_essay_question_responses(row)
        data['question_responses'] = responses
    if quiz.is_listening:
        from portals.utils.quiz_listening import build_listening_sections_for_quiz

        response_map = {
            str(key): str(value)
            for key, value in (row.given_answers or {}).items()
        }
        data['listening_sections'] = build_listening_sections_for_quiz(
            quiz.pk,
            response_map=response_map,
            use_admin_answer_keys=True,
        )
    elif quiz.is_reading:
        from portals.utils.quiz_reading import build_reading_sections_for_quiz

        response_map = {
            str(key): value
            for key, value in (row.given_answers or {}).items()
        }
        teacher_correct_map = {
            str(key): str(value)
            for key, value in (row.teacher_correct_answers or {}).items()
            if str(value).strip()
        }
        data['reading_review_editable'] = False
        data['reading_sections'] = build_reading_sections_for_quiz(
            quiz.pk,
            response_map=response_map,
            correct_answer_map=teacher_correct_map or None,
            use_admin_answer_keys=not teacher_correct_map,
        )
        data['breakdown'] = [
            {
                'id': item['id'],
                'question': item.get('question', ''),
                'question_type_label': item.get('question_type_label', ''),
                'student_answer': item.get('student_answer_display', ''),
                'correct_answer': item.get('correct_answer_display', item.get('correct_answer', '')),
                'is_correct': item.get('is_correct'),
            }
            for section in data['reading_sections']
            for item in section['questions']
        ]
    elif quiz.is_speaking:
        from portals.models import SpeakingRecording
        from portals.utils.quiz_speaking import (
            build_speaking_sections_for_quiz,
            estimate_speaking_quiz_seconds,
        )

        recording_map = {
            str(row.question_id): {
                'audio_url': row.audio_url,
                'duration_sec': row.duration_sec,
            }
            for row in SpeakingRecording.objects.filter(result_id=row.pk).select_related('question')
        }
        sections = build_speaking_sections_for_quiz(
            quiz.pk,
            recording_map=recording_map,
        )
        data['speaking_sections'] = sections
        estimated_total_seconds = estimate_speaking_quiz_seconds(sections)
        data['estimated_total_seconds'] = estimated_total_seconds
        data['estimated_total_minutes'] = max(1, round(estimated_total_seconds / 60))
    return data


def _teacher_pending_quiz_results_queryset(teacher_id):
    from django.db.models import Q

    course_codes = get_teacher_course_type_codes(teacher_id)
    if not course_codes:
        return None
    pending_filter = Q(reviewed_at__isnull=True) & Q(
        quiz__category__services__slug__in=quiz_category_slugs_for_portal_codes(course_codes),
    ) & (Q(quiz__is_essay=True) | Q(quiz__is_speaking=True))
    # Do not require group.courses slug match here — empty/mismatched courses M2M
    # would hide mock writing/speaking from the review queue. Python filter applies
    # teacher_can_see_quiz_result (with shared-group fallback).
    student_filter = pending_filter & Q(
        student__isnull=False,
        student__groups__teacher_id=teacher_id,
        student__groups__is_active=True,
    )
    customer_filter = pending_filter & Q(
        customer__isnull=False,
        customer__teacher_id=teacher_id,
    )
    return (
        QuizResult.objects.filter(student_filter | customer_filter)
        .select_related('student', 'customer', 'quiz', 'quiz__category')
        .distinct()
        .order_by('-completed_at', 'id')
    )


def get_teacher_pending_quiz_results(teacher_id):
    from portals.utils.student_courses import filter_quiz_results_for_teacher

    qs = _teacher_pending_quiz_results_queryset(teacher_id)
    if qs is None:
        return []
    qs = qs.prefetch_related(
        Prefetch('quiz__questions', queryset=QuizQuestion.objects.order_by('order', 'id')),
    )
    visible = filter_quiz_results_for_teacher(qs, teacher_id)
    return [serialize_quiz_result_review(row) for row in visible[:100]]


def get_teacher_quiz_result_detail(teacher_id, result_id):
    from portals.utils.student_courses import teacher_can_review_quiz_result

    row = (
        QuizResult.objects.filter(pk=result_id)
        .select_related('student', 'customer', 'quiz', 'quiz__category')
        .prefetch_related(
            Prefetch('quiz__questions', queryset=QuizQuestion.objects.order_by('order', 'id')),
        )
        .first()
    )
    if not row or not row.quiz.requires_teacher_review:
        return None
    if not teacher_can_review_quiz_result(teacher_id, row):
        return None
    return serialize_quiz_result_review(row)


@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_student_group_ids(student_id):
    return list(
        StudyGroup.objects.filter(students__pk=student_id, is_active=True)
        .values_list('id', flat=True)
    )


@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_student_schedules(student_id):
    group_ids = get_student_group_ids(student_id)
    qs = (
        Schedule.objects.filter(group_id__in=group_ids)
        .select_related('group')
        .order_by('weekday', 'start_time', 'id')
    )
    return [serialize_schedule(row) for row in qs]


@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_student_lessons(student_id):
    group_ids = get_student_group_ids(student_id)
    qs = (
        Lesson.objects.filter(
            group_id__in=group_ids,
            teacher_id=F('group__teacher_id'),
        )
        .select_related('group', 'category')
        .order_by('-lesson_date', '-created_at', 'id')
    )
    return [serialize_lesson(row) for row in qs]


@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_student_video_records(student_id):
    group_ids = get_student_group_ids(student_id)
    qs = (
        VideoRecord.objects.filter(group_id__in=group_ids)
        .select_related('group')
        .order_by('-lesson_date', '-id')
    )
    return [serialize_video_record(row) for row in qs]


@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_student_scores(student_id):
    from portals.utils.student_courses import SCORE_LIST_LIMIT, filter_quiz_results_for_student

    codes = get_student_course_type_codes(student_id)
    if not codes:
        return []
    quiz_qs = (
        _quiz_results_queryset()
        .filter(
            student_id=student_id,
            quiz__category__services__slug__in=quiz_category_slugs_for_portal_codes(codes),
        )
        .select_related('quiz__category')
        .distinct()[:500]
    )
    quiz_visible = filter_quiz_results_for_student(quiz_qs, student_id)
    quiz_rows = [serialize_quiz_result_as_score(row) for row in quiz_visible[:SCORE_LIST_LIMIT]]
    return quiz_rows


@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_student_quizzes(student_id):
    from portals.models import Quiz
    from portals.utils.student_courses import filter_quizzes_for_student

    codes = get_student_course_type_codes(student_id)
    if not codes:
        return []
    qs = (
        Quiz.objects.filter(category__services__slug__in=quiz_category_slugs_for_portal_codes(codes))
        .select_related('category')
        .prefetch_related('questions')
        .distinct()
        .order_by('-created_at', 'id')
    )
    visible = filter_quizzes_for_student(qs, student_id)
    return [serialize_quiz(row) for row in visible]


@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_student_attendance_detail(student_id):
    """Attendance summary for a student's own profile."""
    return get_parent_child_attendance_detail(student_id)


@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_parent_child_attendance_detail(student_id):
    student = (
        StudentProfile.objects.filter(pk=student_id)
        .select_related('user')
        .prefetch_related('groups')
        .first()
    )
    if not student:
        return None

    records_qs = (
        Attendance.objects.filter(student_id=student_id)
        .select_related('schedule', 'schedule__group', 'student')
        .order_by('-session_date', '-marked_at')[:200]
    )
    records = [serialize_attendance(row) for row in records_qs]
    summary = {'present': 0, 'absent': 0, 'late': 0, 'total': len(records)}
    for row in records:
        if row['status'] in summary:
            summary[row['status']] += 1

    present = summary['present']
    total = summary['total']
    attendance_rate = round(100 * present / total, 1) if total else None
    group_names = list(student.groups.order_by('name').values_list('name', flat=True))

    return {
        'student': serialize_student(student),
        'groups': group_names,
        'summary': summary,
        'records': records,
        'attendance_rate': attendance_rate,
    }


@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_parent_child_attendance(student_id):
    qs = (
        Attendance.objects.filter(student_id=student_id)
        .select_related('student', 'schedule', 'schedule__group')
        .order_by('-session_date', '-marked_at')[:200]
    )
    return [serialize_attendance(row) for row in qs]


def get_student_quiz_results(student_id, *, quiz_ids=None):
    from portals.utils.student_courses import filter_quiz_results_for_student

    codes = get_student_course_type_codes(student_id)
    if not codes:
        return []
    if quiz_ids is not None and not quiz_ids:
        return []
    qs = (
        _quiz_results_queryset()
        .filter(
            student_id=student_id,
            quiz__category__services__slug__in=quiz_category_slugs_for_portal_codes(codes),
        )
        .select_related('quiz__category')
        .distinct()
    )
    if quiz_ids is not None:
        qs = qs.filter(quiz_id__in=list(quiz_ids))
    visible = filter_quiz_results_for_student(qs, student_id)
    return _attach_attempt_metadata([serialize_quiz_result(row) for row in visible])


@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_parent_child_quiz_results(student_id, *, parent_id=None):
    from portals.utils.parent_access import parent_can_access_student

    if parent_id is not None and not parent_can_access_student(parent_id, student_id):
        return []
    return get_student_quiz_results(student_id)


def get_teacher_student_quiz_results(teacher_id, student_id):
    """Fresh history — includes mock section results; not LocMem-cached."""
    from portals.utils.student_courses import filter_quiz_results_for_teacher
    from portals.utils.teacher_access import get_teacher_student

    if not get_teacher_student(teacher_id, student_id):
        return []
    course_codes = get_teacher_course_type_codes(teacher_id)
    if not course_codes:
        return []
    qs = (
        _quiz_results_queryset()
        .filter(
            student_id=student_id,
            quiz__category__services__slug__in=quiz_category_slugs_for_portal_codes(course_codes),
        )
        .select_related('quiz__category')
        .distinct()
    )
    visible = filter_quiz_results_for_teacher(qs, teacher_id)
    return [serialize_quiz_result(row) for row in visible]


def get_teacher_student_scores(teacher_id, student_id):
    from portals.utils.student_courses import filter_quiz_results_for_teacher
    from portals.utils.teacher_access import get_teacher_student

    if not get_teacher_student(teacher_id, student_id):
        return []
    course_codes = get_teacher_course_type_codes(teacher_id)
    if not course_codes:
        return []
    quiz_qs = (
        _quiz_results_queryset()
        .filter(
            student_id=student_id,
            quiz__category__services__slug__in=quiz_category_slugs_for_portal_codes(course_codes),
        )
        .select_related('quiz__category', 'student')
        .distinct()
    )
    quiz_visible = filter_quiz_results_for_teacher(quiz_qs, teacher_id)
    quiz_rows = [serialize_quiz_result_as_score(row) for row in quiz_visible]
    return quiz_rows


def group_scores_by_day(scores):
    """Group score rows by calendar day (newest days first)."""
    from collections import OrderedDict

    buckets = OrderedDict()
    for row in scores:
        dt = row.get('date')
        if not dt:
            continue
        if hasattr(dt, 'date'):
            day = dt.date() if hasattr(dt, 'hour') else dt
        else:
            day = dt
        key = day.isoformat()
        if key not in buckets:
            buckets[key] = {'date': day, 'entries': []}
        buckets[key]['entries'].append(row)
    return list(buckets.values())


def get_teacher_student_group_names(teacher_id, student_id):
    return list(
        StudyGroup.objects.filter(
            teacher_id=teacher_id,
            students__pk=student_id,
        )
        .values_list('name', flat=True)
        .order_by('name')
    )


def get_teacher_student_profile_groups(teacher_id, student_id):
    return list(
        StudyGroup.objects.filter(
            teacher_id=teacher_id,
            students__pk=student_id,
            is_active=True,
        )
        .order_by('name')
        .values('id', 'name')
    )


def resolve_teacher_profile_group(request, profile_groups):
    if not profile_groups:
        return None
    if len(profile_groups) == 1:
        return profile_groups[0]['id']
    from_group = request.GET.get('from_group')
    if from_group:
        try:
            group_id = int(from_group)
        except (TypeError, ValueError):
            group_id = None
        if group_id and any(row['id'] == group_id for row in profile_groups):
            return group_id
    return profile_groups[0]['id']


def resolve_teacher_profile_duration_group(request, profile_groups):
    return resolve_teacher_profile_group(request, profile_groups)


def get_teacher_student_group_service_codes(teacher_id, student_id, group_id):
    from portals.utils.group_services import study_group_portal_codes

    group = (
        StudyGroup.objects.filter(
            pk=group_id,
            teacher_id=teacher_id,
            students__pk=student_id,
            is_active=True,
        )
        .prefetch_related('courses')
        .first()
    )
    if not group:
        return None
    return set(study_group_portal_codes(group))


def filter_teacher_profile_rows_by_group(rows, service_codes, *, key='course_type'):
    if not service_codes:
        return rows
    return [row for row in rows if row.get(key) in service_codes]


def filter_attendance_detail_by_group(attendance_detail, group_id):
    if not attendance_detail or not group_id:
        return attendance_detail
    filtered_records = [
        row for row in attendance_detail.get('records', [])
        if row.get('group_id') == group_id
    ]
    summary = {'present': 0, 'absent': 0, 'late': 0, 'total': len(filtered_records)}
    for row in filtered_records:
        status = row.get('status')
        if status in summary:
            summary[status] += 1
    present = summary['present']
    total = summary['total']
    return {
        **attendance_detail,
        'summary': summary,
        'records': filtered_records,
        'attendance_rate': round(100 * present / total, 1) if total else None,
    }


def resolve_teacher_student_profile_back(request, teacher_id, student_id):
    """Back target for teacher student profile — prefer originating group."""
    from django.utils.translation import gettext as _

    from portals.utils.teacher_access import get_teacher_group

    student_groups = list(
        StudyGroup.objects.filter(
            teacher_id=teacher_id,
            students__pk=student_id,
        )
        .values_list('pk', 'name')
        .order_by('name')
    )

    from_group = request.GET.get('from_group')
    if from_group:
        try:
            group_id = int(from_group)
        except (TypeError, ValueError):
            group_id = None
        if group_id and any(pk == group_id for pk, _ in student_groups):
            group = get_teacher_group(teacher_id, group_id)
            if group:
                return (
                    reverse('portals:teacher-group-detail', kwargs={'pk': group_id}),
                    group.name,
                    group_id,
                )

    if len(student_groups) == 1:
        group_id, group_name = student_groups[0]
        return (
            reverse('portals:teacher-group-detail', kwargs={'pk': group_id}),
            group_name,
            group_id,
        )

    return reverse('portals:teacher-groups'), _('Qruplar'), None


# ---------------------------------------------------------------------------
# Page blobs (cached per profile + query string)
# ---------------------------------------------------------------------------

@cached_page_data(timeout='CACHE_TIMEOUT_MEDIUM')
def get_teacher_dashboard_data(request, teacher_id):
    return {
        'groups': get_teacher_groups(teacher_id),
    }


def get_teacher_dashboard_stats(teacher_id):
    """Heavy dashboard counts — loaded via AJAX after the shell renders."""
    from portals.utils.weekly_scores import get_teacher_weekly_scores_list

    groups = get_teacher_groups(teacher_id)
    quiz_scores = get_teacher_scores(teacher_id)
    weekly_scores = get_teacher_weekly_scores_list(teacher_id)
    return {
        'group_count': len(groups),
        'lesson_count': len(get_teacher_lessons(teacher_id)),
        'quiz_count': len(get_teacher_quizzes(teacher_id)),
        'student_count': sum(g.get('student_count', 0) for g in groups),
        'quiz_result_count': len(quiz_scores),
        'weekly_score_count': len(weekly_scores),
    }


def _student_performance_snapshot(student_id, *, parent_id=None, group_id=None):
    from portals.utils.attendance_stats import compute_attendance_stats
    from portals.utils.group_services import study_group_portal_codes
    from portals.utils.ielts_mock_test import (
        get_student_completed_mock_attempts,
        get_student_mock_exam_programs,
        serialize_mock_attempt_summary,
        student_can_access_mock,
    )
    from portals.utils.quiz_stats import (
        build_mock_stats_list,
        compute_quiz_average_stats,
        compute_weekly_average_stats,
    )
    from portals.utils.weekly_scores import get_student_weekly_scores

    group = None
    group_service_codes = None
    if group_id:
        group = (
            StudyGroup.objects.filter(pk=group_id, students__pk=student_id, is_active=True)
            .select_related('teacher')
            .prefetch_related('courses')
            .first()
        )
        if group:
            group_service_codes = set(study_group_portal_codes(group))

    weekly_scores = get_student_weekly_scores(student_id)
    if group:
        weekly_scores = [
            row for row in weekly_scores
            if row.get('study_group_id') == group.pk
        ]

    if parent_id is not None:
        quiz_results = get_parent_child_quiz_results(student_id, parent_id=parent_id)
    else:
        quiz_results = get_student_quiz_results(student_id)

    if group_service_codes is not None:
        quiz_results = [
            row for row in quiz_results
            if row.get('course_type') in group_service_codes
        ]

    attendance_detail = get_student_attendance_detail(student_id)
    if group and attendance_detail:
        filtered_records = [
            row for row in attendance_detail.get('records', [])
            if row.get('group_id') == group.pk
        ]
        summary = {'present': 0, 'absent': 0, 'late': 0, 'total': len(filtered_records)}
        for row in filtered_records:
            if row['status'] in summary:
                summary[row['status']] += 1
        present = summary['present']
        total = summary['total']
        attendance_detail = {
            **attendance_detail,
            'summary': summary,
            'records': filtered_records,
            'attendance_rate': round(100 * present / total, 1) if total else None,
        }

    mock_stats_list = []
    mock_programs = get_student_mock_exam_programs(student_id)
    if group_service_codes is not None:
        mock_programs = [code for code in mock_programs if code in group_service_codes]
    if mock_programs and student_can_access_mock(student_id):
        mock_attempts = [
            serialize_mock_attempt_summary(attempt)
            for attempt in get_student_completed_mock_attempts(student_id)
            if getattr(attempt, 'exam_program', None) in mock_programs
        ]
        mock_stats_list = build_mock_stats_list(mock_attempts)

    return {
        'weekly_average': compute_weekly_average_stats(weekly_scores),
        'quiz_average': compute_quiz_average_stats(quiz_results),
        'attendance_stats': compute_attendance_stats(attendance_detail),
        'mock_stats_list': mock_stats_list,
    }


def build_student_performance_by_groups(
    student_id,
    *,
    parent_id=None,
    teacher_id=None,
    focus_group_id=None,
):
    """Per-group performance cards when a student belongs to multiple groups."""
    qs = StudyGroup.objects.filter(students__pk=student_id, is_active=True)
    if teacher_id:
        qs = qs.filter(teacher_id=teacher_id)
    if focus_group_id:
        qs = qs.filter(pk=focus_group_id)
    groups = list(qs.order_by('name').values('id', 'name'))
    if not groups:
        return []
    if teacher_id:
        return [
            {
                'group_id': group['id'],
                'group_name': group['name'],
                **_student_performance_snapshot(
                    student_id,
                    parent_id=parent_id,
                    group_id=group['id'],
                ),
            }
            for group in groups
        ]
    if len(groups) <= 1:
        return []
    return [
        {
            'group_id': group['id'],
            'group_name': group['name'],
            **_student_performance_snapshot(
                student_id,
                parent_id=parent_id,
                group_id=group['id'],
            ),
        }
        for group in groups
    ]


@cached_page_data(timeout='CACHE_TIMEOUT_MEDIUM')
def get_student_dashboard_data(request, student_id):
    from portals.utils.weekly_scores import get_student_weekly_scores

    group_ids = get_student_group_ids(student_id)
    return {
        'group_ids': group_ids,
        'schedule_count': len(get_student_schedules(student_id)),
        'lesson_count': len(get_student_lessons(student_id)),
        'weekly_score_count': len(get_student_weekly_scores(student_id)),
        'quiz_result_count': len(get_student_scores(student_id)),
        'mock_count': _student_mock_count(student_id),
        **_student_performance_snapshot(student_id),
    }


def _student_mock_count(student_id):
    from portals.models import IeltsMockTestAttempt
    from portals.utils.ielts_mock_test import (
        get_student_mock_exam_programs,
        student_can_access_mock,
    )

    if not get_student_mock_exam_programs(student_id) or not student_can_access_mock(student_id):
        return None
    return IeltsMockTestAttempt.objects.filter(
        student_id=student_id,
        status=IeltsMockTestAttempt.Status.COMPLETED,
    ).count()


def _parent_child_mock_count(student_id):
    return _student_mock_count(student_id)


@cached_page_data(timeout='CACHE_TIMEOUT_MEDIUM')
def get_parent_dashboard_data(request, parent_id):
    from portals.utils.weekly_scores import get_student_weekly_scores

    profile = (
        ParentProfile.objects.prefetch_related('students')
        .filter(pk=parent_id)
        .first()
    )
    if not profile:
        return {'children': []}
    children = []
    for student in profile.students.select_related('user').order_by('user__username', 'id'):
        group_ids = get_student_group_ids(student.pk)
        children.append({
            'student': serialize_student(student),
            'group_ids': group_ids,
            'schedule_count': len(get_student_schedules(student.pk)),
            'lesson_count': len(get_student_lessons(student.pk)),
            'score_count': len(get_student_weekly_scores(student.pk)),
            'quiz_count': len(get_student_quizzes(student.pk)),
            'attendance_count': len(get_parent_child_attendance(student.pk)),
            'quiz_result_count': len(get_parent_child_quiz_results(student.pk, parent_id=parent_id)),
            'mock_count': _parent_child_mock_count(student.pk),
            'quiz_results': latest_quiz_result_per_quiz(
                get_parent_child_quiz_results(student.pk, parent_id=parent_id),
                limit=5,
            ),
            **_student_performance_snapshot(student.pk, parent_id=parent_id),
        })
    return {'children': children}


def get_customer_mock_quiz_take_data(customer_id: int, quiz_id: int, *, mock_attempt_id: int):
    """Load quiz take payload for customer mock sections only."""
    from portals.utils.customer_mock import (
        customer_mock_allows_active_section_take,
        get_active_customer_mock_attempt,
    )

    if not customer_mock_allows_active_section_take(customer_id, mock_attempt_id, quiz_id):
        return None

    attempt = get_active_customer_mock_attempt(customer_id, mock_attempt_id)
    if not attempt:
        return None

    exam_program = attempt.exam_program
    quiz = (
        Quiz.objects.filter(
            pk=quiz_id,
            category__services__slug__in=quiz_category_slugs_for_portal_codes([exam_program]),
        )
        .distinct()
        .select_related('category')
        .prefetch_related(Prefetch('questions', queryset=QuizQuestion.objects.order_by('order', 'id')))
        .first()
    )
    if not quiz:
        return None

    if quiz.is_variant_quiz:
        questions = [q for q in quiz.questions.all() if q.is_answerable]
        if not questions:
            return None
        return {
            **serialize_quiz(quiz),
            'questions': [serialize_quiz_question_for_student(q) for q in questions],
            'view_only': False,
            'is_pending_review': False,
            'is_mock_section': True,
        }

    if quiz.is_reading:
        from portals.utils.quiz_reading import build_reading_sections_for_quiz, get_reading_questions_for_quiz

        if not get_reading_questions_for_quiz(quiz):
            return None
        sections = build_reading_sections_for_quiz(quiz.pk)
        flat_questions = [row for section in sections for row in section['questions']]
        response_ids = [row['id'] for row in flat_questions]
        return {
            **serialize_quiz(quiz),
            'questions': flat_questions,
            'reading_sections': sections,
            'response_question_ids': response_ids,
            'response_question_count': len(response_ids),
            'view_only': False,
            'is_pending_review': False,
            'is_mock_section': True,
        }

    if quiz.is_speaking:
        from portals.utils.quiz_speaking import (
            build_speaking_sections_for_quiz,
            estimate_speaking_quiz_seconds,
            get_speaking_questions_for_quiz,
        )

        if not get_speaking_questions_for_quiz(quiz):
            return None
        sections = build_speaking_sections_for_quiz(quiz.pk)
        flat_questions = [row for section in sections for row in section['questions']]
        response_ids = [row['id'] for row in flat_questions]
        estimated_total_seconds = estimate_speaking_quiz_seconds(sections)
        return {
            **serialize_quiz(quiz),
            'questions': flat_questions,
            'speaking_sections': sections,
            'response_question_ids': response_ids,
            'response_question_count': len(response_ids),
            'estimated_total_seconds': estimated_total_seconds,
            'estimated_total_minutes': max(1, round(estimated_total_seconds / 60)),
            'view_only': False,
            'is_pending_review': False,
            'is_mock_section': True,
        }

    if quiz.is_listening:
        from portals.utils.quiz_listening import (
            build_listening_sections_for_quiz,
            get_listening_questions_for_quiz,
        )

        if not get_listening_questions_for_quiz(quiz):
            return None
        sections = build_listening_sections_for_quiz(quiz.pk)
        flat_questions = [row for section in sections for row in section['questions']]
        response_ids = [row['id'] for row in flat_questions]
        return {
            **serialize_quiz(quiz),
            'questions': flat_questions,
            'listening_sections': sections,
            'response_question_ids': response_ids,
            'response_question_count': len(response_ids),
            'view_only': False,
            'is_pending_review': False,
            'is_mock_section': True,
        }

    if quiz.is_manual_grading and not quiz.is_listening and not quiz.is_speaking:
        questions = [q for q in quiz.questions.all() if q.is_answerable]
        if not questions:
            return None
        serialized_qs = [serialize_quiz_question_for_student(q) for q in questions]
        response_ids = [q['id'] for q in serialized_qs]
        return {
            **serialize_quiz(quiz),
            'questions': serialized_qs,
            'listening_sections': [],
            'response_question_ids': response_ids,
            'response_question_count': len(response_ids),
            'view_only': False,
            'is_mock_section': True,
        }

    return None
