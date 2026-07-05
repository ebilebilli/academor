"""Reading passage admin — dynamic field visibility by question type."""

from __future__ import annotations

from django.utils.translation import gettext_lazy as _

from portals.models.reading_models import (
    MATCHING_QUESTION_TYPES,
    TEXT_QUESTION_TYPES,
    ReadingQuestionType,
)

READING_QUESTION_TOGGLE_FIELDS = (
    'group_ref',
    'answer_options',
    'question_config',
    'word_limit',
    'case_insensitive',
    'accept_alternatives_text',
)


def reading_question_admin_field_config(question_type: str | None) -> dict:
    """Return show/hide/clear rules for a reading question inline row."""
    normalized = (question_type or ReadingQuestionType.MCQ).strip()
    if normalized not in ReadingQuestionType.values:
        normalized = ReadingQuestionType.MCQ

    is_matching = normalized in MATCHING_QUESTION_TYPES
    is_mcq = normalized == ReadingQuestionType.MCQ
    is_tfng = normalized == ReadingQuestionType.TFNG
    is_ynng = normalized == ReadingQuestionType.YNNG
    is_text = normalized in TEXT_QUESTION_TYPES

    show_fields = ['question', 'correct_answer']
    hide_fields: list[str] = []
    clear_fields: list[str] = []

    if is_matching:
        show_fields.append('group_ref')
    else:
        hide_fields.append('group_ref')
        clear_fields.append('group_ref')

    if is_mcq:
        show_fields.append('answer_options')
    else:
        hide_fields.append('answer_options')
        clear_fields.append('answer_options')

    if is_text:
        show_fields.extend([
            'word_limit',
            'case_insensitive',
            'accept_alternatives_text',
        ])
    else:
        hide_fields.extend([
            'word_limit',
            'case_insensitive',
            'accept_alternatives_text',
        ])
        clear_fields.extend([
            'word_limit',
            'case_insensitive',
            'accept_alternatives_text',
        ])

    if is_text:
        show_fields.append('question_config')
    else:
        hide_fields.append('question_config')
        clear_fields.append('question_config')

    field_help: dict[str, str] = {
        'question': str(_(
            'Prompt, table, flow-chart, or diagram context. '
            'Leave blank for a numbered answer line only when appropriate.',
        )),
        'correct_answer': str(_('Exact text for gap-fill tasks or the matching option label.')),
        'answer_options': str(_(
            'JSON list for multiple choice only. Leave empty for fixed or group options.',
        )),
        'question_config': str(_(
            'Advanced JSON only. Use the fields above for word limits and alternatives.',
        )),
        'word_limit': str(_('Maximum words accepted from the student.')),
        'case_insensitive': str(_('Ignore letter case when auto-scoring text answers.')),
        'accept_alternatives_text': str(_(
            'One acceptable answer per line (e.g. mechanized for mechanised).',
        )),
        'group_ref': str(_(
            'Choose a matching group. New groups appear here as soon as you enter a title below.',
        )),
    }

    if is_mcq:
        field_help['correct_answer'] = str(
            _('Must exactly match one of the answer options.'),
        )
    elif is_tfng:
        field_help['correct_answer'] = str(
            _('Enter one of: True, False, Not Given.'),
        )
    elif is_ynng:
        field_help['correct_answer'] = str(
            _('Enter one of: Yes, No, Not Given.'),
        )
    elif is_matching:
        field_help['correct_answer'] = str(
            _('Must exactly match one option from the selected group pool.'),
        )
    elif is_text:
        field_help['correct_answer'] = str(
            _('Primary expected answer used for auto-scoring and student feedback.'),
        )
        field_help['accept_alternatives_text'] = str(_(
            'Other answers that should also count as correct (one per line).',
        ))

    return {
        'question_type': normalized,
        'show_fields': show_fields,
        'hide_fields': hide_fields,
        'clear_fields': clear_fields,
        'field_help': field_help,
    }
