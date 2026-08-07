"""SAT Student-Produced Response (SPR) validation utilities."""
from __future__ import annotations

import re
from html import unescape
from typing import Dict, List

from django.utils.html import strip_tags


def plain_spr_text(value: str) -> str:
    """Strip HTML (CKEditor) and unescape entities for comparison/storage display."""
    if value is None:
        return ''
    text = strip_tags(str(value))
    return unescape(text).strip()


def normalize_spr_answer(answer_str: str) -> float:
    """
    Normalize a numeric SPR answer to float for comparison.

    Accepts integers, decimals, and simple fractions (a/b).
    Raises ValueError if the value is not a numeric SPR answer.
    """
    cleaned = plain_spr_text(answer_str).replace(' ', '').strip()

    if not cleaned:
        raise ValueError('Answer cannot be empty')

    allowed_chars = set('0123456789.-/')
    if not set(cleaned) <= allowed_chars:
        raise ValueError(f'Invalid characters in answer: {answer_str}')

    if cleaned.count('-') > 1 or (cleaned.count('-') == 1 and not cleaned.startswith('-')):
        raise ValueError(f'Invalid number format: {answer_str}')
    if cleaned.count('.') > 1:
        raise ValueError(f'Invalid number format: {answer_str}')

    if '/' in cleaned:
        parts = cleaned.split('/')
        if len(parts) != 2:
            raise ValueError(f'Invalid fraction format: {answer_str}')
        try:
            numerator = float(parts[0])
            denominator = float(parts[1])
            if denominator == 0:
                raise ValueError('Denominator cannot be zero')
            return numerator / denominator
        except ValueError as exc:
            raise ValueError(f'Invalid fraction: {answer_str}') from exc

    try:
        return float(cleaned)
    except ValueError as exc:
        raise ValueError(f'Invalid number format: {answer_str}') from exc


def normalize_spr_text_answer(answer_str: str) -> str:
    """
    Normalize free-text / equation SPR answers for equality checks.

    Examples that match after normalization:
    - "y = -x + 19" and "y=-x+19"
    - "Y = -X + 19" and "y = -x + 19"
    """
    text = plain_spr_text(answer_str).lower()
    # Collapse whitespace so spacing variants still match.
    text = re.sub(r'\s+', '', text)
    return text


def is_numeric_spr_answer(answer_str: str) -> bool:
    try:
        normalize_spr_answer(answer_str)
        return True
    except ValueError:
        return False


def validate_spr_answer(
    student_answer: str,
    correct_answers: List[str],
    tolerance: float = 0.001,
) -> Dict:
    """
    Validate a student SPR answer against one or more correct answers.

    Matching rules (any correct answer may match):
    1. Numeric: compare floats within tolerance (supports "7/2" ≈ "3.5").
    2. Text/equation: compare normalized plain text (HTML stripped, case/spacing ignored).
    """
    answers = [a for a in (correct_answers or []) if plain_spr_text(str(a))]
    if not answers:
        return {
            'is_correct': False,
            'normalized_student_value': None,
            'error': 'No valid correct answers provided',
        }

    student_plain = plain_spr_text(student_answer)
    if not student_plain:
        return {
            'is_correct': False,
            'normalized_student_value': None,
            'error': 'Answer cannot be empty',
        }

    student_numeric = None
    try:
        student_numeric = normalize_spr_answer(student_plain)
    except ValueError:
        pass

    if student_numeric is not None:
        for answer in answers:
            try:
                correct_value = normalize_spr_answer(answer)
            except ValueError:
                continue
            if abs(student_numeric - correct_value) < tolerance:
                return {
                    'is_correct': True,
                    'normalized_student_value': student_numeric,
                    'error': None,
                }

    student_text = normalize_spr_text_answer(student_plain)
    for answer in answers:
        if student_text == normalize_spr_text_answer(answer):
            return {
                'is_correct': True,
                'normalized_student_value': student_text,
                'error': None,
            }

    return {
        'is_correct': False,
        'normalized_student_value': student_numeric if student_numeric is not None else student_text,
        'error': 'Answer does not match any correct answer',
    }


def validate_spr_length(answer: str, is_negative: bool) -> Dict:
    """Validate classic SAT grid-in length constraints (optional helper)."""
    max_length = 6 if is_negative else 5
    plain = plain_spr_text(answer)

    if len(plain) > max_length:
        return {
            'is_valid': False,
            'error': (
                f'Answer too long. Maximum {max_length} characters for '
                f'{"negative" if is_negative else "positive"} answers'
            ),
        }

    return {
        'is_valid': True,
        'error': None,
    }


def contains_mixed_number(answer: str) -> bool:
    """Detect mixed-number style answers (e.g. "3 1/2")."""
    plain = plain_spr_text(answer)
    if ' ' in plain.strip():
        # Only treat as mixed number when it looks numeric with a fraction.
        if re.search(r'\d\s+\d+/\d+', plain):
            return True

    cleaned = plain.replace(' ', '')
    if '/' in cleaned:
        parts = cleaned.split('/')
        if len(parts) == 2:
            try:
                numerator = int(parts[0])
                denominator = int(parts[1])
                if numerator > 10 and denominator < 10:
                    return True
            except ValueError:
                pass

    return False


def validate_spr_format(answer: str) -> Dict:
    """
    Optional format check for classic numeric SAT SPR answers.

    Free-text / equation answers are considered valid here; length limits
    are enforced only when the answer is purely numeric.
    """
    plain = plain_spr_text(answer)
    if not plain:
        return {'is_valid': False, 'error': 'Answer cannot be empty'}

    if contains_mixed_number(plain):
        return {
            'is_valid': False,
            'error': 'Mixed numbers not allowed. Use improper fraction (e.g., 7/2) or decimal (e.g., 3.5)',
        }

    if is_numeric_spr_answer(plain):
        is_negative = plain.lstrip().startswith('-')
        length_check = validate_spr_length(plain, is_negative)
        if not length_check['is_valid']:
            return length_check

    return {
        'is_valid': True,
        'error': None,
    }
