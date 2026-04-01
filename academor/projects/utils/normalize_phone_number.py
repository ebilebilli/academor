import re

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