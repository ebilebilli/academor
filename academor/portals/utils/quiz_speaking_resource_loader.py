"""Load IELTS-style speaking quizzes from JSON resource files."""

from __future__ import annotations

import json
from pathlib import Path

from django.db import transaction

from portals.models import Quiz, QuizCategory
from portals.models.speaking_models import SpeakingPart, SpeakingPartType, SpeakingQuestion
from portals.utils.cache_utils import invalidate_model_cache

RESOURCES_DIR = Path(__file__).resolve().parent.parent / 'resources' / 'speaking_questions'

DEFAULT_SERVICE = 'ielts'

PART_TYPES = {choice.value for choice in SpeakingPartType}


def _normalize_part_type(raw: str, *, context: str) -> str:
    normalized = (raw or '').strip()
    if normalized not in PART_TYPES:
        raise ValueError(f'{context}: unsupported part_type "{raw}".')
    return normalized


def _normalize_question(raw: dict, *, context: str, default_order: int) -> dict:
    order = int(raw.get('order') or default_order)
    preparation_seconds = raw.get('preparation_seconds')
    answer_seconds = raw.get('answer_seconds')
    return {
        'order': order,
        'question': (raw.get('question') or '').strip(),
        'preparation_seconds': int(preparation_seconds) if preparation_seconds is not None else None,
        'answer_seconds': int(answer_seconds) if answer_seconds is not None else None,
    }


def _normalize_part(raw: dict, *, context: str, default_order: int) -> dict:
    order = int(raw.get('order') or default_order)
    part_type = _normalize_part_type(raw.get('part_type'), context=context)
    questions_raw = raw.get('questions') or []
    if not isinstance(questions_raw, list) or not questions_raw:
        raise ValueError(f'{context}: questions must be a non-empty list.')

    cue_card_topic = (raw.get('cue_card_topic') or '').strip()
    if part_type == SpeakingPartType.PART_2 and not cue_card_topic:
        raise ValueError(f'{context}: cue_card_topic is required for Part 2.')

    bullets = [
        str(item).strip()
        for item in (raw.get('cue_card_bullets') or [])
        if str(item).strip()
    ]

    preparation_seconds = raw.get('preparation_seconds')
    default_answer_seconds = raw.get('default_answer_seconds')

    return {
        'order': order,
        'part_type': part_type,
        'title': (raw.get('title') or '').strip(),
        'instructions': (raw.get('instructions') or '').strip(),
        'cue_card_topic': cue_card_topic,
        'cue_card_bullets': bullets,
        'preparation_seconds': int(preparation_seconds) if preparation_seconds is not None else None,
        'default_answer_seconds': int(default_answer_seconds) if default_answer_seconds is not None else None,
        'questions': [
            _normalize_question(
                item,
                context=f'{context}, question #{index + 1}',
                default_order=index + 1,
            )
            for index, item in enumerate(questions_raw)
        ],
    }


def parse_speaking_resource_file(path: Path) -> dict:
    data = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data, dict):
        raise ValueError(f'{path.name}: root must be a JSON object.')

    service = (data.get('service') or DEFAULT_SERVICE).strip()
    category_name = (data.get('category_name') or '').strip()
    if not category_name:
        raise ValueError(f'{path.name}: category_name is required.')

    title = (data.get('title') or data.get('name') or path.stem).strip()
    parts_raw = data.get('parts') or []
    if not isinstance(parts_raw, list) or not parts_raw:
        raise ValueError(f'{path.name}: parts must be a non-empty list.')

    parts = [
        _normalize_part(
            item,
            context=f'{path.name}, part #{index + 1}',
            default_order=index + 1,
        )
        for index, item in enumerate(parts_raw)
    ]

    return {
        'resource_slug': path.stem,
        'resource_name': title,
        'service': service,
        'category_name': category_name,
        'parts': parts,
    }


def sync_speaking_quiz_content(
    quiz: Quiz,
    parsed: dict,
    *,
    replace_existing: bool = True,
) -> dict:
    if replace_existing:
        SpeakingPart.objects.filter(quiz=quiz).delete()

    part_count = 0
    question_count = 0

    for part_data in parsed['parts']:
        part = SpeakingPart(
            quiz=quiz,
            order=part_data['order'],
            part_type=part_data['part_type'],
            title=part_data['title'],
            instructions=part_data['instructions'],
            cue_card_topic=part_data['cue_card_topic'],
            cue_card_bullets=part_data['cue_card_bullets'],
            preparation_seconds=part_data['preparation_seconds'],
            default_answer_seconds=part_data['default_answer_seconds'],
        )
        part.full_clean()
        part.save()
        part_count += 1

        for item in part_data['questions']:
            question = SpeakingQuestion(
                part=part,
                order=item['order'],
                question=item['question'],
                preparation_seconds=item['preparation_seconds'],
                answer_seconds=item['answer_seconds'],
            )
            question.full_clean()
            question.save()
            question_count += 1

    return {
        'parts': part_count,
        'questions': question_count,
    }


@transaction.atomic
def load_speaking_resource_file(path: Path, *, replace_existing: bool = True) -> dict:
    parsed = parse_speaking_resource_file(path)
    category, _ = QuizCategory.objects.get_or_create(
        service=parsed['service'],
        name=parsed['category_name'],
    )

    defaults = {
        'topic': parsed['resource_name'],
        'is_speaking': True,
        'is_listening': False,
        'is_essay': False,
        'is_reading': False,
        'is_time_limited': False,
        'time_limit_minutes': None,
    }

    quiz = Quiz.objects.filter(resource_slug=parsed['resource_slug']).first()
    if quiz:
        quiz_created = False
        for field, value in defaults.items():
            setattr(quiz, field, value)
        quiz.category = category
    else:
        quiz, quiz_created = Quiz.objects.update_or_create(
            category=category,
            resource_slug=parsed['resource_slug'],
            defaults=defaults,
        )
    quiz.full_clean()
    quiz.save()

    content_stats = sync_speaking_quiz_content(
        quiz,
        parsed,
        replace_existing=replace_existing,
    )
    invalidate_model_cache('Quiz')

    return {
        'file': path.name,
        'category': str(category),
        'category_id': category.pk,
        'category_name': category.name,
        'quiz_created': quiz_created,
        'quiz_id': quiz.pk,
        'quiz_topic': quiz.topic,
        **content_stats,
    }


def load_all_speaking_resources(*, replace_existing: bool = True) -> list[dict]:
    if not RESOURCES_DIR.exists():
        return []

    results = []
    for path in sorted(RESOURCES_DIR.glob('*.json')):
        results.append(load_speaking_resource_file(path, replace_existing=replace_existing))
    return results
