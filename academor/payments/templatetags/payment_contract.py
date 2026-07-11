from django import template

from payments.contract import (
    build_package_details_summary,
    build_payment_clause,
    generate_contract_number,
    is_valid_contract_number,
)
from payments.mock_contract import (
    build_mock_payment_clause,
)

register = template.Library()


@register.inclusion_tag('includes/course_payment_contract.html')
def course_payment_contract(course, package, contract_number=None):
    number = contract_number or generate_contract_number()
    return {
        'course': course,
        'package': package,
        'package_details': build_package_details_summary(package),
        'contract_number': number,
        'payment_clause': build_payment_clause(package),
        'buyer_name': '',
        'buyer_phone': '',
        'contract_date': None,
    }


@register.inclusion_tag('includes/mock_payment_contract.html')
def mock_payment_contract(package, contract_number=None):
    from payments.mock_contract import _package_dict
    from django.utils.translation import get_language

    lang = (get_language() or 'az')[:2]
    number = contract_number or generate_contract_number()
    pkg = _package_dict(package, lang)
    return {
        'package': pkg,
        'package_name': pkg.get('name') or '',
        'contract_number': number,
        'payment_clause': build_mock_payment_clause(pkg, lang=lang),
        'buyer_name': '',
        'buyer_phone': '',
        'contract_date': None,
    }
