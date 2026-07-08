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


def compute_weekly_average_stats(weekly_scores):
    """Normalized average for weekly score rows (score / max_score, default 10)."""
    rows = list(weekly_scores or [])
    percentages = []
    for row in rows:
        pct = quiz_score_percent(row.get('score'), row.get('max_score') or 10)
        if pct is not None:
            percentages.append(pct)

    graded_count = len(percentages)
    avg_score_pct = round(sum(percentages) / graded_count, 1) if graded_count else None
    avg_score_ten = round(avg_score_pct / 10, 1) if avg_score_pct is not None else None
    return {
        'avg_score_pct': avg_score_pct,
        'avg_score_ten': avg_score_ten,
        'graded_count': graded_count,
        'pending_count': 0,
        'total_count': len(rows),
        'tier': quiz_average_score_tier(avg_score_pct),
    }


def compute_mock_average_stats(mock_attempts, *, band_max=9.0):
    """Average IELTS mock band across fully graded attempts."""
    rows = list(mock_attempts or [])
    bands = [
        float(row['overall_band'])
        for row in rows
        if row.get('overall_band') is not None
    ]
    pending_count = sum(1 for row in rows if not row.get('is_fully_graded'))
    graded_count = len(bands)
    avg_band = round(sum(bands) / graded_count, 1) if graded_count else None
    avg_score_pct = (
        round(100 * avg_band / band_max, 1)
        if avg_band is not None and band_max
        else None
    )
    return {
        'avg_band': avg_band,
        'avg_score_pct': avg_score_pct,
        'band_max': band_max,
        'graded_count': graded_count,
        'pending_count': pending_count,
        'total_count': len(rows),
        'tier': quiz_average_score_tier(avg_score_pct),
    }
