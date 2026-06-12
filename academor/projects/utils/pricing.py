"""
Sale discount helpers — shared by public serialization and payment catalog.

`get_active_sale_discounts_by_service_id` is @cached_query; bump via Sale signals in
projects.signals (post_save/post_delete/M2M on Sale.services).
"""

from decimal import Decimal, ROUND_HALF_UP

from projects.models import Sale
from projects.utils.cache_utils import cached_query


def format_decimal_price(price) -> str:
    price = Decimal(price)
    if price == price.to_integral_value():
        return str(int(price))
    return str(price).quantize(Decimal('0.01')).normalize()


def apply_percent_discount(amount, percent: int) -> Decimal:
    amount = Decimal(amount)
    factor = Decimal(100 - int(percent)) / Decimal(100)
    return (amount * factor).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def fetch_active_sale_discounts_by_service_id() -> dict[int, int]:
    """Map service PK → discount percent (highest active sale wins). Fresh DB read."""
    discounts: dict[int, int] = {}
    sales = (
        Sale.objects.filter(is_active=True, apply_to_service_prices=True)
        .prefetch_related('services')
        .order_by('-percent', '-created_at')
    )
    for sale in sales:
        for service in sale.services.all():
            service_id = service.pk
            current = discounts.get(service_id)
            if current is None or sale.percent > current:
                discounts[service_id] = sale.percent
    return discounts


@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_active_sale_discounts_by_service_id() -> dict[int, int]:
    """Cached wrapper for templates/lists; checkout uses ``fetch_*`` instead."""
    return fetch_active_sale_discounts_by_service_id()


def get_sale_percent_for_service(service_id, discounts_map=None) -> int | None:
    if discounts_map is None:
        discounts_map = get_active_sale_discounts_by_service_id()
    return discounts_map.get(service_id)


def package_payable_amount(package, discounts_map=None) -> Decimal:
    base = Decimal(package.price)
    percent = get_sale_percent_for_service(package.course_id, discounts_map)
    if percent:
        return apply_percent_discount(base, percent)
    return base
