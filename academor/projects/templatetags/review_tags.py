from django import template

register = template.Library()


def _sanitize_rating(raw):
    if raw is None:
        return 5
    try:
        value = int(raw)
    except (TypeError, ValueError):
        return 5
    return max(1, min(5, value))


@register.inclusion_tag('includes/review_stars.html')
def render_review_stars(rating):
    """Render filled / empty stars from Review.rating (integer 1–5)."""
    r = _sanitize_rating(rating)
    stars = [{'filled': i < r} for i in range(5)]
    return {'stars': stars, 'rating': r}
