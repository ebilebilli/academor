"""Universal mock test payment agreement (package name from price card)."""

from django.template.loader import render_to_string
from django.utils import translation
from django.utils.translation import gettext as _

from payments.contract import _contract_lang
from projects.utils.pricing import format_decimal_price


def _package_dict(package, lang: str) -> dict:
    if isinstance(package, dict):
        return package
    if hasattr(package, 'localized_name'):
        name = package.localized_name(lang)
    else:
        from projects.utils.queries import price_package_display_name
        name = price_package_display_name(package, lang)
    return {
        'id': package.pk,
        'name': name,
        'credits': getattr(package, 'credits', None),
        'price': package.price,
        'price_display': format_decimal_price(package.price),
    }


def build_mock_payment_clause(package: dict, lang: str | None = None) -> str:
    lang = _contract_lang(lang)
    pkg = package if isinstance(package, dict) else _package_dict(package, lang)
    price = pkg.get('price_display') or ''
    package_name = pkg.get('name') or _('Selected package')

    with translation.override(lang):
        return _(
            'Upon payment of %(price)s AZN for «%(package)s», the Customer receives '
            'access to the selected mock test package on the Academor customer portal.'
        ) % {
            'price': price,
            'package': package_name,
        }


def build_mock_contract_context(
    *,
    package,
    contract_number: str,
    buyer_name: str = '',
    buyer_phone: str = '',
    contract_date=None,
    lang: str | None = None,
):
    lang = _contract_lang(lang)
    pkg = _package_dict(package, lang)
    return {
        'package': pkg,
        'package_name': pkg.get('name') or '',
        'contract_number': contract_number,
        'payment_clause': build_mock_payment_clause(pkg, lang=lang),
        'buyer_name': (buyer_name or '').strip(),
        'buyer_phone': (buyer_phone or '').strip(),
        'contract_date': contract_date,
    }


def render_mock_contract_html(
    *,
    package,
    contract_number: str,
    buyer_name: str = '',
    buyer_phone: str = '',
    contract_date=None,
    lang: str | None = None,
):
    lang = _contract_lang(lang)
    context = build_mock_contract_context(
        package=package,
        contract_number=contract_number,
        buyer_name=buyer_name,
        buyer_phone=buyer_phone,
        contract_date=contract_date,
        lang=lang,
    )
    with translation.override(lang):
        return render_to_string(
            'includes/mock_payment_contract.html',
            context,
        )
