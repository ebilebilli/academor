"""Build SAT Math/Verbal JSON from Word HTML export + answer keys.

Embeds equation/chart images as data-URI <img> tags so CKEditor admin
stores self-contained HTML.
"""
from __future__ import annotations

import base64
import json
import mimetypes
import re
from html import unescape
from pathlib import Path

from lxml import etree
from lxml import html as lh

ROOT = Path(r'c:\Users\user\Desktop\Academor')
EXPORT = ROOT / '_sat_html_export'
OUT_DIR = ROOT / 'academor' / 'portals' / 'resources' / 'sat_questions'
MEDIA_DIR = OUT_DIR / 'media'
REPORT = ROOT / 'sat_analysis_report.json'

MATH_NS = '{http://schemas.openxmlformats.org/officeDocument/2006/math}'


def _mime(path: Path) -> str:
    guess, _ = mimetypes.guess_type(str(path))
    return guess or 'application/octet-stream'


def data_uri(path: Path) -> str:
    raw = path.read_bytes()
    b64 = base64.b64encode(raw).decode('ascii')
    return f'data:{_mime(path)};base64,{b64}'


def clean_text(s: str) -> str:
    s = unescape(s or '')
    s = s.replace('\xa0', ' ').replace('\r', ' ').replace('\n', ' ')
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def paragraph_inner_html(p, files_dir: Path, copy_dir: Path) -> str:
    """Serialize a paragraph's inline content to CKEditor-friendly HTML."""
    parts: list[str] = []
    for node in p.xpath('.//node()'):
        if isinstance(node, etree._Element):
            tag = etree.QName(node).localname.lower()
            if tag == 'img':
                src = node.get('src') or ''
                name = Path(src.replace('\\', '/')).name
                src_path = files_dir / name
                if not src_path.exists():
                    continue
                copy_dir.mkdir(parents=True, exist_ok=True)
                dest = copy_dir / name
                if not dest.exists():
                    dest.write_bytes(src_path.read_bytes())
                width = node.get('width')
                height = node.get('height')
                style_bits = []
                if width:
                    style_bits.append(f'max-width:{width}px')
                if height and int(height or 0) > 40:
                    style_bits.append(f'height:auto')
                # Large figures: keep readable size in editor
                if height and int(height) >= 80:
                    style_bits = ['max-width:100%', 'height:auto']
                style = ';'.join(style_bits)
                uri = data_uri(src_path)
                alt = name
                img = f'<img src="{uri}" alt="{alt}"'
                if style:
                    img += f' style="{style}"'
                if width and int(height or 0) < 80:
                    img += f' width="{width}"'
                    if height:
                        img += f' height="{height}"'
                img += '>'
                parts.append(img)
            elif tag in {'br'}:
                parts.append('<br>')
        elif isinstance(node, str):
            # Only direct text nodes that aren't nested deeper than we already walk
            pass

    # Prefer mixed content walk via xpath string + imgs in order
    # Rebuild from children recursively for better fidelity
    return _serialize_inline(p, files_dir, copy_dir)


def _serialize_inline(el, files_dir: Path, copy_dir: Path) -> str:
    chunks: list[str] = []
    if el.text:
        chunks.append(el.text)
    for child in el:
        tag = etree.QName(child).localname.lower()
        if tag == 'img':
            src = child.get('src') or ''
            name = Path(src.replace('\\', '/')).name
            src_path = files_dir / name
            if src_path.exists():
                copy_dir.mkdir(parents=True, exist_ok=True)
                dest = copy_dir / name
                if not dest.exists():
                    dest.write_bytes(src_path.read_bytes())
                width = child.get('width')
                height = child.get('height')
                h = int(height or 0)
                w = int(width or 0)
                uri = data_uri(src_path)
                if h >= 80 or w >= 200:
                    chunks.append(
                        f'<img src="{uri}" alt="{name}" style="max-width:100%;height:auto;">'
                    )
                else:
                    attrs = f'src="{uri}" alt="{name}"'
                    if width:
                        attrs += f' width="{width}"'
                    if height:
                        attrs += f' height="{height}"'
                    chunks.append(f'<img {attrs}>')
        elif tag in {'br'}:
            chunks.append('<br>')
        elif tag in {'span', 'b', 'strong', 'i', 'em', 'u', 'a', 'sub', 'sup'}:
            inner = _serialize_inline(child, files_dir, copy_dir)
            if tag in {'b', 'strong'} and inner.strip():
                chunks.append(f'<strong>{inner}</strong>')
            else:
                chunks.append(inner)
        else:
            chunks.append(_serialize_inline(child, files_dir, copy_dir))
        if child.tail:
            chunks.append(child.tail)
    html = ''.join(chunks)
    html = html.replace('\xa0', ' ').replace('\r', ' ').replace('\n', ' ')
    html = re.sub(r'[ \t]{2,}', ' ', html)
    return html.strip()


def split_questions(paras, header_re: re.Pattern):
    """Return list of {number, start, end, header_rest_html_source_para}."""
    headers = []
    for i, p in enumerate(paras):
        text = clean_text(''.join(p.itertext()))
        m = header_re.match(text)
        if m:
            headers.append((i, int(m.group(1)), m.group(2) if m.lastindex and m.lastindex >= 2 else ''))
    blocks = []
    for idx, (i, num, rest) in enumerate(headers):
        end = headers[idx + 1][0] if idx + 1 < len(headers) else len(paras)
        blocks.append({'number': num, 'start': i, 'end': end, 'header_rest': rest})
    return blocks


def match_option_line(text: str) -> tuple[str, str] | None:
    """Return (letter, remainder) for option lines like 'A', 'A.', 'A. text'."""
    t = clean_text(text)
    # Preferred: "A. text" / "A) text"
    m = re.match(r'^([A-D])[.)]\s*(.*)$', t, re.I | re.S)
    if m:
        return m.group(1).upper(), clean_text(m.group(2))
    # Exact letter only (image options on same/next paragraph)
    m = re.fullmatch(r'([A-D])\.?', t, re.I)
    if m:
        return m.group(1).upper(), ''
    # "A 12" / "A 8√2 + √80" (letter + short answer, no period)
    m = re.match(r'^([A-D])\s+(.+)$', t, re.I | re.S)
    if m:
        rest = clean_text(m.group(2))
        # Avoid treating stem sentences like "A right triangle..." as options.
        if len(rest) <= 100 and not re.match(
            r'^(right|social|moving|proposal|fish|line|point|function|expression|'
            r'triangle|student|researcher|in\b|the\b|for\b|which\b|what\b|how\b|'
            r'an\b|to\b|based\b)',
            rest,
            re.I,
        ):
            return m.group(1).upper(), rest
    return None


def parse_question_block(paras, start: int, end: int, files_dir: Path, copy_dir: Path) -> dict:
    """Parse one question's paragraphs into stem HTML + options."""
    stem_parts: list[str] = []
    header_p = paras[start]
    header_plain = clean_text(''.join(header_p.itertext()))
    header_has_img = bool(header_p.xpath('.//img'))
    # Always keep header body when it has more than the number, or when it embeds media.
    if header_has_img or not re.fullmatch(r'(?:Question\s+)?\d+[.)]\s*', header_plain, re.I):
        stem_parts.append(_stem_from_header(header_p, files_dir, copy_dir))

    options: dict[str, str] = {}
    current_opt: str | None = None
    opt_parts: list[str] = []

    def flush_opt():
        nonlocal current_opt, opt_parts
        if current_opt:
            content = ' '.join(p for p in opt_parts if p).strip()
            options[current_opt] = content
        current_opt = None
        opt_parts = []

    for p in paras[start + 1 : end]:
        text = clean_text(''.join(p.itertext()))
        opt_match = match_option_line(text)
        html = _serialize_inline(p, files_dir, copy_dir)

        if opt_match:
            letter, remainder = opt_match
            flush_opt()
            current_opt = letter
            # Same-paragraph content: strip leading letter from serialized HTML
            same = re.sub(
                r'^((?:<[^>]+>)*)\s*[A-D][.)]?\s*',
                r'\1',
                html,
                count=1,
                flags=re.I,
            ).strip()
            if remainder and '<img' not in same:
                # Prefer remainder text when no image on this line
                same = remainder if not same or clean_text(re.sub(r'<[^>]+>', '', same)) == remainder else same
            if same and (clean_text(re.sub(r'<[^>]+>', '', same)) or '<img' in same):
                opt_parts.append(same)
            continue

        if not html:
            continue
        plain = clean_text(re.sub(r'<[^>]+>', '', html))
        if not plain and '<img' not in html:
            continue
        if current_opt:
            opt_parts.append(html)
        else:
            stem_parts.append(html)

    flush_opt()

    stem = '<br>'.join(p for p in stem_parts if p)
    stem = re.sub(r'(?:<br>\s*){3,}', '<br><br>', stem).strip()
    if stem and not stem.startswith('<'):
        stem = f'<p>{stem}</p>'
    elif stem and '<img' in stem and not stem.startswith('<p'):
        stem = f'<p>{stem}</p>'

    return {
        'stem_html': stem,
        'options': options,
    }


def _stem_from_header(p, files_dir: Path, copy_dir: Path) -> str:
    """Serialize header paragraph but drop the leading question number."""
    html = _serialize_inline(p, files_dir, copy_dir)
    html = re.sub(
        r'^((?:<[^>]+>)*)(?:Question\s+)?\d+[.)]\s*',
        r'\1',
        html,
        count=1,
        flags=re.I,
    )
    return html.strip()


# Corrupted answer-key cells (MathML garbage). Values verified against question content /
# prior curated JSON where the key XML was unusable.
SPR_OVERRIDES = {
    7: ['4', '4.0'],           # a in (4x^2 ...)(…) factorization
    26: ['7/20', '0.35', '.35'],  # P(red tile)
    33: ['8', '8.0'],          # right triangle leg
}

MCQ_OVERRIDES = {
    44: 'C',  # 9x=54 => 12x=72; last MCQ missing from 43-row key table
}


def load_math_answers() -> list[str]:
    """Return 43 answer strings in table order (OMML-aware)."""
    from docx import Document

    doc = Document(r'c:\Users\user\Desktop\SAT Mock\One\SAT_Math_One_Answer_Keys.docx')
    answers = []
    for row in doc.tables[0].rows:
        cell = row.cells[2]
        text = cell.text.strip()
        ommls = [''.join(om.itertext()) for om in cell._tc.iter(MATH_NS + 'oMath')]
        if ommls and ommls[0] and not ommls[0].startswith('<'):
            ans = ommls[0].strip()
        elif text in 'ABCD':
            ans = text
        else:
            # recover corrupted fraction cells like 3618" > / <mathxmlns=
            compact = re.sub(r'[^0-9A-Da-d./or\-]', '', text)
            if re.fullmatch(r'\d{3,4}', compact):
                # 3618 -> 36/18, 310 -> 3/10, 1517 -> 15/17
                if len(compact) == 4:
                    ans = f'{compact[:2]}/{compact[2:]}'
                elif len(compact) == 3:
                    ans = f'{compact[0]}/{compact[1:]}'
                else:
                    ans = compact
            elif compact:
                ans = compact
            else:
                ans = ''
        # normalize 15or-5
        ans = ans.replace(' ', '')
        if re.match(r'^\d+or-?\d+$', ans, re.I):
            ans = re.sub(r'or', ' or ', ans, flags=re.I)
        answers.append(ans)
    return answers


def load_verbal_answers() -> dict[str, str]:
    report = json.loads(REPORT.read_text(encoding='utf-8'))
    return report['verbal']['answer_map']


def spr_variants(answer: str) -> list[str]:
    ans = clean_text(answer)
    variants = [ans]
    compact = ans.replace(' ', '')
    if compact != ans:
        variants.append(compact)
    # 15 or -5
    m = re.match(r'^(-?\d+)\s*or\s*(-?\d+)$', ans, re.I)
    if m:
        a, b = m.group(1), m.group(2)
        variants.extend([a, b, f'{a} or {b}', f'{a}or{b}', f'{b} or {a}'])
    # fraction
    if '/' in compact:
        variants.append(compact)
        try:
            num, den = compact.split('/', 1)
            val = float(num) / float(den)
            if val == int(val):
                variants.append(str(int(val)))
            else:
                # common decimal forms
                variants.append(f'{val:.10g}')
        except Exception:
            pass
    # unique preserve order
    seen = set()
    out = []
    for v in variants:
        if v and v not in seen:
            seen.add(v)
            out.append(v)
    return out


def build_math():
    html_path = EXPORT / 'SAT_Math_One.html'
    files_dir = EXPORT / 'SAT_Math_One_files'
    copy_dir = MEDIA_DIR / 'math_one'
    raw = html_path.read_bytes()
    root = lh.fromstring(raw)
    paras = root.xpath('//p')
    blocks = split_questions(paras, re.compile(r'^(\d+)\)\s*(.*)$', re.S))

    answers = load_math_answers()
    letter_answers = [a for a in answers if len(a) == 1 and a in 'ABCD']
    spr_answers = [a for a in answers if not (len(a) == 1 and a in 'ABCD')]
    letter_i = 0
    spr_i = 0

    questions = []
    for bi, block in enumerate(blocks):
        global_id = bi + 1
        module = 1 if bi < 22 else 2
        parsed = parse_question_block(paras, block['start'], block['end'], files_dir, copy_dir)
        options = parsed['options']
        stem = parsed['stem_html']
        ordered = [options[k] for k in 'ABCD' if k in options]
        is_mcq = len(ordered) >= 2

        item = {
            'id': global_id,
            'module': module,
            'module_question': block['number'],
            'question': stem,
        }

        if is_mcq:
            item['options'] = ordered
            key_ans = ''
            if global_id in MCQ_OVERRIDES:
                key_ans = MCQ_OVERRIDES[global_id]
            elif letter_i < len(letter_answers):
                key_ans = letter_answers[letter_i]
                letter_i += 1
            if len(key_ans) == 1 and key_ans in options and options[key_ans]:
                item['correct'] = options[key_ans]
            elif len(key_ans) == 1 and key_ans in 'ABCD':
                idx = ord(key_ans) - ord('A')
                item['correct'] = ordered[idx] if 0 <= idx < len(ordered) else ''
                if not item['correct']:
                    item['_key_mismatch'] = key_ans
            else:
                item['correct'] = ''
                item['_missing_key'] = True
            item['answer_key'] = (
                f'<p><strong>Correct Answer: {key_ans}</strong></p>'
                if key_ans
                else '<p><strong>Correct Answer: TBD</strong></p>'
            )
        else:
            item['question_type'] = 'spr'
            if global_id in SPR_OVERRIDES:
                variants = list(SPR_OVERRIDES[global_id])
                key_ans = variants[0]
                # still consume corrupted stream slot so later SPR stay aligned
                if spr_i < len(spr_answers):
                    spr_i += 1
            else:
                key_ans = ''
                if spr_i < len(spr_answers):
                    key_ans = spr_answers[spr_i]
                    spr_i += 1
                variants = spr_variants(key_ans) if key_ans else []
            item['spr_correct_answers'] = variants or ([] if not key_ans else [key_ans])
            if not item['spr_correct_answers']:
                item['_missing_key'] = True
            maxlen = max((len(v) for v in item['spr_correct_answers']), default=5)
            item['spr_max_length'] = max(maxlen, 5)
            item['answer_key'] = (
                f'<p><strong>Correct Answer: {key_ans}</strong></p>'
                if key_ans
                else '<p><strong>Correct Answer: TBD</strong></p>'
            )

        questions.append(item)

    return {
        'title': 'SAT Math One',
        'category_name': 'SAT Math',
        'service': 'sat',
        'is_sat': True,
        'sat_section': 'algebra',
        'time_limit_minutes': 70,
        'questions': questions,
        '_answer_stream': {
            'letters': letter_answers,
            'spr': spr_answers,
            'letters_used': letter_i,
            'spr_used': spr_i,
        },
    }


def build_verbal():
    html_path = EXPORT / 'SAT_Verbal_One.html'
    files_dir = EXPORT / 'SAT_Verbal_One_files'
    copy_dir = MEDIA_DIR / 'verbal_one'
    raw = html_path.read_bytes()
    root = lh.fromstring(raw)
    paras = root.xpath('//p')
    blocks = split_questions(paras, re.compile(r'^Question\s+(\d+)\.?\s*(.*)$', re.I | re.S))
    answer_map = load_verbal_answers()

    questions = []
    for bi, block in enumerate(blocks):
        module = 1 if bi < 27 else 2
        key = f'M{module}-Q{block["number"]}'
        parsed = parse_question_block(paras, block['start'], block['end'], files_dir, copy_dir)
        options = parsed['options']
        ordered = [options[k] for k in 'ABCD' if k in options]
        letter = answer_map.get(key, '')
        correct = ''
        if len(letter) == 1 and letter in options:
            correct = options[letter]
        elif len(letter) == 1 and letter in 'ABCD' and ordered:
            idx = ord(letter) - ord('A')
            if 0 <= idx < len(ordered):
                correct = ordered[idx]

        questions.append({
            'id': bi + 1,
            'module': module,
            'module_question': block['number'],
            'question': parsed['stem_html'],
            'options': ordered,
            'correct': correct,
            'answer_key': f'<p><strong>Correct Answer: {letter}</strong></p>' if letter else '',
        })
    return {
        'title': 'SAT Verbal One',
        'category_name': 'SAT Verbal',
        'service': 'sat',
        'is_sat': True,
        'sat_section': 'reading',
        'time_limit_minutes': 64,
        'questions': questions,
    }


def validate(payload: dict, name: str) -> list[str]:
    issues = []
    for q in payload['questions']:
        qid = q['id']
        if not (q.get('question') or '').strip():
            issues.append(f'{name} Q{qid}: empty stem')
        if q.get('question_type') == 'spr':
            if not q.get('spr_correct_answers'):
                issues.append(f'{name} Q{qid}: SPR missing answers')
        else:
            opts = q.get('options') or []
            if len(opts) < 2:
                issues.append(f'{name} Q{qid}: MCQ needs options (got {len(opts)})')
            correct = q.get('correct') or ''
            if not correct:
                issues.append(f'{name} Q{qid}: missing correct (key={q.get("_key_mismatch") or q.get("_missing_key")})')
            elif correct not in opts:
                issues.append(f'{name} Q{qid}: correct not in options')
        if '<img' in (q.get('question') or ''):
            pass  # media present
    return issues


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    math = build_math()
    stream = math.pop('_answer_stream', {})
    verbal = build_verbal()

    # Strip internal flags from output but keep report
    math_issues = validate(math, 'math')
    verbal_issues = validate(verbal, 'verbal')

    def scrub(qs):
        for q in qs:
            q.pop('_key_mismatch', None)
            q.pop('_missing_key', None)
            q.pop('module', None)
            q.pop('module_question', None)

    meta = {
        'math_count': len(math['questions']),
        'verbal_count': len(verbal['questions']),
        'math_spr': sum(1 for q in math['questions'] if q.get('question_type') == 'spr'),
        'math_mcq': sum(1 for q in math['questions'] if q.get('question_type') != 'spr'),
        'math_with_img': sum(
            1
            for q in math['questions']
            if '<img' in (q.get('question') or '')
            or any('<img' in o for o in (q.get('options') or []))
        ),
        'verbal_with_img': sum(1 for q in verbal['questions'] if '<img' in (q.get('question') or '')),
        'answer_stream': stream,
        'math_issues': math_issues,
        'verbal_issues': verbal_issues,
        'math_types': [
            {
                'id': q['id'],
                'type': q.get('question_type', 'mcq'),
                'key_mismatch': q.get('_key_mismatch'),
                'missing_key': q.get('_missing_key'),
                'opts': len(q.get('options') or []),
                'has_img': ('<img' in (q.get('question') or ''))
                or any('<img' in o for o in (q.get('options') or [])),
                'correct_preview': (q.get('correct') or (q.get('spr_correct_answers') or [''])[0])[:80],
            }
            for q in math['questions']
        ],
    }
    (ROOT / '_sat_build_meta.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')

    scrub(math['questions'])
    scrub(verbal['questions'])

    (OUT_DIR / 'sat_math_one.json').write_text(
        json.dumps(math, ensure_ascii=False, indent=2), encoding='utf-8'
    )
    (OUT_DIR / 'sat_verbal_one.json').write_text(
        json.dumps(verbal, ensure_ascii=False, indent=2), encoding='utf-8'
    )
    print('Wrote', OUT_DIR / 'sat_math_one.json')
    print('Wrote', OUT_DIR / 'sat_verbal_one.json')
    print('Meta', ROOT / '_sat_build_meta.json')
    print('math', meta['math_count'], 'SPR', meta['math_spr'], 'MCQ', meta['math_mcq'], 'img', meta['math_with_img'])
    print('verbal', meta['verbal_count'], 'img', meta['verbal_with_img'])
    print('issues math', len(math_issues), 'verbal', len(verbal_issues))


if __name__ == '__main__':
    main()
