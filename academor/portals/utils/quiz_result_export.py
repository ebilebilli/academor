"""Client-side Word export payload for quiz results (variant / reading / speaking)."""

from __future__ import annotations

import re
from html import unescape

from django.utils.html import strip_tags
from django.utils.translation import gettext as _

from portals.models import QuizResult

_ORPHAN_ATTR_PREFIX_RE = re.compile(
    r'^(?:[a-zA-Z-:]+="[^"]*"\s*)+/?\s*>',
    re.ASCII,
)
_EMPTY_P_RE = re.compile(r'<p(?:\s[^>]*)?>\s*(?:<br\s*/?>)?\s*</p>', re.IGNORECASE)
_LEADING_BR_RE = re.compile(r'^(?:\s*<br\s*/?>)+', re.IGNORECASE)
_HAS_HTML_RE = re.compile(r'<[a-z][\s\S]*>', re.IGNORECASE)


def quiz_result_supports_word_export(quiz) -> bool:
    if not quiz:
        return False
    if quiz.is_listening or quiz.is_essay:
        return False
    return bool(quiz.is_variant_quiz or quiz.is_reading_quiz or quiz.is_speaking)


def _plain(value) -> str:
    """Plain text with real characters — entities like &ne; must not reach Word literally."""
    return unescape(strip_tags(str(value or ''))).strip()


def _rich_html(value) -> str:
    """Keep quiz HTML (formulas/images/special marks) for Word export."""
    if value is None:
        return ''
    text = str(value).strip()
    if not text:
        return ''
    if '&lt;' in text and any(
        token in text for token in ('&lt;p', '&lt;img', '&lt;br', '&lt;strong', '&lt;sub', '&lt;sup')
    ):
        text = unescape(text)
    text = _ORPHAN_ATTR_PREFIX_RE.sub('', text, count=1).strip()
    text = _EMPTY_P_RE.sub('', text)
    text = _LEADING_BR_RE.sub('', text).strip()
    return text


def _is_html(value: str) -> bool:
    return bool(value and _HAS_HTML_RE.search(value))


def _content_field(value) -> dict:
    html = _rich_html(value)
    if not html:
        return {'value': '', 'text': '', 'is_html': False}
    if _is_html(html):
        return {'value': html, 'text': _plain(html), 'is_html': True}
    plain = _plain(html)
    return {'value': plain, 'text': plain, 'is_html': False}


def _owner_name(result: QuizResult) -> str:
    if result.customer_id:
        customer = result.customer
        return customer.full_name if customer else ''
    if result.student_id:
        student = result.student
        return student.full_name if student else ''
    return ''


def _variant_items(result: QuizResult) -> list[dict]:
    from portals.utils.notifications import _build_variant_breakdown

    items = []
    for index, row in enumerate(_build_variant_breakdown(result), start=1):
        question = _content_field(row.get('question'))
        student_answer = _content_field(row.get('student_answer') or row.get('selected_label'))
        correct_answer = _content_field(row.get('correct_label') or row.get('correct_answer'))
        items.append({
            'number': index,
            'question': question,
            'student_answer': student_answer,
            'correct_answer': correct_answer,
            'is_correct': bool(row.get('is_correct')),
            'status': _('Correct') if row.get('is_correct') else _('Incorrect'),
        })
    return items


def _reading_items(result: QuizResult) -> list[dict]:
    from portals.utils.quiz_reading import build_reading_sections_for_quiz

    response_map = {
        str(key): str(value)
        for key, value in (result.given_answers or {}).items()
    }
    teacher_correct_map = {
        str(key): str(value)
        for key, value in (result.teacher_correct_answers or {}).items()
        if str(value).strip()
    }
    sections = build_reading_sections_for_quiz(
        result.quiz_id,
        response_map=response_map,
        correct_answer_map=teacher_correct_map or None,
        use_admin_answer_keys=not teacher_correct_map,
    )
    items = []
    number = 0
    for section in sections:
        for row in section.get('questions') or []:
            number += 1
            is_correct = row.get('is_correct')
            status = ''
            if is_correct is True:
                status = _('Correct')
            elif is_correct is False:
                status = _('Incorrect')
            items.append({
                'number': number,
                'question': _content_field(row.get('question')),
                'student_answer': _content_field(
                    row.get('student_answer_display') or row.get('student_answer'),
                ),
                'correct_answer': _content_field(
                    row.get('correct_answer_display')
                    or row.get('correct_answer'),
                ),
                'is_correct': is_correct,
                'status': status,
            })
    return items


def _speaking_items(result: QuizResult) -> list[dict]:
    from portals.models import SpeakingRecording
    from portals.utils.quiz_speaking import build_speaking_sections_for_quiz

    recording_map = {
        str(recording.question_id): {
            'audio_url': recording.audio_url,
            'duration_sec': recording.duration_sec,
        }
        for recording in SpeakingRecording.objects.filter(result_id=result.pk)
    }
    sections = build_speaking_sections_for_quiz(
        result.quiz_id,
        recording_map=recording_map,
    )
    items = []
    number = 0
    for section in sections:
        for question in section.get('questions') or []:
            number += 1
            duration = question.get('student_duration_sec')
            if question.get('has_recording'):
                answer = _('Audio recording submitted')
                if duration:
                    answer = f'{answer} ({duration}s)'
            else:
                answer = _('No recording')
            # Prefer full HTML prompt when available (images / special marks).
            prompt = question.get('question') or question.get('question_plain') or ''
            items.append({
                'number': number,
                'question': _content_field(prompt),
                'student_answer': _content_field(answer),
                'correct_answer': _content_field(''),
                'is_correct': None,
                'status': '',
            })
    return items


def build_quiz_result_word_export(result: QuizResult) -> dict | None:
    """Return JSON-serializable payload for browser Word download, or None if unsupported."""
    quiz = getattr(result, 'quiz', None)
    if not quiz_result_supports_word_export(quiz):
        return None

    if quiz.is_reading_quiz:
        items = _reading_items(result)
    elif quiz.is_speaking:
        items = _speaking_items(result)
    elif quiz.is_variant_quiz:
        items = _variant_items(result)
    else:
        return None

    score = result.total_score
    if quiz.is_reading_quiz:
        from portals.utils.quiz_reading import get_reading_questions_for_quiz

        question_count = len(get_reading_questions_for_quiz(quiz))
    elif quiz.is_speaking:
        from portals.utils.quiz_speaking import get_speaking_questions_for_quiz

        question_count = len(get_speaking_questions_for_quiz(quiz))
    else:
        question_count = quiz.questions.count()
    max_value = quiz.score_max_value(question_count=question_count)

    owner = _owner_name(result)
    topic = quiz.topic or _('Quiz')
    completed = ''
    if result.completed_at:
        completed = result.completed_at.strftime('%Y-%m-%d %H:%M')

    safe_owner = ''.join(ch if ch.isalnum() or ch in ('-', '_') else '_' for ch in owner)[:40]
    safe_topic = ''.join(ch if ch.isalnum() or ch in ('-', '_') else '_' for ch in topic)[:40]
    filename = f'{safe_owner or "result"}_{safe_topic or "quiz"}.doc'.strip('_')

    score_text = '—'
    if score is not None:
        score_text = f'{score:g}/{max_value:g}' if max_value else f'{score:g}'

    return {
        'filename': filename,
        'title': str(_('Quiz result')),
        'student_label': str(_('Student')),
        'student_name': owner,
        'quiz_label': str(_('Quiz')),
        'quiz_topic': topic,
        'score_label': str(_('Score')),
        'score_text': score_text,
        'date_label': str(_('Submitted')),
        'completed_at': completed,
        'question_label': str(_('Question')),
        'your_answer_label': str(_('Your answer')),
        'correct_answer_label': str(_('Correct answer')),
        'feedback_label': str(_('Teacher feedback')),
        'teacher_feedback': (result.teacher_feedback or '').strip(),
        'items': items,
    }
