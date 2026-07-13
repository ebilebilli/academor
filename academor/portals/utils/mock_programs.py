"""Exam-program configuration for portal mock tests."""

from __future__ import annotations

from dataclasses import dataclass

from django.utils.translation import gettext_lazy as _


IELTS_SERVICE = 'ielts'
SAT_SERVICE = 'sat'

MOCK_EXAM_PROGRAMS = (IELTS_SERVICE, SAT_SERVICE)

PROGRAM_QUIZ_FLAG_FIELD = {
    IELTS_SERVICE: 'is_ielts',
    SAT_SERVICE: 'is_sat',
}

PROGRAM_LABELS = {
    IELTS_SERVICE: _('IELTS'),
    SAT_SERVICE: _('SAT'),
}

IELTS_BAND_MAX = 9.0
SAT_SECTION_SCORE_MIN = 200
SAT_SECTION_SCORE_MAX = 800
SAT_TOTAL_SCORE_MAX = 1600


@dataclass(frozen=True)
class MockSectionSpec:
    key: str
    label: str
    quiz_flags: dict[str, bool]
    quiz_field: str
    result_field: str
    take_url_kind: str
    auto_graded: bool
    category_names: tuple[str, ...] = ()
    sat_sections: tuple[str, ...] = ()


IELTS_SECTIONS: tuple[MockSectionSpec, ...] = (
    MockSectionSpec(
        'listening',
        _('Listening'),
        {'is_listening': True},
        'listening_quiz',
        'listening_result',
        'manual',
        True,
    ),
    MockSectionSpec(
        'reading',
        _('Reading'),
        {'is_reading': True},
        'reading_quiz',
        'reading_result',
        'reading',
        True,
    ),
    MockSectionSpec(
        'writing',
        _('Writing'),
        {'is_essay': True},
        'writing_quiz',
        'writing_result',
        'manual',
        False,
    ),
    MockSectionSpec(
        'speaking',
        _('Speaking'),
        {'is_speaking': True},
        'speaking_quiz',
        'speaking_result',
        'speaking',
        False,
    ),
)

SAT_SECTIONS: tuple[MockSectionSpec, ...] = (
    MockSectionSpec(
        'reading_writing',
        _('Reading and Writing'),
        {},
        'reading_quiz',
        'reading_result',
        'variant',
        True,
        ('SAT Reading and Writing',),
        ('reading', 'writing'),
    ),
    MockSectionSpec(
        'math',
        _('Math'),
        {},
        'math_quiz',
        'math_result',
        'variant',
        True,
        ('SAT Math',),
        ('algebra', 'geometry_data'),
    ),
)

MOCK_PROGRAM_CONFIG: dict[str, dict] = {
    IELTS_SERVICE: {
        'sections': IELTS_SECTIONS,
        'scoring': 'ielts_band',
        'first_section': 'listening',
    },
    SAT_SERVICE: {
        'sections': SAT_SECTIONS,
        'scoring': 'sat_scaled',
        'first_section': 'reading_writing',
    },
}


def is_valid_mock_program(exam_program: str | None) -> bool:
    return exam_program in MOCK_PROGRAM_CONFIG


def get_program_sections(exam_program: str) -> tuple[MockSectionSpec, ...]:
    config = MOCK_PROGRAM_CONFIG.get(exam_program) or {}
    return config.get('sections', ())


def get_program_first_section(exam_program: str) -> str | None:
    config = MOCK_PROGRAM_CONFIG.get(exam_program) or {}
    return config.get('first_section')


def get_program_scoring_mode(exam_program: str) -> str:
    config = MOCK_PROGRAM_CONFIG.get(exam_program) or {}
    return config.get('scoring', 'ielts_band')


def get_section_spec(exam_program: str, section_key: str) -> MockSectionSpec | None:
    for spec in get_program_sections(exam_program):
        if spec.key == section_key:
            return spec
    return None


def get_section_label(exam_program: str, section_key: str, *, translate: bool = True) -> str:
    spec = get_section_spec(exam_program, section_key)
    if not spec:
        return section_key
    if not translate:
        # Fixed English exam section names (Listening, Math, …).
        return {
            'listening': 'Listening',
            'reading': 'Reading',
            'writing': 'Writing',
            'speaking': 'Speaking',
            'reading_writing': 'Reading and Writing',
            'math': 'Math',
        }.get(section_key, section_key)
    return str(spec.label)


def get_section_order(exam_program: str) -> tuple[str, ...]:
    return tuple(spec.key for spec in get_program_sections(exam_program))


def get_next_section(exam_program: str, section_key: str) -> str | None:
    order = get_section_order(exam_program)
    try:
        index = order.index(section_key)
    except ValueError:
        return None
    if index + 1 >= len(order):
        return None
    return order[index + 1]


def get_auto_sections(exam_program: str) -> frozenset[str]:
    return frozenset(spec.key for spec in get_program_sections(exam_program) if spec.auto_graded)


def get_manual_sections(exam_program: str) -> frozenset[str]:
    return frozenset(spec.key for spec in get_program_sections(exam_program) if not spec.auto_graded)


def get_program_quiz_filters(exam_program: str) -> dict[str, bool]:
    flag_field = PROGRAM_QUIZ_FLAG_FIELD.get(exam_program)
    if not flag_field:
        return {}
    return {flag_field: True}


def get_take_url_name(role: str, take_url_kind: str) -> str:
    mapping = {
        'variant': f'portals:{role}-quiz-take',
        'manual': f'portals:{role}-manual-quiz-take',
        'reading': f'portals:{role}-reading-quiz-take',
        'speaking': f'portals:{role}-speaking-quiz-take',
    }
    return mapping[take_url_kind]


def resolve_take_url_kind(exam_program: str, section_key: str, quiz) -> str:
    """Pick student/customer take view from quiz format (SAT reading uses passage UI)."""
    from portals.models import Quiz

    spec = get_section_spec(exam_program, section_key)
    if not spec:
        return 'variant'
    if exam_program == SAT_SERVICE and isinstance(quiz, Quiz):
        if quiz.is_reading:
            return 'reading'
        if quiz.is_essay or quiz.is_listening:
            return 'manual'
        if quiz.is_speaking:
            return 'speaking'
        return 'variant'
    return spec.take_url_kind


def get_mock_landing_url_name(role: str) -> str:
    return f'portals:{role}-mock-landing'


def get_mock_complete_url_name(role: str) -> str:
    return f'portals:{role}-mock-complete'


def section_index_for_program(exam_program: str, section_key: str) -> int:
    order = get_section_order(exam_program)
    try:
        return order.index(section_key) + 1
    except ValueError:
        return 0


def is_final_section(exam_program: str, section_key: str) -> bool:
    order = get_section_order(exam_program)
    return bool(order) and section_key == order[-1]


def sat_section_scaled_score(total_score, max_score) -> int | None:
    if total_score is None or max_score is None or max_score <= 0:
        return None
    ratio = float(total_score) / float(max_score)
    scaled = SAT_SECTION_SCORE_MIN + ratio * (SAT_SECTION_SCORE_MAX - SAT_SECTION_SCORE_MIN)
    return int(round(scaled))


def program_overall_score_label(exam_program: str) -> str:
    if get_program_scoring_mode(exam_program) == 'sat_scaled':
        return str(_('Total score'))
    return str(_('Overall band'))


def get_program_label(exam_program: str) -> str:
    return str(PROGRAM_LABELS.get(exam_program, exam_program))
