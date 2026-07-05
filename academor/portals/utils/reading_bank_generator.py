"""Build platform-compatible IELTS reading quiz JSON from topic data."""

from __future__ import annotations

import json
import re
from pathlib import Path

RESOURCES_DIR = (
    Path(__file__).resolve().parent.parent / 'resources' / 'reading_questions'
)

_ROMAN_HEADINGS = ('i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii')


def _heading_label(text: str) -> str:
    label = text.strip()
    while True:
        stripped = re.sub(r'^[ivx]+\.\s*', '', label, flags=re.IGNORECASE)
        stripped = re.sub(r'^[a-z]\.\s*', '', stripped, flags=re.IGNORECASE)
        if stripped == label:
            return label.strip()
        label = stripped


def _normalize_headings_pool(pool: list[str]) -> list[str]:
    labels = [_heading_label(item) for item in pool]
    return [
        f'{_ROMAN_HEADINGS[index]}. {labels[index]}'
        for index in range(len(labels))
    ]


def _resolve_heading_answer(answer: str, pool: list[str]) -> str:
    target = _heading_label(answer)
    for item in pool:
        if _heading_label(item) == target:
            return item
    raise ValueError(f'heading answer not in pool: {answer!r}')


def _p(text: str) -> str:
    return f'<p>{text}</p>'


def _word_count_html(html: str) -> int:
    text = re.sub(r'<[^>]+>', ' ', html)
    return len(text.split())


def _completion_config(item: dict) -> dict:
    limit = int(item.get('word_limit') or 1)
    labels = {
        1: 'ONE WORD ONLY',
        2: 'NO MORE THAN TWO WORDS',
        3: 'NO MORE THAN THREE WORDS',
    }
    cfg = {
        'word_limit': limit,
        'word_limit_label': labels.get(limit, f'NO MORE THAN {limit} WORDS'),
        'case_insensitive': True,
    }
    alts = item.get('alternatives') or []
    if alts:
        cfg['accept_alternatives'] = alts
    return cfg


def build_passage_body(title: str, paragraphs: dict[str, str]) -> str:
    parts = [_p(f'<strong>{title}</strong>')]
    for letter in sorted(paragraphs.keys()):
        parts.append(_p(f'<strong>{letter}</strong> {paragraphs[letter]}'))
    return ''.join(parts)


def build_quiz_json(topic: dict) -> dict:
    quiz_number = topic['quiz_number']
    title = topic['title']
    paragraphs = topic['paragraphs']
    para_letters = sorted(paragraphs.keys())
    body = build_passage_body(title, paragraphs)

    headings_pool = _normalize_headings_pool(list(topic['headings_pool']))
    matching_headings = [
        {
            **item,
            'correct': _resolve_heading_answer(item['correct'], headings_pool),
        }
        for item in topic['matching_headings']
    ]
    matching_info = topic['matching_info']

    info_pool = [f'Paragraph {letter}' for letter in para_letters]

    question_groups = [
        {
            'order': 1,
            'title': 'Questions 11–15',
            'instructions': (
                '<p>Choose the correct heading for paragraphs <strong>B–F</strong> '
                'from the list of headings below.</p>'
                '<p><em>Write the correct number, <strong>i–vii</strong>, '
                'in boxes 11–15 on your answer sheet.</em></p>'
            ),
            'question_type': 'matching_headings',
            'option_pool': headings_pool,
            'questions': [
                {
                    'order': 11 + index,
                    'question': _p(f'Paragraph {item["paragraph"]}'),
                    'correct_answer': item['correct'],
                }
                for index, item in enumerate(matching_headings)
            ],
        },
        {
            'order': 2,
            'title': 'Questions 16–20',
            'instructions': (
                '<p>Which paragraph contains the following information?</p>'
                '<p><em>Write the correct letter, <strong>A–G</strong>, '
                'in boxes 16–20 on your answer sheet.</em></p>'
            ),
            'question_type': 'matching_info',
            'option_pool': info_pool,
            'questions': [
                {
                    'order': 16 + index,
                    'question': _p(item['question']),
                    'correct_answer': f'Paragraph {item["paragraph"]}',
                }
                for index, item in enumerate(matching_info)
            ],
        },
    ]

    questions = []

    for index, item in enumerate(topic['tfng'], start=1):
        questions.append({
            'order': index,
            'question_type': 'tfng',
            'question': _p(item['question']),
            'correct_answer': item['answer'],
        })

    for index, item in enumerate(topic['ynng'], start=6):
        questions.append({
            'order': index,
            'question_type': 'ynng',
            'question': _p(item['question']),
            'correct_answer': item['answer'],
        })

    for index, item in enumerate(topic['sentence_completion'], start=21):
        questions.append({
            'order': index,
            'question_type': 'sentence_completion',
            'question': _p(item['question']),
            'correct_answer': item['answer'],
            'question_config': _completion_config(item),
        })

    for index, item in enumerate(topic['summary_completion'], start=25):
        questions.append({
            'order': index,
            'question_type': 'summary_completion',
            'question': _p(item['question']),
            'correct_answer': item['answer'],
            'question_config': _completion_config(item),
        })

    completion_type = topic.get('completion_type') or (
        'table_completion' if quiz_number % 2 == 0 else 'flowchart_completion'
    )
    for index, item in enumerate(topic['table_completion'], start=29):
        questions.append({
            'order': index,
            'question_type': completion_type,
            'question': _p(item['question']),
            'correct_answer': item['answer'],
            'question_config': _completion_config(item),
        })

    for index, item in enumerate(topic['mcq'], start=32):
        questions.append({
            'order': index,
            'question_type': 'mcq',
            'question': _p(item['question']),
            'answer_options': item['options'],
            'correct_answer': item['answer'],
        })

    for index, item in enumerate(topic['short_answer'], start=37):
        questions.append({
            'order': index,
            'question_type': 'short_answer',
            'question': _p(item['question']),
            'correct_answer': item['answer'],
            'question_config': _completion_config(item),
        })

    questions.sort(key=lambda q: q['order'])

    return {
        'title': f'IELTS Academic Reading — Practice Test {quiz_number}',
        'service': 'ielts',
        'category_name': 'Reading practice',
        'time_limit_minutes': 60,
        'passages': [
            {
                'order': 1,
                'title': 'Passage 1',
                'instructions': (
                    '<p><strong>Questions 1–40</strong></p>'
                    '<p>You should spend about 60 minutes on <strong>Questions 1–40</strong>, '
                    'which are based on the reading passage below.</p>'
                ),
                'body': body,
                'question_groups': question_groups,
                'questions': questions,
            },
        ],
    }


def validate_quiz(data: dict, *, quiz_number: int) -> list[str]:
    errors: list[str] = []
    passage = data['passages'][0]
    wc = _word_count_html(passage['body'])
    if wc < 600 or wc > 900:
        errors.append(f'quiz {quiz_number}: passage word count {wc} (need 600–900)')

    orders: list[int] = []
    for group in passage['question_groups']:
        orders.extend(q['order'] for q in group['questions'])
    orders.extend(q['order'] for q in passage['questions'])
    if len(orders) != 40:
        errors.append(f'quiz {quiz_number}: expected 40 questions, got {len(orders)}')
    if sorted(orders) != list(range(1, 41)):
        errors.append(f'quiz {quiz_number}: question orders must be 1–40')

    types = {q['question_type'] for q in passage['questions']}
    for group in passage['question_groups']:
        types.add(group['question_type'])
    required = {
        'mcq', 'tfng', 'ynng', 'matching_headings', 'matching_info',
        'sentence_completion', 'summary_completion', 'short_answer',
    }
    if not required.issubset(types):
        errors.append(f'quiz {quiz_number}: missing types {required - types}')
    if 'table_completion' not in types and 'flowchart_completion' not in types:
        errors.append(f'quiz {quiz_number}: missing table/flowchart completion')

    return errors


def write_quiz_file(topic: dict) -> Path:
    quiz_number = topic['quiz_number']
    data = build_quiz_json(topic)
    errors = validate_quiz(data, quiz_number=quiz_number)
    if errors:
        raise ValueError('; '.join(errors))

    path = RESOURCES_DIR / f'ielts_reading_test_{quiz_number}.json'
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + '\n',
        encoding='utf-8',
    )
    return path


def generate_all(topics: list[dict]) -> list[Path]:
    RESOURCES_DIR.mkdir(parents=True, exist_ok=True)
    paths = []
    for topic in topics:
        paths.append(write_quiz_file(topic))
    return paths
