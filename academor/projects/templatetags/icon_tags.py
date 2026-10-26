"""Bootstrap Icons for icon names that are stored as Font Awesome classes.

Public pages ship only Bootstrap Icons. Some icon names still come from the
database or Python as Font Awesome classes (service ``card_icon`` choices,
``AboutWhyItem.icon``, price-package tab icons), and the portal keeps using
them as-is. ``{{ value|bi_icon }}`` maps such a value to Bootstrap Icons
classes at render time, so stored data and the portal stay untouched.
"""
from django import template

register = template.Library()

# Font Awesome 5 name (without "fa-") -> Bootstrap Icons 1.11 name (without "bi-")
FA_TO_BI = {
    # service category card icons (projects/service_category_icons.py)
    'book-open': 'book',
    'language': 'translate',
    'comments': 'chat-dots',
    'microphone-alt': 'mic',
    'headphones': 'headphones',
    'pen': 'pencil',
    'certificate': 'patch-check',
    'file-alt': 'file-text',
    'chart-line': 'graph-up-arrow',
    'calculator': 'calculator',
    'graduation-cap': 'mortarboard',
    'university': 'bank',
    'user-graduate': 'person-badge',
    'pencil-alt': 'pencil',
    'globe-americas': 'globe-americas',
    'plane-departure': 'airplane',
    'laptop': 'laptop',
    'users': 'people',
    'user': 'person',
    'briefcase': 'briefcase',
    'child': 'emoji-smile',
    'chalkboard-teacher': 'easel',
    'star': 'star',
    # price-package tab icons (projects/utils/price_package_tabs.py)
    'th-large': 'grid',
    'bolt': 'lightning-charge',
    'user-plus': 'person-plus',
    'object-group': 'collection',
    'user-check': 'person-check',
    'credit-card': 'credit-card',
    'clipboard-list': 'clipboard-check',
    'tag': 'tag',
    # common free-text choices for AboutWhyItem / advantages
    'check': 'check-lg',
    'check-circle': 'check-circle',
    'award': 'award',
    'trophy': 'trophy',
    'medal': 'award',
    'book': 'book',
    'globe': 'globe',
    'heart': 'heart',
    'lightbulb': 'lightbulb',
    'clock': 'clock',
    'calendar-alt': 'calendar3',
    'calendar': 'calendar3',
    'chart-bar': 'bar-chart',
    'handshake': 'people',
    'smile': 'emoji-smile',
    'thumbs-up': 'hand-thumbs-up',
    'shield-alt': 'shield-check',
    'rocket': 'rocket-takeoff',
    'map-marker-alt': 'geo-alt',
    'phone-alt': 'telephone',
    'envelope': 'envelope',
    'video': 'camera-video',
    'comment': 'chat',
    'comment-dots': 'chat-dots',
    'user-tie': 'person-badge',
    'id-card': 'person-vcard',
    'passport': 'passport',
    'plane': 'airplane',
    'school': 'building',
    'building': 'building',
    'home': 'house',
    'info-circle': 'info-circle',
    'question-circle': 'question-circle',
}

FA_PREFIXES = {'fa', 'fas', 'far', 'fab', 'fal', 'fad'}
FALLBACK = 'star'


@register.filter
def bi_icon(value):
    """'fa fa-users' / 'fas fa-users' / 'fa-users' / 'bi-people' -> 'bi bi-people'."""
    tokens = str(value or '').split()
    for token in tokens:
        if token.startswith('bi-'):
            return f'bi {token}'
    for token in tokens:
        if token in FA_PREFIXES or not token.startswith('fa-'):
            continue
        return f'bi bi-{FA_TO_BI.get(token[3:], FALLBACK)}'
    return f'bi bi-{FALLBACK}'
