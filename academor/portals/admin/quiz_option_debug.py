"""Deploy diagnostics for SAT/MCQ answer-option save failures."""

from __future__ import annotations

import json
import logging

from portals.admin.widgets import nonempty_options, option_has_text

logger = logging.getLogger('portals.admin.quiz_options')

CLIENT_DEBUG_FIELD = 'quiz_options_client_debug'


def _preview(value, limit=80):
    text = str(value if value is not None else '').replace('\n', ' ').replace('\r', ' ')
    if len(text) > limit:
        return f'{text[:limit]}…(len={len(text)})'
    return text


def _getlist(data, name):
    getter = getattr(data, 'getlist', None)
    if callable(getter):
        return list(getter(name))
    value = data.get(name) if data is not None else None
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _as_option_list(value):
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value or '[]')
        except json.JSONDecodeError:
            return [value] if value.strip() else []
        return parsed if isinstance(parsed, list) else []
    return []


def collect_field_snapshot(data, name):
    hidden_values = _getlist(data, name)
    hidden_filled = 0
    for value in hidden_values:
        hidden_filled = max(hidden_filled, len(nonempty_options(_as_option_list(value))))

    items = []
    for index in range(50):
        key = f'{name}_item_{index}'
        if data is None or key not in data:
            break
        items.append(data.get(key) or '')

    related_keys = []
    if data is not None:
        related_keys = sorted(
            str(key) for key in data.keys()
            if str(key) == name or str(key).startswith(f'{name}_')
        )

    return {
        'field': name,
        'related_keys': related_keys,
        'hidden_posted': name in (data or {}),
        'hidden_count': len(hidden_values),
        'hidden_filled': hidden_filled,
        'hidden_preview': [_preview(value) for value in hidden_values[:3]],
        'item_count': len(items),
        'item_filled': len(nonempty_options(items)),
        'items': [
            {
                'i': index,
                'len': len(str(value or '')),
                'has_text': option_has_text(value),
                'preview': _preview(value, 50),
            }
            for index, value in enumerate(items)
        ],
    }


def _parse_client_debug(data):
    raw = (data.get(CLIENT_DEBUG_FIELD) if data is not None else None) or ''
    if not raw:
        return None
    try:
        parsed = json.loads(raw)
    except (TypeError, json.JSONDecodeError):
        return {'parse_error': True, 'preview': _preview(raw, 120)}
    return parsed


def _form_error_map(form):
    errors = getattr(form, 'errors', None) or {}
    return {field: [str(err) for err in error_list] for field, error_list in errors.items()}


def log_quiz_options_post(request, *, source, object_id=None):
    """One line per Save click so we can see what the browser posted."""
    data = getattr(request, 'POST', None)
    if not data:
        return
    keys = [str(key) for key in data.keys()]
    option_keys = [
        key for key in keys
        if 'answer_option' in key or 'spr_correct' in key or key == CLIENT_DEBUG_FIELD
    ]
    field_names = []
    for key in option_keys:
        if key == CLIENT_DEBUG_FIELD:
            continue
        if '_item_' in key:
            field_names.append(key.split('_item_')[0])
        else:
            field_names.append(key)
    unique_fields = list(dict.fromkeys(field_names))
    payload = {
        'source': source,
        'path': getattr(request, 'path', ''),
        'object_id': object_id,
        'user': str(getattr(request, 'user', '')),
        'post_key_count': len(keys),
        'option_keys': option_keys,
        'fields': [collect_field_snapshot(data, name) for name in unique_fields[:20]],
        'client_debug': _parse_client_debug(data),
    }
    logger.warning('QUIZ_OPTIONS_SAVE_POST %s', json.dumps(payload, ensure_ascii=False, default=str))


def log_quiz_question_form_errors(form, *, source):
    """WARNING so gunicorn/docker logs show it with default LOGGING (root=WARNING)."""
    data = getattr(form, 'data', None)
    prefix = getattr(form, 'prefix', None) or ''
    add_prefix = getattr(form, 'add_prefix', lambda name: name)
    instance = getattr(form, 'instance', None)
    quiz = getattr(instance, 'quiz', None) if instance is not None else None

    payload = {
        'source': source,
        'prefix': prefix or None,
        'question_pk': getattr(instance, 'pk', None),
        'quiz_id': getattr(instance, 'quiz_id', None) or getattr(quiz, 'pk', None),
        'quiz_topic': getattr(quiz, 'topic', None),
        'sat_section': getattr(quiz, 'sat_section', None),
        'is_sat': getattr(quiz, 'is_sat', None),
        'question_type': (
            (form.cleaned_data or {}).get('question_type')
            if getattr(form, 'cleaned_data', None)
            else None
        ) or (data.get(add_prefix('question_type')) if data is not None else None),
        'empty_permitted': bool(getattr(form, 'empty_permitted', False)),
        'errors': _form_error_map(form),
        'answer_options': collect_field_snapshot(data, add_prefix('answer_options')),
        'spr_correct_answers': collect_field_snapshot(data, add_prefix('spr_correct_answers')),
        'client_debug': _parse_client_debug(data),
    }
    logger.warning('QUIZ_OPTIONS_SAVE_FAILED %s', json.dumps(payload, ensure_ascii=False, default=str))
