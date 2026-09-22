import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


_PHONE_ALLOWED_CHARS_RE = re.compile(r'^[\d\s\-\+\(\)]+$')
_PHONE_SEPARATORS_RE = re.compile(r'[\s\-\(\)]')
_PHONE_RULES = {
    'US': {'country_codes': ('1',), 'min_length': 10, 'max_length': 10},
    'CA': {'country_codes': ('1',), 'min_length': 10, 'max_length': 10},
    'UK': {'country_codes': ('44',), 'min_length': 10, 'max_length': 10},
    'AZ': {'country_codes': ('994',), 'min_length': 9, 'max_length': 9},
    'IN': {'country_codes': ('91',), 'min_length': 10, 'max_length': 10},
    'FR': {'country_codes': ('33',), 'min_length': 9, 'max_length': 9},
    'DE': {'country_codes': ('49',), 'min_length': 10, 'max_length': 11},
    'AU': {'country_codes': ('61',), 'min_length': 9, 'max_length': 9},
}


def validate_phone_number(value: str) -> bool:
    if not value:
        return False

    raw = value.strip()
    if not _PHONE_ALLOWED_CHARS_RE.fullmatch(raw):
        return False

    normalized = _PHONE_SEPARATORS_RE.sub('', raw)
    has_plus = normalized.startswith('+')
    if has_plus:
        normalized = normalized[1:]
    if not normalized.isdigit():
        return False

    for rule in _PHONE_RULES.values():
        for code in rule['country_codes']:
            if normalized.startswith(code):
                national = normalized[len(code):]
                candidates = [national]
                # Some users include a trunk prefix zero after country code
                # (e.g. +9940xxxxxxxxx). Accept by normalizing one leading 0.
                if national.startswith('0'):
                    candidates.append(national[1:])
                for candidate in candidates:
                    if rule['min_length'] <= len(candidate) <= rule['max_length']:
                        return True

    if not has_plus:
        digits_len = len(normalized)
        for rule in _PHONE_RULES.values():
            if rule['min_length'] <= digits_len <= rule['max_length']:
                return True

    return False


def phone_number_validator(value: str) -> None:
    if value and not validate_phone_number(value):
        raise ValidationError(_('Please enter a valid phone number.'))


# Operator prefix (without leading 0) → brand name
AZ_MOBILE_OPERATORS = {
    '10': 'Azercell',
    '50': 'Azercell',
    '51': 'Azercell',
    '55': 'Bakcell',
    '99': 'Bakcell',
    '70': 'Nar',
    '77': 'Nar',
    '60': 'Naxtel',
}

AZ_MOBILE_PREFIXES_WITH_ZERO = {
    f'0{prefix}' for prefix in AZ_MOBILE_OPERATORS
}

_AZ_MOBILE_INVALID = {
    'valid': False,
    'normalized': None,
    'operator': None,
    'error': 'Invalid Azerbaijan mobile phone number',
}


def validate_az_mobile_phone(phone: str) -> dict:
    """
    Validate an Azerbaijan mobile number and return a structured result.

    normalized is always +994XXXXXXXXX (9 national digits) when valid.
    """
    if not phone or not str(phone).strip():
        return dict(_AZ_MOBILE_INVALID)

    raw = str(phone).strip()
    if not _PHONE_ALLOWED_CHARS_RE.fullmatch(raw):
        return dict(_AZ_MOBILE_INVALID)

    digits = _PHONE_SEPARATORS_RE.sub('', raw)
    if digits.startswith('+'):
        digits = digits[1:]
    if not digits.isdigit():
        return dict(_AZ_MOBILE_INVALID)

    if digits.startswith('00994'):
        digits = digits[5:]
    elif digits.startswith('994'):
        digits = digits[3:]

    if digits.startswith('0'):
        if len(digits) != 10:
            return dict(_AZ_MOBILE_INVALID)
        op_code = digits[:3]
        if op_code not in AZ_MOBILE_PREFIXES_WITH_ZERO:
            return dict(_AZ_MOBILE_INVALID)
        national = digits[1:]
    else:
        if len(digits) != 9:
            return dict(_AZ_MOBILE_INVALID)
        op_code = digits[:2]
        if op_code not in AZ_MOBILE_OPERATORS:
            return dict(_AZ_MOBILE_INVALID)
        national = digits

    operator = AZ_MOBILE_OPERATORS[national[:2]]
    return {
        'valid': True,
        'normalized': f'+994{national}',
        'operator': operator,
        'error': None,
    }


def normalize_az_phone(phone: str):
    """
    Azərbaycan mobil nömrəsini 9 rəqəmli formata salır: 501234567
    """
    result = validate_az_mobile_phone(phone)
    if not result['valid']:
        return None
    return result['normalized'][4:]