"""Auto-scoring for listening quiz attempts."""

from __future__ import annotations

import re

from portals.models import Quiz, ListeningQuestion
from portals.utils.quiz_listening import (
    get_listening_questions_for_quiz,
    listening_correct_option_index,
)
from portals.utils.quiz_submit import _looks_like_variant_index


def _normalize_text_answer(value: str, *, case_insensitive: bool) -> str:
    text = re.sub(r'\s+', ' ', (value or '').strip())
    if case_insensitive:
        return text.casefold()
    return text


def _word_count(value: str) -> int:
    return len([part for part in re.split(r'\s+', (value or '').strip()) if part])


def _text_answer_matches(question: ListeningQuestion, raw_value) -> bool:
    config = question.question_config or {}
    submitted = _normalize_text_answer(
        '' if raw_value is None else str(raw_value),
        case_insensitive=bool(config.get('case_insensitive', True)),
    )
    if not submitted:
        return False

    word_limit = config.get('word_limit')
    if word_limit is not None:
        try:
            limit = int(word_limit)
        except (TypeError, ValueError):
            limit = None
        if limit is not None and _word_count(str(raw_value or '').strip()) > limit:
            return False

    spr_max = question.spr_max_length
    if spr_max is not None:
        try:
            max_len = int(spr_max)
        except (TypeError, ValueError):
            max_len = None
        if max_len is not None and len(str(raw_value or '').strip()) > max_len:
            return False

    # Prefer SPR multi-answer list (SAT-style). Fall back to legacy correct_answer + alternatives.
    candidates = list(question.spr_accepted_answers)
    if not candidates:
        candidates = [question.correct_answer]
        candidates.extend(config.get('accept_alternatives') or [])

    # Numeric / equation-friendly match when SPR answers are set (same rules as SAT Math).
    if question.spr_correct_answers:
        from portals.utils.sat_spr_validation import validate_spr_answer

        if validate_spr_answer(str(raw_value or ''), candidates).get('is_correct'):
            return True

    normalized_candidates = [
        _normalize_text_answer(str(item), case_insensitive=bool(config.get('case_insensitive', True)))
        for item in candidates
        if str(item).strip()
    ]
    return submitted in normalized_candidates


def _choice_answer_matches(question: ListeningQuestion, raw_value) -> bool:
    correct_index = listening_correct_option_index(question)
    if correct_index is None:
        return False
    if _looks_like_variant_index(raw_value, question):
        return int(str(raw_value).strip()) == correct_index
    options = question.variant_options
    submitted = str(raw_value or '').strip()
    if submitted and submitted in options:
        return options.index(submitted) == correct_index
    return False


def score_listening_question(question: ListeningQuestion, raw_value) -> bool:
    if question.is_variant:
        return _choice_answer_matches(question, raw_value)
    return _text_answer_matches(question, raw_value)


def score_listening_quiz(
    quiz: Quiz,
    given_answers: dict,
    *,
    questions: list[ListeningQuestion] | None = None,
) -> tuple[float, int, list[dict]]:
    questions = (
        list(questions)
        if questions is not None
        else get_listening_questions_for_quiz(quiz)
    )
    max_score = len(questions)
    score = 0.0
    breakdown = []

    for question in questions:
        raw = given_answers.get(str(question.pk), given_answers.get(question.pk, ''))
        is_correct = score_listening_question(question, raw)
        if is_correct:
            score += 1.0
        breakdown.append({
            'id': question.pk,
            'question_type': 'variant' if question.is_variant else 'spr',
            'student_answer': raw,
            'is_correct': is_correct,
            'correct_answer': question.correct_answer,
            'spr_correct_answers': (
                None if question.is_variant else list(question.spr_accepted_answers)
            ),
        })

    return score, max_score, breakdown
