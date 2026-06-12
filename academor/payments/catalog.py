"""Resolve payable courses and price packages; amount always comes from the database."""

from decimal import Decimal

from django.utils.translation import gettext as _, get_language

from projects.models import CoursePricePackage, Service
from projects.utils.pricing import (
    fetch_active_sale_discounts_by_service_id,
    package_payable_amount,
)
from projects.utils.queries import (
    _service_category_display_name,
    get_active_project_category_by_slug,
    price_package_display_name,
)


class CourseNotPayableError(Exception):
    """Course missing, inactive, or has no payable package."""


class PricePackageNotFoundError(Exception):
    """Package missing, inactive, or does not belong to the course."""


def course_has_payable_packages(course: Service) -> bool:
    return course.price_packages.filter(is_active=True, price__gt=0).exists()


def get_payable_course(slug: str) -> Service:
    course = get_active_project_category_by_slug(slug)
    if not course:
        raise CourseNotPayableError(_('Course not found or is not active.'))
    if not course_has_payable_packages(course):
        if course.price and course.price > 0:
            raise CourseNotPayableError(
                _('Payment packages are not configured for this course.')
            )
        raise CourseNotPayableError(_('Payment is not available for this course.'))
    return course


def get_payable_price_package(course: Service, package_id) -> CoursePricePackage:
    if not package_id:
        raise PricePackageNotFoundError(_('Please select a price package.'))
    try:
        package_id = int(package_id)
    except (TypeError, ValueError):
        raise PricePackageNotFoundError(_('Invalid price package.'))

    package = (
        CoursePricePackage.objects.filter(
            pk=package_id,
            course_id=course.pk,
            is_active=True,
        )
        .first()
    )
    if not package or not package.price or package.price <= 0:
        raise PricePackageNotFoundError(_('Selected price package is not available.'))
    return package


def course_display_name(course: Service, lang: str | None = None) -> str:
    lang = lang or (get_language() or 'az')[:2]
    return _service_category_display_name(course, lang)


def course_payment_description(
    course: Service,
    package: CoursePricePackage,
    lang: str | None = None,
) -> str:
    lang = lang or (get_language() or 'az')[:2]
    course_name = course_display_name(course, lang)
    package_name = price_package_display_name(package, lang)
    return f'Academor — {course_name} — {package_name}'[:255]


def package_amount(package: CoursePricePackage) -> Decimal:
    """Payable total for checkout — always uses a fresh sale discount lookup."""
    discounts_map = fetch_active_sale_discounts_by_service_id()
    return package_payable_amount(package, discounts_map=discounts_map)


def default_price_package_index(packages, preferred_package_id=None) -> int:
    """Index into serialized package list; restores session choice when possible."""
    if not packages:
        return 0
    if preferred_package_id is not None:
        try:
            pkg_id = int(preferred_package_id)
        except (TypeError, ValueError):
            return 0
        for index, pkg in enumerate(packages):
            candidate_id = pkg.get('id') if isinstance(pkg, dict) else getattr(pkg, 'pk', None)
            if candidate_id == pkg_id:
                return index
    return 0
