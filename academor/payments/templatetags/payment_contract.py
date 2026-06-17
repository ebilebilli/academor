from django import template

from payments.contract import (
    build_package_details_summary,
    build_payment_clause,
    generate_contract_number,
    is_valid_contract_number,
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
