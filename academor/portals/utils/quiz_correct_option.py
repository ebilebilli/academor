"""Resolve MCQ correct answers by 1-based option number (admin) or stored index."""


def initial_option_number_from_index(index) -> int | None:
    if index is None:
        return None
    try:
        return int(index) + 1
    except (TypeError, ValueError):
        return None


def option_index_from_number(
    option_number,
    option_count: int,
    *,
    existing_index=None,
) -> int | None:
    """Convert admin 1-based option number to a 0-based index."""
    if option_number not in (None, ''):
        try:
            idx = int(option_number) - 1
        except (TypeError, ValueError):
            idx = -1
        if 0 <= idx < option_count:
            return idx

    if existing_index is not None:
        try:
            idx = int(existing_index)
        except (TypeError, ValueError):
            idx = -1
        if 0 <= idx < option_count:
            return idx

    return None


def sync_correct_option_fields(
    options: list[str],
    *,
    option_number=None,
    existing_index=None,
    existing_answer: str = '',
    match_answer=None,
) -> tuple[int, str] | None:
    """Return (correct_option_index, correct_answer) or None if unresolved."""
    if len(options) < 2:
        return None

    idx = option_index_from_number(
        option_number,
        len(options),
        existing_index=existing_index,
    )
    if idx is None and match_answer is not None and existing_answer:
        idx = match_answer(options, existing_answer)

    if idx is None:
        return None

    answer = str(options[idx]).strip()
    if not answer:
        return None
    return idx, answer[:500]
