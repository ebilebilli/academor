"""Load quizzes and questions from JSON resource files."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from django.db import transaction

from portals.models import Quiz, QuizCategory, QuizQuestion

RESOURCES_DIR = Path(__file__).resolve().parent.parent / 'resources' / 'quiz_questions'


DEFAULT_SERVICE = 'general_english'


def _as_bool(value) -> bool:
    if isinstance(value, str):
        return value.strip().lower() in {'1', 'true', 'yes', 'y', 'on'}
    return bool(value)


def _question_is_dropdown(raw: dict, quiz_default: bool = False) -> bool:
    for key in ('type', 'answer_type', 'answer_ui'):
        if str(raw.get(key) or '').strip().lower() == 'dropdown':
            return True
    question_type = str(raw.get('question_type') or '').strip().lower()
    if question_type == 'dropdown':
        return True
    if 'is_dropdown' in raw:
        return _as_bool(raw.get('is_dropdown'))
    return quiz_default


def _source_key(resource_slug: str, raw: dict, index: int, question_text: str) -> str:
    question_id = raw.get('id')
    if question_id is not None:
        return f'{resource_slug}:q{question_id}'
    digest = hashlib.sha1(f'{resource_slug}:{index}:{question_text}'.encode('utf-8')).hexdigest()
    return digest[:16]


def _normalize_question(
    raw: dict,
    index: int,
    resource_slug: str,
    *,
    quiz_is_dropdown: bool = False,
) -> dict:
    question = (raw.get('question') or '').strip()
    if not question:
        raise ValueError(f'Question #{index + 1} in {resource_slug} is missing text.')

    # Determine question type (MCQ or SPR)
    question_type = (raw.get('question_type') or 'mcq').strip().lower()
    is_dropdown = _question_is_dropdown(raw, quiz_is_dropdown)
    if question_type == 'dropdown':
        question_type = 'mcq'
        is_dropdown = True

    if question_type == 'spr':
        # SPR (Student-Produced Response) validation
        spr_correct_answers = raw.get('spr_correct_answers') or []
        if not isinstance(spr_correct_answers, list):
            raise ValueError(f'Question #{index + 1} in {resource_slug}: spr_correct_answers must be a list.')
        
        if not spr_correct_answers:
            raise ValueError(f'Question #{index + 1} in {resource_slug}: SPR questions must have at least one correct answer.')
        
        spr_max_length = raw.get('spr_max_length')
        if spr_max_length is not None:
            spr_max_length = int(spr_max_length)
        
        return {
            'source_key': _source_key(resource_slug, raw, index, question),
            'question': question,
            'question_type': QuizQuestion.QuestionType.SPR,
            'is_dropdown': False,
            'answer_options': [],
            'correct_answer': '',
            'correct_option_index': 0,
            'spr_correct_answers': spr_correct_answers,
            'spr_max_length': spr_max_length,
        }
    else:
        # MCQ (Multiple Choice) validation
        options_raw = raw.get('options') or raw.get('answer_options') or []
        options = [str(item).strip() for item in options_raw if str(item).strip()]
        if len(options) < 2:
            raise ValueError(f'Question #{index + 1} in {resource_slug} needs at least two options.')

        correct = (raw.get('correct') or raw.get('correct_answer') or '').strip()
        if not correct and raw.get('answer') is not None and raw.get('answer') != '':
            try:
                answer_index = int(raw['answer'])
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f'Question #{index + 1} in {resource_slug}: invalid answer index.',
                ) from exc
            if not 0 <= answer_index < len(options):
                raise ValueError(
                    f'Question #{index + 1} in {resource_slug}: answer index out of range.',
                )
            correct = options[answer_index]

        if not correct:
            raise ValueError(f'Question #{index + 1} in {resource_slug} is missing correct answer.')
        if correct not in options:
            raise ValueError(
                f'Question #{index + 1} in {resource_slug}: correct answer must match an option.',
            )

        return {
            'source_key': _source_key(resource_slug, raw, index, question),
            'question': question,
            'question_type': QuizQuestion.QuestionType.MCQ,
            'is_dropdown': is_dropdown,
            'answer_options': options,
            'correct_answer': correct,
            'correct_option_index': options.index(correct),
            'spr_correct_answers': None,
            'spr_max_length': None,
        }


def parse_resource_file(path: Path) -> dict:
    data = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data, dict):
        raise ValueError(f'{path.name}: root must be a JSON object.')

    level = (data.get('level') or '').strip()
    service = (data.get('service') or DEFAULT_SERVICE).strip()
    category_name = (data.get('category_name') or level or '').strip()
    if not category_name:
        raise ValueError(f'{path.name}: level or category_name is required.')

    questions_raw = data.get('questions') or []
    if not isinstance(questions_raw, list) or not questions_raw:
        raise ValueError(f'{path.name}: questions must be a non-empty list.')

    quiz_number = data.get('quiz')
    title = (data.get('title') or data.get('name') or '').strip()
    if title:
        resource_name = title
    elif level and quiz_number is not None:
        resource_name = f'{level} Quiz {quiz_number}'
    else:
        resource_name = path.stem

    resource_slug = path.stem
    quiz_is_dropdown = _as_bool(data.get('is_dropdown')) or str(
        data.get('answer_ui') or '',
    ).strip().lower() == 'dropdown'
    questions = [
        _normalize_question(item, index, resource_slug, quiz_is_dropdown=quiz_is_dropdown)
        for index, item in enumerate(questions_raw)
    ]

    return {
        'resource_slug': resource_slug,
        'resource_name': resource_name,
        'level': level,
        'service': service,
        'category_name': category_name,
        'is_sat': bool(data.get('is_sat')),
        'sat_section': (data.get('sat_section') or '').strip(),
        'time_limit_minutes': data.get('time_limit_minutes'),
        'has_shared_passage': bool(data.get('has_shared_passage')),
        'shared_passage': (data.get('shared_passage') or data.get('passage') or '').strip(),
        'shared_youtube_url': (data.get('shared_youtube_url') or '').strip(),
        'questions': questions,
    }


def ensure_quiz_from_resource(parsed: dict, category: QuizCategory) -> tuple[Quiz, bool]:
    """Create or update a Quiz row for a loaded JSON resource."""
    has_shared = bool(parsed.get('has_shared_passage'))
    shared_passage = (parsed.get('shared_passage') or '').strip()
    shared_youtube_url = (parsed.get('shared_youtube_url') or '').strip()
    if has_shared and not shared_passage:
        raise ValueError(
            f'{parsed["resource_slug"]}: has_shared_passage is true but shared_passage is empty.',
        )
    if has_shared and shared_youtube_url:
        from portals.utils.lesson_media import extract_youtube_video_id

        if not extract_youtube_video_id(shared_youtube_url):
            raise ValueError(
                f'{parsed["resource_slug"]}: shared_youtube_url must be a valid YouTube URL.',
            )

    defaults = {
        'topic': parsed['resource_name'],
        'is_listening': False,
        'is_essay': False,
        'is_speaking': False,
        'is_reading': False,
        'is_math': False,
        'is_ielts': False,
        'is_sat': parsed.get('is_sat', False),
        'sat_section': parsed.get('sat_section', ''),
        'has_shared_passage': has_shared,
        'shared_passage': shared_passage if has_shared else '',
        'shared_youtube_url': shared_youtube_url if has_shared else '',
    }
    time_limit = parsed.get('time_limit_minutes')
    if time_limit:
        defaults['is_time_limited'] = True
        defaults['time_limit_minutes'] = int(time_limit)

    quiz, created = Quiz.objects.update_or_create(
        category=category,
        resource_slug=parsed['resource_slug'],
        defaults=defaults,
    )
    return quiz, created


def sync_quiz_questions(
    quiz: Quiz,
    parsed: dict,
    *,
    deactivate_missing: bool = True,
) -> dict:
    """Upsert QuizQuestion rows on the quiz from parsed resource data."""
    seen_keys: set[str] = set()
    created = 0
    updated = 0

    for index, item in enumerate(parsed['questions']):
        seen_keys.add(item['source_key'])
        obj, was_created = QuizQuestion.objects.update_or_create(
            quiz=quiz,
            source_key=item['source_key'],
            defaults={
                'order': index + 1,
                'prompt_type': QuizQuestion.PromptType.TEXT,
                'question_type': item['question_type'],
                'is_dropdown': item.get('is_dropdown', False),
                'question': item['question'],
                'answer_options': item['answer_options'],
                'correct_answer': item['correct_answer'],
                'correct_option_index': item['correct_option_index'],
                'spr_correct_answers': item['spr_correct_answers'],
                'spr_max_length': item['spr_max_length'],
            },
        )
        if was_created:
            created += 1
        else:
            updated += 1

    deleted = 0
    if deactivate_missing:
        deleted, _ = (
            QuizQuestion.objects.filter(quiz=quiz)
            .exclude(source_key__in=seen_keys)
            .delete()
        )

    return {
        'created': created,
        'updated': updated,
        'deleted': deleted,
        'total': quiz.questions.count(),
    }


@transaction.atomic
def load_resource_file(path: Path, *, deactivate_missing: bool = True) -> dict:
    from portals.utils.quiz_category_services import ensure_quiz_category

    parsed = parse_resource_file(path)
    category, _ = ensure_quiz_category(parsed['service'], parsed['category_name'])

    quiz, quiz_created = ensure_quiz_from_resource(parsed, category)
    question_stats = sync_quiz_questions(
        quiz,
        parsed,
        deactivate_missing=deactivate_missing,
    )

    return {
        'file': path.name,
        'category': str(category),
        'quiz_created': quiz_created,
        'quiz_id': quiz.pk,
        'quiz_topic': quiz.topic,
        **question_stats,
    }


def load_all_resources(*, deactivate_missing: bool = True) -> list[dict]:
    if not RESOURCES_DIR.exists():
        return []

    results = []
    for path in sorted(RESOURCES_DIR.glob('*.json')):
        results.append(load_resource_file(path, deactivate_missing=deactivate_missing))
    return results