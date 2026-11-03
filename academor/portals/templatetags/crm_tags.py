from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()


@register.filter
def azn(value, decimals=0):
    """1250.5 → '1 251 AZN' (thin-space thousands); decimals=2 keeps qəpik."""
    try:
        amount = Decimal(value or 0)
    except (InvalidOperation, TypeError, ValueError):
        return value
    places = int(decimals or 0)
    text = f'{amount:,.{places}f}'.replace(',', ' ')
    return f'{text} AZN'


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
