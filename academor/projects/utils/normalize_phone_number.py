import re


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


def normalize_az_phone(phone: str) -> str:
    """
    Azərbaycan mobil nömrəsini 9 rəqəmli formata salır: 501234567
    """
    if not phone:
        return None
    digits = re.sub(r'\D', '', phone.strip())
    if digits.startswith('994'):
        digits = digits[3:]
        
    if digits.startswith('0'):
        digits = digits[1:]

    if len(digits) > 9:
        digits = digits[-9:]

    if len(digits) != 9:
        return None

    prefix = digits[:2]
    if prefix in {'50', '51', '55', '70', '77', '99'}:
        return digits

    return None