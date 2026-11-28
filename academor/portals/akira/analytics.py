"""The numbers behind every AKIRA report. Plain code, no AI.

Rule: every number a student, parent or teacher sees is computed here. The AI only
puts these facts into words, and it is never asked to count or estimate anything.
"""

from __future__ import annotations

from collections import OrderedDict

from portals.akira.courses import CourseProfile

CORRECT, WRONG, BLANK = 'correct', 'wrong', 'blank'
OTHER_DOMAIN = 'Other'
WEAK_PERCENT = 70
STRONG_PERCENT = 80
MIN_QUESTIONS_FOR_DOMAIN = 2


def percent(part: int, whole: int) -> int:
    return round(part * 100 / whole) if whole else 0


def build_item(number: int, status: str, domain: str = '', skill: str = '') -> dict:
    return {'number': int(number), 'status': status, 'domain': domain or OTHER_DOMAIN, 'skill': skill or ''}


def analyse_section(items: list[dict], course: CourseProfile, *, duration_sec: int | None = None,
                    scaled: str = '', label: str = '') -> dict:
    """Facts for one quiz / one test section.

    ``items`` are ``build_item`` dicts in question order.
    """
    total = len(items)
    correct = sum(1 for item in items if item['status'] == CORRECT)
    wrong_numbers = [item['number'] for item in items if item['status'] == WRONG]
    blank_numbers = [item['number'] for item in items if item['status'] == BLANK]

    domains: OrderedDict[str, dict] = OrderedDict()
    for name in course.domains:
        domains[name] = {'name': name, 'correct': 0, 'total': 0}
    skill_misses: dict[str, int] = {}
    for item in items:
        bucket = domains.setdefault(item['domain'], {'name': item['domain'], 'correct': 0, 'total': 0})
        bucket['total'] += 1
        if item['status'] == CORRECT:
            bucket['correct'] += 1
        elif item['skill']:
            skill_misses[item['skill']] = skill_misses.get(item['skill'], 0) + 1
    domain_rows = [
        {**row, 'percent': percent(row['correct'], row['total'])}
        for row in domains.values() if row['total']
    ]
    domain_rows.sort(key=lambda row: (row['percent'], -row['total']))
    countable = [row for row in domain_rows if row['total'] >= MIN_QUESTIONS_FOR_DOMAIN and row['name'] != OTHER_DOMAIN]
    weak = [row['name'] for row in countable if row['percent'] < WEAK_PERCENT][:2]
    strong = [row['name'] for row in reversed(countable) if row['percent'] >= STRONG_PERCENT][:2]
    weak_skills = [
        {'skill': name, 'missed': count}
        for name, count in sorted(skill_misses.items(), key=lambda pair: (-pair[1], pair[0]))[:3]
    ]

    # Time pressure: how many of the misses sit in the last third of the section.
    misses = wrong_numbers + blank_numbers
    last_third_start = total - total // 3 + 1 if total >= 6 else total + 1
    late_misses = sum(1 for number in misses if number >= last_third_start)

    facts = {
        'course': course.label,
        'label': label or course.label,
        'correct': correct,
        'wrong': len(wrong_numbers),
        'blank': len(blank_numbers),
        'total': total,
        'percent': percent(correct, total),
        'domains': domain_rows,
        'weak_domains': weak,
        'strong_domains': strong,
        'weak_skills': weak_skills,
        'wrong_numbers': wrong_numbers,
        'blank_numbers': blank_numbers,
        'late_misses': late_misses,
        'misses': len(misses),
    }
    if scaled:
        facts['scaled'] = scaled
        if course.section_scale_max:
            facts['scale_max'] = course.section_scale_max
    if duration_sec and total:
        facts['duration_min'] = round(duration_sec / 60)
        facts['sec_per_question'] = round(duration_sec / total)
        if course.target_sec_per_question:
            facts['target_sec_per_question'] = course.target_sec_per_question
    return facts


def time_pressure(facts: dict) -> bool:
    """Most misses at the end of the section: the student ran out of time, not of knowledge."""
    return facts.get('misses', 0) >= 3 and facts.get('late_misses', 0) * 2 >= facts['misses']


def headline(facts_list: list[dict]) -> dict:
    """Summary across sections (a public test has two SAT sections)."""
    correct = sum(f['correct'] for f in facts_list)
    total = sum(f['total'] for f in facts_list)
    weak = [name for f in facts_list for name in f['weak_domains']]
    strong = [name for f in facts_list for name in f['strong_domains']]
    return {
        'correct': correct,
        'total': total,
        'percent': percent(correct, total),
        'weak_domains': weak[:3],
        'strong_domains': strong[:3],
        'time_pressure': any(time_pressure(f) for f in facts_list),
    }
