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
    'spr_correct_answers',
    'spr_max_length',
    'accept_alternatives_text',
    'correct_option_number',
    'correct_answer',
    'correct_option_index',
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

    show_fields = ['question']
    hide_fields: list[str] = []
    clear_fields: list[str] = []

    if is_text:
        show_fields.extend([
            'spr_correct_answers',
            'spr_max_length',
            'word_limit',
            'case_insensitive',
            'question_config',
        ])
        hide_fields.extend([
            'correct_option_number',
            'correct_answer',
            'correct_option_index',
            'accept_alternatives_text',
        ])
        clear_fields.append('accept_alternatives_text')
    else:
        show_fields.append('correct_option_number')
        hide_fields.extend([
            'correct_answer',
            'correct_option_index',
            'spr_correct_answers',
            'spr_max_length',
            'word_limit',
            'case_insensitive',
            'accept_alternatives_text',
            'question_config',
        ])
        clear_fields.extend([
            'spr_correct_answers',
            'spr_max_length',
            'word_limit',
            'case_insensitive',
            'accept_alternatives_text',
            'question_config',
        ])

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

    field_help: dict[str, str] = {
        'question': str(_(
            'Prompt, table, flow-chart, or diagram context. '
            'Leave blank for a numbered answer line only when appropriate.',
        )),
        'correct_option_number': str(_(
            'Enter 1 for Option 1, 2 for Option 2, 3 for Option 3, 4 for Option 4. '
            'This is what auto-scoring uses.',
        )),
        'correct_answer': str(_('Exact text for gap-fill tasks or the matching option label.')),
        'answer_options': str(_(
            'Add answer choices using the + button for multiple choice. '
            'Leave empty for matching or typed tasks.',
        )),
        'question_config': str(_(
            'Advanced JSON only. Prefer SPR answers and word limit fields above.',
        )),
        'word_limit': str(_('Maximum words accepted from the student (IELTS NO MORE THAN N WORDS).')),
        'case_insensitive': str(_('Ignore letter case when auto-scoring text answers.')),
        'spr_correct_answers': str(_(
            'One or more accepted correct answers for typed gap-fill tasks '
            '(e.g. library / the library).',
        )),
        'spr_max_length': str(_(
            'Optional character limit for the student typed answer. Leave blank for free text.',
        )),
        'accept_alternatives_text': str(_(
            'Legacy field — prefer SPR correct answers.',
        )),
        'group_ref': str(_(
            'Choose a matching group. New groups appear here as soon as you enter a title below.',
        )),
    }

    if is_mcq:
        field_help['correct_option_number'] = str(
            _('Enter the option number (1 = first option, 2 = second, …).'),
        )
    elif is_tfng:
        field_help['correct_option_number'] = str(
            _('Enter 1 for True, 2 for False, 3 for Not Given.'),
        )
    elif is_ynng:
        field_help['correct_option_number'] = str(
            _('Enter 1 for Yes, 2 for No, 3 for Not Given.'),
        )
    elif is_matching:
        field_help['correct_option_number'] = str(
            _('Enter the option number from the selected group pool (1 = first, 2 = second, …).'),
        )

    return {
        'question_type': normalized,
        'show_fields': show_fields,
        'hide_fields': hide_fields,
        'clear_fields': clear_fields,
        'field_help': field_help,
    }
