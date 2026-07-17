"""Load quizzes and questions from JSON resource files."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from django.db import transaction

from portals.models import Quiz, QuizCategory, QuizQuestion

RESOURCES_DIR = Path(__file__).resolve().parent.parent / 'resources' / 'quiz_questions'


DEFAULT_SERVICE = 'general_english'


def _source_key(resource_slug: str, raw: dict, index: int, question_text: str) -> str:
    question_id = raw.get('id')
    if question_id is not None:
        return f'{resource_slug}:q{question_id}'
    digest = hashlib.sha1(f'{resource_slug}:{index}:{question_text}'.encode('utf-8')).hexdigest()
    return digest[:16]


def _normalize_question(raw: dict, index: int, resource_slug: str) -> dict:
    question = (raw.get('question') or '').strip()
    if not question:
        raise ValueError(f'Question #{index + 1} in {resource_slug} is missing text.')

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
        'answer_options': options,
        'correct_answer': correct,
        'correct_option_index': options.index(correct),
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
    questions = [
        _normalize_question(item, index, resource_slug)
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
        'questions': questions,
    }


def ensure_quiz_from_resource(parsed: dict, category: QuizCategory) -> tuple[Quiz, bool]:
    """Create or update a Quiz row for a loaded JSON resource."""
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
                'question': item['question'],
                'answer_options': item['answer_options'],
                'correct_answer': item['correct_answer'],
                'correct_option_index': item['correct_option_index'],
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