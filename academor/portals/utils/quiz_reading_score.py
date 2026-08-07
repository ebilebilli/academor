"""Auto-scoring for IELTS reading quiz attempts."""

from __future__ import annotations

import re

from portals.models import Quiz, ReadingQuestion
from portals.models.reading_models import CHOICE_QUESTION_TYPES, TEXT_QUESTION_TYPES, matching_option_index
from portals.utils.quiz_reading import (
    get_reading_questions_for_quiz,
    reading_correct_option_index,
    resolve_question_options,
)
from portals.utils.quiz_submit import _looks_like_variant_index


def _normalize_text_answer(value: str, *, case_insensitive: bool) -> str:
    text = re.sub(r'\s+', ' ', (value or '').strip())
    if case_insensitive:
        return text.casefold()
    return text


def _word_count(value: str) -> int:
    return len([part for part in re.split(r'\s+', (value or '').strip()) if part])


def _text_answer_matches(question: ReadingQuestion, raw_value) -> bool:
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

    candidates = [question.correct_answer]
    candidates.extend(config.get('accept_alternatives') or [])
    normalized_candidates = [
        _normalize_text_answer(str(item), case_insensitive=bool(config.get('case_insensitive', True)))
        for item in candidates
        if str(item).strip()
    ]
    return submitted in normalized_candidates


def _choice_answer_matches(question: ReadingQuestion, raw_value) -> bool:
    correct_index = reading_correct_option_index(question)
    if correct_index is None:
        return False
    if _looks_like_variant_index(raw_value, question):
        return int(str(raw_value).strip()) == correct_index
    options = resolve_question_options(question)
    submitted = str(raw_value or '').strip()
    if submitted:
        submitted_index = matching_option_index(options, submitted)
        if submitted_index is not None:
            return submitted_index == correct_index
    return False


def score_reading_question(question: ReadingQuestion, raw_value) -> bool:
    if question.question_type in CHOICE_QUESTION_TYPES:
        return _choice_answer_matches(question, raw_value)
    if question.question_type in TEXT_QUESTION_TYPES:
        return _text_answer_matches(question, raw_value)
    return False


def score_reading_quiz(
    quiz: Quiz,
    given_answers: dict,
    *,
    questions: list[ReadingQuestion] | None = None,
) -> tuple[float, int, list[dict]]:
    questions = (
        list(questions)
        if questions is not None
        else get_reading_questions_for_quiz(quiz)
    )
    max_score = len(questions)
    score = 0.0
    breakdown = []

    for question in questions:
        raw = given_answers.get(str(question.pk), given_answers.get(question.pk, ''))
        is_correct = score_reading_question(question, raw)
        if is_correct:
            score += 1.0
        breakdown.append({
            'id': question.pk,
            'question_type': question.question_type,
            'student_answer': raw,
            'is_correct': is_correct,
            'correct_answer': question.correct_answer,
        })

    return score, max_score, breakdown


def normalize_reading_answers(
    quiz: Quiz,
    raw: dict | None,
    *,
    ordered_answers: list | None = None,
    questions: list[ReadingQuestion] | None = None,
) -> dict[str, str]:
    questions = (
        list(questions)
        if questions is not None
        else get_reading_questions_for_quiz(quiz)
    )
    normalized: dict[str, str] = {}
    if not isinstance(raw, dict):
        raw = {}

    for question in questions:
        key = str(question.pk)
        value = raw.get(key, raw.get(question.pk, ''))
        if question.question_type in CHOICE_QUESTION_TYPES:
            if _looks_like_variant_index(value, question):
                normalized[key] = str(int(str(value).strip()))
            elif str(value or '').strip():
                normalized[key] = str(value).strip()
        elif str(value or '').strip():
            normalized[key] = str(value).strip()

    if ordered_answers:
        values = list(ordered_answers)
        if len(values) == len(questions):
            for question, value in zip(questions, values):
                key = str(question.pk)
                if key in normalized:
                    continue
                if question.question_type in CHOICE_QUESTION_TYPES:
                    if _looks_like_variant_index(value, question):
                        normalized[key] = str(int(value))
                elif str(value or '').strip():
                    normalized[key] = str(value).strip()

    return normalized


def validate_reading_answers(
    quiz: Quiz,
    answers: dict[str, str],
    *,
    questions: list[ReadingQuestion] | None = None,
) -> str | None:
    from django.utils.translation import gettext as _

    questions = (
        list(questions)
        if questions is not None
        else get_reading_questions_for_quiz(quiz)
    )
    if not questions:
        return str(_('No reading questions found for this quiz.'))

    missing = []
    for question in questions:
        raw = answers.get(str(question.pk), '')
        if question.question_type in CHOICE_QUESTION_TYPES:
            if not _looks_like_variant_index(raw, question) and not str(raw).strip():
                missing.append(question.pk)
        elif not str(raw).strip():
            missing.append(question.pk)

    if missing:
        return str(_('Answer every task before submitting.'))
    return None
