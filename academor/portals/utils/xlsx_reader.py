"""Read cell values from an .xlsx file with the standard library only (no openpyxl dependency).

Formulas come back as the value Excel saved last time; dates come back as Excel serial numbers
(see `excel_date`), because telling dates from numbers needs the style table, which the CRM
importer does not need — it knows which columns hold dates.
"""

from __future__ import annotations

import posixpath
import re
import zipfile
from datetime import date, datetime, time, timedelta
from xml.etree import ElementTree as ET

NS = {
    'm': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'rel': 'http://schemas.openxmlformats.org/package/2006/relationships',
}
_REF = re.compile(r'([A-Z]+)(\d+)')
EXCEL_EPOCH = date(1899, 12, 30)


def _col_index(letters: str) -> int:
    n = 0
    for ch in letters:
        n = n * 26 + (ord(ch) - 64)
    return n - 1


def _text(el) -> str:
    return ''.join(t.text or '' for t in el.iter(f"{{{NS['m']}}}t"))


class Workbook:
    def __init__(self, path):
        self.zip = zipfile.ZipFile(path)
        self.shared = []
        if 'xl/sharedStrings.xml' in self.zip.namelist():
            root = ET.fromstring(self.zip.read('xl/sharedStrings.xml'))
            self.shared = [_text(si) for si in root.findall('m:si', NS)]
        wb = ET.fromstring(self.zip.read('xl/workbook.xml'))
        rels = ET.fromstring(self.zip.read('xl/_rels/workbook.xml.rels'))
        targets = {r.get('Id'): r.get('Target') for r in rels.findall('rel:Relationship', NS)}
        self.sheets = {}
        for sh in wb.find('m:sheets', NS):
            target = targets.get(sh.get(f"{{{NS['r']}}}id"), '')
            if target.startswith('/'):
                path_in_zip = target.lstrip('/')
            else:
                path_in_zip = posixpath.normpath(posixpath.join('xl', target))
            self.sheets[sh.get('name')] = path_in_zip

    def sheet_names(self):
        return list(self.sheets)

    def find_sheet(self, *needles):
        """First sheet whose name contains any of the needles (case-insensitive, emoji ignored)."""
        for name in self.sheets:
            low = name.lower()
            if any(n.lower() in low for n in needles):
                return name
        return None

    def rows(self, sheet_name):
        """Yield each row as a list of values (str / float / None), padded to the row's width."""
        root = ET.fromstring(self.zip.read(self.sheets[sheet_name]))
        data = root.find('m:sheetData', NS)
        if data is None:
            return
        for row in data.findall('m:row', NS):
            values = {}
            for c in row.findall('m:c', NS):
                m = _REF.match(c.get('r') or '')
                if not m:
                    continue
                idx = _col_index(m.group(1))
                kind = c.get('t')
                v = c.find('m:v', NS)
                if kind == 's' and v is not None:
                    values[idx] = self.shared[int(v.text)]
                elif kind == 'inlineStr':
                    is_ = c.find('m:is', NS)
                    values[idx] = _text(is_) if is_ is not None else ''
                elif kind in ('str', 'e'):
                    values[idx] = v.text if v is not None else None
                elif kind == 'b':
                    values[idx] = bool(int(v.text)) if v is not None else None
                elif v is not None and v.text is not None:
                    try:
                        num = float(v.text)
                        values[idx] = int(num) if num.is_integer() else num
                    except ValueError:
                        values[idx] = v.text
            if values:
                yield [values.get(i) for i in range(max(values) + 1)]

    def table(self, sheet_name, header_hint):
        """Rows as dicts, keyed by the first row that contains `header_hint`."""
        header = None
        for row in self.rows(sheet_name):
            cells = [str(v).strip() if v is not None else '' for v in row]
            if header is None:
                if header_hint in cells:
                    header = cells
                continue
            if not any(v not in (None, '') for v in row):
                continue
            yield {h: (row[i] if i < len(row) else None) for i, h in enumerate(header) if h}


def excel_date(value):
    """Serial number, datetime, or a 'dd.mm.yyyy' / 'yyyy-mm-dd' string → date (None if blank/unknown)."""
    if value in (None, ''):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, (int, float)):
        if value <= 0 or value > 2958465:
            return None
        return EXCEL_EPOCH + timedelta(days=int(value))
    text = str(value).strip()
    for fmt in ('%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S', '%d.%m.%y'):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def excel_time(value):
    """0.4583 (fraction of a day), '11:00', '11:00 - 12:30' → (start time, minutes or None)."""
    if value in (None, ''):
        return None, None
    if isinstance(value, (int, float)) and 0 <= value < 1:
        minutes = round(value * 24 * 60)
        return time(minutes // 60, minutes % 60), None
    found = re.findall(r'(\d{1,2})[:.](\d{2})', str(value))
    if not found:
        return None, None
    h, m = map(int, found[0])
    if h > 23 or m > 59:
        return None, None
    start = time(h, m)
    duration = None
    if len(found) > 1:
        h2, m2 = map(int, found[1])
        duration = (h2 * 60 + m2) - (h * 60 + m)
        if duration <= 0:
            duration = None
    return start, duration
