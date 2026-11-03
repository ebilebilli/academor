"""CRM data layer: billing (charges / payments / debts), attendance and dashboard figures."""

from __future__ import annotations

import calendar
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal

from django.db import IntegrityError, transaction
from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone

from portals.models import (
    Attendance,
    Lead,
    Schedule,
    StudentCharge,
    StudentPayment,
    StudentProfile,
    StudyGroup,
)

ZERO = Decimal('0')
MONTHS_AZ = (
    'Yanvar', 'Fevral', 'Mart', 'Aprel', 'May', 'İyun',
    'İyul', 'Avqust', 'Sentyabr', 'Oktyabr', 'Noyabr', 'Dekabr',
)
MONTHS_AZ_SHORT = ('Yan', 'Fev', 'Mar', 'Apr', 'May', 'İyn', 'İyl', 'Avq', 'Sen', 'Okt', 'Noy', 'Dek')
DUE_DAY = 10  # monthly fees are due by the 10th of the month


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
@transaction.atomic
def generate_monthly_charges(period: date, user=None):
    """One monthly charge per student per group with a fee; existing ones are left alone."""
    period = month_start(period)
    due = period.replace(day=min(DUE_DAY, calendar.monthrange(period.year, period.month)[1]))
    created = skipped = 0
    no_fee = []
    for group in billable_groups().prefetch_related('students'):
        if not group.monthly_fee:
            if group.students.exists():
                no_fee.append(group)
            continue
        for student in group.students.all():
            exists = StudentCharge.objects.filter(
                student=student, group=group, period=period,
                kind=StudentCharge.Kind.MONTHLY, is_cancelled=False,
            ).exists()
            if exists:
                skipped += 1
                continue
            try:
                with transaction.atomic():
                    StudentCharge.objects.create(
                        student=student, group=group, period=period, kind=StudentCharge.Kind.MONTHLY,
                        description=f'{group.name} — {month_label(period)}',
                        amount=group.monthly_fee, due_date=due, created_by=user,
                    )
                created += 1
            except IntegrityError:
                skipped += 1
    return {'created': created, 'skipped': skipped, 'no_fee_groups': no_fee}


def _sums_by_student(qs, field='amount'):
    return {row['student_id']: row['s'] or ZERO for row in qs.values('student_id').annotate(s=Sum(field))}


def balances():
    """{student_id: (charged, paid, balance)} for everyone with any billing record."""
    charged = _sums_by_student(StudentCharge.objects.filter(is_cancelled=False))
    paid = _sums_by_student(StudentPayment.objects.all())
    out = {}
    for sid in set(charged) | set(paid):
        c, p = charged.get(sid, ZERO), paid.get(sid, ZERO)
        out[sid] = (c, p, c - p)
    return out


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


def debtors():
    """Students who owe money, most overdue first."""
    today = timezone.localdate()
    owing = {sid: b for sid, b in balances().items() if b[2] > 0}
    if not owing:
        return []
    students = StudentProfile.objects.filter(pk__in=owing).select_related('user').prefetch_related('groups')
    charges = defaultdict(list)
    for ch in StudentCharge.objects.filter(student_id__in=owing, is_cancelled=False):
        charges[ch.student_id].append(ch)
    rows = []
    for st in students:
        charged, paid, balance = owing[st.pk]
        alloc = allocate(charges[st.pk], paid)
        unpaid = [r for r in alloc if r['left'] > 0]
        overdue = [r for r in unpaid if r['state'] == 'overdue']
        oldest = min((r['charge'].due_date for r in overdue), default=None)
        rows.append({
            'student': st,
            'balance': balance,
            'overdue_amount': sum((r['left'] for r in overdue), ZERO),
            'oldest_due': oldest,
            'days_overdue': (today - oldest).days if oldest else 0,
            'open_items': len(unpaid),
        })
    rows.sort(key=lambda r: (-r['days_overdue'], -r['balance']))
    return rows


def student_ledger(student):
    charges = list(StudentCharge.objects.filter(student=student, is_cancelled=False).select_related('group'))
    payments = list(StudentPayment.objects.filter(student=student).select_related('received_by'))
    paid = sum((p.amount for p in payments), ZERO)
    charged = sum((c.amount for c in charges), ZERO)
    rows = allocate(charges, paid)
    rows.sort(key=lambda r: (r['charge'].due_date, r['charge'].id), reverse=True)
    return {'charges': rows, 'payments': payments, 'charged': charged, 'paid': paid, 'balance': charged - paid}


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
    return {row['m'].date() if hasattr(row['m'], 'date') else row['m']: row['s'] or ZERO for row in qs}


def revenue_series(months=6):
    """Last N months: office payments, online payments and the month's billed total."""
    this = month_start(timezone.localdate())
    start = add_months(this, -(months - 1))
    office = {
        (row['m'].date() if hasattr(row['m'], 'date') else row['m']): row['s'] or ZERO
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
    collected = StudentPayment.objects.filter(paid_at__range=(start, end)).aggregate(s=Sum('amount'))['s'] or ZERO
    online = online_payments_by_month(this).get(this, ZERO)
    billed = StudentCharge.objects.filter(is_cancelled=False, period=this).aggregate(s=Sum('amount'))['s'] or ZERO
    debt_rows = debtors()
    att = attendance_overview(this)
    active_students = StudentProfile.objects.filter(groups__is_active=True).distinct().count()
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
        'active_students': active_students,
        'collected': collected + online,
        'collected_online': online,
        'billed': billed,
        'collect_pct': min(100, round((collected + online) * 100 / billed)) if billed else None,
        'debt_total': sum((r['balance'] for r in debt_rows), ZERO),
        'debtors_count': len(debt_rows),
        'debtors': debt_rows[:6],
        'attendance': att,
        'revenue': revenue_series(6),
        'funnel': lead_funnel(add_months(this, -2)),
        'sources': lead_sources(add_months(this, -2)),
        'recent_leads': list(Lead.objects.select_related('assigned_to')[:6]),
        'follow_ups': follow_ups,
        'lessons_today': todays_lessons(),
    }
