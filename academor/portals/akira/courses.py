"""Which courses AKIRA works for, and what it needs to know about each one.

AKIRA itself is course-neutral: the analytics, the AI client and the screens take a
``CourseProfile`` and never look for "SAT" by name. Adding General English, IELTS,
FMVA, DipIFR or any other programme means adding one profile here (and, when the
course has them, skill tags on its questions). A profile with ``enabled=False`` is a
reserved slot: AKIRA stays silent for that course until it is switched on.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CourseProfile:
    code: str  # portal course code, the same codes ``portal_services`` uses
    label: str
    family: str  # sat | ielts | english | finance | other
    enabled: bool = False
    # Rough pace target for one question, in seconds (None: the course has no pace target).
    target_sec_per_question: int | None = None
    # One line for the AI: what this course is and what a good result means.
    brief: str = ''
    # Skill areas in the order a teacher would read them (optional; empty = take them from the questions).
    domains: tuple[str, ...] = field(default_factory=tuple)
    # Maximum scaled score of one section, when the course has a scale (SAT: 800).
    section_scale_max: int | None = None


SAT_MATH = CourseProfile(
    code='sat-math',
    label='SAT Math',
    family='sat',
    enabled=True,
    target_sec_per_question=95,  # 35 minutes / 22 questions per module
    brief='Digital SAT Math section (scaled 200-800).',
    domains=('Algebra', 'Advanced Math', 'Problem-Solving and Data Analysis', 'Geometry and Trigonometry'),
    section_scale_max=800,
)

SAT_VERBAL = CourseProfile(
    code='sat-verbal',
    label='SAT Reading and Writing',
    family='sat',
    enabled=True,
    target_sec_per_question=71,  # 32 minutes / 27 questions per module
    brief='Digital SAT Reading and Writing section (scaled 200-800).',
    domains=('Information and Ideas', 'Craft and Structure', 'Expression of Ideas', 'Standard English Conventions'),
    section_scale_max=800,
)

# Reserved slots: the system is ready for them, AKIRA switches on when each is enabled.
IELTS = CourseProfile(code='ielts', label='IELTS', family='ielts', brief='IELTS Academic / General (band 0-9).')
GENERAL_ENGLISH = CourseProfile(code='general_english', label='General English', family='english', brief='General English course.')
FMVA = CourseProfile(code='fmva', label='FMVA', family='finance', brief='Financial Modeling & Valuation Analyst (CFI).')
DIPIFR = CourseProfile(code='dipifr', label='DipIFR', family='finance', brief='ACCA Diploma in International Financial Reporting.')

COURSES: dict[str, CourseProfile] = {
    profile.code: profile
    for profile in (SAT_MATH, SAT_VERBAL, IELTS, GENERAL_ENGLISH, FMVA, DIPIFR)
}

# Other spellings of the same course that appear in services and quizzes.
_ALIASES = {
    'sat_math': 'sat-math',
    'sat-verbal': 'sat-verbal',
    'sat_verbal': 'sat-verbal',
    'sat-rw': 'sat-verbal',
    'general-english': 'general_english',
    'english': 'general_english',
}


def get_course(code: str | None) -> CourseProfile | None:
    if not code:
        return None
    key = str(code).strip().lower()
    return COURSES.get(_ALIASES.get(key, key))


def active_course(code: str | None) -> CourseProfile | None:
    """The profile when AKIRA is switched on for this course, else None."""
    profile = get_course(code)
    return profile if profile and profile.enabled else None


def course_for_quiz(quiz) -> CourseProfile | None:
    """The course a portal quiz belongs to (SAT quizzes: by their section)."""
    if quiz is None:
        return None
    if getattr(quiz, 'is_sat', False):
        return SAT_MATH if getattr(quiz, 'is_math', False) or _is_math_section(quiz) else SAT_VERBAL
    return get_course(getattr(quiz, 'service_code', ''))


def _is_math_section(quiz) -> bool:
    math_sections = getattr(type(quiz), 'SAT_MATH_SECTIONS', frozenset({'algebra', 'geometry_data'}))
    return str(getattr(quiz, 'sat_section', '') or '') in math_sections
