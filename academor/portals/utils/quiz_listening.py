"""Listening-quiz helpers built on ListeningAudio / ListeningQuestion models."""
from portals.models import ListeningAudio, ListeningQuestion, Quiz


def get_quiz_listening_audios(quiz_id: int):
    return (
        ListeningAudio.objects.filter(quiz_id=quiz_id)
        .prefetch_related('questions')
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


def serialize_listening_question(
    question: ListeningQuestion,
    *,
    student_answer: str = '',
    number: int = 0,
) -> dict:
    from portals.utils.quiz_submit import listening_student_answer_display

    options = question.variant_options
    is_variant = len(options) >= 2
    return {
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
    }


def build_listening_sections_for_quiz(
    quiz_id: int,
    *,
    response_map: dict | None = None,
) -> list[dict]:
    """Build student-facing sections from a listening quiz."""
    response_map = response_map or {}
    sections: list[dict] = []
    question_number = 0

    for audio in get_quiz_listening_audios(quiz_id):
        section_questions = []
        for row in audio.questions.all().order_by('order', 'id'):
            if not row.is_answerable:
                continue
            question_number += 1
            section_questions.append(
                serialize_listening_question(
                    row,
                    student_answer=response_map.get(str(row.pk), ''),
                    number=question_number,
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
