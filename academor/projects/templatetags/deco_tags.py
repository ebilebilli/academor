from django import template
from django.templatetags.static import static
from django.utils.html import format_html, format_html_join

from projects.page_shapes import shapes_for

register = template.Library()


def _placements(context):
    request = context.get('request')
    match = getattr(request, 'resolver_match', None)
    return shapes_for(getattr(match, 'url_name', None))


def _svg(classes, style, motion, shape):
    return (
        ' '.join(classes),
        style,
        format_html(' data-motion="{}"', motion) if motion else '',
        static('assets/img/shapes/shapes.svg'),
        shape,
    )


_SVG = '<svg class="{}" focusable="false" style="{}"{}><use href="{}#{}"></use></svg>'


@register.simple_tag(takes_context=True)
def page_shapes(context):
    """Background (behind content) and edge (in front, gutter only) shapes for this page."""
    sets = _placements(context)
    back = format_html_join('', _SVG, (
        _svg(['page-shape', 'page-shape--back', f'page-shape--{colour}'],
             f'--s:{size}px;--x:{x}%;--top:{top}%;--rot:{rot}deg', motion, shape)
        for shape, colour, size, x, top, rot, motion in sets.get('back', ())
    ))
    edge = format_html_join('', _SVG, (
        _svg(['page-shape', 'page-shape--edge', f'page-shape--{side}', f'page-shape--{colour}'],
             f'--s:{size}px;--top:{top}%;--rot:{rot}deg', motion, shape)
        for shape, colour, size, side, top, rot, motion in sets.get('edge', ())
    ))
    return format_html(
        '<div class="page-shapes page-shapes--back" aria-hidden="true">{}</div>'
        '<div class="page-shapes page-shapes--edge" aria-hidden="true">{}</div>',
        back, edge,
    )


@register.simple_tag(takes_context=True)
def banner_shapes(context):
    """Bold shapes in the corners of the page-header band."""
    items = format_html_join('', _SVG, (
        _svg(['banner-shape', f'banner-shape--{corner}', f'page-shape--{colour}'],
             f'--s:{size}px;--rot:{rot}deg', motion, shape)
        for shape, colour, size, corner, rot, motion in _placements(context).get('banner', ())
    ))
    return format_html('<div class="banner-shapes" aria-hidden="true">{}</div>', items) if items else ''
