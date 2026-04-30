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
    loading='lazy',
    fetchpriority='auto',
):
    """
    Wrap an image with a site-branded placeholder until load (same asset as header logo).

    layout:
      ''        — block, full width of parent
      'cover'   — fill absolute hero / carousel / ratio box (object-fit cover on img)
      'circle'  — fill circular frame (abroad cards, university flags)
    """
    allowed = ('', 'cover', 'circle')
    if layout not in allowed:
        layout = ''
    return {
        'src': src,
        'alt': alt or '',
        'img_class': img_class,
        'layout': layout,
        'width': width,
        'height': height,
        'loading': loading,
        'fetchpriority': fetchpriority,
    }
