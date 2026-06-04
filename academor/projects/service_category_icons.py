"""Font Awesome 5 icons for service cards — aligned with Academor SEO course/exam offerings."""

from django.utils.translation import gettext_lazy as _

# Homepage + /courses/ card icons (General English, IELTS, GMAT, GRE, Speaking, YÖS, ALES, abroad…)
SERVICE_CATEGORY_ICON_CHOICES = [
    ('', _('Default — open book')),
    ('fa-book-open', _('General English / language course')),
    ('fa-language', _('English / language learning')),
    ('fa-comments', _('Speaking / conversation')),
    ('fa-microphone-alt', _('Speaking practice / Only Speaking')),
    ('fa-headphones', _('Listening practice')),
    ('fa-pen', _('Writing skills')),
    ('fa-certificate', _('IELTS / certificate program')),
    ('fa-file-alt', _('Exam preparation (general)')),
    ('fa-chart-line', _('GMAT / GRE / test strategy')),
    ('fa-calculator', _('GMAT — quantitative')),
    ('fa-graduation-cap', _('GRE / university admission test')),
    ('fa-university', _('YÖS / university placement')),
    ('fa-user-graduate', _('ALES / academic exam')),
    ('fa-pencil-alt', _('SAT / standardized test')),
    ('fa-globe-americas', _('Study abroad')),
    ('fa-plane-departure', _('Study abroad / international')),
    ('fa-laptop', _('Online lessons')),
    ('fa-users', _('Group classes')),
    ('fa-user', _('Private / individual lessons')),
    ('fa-briefcase', _('Business English')),
    ('fa-child', _('Kids / young learners')),
    ('fa-chalkboard-teacher', _('Teaching / instruction')),
    ('fa-star', _('Featured / premium program')),
]

SERVICE_CATEGORY_ICON_DEFAULT = 'fa-book-open'

# Optional slug hints when card_icon is empty (matches common Academor program URLs).
_SLUG_ICON_HINTS = (
    ('ielts', 'fa-certificate'),
    ('speaking', 'fa-comments'),
    ('only-speaking', 'fa-microphone-alt'),
    ('gmat', 'fa-chart-line'),
    ('gre', 'fa-graduation-cap'),
    ('yos', 'fa-university'),
    ('ales', 'fa-user-graduate'),
    ('sat', 'fa-pencil-alt'),
    ('general', 'fa-book-open'),
    ('business', 'fa-briefcase'),
    ('online', 'fa-laptop'),
    ('kid', 'fa-child'),
    ('uşaq', 'fa-child'),
    ('abroad', 'fa-globe-americas'),
    ('xaric', 'fa-plane-departure'),
)


def resolve_service_category_icon(card_icon: str = '', slug: str = '') -> str:
    """Return a Font Awesome 5 class name (no leading ``fa`` wrapper)."""
    value = (card_icon or '').strip()
    if value.startswith('fa '):
        value = value.replace('fa ', 'fa-', 1).replace(' ', '')
    if value.startswith('fa-'):
        return value

    slug_lower = (slug or '').lower()
    for fragment, icon in _SLUG_ICON_HINTS:
        if fragment in slug_lower:
            return icon

    return SERVICE_CATEGORY_ICON_DEFAULT
