"""Public level tests that run portal quizzes (SAT, IELTS Reading, IELTS Listening).

A public ``Test`` with ``portal_quizzes`` is an exam: each quiz is one section, shown with the
portal exam screen and scored with the portal scorers. Nothing is copied: the questions are
read live from the portal. The visitor's attempt lives in ``UserResult`` (created when they
enter their name and phone) and in the session (which section is next, when it started).
"""

from __future__ import annotations

import math

from django.db.models import Prefetch
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.translation import gettext as _

SESSION_KEY = 'level_exam'
# a little slack on top of the limit for slow networks / auto-submit round trips
TIME_GRACE_SEC = 90

KIND_SAT = 'sat'
KIND_IELTS_READING = 'ielts_reading'
KIND_IELTS_LISTENING = 'ielts_listening'
KIND_GENERAL = 'general'

SECTION_SAT_RW = 'sat_rw'
SECTION_SAT_MATH = 'sat_math'
SECTION_READING = 'reading'
SECTION_LISTENING = 'listening'
SECTION_VARIANT = 'variant'

# official exam timing, used when the portal quiz has no limit of its own
DEFAULT_MINUTES = {
    SECTION_SAT_RW: 64,
    SECTION_SAT_MATH: 70,
    SECTION_READING: 60,
    SECTION_LISTENING: 40,
}

TAKE_TEMPLATES = {
    'reading': 'portals/student/quiz_take_reading.html',
    'listening': 'portals/student/quiz_take_manual.html',
    'variant': 'portals/student/quiz_take.html',
}

# IELTS raw score (out of 40) -> band. Academic Reading and Listening, official tables.
_LISTENING_BANDS = (
    (39, 9.0), (37, 8.5), (35, 8.0), (32, 7.5), (30, 7.0), (26, 6.5), (23, 6.0),
    (18, 5.5), (16, 5.0), (13, 4.5), (10, 4.0), (8, 3.5), (6, 3.0), (4, 2.5), (2, 2.0), (1, 1.0),
)
_READING_BANDS = (
    (39, 9.0), (37, 8.5), (35, 8.0), (33, 7.5), (30, 7.0), (27, 6.5), (23, 6.0),
    (19, 5.5), (15, 5.0), (13, 4.5), (10, 4.0), (8, 3.5), (6, 3.0), (4, 2.5), (2, 2.0), (1, 1.0),
)


# ---------------------------------------------------------------- sections

def section_kind(quiz) -> str:
    """What the section is (for labels, timing and bands)."""
    if quiz.is_sat:
        math_sections = {quiz.SatSection.ALGEBRA, quiz.SatSection.GEOMETRY_DATA}
        return SECTION_SAT_MATH if (quiz.is_math or quiz.sat_section in math_sections) else SECTION_SAT_RW
    if quiz.is_math:
        return SECTION_SAT_MATH
    if quiz.is_reading:
        return SECTION_READING
    if quiz.is_listening:
        return SECTION_LISTENING
    return SECTION_VARIANT


FORMAT_READING = 'reading'
FORMAT_LISTENING = 'listening'
FORMAT_VARIANT = 'variant'


def section_format(quiz) -> str:
    """How the portal stores and shows the questions (SAT practice tests are often plain MCQ)."""
    if quiz.is_reading or quiz.is_math:
        return FORMAT_READING
    if quiz.is_listening:
        return FORMAT_LISTENING
    return FORMAT_VARIANT


def is_supported_quiz(quiz) -> bool:
    """Auto-scored formats only: writing / speaking need a teacher."""
    return not (quiz.is_speaking or (quiz.is_manual_grading and not quiz.is_listening))


def exam_quizzes(test) -> list:
    """The test's portal quizzes in exam order: Reading & Writing before Math."""
    quizzes = [q for q in test.portal_quizzes.all() if is_supported_quiz(q)]
    return sorted(quizzes, key=lambda q: (1 if section_kind(q) == SECTION_SAT_MATH else 0, q.order, q.pk))


def exam_kind(quizzes) -> str:
    if not quizzes:
        return KIND_GENERAL
    if any(section_kind(q) in (SECTION_SAT_RW, SECTION_SAT_MATH) for q in quizzes):
        return KIND_SAT
    kinds = {section_kind(q) for q in quizzes}
    if kinds == {SECTION_LISTENING}:
        return KIND_IELTS_LISTENING
    if kinds == {SECTION_READING}:
        return KIND_IELTS_READING
    return KIND_GENERAL


def section_label(quiz) -> str:
    kind = section_kind(quiz)
    if kind == SECTION_SAT_RW:
        return _('Reading and Writing')
    if kind == SECTION_SAT_MATH:
        return _('Math')
    if kind == SECTION_READING:
        return _('Reading')
    if kind == SECTION_LISTENING:
        return _('Listening')
    return quiz.topic


def section_minutes(quiz) -> int | None:
    if quiz.is_time_limited and quiz.time_limit_minutes:
        return int(quiz.time_limit_minutes)
    return DEFAULT_MINUTES.get(section_kind(quiz))


def _load_quiz(quiz_id: int):
    from portals.models import Quiz, QuizQuestion

    return (
        Quiz.objects.filter(pk=quiz_id)
        .select_related('category')
        .prefetch_related(Prefetch('questions', queryset=QuizQuestion.objects.order_by('order', 'id')))
        .first()
    )


def build_take_payload(quiz) -> dict | None:
    """Same data the portal exam screen gets, minus any student access checks."""
    from portals.utils.queries import serialize_quiz, serialize_quiz_question_for_student

    fmt = section_format(quiz)
    base = {**serialize_quiz(quiz), 'view_only': False, 'is_pending_review': False, 'is_mock_section': True}

    if fmt == FORMAT_READING:
        from portals.utils.quiz_reading import build_reading_sections_for_quiz, get_reading_questions_for_quiz

        if not get_reading_questions_for_quiz(quiz):
            return None
        sections = build_reading_sections_for_quiz(quiz.pk)
        flat = [row for section in sections for row in section['questions']]
        payload = {**base, 'questions': flat, 'reading_sections': sections}
        ids = [row['id'] for row in flat]
    elif fmt == FORMAT_LISTENING:
        from portals.utils.quiz_listening import build_listening_sections_for_quiz, get_listening_questions_for_quiz

        if not get_listening_questions_for_quiz(quiz):
            return None
        sections = build_listening_sections_for_quiz(quiz.pk)
        flat = [row for section in sections for row in section['questions']]
        payload = {**base, 'questions': flat, 'listening_sections': sections}
        ids = [row['id'] for row in flat]
    else:
        questions = [q for q in quiz.questions.all() if q.is_answerable]
        if not questions:
            return None
        payload = {**base, 'questions': [serialize_quiz_question_for_student(q) for q in questions]}
        ids = [q.pk for q in questions]

    payload['response_question_ids'] = ids
    payload['response_question_count'] = len(ids)
    minutes = section_minutes(quiz)
    payload['is_time_limited'] = bool(minutes)
    payload['time_limit_minutes'] = minutes
    payload['time_limit_seconds'] = minutes * 60 if minutes else 0
    return payload


def question_count(quiz) -> int:
    fmt = section_format(quiz)
    if fmt == FORMAT_READING:
        from portals.utils.quiz_reading import get_reading_questions_for_quiz

        return len(get_reading_questions_for_quiz(quiz))
    if fmt == FORMAT_LISTENING:
        from portals.utils.quiz_listening import get_listening_questions_for_quiz

        return len(get_listening_questions_for_quiz(quiz))
    return sum(1 for q in quiz.questions.all() if q.is_answerable)


# ---------------------------------------------------------------- scoring

def score_section(quiz, data: dict) -> dict:
    """Score one submitted section with the portal scorers. Correct answers are not returned."""
    answers = data.get('answers') or {}
    fmt = section_format(quiz)
    if fmt == FORMAT_READING:
        from portals.utils.quiz_reading import get_reading_questions_for_quiz
        from portals.utils.quiz_reading_score import normalize_reading_answers, score_reading_quiz

        questions = get_reading_questions_for_quiz(quiz)
        given = normalize_reading_answers(quiz, answers, ordered_answers=data.get('ordered_answers'), questions=questions)
        score, total, breakdown = score_reading_quiz(quiz, given, questions=questions)
    elif fmt == FORMAT_LISTENING:
        from portals.utils.quiz_listening import get_listening_questions_for_quiz
        from portals.utils.quiz_listening_score import score_listening_quiz
        from portals.utils.quiz_submit import _normalize_listening_model_answers

        questions = get_listening_questions_for_quiz(quiz)
        given = _normalize_listening_model_answers(
            answers, quiz, ordered_answers=data.get('ordered_answers'), questions=questions,
        )
        score, total, breakdown = score_listening_quiz(quiz, given, questions=questions)
    else:
        from portals.utils.quiz_submit import score_variant_quiz

        score, total, breakdown = score_variant_quiz(quiz, answers)

    # question numbers as the student saw them; fall back to position when they repeat
    numbers = [item.get('number') for item in breakdown]
    use_own_numbers = all(numbers) and len(set(numbers)) == len(numbers)
    stored, wrong, unanswered = {}, [], []
    for index, item in enumerate(breakdown, start=1):
        number = item['number'] if use_own_numbers else index
        raw = item.get('student_answer', item.get('selected_index'))
        if raw in (None, ''):
            unanswered.append(number)
            continue
        stored[str(item['id'])] = raw
        if not item.get('is_correct'):
            wrong.append(number)
    return {
        'correct': int(score),
        'total': int(total),
        'answers': stored,
        'wrong': wrong,
        'unanswered': unanswered,
    }


def ielts_band(kind: str, correct: int, total: int) -> float | None:
    """Official raw-to-band table; a test shorter than 40 questions is scaled to 40."""
    if kind not in (KIND_IELTS_READING, KIND_IELTS_LISTENING) or not total:
        return None
    raw40 = int(round(correct * 40 / total)) if total != 40 else correct
    table = _LISTENING_BANDS if kind == KIND_IELTS_LISTENING else _READING_BANDS
    for minimum, band in table:
        if raw40 >= minimum:
            return band
    return 0.0


def format_band(band: float | None) -> str:
    if band is None:
        return ''
    return f'{band:.1f}'


def summary_level(kind: str, sections: list[dict]) -> str:
    """Short line for UserResult.level / CRM (max 50 chars)."""
    if kind == KIND_SAT:
        parts = []
        for row in sections:
            short = 'R&W' if row.get('kind') == SECTION_SAT_RW else ('Math' if row.get('kind') == SECTION_SAT_MATH else 'S')
            parts.append(f"{short} {row['correct']}/{row['total']}")
        return ' · '.join(parts)[:50]
    if kind in (KIND_IELTS_READING, KIND_IELTS_LISTENING) and sections:
        row = sections[0]
        return f"Band {format_band(row.get('band'))} ({row['correct']}/{row['total']})"[:50]
    return ' · '.join(f"{row['correct']}/{row['total']}" for row in sections)[:50]


# ---------------------------------------------------------------- session attempt

def get_attempt(request, test_id: int) -> dict | None:
    data = request.session.get(SESSION_KEY) or {}
    attempt = data.get(str(test_id))
    return attempt if isinstance(attempt, dict) and attempt.get('result_id') else None


def save_attempt(request, test_id: int, attempt: dict | None) -> None:
    data = dict(request.session.get(SESSION_KEY) or {})
    if attempt is None:
        data.pop(str(test_id), None)
    else:
        data[str(test_id)] = attempt
    request.session[SESSION_KEY] = data
    request.session.modified = True


def elapsed_seconds(started_at: str | None) -> int | None:
    parsed = parse_datetime(started_at) if started_at else None
    if not parsed:
        return None
    if timezone.is_naive(parsed):
        parsed = timezone.make_aware(parsed, timezone.get_current_timezone())
    return max(0, int((timezone.now() - parsed).total_seconds()))


def section_was_late(quiz, started_at: str | None) -> bool:
    minutes = section_minutes(quiz)
    elapsed = elapsed_seconds(started_at)
    if not minutes or elapsed is None:
        return False
    return elapsed > minutes * 60 + TIME_GRACE_SEC


def percent(correct: int, total: int) -> int:
    return int(math.floor(100 * correct / total)) if total else 0


# ---------------------------------------------------------------- SAT scaled score

def parse_sat_score_table(text: str) -> dict:
    """College Board raw-to-scale table pasted in the admin -> {'rw': {raw: (lo, hi)}, 'math': {...}}.

    Rows look like "40 620 640", "40 600-640 620-660" or "58 - 750"; anything else is skipped.
    """
    table = {'rw': {}, 'math': {}}
    for line in (text or '').splitlines():
        parts = line.replace(';', ' ').replace(',', ' ').replace('\t', ' ').split()
        if len(parts) < 2 or not parts[0].isdigit():
            continue
        raw = int(parts[0])
        for key, cell in zip(('rw', 'math'), parts[1:3]):
            cell = cell.replace('–', '-').replace('—', '-')
            if cell == '-' or not cell:
                continue
            bounds = [b for b in cell.split('-') if b]
            if not bounds or not all(b.isdigit() for b in bounds):
                continue
            low, high = int(bounds[0]), int(bounds[-1])
            if 200 <= low <= high <= 800:
                table[key][raw] = (low, high)
    return table


def sat_scaled_scores(test, sections: list[dict]) -> dict | None:
    """Estimated SAT section scores (and total when both sections are there) from the admin table."""
    table = parse_sat_score_table(getattr(test, 'sat_score_table', ''))
    if not table['rw'] and not table['math']:
        return None
    rows = []
    for row in sections:
        key = 'math' if row.get('kind') == SECTION_SAT_MATH else 'rw'
        found = table[key].get(int(row.get('correct') or 0))
        if found is None:
            continue
        rows.append({'quiz_id': row.get('quiz_id'), 'kind': key, 'low': found[0], 'high': found[1]})
    if not rows:
        return None
    result = {'sections': {r['quiz_id']: r for r in rows}}
    kinds = {r['kind'] for r in rows}
    if kinds == {'rw', 'math'} and len(rows) == 2:
        result['total_low'] = sum(r['low'] for r in rows)
        result['total_high'] = sum(r['high'] for r in rows)
    return result


def format_score_range(low: int, high: int) -> str:
    return str(low) if low == high else f'{low}–{high}'
