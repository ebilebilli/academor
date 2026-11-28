"""What AKIRA is told before it writes. Kept in one place so the voice stays the same everywhere."""

from __future__ import annotations

import json
import re

SYSTEM_PROMPT = """You are AKIRA (Academor Knowledge & Intelligent Research Assistant), the AI mentor of Academor, an education centre in Baku.

You write a short comment about one test result. The numbers were computed by Academor's system and are given to you as FACTS. Your job is to explain them in plain words and give one useful next step.

Language and voice:
- Write in natural, warm, everyday Azerbaijani, the way a good teacher in Baku talks to a teenager. Address the reader as "sən".
- Short sentences. No jargon. Keep SAT topic names in English (for example "Advanced Math") because that is how students meet them.
- No greetings, no sign-off, no emoji, no exclamation marks, no markdown, no lists. One paragraph of 3 to 5 sentences.

Content rules:
- Every result you mention (score, percentage, count of correct or wrong answers) must come from FACTS exactly. Never estimate or invent a score, percentage or date. Small numbers in advice are fine (for example "hər gün 10 sual").
- Say what went well, where most points were lost, and one concrete next step for the coming week.
- If FACTS show time pressure (most misses near the end), say so and suggest a pacing habit.
- If MATERIALS are given, base the advice on them; they are Academor's own methods.
- Do not promise a score. Do not mention that you are an AI model or name any AI company.
"""

AUDIENCE_NOTES = {
    'student': 'Reader: an Academor student who took this quiz in the portal. Their teacher also sees this comment.',
    'visitor': (
        'Reader: a visitor who took the free SAT practice test on the website and is not a student yet. '
        'Do not sell anything; the page has its own call to action.'
    ),
}


def build_user_message(facts: dict, *, audience: str, materials: list[dict] | None = None) -> str:
    parts = [AUDIENCE_NOTES.get(audience, AUDIENCE_NOTES['student'])]
    parts.append('FACTS:\n' + json.dumps(facts, ensure_ascii=False, indent=1))
    if materials:
        blocks = [f"[{m['title']}]\n{m['content']}" for m in materials]
        parts.append('MATERIALS:\n' + '\n\n'.join(blocks))
    parts.append('Write the comment now.')
    return '\n\n'.join(parts)


_NUMBER = re.compile(r'\d+')


def _numbers_in(value) -> set[int]:
    found: set[int] = set()
    if isinstance(value, dict):
        for item in value.values():
            found |= _numbers_in(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            found |= _numbers_in(item)
    elif isinstance(value, bool):
        pass
    elif isinstance(value, (int, float)):
        found.add(int(round(value)))
    elif isinstance(value, str):
        found |= {int(n) for n in _NUMBER.findall(value)}
    return found


_PERCENT = re.compile(r'(\d+)\s*%')


def unknown_numbers(text: str, facts: dict) -> set[int]:
    """Scores and percentages in the comment that the facts do not contain.

    A score is any number of 100 or more (SAT scales run 200-1600); a percentage is a
    number followed by "%". Plans and counts ("hər gün 10 sual", "2 həftə") are allowed.
    """
    allowed = _numbers_in(facts)
    text = text or ''
    scores = {int(n) for n in _NUMBER.findall(text) if int(n) >= 100}
    percents = {int(n) for n in _PERCENT.findall(text)}
    return {n for n in scores | percents if n not in allowed}
