"""Map active public site services (courses) to portal course_type codes."""

from django.utils.translation import get_language

# Ordered: more specific fragments first.
_SERVICE_COURSE_TYPE_FRAGMENTS = (
    ('only-speaking', 'speaking'),
    ('general-english', 'general_english'),
    ('general_english', 'general_english'),
    ('study-abroad', 'study_abroad'),
    ('study_abroad', 'study_abroad'),
    ('business-english', 'general_english'),
    ('ielts', 'ielts'),
    ('speaking', 'speaking'),
    ('gmat', 'gmat'),
    ('gre', 'gre'),
    ('sat', 'sat'),
    ('yos', 'yos'),
    ('yo-s', 'yos'),
    ('ales', 'ales'),
    ('xaric', 'study_abroad'),
    ('abroad', 'study_abroad'),
    ('english', 'general_english'),
)

DEFAULT_PORTAL_SERVICE_CODE = 'other'


def _normalize_lang(lang=None):
    raw = (lang or get_language() or 'az').split('-')[0].lower()
    return raw if raw in {'az', 'en', 'ru'} else 'az'


def _localized_service_name(service, lang=None):
    lang = _normalize_lang(lang)
    if lang == 'en':
        return (service.name_en or service.name_az or service.name_ru or service.slug or '').strip()
    if lang == 'ru':
        return (service.name_ru or service.name_az or service.name_en or service.slug or '').strip()
    return (service.name_az or service.name_en or service.name_ru or service.slug or '').strip()


def localized_service_name(service, lang=None):
    return _localized_service_name(service, lang)


def classroom_service_portal_codes(services):
    """Portal course_type codes inferred from linked site Service rows."""
    codes = set()
    for service in services:
        code = infer_course_type_for_service(service)
        if code:
            codes.add(code)
        slug = (service.slug or '').strip()
        if slug:
            codes.add(slug)
    return codes


def expand_course_types_to_service_slugs(course_types, lang=None):
    """Map portal course_type codes to active site service slugs for ORM filters."""
    slugs = set()
    for code in course_types or []:
        if not code:
            continue
        slugs.add(code)
        for service in get_active_services_queryset():
            if infer_course_type_for_service(service) == code and service.slug:
                slugs.add(service.slug)
    return sorted(slugs)


def services_for_portal_codes(codes):
    """Active site Service rows for portal course_type codes."""
    slugs = expand_course_types_to_service_slugs(codes)
    if not slugs:
        return get_active_services_queryset().none()
    return get_active_services_queryset().filter(slug__in=slugs)


def get_active_service_choices(lang=None):
    return [
        (service.slug, _localized_service_name(service, lang))
        for service in get_active_services_queryset()
        if service.slug
    ]


def infer_course_type_for_service(service):
    """Return portal course_type code for an active service, or None if unmappable."""
    parts = [
        (service.slug or '').lower(),
        (service.name_az or '').lower(),
        (service.name_en or '').lower(),
        (service.name_ru or '').lower(),
    ]
    for text in parts:
        if not text:
            continue
        normalized = text.replace('_', '-')
        for fragment, code in _SERVICE_COURSE_TYPE_FRAGMENTS:
            if fragment in normalized:
                return code
    return None


def get_active_services_queryset():
    from projects.models.service_models import Service

    return Service.objects.filter(is_active=True).order_by('order', 'id')


def get_active_course_type_codes():
    codes = set()
    for service in get_active_services_queryset():
        code = infer_course_type_for_service(service)
        if code:
            codes.add(code)
    return codes


def get_active_course_type_choices(lang=None):
    """Unique course types from active site services, labeled with the service name."""
    choices = []
    seen = set()
    for service in get_active_services_queryset():
        code = infer_course_type_for_service(service)
        if not code or code in seen:
            continue
        label = _localized_service_name(service, lang)
        if not label:
            continue
        seen.add(code)
        choices.append((code, label))
    return choices


def get_course_type_label_map(lang=None):
    labels = {code: str(label) for code, label in get_active_course_type_choices(lang)}
    for slug, name in get_active_service_choices(lang):
        labels.setdefault(slug, str(name))
    return labels


def resolve_course_type_label(code, lang=None):
    if not code:
        return ''
    return get_course_type_label_map(lang).get(code, code)


def is_active_portal_course_type(code):
    return bool(code) and code in get_active_course_type_codes()
