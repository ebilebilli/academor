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


def compute_mock_average_stats(mock_attempts, *, band_max=9.0, sat_total_max=1600):
    """Average mock results across fully graded attempts (IELTS band and/or SAT total)."""
    rows = list(mock_attempts or [])
    ielts_bands = []
    sat_totals = []
    for row in rows:
        if not row.get('is_fully_graded'):
            continue
        if row.get('scoring_mode') == 'sat_scaled' and row.get('overall_score') is not None:
            sat_totals.append(float(row['overall_score']))
        elif row.get('overall_band') is not None:
            ielts_bands.append(float(row['overall_band']))

    pending_count = sum(1 for row in rows if not row.get('is_fully_graded'))
    graded_count = len(ielts_bands) + len(sat_totals)
    avg_band = round(sum(ielts_bands) / len(ielts_bands), 1) if ielts_bands else None
    avg_total_score = round(sum(sat_totals) / len(sat_totals)) if sat_totals else None

    if ielts_bands and not sat_totals:
        avg_score_pct = (
            round(100 * avg_band / band_max, 1)
            if avg_band is not None and band_max
            else None
        )
    elif sat_totals and not ielts_bands:
        avg_score_pct = (
            round(100 * avg_total_score / sat_total_max, 1)
            if avg_total_score is not None and sat_total_max
            else None
        )
    else:
        pct_values = []
        if avg_band is not None and band_max:
            pct_values.append(100 * avg_band / band_max)
        if avg_total_score is not None and sat_total_max:
            pct_values.append(100 * avg_total_score / sat_total_max)
        avg_score_pct = round(sum(pct_values) / len(pct_values), 1) if pct_values else None

    return {
        'avg_band': avg_band,
        'avg_total_score': avg_total_score,
        'avg_score_pct': avg_score_pct,
        'band_max': band_max,
        'sat_total_max': sat_total_max,
        'graded_count': graded_count,
        'pending_count': pending_count,
        'total_count': len(rows),
        'tier': quiz_average_score_tier(avg_score_pct),
    }


def build_mock_stats_list(mock_attempts):
    """Build one dashboard mock card payload per exam program (IELTS, SAT, …)."""
    from portals.utils.mock_programs import MOCK_EXAM_PROGRAMS, PROGRAM_LABELS

    rows = list(mock_attempts or [])
    if not rows:
        return []

    by_program: dict[str, list] = {}
    for row in rows:
        program = (row.get('exam_program') or '').strip()
        if not program:
            continue
        by_program.setdefault(program, []).append(row)

    ordered_programs = [code for code in MOCK_EXAM_PROGRAMS if code in by_program]
    ordered_programs.extend(
        program for program in sorted(by_program)
        if program not in MOCK_EXAM_PROGRAMS
    )

    cards = []
    for program in ordered_programs:
        program_rows = by_program.get(program) or []
        stats = compute_mock_average_stats(program_rows)
        if not stats['total_count']:
            continue
        scoring_mode = next(
            (row.get('scoring_mode') for row in program_rows if row.get('scoring_mode')),
            None,
        )
        cards.append({
            'exam_program': program,
            'exam_program_label': str(PROGRAM_LABELS.get(program, program)),
            'scoring_mode': scoring_mode,
            **stats,
        })
    return cards
