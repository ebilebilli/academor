"""Quiz category ↔ site course (Service) helpers."""

from portals.utils.portal_services import (
    classroom_service_portal_codes,
    expand_course_types_to_service_slugs,
    services_for_portal_codes,
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


def ensure_quiz_category(service_code, name):
    """Get or create a category for a portal service code and category name."""
    from portals.models import QuizCategory

    services = list(services_for_portal_codes([service_code]))
    if not services:
        raise ValueError(f'No active site service matches portal code {service_code!r}')

    category = (
        QuizCategory.objects.filter(name=name, services__in=services)
        .distinct()
        .first()
    )
    if category:
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
