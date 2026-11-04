from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()


@register.filter
def azn(value, decimals=None):
    """1250 -> '1 250 AZN', 41.86 -> '41.86 AZN' (qəpik only when there are any); decimals=2 forces them."""
    try:
        amount = Decimal(value or 0)
    except (InvalidOperation, TypeError, ValueError):
        return value
    if decimals in (None, ''):
        places = 0 if amount == amount.to_integral_value() else 2
    else:
        places = int(decimals)
    text = f'{amount:,.{places}f}'.replace(',', ' ')
    return f'{text} AZN'


def _dec(v):
    try:
        return Decimal(v or 0)
    except (InvalidOperation, TypeError, ValueError):
        return Decimal('0')


@register.filter
def sub(a, b):
    return _dec(a) - _dec(b)


@register.filter
def add_money(a, b):
    return _dec(a) + _dec(b)


@register.filter
def initials(value):
    parts = [p for p in str(value or '').replace('_', ' ').split() if p]
    if not parts:
        return '?'
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[1][0]).upper()


@register.filter
def tone(rate):
    """Attendance / collection rate → good | warn | bad | none."""
    if rate is None or rate == '':
        return 'none'
    rate = float(rate)
    if rate >= 85:
        return 'good'
    if rate >= 70:
        return 'warn'
    return 'bad'


@register.filter
def get_item(mapping, key):
    try:
        return mapping.get(key)
    except AttributeError:
        return None
