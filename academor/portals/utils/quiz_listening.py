"""Listening-quiz helpers built on ListeningAudio / ListeningQuestion models."""

from django.db.models import Prefetch, QuerySet

from portals.models import ListeningAudio, ListeningQuestion, Quiz


def build_listening_spr_answers(question: ListeningQuestion) -> list[str]:
    """
    Build accepted SPR answers for a gap-fill listening question.

    Prefer existing spr_correct_answers; otherwise seed from correct_answer
    and question_config.accept_alternatives (legacy JSON / admin single-answer).
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


def convert_listening_gapfill_to_spr(
    question: ListeningQuestion,
    *,
    save: bool = True,
) -> bool:
    """
    Convert a typed gap-fill ListeningQuestion (no MCQ options) to SPR fields.

    Returns True when spr_correct_answers was written/updated.
    MCQ questions (2+ answer_options) are skipped.
    """
    if len(question.variant_options) >= 2:
        return False

    answers = build_listening_spr_answers(question)
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


def convert_listening_queryset_gapfill_to_spr(qs: QuerySet) -> dict:
    """Bulk-convert gap-fill listening questions in a queryset to SPR."""
    converted = 0
    skipped_mcq = 0
    skipped_empty = 0
    for question in qs.iterator():
        if len(question.variant_options) >= 2:
            skipped_mcq += 1
            continue
        if convert_listening_gapfill_to_spr(question, save=True):
            converted += 1
        else:
            skipped_empty += 1
    return {
        'converted': converted,
        'skipped_mcq': skipped_mcq,
        'skipped_empty': skipped_empty,
    }


def get_quiz_listening_audios(quiz_id: int):
    return (
        ListeningAudio.objects.filter(quiz_id=quiz_id)
        .prefetch_related(
            Prefetch(
                'questions',
                queryset=ListeningQuestion.objects.order_by('order', 'id'),
            ),
        )
        .order_by('order', 'id')
    )


def get_listening_questions_for_quiz(quiz: Quiz) -> list[ListeningQuestion]:
    if not quiz.is_listening or not quiz.pk:
        return []
    return [
        question
        for question in ListeningQuestion.objects.filter(audio__quiz_id=quiz.pk)
        .select_related('audio')
        .order_by('audio__order', 'audio_id', 'order', 'id')
        if question.is_answerable
    ]


def serialize_listening_audio(audio: ListeningAudio) -> dict:
    return {
        'id': audio.pk,
        'title': audio.title,
        'question': audio.title or audio.description,
        'description': audio.description,
        'prompt_type': 'audio',
        'media_file_url': audio.media_file_url,
        'media_url': audio.audio_url,
        'order': audio.order,
        'requires_student_response': False,
    }


def listening_correct_option_index(question: ListeningQuestion) -> int | None:
    options = question.variant_options
    if len(options) < 2:
        return None
    correct = (question.correct_answer or '').strip()
    if correct and correct in options:
        return options.index(correct)
    index = question.correct_option_index
    if 0 <= index < len(options):
        return index
    return None


def listening_selected_option_index(question: ListeningQuestion, raw_value) -> int | None:
    from portals.utils.quiz_submit import _looks_like_variant_index

    if not _looks_like_variant_index(raw_value, question):
        return None
    return int(str(raw_value).strip())


def listening_accept_alternatives(question: ListeningQuestion) -> list[str]:
    config = question.question_config or {}
    return [
        str(item).strip()
        for item in (config.get('accept_alternatives') or [])
        if str(item).strip()
    ]


def listening_correct_answer_display(question: ListeningQuestion) -> str:
    from django.utils.translation import gettext as _

    answers = question.spr_accepted_answers
    if not answers:
        primary = (question.correct_answer or '').strip()
        alternatives = listening_accept_alternatives(question)
        if not alternatives:
            return primary
        if not primary:
            return ', '.join(alternatives)
        return f'{primary} ({_("also")}: {", ".join(alternatives)})'
    if len(answers) == 1:
        return answers[0]
    return f'{answers[0]} ({_("also")}: {", ".join(answers[1:])})'


def serialize_listening_question(
    question: ListeningQuestion,
    *,
    student_answer: str = '',
    number: int = 0,
    use_admin_answer_keys: bool = False,
) -> dict:
    from portals.utils.quiz_submit import listening_student_answer_display

    options = question.variant_options
    is_variant = len(options) >= 2
    payload = {
        'id': question.pk,
        'audio_id': question.audio_id,
        'question': question.question,
        'order': question.order,
        'student_answer': student_answer,
        'student_answer_display': listening_student_answer_display(question, student_answer),
        'requires_student_response': True,
        'number': number,
        'prompt_type': 'variant' if is_variant else 'text',
        'is_variant': is_variant,
        'answer_options': options if is_variant else [],
        'spr_max_length': question.spr_max_length if not is_variant else None,
        'question_type': 'variant' if is_variant else 'spr',
    }
    if is_variant:
        selected_index = listening_selected_option_index(question, student_answer)
        payload.update({
            'selected_option_index': selected_index,
            'has_selected_option': selected_index is not None,
        })

    if use_admin_answer_keys:
        from portals.utils.quiz_listening_score import score_listening_question

        payload['correct_answer'] = question.correct_answer
        payload['correct_answer_display'] = listening_correct_answer_display(question)
        payload['spr_correct_answers'] = list(question.spr_accepted_answers)
        if is_variant:
            payload['correct_option_index'] = listening_correct_option_index(question)
        if student_answer not in ('', None):
            payload['is_correct'] = score_listening_question(question, student_answer)
        else:
            payload['is_correct'] = False
    return payload


def build_listening_sections_for_quiz(
    quiz_id: int,
    *,
    response_map: dict | None = None,
    use_admin_answer_keys: bool = False,
) -> list[dict]:
    """Build student-facing sections from a listening quiz."""
    response_map = response_map or {}
    sections: list[dict] = []
    question_number = 0

    for audio in get_quiz_listening_audios(quiz_id):
        section_questions = []
        for row in audio.questions.all():
            if not row.is_answerable:
                continue
            question_number += 1
            section_questions.append(
                serialize_listening_question(
                    row,
                    student_answer=response_map.get(str(row.pk), ''),
                    number=question_number,
                    use_admin_answer_keys=use_admin_answer_keys,
                )
            )
        sections.append({
            'audio': serialize_listening_audio(audio),
            'questions': section_questions,
            'section_number': len(sections) + 1,
            'question_range_start': section_questions[0]['number'] if section_questions else None,
            'question_range_end': section_questions[-1]['number'] if section_questions else None,
        })

    return sections
