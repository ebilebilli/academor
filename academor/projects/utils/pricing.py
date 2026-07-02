"""
Sale discount helpers — shared by public serialization and payment catalog.

Active sales exclude expired rows (``end_date`` before today).

``get_active_sale_discounts_by_service_id`` / ``get_active_sale_discounts_by_package_id``
are fresh DB reads; bump via ``invalidate_sale_cache()`` in projects.signals
(Sale save/delete/M2M, Media→Sale, SaleAdmin list_editable) and global bumps on
Service / CoursePricePackage changes.
"""

from decimal import Decimal, ROUND_HALF_UP

from django.db.models import Q
from django.utils import timezone

from projects.models import Sale


def format_decimal_price(price) -> str:
    price = Decimal(price)
    if price == price.to_integral_value():
        return str(int(price))
    return str(price.quantize(Decimal('0.01')).normalize())


def apply_percent_discount(amount, percent: int) -> Decimal:
    amount = Decimal(amount)
    factor = Decimal(100 - int(percent)) / Decimal(100)
    return (amount * factor).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def _active_sales_queryset():
    today = timezone.localdate()
    return (
        Sale.objects.filter(is_active=True)
        .filter(Q(end_date__isnull=True) | Q(end_date__gte=today))
        .exclude(percent__isnull=True)
        .order_by('-percent', '-created_at')
    )


def fetch_active_sale_discounts_by_service_id() -> dict[int, int]:
    """Map service PK → discount percent (highest active sale wins). Fresh DB read."""
    discounts: dict[int, int] = {}
    sales = _active_sales_queryset().prefetch_related('services')
    for sale in sales:
        services = list(sale.services.all())
        if not services:
            continue
        for service in services:
            service_id = service.pk
            current = discounts.get(service_id)
            if current is None or sale.percent > current:
                discounts[service_id] = sale.percent
    return discounts


def fetch_active_sale_discounts_by_package_id() -> dict[int, int]:
    """Map price-package PK → discount percent (highest active sale wins). Fresh DB read."""
    discounts: dict[int, int] = {}
    sales = _active_sales_queryset().prefetch_related('price_packages')
    for sale in sales:
        packages = list(sale.price_packages.all())
        if not packages:
            continue
        for package in packages:
            package_id = package.pk
            current = discounts.get(package_id)
            if current is None or sale.percent > current:
                discounts[package_id] = sale.percent
    return discounts


def get_active_sale_discounts_by_service_id() -> dict[int, int]:
    """Fresh service discount map — not cached (time-bound sales + multi-worker LocMem safety)."""
    return fetch_active_sale_discounts_by_service_id()


def get_active_sale_discounts_by_package_id() -> dict[int, int]:
    """Fresh package discount map — not cached."""
    return fetch_active_sale_discounts_by_package_id()


def get_sale_percent_for_service(service_id, discounts_map=None) -> int | None:
    if discounts_map is None:
        discounts_map = get_active_sale_discounts_by_service_id()
    return discounts_map.get(service_id)


def get_sale_percent_for_package(
    package,
    service_discounts_map=None,
    package_discounts_map=None,
) -> int | None:
    if package_discounts_map is None:
        package_discounts_map = get_active_sale_discounts_by_package_id()
    if service_discounts_map is None:
        service_discounts_map = get_active_sale_discounts_by_service_id()

    package_percent = package_discounts_map.get(package.pk)
    service_percent = service_discounts_map.get(package.course_id)
    if package_percent is None:
        return service_percent
    if service_percent is None:
        return package_percent
    return max(package_percent, service_percent)


def package_payable_amount(
    package,
    discounts_map=None,
    package_discounts_map=None,
) -> Decimal:
    base = Decimal(package.price)
    percent = get_sale_percent_for_package(
        package,
        service_discounts_map=discounts_map,
        package_discounts_map=package_discounts_map,
    )
    if percent:
        return apply_percent_discount(base, percent)
    return base
