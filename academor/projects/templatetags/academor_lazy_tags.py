"""
Branded lazy-image helpers (navbar logo as lightweight placeholder).
"""
from django import template

register = template.Library()


@register.inclusion_tag('includes/academor_branded_lazy_img.html')
def academor_branded_lazy_img(
    src,
    alt='',
    img_class='',
    layout='',
    width=None,
    height=None,
    sizes=None,
    srcset=None,
    loading='lazy',
    fetchpriority='auto',
    reveal='fade',
    decoding='async',
):
    """
    Wrap an image with a site-branded placeholder until load (same asset as header logo).

    layout:
      ''        — block, full width of parent
      'cover'   — fill absolute hero / carousel / ratio box (object-fit cover on img)
      'circle'  — fill circular frame (abroad cards, university flags)

    reveal:
      'fade'      — hide img until loaded (default)
      'immediate' — show img while loading (marquee logos; avoids stuck invisible frames)
    """
    allowed = ('', 'cover', 'circle')
    if layout not in allowed:
        layout = ''
    reveal = (reveal or 'fade').lower()
    if reveal not in ('fade', 'immediate'):
        reveal = 'fade'
    decoding = decoding or 'async'
    if decoding not in ('async', 'auto', 'sync'):
        decoding = 'async'
    return {
        'src': src,
        'alt': alt or '',
        'img_class': img_class,
        'layout': layout,
        'width': width,
        'height': height,
        'sizes': sizes,
        'srcset': srcset,
        'loading': loading,
        'fetchpriority': fetchpriority,
        'reveal': reveal,
        'decoding': decoding,
    }
