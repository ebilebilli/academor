"""Reading-quiz helpers built on ReadingPassage / ReadingQuestion models."""

from __future__ import annotations

from django.db.models import Prefetch, QuerySet

from portals.models import ReadingPassage, ReadingQuestion, Quiz
from portals.models.reading_models import (
    CHOICE_QUESTION_TYPES,
    TEXT_QUESTION_TYPES,
    ReadingQuestionGroup,
    matching_option_index,
    resolve_reading_question_options,
)


def build_reading_spr_answers(question: ReadingQuestion) -> list[str]:
    """
    Build accepted SPR answers for a typed reading question.

    Prefer spr_correct_answers; otherwise seed from correct_answer and
    question_config.accept_alternatives (legacy gap-fill admin/JSON).
    """
    from portals.utils.sat_spr_validation import plain_spr_text

    answers = [
        plain_spr_text(item)
        for item in (question.spr_correct_answers or [])
        if plain_spr_text(item)
    ]
    if answers:
        return answers

    combined: list[str] = []
    primary = plain_spr_text(question.correct_answer or '')
    if primary:
        combined.append(primary)
    config = question.question_config or {}
    for item in config.get('accept_alternatives') or []:
        text = plain_spr_text(item)
        if text and text not in combined:
            combined.append(text)
    return combined


def convert_reading_gapfill_to_spr(
    question: ReadingQuestion,
    *,
    save: bool = True,
) -> bool:
    """Convert a typed reading gap-fill question to SPR fields. Returns True if updated."""
    if question.question_type not in TEXT_QUESTION_TYPES:
        return False

    answers = build_reading_spr_answers(question)
    if not answers:
        return False

    already = [
        str(item).strip()
        for item in (question.spr_correct_answers or [])
        if str(item).strip()
    ]
    if already == answers and (question.correct_answer or '').strip() == answers[0][:500]:
        return False

    question.answer_options = []
    question.correct_option_index = 0
    question.spr_correct_answers = answers
    question.correct_answer = answers[0][:500]
    if save:
        question.save(
            update_fields=[
                'answer_options',
                'correct_option_index',
                'spr_correct_answers',
                'correct_answer',
            ],
        )
    return True


def convert_reading_queryset_gapfill_to_spr(qs: QuerySet) -> dict:
    """Bulk-convert typed reading questions in a queryset to SPR."""
    converted = 0
    skipped_choice = 0
    skipped_empty = 0
    for question in qs.iterator():
        if question.question_type not in TEXT_QUESTION_TYPES:
            skipped_choice += 1
            continue
        if convert_reading_gapfill_to_spr(question, save=True):
            converted += 1
        else:
            skipped_empty += 1
    return {
        'converted': converted,
        'skipped_choice': skipped_choice,
        'skipped_empty': skipped_empty,
    }


def resolve_question_options(question: ReadingQuestion) -> list[str]:
    return resolve_reading_question_options(question)


def get_quiz_reading_passages(quiz_id: int):
    return (
        ReadingPassage.objects.filter(quiz_id=quiz_id)
        .prefetch_related(
            Prefetch(
                'question_groups',
                queryset=ReadingQuestionGroup.objects.order_by('order', 'id'),
            ),
            Prefetch(
                'questions',
                queryset=(
                    ReadingQuestion.objects
                    .select_related('group')
                    .order_by('order', 'id')
                ),
            ),
        )
        .order_by('order', 'id')
    )


def get_reading_questions_for_quiz(quiz: Quiz) -> list[ReadingQuestion]:
    if not quiz.is_reading_quiz or not quiz.pk:
        return []
    return [
        question
        for question in ReadingQuestion.objects.filter(passage__quiz_id=quiz.pk)
        .select_related('passage', 'group')
        .order_by('passage__order', 'passage_id', 'order', 'id')
        if question.is_answerable
    ]


def reading_question_interaction_family(question: ReadingQuestion) -> str:
    if question.question_type in CHOICE_QUESTION_TYPES:
        return 'choice'
    if question.question_type in TEXT_QUESTION_TYPES:
        return 'text'
    return 'text'


def serialize_reading_passage(passage: ReadingPassage) -> dict:
    return {
        'id': passage.pk,
        'title': passage.title,
        'instructions': passage.instructions,
        'body': passage.body,
        'order': passage.order,
    }


def serialize_reading_question_group(group) -> dict:
    return {
        'id': group.pk,
        'title': group.title,
        'instructions': group.instructions,
        'question_type': group.question_type,
        'group_type': group.question_type,
        'question_type_label': group.get_question_type_display(),
        'option_pool': group.pool_options,
        'question_config': {},
        'order': group.order,
    }


def reading_correct_option_index(question: ReadingQuestion) -> int | None:
    options = question.variant_options
    if len(options) < 2:
        return None
    index = question.correct_option_index
    if 0 <= index < len(options):
        return index
    correct = (question.correct_answer or '').strip()
    return matching_option_index(options, correct)


def reading_selected_option_index(question: ReadingQuestion, raw_value) -> int | None:
    from portals.utils.quiz_submit import _looks_like_variant_index

    if not _looks_like_variant_index(raw_value, question):
        return None
    return int(str(raw_value).strip())


def reading_student_answer_display(question: ReadingQuestion, raw_value) -> str:
    from portals.utils.quiz_submit import listening_student_answer_display

    return listening_student_answer_display(question, raw_value)


def reading_accept_alternatives(question: ReadingQuestion) -> list[str]:
    answers = build_reading_spr_answers(question)
    if len(answers) > 1:
        return answers[1:]
    config = question.question_config or {}
    return [
        str(item).strip()
        for item in (config.get('accept_alternatives') or [])
        if str(item).strip()
    ]


def reading_correct_answer_display(question: ReadingQuestion) -> str:
    from django.utils.translation import gettext as _

    answers = build_reading_spr_answers(question)
    if not answers:
        primary = (question.correct_answer or '').strip()
        alternatives = reading_accept_alternatives(question)
        if not alternatives:
            return primary
        if not primary:
            return ', '.join(alternatives)
        return f'{primary} ({_("also")}: {", ".join(alternatives)})'
    if len(answers) == 1:
        return answers[0]
    return f'{answers[0]} ({_("also")}: {", ".join(answers[1:])})'


def reading_teacher_answer_matches(
    question: ReadingQuestion,
    student_raw,
    teacher_correct: str,
) -> bool:
    teacher = str(teacher_correct or '').strip()
    if not teacher:
        return False
    if question.question_type in CHOICE_QUESTION_TYPES:
        student_label = reading_student_answer_display(question, student_raw).strip()
        student_raw_text = str(student_raw or '').strip()
        options = question.variant_options
        if matching_option_index(options, teacher) is not None:
            teacher_index = matching_option_index(options, teacher)
            if student_raw_text.isdigit():
                index = int(student_raw_text)
                if 0 <= index < len(options) and index == teacher_index:
                    return True
            if student_label and matching_option_index(options, student_label) == teacher_index:
                return True
            if student_raw_text and matching_option_index(options, student_raw_text) == teacher_index:
                return True
            return False
        teacher_norm = teacher.casefold()
        if student_label and student_label.casefold() == teacher_norm:
            return True
        if student_raw_text and student_raw_text.casefold() == teacher_norm:
            return True
        if student_raw_text.isdigit():
            index = int(student_raw_text)
            if 0 <= index < len(options) and options[index].casefold() == teacher_norm:
                return True
        return False

    from portals.utils.quiz_reading_score import score_reading_question

    # Teacher override: temporarily score against the teacher key as primary SPR answer.
    original_spr = question.spr_correct_answers
    original_correct = question.correct_answer
    try:
        question.spr_correct_answers = [teacher]
        question.correct_answer = teacher[:500]
        return score_reading_question(question, student_raw)
    finally:
        question.spr_correct_answers = original_spr
        question.correct_answer = original_correct


def serialize_reading_question(
    question: ReadingQuestion,
    *,
    student_answer: str = '',
    number: int = 0,
    correct_answer_map: dict | None = None,
    use_admin_answer_keys: bool = False,
) -> dict:
    options = question.variant_options
    is_choice = reading_question_interaction_family(question) == 'choice'
    config = question.question_config or {}
    payload = {
        'id': question.pk,
        'passage_id': question.passage_id,
        'group_id': question.group_id,
        'question': question.question,
        'order': question.order,
        'question_type': question.question_type,
        'question_type_label': question.get_question_type_display(),
        'interaction_family': reading_question_interaction_family(question),
        'student_answer': student_answer,
        'student_answer_display': (
            reading_student_answer_display(question, student_answer)
            if is_choice
            else str(student_answer or '').strip()
        ),
        'requires_student_response': True,
        'number': number,
        'is_choice': is_choice,
        'is_text': not is_choice,
        'answer_options': options if is_choice else [],
        'word_limit': config.get('word_limit'),
        'word_limit_label': config.get('word_limit_label', ''),
        'spr_max_length': question.spr_max_length if not is_choice else None,
        'question_config': config,
    }
    if is_choice:
        selected_index = reading_selected_option_index(question, student_answer)
        payload.update({
            'selected_option_index': selected_index,
            'has_selected_option': selected_index is not None,
        })

    if correct_answer_map is not None:
        teacher_correct = str(correct_answer_map.get(str(question.pk), '') or '').strip()
        payload['correct_answer'] = teacher_correct
        payload['correct_answer_display'] = teacher_correct
        if teacher_correct and student_answer not in ('', None):
            payload['is_correct'] = reading_teacher_answer_matches(
                question,
                student_answer,
                teacher_correct,
            )
        elif teacher_correct:
            payload['is_correct'] = False
        else:
            payload['is_correct'] = None
    elif use_admin_answer_keys:
        from portals.utils.quiz_reading_score import score_reading_question

        payload['correct_answer'] = question.correct_answer
        payload['accept_alternatives'] = reading_accept_alternatives(question)
        payload['spr_correct_answers'] = list(build_reading_spr_answers(question))
        payload['correct_answer_display'] = reading_correct_answer_display(question)
        if student_answer not in ('', None):
            payload['is_correct'] = score_reading_question(question, student_answer)
        else:
            payload['is_correct'] = False
    return payload


def reading_display_number(question: ReadingQuestion, *, fallback: int) -> int:
    """Prefer admin Order for student-facing labels (IELTS Q27, Q31, …)."""
    order = getattr(question, 'order', None)
    try:
        order_int = int(order)
    except (TypeError, ValueError):
        order_int = 0
    return order_int if order_int > 0 else fallback


def build_reading_sections_for_quiz(
    quiz_id: int,
    *,
    response_map: dict | None = None,
    correct_answer_map: dict | None = None,
    use_admin_answer_keys: bool = False,
) -> list[dict]:
    response_map = response_map or {}
    sections: list[dict] = []
    fallback_number = 0

    for passage in get_quiz_reading_passages(quiz_id):
        groups = [
            serialize_reading_question_group(group)
            for group in passage.question_groups.all()
        ]
        section_questions = []
        seen_group_ids: set[int] = set()
        # Prefetch already orders by (order, id); keep that as render order.
        for row in passage.questions.all():
            if not row.is_answerable:
                continue
            fallback_number += 1
            group_start = False
            group_instructions = None
            if row.group_id and row.group_id not in seen_group_ids:
                seen_group_ids.add(row.group_id)
                group_start = True
                group_instructions = serialize_reading_question_group(row.group)
            question_payload = serialize_reading_question(
                row,
                student_answer=response_map.get(str(row.pk), ''),
                number=reading_display_number(row, fallback=fallback_number),
                correct_answer_map=correct_answer_map,
                use_admin_answer_keys=use_admin_answer_keys,
            )
            question_payload['group_start'] = group_start
            if group_instructions is not None:
                question_payload['group_instructions'] = group_instructions
            section_questions.append(question_payload)
        numbers = [item['number'] for item in section_questions]
        sections.append({
            'passage': serialize_reading_passage(passage),
            'groups': groups,
            'questions': section_questions,
            'section_number': len(sections) + 1,
            'question_range_start': min(numbers) if numbers else None,
            'question_range_end': max(numbers) if numbers else None,
        })

    return sections
