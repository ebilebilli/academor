"""Academor CRM: leads, students, billing, attendance and groups for the office team.

Staff only (Django staff users). Lives under the secret admin prefix: {ADMIN_URL}crm/.
"""

from __future__ import annotations

import json
from decimal import Decimal, InvalidOperation
from functools import wraps
from urllib.parse import quote

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.db.models import Count, Q, Sum
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone, translation
from django.views.decorators.http import require_POST

from portals.crm_forms import ChargeForm, LeadForm, LeadNoteForm, PaymentForm
from portals.models import (
    Attendance,
    Lead,
    LeadActivity,
    StudentCharge,
    StudentPayment,
    StudentProfile,
    StudyGroup,
)
from portals.utils import crm

def crm_view(view):
    """Staff only, and always in Azerbaijani (dates like "3 gün əvvəl", labels)."""
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        with translation.override('az'):
            return view(request, *args, **kwargs)
    return staff_member_required(wrapped)


def _ctx(request, section, **extra):
    open_leads = Lead.objects.filter(status=Lead.Status.NEW).count()
    return {'crm_section': section, 'crm_new_leads': open_leads, **extra}


def _wa_link(phone, text=''):
    digits = ''.join(ch for ch in (phone or '') if ch.isdigit())
    if not digits:
        return ''
    if len(digits) == 9:
        digits = '994' + digits
    elif digits.startswith('0') and len(digits) == 10:
        digits = '994' + digits[1:]
    return f'https://wa.me/{digits}' + (f'?text={quote(text)}' if text else '')


# ---------------------------------------------------------------- dashboard
@crm_view
def dashboard(request):
    return render(request, 'crm/dashboard.html', _ctx(request, 'dashboard', d=crm.dashboard()))


@crm_view
def search(request):
    q = (request.GET.get('q') or '').strip()
    leads = students = []
    if q:
        leads = list(Lead.objects.filter(Q(full_name__icontains=q) | Q(phone__icontains=q) | Q(email__icontains=q))[:20])
        students = list(
            StudentProfile.objects.filter(
                Q(user__username__icontains=q) | Q(user__first_name__icontains=q)
                | Q(user__last_name__icontains=q) | Q(phone__icontains=q)
            ).select_related('user')[:20]
        )
    return render(request, 'crm/search.html', _ctx(request, '', q=q, leads=leads, students=students))


# ---------------------------------------------------------------- leads
def _lead_filters(request):
    qs = Lead.objects.select_related('assigned_to')
    f = {k: (request.GET.get(k) or '').strip() for k in ('q', 'source', 'status', 'assigned')}
    if f['q']:
        qs = qs.filter(Q(full_name__icontains=f['q']) | Q(phone__icontains=f['q']) | Q(interest__icontains=f['q']))
    if f['source']:
        qs = qs.filter(source=f['source'])
    if f['status']:
        qs = qs.filter(status=f['status'])
    if f['assigned'] == 'me':
        qs = qs.filter(assigned_to=request.user)
    elif f['assigned'] == 'none':
        qs = qs.filter(assigned_to__isnull=True)
    return qs, f


@crm_view
def leads(request):
    view = request.GET.get('view') or 'board'
    qs, f = _lead_filters(request)
    ctx = _ctx(
        request, 'leads', view=view, f=f, sources=Lead.Source.choices, statuses=Lead.Status.choices,
        today=timezone.localdate(),
    )
    if view == 'list':
        page = Paginator(qs, 40).get_page(request.GET.get('page'))
        ctx.update(page=page)
    else:
        cols = []
        for value, label in Lead.Status.choices:
            col_qs = qs.filter(status=value)
            # closed columns only show the latest cards
            limit = 30 if value in (Lead.Status.ENROLLED, Lead.Status.LOST) else 200
            cols.append({'value': value, 'label': label, 'count': col_qs.count(), 'leads': list(col_qs[:limit])})
        ctx.update(columns=cols)
    return render(request, 'crm/leads.html', ctx)


@crm_view
def lead_new(request):
    form = LeadForm(request.POST or None, initial={'source': Lead.Source.PHONE, 'assigned_to': request.user})
    if request.method == 'POST' and form.is_valid():
        lead = form.save()
        LeadActivity.objects.create(lead=lead, author=request.user, kind=LeadActivity.Kind.CREATED,
                                    text=f'Əl ilə əlavə edildi: {lead.get_source_display()}')
        messages.success(request, 'Müraciət əlavə olundu.')
        return redirect('crm:lead', pk=lead.pk)
    return render(request, 'crm/lead_form.html', _ctx(request, 'leads', form=form))


@crm_view
def lead_detail(request, pk):
    lead = get_object_or_404(Lead.objects.select_related('assigned_to', 'student__user'), pk=pk)
    old_status = lead.status
    form = LeadForm(instance=lead)
    note_form = LeadNoteForm()
    if request.method == 'POST':
        if 'save_lead' in request.POST:
            form = LeadForm(request.POST, instance=lead)
            if form.is_valid():
                lead = form.save()
                if lead.status != old_status:
                    LeadActivity.objects.create(
                        lead=lead, author=request.user, kind=LeadActivity.Kind.STATUS,
                        text=f'{Lead.Status(old_status).label} → {lead.get_status_display()}',
                    )
                messages.success(request, 'Yadda saxlanıldı.')
                return redirect('crm:lead', pk=lead.pk)
        elif 'add_note' in request.POST:
            note_form = LeadNoteForm(request.POST)
            if note_form.is_valid():
                note = note_form.save(commit=False)
                note.lead, note.author = lead, request.user
                note.save()
                Lead.objects.filter(pk=lead.pk).update(updated_at=timezone.now())
                return redirect('crm:lead', pk=lead.pk)
        elif 'link_student' in request.POST:
            student = StudentProfile.objects.filter(pk=request.POST.get('student')).first()
            if student:
                lead.student = student
                lead.status = Lead.Status.ENROLLED
                lead.save(update_fields=['student', 'status', 'updated_at'])
                LeadActivity.objects.create(lead=lead, author=request.user, kind=LeadActivity.Kind.STATUS,
                                            text=f'Tələbəyə bağlandı: {student.full_name}')
                messages.success(request, 'Müraciət tələbəyə bağlandı.')
            return redirect('crm:lead', pk=lead.pk)
    wa_text = f'Salam, {lead.full_name}! Academor-dan yazırıq.'
    return render(request, 'crm/lead_detail.html', _ctx(
        request, 'leads', lead=lead, form=form, note_form=note_form,
        activities=lead.activities.select_related('author')[:50],
        wa=_wa_link(lead.phone, wa_text),
        students=StudentProfile.objects.select_related('user').order_by('user__username'),
        statuses=Lead.Status.choices,
    ))


@crm_view
@require_POST
def lead_move(request, pk):
    """Board drag & drop: change a lead's status."""
    lead = get_object_or_404(Lead, pk=pk)
    try:
        status = json.loads(request.body or '{}').get('status')
    except ValueError:
        status = request.POST.get('status')
    if status not in Lead.Status.values:
        return JsonResponse({'ok': False, 'error': 'bad_status'}, status=400)
    if status != lead.status:
        old = lead.status
        lead.status = status
        lead.save(update_fields=['status', 'updated_at'])
        LeadActivity.objects.create(lead=lead, author=request.user, kind=LeadActivity.Kind.STATUS,
                                    text=f'{Lead.Status(old).label} → {lead.get_status_display()}')
    return JsonResponse({'ok': True, 'status': lead.status})


# ---------------------------------------------------------------- students
@crm_view
def students(request):
    q = (request.GET.get('q') or '').strip()
    group_id = request.GET.get('group') or ''
    only = request.GET.get('only') or ''
    qs = StudentProfile.objects.select_related('user').prefetch_related('groups').order_by('user__username')
    if q:
        qs = qs.filter(Q(user__username__icontains=q) | Q(user__first_name__icontains=q)
                       | Q(user__last_name__icontains=q) | Q(phone__icontains=q))
    if group_id:
        qs = qs.filter(groups__pk=group_id)
    bal = crm.balances()
    start, end = crm.month_range(timezone.localdate())
    att = crm.attendance_by_student(start, end)
    if only == 'debt':
        qs = qs.filter(pk__in=[sid for sid, b in bal.items() if b[2] > 0])
    elif only == 'risk':
        qs = qs.filter(pk__in=[sid for sid, v in att.items() if v['rate'] is not None and v['rate'] < 75])
    page = Paginator(qs.distinct(), 40).get_page(request.GET.get('page'))
    rows = []
    for st in page:
        b = bal.get(st.pk, (crm.ZERO, crm.ZERO, crm.ZERO))
        a = att.get(st.pk)
        rows.append({'student': st, 'balance': b[2], 'paid': b[1], 'att': a,
                     'groups': [g for g in st.groups.all() if not g.is_main_register]})
    groups = crm.billable_groups().order_by('name')
    return render(request, 'crm/students.html', _ctx(
        request, 'students', page=page, rows=rows, q=q, group_id=group_id, only=only, groups=groups,
        total=StudentProfile.objects.count(),
    ))


@crm_view
def student_detail(request, pk):
    student = get_object_or_404(StudentProfile.objects.select_related('user'), pk=pk)
    ledger = crm.student_ledger(student)
    today = timezone.localdate()
    since = crm.add_months(crm.month_start(today), -2)
    marks = list(
        Attendance.objects.filter(student=student, session_date__gte=since)
        .select_related('group', 'schedule__group').order_by('-session_date')
    )
    summary = {'present': 0, 'late': 0, 'absent': 0}
    for m in marks:
        summary[m.status] = summary.get(m.status, 0) + 1
    rate = crm._rate(summary['present'], summary['late'], summary['absent'])
    pay_form = PaymentForm(initial={'student': student, 'amount': ledger['balance'] if ledger['balance'] > 0 else None})
    charge_form = ChargeForm(initial={'student': student})
    debt_text = (
        f'Salam! Academor-dan yazırıq. {student.full_name} üzrə {ledger["balance"]} AZN '
        f'ödəniş gözlənilir. Sualınız olarsa, bizə yazın.'
    )
    return render(request, 'crm/student_detail.html', _ctx(
        request, 'students', student=student, ledger=ledger, marks=marks[:40], summary=summary, rate=rate,
        groups=[g for g in student.groups.select_related('teacher__user') if not g.is_main_register],
        pay_form=pay_form, charge_form=charge_form, leads=student.crm_leads.all()[:5],
        wa=_wa_link(student.phone, debt_text if ledger['balance'] > 0 else ''),
    ))


# ---------------------------------------------------------------- billing
@crm_view
def payments(request):
    period = crm.parse_month(request.GET.get('month'))
    start, end = crm.month_range(period)
    method = request.GET.get('method') or ''
    qs = StudentPayment.objects.filter(paid_at__range=(start, end)).select_related('student__user', 'received_by')
    if method:
        qs = qs.filter(method=method)
    by_method = {row['method']: row['s'] for row in qs.values('method').annotate(s=Sum('amount'))}
    total = sum(by_method.values(), crm.ZERO)
    billed = StudentCharge.objects.filter(is_cancelled=False, period=period).aggregate(s=Sum('amount'))['s'] or crm.ZERO
    online = crm.online_payments_by_month(period).get(period, crm.ZERO)
    methods = [
        {'value': v, 'label': l, 'sum': by_method.get(v, crm.ZERO),
         'pct': float(by_method.get(v, 0) / total * 100) if total else 0}
        for v, l in StudentPayment.Method.choices
    ]
    return render(request, 'crm/payments.html', _ctx(
        request, 'payments', period=period, period_label=crm.month_label(period),
        prev=crm.add_months(period, -1), next=crm.add_months(period, 1),
        payments=qs[:300], total=total, billed=billed, online=online, methods=methods, method=method,
        method_choices=StudentPayment.Method.choices, revenue=crm.revenue_series(6),
        groups_no_fee=crm.billable_groups().filter(monthly_fee__isnull=True).annotate(n=Count('students')).filter(n__gt=0),
    ))


@crm_view
def payment_new(request):
    form = PaymentForm(request.POST or None, initial={'student': request.GET.get('student')})
    if request.method == 'POST' and form.is_valid():
        pay = form.save(commit=False)
        pay.received_by = request.user
        pay.save()
        messages.success(request, f'{pay.amount} AZN ödəniş qeydə alındı (qəbz {pay.receipt_number}).')
        nxt = request.POST.get('next')
        if nxt and nxt.startswith('/'):
            return redirect(nxt)
        return redirect('crm:payment_receipt', pk=pay.pk)
    return render(request, 'crm/payment_form.html', _ctx(request, 'payments', form=form, title='Ödəniş qəbul et'))


@crm_view
def charge_new(request):
    form = ChargeForm(request.POST or None, initial={'student': request.GET.get('student')})
    if request.method == 'POST' and form.is_valid():
        ch = form.save(commit=False)
        ch.created_by = request.user
        ch.save()
        messages.success(request, f'{ch.amount} AZN hesab yazıldı.')
        nxt = request.POST.get('next')
        if nxt and nxt.startswith('/'):
            return redirect(nxt)
        return redirect('crm:student', pk=ch.student_id)
    return render(request, 'crm/payment_form.html', _ctx(request, 'payments', form=form, title='Hesab yaz'))


@crm_view
@require_POST
def charge_cancel(request, pk):
    ch = get_object_or_404(StudentCharge, pk=pk)
    ch.is_cancelled = True
    ch.save(update_fields=['is_cancelled'])
    messages.info(request, 'Hesab ləğv edildi.')
    return redirect('crm:student', pk=ch.student_id)


@crm_view
def payment_receipt(request, pk):
    pay = get_object_or_404(StudentPayment.objects.select_related('student__user', 'received_by'), pk=pk)
    return render(request, 'crm/receipt.html', {'pay': pay, 'balance': crm.student_ledger(pay.student)['balance']})


@crm_view
def debts(request):
    rows = crm.debtors()
    for r in rows:
        r['wa'] = _wa_link(
            r['student'].phone,
            f'Salam! Academor-dan yazırıq. {r["student"].full_name} üzrə {r["balance"]} AZN ödəniş gözlənilir.',
        )
    total = sum((r['balance'] for r in rows), crm.ZERO)
    overdue = sum((r['overdue_amount'] for r in rows), crm.ZERO)
    return render(request, 'crm/debts.html', _ctx(request, 'debts', rows=rows, total=total, overdue=overdue))


@crm_view
@require_POST
def charges_generate(request):
    period = crm.parse_month(request.POST.get('month'))
    res = crm.generate_monthly_charges(period, user=request.user)
    msg = f'{crm.month_label(period)}: {res["created"]} yeni hesab yazıldı'
    if res['skipped']:
        msg += f', {res["skipped"]} artıq var idi'
    messages.success(request, msg + '.')
    if res['no_fee_groups']:
        messages.warning(request, 'Aylıq haqqı yazılmayan qruplar: ' + ', '.join(g.name for g in res['no_fee_groups']))
    return redirect(f"{reverse('crm:payments')}?month={period:%Y-%m}")


# ---------------------------------------------------------------- groups & attendance
@crm_view
def groups(request):
    if request.method == 'POST':
        group = get_object_or_404(StudyGroup, pk=request.POST.get('group'))
        raw = (request.POST.get('monthly_fee') or '').replace(',', '.').strip()
        try:
            group.monthly_fee = Decimal(raw) if raw else None
        except InvalidOperation:
            messages.error(request, 'Məbləğ düzgün deyil.')
            return redirect('crm:groups')
        group.save(update_fields=['monthly_fee'])
        messages.success(request, f'{group.name}: aylıq haqq yeniləndi.')
        return redirect('crm:groups')
    start, end = crm.month_range(timezone.localdate())
    rate_rows = (
        Attendance.objects.filter(session_date__range=(start, end), student__isnull=False)
        .values('group_id', 'status').annotate(n=Count('id'))
    )
    by_group = {}
    for row in rate_rows:
        by_group.setdefault(row['group_id'], {'present': 0, 'late': 0, 'absent': 0})[row['status']] = row['n']
    rows = []
    for g in crm.billable_groups().select_related('teacher__user').annotate(n=Count('students', distinct=True)).order_by('name'):
        c = by_group.get(g.pk, {'present': 0, 'late': 0, 'absent': 0})
        rows.append({
            'group': g, 'students': g.n, 'rate': crm._rate(c['present'], c['late'], c['absent']),
            'expected': (g.monthly_fee or 0) * g.n, 'fill': round(g.n * 100 / g.max_students) if g.max_students else 0,
        })
    expected = sum((r['expected'] for r in rows), crm.ZERO)
    return render(request, 'crm/groups.html', _ctx(request, 'groups', rows=rows, expected=expected))


@crm_view
def attendance(request):
    period = crm.parse_month(request.GET.get('month'))
    ov = crm.attendance_overview(period)
    from portals.utils.admin_teacher_attendance import teacher_month_summaries

    teachers = teacher_month_summaries(period.year, period.month)
    try:
        teacher_url = reverse('admin:portals_attendance_teachers')
    except Exception:
        teacher_url = ''
    return render(request, 'crm/attendance.html', _ctx(
        request, 'attendance', ov=ov, period=period, period_label=crm.month_label(period),
        prev=crm.add_months(period, -1), next=crm.add_months(period, 1), teachers=teachers,
        teacher_url=teacher_url,
    ))


def admin_login(request):
    """The admin login, landing on the CRM dashboard unless a page asked for the login."""
    from django.contrib import admin

    extra = {}
    if 'next' not in request.GET and 'next' not in request.POST:
        crm_url = reverse('crm:dashboard')
        extra['next'] = crm_url  # the form's hidden field
        if request.method == 'POST':
            request.POST = request.POST.copy()
            request.POST['next'] = crm_url
    return admin.site.login(request, extra_context=extra)
