"""Quiz result aggregates for profile and dashboard views."""


def quiz_score_percent(total_score, max_value):
    if total_score is None or not max_value:
        return None
    try:
        total = float(total_score)
        maximum = float(max_value)
    except (TypeError, ValueError):
        return None
    if maximum <= 0:
        return None
    return max(0.0, min(100.0, 100 * total / maximum))


def quiz_average_score_tier(avg_score_pct):
    if avg_score_pct is None:
        return 'empty'
    if avg_score_pct >= 85:
        return 'excellent'
    if avg_score_pct >= 70:
        return 'good'
    if avg_score_pct >= 50:
        return 'fair'
    return 'low'


def compute_quiz_average_stats(quiz_results):
    """
    Normalized quiz average for mixed scales (e.g. /10 manual review, /N variant).

    Each graded attempt contributes score / max * 100. Pending review and
    unscored attempts are excluded from the average.
    """
    rows = list(quiz_results or [])
    pending_count = sum(1 for row in rows if row.get('is_pending_review'))
    percentages = []
    for row in rows:
        if row.get('is_pending_review'):
            continue
        pct = quiz_score_percent(row.get('total_score'), row.get('max_value'))
        if pct is not None:
            percentages.append(pct)

    graded_count = len(percentages)
    avg_score_pct = round(sum(percentages) / graded_count, 1) if graded_count else None
    return {
        'avg_score_pct': avg_score_pct,
        'graded_count': graded_count,
        'pending_count': pending_count,
        'total_count': len(rows),
        'tier': quiz_average_score_tier(avg_score_pct),
    }


def compute_lesson_average_stats(scores):
    """Normalized average for admin lesson score rows (value / max_value)."""
    rows = list(scores or [])
    percentages = []
    for row in rows:
        pct = quiz_score_percent(row.get('value'), row.get('max_value'))
        if pct is not None:
            percentages.append(pct)

    graded_count = len(percentages)
    avg_score_pct = round(sum(percentages) / graded_count, 1) if graded_count else None
    return {
        'avg_score_pct': avg_score_pct,
        'graded_count': graded_count,
        'pending_count': 0,
        'total_count': len(rows),
        'tier': quiz_average_score_tier(avg_score_pct),
    }
