"""Load IELTS-style reading quizzes from JSON resource files."""

from __future__ import annotations

import json
import re
from pathlib import Path

from django.db import transaction
from django.core.exceptions import ValidationError

from portals.models import Quiz
from portals.models.reading_models import (
    GROUP_QUESTION_TYPES,
    MATCHING_QUESTION_TYPES,
    ReadingPassage,
    ReadingQuestion,
    ReadingQuestionGroup,
    ReadingQuestionType,
    matching_option_index,
)

RESOURCES_DIR = Path(__file__).resolve().parent.parent / 'resources' / 'reading_questions'

DEFAULT_SERVICE = 'ielts'
QUESTION_TYPE_ALIASES = {
    'matching_paragraph_information': ReadingQuestionType.MATCHING_INFO,
    'mcq_multi': ReadingQuestionType.MCQ,
    'flow_chart_completion': ReadingQuestionType.FLOWCHART_COMPLETION,
    'flow-chart-completion': ReadingQuestionType.FLOWCHART_COMPLETION,
    'diagram_label_completion': ReadingQuestionType.DIAGRAM_LABEL,
}
_QUESTION_RANGE_RE = re.compile(
    r'Questions?\s+(\d+)\s*[–—-]\s*(\d+)',
    re.IGNORECASE,
)


def _parse_question_range(text: str) -> tuple[int, int] | None:
    match = _QUESTION_RANGE_RE.search(text or '')
    if not match:
        return None
    start, end = int(match.group(1)), int(match.group(2))
    if start > end:
        return None
    return start, end


def _is_relative_one_based(orders: list[int]) -> bool:
    return bool(orders) and orders == list(range(1, len(orders) + 1))


def _is_consecutive(orders: list[int]) -> bool:
    if not orders:
        return False
    sorted_orders = sorted(orders)
    return sorted_orders == list(range(sorted_orders[0], sorted_orders[0] + len(sorted_orders)))


def _apply_absolute_orders_from_title(questions: list[dict], title: str) -> None:
    """Map relative 1..n group orders onto 'Questions 31–35' style titles."""
    title_range = _parse_question_range(title)
    if not title_range:
        return
    start, end = title_range
    if end - start + 1 != len(questions):
        return
    if not _is_relative_one_based([item['order'] for item in questions]):
        return
    for index, item in enumerate(questions):
        item['order'] = start + index


def _apply_absolute_orders_for_passage(
    *,
    groups: list[dict],
    standalone: list[dict],
    title: str,
    instructions: str,
) -> None:
    """Fill absolute IELTS numbers for standalones using passage range minus group claims."""
    for group in groups:
        _apply_absolute_orders_from_title(group['questions'], group.get('title') or '')

    if not standalone:
        return

    passage_range = _parse_question_range(instructions) or _parse_question_range(title)
    if not passage_range:
        return
    start, end = passage_range
    claimed = {
        item['order']
        for group in groups
        for item in group['questions']
    }
    available = [number for number in range(start, end + 1) if number not in claimed]
    if len(available) != len(standalone):
        return

    current_orders = sorted(item['order'] for item in standalone)
    if current_orders == available:
        return

    orders = [item['order'] for item in standalone]
    if not (_is_relative_one_based(orders) or _is_consecutive(orders)):
        return

    for item, order in zip(standalone, available):
        item['order'] = order



def _require_text(value, *, field: str, context: str) -> str:
    text = (value or '').strip()
    if not text:
        raise ValueError(f'{context}: {field} is required.')
    return text


def _normalize_question_type(raw: str, *, context: str) -> str:
    normalized = (raw or ReadingQuestionType.MCQ).strip()
    normalized = QUESTION_TYPE_ALIASES.get(normalized, normalized)
    if normalized not in ReadingQuestionType.values:
        raise ValueError(f'{context}: unsupported question_type "{raw}".')
    return normalized


def _normalize_question(raw: dict, *, context: str, default_order: int) -> dict:
    order = int(raw.get('order') or default_order)
    question_type = _normalize_question_type(raw.get('question_type'), context=context)
    question = (raw.get('question') or '').strip()
    correct_answer = (raw.get('correct_answer') or '').strip()
    if not correct_answer:
        raise ValueError(f'{context}: correct_answer is required.')

    payload = {
        'order': order,
        'question_type': question_type,
        'question': question,
        'correct_answer': correct_answer,
        'answer_options': [
            str(item).strip()
            for item in (raw.get('answer_options') or [])
            if str(item).strip()
        ],
        'question_config': raw.get('question_config') or {},
        'group_order': raw.get('group_order'),
    }
    return payload


def _normalize_group(raw: dict, *, context: str, default_order: int) -> dict:
    order = int(raw.get('order') or default_order)
    question_type = _normalize_question_type(raw.get('question_type'), context=context)
    if question_type not in GROUP_QUESTION_TYPES:
        raise ValueError(f'{context}: unsupported group question_type.')

    option_pool = [
        str(item).strip()
        for item in (raw.get('option_pool') or [])
        if str(item).strip()
    ]
    if question_type in MATCHING_QUESTION_TYPES:
        if len(option_pool) < 2:
            raise ValueError(f'{context}: option_pool needs at least two items.')
    else:
        option_pool = []

    questions_raw = raw.get('questions') or []
    if not isinstance(questions_raw, list) or not questions_raw:
        raise ValueError(f'{context}: questions must be a non-empty list.')

    questions = [
        _normalize_question(
            {**item, 'question_type': item.get('question_type') or question_type},
            context=f'{context}, group question #{index + 1}',
            default_order=index + 1,
        )
        for index, item in enumerate(questions_raw)
    ]
    for item in questions:
        if item['question_type'] != question_type:
            raise ValueError(
                f'{context}: group question type must match group question_type.',
            )
        if question_type in MATCHING_QUESTION_TYPES and matching_option_index(option_pool, item['correct_answer']) is None:
            raise ValueError(
                f'{context}: correct_answer must match an option in option_pool.',
            )

    return {
        'order': order,
        'title': (raw.get('title') or '').strip(),
        'instructions': (raw.get('instructions') or '').strip(),
        'question_type': question_type,
        'option_pool': option_pool,
        'questions': questions,
    }


def _normalize_passage(raw: dict, *, context: str, default_order: int) -> dict:
    order = int(raw.get('order') or default_order)
    body = _require_text(raw.get('body'), field='body', context=context)

    groups_raw = raw.get('question_groups') or []
    if not isinstance(groups_raw, list):
        raise ValueError(f'{context}: question_groups must be a list.')

    groups = [
        _normalize_group(
            item,
            context=f'{context}, group #{index + 1}',
            default_order=index + 1,
        )
        for index, item in enumerate(groups_raw)
    ]

    questions_raw = raw.get('questions') or []
    if not isinstance(questions_raw, list):
        raise ValueError(f'{context}: questions must be a list.')

    standalone_questions = [
        _normalize_question(
            item,
            context=f'{context}, question #{index + 1}',
            default_order=index + 1,
        )
        for index, item in enumerate(questions_raw)
    ]

    if not groups and not standalone_questions:
        raise ValueError(f'{context}: add question_groups and/or questions.')

    title = (raw.get('title') or '').strip()
    instructions = (raw.get('instructions') or '').strip()
    _apply_absolute_orders_for_passage(
        groups=groups,
        standalone=standalone_questions,
        title=title,
        instructions=instructions,
    )

    return {
        'order': order,
        'title': title,
        'instructions': instructions,
        'body': body,
        'question_groups': groups,
        'questions': standalone_questions,
    }


def parse_reading_resource_file(path: Path) -> dict:
    data = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data, dict):
        raise ValueError(f'{path.name}: root must be a JSON object.')

    service = (data.get('service') or DEFAULT_SERVICE).strip()
    category_name = (data.get('category_name') or '').strip()
    if not category_name:
        raise ValueError(f'{path.name}: category_name is required.')

    title = (data.get('title') or data.get('name') or path.stem).strip()
    passages_raw = data.get('passages') or []
    if not isinstance(passages_raw, list) or not passages_raw:
        raise ValueError(f'{path.name}: passages must be a non-empty list.')

    passages = [
        _normalize_passage(
            item,
            context=f'{path.name}, passage #{index + 1}',
            default_order=index + 1,
        )
        for index, item in enumerate(passages_raw)
    ]

    return {
        'resource_slug': path.stem,
        'resource_name': title,
        'service': service,
        'category_name': category_name,
        'time_limit_minutes': data.get('time_limit_minutes'),
        'passages': passages,
    }


def _create_question(
    passage: ReadingPassage,
    *,
    group: ReadingQuestionGroup | None,
    item: dict,
) -> ReadingQuestion:
    question = ReadingQuestion(
        passage=passage,
        group=group,
        order=item['order'],
        question_type=item['question_type'],
        question=item['question'],
        answer_options=item['answer_options'],
        correct_answer=item['correct_answer'],
        question_config=item['question_config'],
    )
    try:
        question.full_clean()
    except ValidationError as exc:
        pool = group.pool_options if group else item['answer_options']
        raise ValueError(
            f"Passage {passage.title!r} (order={passage.order}), "
            f"question order={item['order']}, type={item['question_type']!r}: "
            f"correct_answer={item['correct_answer']!r} does not match options {pool!r}. "
            f"Original error: {exc}"
        ) from exc
    question.save()
    return question


def sync_reading_quiz_content(
    quiz: Quiz,
    parsed: dict,
    *,
    replace_existing: bool = True,
) -> dict:
    if replace_existing:
        ReadingPassage.objects.filter(quiz=quiz).delete()

    passage_count = 0
    group_count = 0
    question_count = 0
    groups_by_order: dict[int, ReadingQuestionGroup] = {}

    for passage_data in parsed['passages']:
        passage = ReadingPassage.objects.create(
            quiz=quiz,
            order=passage_data['order'],
            title=passage_data['title'],
            instructions=passage_data['instructions'],
            body=passage_data['body'],
        )
        passage.full_clean()
        passage_count += 1

        for group_data in passage_data['question_groups']:
            group = ReadingQuestionGroup.objects.create(
                passage=passage,
                order=group_data['order'],
                title=group_data['title'],
                instructions=group_data['instructions'],
                question_type=group_data['question_type'],
                option_pool=group_data['option_pool'],
            )
            group.full_clean()
            groups_by_order[group_data['order']] = group
            group_count += 1

            for item in group_data['questions']:
                _create_question(passage, group=group, item=item)
                question_count += 1

        for item in passage_data['questions']:
            group = None
            group_order = item.get('group_order')
            if group_order is not None:
                group = groups_by_order.get(int(group_order))
                if group is None:
                    raise ValueError(
                        f'Unknown group_order {group_order} for question order {item["order"]}.',
                    )
                if item['question_type'] != group.question_type:
                    raise ValueError(
                        f'Question order {item["order"]} type must match group {group_order}.',
                    )
                if item['correct_answer'] not in group.pool_options:
                    raise ValueError(
                        f'Question order {item["order"]}: correct_answer must be in group pool.',
                    )
            _create_question(passage, group=group, item=item)
            question_count += 1

    return {
        'passages': passage_count,
        'groups': group_count,
        'questions': question_count,
    }


@transaction.atomic
def load_reading_resource_file(path: Path, *, replace_existing: bool = True) -> dict:
    from portals.utils.quiz_category_services import ensure_quiz_category

    parsed = parse_reading_resource_file(path)
    category, _ = ensure_quiz_category(parsed['service'], parsed['category_name'])

    defaults = {
        'topic': parsed['resource_name'],
        'is_reading': True,
        'is_listening': False,
        'is_essay': False,
        'is_speaking': False,
    }
    time_limit = parsed.get('time_limit_minutes')
    if time_limit:
        defaults['is_time_limited'] = True
        defaults['time_limit_minutes'] = int(time_limit)

    quiz, quiz_created = Quiz.objects.update_or_create(
        category=category,
        resource_slug=parsed['resource_slug'],
        defaults=defaults,
    )
    quiz.full_clean()
    quiz.save()

    content_stats = sync_reading_quiz_content(
        quiz,
        parsed,
        replace_existing=replace_existing,
    )

    return {
        'file': path.name,
        'category': str(category),
        'quiz_created': quiz_created,
        'quiz_id': quiz.pk,
        'quiz_topic': quiz.topic,
        **content_stats,
    }


def load_all_reading_resources(*, replace_existing: bool = True) -> list[dict]:
    if not RESOURCES_DIR.exists():
        return []

    results = []
    for path in sorted(RESOURCES_DIR.glob('*.json')):
        results.append(load_reading_resource_file(path, replace_existing=replace_existing))
    return results
