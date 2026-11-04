"""CRM data layer: billing (charges / payments / debts), attendance and dashboard figures."""

from __future__ import annotations

import calendar
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone

from portals.models import (
    Attendance,
    Enrollment,
    Lead,
    Schedule,
    StudentCharge,
    StudentPayment,
    StudentProfile,
    StudyGroup,
    TeacherProfile,
)

ZERO = Decimal('0')
MONTHS_AZ = (
    'Yanvar', 'Fevral', 'Mart', 'Aprel', 'May', 'İyun',
    'İyul', 'Avqust', 'Sentyabr', 'Oktyabr', 'Noyabr', 'Dekabr',
)
MONTHS_AZ_SHORT = ('Yan', 'Fev', 'Mar', 'Apr', 'May', 'İyn', 'İyl', 'Avq', 'Sen', 'Okt', 'Noy', 'Dek')


def month_start(d: date) -> date:
    return d.replace(day=1)


def add_months(d: date, n: int) -> date:
    y, m = divmod(d.month - 1 + n, 12)
    return date(d.year + y, m + 1, 1)


def month_label(d: date) -> str:
    return f'{MONTHS_AZ[d.month - 1]} {d.year}'


def month_range(d: date):
    start = month_start(d)
    return start, start.replace(day=calendar.monthrange(start.year, start.month)[1])


def parse_month(raw, default=None) -> date:
    default = default or month_start(timezone.localdate())
    try:
        y, m = str(raw).split('-')[:2]
        return date(int(y), int(m), 1)
    except (TypeError, ValueError):
        return default


def billable_groups():
    return StudyGroup.objects.filter(is_active=True, is_register_only=False, is_main_register=False)


# ---------------------------------------------------------------- billing
def sync_charges(user=None, today=None):
    """Write the monthly charge of every active enrollment whose due day has come.

    Idempotent: a month that already has a charge (even a cancelled one) is never billed again.
    """
    today = today or timezone.localdate()
    enrollments = list(
        Enrollment.objects.filter(status=Enrollment.Status.ACTIVE, monthly_fee__gt=0)
        .filter(Q(first_due_date__lte=today) | Q(first_due_date__isnull=True, start_date__lte=today))
    )
    if not enrollments:
        return 0
    existing = set(
        StudentCharge.objects.filter(kind=StudentCharge.Kind.MONTHLY, enrollment__in=enrollments)
        .values_list('enrollment_id', 'period')
    )
    new = []
    for e in enrollments:
        for due in e.due_dates(today):
            period = month_start(due)
            if (e.pk, period) in existing:
                continue
            existing.add((e.pk, period))
            new.append(StudentCharge(
                student_id=e.student_id, enrollment=e, group_id=e.group_id, kind=StudentCharge.Kind.MONTHLY,
                period=period, description=f'{e.course} — {month_label(period)}', amount=e.monthly_fee,
                due_date=due, created_by=user,
            ))
    if new:
        StudentCharge.objects.bulk_create(new, ignore_conflicts=True)
    return len(new)


def close_enrollment_billing(enrollment):
    """After someone leaves, unpaid monthly charges due after the leaving date are cancelled."""
    if not enrollment.ended_at:
        return 0
    return StudentCharge.objects.filter(
        enrollment=enrollment, kind=StudentCharge.Kind.MONTHLY, is_cancelled=False,
        due_date__gt=enrollment.ended_at,
    ).update(is_cancelled=True)


def _bucket_sums(qs):
    return {
        (row['student_id'], row['enrollment_id']): row['s'] or ZERO
        for row in qs.values('student_id', 'enrollment_id').annotate(s=Sum('amount'))
    }


class Balance(tuple):
    """(charged, paid, debt, credit). Each course is settled on its own: money paid for one
    course never hides a debt on another, and one-off payments (mock test...) are not credit."""

    __slots__ = ()

    def __new__(cls, charged=ZERO, paid=ZERO, debt=ZERO, credit=ZERO):
        return super().__new__(cls, (charged, paid, debt, credit))

    charged = property(lambda self: self[0])
    paid = property(lambda self: self[1])
    debt = property(lambda self: self[2])
    credit = property(lambda self: self[3])


EMPTY_BALANCE = Balance()


def balances(student_ids=None):
    """{student_id: Balance} for everyone with any billing record."""
    charges = StudentCharge.objects.filter(is_cancelled=False)
    pays = StudentPayment.objects.all()
    if student_ids is not None:
        charges, pays = charges.filter(student_id__in=student_ids), pays.filter(student_id__in=student_ids)
    charged, paid = _bucket_sums(charges), _bucket_sums(pays)
    acc = defaultdict(lambda: [ZERO, ZERO, ZERO, ZERO])
    for key in set(charged) | set(paid):
        c, p = charged.get(key, ZERO), paid.get(key, ZERO)
        row = acc[key[0]]
        row[0] += c
        row[1] += p
        if key[1] is not None:  # course buckets; unlinked payments are one-offs
            row[2] += max(c - p, ZERO)
            row[3] += max(p - c, ZERO)
        else:
            row[2] += max(c - p, ZERO)
    return {sid: Balance(*v) for sid, v in acc.items()}


def allocate(charges, paid_total):
    """FIFO: payments cover the oldest charges first. Returns rows with paid / left / state."""
    today = timezone.localdate()
    left_to_spend = paid_total
    rows = []
    for ch in sorted(charges, key=lambda c: (c.due_date, c.id)):
        covered = min(ch.amount, max(left_to_spend, ZERO))
        left_to_spend -= covered
        left = ch.amount - covered
        if left <= 0:
            state = 'paid'
        elif ch.due_date < today:
            state = 'overdue'
        elif covered > 0:
            state = 'partial'
        else:
            state = 'open'
        rows.append({'charge': ch, 'covered': covered, 'left': left, 'state': state})
    return rows


def _allocate_buckets(charges, payments):
    """Allocate per course (enrollment); returns (rows, {enrollment_id: debt})."""
    by_c, by_p = defaultdict(list), defaultdict(lambda: ZERO)
    for ch in charges:
        by_c[ch.enrollment_id].append(ch)
    for p in payments:
        by_p[p.enrollment_id] += p.amount
    rows, debt = [], {}
    for key in set(by_c) | set(by_p):
        part = allocate(by_c.get(key, []), by_p[key])
        rows.extend(part)
        debt[key] = sum((r['left'] for r in part), ZERO)
    return rows, debt


def debtors():
    """Students who owe money, most overdue first."""
    today = timezone.localdate()
    owing = {sid: b for sid, b in balances().items() if b.debt > 0}
    if not owing:
        return []
    students = StudentProfile.objects.filter(pk__in=owing).select_related('user')
    charges, payments = defaultdict(list), defaultdict(list)
    for ch in StudentCharge.objects.filter(student_id__in=owing, is_cancelled=False):
        charges[ch.student_id].append(ch)
    for p in StudentPayment.objects.filter(student_id__in=owing).only('student_id', 'enrollment_id', 'amount'):
        payments[p.student_id].append(p)
    courses = defaultdict(list)
    for e in Enrollment.objects.filter(student_id__in=owing).exclude(status=Enrollment.Status.WAITING):
        courses[e.student_id].append(e.course)
    rows = []
    for st in students:
        b = owing[st.pk]
        alloc, _ = _allocate_buckets(charges[st.pk], payments[st.pk])
        unpaid = [r for r in alloc if r['left'] > 0]
        overdue = [r for r in unpaid if r['state'] == 'overdue']
        oldest = min((r['charge'].due_date for r in overdue), default=None)
        rows.append({
            'student': st,
            'balance': b.debt,
            'courses': sorted(set(courses[st.pk])),
            'overdue_amount': sum((r['left'] for r in overdue), ZERO),
            'oldest_due': oldest,
            'days_overdue': (today - oldest).days if oldest else 0,
            'open_items': len(unpaid),
        })
    rows.sort(key=lambda r: (-r['days_overdue'], -r['balance']))
    return rows


def student_ledger(student):
    charges = list(
        StudentCharge.objects.filter(student=student, is_cancelled=False).select_related('group', 'enrollment')
    )
    payments = list(
        StudentPayment.objects.filter(student=student).select_related('received_by', 'teacher__user', 'enrollment')
    )
    rows, debt_by_enrollment = _allocate_buckets(charges, payments)
    rows.sort(key=lambda r: (r['charge'].due_date, r['charge'].id), reverse=True)
    b = balances([student.pk]).get(student.pk, EMPTY_BALANCE)
    return {
        'charges': rows, 'payments': payments, 'charged': b.charged, 'paid': b.paid,
        'balance': b.debt, 'credit': b.credit, 'debt_by_enrollment': debt_by_enrollment,
    }


def upcoming_dues(days=7):
    """Active enrollments whose next monthly payment falls within the next `days` days."""
    today = timezone.localdate()
    horizon = today + timedelta(days=days)
    rows = []
    for e in Enrollment.objects.filter(status=Enrollment.Status.ACTIVE, monthly_fee__gt=0).select_related(
        'student__user', 'teacher__user',
    ):
        nxt = e.next_due_date
        if nxt and nxt <= horizon:
            rows.append({'enrollment': e, 'student': e.student, 'due': nxt, 'days': (nxt - today).days})
    rows.sort(key=lambda r: r['due'])
    return rows


def online_payments_by_month(start: date):
    """Successful card payments made on the site (payments app), by month."""
    try:
        from payments.models import Payment
    except Exception:  # pragma: no cover - payments app is optional
        return {}
    qs = (
        Payment.objects.filter(status=Payment.Status.SUCCESS, created_at__date__gte=start)
        .annotate(m=TruncMonth('created_at')).values('m').annotate(s=Sum('amount'))
    )
    return {_as_date(row['m']): row['s'] or ZERO for row in qs}


def _as_date(v):
    return v.date() if hasattr(v, 'date') else v


def revenue_series(months=6):
    """Last N months: office payments, online payments and the month's billed total."""
    this = month_start(timezone.localdate())
    start = add_months(this, -(months - 1))
    office = {
        _as_date(row['m']): row['s'] or ZERO
        for row in StudentPayment.objects.filter(paid_at__gte=start)
        .annotate(m=TruncMonth('paid_at')).values('m').annotate(s=Sum('amount'))
    }
    online = online_payments_by_month(start)
    billed = {
        row['period']: row['s'] or ZERO
        for row in StudentCharge.objects.filter(is_cancelled=False, period__gte=start)
        .values('period').annotate(s=Sum('amount'))
    }
    series = []
    for i in range(months):
        m = add_months(start, i)
        series.append({
            'month': m, 'label': MONTHS_AZ_SHORT[m.month - 1],
            'office': office.get(m, ZERO), 'online': online.get(m, ZERO), 'billed': billed.get(m, ZERO),
        })
    peak = max([max(r['office'] + r['online'], r['billed']) for r in series] + [Decimal('1')])
    for r in series:
        r['total'] = r['office'] + r['online']
        r['h_office'] = float(r['office'] / peak * 100)
        r['h_online'] = float(r['online'] / peak * 100)
        r['h_billed'] = float(r['billed'] / peak * 100)
        r['h_total'] = r['h_office'] + r['h_online']
    return series


# ---------------------------------------------------------------- teachers & reports
TEACHER_COST = Q(teacher_status__in=(StudentPayment.TeacherStatus.PENDING, StudentPayment.TeacherStatus.PAID))


def _money_totals(qs):
    agg = qs.aggregate(
        revenue=Sum('amount'), n=Count('id'), new=Count('id', filter=Q(is_new_customer=True)),
        tcost=Sum('teacher_amount', filter=TEACHER_COST),
        paid=Sum('teacher_amount', filter=Q(teacher_status=StudentPayment.TeacherStatus.PAID)),
        pending=Sum('teacher_amount', filter=Q(teacher_status=StudentPayment.TeacherStatus.PENDING)),
    )
    out = {k: (v if v is not None else ZERO) if k not in ('n', 'new') else v for k, v in agg.items()}
    out['net'] = out['revenue'] - out['tcost']
    out['avg'] = (out['revenue'] / out['n']).quantize(Decimal('0.01')) if out['n'] else ZERO
    out['margin'] = round(out['net'] * 100 / out['revenue']) if out['revenue'] else None
    return out


def teacher_payouts(period: date):
    """Per teacher for the month: what their students paid, their share, paid and still owed."""
    start, end = month_range(period)
    month = StudentPayment.objects.filter(paid_at__range=(start, end), teacher__isnull=False)
    rows = []
    teacher_ids = set(month.order_by().values_list('teacher_id', flat=True))
    older = {
        r['teacher_id']: r['s'] for r in StudentPayment.objects.filter(
            paid_at__lt=start, teacher_status=StudentPayment.TeacherStatus.PENDING, teacher__isnull=False,
        ).values('teacher_id').annotate(s=Sum('teacher_amount'))
    }
    teacher_ids |= set(older)
    teachers = {t.pk: t for t in TeacherProfile.objects.filter(pk__in=teacher_ids).select_related('user')}
    for tid in teacher_ids:
        t = teachers.get(tid)
        if not t:
            continue
        qs = month.filter(teacher_id=tid)
        tot = _money_totals(qs)
        tot['students'] = qs.order_by().values('student_id').distinct().count()
        rows.append({'teacher': t, 'older_pending': older.get(tid) or ZERO, **tot})
    rows.sort(key=lambda r: (-(r['pending'] + r['older_pending']), -r['revenue']))
    return rows


def monthly_report(months=12):
    this = month_start(timezone.localdate())
    out = []
    for i in range(months - 1, -1, -1):
        m = add_months(this, -i)
        start, end = month_range(m)
        tot = _money_totals(StudentPayment.objects.filter(paid_at__range=(start, end)))
        tot['billed'] = (
            StudentCharge.objects.filter(is_cancelled=False, period=m).aggregate(s=Sum('amount'))['s'] or ZERO
        )
        out.append({'month': m, 'label': month_label(m), **tot})
    return [r for r in out if r['n'] or r['billed']] or out[-1:]


def breakdown(start: date, end: date, field: str):
    """Revenue split by course (field='course') or teacher (field='teacher')."""
    qs = StudentPayment.objects.filter(paid_at__range=(start, end))
    total = qs.aggregate(s=Sum('amount'))['s'] or ZERO
    key = 'course' if field == 'course' else 'teacher_id'
    rows = []
    for value in qs.order_by().values_list(key, flat=True).distinct():
        tot = _money_totals(qs.filter(**{key: value}))
        tot['share'] = float(tot['revenue'] * 100 / total) if total else 0
        tot['students'] = qs.filter(**{key: value}).order_by().values('student_id').distinct().count()
        rows.append({'key': value, **tot})
    if field == 'teacher':
        names = {t.pk: t for t in TeacherProfile.objects.filter(pk__in=[r['key'] for r in rows if r['key']]).select_related('user')}
        for r in rows:
            r['teacher'] = names.get(r['key'])
    rows.sort(key=lambda r: -r['revenue'])
    peak = max([r['revenue'] for r in rows] + [Decimal('1')])
    for r in rows:
        r['bar'] = float(r['revenue'] * 100 / peak)
    return rows


def course_names():
    """Every course name already used, for the course field's suggestions."""
    names = set(Enrollment.objects.values_list('course', flat=True))
    names |= set(StudentPayment.objects.exclude(course='').values_list('course', flat=True))
    return sorted(n for n in names if n)


# ---------------------------------------------------------------- attendance
def _rate(present, late, absent):
    total = present + late + absent
    return round((present + late) * 100 / total) if total else None


def attendance_by_student(start: date, end: date):
    """{student_id: {'present','late','absent','rate'}} for marks in the range."""
    out = defaultdict(lambda: {'present': 0, 'late': 0, 'absent': 0})
    rows = (
        Attendance.objects.filter(session_date__range=(start, end), student__isnull=False)
        .values('student_id', 'status').annotate(n=Count('id'))
    )
    for row in rows:
        out[row['student_id']][row['status']] = row['n']
    for v in out.values():
        v['rate'] = _rate(v['present'], v['late'], v['absent'])
        v['marks'] = v['present'] + v['late'] + v['absent']
    return out


def attendance_overview(period: date):
    start, end = month_range(period)
    totals = dict(
        Attendance.objects.filter(session_date__range=(start, end))
        .values_list('status').annotate(n=Count('id'))
    )
    present, late, absent = (totals.get(k, 0) for k in ('present', 'late', 'absent'))
    per_day = defaultdict(lambda: {'present': 0, 'late': 0, 'absent': 0})
    for row in (
        Attendance.objects.filter(session_date__range=(start, end))
        .values('session_date', 'status').annotate(n=Count('id'))
    ):
        per_day[row['session_date']][row['status']] = row['n']
    peak = max([sum(v.values()) for v in per_day.values()] + [1])
    days = []
    d = start
    while d <= end:
        v = per_day.get(d, {'present': 0, 'late': 0, 'absent': 0})
        days.append({
            'date': d, 'n': d.day, 'weekend': d.weekday() >= 5, **v,
            'h_present': v['present'] * 100 / peak, 'h_late': v['late'] * 100 / peak,
            'h_absent': v['absent'] * 100 / peak, 'total': sum(v.values()),
        })
        d += timedelta(days=1)
    by_student = attendance_by_student(start, end)
    at_risk_ids = [sid for sid, v in by_student.items() if v['rate'] is not None and v['rate'] < 75 and v['marks'] >= 3]
    students = {s.pk: s for s in StudentProfile.objects.filter(pk__in=at_risk_ids).select_related('user').prefetch_related('groups')}
    at_risk = sorted(
        ({'student': students[sid], **by_student[sid]} for sid in at_risk_ids if sid in students),
        key=lambda r: r['rate'],
    )
    return {
        'start': start, 'end': end, 'present': present, 'late': late, 'absent': absent,
        'marks': present + late + absent, 'rate': _rate(present, late, absent),
        'days': days, 'at_risk': at_risk, 'students_marked': len(by_student),
    }


def todays_lessons():
    today = timezone.localdate()
    return list(
        Schedule.objects.filter(weekday=today.weekday(), group__is_active=True, effective_from__lte=today)
        .select_related('group', 'group__teacher__user').order_by('start_time')[:12]
    )


# ---------------------------------------------------------------- leads
def lead_funnel(since: date | None = None):
    qs = Lead.objects.all()
    if since:
        qs = qs.filter(created_at__date__gte=since)
    counts = dict(qs.values_list('status').annotate(n=Count('id')))
    total = sum(counts.values())
    peak = max(counts.values(), default=0)
    steps = []
    for value, label in Lead.Status.choices:
        n = counts.get(value, 0)
        # bar length relative to the biggest stage; pct is the share of all leads
        steps.append({'value': value, 'label': label, 'n': n, 'pct': round(n * 100 / total) if total else 0,
                      'bar': round(n * 100 / peak) if peak else 0})
    return {'total': total, 'steps': steps}


SOURCE_COLORS = {
    'contact_form': '#FF5414', 'study_abroad': '#0E7C86', 'level_test': '#6C5CE7', 'online_payment': '#16A34A',
    'phone': '#00313D', 'whatsapp': '#22C55E', 'instagram': '#E1306C', 'walk_in': '#F59E0B',
    'referral': '#3B82F6', 'corporate': '#64748B', 'other': '#94A3B8',
}


def lead_sources(since: date):
    rows = list(
        Lead.objects.filter(created_at__date__gte=since).values('source').annotate(n=Count('id')).order_by('-n')
    )
    total = sum(r['n'] for r in rows) or 1
    labels = dict(Lead.Source.choices)
    offset = 0.0
    out = []
    for r in rows:
        frac = r['n'] / total
        out.append({
            'source': r['source'], 'label': labels.get(r['source'], r['source']), 'n': r['n'],
            'pct': round(frac * 100), 'color': SOURCE_COLORS.get(r['source'], '#94A3B8'),
            # donut segment on a circle with circumference 100
            'dash': f'{frac * 100:.2f} {100 - frac * 100:.2f}', 'offset': f'{25 - offset:.2f}',
        })
        offset += frac * 100
    return out


def dashboard(period: date | None = None):
    today = timezone.localdate()
    this = month_start(today)
    prev = add_months(this, -1)
    leads_this = Lead.objects.filter(created_at__date__gte=this).count()
    leads_prev = Lead.objects.filter(created_at__date__gte=prev, created_at__date__lt=this).count()
    enrolled_this = Lead.objects.filter(created_at__date__gte=this, status=Lead.Status.ENROLLED).count()
    start, end = month_range(this)
    money = _money_totals(StudentPayment.objects.filter(paid_at__range=(start, end)))
    online = online_payments_by_month(this).get(this, ZERO)
    billed = StudentCharge.objects.filter(is_cancelled=False, period=this).aggregate(s=Sum('amount'))['s'] or ZERO
    debt_rows = debtors()
    att = attendance_overview(this)
    by_status = dict(
        Enrollment.objects.values_list('status').annotate(n=Count('student_id', distinct=True))
    )
    teacher_owed = (
        StudentPayment.objects.filter(teacher_status=StudentPayment.TeacherStatus.PENDING)
        .aggregate(s=Sum('teacher_amount'))['s'] or ZERO
    )
    follow_ups = list(
        Lead.objects.filter(status__in=(Lead.Status.NEW, Lead.Status.CONTACTED, Lead.Status.TRIAL))
        .filter(Q(next_action_at__lte=today) | Q(next_action_at__isnull=True, status=Lead.Status.NEW))
        .select_related('assigned_to').order_by('next_action_at', '-created_at')[:6]
    )
    return {
        'today': today,
        'month_label': month_label(this),
        'leads_this': leads_this,
        'leads_delta': leads_this - leads_prev,
        'conversion': round(enrolled_this * 100 / leads_this) if leads_this else None,
        'active_students': by_status.get(Enrollment.Status.ACTIVE, 0),
        'waiting_students': by_status.get(Enrollment.Status.WAITING, 0),
        'money': money,
        'collected': money['revenue'] + online,
        'collected_online': online,
        'billed': billed,
        'collect_pct': min(100, round(money['revenue'] * 100 / billed)) if billed else None,
        'teacher_owed': teacher_owed,
        'debt_total': sum((r['balance'] for r in debt_rows), ZERO),
        'debtors_count': len(debt_rows),
        'debtors': debt_rows[:6],
        'upcoming': upcoming_dues(7)[:8],
        'attendance': att,
        'revenue': revenue_series(6),
        'funnel': lead_funnel(add_months(this, -2)),
        'sources': lead_sources(add_months(this, -2)),
        'recent_leads': list(Lead.objects.select_related('assigned_to')[:6]),
        'follow_ups': follow_ups,
        'lessons_today': todays_lessons(),
    }
