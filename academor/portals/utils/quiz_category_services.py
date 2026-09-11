"""Quiz category ↔ site course (Service) helpers."""

from django.db.models import Q

from portals.utils.portal_services import (
    classroom_service_portal_codes,
    expand_course_types_to_service_slugs,
    localized_service_name,
    reset_active_service_snapshot,
    services_for_portal_codes,
)

SAT_MATH_SECTIONS = frozenset({'algebra', 'geometry_data', 'math'})
SAT_VERBAL_SECTIONS = frozenset({'reading', 'writing', 'reading_writing'})

_TRACK_FAMILIES = (
    {
        'generic': 'sat',
        'tracks': (
            {
                'code': 'sat-math',
                'slugs': ('sat-math',),
                'name_needles': ('sat math',),
                'category_hints': ('math',),
            },
            {
                'code': 'sat-verbal',
                'slugs': ('sat-verbal',),
                'name_needles': ('sat verbal',),
                'category_hints': ('verbal', 'reading', 'writing'),
            },
        ),
    },
    {
        'generic': 'gre',
        'tracks': (
            {
                'code': 'gre-math',
                'slugs': ('gre-math',),
                'name_needles': ('gre math',),
                'category_hints': ('math',),
            },
            {
                'code': 'gre-verbal',
                'slugs': ('gre-verbal',),
                'name_needles': ('gre verbal',),
                'category_hints': ('verbal',),
            },
        ),
    },
)


def quiz_category_portal_codes(category):
    if not category or not category.pk:
        return []
    if hasattr(category, '_prefetched_objects_cache') and 'services' in category._prefetched_objects_cache:
        services = category.services.all()
    else:
        services = category.services.all()
    return sorted(classroom_service_portal_codes(services))


def quiz_category_primary_portal_code(category):
    codes = quiz_category_portal_codes(category)
    return codes[0] if codes else ''


def quiz_category_display_name(category, lang=None):
    """Portal title for a quiz category.

    The admin-entered name always wins. Only when it's left blank do we fall
    back to the linked site service name(s) — matching the admin form, which
    auto-fills the name from the first selected service when left empty.
    """
    if not category:
        return ''
    stored_name = (category.name or '').strip()
    if stored_name:
        return stored_name
    services = []
    if getattr(category, 'pk', None):
        services = list(category.services.all())
    names = []
    seen = set()
    for service in services:
        name = localized_service_name(service, lang)
        key = name.casefold()
        if name and key not in seen:
            seen.add(key)
            names.append(name)
    if names:
        return ', '.join(names)
    return stored_name


def quiz_category_slugs_for_portal_codes(course_codes):
    return expand_course_types_to_service_slugs(course_codes)


def quiz_categories_for_portal_codes(course_codes):
    from portals.models import QuizCategory

    slugs = quiz_category_slugs_for_portal_codes(course_codes)
    if not slugs:
        return QuizCategory.objects.none()
    return QuizCategory.objects.filter(services__slug__in=slugs).distinct()


def quizzes_for_portal_codes(course_codes):
    from portals.models import Quiz

    slugs = quiz_category_slugs_for_portal_codes(course_codes)
    if not slugs:
        return Quiz.objects.none()
    return Quiz.objects.filter(category__services__slug__in=slugs).distinct()


def category_has_portal_code(category, course_codes):
    if not category or not course_codes:
        return False
    from portals.utils.portal_services import portal_course_keys_overlap

    return portal_course_keys_overlap(quiz_category_portal_codes(category), course_codes)


def resolve_quiz_loader_service_code(service_code, category_name=''):
    """Map generic SAT/GRE loader codes to the verbal/math site service when present."""
    code = (service_code or '').strip()
    if not code:
        return code
    name = (category_name or '').strip().lower()
    normalized = code.lower().replace('_', '-')
    for family in _TRACK_FAMILIES:
        if normalized != family['generic']:
            continue
        for track in family['tracks']:
            if not any(hint in name for hint in track['category_hints']):
                continue
            if family['generic'] == 'sat' and track['code'] == 'sat-math' and 'verbal' in name:
                continue
            if list(services_for_portal_codes([track['code']])):
                return track['code']
    return code


def _sync_category_services(category, services):
    desired_ids = {service.pk for service in services}
    current_ids = set(category.services.values_list('pk', flat=True))
    if current_ids != desired_ids:
        category.services.set(services)


def ensure_quiz_category(service_code, name):
    """Get or create a category for a portal service code and category name."""
    from portals.models import QuizCategory

    resolved_code = resolve_quiz_loader_service_code(service_code, name)
    services = list(services_for_portal_codes([resolved_code]))
    if not services:
        raise ValueError(f'No active site service matches portal code {service_code!r}')

    category = (
        QuizCategory.objects.filter(name=name, services__in=services)
        .distinct()
        .first()
    )
    if category:
        _sync_category_services(category, services)
        return category, False

    # Adopt an orphan category with the same name (left over from loaders
    # that created categories without linking services) instead of duplicating.
    orphan = (
        QuizCategory.objects.filter(name=name, services__isnull=True)
        .first()
    )
    if orphan:
        orphan.services.set(services)
        return orphan, False

    category = QuizCategory.objects.create(name=name)
    category.services.set(services)
    return category, True


def quiz_belongs_to_sat_math(quiz):
    if getattr(quiz, 'is_math', False):
        return True
    section = (getattr(quiz, 'sat_section', None) or '').strip().lower()
    if section in SAT_MATH_SECTIONS:
        return True
    topic = (getattr(quiz, 'topic', None) or '').lower()
    return 'sat' in topic and 'math' in topic


def quiz_belongs_to_sat_verbal(quiz):
    if quiz_belongs_to_sat_math(quiz):
        return False
    section = (getattr(quiz, 'sat_section', None) or '').strip().lower()
    if section in SAT_VERBAL_SECTIONS:
        return True
    topic = (getattr(quiz, 'topic', None) or '').lower()
    category = getattr(quiz, 'category', None)
    category_name = (getattr(category, 'name', None) or '').lower()
    blob = f'{topic} {category_name}'
    return any(token in blob for token in ('verbal', 'reading', 'writing'))


def _find_track_service(slugs, name_needles):
    from projects.models.service_models import Service

    qs = Service.objects.filter(is_active=True).exclude(
        Q(ielts_mock_test=True) | Q(sat_mock_test=True),
    )
    for slug in slugs:
        row = qs.filter(slug=slug).first()
        if row:
            return row
    for needle in name_needles:
        row = qs.filter(
            Q(name_en__icontains=needle)
            | Q(name_az__icontains=needle)
            | Q(name_ru__icontains=needle)
        ).first()
        if row:
            return row
    return None


def _category_name_looks_like_math(name):
    text = (name or '').lower()
    return 'math' in text and 'verbal' not in text


def relink_sat_math_and_verbal_categories():
    """Keep SAT Math quizzes on the math service; SAT Verbal stays verbal-only."""
    from portals.models import Quiz, QuizCategory

    reset_active_service_snapshot()
    verbal_service = _find_track_service(('sat-verbal',), ('sat verbal', 'sat-verbal'))
    math_service = _find_track_service(('sat-math',), ('sat math', 'sat-math'))
    if not verbal_service or not math_service or verbal_service.pk == math_service.pk:
        return {'skipped': True}

    sat_categories = list(
        QuizCategory.objects.filter(Q(services=verbal_service) | Q(services=math_service))
        .prefetch_related('services')
        .distinct()
    )
    math_category = next(
        (row for row in sat_categories if _category_name_looks_like_math(row.name)),
        None,
    )
    if math_category is None:
        math_category, _ = ensure_quiz_category(
            'sat-math',
            math_service.name_az or math_service.name_en or 'SAT Math',
        )
        if math_category not in sat_categories:
            sat_categories.append(math_category)

    verbal_home = next(
        (
            row
            for row in sat_categories
            if row.pk != math_category.pk and not _category_name_looks_like_math(row.name)
        ),
        None,
    )

    moved_math = 0
    moved_verbal = 0
    quiz_ids = Quiz.objects.filter(category__in=sat_categories).values_list('pk', flat=True)
    quizzes = Quiz.objects.filter(pk__in=quiz_ids).select_related('category')
    for quiz in quizzes:
        if quiz_belongs_to_sat_math(quiz):
            if quiz.category_id != math_category.pk:
                quiz.category = math_category
                quiz.save(update_fields=['category'])
                moved_math += 1
            continue
        if verbal_home and quiz.category_id == math_category.pk and quiz_belongs_to_sat_verbal(quiz):
            quiz.category = verbal_home
            quiz.save(update_fields=['category'])
            moved_verbal += 1

    if math_category.parent_id:
        math_category.parent = None
        math_category.save(update_fields=['parent'])
    math_category.services.set([math_service])
    for category in sat_categories:
        if category.pk == math_category.pk:
            continue
        if _category_name_looks_like_math(category.name):
            if category.parent_id:
                category.parent = None
                category.save(update_fields=['parent'])
            category.services.set([math_service])
            continue
        category.services.set([verbal_service])

    return {
        'skipped': False,
        'math_category_id': math_category.pk,
        'moved_math': moved_math,
        'moved_verbal': moved_verbal,
    }


def _group_track_codes_for_services(services, family):
    codes = set()
    has_generic = False
    track_by_slug = {}
    track_by_needle = []
    for track in family['tracks']:
        for slug in track['slugs']:
            track_by_slug[slug] = track['code']
        for needle in track['name_needles']:
            track_by_needle.append((needle, track['code']))
    for service in services:
        if getattr(service, 'is_mock_test', False):
            has_generic = True
            continue
        slug = (getattr(service, 'slug', None) or '').strip().lower()
        if slug in track_by_slug:
            codes.add(track_by_slug[slug])
            continue
        blob = ' '.join(
            (
                slug.replace('-', ' '),
                (getattr(service, 'name_az', None) or ''),
                (getattr(service, 'name_en', None) or ''),
                (getattr(service, 'name_ru', None) or ''),
            )
        ).lower()
        matched = False
        for needle, code in track_by_needle:
            if needle in blob:
                codes.add(code)
                matched = True
                break
        if not matched:
            from portals.utils.portal_services import infer_course_type_for_service

            inferred = infer_course_type_for_service(service)
            if inferred == family['generic']:
                has_generic = True
            elif inferred:
                codes.add(inferred)
    return codes, has_generic


def expand_generic_exam_track_enrollments():
    """Replace collapsed sat/gre enrollments with verbal/math slugs from group courses."""
    from portals.models import StudentCourseSpecialization, StudyGroup, TeacherCourseSpecialization

    reset_active_service_snapshot()
    created = 0
    removed = 0
    for family in _TRACK_FAMILIES:
        generic = family['generic']
        track_codes = {track['code'] for track in family['tracks']}
        if not any(list(services_for_portal_codes([code])) for code in track_codes):
            continue

        student_rows = list(
            StudentCourseSpecialization.objects.filter(course_type=generic, is_active=True)
        )
        for row in student_rows:
            groups = StudyGroup.objects.filter(students=row.student).prefetch_related('courses')
            wanted = set()
            keep_generic = False
            for group in groups:
                codes, has_generic = _group_track_codes_for_services(group.courses.all(), family)
                wanted.update(codes)
                keep_generic = keep_generic or has_generic
            if not wanted:
                continue
            for code in wanted:
                _, was_created = StudentCourseSpecialization.objects.update_or_create(
                    student_id=row.student_id,
                    course_type=code,
                    defaults={'is_active': True},
                )
                if was_created:
                    created += 1
            if not keep_generic:
                row.delete()
                removed += 1

        teacher_rows = list(TeacherCourseSpecialization.objects.filter(course_type=generic))
        for row in teacher_rows:
            groups = StudyGroup.objects.filter(teacher_id=row.teacher_id).prefetch_related('courses')
            wanted = set()
            keep_generic = False
            for group in groups:
                codes, has_generic = _group_track_codes_for_services(group.courses.all(), family)
                wanted.update(codes)
                keep_generic = keep_generic or has_generic
            if not wanted:
                continue
            for code in wanted:
                _, was_created = TeacherCourseSpecialization.objects.get_or_create(
                    teacher_id=row.teacher_id,
                    course_type=code,
                )
                if was_created:
                    created += 1
            if not keep_generic:
                row.delete()
                removed += 1

    return {'created': created, 'removed': removed}
