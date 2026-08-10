"""Map active public site services (courses) to portal course_type codes."""

import threading
import time
from typing import NamedTuple

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

# The lookup helpers below run once per quiz / result / group row, so reading
# ``projects_service`` directly turned a tiny static table into ~1000 identical
# queries on a single portal page. The snapshot below is rebuilt on every
# request boundary (and whenever a Service row changes), so a snapshot never
# outlives the request that built it.
_SNAPSHOT_TTL_SECONDS = 30
_snapshot_state = threading.local()


class _ServiceRow(NamedTuple):
    pk: int
    slug: str
    code: str
    name_az: str
    name_en: str
    name_ru: str


class _ServiceSnapshot:
    """Precomputed portal-code lookups for the active site services."""

    def __init__(self, rows):
        self.rows = rows
        self.by_pk = {row.pk: row for row in rows}
        self.code_slugs = {}
        self.active_codes = set()
        for row in rows:
            if row.code:
                bucket = self.code_slugs.setdefault(row.code, {row.code})
                if row.slug:
                    bucket.add(row.slug)
                self.active_codes.add(row.code)
            if row.slug:
                self.active_codes.add(row.slug)
        self._label_maps = {}
        self._choices = {}

    def slugs_for_code(self, code):
        return self.code_slugs.get(code) or {code}

    def label_map(self, lang):
        cached = self._label_maps.get(lang)
        if cached is None:
            labels = {}
            for row in self.rows:
                name = _localized_row_name(row, lang)
                if not name:
                    continue
                if row.slug:
                    labels[row.slug] = name
                if row.code:
                    labels.setdefault(row.code, name)
            cached = labels
            self._label_maps[lang] = cached
        return cached

    def choices(self, lang):
        cached = self._choices.get(lang)
        if cached is None:
            cached = [
                (row.slug, _localized_row_name(row, lang))
                for row in self.rows
                if row.slug
            ]
            self._choices[lang] = cached
        return cached


def _localized_row_name(row, lang):
    lang = _normalize_lang(lang)
    if lang == 'en':
        candidates = (row.name_en, row.name_az, row.name_ru)
    elif lang == 'ru':
        candidates = (row.name_ru, row.name_az, row.name_en)
    else:
        candidates = (row.name_az, row.name_en, row.name_ru)
    for candidate in (*candidates, row.slug):
        text = (candidate or '').strip()
        if text:
            return text
    return ''


def _build_snapshot():
    rows = []
    for service in get_active_services_queryset().only(
        'id',
        'slug',
        'name_az',
        'name_en',
        'name_ru',
        'order',
    ):
        rows.append(_ServiceRow(
            pk=service.pk,
            slug=(service.slug or '').strip(),
            code=infer_course_type_for_service(service) or '',
            name_az=service.name_az or '',
            name_en=service.name_en or '',
            name_ru=service.name_ru or '',
        ))
    return _ServiceSnapshot(rows)


def _snapshot():
    snapshot = getattr(_snapshot_state, 'snapshot', None)
    expires_at = getattr(_snapshot_state, 'expires_at', 0.0)
    if snapshot is None or time.monotonic() >= expires_at:
        snapshot = _build_snapshot()
        _snapshot_state.snapshot = snapshot
        _snapshot_state.expires_at = time.monotonic() + _SNAPSHOT_TTL_SECONDS
    return snapshot


def reset_active_service_snapshot(**_kwargs):
    """Drop the memoized snapshot (request boundaries and Service writes)."""
    _snapshot_state.snapshot = None
    _snapshot_state.expires_at = 0.0


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
            continue
        slug = (service.slug or '').strip()
        if slug:
            codes.add(slug)
    return codes


def normalize_portal_course_type(code):
    """Map a portal code or active service slug to the canonical course_type."""
    if not code:
        return ''
    snapshot = _snapshot()
    if code in snapshot.active_codes:
        return code
    for row in snapshot.rows:
        if row.slug and row.slug == code:
            if row.code and row.code in snapshot.active_codes:
                return row.code
            if row.slug in snapshot.active_codes:
                return row.slug
    return code


def expand_course_types_to_service_slugs(course_types, lang=None):
    """Map portal course_type codes to active site service slugs for ORM filters."""
    del lang  # reserved for callers that pass UI language
    if not course_types:
        return []
    snapshot = _snapshot()
    slugs = set()
    for code in course_types:
        if not code:
            continue
        slugs.update(snapshot.slugs_for_code(code))
    return sorted(slugs)


def portal_course_keys_overlap(left_keys, right_keys):
    """True when two portal key sets share an active site service (code or slug)."""
    if not left_keys or not right_keys:
        return False
    snapshot = _snapshot()
    left = set()
    for code in left_keys:
        if code:
            left.update(snapshot.slugs_for_code(code))
    if not left:
        return False
    for code in right_keys:
        if code and not left.isdisjoint(snapshot.slugs_for_code(code)):
            return True
    return False


def services_for_portal_codes(codes):
    """Active site Service rows for portal course_type codes."""
    slugs = expand_course_types_to_service_slugs(codes)
    if not slugs:
        return get_active_services_queryset().none()
    return get_active_services_queryset().filter(slug__in=slugs)


def portal_codes_for_service_ids(service_ids):
    """Portal course_type codes inferred from site Service primary keys."""
    ids = []
    for pk in service_ids or []:
        try:
            ids.append(int(pk))
        except (TypeError, ValueError):
            continue
    if not ids:
        return []
    snapshot = _snapshot()
    codes = set()
    for pk in ids:
        row = snapshot.by_pk.get(pk)
        if not row:
            continue
        if row.code:
            codes.add(row.code)
        elif row.slug:
            codes.add(row.slug)
    return sorted(codes)


def get_active_service_choices(lang=None):
    return list(_snapshot().choices(_normalize_lang(lang)))


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
    """Active portal keys: inferred course codes plus every active service slug.

    Role / enrollment forms store the service slug as the key so each site
    service is selectable. Legacy inferred codes (``ielts``, ``sat``, …) stay
    valid for existing rows and filters.
    """
    return set(_snapshot().active_codes)


def get_active_course_type_choices(lang=None):
    """One choice per active site service (value = slug, label = localized name)."""
    return get_active_service_choices(lang)


def get_course_type_label_map(lang=None):
    return dict(_snapshot().label_map(_normalize_lang(lang)))


def resolve_course_type_label(code, lang=None):
    if not code:
        return ''
    return _snapshot().label_map(_normalize_lang(lang)).get(code, code)


def is_active_portal_course_type(code):
    return bool(code) and code in _snapshot().active_codes
