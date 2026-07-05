from __future__ import annotations

from django.utils.html import strip_tags
from django.utils.translation import gettext as _

from portals.models import Quiz, SpeakingPart, SpeakingPartType, SpeakingQuestion


# Official IELTS speaking section time labels (exam-style overview).
IELTS_SPEAKING_PART_TIME_LIMITS = {
    SpeakingPartType.PART_1: 300,
    SpeakingPartType.PART_2: None,
    SpeakingPartType.PART_3: 300,
}

IELTS_SPEAKING_PART_HEADINGS = {
    SpeakingPartType.PART_1: _('Part 1 — Introduction & Interview'),
    SpeakingPartType.PART_2: _('Part 2 — Long Turn'),
    SpeakingPartType.PART_3: _('Part 3 — Discussion'),
}


def format_speaking_clock(seconds: int) -> str:
    seconds = max(0, int(seconds or 0))
    minutes, secs = divmod(seconds, 60)
    return f'{minutes:02d}:{secs:02d}'


def speaking_part_heading(part: SpeakingPart) -> str:
    if (part.title or '').strip():
        return part.title.strip()
    return str(IELTS_SPEAKING_PART_HEADINGS.get(part.part_type, part.get_part_type_display()))


def speaking_part_time_limit_seconds(part: SpeakingPart) -> int | None:
    if part.part_type == SpeakingPartType.PART_2:
        return None
    return IELTS_SPEAKING_PART_TIME_LIMITS.get(part.part_type)


def estimate_speaking_quiz_seconds(sections: list[dict]) -> int:
    total = 0
    for section in sections:
        part = section['part']
        if part['is_part_2']:
            total += int(part.get('preparation_seconds') or 0)
            total += int(part.get('default_answer_seconds') or 0)
            continue
        part_limit = part.get('time_limit_seconds')
        if part_limit:
            total += int(part_limit)
            continue
        for question in section.get('questions') or []:
            total += int(question.get('preparation_seconds') or 0)
            total += int(question.get('answer_seconds') or 0)
    return total


def get_quiz_speaking_parts(quiz_id: int):
    return (
        SpeakingPart.objects.filter(quiz_id=quiz_id)
        .prefetch_related('questions')
        .order_by('order', 'id')
    )


def get_speaking_questions_for_quiz(quiz: Quiz) -> list[SpeakingQuestion]:
    if not quiz.is_speaking or not quiz.pk:
        return []
    return [
        question
        for question in SpeakingQuestion.objects.filter(part__quiz_id=quiz.pk)
        .select_related('part')
        .order_by('part__order', 'part_id', 'order', 'id')
        if question.is_answerable
    ]


def serialize_speaking_part(part: SpeakingPart) -> dict:
    part_label = speaking_part_heading(part)
    time_limit_seconds = speaking_part_time_limit_seconds(part)
    prep_seconds = part.resolved_preparation_seconds
    answer_seconds = part.resolved_default_answer_seconds
    return {
        'id': part.pk,
        'part_type': part.part_type,
        'part_type_label': str(part.get_part_type_display()),
        'title': part.title,
        'label': part_label,
        'heading': part_label,
        'instructions': part.instructions,
        'cue_card_topic': part.cue_card_topic,
        'cue_card_bullets': list(part.cue_card_bullets or []),
        'preparation_seconds': prep_seconds,
        'default_answer_seconds': answer_seconds,
        'preparation_clock': format_speaking_clock(prep_seconds),
        'speaking_clock': format_speaking_clock(answer_seconds),
        'time_limit_seconds': time_limit_seconds,
        'time_limit_clock': format_speaking_clock(time_limit_seconds) if time_limit_seconds else '',
        'order': part.order,
        'is_part_1': part.part_type == SpeakingPartType.PART_1,
        'is_part_2': part.part_type == SpeakingPartType.PART_2,
        'is_part_3': part.part_type == SpeakingPartType.PART_3,
        'questions_heading': _('Discussion Questions:') if part.part_type == SpeakingPartType.PART_3 else _('Questions:'),
    }


def serialize_speaking_question(
    question: SpeakingQuestion,
    *,
    student_audio_url: str = '',
    student_duration_sec: int = 0,
    number: int = 0,
    part_question_number: int = 0,
) -> dict:
    part = question.part
    question_text = strip_tags(question.question or '').strip()
    return {
        'id': question.pk,
        'part_id': part.pk,
        'part_type': part.part_type,
        'part_type_label': str(part.get_part_type_display()),
        'number': number,
        'part_question_number': part_question_number or number,
        'question': question.question,
        'question_plain': question_text,
        'preparation_seconds': question.resolved_preparation_seconds,
        'answer_seconds': question.resolved_answer_seconds,
        'student_audio_url': student_audio_url,
        'student_duration_sec': student_duration_sec,
        'has_recording': bool(student_audio_url),
        'cue_card_topic': part.cue_card_topic if part.part_type == SpeakingPartType.PART_2 else '',
        'cue_card_bullets': list(part.cue_card_bullets or []) if part.part_type == SpeakingPartType.PART_2 else [],
    }


def build_speaking_sections_for_quiz(
    quiz_id: int,
    *,
    recording_map: dict | None = None,
) -> list[dict]:
    recording_map = recording_map or {}
    sections: list[dict] = []
    question_number = 0

    for part in get_quiz_speaking_parts(quiz_id):
        part_questions = []
        part_question_number = 0
        for row in part.questions.all().order_by('order', 'id'):
            if not row.is_answerable:
                continue
            question_number += 1
            part_question_number += 1
            recording = recording_map.get(str(row.pk), {})
            part_questions.append(
                serialize_speaking_question(
                    row,
                    student_audio_url=recording.get('audio_url', ''),
                    student_duration_sec=int(recording.get('duration_sec') or 0),
                    number=question_number,
                    part_question_number=part_question_number,
                ),
            )
        sections.append({
            'part': serialize_speaking_part(part),
            'questions': part_questions,
            'section_number': len(sections) + 1,
            'question_count': len(part_questions),
        })

    return sections


def speaking_part_official_instructions(part_type: str) -> str:
    messages = {
        SpeakingPartType.PART_1: _(
            'In this first part the examiner will ask you questions about yourself '
            'and familiar topics. Give short, natural answers.',
        ),
        SpeakingPartType.PART_2: _(
            'You will receive a topic card. You have one minute to prepare and may '
            'make notes. Then speak for one to two minutes on the topic.',
        ),
        SpeakingPartType.PART_3: _(
            'The examiner will ask further questions connected to the Part 2 topic. '
            'Give longer, more developed answers.',
        ),
    }
    return str(messages.get(part_type, ''))
