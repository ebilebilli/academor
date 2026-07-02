import re


def _digits(value):
    if not value:
        return None
    digits = re.sub(r'\D', '', str(value))
    return digits if len(digits) >= 9 else None


def resolve_whatsapp_url(contact_data):
    """Best WhatsApp chat URL from serialized contact data (admin Contact model)."""
    if not contact_data:
        return None
    for key in ('whatsapp_number_me', 'whatsapp_number_2_me'):
        digits = _digits(contact_data.get(key))
        if digits:
            return f'https://wa.me/{digits}'
    for key in ('phone_href', 'phone', 'phone_three', 'phone_three_href'):
        digits = _digits(contact_data.get(key))
        if digits:
            return f'https://wa.me/{digits}'
    return None
