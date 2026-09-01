"""Parse Qrup_detallari.xlsx and generate portal import JSON + credentials."""

import json
import re
import secrets
import string
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

EXCEL = Path(r'c:\Users\user\Desktop\Achedmor Operations\Qrup_detallari.xlsx')
OUT_DIR = Path(__file__).resolve().parents[1] / 'academor' / 'portals' / 'data'

SUBJECT_MAP = {
    'General English': 'general-english',
    'Foundation IELTS': 'ielts',
    'English for Kids': 'english-for-kids',
    'Kids English': 'english-for-kids',
    'AP Economics': 'ap-economics',
    'GRE Math': 'gre-math',
    'GRE Verbal': 'gre-verbal',
    'IELTS': 'ielts',
    'Ielts': 'ielts',
    'SAT Verbal': 'sat-verbal',
    'CFA 1': 'cfa-1',
    'CFA-1': 'cfa-1',
}


def complex_password(role: str, index: int) -> str:
    alphabet = string.ascii_letters + string.digits
    suffix = ''.join(secrets.choice(alphabet) for _ in range(5))
    return f'AcD3mor!{role}{index:02d}#{suffix}'


def student_course_enrollment_slugs(subject='', course_slug=''):
    subject = clean(subject)
    slug = subject_to_slug(subject) if subject else normalize_import_slug(course_slug)
    subject_l = subject.lower()
    if slug == 'ielts' or 'ielts' in subject_l:
        return ['ielts-course', 'english-language-course']
    if slug:
        return [slug]
    return []


def normalize_import_slug(slug):
    slug = (slug or '').strip().lower()
    if slug in ('foundation-ielts', 'foundation_ielts'):
        return 'ielts'
    return slug


def clean(val):
    if pd.isna(val):
        return ''
    return str(val).strip()


def norm_phone(val):
    s = clean(val)
    if not s:
        return ''
    return re.sub(r'[^\d+]', '', s.replace(' ', '').replace('-', ''))


def norm_date(val):
    if pd.isna(val) or val == '':
        return None
    if isinstance(val, datetime):
        return val.strftime('%Y-%m-%d')
    s = str(val).strip()
    if not s or s.lower() == 'nan':
        return None
    try:
        return pd.to_datetime(val).strftime('%Y-%m-%d')
    except Exception:
        return None


def norm_group(name):
    s = clean(name).lower()
    return re.sub(r'\s+', ' ', s)


def subject_to_slug(subject):
    subject = clean(subject)
    if not subject:
        return ''
    return SUBJECT_MAP.get(subject, subject.lower().replace(' ', '-'))


def student_name_tokens(name):
    return [
        t.lower()
        for t in re.findall(r'[\w\u018f\u0259\u00e7\u015f\u0131\u011f\u00fc\u00f6]+', clean(name).lower())
        if len(t) > 2
    ]


def extract_paren_content(name):
    match = re.search(r'\(([^)]+)\)', clean(name))
    if not match:
        return []
    return [part.strip() for part in match.group(1).split(',') if part.strip()]


def name_parts(full_name):
    return [
        part.lower()
        for part in re.split(r'[\s(),]+', clean(full_name))
        if part
    ]


def resolve_student_label(label, students, group):
    label_parts = [part.lower() for part in re.split(r'[\s,]+', clean(label)) if part]
    if not label_parts:
        return None

    matches = []
    for student in students:
        parts = name_parts(student['full_name'])
        if any(label_part == part for label_part in label_parts for part in parts):
            matches.append(student)
            continue
        if len(label_parts) == 1 and len(label_parts[0]) > 4:
            label_norm = norm_group(label)
            name_norm = norm_group(student['full_name'])
            if label_norm in name_norm or name_norm in label_norm:
                matches.append(student)

    if not matches:
        return None
    if len(matches) == 1:
        return matches[0]['full_name']

    group_subject = group.get('course_slug') or subject_to_slug(group.get('subject', ''))
    for student in matches:
        if (
            student.get('teacher') == group.get('teacher')
            and subject_to_slug(student.get('subject', '')) == group_subject
        ):
            return student['full_name']

    return matches[0]['full_name']


def student_fits_group(student, group):
    group_subject = group.get('course_slug') or subject_to_slug(group.get('subject', ''))
    return (
        student.get('teacher') == group.get('teacher')
        and subject_to_slug(student.get('subject', '')) == group_subject
    )


def strip_student_names_from_group(name, student_names=()):
    """Remove parenthetical student lists and embedded student name tokens."""
    s = clean(name)
    s = re.sub(r'\s*\([^)]*\)', '', s)
    tokens_to_strip = set()
    for student in student_names:
        for token in student_name_tokens(student):
            if len(token) > 3:
                tokens_to_strip.add(token)
    for token in sorted(tokens_to_strip, key=len, reverse=True):
        s = re.sub(rf'(?<!\w){re.escape(token)}(?!\w)', '', s, flags=re.I)
    return re.sub(r'\s+', ' ', s).strip()


DAY_NAMES = (
    ('monday', 0),
    ('tuesday', 1),
    ('wednesday', 2),
    ('thursday', 3),
    ('friday', 4),
    ('saturday', 5),
    ('sunday', 6),
)


def is_ielts_subject(subject):
    subject_l = clean(subject).lower()
    return 'ielts' in subject_l


def group_course_slugs(subject, course_slug):
    slug = normalize_import_slug(course_slug)
    if is_ielts_subject(subject) or slug == 'ielts':
        return ['general-english', 'ielts']
    if slug:
        return [slug]
    return []


def weekday_from_text(text):
    token = clean(text).lower()
    for name, num in DAY_NAMES:
        if name in token:
            return num
    return None


def weekdays_from_text(text):
    """All weekday numbers mentioned in text (e.g. 'Monday, Wednesday')."""
    text = clean(text).lower().replace(' and ', ', ')
    found = []
    for part in re.split(r'[,;]', text):
        wd = weekday_from_text(part)
        if wd is not None:
            found.append(wd)
    return sorted(set(found))


def parse_weekdays(days_str):
    return weekdays_from_text(days_str)


def parse_time_range(text):
    times = re.findall(r'(\d{1,2})\s*:\s*(\d{2})', clean(text))
    if len(times) >= 2:
        sh, sm = int(times[0][0]), int(times[0][1])
        eh, em = int(times[1][0]), int(times[1][1])
        start_min = sh * 60 + sm
        end_min = eh * 60 + em
        duration = end_min - start_min if end_min > start_min else 90
        return f'{sh:02d}:{sm:02d}', duration
    if len(times) == 1:
        sh, sm = int(times[0][0]), int(times[0][1])
        return f'{sh:02d}:{sm:02d}', 90
    return None, None


DAY_PATTERN = r'(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)'
SCHEDULE_ENTRY = re.compile(
    rf'(({DAY_PATTERN}(?:\s*,\s*{DAY_PATTERN})*)\s*:?\s*'
    rf'(\d{{1,2}}\s*:\s*\d{{2}}(?:\s*-\s*\d{{1,2}}\s*:\s*\d{{2}})?))',
    re.I,
)


def parse_group_schedule(days_str, schedule_str):
    days_str = clean(days_str)
    schedule_str = clean(schedule_str)
    if not days_str and not schedule_str:
        return []

    slots = []
    if re.search(rf'{DAY_PATTERN}\b', schedule_str, re.I):
        for match in SCHEDULE_ENTRY.finditer(schedule_str):
            weekdays = weekdays_from_text(match.group(2))
            start, duration = parse_time_range(match.group(3))
            if start and weekdays:
                for wd in weekdays:
                    slots.append({'weekday': wd, 'start_time': start, 'duration_min': duration})
    else:
        start, duration = parse_time_range(schedule_str)
        weekdays = parse_weekdays(days_str)
        if start and weekdays:
            for wd in weekdays:
                slots.append({'weekday': wd, 'start_time': start, 'duration_min': duration})

    deduped = []
    seen = set()
    for slot in slots:
        key = (slot['weekday'], slot['start_time'])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(slot)
    return deduped


def match_group(student, groups):
    gn = norm_group(student.get('group_name', ''))
    if not gn:
        return ''

    best_name = ''
    best_score = 0
    for group in groups:
        gname = group['name']
        key = norm_group(gname)
        score = 0
        if gn == key:
            score = 1000
        elif gn in key or key in gn:
            score = min(len(gn), len(key)) + 10
        else:
            for token in gn.split():
                if len(token) > 3 and token in key:
                    score += len(token)
        if student_fits_group(student, group):
            score += 25
        if score > best_score:
            best_score = score
            best_name = gname
    if best_name:
        best_group = next(g for g in groups if g['name'] == best_name)
        if student_fits_group(student, best_group):
            return best_name
    return ''


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    students_df = pd.read_excel(EXCEL, sheet_name='Tələbə-Qrup', header=0)
    students_df.columns = [
        'no', 'full_name', 'phone', 'group_name', 'subject', 'teacher',
        'start_date', 'note', 'lessons', 'month', 'birthday', 'absence',
    ] + list(students_df.columns[12:])

    HEADER_NAMES = {'ad soyad', '№', 'telefon', 'qrup', 'fənn', 'müəllim', 'qeyd'}
    students = []
    seen_names = set()
    for _, row in students_df.iterrows():
        name = clean(row['full_name'])
        if not name or name.lower() in HEADER_NAMES:
            continue
        no_val = clean(row['no'])
        if no_val and not str(no_val).isdigit():
            continue
        if re.search(r'qerar verecek|gelecek', name, re.I):
            continue
        if name in seen_names:
            continue
        seen_names.add(name)
        students.append({
            'full_name': name,
            'phone': norm_phone(row['phone']),
            'group_name': clean(row['group_name']),
            'subject': clean(row['subject']),
            'teacher': clean(row['teacher']),
            'start_date': norm_date(row['start_date']),
            'note': clean(row['note']) or None,
        })

    groups_df = pd.read_excel(EXCEL, sheet_name='Qruplar', header=0)
    groups_df.columns = [
        'no', 'name', 'subject', 'teacher', 'days', 'schedule',
        'room', 'student_count', 'max_students',
    ] + list(groups_df.columns[9:])

    groups = []
    for _, row in groups_df.iterrows():
        name = clean(row['name'])
        if not name or name.lower() in {'qrup adı', 'qrup'}:
            continue
        no_val = clean(row['no'])
        if no_val and not str(no_val).isdigit():
            continue
        subject = clean(row['subject'])
        max_st = row['max_students']
        try:
            max_st = int(max_st) if not pd.isna(max_st) else 12
        except (ValueError, TypeError):
            max_st = 12
        groups.append({
            'name': name,
            'subject': subject,
            'course_slug': subject_to_slug(subject),
            'teacher': clean(row['teacher']),
            'max_students': max_st,
            'student_names': [],
            '_explicit_labels': extract_paren_content(name),
            '_days': clean(row['days']),
            '_schedule': clean(row['schedule']),
            '_room': clean(row['room']),
        })

    all_student_names = [s['full_name'] for s in students]
    assigned = {}
    for g in groups:
        raw_name = g['name']
        explicit_labels = g.pop('_explicit_labels', [])
        g['name'] = strip_student_names_from_group(raw_name, all_student_names)
        for label in explicit_labels:
            resolved = resolve_student_label(label, students, g)
            if resolved and resolved not in g['student_names']:
                g['student_names'].append(resolved)
                assigned[resolved] = g['name']

    for s in students:
        s['username'] = s['full_name']
        slug = subject_to_slug(s.get('subject', ''))
        s['course_slug'] = slug
        s['course_enrollments'] = student_course_enrollment_slugs(s.get('subject', ''), slug)
        if s['full_name'] in assigned:
            s['matched_group'] = assigned[s['full_name']]
        else:
            s['matched_group'] = match_group(s, groups)

    for i, s in enumerate(students, 1):
        s['password'] = complex_password('S', i)

    for s in students:
        if s['full_name'] in assigned:
            continue
        for g in groups:
            if g['name'] == s['matched_group'] and student_fits_group(s, g):
                g['student_names'].append(s['full_name'])
                assigned[s['full_name']] = g['name']
                break

    teachers_set = {}
    for g in groups:
        t = g['teacher']
        if t:
            teachers_set.setdefault(t, set()).add(g['course_slug'])
    for s in students:
        t = s['teacher']
        if t:
            slug = subject_to_slug(s['subject'])
            if slug:
                teachers_set.setdefault(t, set()).add(slug)

    SKIP_TEACHERS = {'müəllim'}
    teachers = []
    for i, (name, courses) in enumerate(
        sorted((n, c) for n, c in teachers_set.items() if n.lower() not in SKIP_TEACHERS),
        1,
    ):
        courses = sorted(normalize_import_slug(c) for c in courses if c and c != 'fənn')
        teachers.append({
            'full_name': name,
            'courses': courses,
            'username': name,
            'password': complex_password('T', i),
        })

    for g in groups:
        g['course_slug'] = normalize_import_slug(g.get('course_slug', ''))
        g['course_slugs'] = group_course_slugs(g.get('subject', ''), g['course_slug'])
        g['schedule'] = parse_group_schedule(g.pop('_days', ''), g.pop('_schedule', ''))
        room = g.pop('_room', '')
        if room:
            for slot in g['schedule']:
                slot['room_or_link'] = room

    payload = {
        'source': str(EXCEL.name),
        'generated_at': datetime.now().isoformat(),
        'teachers': teachers,
        'students': students,
        'groups': groups,
    }

    json_path = OUT_DIR / 'qrup_import.json'
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')

    lines = ['=== MÜƏLLİMLƏR ===', '']
    for t in teachers:
        lines.append(t['full_name'])
        lines.append(f"  İstifadəçi adı: {t['username']}")
        lines.append(f"  Parol: {t['password']}")
        lines.append(f"  Kurslar: {', '.join(t['courses'])}")
        lines.append('')

    lines += ['=== TƏLƏBƏLƏR ===', '']
    for s in students:
        lines.append(s['full_name'])
        lines.append(f"  İstifadəçi adı: {s['username']}")
        lines.append(f"  Parol: {s['password']}")
        lines.append(f"  Qrup: {s.get('matched_group') or s['group_name']}")
        lines.append(f"  Müəllim: {s['teacher']}")
        lines.append(f"  Kurslar: {', '.join(s.get('course_enrollments') or [])}")
        lines.append('')

    cred_path = OUT_DIR / 'qrup_import_credentials.txt'
    cred_path.write_text('\n'.join(lines), encoding='utf-8')

    cred_json = {
        'teachers': [
            {'full_name': t['full_name'], 'username': t['username'], 'password': t['password']}
            for t in teachers
        ],
        'students': [
            {
                'full_name': s['full_name'],
                'username': s['username'],
                'password': s['password'],
                'group': s.get('matched_group') or s['group_name'],
            }
            for s in students
        ],
    }
    (OUT_DIR / 'qrup_import_credentials.json').write_text(
        json.dumps(cred_json, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )

    print(f'Students: {len(students)}')
    print(f'Teachers: {len(teachers)}')
    print(f'Groups: {len(groups)}')
    print(f'JSON: {json_path}')
    print(f'Credentials: {cred_path}')
    for g in groups:
        print(f"  [{len(g['student_names'])}] {g['name'][:60]}")


if __name__ == '__main__':
    main()
