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
    """Return (correct_option_index, correct_answer) or None if unresolved.

    Priority: the admin's option number, then the stored answer text, then the stored index.
    The index column defaults to 0, so rows created in code (resource loaders, scripts) carry
    index 0 next to the real answer text; trusting the index there would silently turn the
    first option into the correct one.
    """
    if len(options) < 2:
        return None

    idx = option_index_from_number(option_number, len(options))
    if idx is None:
        stored_idx = option_index_from_number(None, len(options), existing_index=existing_index)
        text_idx = (
            match_answer(options, existing_answer)
            if match_answer is not None and existing_answer
            else None
        )
        if stored_idx is not None and (
            text_idx is None
            # duplicate option texts: keep the stored index when it points at the same text
            or match_answer([options[stored_idx]], existing_answer) == 0
        ):
            idx = stored_idx
        else:
            idx = text_idx

    if idx is None:
        return None

    answer = str(options[idx]).strip()
    if not answer:
        return None
    return idx, answer[:500]
