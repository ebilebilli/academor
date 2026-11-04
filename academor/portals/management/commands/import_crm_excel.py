"""Bring the office Excel books into the CRM.

    python manage.py import_crm_excel --students "Qrup Detallar.xlsx" --payments "ACADEMOR İdarəetmə Sistemi.xlsx"

Without --commit nothing is saved: the command only prints what it would do. Running it again
skips what is already there (same student + course + start, same payment date + amount + course).

* Qrup Detallar   → groups (Qruplar: teacher, capacity, lesson days/time), students and their
                    course registrations (Tələbələr: Aktiv/Gözləyir, Ayrılanlar: left with reason).
* İdarəetmə       → payments (💳 Ödənişlər) with method, teacher, teacher %, teacher share and
                    whether the teacher was paid. Each historical payment is booked against a
                    matching charge, so the past is settled and only new months create debt.

A course's monthly fee and teacher % come from the student's latest payment for that course, and
its billing day from that payment's "Növbəti Ödəniş" (next payment) date.
"""

from __future__ import annotations

import re
from collections import defaultdict
from decimal import Decimal, InvalidOperation

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from portals.crm_forms import unique_username
from portals.models import (
    Enrollment,
    Schedule,
    StudentCharge,
    StudentPayment,
    StudentProfile,
    StudyGroup,
    TeacherProfile,
)
from portals.utils.crm import month_label, month_start
from portals.utils.crm_leads import phone_key
from portals.utils.xlsx_reader import Workbook, excel_date, excel_time

User = get_user_model()
ZERO = Decimal('0')

METHODS = {'nağd': 'cash', 'kart': 'card', 'kart - up': 'card_up', 'kart-up': 'card_up', 'köçürmə': 'transfer'}
STATUSES = {'aktiv': 'active', 'gözləyir': 'waiting', 'ayrıldı': 'left', 'bitirdi': 'finished'}
TEACHER_PAID = {'bəli': 'paid', 'xeyr': 'pending', 'verilməyəcək': 'none'}
DAY_COLUMNS = ('Be', 'Ça', 'Ç ', 'Ca', 'C ', 'Ş', 'B ')


def norm(text) -> str:
    return re.sub(r'[^0-9a-zəğıöüşçİı]+', '', str(text or '').lower().replace('i̇', 'i'))


def clean_name(text) -> str:
    return ' '.join(str(text or '').split())


def money(value) -> Decimal:
    if value in (None, ''):
        return ZERO
    try:
        return Decimal(str(value).replace(',', '.').replace('₼', '').strip()).quantize(Decimal('0.01'))
    except (InvalidOperation, ValueError):
        return ZERO


def pick(row: dict, *prefixes):
    """Value of the first column whose header starts with one of the prefixes."""
    for p in prefixes:
        for k, v in row.items():
            if k.startswith(p):
                return v
    return None


def yes(value) -> bool:
    return str(value or '').strip().lower().startswith('bəli')


class Command(BaseCommand):
    help = 'Import students, groups, courses and payments from the office Excel books into the CRM.'

    def add_arguments(self, parser):
        parser.add_argument('--students', help='Qrup Detallar .xlsx (Tələbələr, Qruplar, Ayrılanlar)')
        parser.add_argument('--payments', help='İdarəetmə Sistemi .xlsx (💳 Ödənişlər)')
        parser.add_argument('--commit', action='store_true', help='Save. Without it this is a dry run.')

    def handle(self, *args, **opts):
        if not opts['students'] and not opts['payments']:
            raise CommandError('Give --students and/or --payments.')
        self.stats = defaultdict(int)
        self.warnings = []
        self._load_people()
        with transaction.atomic():
            payments = self._read_payments(opts['payments']) if opts['payments'] else []
            if opts['students']:
                book = Workbook(opts['students'])
                self._import_groups(book)
                self._import_enrollments(book, payments)
            if payments:
                self._import_payments(payments)
                self._import_unpaid()
            self._report(opts['commit'])
            if not opts['commit']:
                transaction.set_rollback(True)

    # ------------------------------------------------------------ people
    def _load_people(self):
        self.students_by_phone, self.students_by_name = defaultdict(list), defaultdict(list)
        for st in StudentProfile.objects.select_related('user'):
            self._remember(st, st.full_name, st.phone)
        self.teachers = {norm(t.full_name): t for t in TeacherProfile.objects.select_related('user')}
        self.groups = {norm(g.name): g for g in StudyGroup.objects.all()}

    def _remember(self, st, name, phone):
        if st not in self.students_by_name[norm(name)]:
            self.students_by_name[norm(name)].append(st)
        key = phone_key(phone or '')
        if key and st not in self.students_by_phone[key]:
            self.students_by_phone[key].append(st)

    @staticmethod
    def _names_match(a, b):
        """'Ali' ~ 'Ali Demo', 'Demo Ali' ~ 'Ali Demo'; siblings sharing a parent's phone do not match."""
        from difflib import SequenceMatcher

        ta, tb = set(norm(w) for w in a.split() if norm(w)), set(norm(w) for w in b.split() if norm(w))
        if not (ta and tb):
            return False
        if ta <= tb or tb <= ta:
            return True
        # a typo on the same phone: 'Ali Demoglu' ~ 'Ali Demooglu'
        return SequenceMatcher(None, ' '.join(sorted(ta)), ' '.join(sorted(tb))).ratio() >= 0.88

    def _find(self, name, phone):
        key = phone_key(phone or '')
        for st in self.students_by_name.get(norm(name), []):
            # the same name is the same person unless both have different phone numbers
            if not key or not phone_key(st.phone) or phone_key(st.phone) == key:
                return st
        if key:
            for st in self.students_by_phone.get(key, []):
                if self._names_match(name, st.full_name):
                    return st
        return None

    def student(self, name, phone, birth=None):
        name = clean_name(name)
        if not name:
            return None
        st = self._find(name, phone)
        if st is None:
            user = User(username=unique_username(name))
            user.set_unusable_password()
            user.save()
            st = StudentProfile.objects.create(user=user, phone=clean_name(phone), birth_date=birth)
            self.stats['students created'] += 1
        else:
            changed = []
            if phone and not st.phone:
                st.phone = clean_name(phone)
                changed.append('phone')
            if birth and not st.birth_date:
                st.birth_date = birth
                changed.append('birth_date')
            if changed:
                st.save(update_fields=changed)
        self._remember(st, name, phone)
        return st

    def teacher(self, name):
        name = clean_name(name)
        if not name or name in ('—', '-'):
            return None
        t = self.teachers.get(norm(name))
        if t is None:
            user = User(username=unique_username(name))
            user.set_unusable_password()
            user.save()
            t = TeacherProfile.objects.create(user=user)
            self.teachers[norm(name)] = t
            self.stats['teachers created'] += 1
        return t

    # ------------------------------------------------------------ groups
    def _import_groups(self, book):
        sheet = book.find_sheet('qruplar')
        if not sheet:
            self.warnings.append('"Qruplar" vərəqi tapılmadı.')
            return
        for row in book.table(sheet, 'Qrup Adı'):
            name = clean_name(row.get('Qrup Adı'))
            if not name:
                continue
            teacher = self.teacher(row.get('Müəllim'))
            g = self.groups.get(norm(name))
            if g is None:
                if not teacher:
                    self.warnings.append(f'Qrup "{name}": müəllim yoxdur, əlavə olunmadı.')
                    continue
                g = StudyGroup.objects.create(
                    name=name, teacher=teacher, max_students=int(money(row.get('Maks')) or 12),
                )
                self.groups[norm(name)] = g
                self.stats['groups created'] += 1
            start, duration = excel_time(row.get('Saat'))
            if not start:
                continue
            days = [i for i, prefix in enumerate(DAY_COLUMNS) if str(pick(row, prefix) or '').strip() == '✓']
            for day in days:
                if not g.schedules.filter(weekday=day, start_time=start).exists():
                    Schedule.objects.create(group=g, weekday=day, start_time=start, duration_min=duration or 90,
                                            effective_from=g.start_date or timezone.localdate())
                    self.stats['lesson slots created'] += 1

    # ------------------------------------------------------------ payments (read first: fees come from them)
    def _read_payments(self, path):
        book = Workbook(path)
        sheet = book.find_sheet('ödənişlər')
        sheets = [s for s in book.sheet_names() if 'ödənişlər' in s.lower() and 'müəllim' not in s.lower()]
        sheet = sheets[0] if sheets else sheet
        if not sheet:
            raise CommandError('"Ödənişlər" vərəqi tapılmadı.')
        rows = []
        self.unpaid = []
        for row in book.table(sheet, 'Ad Soyad'):
            name = clean_name(row.get('Ad Soyad'))
            paid_at = excel_date(row.get('Tarix'))
            amount = money(pick(row, 'Məbləğ'))
            if not name or not paid_at:
                continue
            status = clean_name(row.get('Status')).lower()
            if status == 'ödənilməyib':
                # money still to come: a debt, not a payment
                self.unpaid.append({'name': name, 'phone': row.get('Telefon'), 'due': paid_at, 'amount': amount,
                                    'course': clean_name(row.get('Kurs'))})
                continue
            if amount <= 0:
                self.stats['payments skipped (0 AZN)'] += 1
                continue
            pct = money(pick(row, 'Müəllim Faizi'))
            rows.append({
                'name': name, 'phone': row.get('Telefon'), 'paid_at': paid_at, 'amount': amount,
                'course': clean_name(row.get('Kurs')) or clean_name(pick(row, 'Fənn')),
                'method': METHODS.get(clean_name(pick(row, 'Ödəniş Üsulu')).lower(), 'cash'),
                'status': status, 'new': yes(pick(row, 'Yeni Müştəri')), 'teacher': row.get('Müəllim'),
                'pct': (pct * 100 if pct <= 1 else pct).quantize(Decimal('0.001')),
                'teacher_amount': money(pick(row, 'Müəllimə Gedən')),
                'teacher_paid': clean_name(pick(row, 'Müəllimə ödənilib')).lower().rstrip(' ✔'),
                'next_due': excel_date(pick(row, 'Növbəti Ödəniş')), 'note': clean_name(row.get('Qeyd')),
            })
        rows.sort(key=lambda r: r['paid_at'])
        return rows

    def _latest_payment(self, payments, student_name, phone, course):
        key, nm, course_n = phone_key(phone or ''), norm(student_name), norm(course)
        mine = [p for p in payments if norm(p['name']) == nm or (
            key and phone_key(p['phone'] or '') == key and self._names_match(p['name'], student_name))]
        same = [p for p in mine if self._same_course(p['course'], course_n)]
        return (same or mine or [None])[-1]

    @staticmethod
    def _next_due(last):
        """Billing continues from the "Növbəti Ödəniş" date, or a month after the last payment."""
        if not last:
            return None
        if last['next_due']:
            return last['next_due']
        return Enrollment(start_date=last['paid_at']).due_date_for(1)

    @staticmethod
    def _same_course(a, b_norm):
        a = norm(a)
        return bool(a and b_norm) and (a == b_norm or a.startswith(b_norm) or b_norm.startswith(a))

    # ------------------------------------------------------------ enrollments
    def _import_enrollments(self, book, payments):
        rows = []
        sheet = book.find_sheet('tələbələr')
        if sheet:
            for row in book.table(sheet, 'Ad Soyad'):
                rows.append({
                    'name': row.get('Ad Soyad'), 'phone': row.get('Telefon'), 'course': row.get('Fənn'),
                    'group': row.get('Qrup'), 'teacher': row.get('Müəllim'), 'start': excel_date(row.get('Başlama')),
                    'birth': excel_date(row.get('Doğum Tarixi')), 'note': clean_name(row.get('Qeyd')),
                    'status': STATUSES.get(clean_name(row.get('Status')).lower(), 'active'), 'ended': None, 'reason': '',
                })
        sheet = book.find_sheet('ayrılanlar')
        if sheet:
            for row in book.table(sheet, 'Ad Soyad'):
                rows.append({
                    'name': row.get('Ad Soyad'), 'phone': row.get('Telefon'), 'course': row.get('Fənn'),
                    'group': None, 'teacher': None, 'start': excel_date(row.get('Başladı')), 'birth': None, 'note': '',
                    'status': STATUSES.get(clean_name(row.get('Status')).lower(), 'left'),
                    'ended': excel_date(row.get('Ayrıldı')), 'reason': clean_name(row.get('Səbəb')),
                })
        self.enrollments_by_student = defaultdict(list)
        before, seen = set(), set()  # only what was in the CRM before this run counts as "already there"
        for e in Enrollment.objects.all():
            self.enrollments_by_student[e.student_id].append(e)
            before.add((e.student_id, norm(e.course), e.start_date))
        for r in rows:
            st = self.student(r['name'], r['phone'], r['birth'])
            course = clean_name(r['course'])
            if not st or not course:
                continue
            last = self._latest_payment(payments, r['name'], r['phone'], course)
            start = r['start'] or (last['paid_at'] if last else timezone.localdate())
            if (st.pk, norm(course), start) in before:
                self.stats['courses already there'] += 1
                continue
            if (st.pk, norm(course), start) in seen:
                self.warnings.append(f'{st.full_name} ({course}): vərəqdə iki dəfə yazılıb — bir dəfə götürüldü.')
                continue
            seen.add((st.pk, norm(course), start))
            teacher = self.teacher(r['teacher'])
            group = self.groups.get(norm(r['group'])) if r['group'] else None
            if r['group'] and not group:
                if teacher:
                    group = StudyGroup.objects.create(name=clean_name(r['group']), teacher=teacher, max_students=4)
                    self.groups[norm(r['group'])] = group
                    self.stats['groups created'] += 1
                    self.warnings.append(f'Qrup "{group.name}" yalnız Tələbələr vərəqində var idi — yaradıldı, dərs saatlarını CRM-də yazın.')
                else:
                    self.warnings.append(f'{clean_name(r["name"])}: qrup "{clean_name(r["group"])}" tapılmadı.')
            teacher = teacher or (group.teacher if group else None) or (
                self.teacher(last['teacher']) if last else None)
            fee = last['amount'] if last else ZERO
            if not last and r['status'] == 'active':
                self.warnings.append(f'{st.full_name} ({course}): ödəniş tapılmadı — aylıq haqqı CRM-də yazın.')
            e = Enrollment.objects.create(
                student=st, course=course, group=group, teacher=teacher, monthly_fee=fee,
                teacher_percent=last['pct'] if last else ZERO, start_date=start,
                first_due_date=self._next_due(last),
                status=r['status'], ended_at=r['ended'], leave_reason=r['reason'][:255], note=r['note'][:255],
            )
            self.enrollments_by_student[st.pk].append(e)
            self.stats[f'courses created ({e.get_status_display()})'] += 1
            if group and e.status == Enrollment.Status.ACTIVE and not group.students.filter(pk=st.pk).exists():
                if group.max_students and group.students.count() >= group.max_students:
                    group.max_students = group.students.count() + 1
                    group.save(update_fields=['max_students'])
                group.students.add(st)

    # ------------------------------------------------------------ payments
    def _import_payments(self, payments):
        if not hasattr(self, 'enrollments_by_student'):
            self.enrollments_by_student = defaultdict(list)
            for e in Enrollment.objects.all():
                self.enrollments_by_student[e.student_id].append(e)
        monthly_taken = set(
            StudentCharge.objects.filter(kind=StudentCharge.Kind.MONTHLY, is_cancelled=False, enrollment__isnull=False)
            .values_list('enrollment_id', 'period')
        )
        from collections import Counter

        # payments saved by an earlier run; two equal rows in the sheet are still two payments
        before = Counter(StudentPayment.objects.values_list('student_id', 'paid_at', 'amount', 'course'))
        for p in payments:
            st = self.student(p['name'], p['phone'])
            key = (st.pk, p['paid_at'], p['amount'], p['course'][:120])
            if before[key] > 0:
                before[key] -= 1
                self.stats['payments already there'] += 1
                continue
            course_n = norm(p['course'])
            enrollment = next((e for e in self.enrollments_by_student[st.pk] if self._same_course(e.course, course_n)), None)
            teacher = self.teacher(p['teacher'])
            if not teacher and p['teacher_amount']:
                self.warnings.append(
                    f'{p["paid_at"]:%d.%m.%Y} {st.full_name}: müəllim payı {p["teacher_amount"]} AZN, '
                    f'amma müəllim adı yoxdur — pay yazılmadı.')
            t_status = TEACHER_PAID.get(p['teacher_paid'])
            if not teacher or not p['teacher_amount']:
                t_status = 'none'
            elif t_status is None:
                t_status = 'pending'
            note = p['note']
            if 'bron' in p['status']:
                note = f'Bron. {note}'.strip()
            StudentPayment.objects.create(
                student=st, enrollment=enrollment, course=p['course'][:120], amount=p['amount'], method=p['method'],
                paid_at=p['paid_at'], is_new_customer=p['new'], teacher=teacher, teacher_percent=p['pct'],
                teacher_amount=p['teacher_amount'] if teacher else ZERO, teacher_status=t_status,
                teacher_paid_at=p['paid_at'] if t_status == 'paid' else None, note=note[:255],
            )
            self.stats['payments created'] += 1
            if enrollment:
                # the past is settled: book the payment against a charge of the same amount
                period = month_start(p['paid_at'])
                monthly = (enrollment.pk, period) not in monthly_taken
                StudentCharge.objects.create(
                    student=st, enrollment=enrollment, group=enrollment.group,
                    kind=StudentCharge.Kind.MONTHLY if monthly else StudentCharge.Kind.OTHER,
                    period=period, description=f'{enrollment.course} — {month_label(period)} (Excel)',
                    amount=p['amount'], due_date=p['paid_at'],
                )
                if monthly:
                    monthly_taken.add((enrollment.pk, period))
            else:
                self.stats['payments without a course (one-off)'] += 1

    def _import_unpaid(self):
        for u in getattr(self, 'unpaid', []):
            st = self.student(u['name'], u['phone'])
            description = f'{u["course"] or "Ödəniş"} (Excel: ödənilməyib)'[:200]
            if StudentCharge.objects.filter(student=st, due_date=u['due'], amount=u['amount'],
                                            description=description).exists():
                continue
            enrollment = next((e for e in self.enrollments_by_student[st.pk]
                               if self._same_course(e.course, norm(u['course']))), None)
            StudentCharge.objects.create(
                student=st, enrollment=enrollment, kind=StudentCharge.Kind.OTHER, period=month_start(u['due']),
                description=description, amount=u['amount'], due_date=u['due'],
            )
            self.stats['unpaid rows → debt'] += 1

    # ------------------------------------------------------------ report
    def _report(self, committed):
        self.stdout.write(self.style.MIGRATE_HEADING('Nəticə' + ('' if committed else ' (sınaq — heç nə yadda saxlanmadı)')))
        for k in sorted(self.stats):
            self.stdout.write(f'  {k}: {self.stats[k]}')
        if self.warnings:
            self.stdout.write(self.style.WARNING(f'\n{len(self.warnings)} xəbərdarlıq:'))
            for w in self.warnings:
                self.stdout.write(f'  • {w}')
        if not committed:
            self.stdout.write(self.style.NOTICE('\nYadda saxlamaq üçün eyni əmri --commit ilə işlədin.'))
