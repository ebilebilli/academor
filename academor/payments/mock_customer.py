"""Resolve or create portal customer profiles for public mock purchases."""

from __future__ import annotations

import re
import secrets

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.translation import gettext as _

from portals.forms import PORTAL_ROLE_CUSTOMER, create_portal_profile
from portals.models import CustomerProfile, ParentProfile, StudentProfile, TeacherProfile
from portals.utils.normalize_phone_number import normalize_az_phone

from portals.utils.portal_session import is_portal_authenticated
from portals.utils.queries import get_customer_profile, get_portal_role

User = get_user_model()


def portal_customer_checkout(request) -> bool:
    if not is_portal_authenticated(request):
        return False
    return get_portal_role(request.portal_user) == 'customer'


def portal_customer_profile(request):
    if not portal_customer_checkout(request):
        return None
    return get_customer_profile(request.portal_user)


def format_phone_storage(phone: str) -> str:
    az_digits = normalize_az_phone(phone)
    if az_digits:
        return f'+994{az_digits}'
    return re.sub(r'\s+', '', (phone or '').strip())


def phone_lookup_candidates(phone: str) -> list[str]:
    candidates: list[str] = []
    stored = format_phone_storage(phone)
    if stored:
        candidates.append(stored)
    az_digits = normalize_az_phone(phone)
    if az_digits:
        candidates.extend(
            [
                f'+994{az_digits}',
                az_digits,
                f'994{az_digits}',
                f'0{az_digits}',
            ]
        )
    raw = re.sub(r'\s+', '', (phone or '').strip())
    if raw and raw not in candidates:
        candidates.append(raw)
    return list(dict.fromkeys(candidates))


def find_customer_profile_by_phone(phone: str) -> CustomerProfile | None:
    candidates = phone_lookup_candidates(phone)
    if not candidates:
        return None
    return CustomerProfile.objects.filter(phone__in=candidates).first()


def _generate_username(phone: str) -> str:
    az_digits = normalize_az_phone(phone)
    digits = az_digits or re.sub(r'\D', '', phone or '')[-12:]
    base = f'mock{digits}' if digits else f'mock{secrets.token_hex(4)}'
    base = base[:140]
    username = base
    suffix = 1
    while User.objects.filter(username=username).exists():
        tail = f'_{suffix}'
        username = f'{base[:150 - len(tail)]}{tail}'
        suffix += 1
    return username


def _phone_used_by_other_portal_role(phone: str) -> bool:
    candidates = phone_lookup_candidates(phone)
    if not candidates:
        return False
    if StudentProfile.objects.filter(phone__in=candidates).exists():
        return True
    if TeacherProfile.objects.filter(phone__in=candidates).exists():
        return True
    if ParentProfile.objects.filter(phone__in=candidates).exists():
        return True
    return False


@transaction.atomic
def resolve_or_create_customer_for_mock_purchase(
    *,
    buyer_name: str,
    buyer_phone: str,
    buyer_email: str | None = None,
) -> CustomerProfile:
    existing = find_customer_profile_by_phone(buyer_phone)
    if existing:
        return existing

    if _phone_used_by_other_portal_role(buyer_phone):
        raise ValidationError(
            _(
                'This phone number is already linked to another Academor account. '
                'Please contact us to complete your purchase.'
            )
        )

    stored_phone = format_phone_storage(buyer_phone)
    username = _generate_username(buyer_phone)
    user = User.objects.create_user(
        username=username,
        password=secrets.token_urlsafe(16),
        email=buyer_email or '',
        first_name=(buyer_name or '')[:150],
    )
    create_portal_profile(
        user,
        PORTAL_ROLE_CUSTOMER,
        phone=stored_phone,
        mock_credits=0,
    )
    return CustomerProfile.objects.select_related('user').get(user_id=user.pk)
