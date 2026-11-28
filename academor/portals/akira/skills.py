"""Skill tags for questions (domain + skill), read from the question resource files.

Questions loaded from JSON resources keep ``source_key = "<resource slug>:q<id>"``; the
resource item itself carries ``domain`` and ``skill``. This module maps one to the
other without a database column, so any course whose resources carry the two keys
gets per-skill analytics for free. Questions without tags fall into one bucket.
"""

from __future__ import annotations

import json
import logging
from functools import lru_cache
from pathlib import Path

logger = logging.getLogger(__name__)

RESOURCE_DIRS = (
    Path(__file__).resolve().parent.parent / 'resources' / 'sat_questions',
    Path(__file__).resolve().parent.parent / 'resources' / 'quiz_questions',
)


@lru_cache(maxsize=1)
def _skill_index() -> dict[str, tuple[str, str]]:
    index: dict[str, tuple[str, str]] = {}
    for folder in RESOURCE_DIRS:
        if not folder.is_dir():
            continue
        for path in sorted(folder.glob('*.json')):
            try:
                data = json.loads(path.read_text(encoding='utf-8'))
            except (OSError, ValueError):
                logger.warning('AKIRA: could not read %s', path)
                continue
            questions = data.get('questions') if isinstance(data, dict) else None
            for item in questions or []:
                if not isinstance(item, dict) or item.get('id') is None:
                    continue
                domain = str(item.get('domain') or '').strip()
                skill = str(item.get('skill') or '').strip()
                if domain or skill:
                    index[f'{path.stem}:q{item["id"]}'] = (domain, skill)
    return index


def question_skill(question) -> tuple[str, str]:
    """(domain, skill) for a question; empty strings when the question has no tags."""
    key = str(getattr(question, 'source_key', '') or '')
    if not key:
        return '', ''
    return _skill_index().get(key, ('', ''))
