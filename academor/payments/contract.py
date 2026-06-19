"""Training agreement text for course checkout (i18n legal copy + dynamic package fields)."""

import re
import secrets

from django.template.loader import render_to_string
from django.utils import timezone, translation
from django.utils.translation import get_language, gettext as _, ngettext

from payments.catalog import course_display_name
from projects.utils.queries import serialize_price_package

CONTRACT_NUMBER_RE = re.compile(r'^\d{4}-\d{6}$')


def generate_contract_number() -> str:
    """Random agreement number for display (e.g. 2026-482917)."""
    year = timezone.localdate().year
    suffix = secrets.randbelow(900_000) + 100_000
    return f'{year}-{suffix}'


def is_valid_contract_number(value: str) -> bool:
    return bool(value and CONTRACT_NUMBER_RE.match(value.strip()))


def _contract_lang(lang: str | None = None) -> str:
    return (lang or get_language() or 'az')[:2]


def _format_months_label(package: dict, lang: str) -> str:
    months_display = (package.get('months_display') or '').strip()
    if months_display:
        return months_display
    months = package.get('months')
    if not months:
        return ''
    with translation.override(lang):
        return ngettext(
            '%(counter)s month',
            '%(counter)s months',
            months,
        ) % {'counter': months}


def _format_lessons_label(package: dict, lang: str) -> str:
    lesson_count = package.get('lesson_count')
    if not lesson_count:
        return ''
    with translation.override(lang):
        return ngettext(
            '%(counter)s lesson',
            '%(counter)s lessons',
            lesson_count,
        ) % {'counter': lesson_count}


def build_package_details_summary(package: dict, lang: str | None = None) -> str:
    """Comma-separated package facts for clause 1.1 (e.g. 1 ay, 8 dərs)."""
    lang = _contract_lang(lang)
    lesson_minutes_display = (package.get('lesson_minutes_display') or '').strip()

    with translation.override(lang):
        parts = []
        months_label = _format_months_label(package, lang)
        lessons_label = _format_lessons_label(package, lang)
        if months_label:
            parts.append(months_label)
        if lessons_label:
            parts.append(lessons_label)
        if lesson_minutes_display:
            parts.append(
                _('%(minutes)s per lesson') % {'minutes': lesson_minutes_display}
            )
        return ', '.join(parts)


def build_payment_clause(package: dict, lang: str | None = None) -> str:
    """Clause 2.1 — amount, months, and lessons from serialized price package."""
    lang = _contract_lang(lang)
    price = package.get('price_display') or ''
    lesson_minutes_display = (package.get('lesson_minutes_display') or '').strip()

    with translation.override(lang):
        period = _format_months_label(package, lang) or _('the agreed period')
        lessons = _format_lessons_label(package, lang) or _('the agreed number of lessons')

        if lesson_minutes_display:
            minutes_clause = _(
                ', each lesson lasting %(minutes)s'
            ) % {'minutes': lesson_minutes_display}
        else:
            minutes_clause = ''

        return _(
            'Upon payment of %(price)s AZN, the Learner is registered for a '
            '%(period)s training programme comprising %(lessons)s%(minutes_clause)s.'
        ) % {
            'price': price,
            'period': period,
            'lessons': lessons,
            'minutes_clause': minutes_clause,
        }


def build_contract_context(
    *,
    course,
    package,
    contract_number: str,
    buyer_name: str = '',
    buyer_phone: str = '',
    contract_date=None,
    lang: str | None = None,
):
    lang = _contract_lang(lang)
    package_dict = (
        serialize_price_package(package, lang=lang) if package else {}
    )
    return {
        'course': {'name': course_display_name(course, lang)},
        'package': package_dict,
        'package_details': build_package_details_summary(package_dict, lang=lang),
        'contract_number': contract_number,
        'payment_clause': build_payment_clause(package_dict, lang=lang),
        'buyer_name': (buyer_name or '').strip(),
        'buyer_phone': (buyer_phone or '').strip(),
        'contract_date': contract_date,
    }


def render_course_contract_html(
    *,
    course,
    package,
    contract_number: str,
    buyer_name: str = '',
    buyer_phone: str = '',
    contract_date=None,
    lang: str | None = None,
):
    lang = _contract_lang(lang)
    context = build_contract_context(
        course=course,
        package=package,
        contract_number=contract_number,
        buyer_name=buyer_name,
        buyer_phone=buyer_phone,
        contract_date=contract_date,
        lang=lang,
    )
    with translation.override(lang):
        return render_to_string(
            'includes/course_payment_contract.html',
            context,
        )
