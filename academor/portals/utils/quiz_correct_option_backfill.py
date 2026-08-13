"""Backfill correct_option_index from legacy correct_answer text."""

from __future__ import annotations

from portals.models import ListeningQuestion, QuizQuestion
from portals.models.reading_models import (
    CHOICE_QUESTION_TYPES,
    ReadingQuestion,
    matching_option_index,
    resolve_reading_question_options,
)
from portals.utils.quiz_correct_option import sync_correct_option_fields


def backfill_quiz_question_mcq(question: QuizQuestion) -> bool:
    if question.question_type == QuizQuestion.QuestionType.SPR:
        return False
    options = [
        str(item).strip()
        for item in (question.answer_options or [])
        if str(item).strip()
    ]
    if len(options) < 2:
        return False

    resolved = sync_correct_option_fields(
        options,
        existing_index=question.correct_option_index,
        existing_answer=(question.correct_answer or '').strip(),
        match_answer=lambda opts, value: opts.index(value) if value in opts else None,
    )
    if resolved is None:
        return False

    idx, answer = resolved
    changed = (
        question.correct_option_index != idx
        or (question.correct_answer or '').strip() != answer
    )
    if changed:
        question.correct_option_index = idx
        question.correct_answer = answer
        question.save(update_fields=['correct_option_index', 'correct_answer'])
    return changed


def backfill_listening_question(question: ListeningQuestion) -> bool:
    options = question.variant_options
    if len(options) < 2:
        return False

    resolved = sync_correct_option_fields(
        options,
        existing_index=question.correct_option_index,
        existing_answer=(question.correct_answer or '').strip(),
        match_answer=lambda opts, value: opts.index(value) if value in opts else None,
    )
    if resolved is None:
        return False

    idx, answer = resolved
    changed = (
        question.correct_option_index != idx
        or (question.correct_answer or '').strip() != answer
    )
    if changed:
        question.correct_option_index = idx
        question.correct_answer = answer
        question.save(update_fields=['correct_option_index', 'correct_answer'])
    return changed


def backfill_reading_question(question: ReadingQuestion) -> bool:
    if question.question_type not in CHOICE_QUESTION_TYPES:
        return False

    options = resolve_reading_question_options(question)
    if len(options) < 2:
        return False

    resolved = sync_correct_option_fields(
        options,
        existing_index=question.correct_option_index,
        existing_answer=(question.correct_answer or '').strip(),
        match_answer=matching_option_index,
    )
    if resolved is None:
        return False

    idx, answer = resolved
    changed = (
        question.correct_option_index != idx
        or (question.correct_answer or '').strip() != answer
    )
    if changed:
        question.correct_option_index = idx
        question.correct_answer = answer
        question.save(update_fields=['correct_option_index', 'correct_answer'])
    return changed
