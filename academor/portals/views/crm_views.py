"""Academor CRM: leads, students, billing, attendance and groups for the office team.

Staff only (Django staff users). Lives under the secret admin prefix: {ADMIN_URL}crm/.
"""

from __future__ import annotations

import json
from datetime import date
from functools import wraps
from urllib.parse import quote

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count, Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone, translation
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from portals.crm_forms import (
    ChargeForm,
    EnrollmentForm,
    GroupForm,
    LeadForm,
    LeadNoteForm,
    PaymentForm,
    StudentForm,
    TeacherForm,
    new_password,
    save_enrollment,
)
from portals.models import (
    Attendance,
    Enrollment,
    Lead,
    LeadActivity,
    StudentCharge,
    StudentPayment,
    StudentProfile,
    StudyGroup,
    TeacherProfile,
)
from portals.utils import crm

def crm_view(view):
    """Staff only, and always in Azerbaijani (dates like "3 gün əvvəl", labels)."""
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        with translation.override('az'):
            # monthly charges are written on the day they fall due, on the next CRM visit
            crm.sync_charges(user=request.user)
            return view(request, *args, **kwargs)
    return staff_member_required(wrapped)


def _ctx(request, section, **extra):
    open_leads = Lead.objects.filter(status=Lead.Status.NEW).count()
    return {'crm_section': section, 'crm_new_leads': open_leads, 'crm_courses': crm.course_names(), **extra}


def _next_or(request, fallback):
    nxt = request.POST.get('next') or request.GET.get('next') or ''
    if nxt and url_has_allowed_host_and_scheme(nxt, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        return redirect(nxt)
    return redirect(fallback)


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
                if lead.status == Lead.Status.ENROLLED and not lead.student_id:
                    return redirect('crm:lead_convert', pk=lead.pk)
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
    out = {'ok': True, 'status': lead.status}
    if lead.status == Lead.Status.ENROLLED and not lead.student_id:
        out['redirect'] = reverse('crm:lead_convert', args=[lead.pk])
    return JsonResponse(out)


@crm_view
def lead_convert(request, pk):
    """Müraciət → tələbə: create the student and their first course in one step."""
    lead = get_object_or_404(Lead, pk=pk)
    if lead.student_id:
        messages.info(request, 'Bu müraciət artıq tələbəyə bağlanıb.')
        return redirect('crm:student', pk=lead.student_id)
    s_form = StudentForm(request.POST or None, prefix='s', initial={
        'full_name': lead.full_name, 'phone': lead.phone, 'email': lead.email,
    })
    e_form = EnrollmentForm(request.POST or None, prefix='e', initial={'course': lead.interest})
    if request.method == 'POST' and s_form.is_valid() and e_form.is_valid():
        with transaction.atomic():
            student = s_form.save()
            e_form.student = student
            save_enrollment(e_form, student, user=request.user, lead=lead)
            old = lead.status
            lead.student, lead.status = student, Lead.Status.ENROLLED
            lead.save(update_fields=['student', 'status', 'updated_at'])
            LeadActivity.objects.create(
                lead=lead, author=request.user, kind=LeadActivity.Kind.STATUS,
                text=f'{Lead.Status(old).label} → Tələbə oldu: {student.full_name}',
            )
        messages.success(request, f'{student.full_name} tələbə kimi qeydiyyata alındı.')
        return redirect('crm:student', pk=student.pk)
    return render(request, 'crm/student_form.html', _ctx(
        request, 'leads', s_form=s_form, e_form=e_form, lead=lead, title='Tələbəyə çevir',
        back=reverse('crm:lead', args=[lead.pk]),
    ))


# ---------------------------------------------------------------- students
STUDENT_TABS = (
    ('active', 'Aktiv'), ('waiting', 'Gözləyir'), ('left', 'Ayrılanlar'), ('none', 'Kurssuz'), ('all', 'Hamısı'),
)


@crm_view
def students(request):
    q = (request.GET.get('q') or '').strip()
    group_id = request.GET.get('group') or ''
    teacher_id = request.GET.get('teacher') or ''
    tab = request.GET.get('tab') or 'active'
    only = request.GET.get('only') or ''
    qs = StudentProfile.objects.select_related('user').order_by('user__username')
    if q:
        qs = qs.filter(Q(user__username__icontains=q) | Q(user__first_name__icontains=q)
                       | Q(user__last_name__icontains=q) | Q(phone__icontains=q))
    if group_id:
        qs = qs.filter(Q(groups__pk=group_id) | Q(crm_enrollments__group_id=group_id))
    if teacher_id:
        qs = qs.filter(crm_enrollments__teacher_id=teacher_id)
    if tab == 'active':
        qs = qs.filter(crm_enrollments__status=Enrollment.Status.ACTIVE)
    elif tab == 'waiting':
        qs = qs.filter(crm_enrollments__status=Enrollment.Status.WAITING)
    elif tab == 'left':
        qs = qs.filter(crm_enrollments__status__in=(Enrollment.Status.LEFT, Enrollment.Status.FINISHED)).exclude(
            crm_enrollments__status=Enrollment.Status.ACTIVE)
    elif tab == 'none':
        qs = qs.filter(crm_enrollments__isnull=True)
    bal = crm.balances()
    start, end = crm.month_range(timezone.localdate())
    att = crm.attendance_by_student(start, end)
    if only == 'debt':
        qs = qs.filter(pk__in=[sid for sid, b in bal.items() if b.debt > 0])
    elif only == 'risk':
        qs = qs.filter(pk__in=[sid for sid, v in att.items() if v['rate'] is not None and v['rate'] < 75])
    page = Paginator(qs.distinct(), 40).get_page(request.GET.get('page'))
    ids = [st.pk for st in page]
    enrollments = {}
    for e in Enrollment.objects.filter(student_id__in=ids).select_related('teacher__user', 'group'):
        enrollments.setdefault(e.student_id, []).append(e)
    rows = []
    for st in page:
        es = enrollments.get(st.pk, [])
        live = [e for e in es if e.status in (Enrollment.Status.ACTIVE, Enrollment.Status.WAITING)]
        shown = live or es
        dues = [e.next_due_date for e in live if e.next_due_date]
        rows.append({
            'student': st, 'balance': bal.get(st.pk, crm.EMPTY_BALANCE), 'att': att.get(st.pk),
            'enrollments': shown, 'fee': sum((e.monthly_fee for e in live if e.status == 'active'), crm.ZERO),
            'next_due': min(dues) if dues else None,
        })
    counts = dict(Enrollment.objects.values_list('status').annotate(n=Count('student_id', distinct=True)))
    counts['none'] = StudentProfile.objects.filter(crm_enrollments__isnull=True).count()
    counts['left'] = counts.get('left', 0) + counts.get('finished', 0)
    counts['all'] = StudentProfile.objects.count()
    tabs = [{'value': v, 'label': l, 'n': counts.get(v, 0)} for v, l in STUDENT_TABS]
    return render(request, 'crm/students.html', _ctx(
        request, 'students', page=page, rows=rows, q=q, group_id=group_id, teacher_id=teacher_id, only=only,
        tab=tab, tabs=tabs, groups=crm.billable_groups().order_by('name'),
        teachers=TeacherProfile.objects.select_related('user').order_by('user__username'),
    ))


@crm_view
def student_new(request):
    s_form = StudentForm(request.POST or None, prefix='s')
    e_form = EnrollmentForm(request.POST or None, prefix='e', initial={'group': request.GET.get('group')})
    if request.method == 'POST' and s_form.is_valid() and e_form.is_valid():
        with transaction.atomic():
            student = s_form.save()
            e_form.student = student
            save_enrollment(e_form, student, user=request.user)
        messages.success(request, f'{student.full_name} əlavə olundu.')
        if 'pay' in request.POST:
            return redirect(f"{reverse('crm:payment_new')}?student={student.pk}")
        return redirect('crm:student', pk=student.pk)
    return render(request, 'crm/student_form.html', _ctx(
        request, 'students', s_form=s_form, e_form=e_form, title='Yeni tələbə', back=reverse('crm:students'),
    ))


@crm_view
def student_edit(request, pk):
    student = get_object_or_404(StudentProfile.objects.select_related('user'), pk=pk)
    form = StudentForm(request.POST or None, prefix='s', student=student)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Məlumatlar yeniləndi.')
        return redirect('crm:student', pk=student.pk)
    return render(request, 'crm/student_form.html', _ctx(
        request, 'students', s_form=form, title='Tələbə məlumatları', student=student,
        back=reverse('crm:student', args=[student.pk]),
    ))


@crm_view
def enrollment_new(request, student_pk):
    student = get_object_or_404(StudentProfile.objects.select_related('user'), pk=student_pk)
    form = EnrollmentForm(request.POST or None, prefix='e', student=student)
    if request.method == 'POST' and form.is_valid():
        e = save_enrollment(form, student, user=request.user)
        messages.success(request, f'{e.course} kursu əlavə olundu.')
        return redirect('crm:student', pk=student.pk)
    return render(request, 'crm/enrollment_form.html', _ctx(
        request, 'students', form=form, student=student, title='Kurs əlavə et',
    ))


@crm_view
def enrollment_edit(request, pk):
    e = get_object_or_404(Enrollment.objects.select_related('student__user'), pk=pk)
    form = EnrollmentForm(request.POST or None, prefix='e', instance=e, student=e.student)
    if request.method == 'POST' and form.is_valid():
        e = save_enrollment(form, e.student, user=request.user)
        messages.success(request, f'{e.course}: yadda saxlanıldı.')
        return redirect('crm:student', pk=e.student_id)
    return render(request, 'crm/enrollment_form.html', _ctx(
        request, 'students', form=form, student=e.student, enrollment=e, title=e.course,
    ))


@crm_view
def student_detail(request, pk):
    return _student_page(request, pk)


def _student_page(request, pk, new_password_value=None):
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
    enrollments = list(student.crm_enrollments.select_related('teacher__user', 'group'))
    for e in enrollments:
        e.debt = ledger['debt_by_enrollment'].get(e.pk, crm.ZERO)
    live = [e for e in enrollments if e.status == Enrollment.Status.ACTIVE]
    first = live[0] if live else None
    pay_form = PaymentForm(initial={
        'student': student, 'enrollment': first,
        'amount': (first.debt or first.monthly_fee) if first else None,
        'teacher': first.teacher_id if first else None,
        'teacher_percent': first.teacher_percent if first else None,
        'is_new_customer': not ledger['payments'],
    })
    pay_form.fields['enrollment'].queryset = student.crm_enrollments.select_related('teacher__user')
    charge_form = ChargeForm(initial={'student': student})
    charge_form.fields['enrollment'].queryset = student.crm_enrollments.all()
    debt_text = (
        f'Salam! Academor-dan yazırıq. {student.full_name} üzrə {ledger["balance"]} AZN '
        f'ödəniş gözlənilir. Sualınız olarsa, bizə yazın.'
    )
    return render(request, 'crm/student_detail.html', _ctx(
        request, 'students', student=student, ledger=ledger, marks=marks[:40], summary=summary, rate=rate,
        enrollments=enrollments, pay_form=pay_form, charge_form=charge_form, leads=student.crm_leads.all()[:5],
        wa=_wa_link(student.phone, debt_text if ledger['balance'] > 0 else ''),
        new_password=new_password_value,
    ))


@crm_view
@require_POST
def student_password(request, pk):
    """Give the student a fresh portal password, shown once on this response only."""
    student = get_object_or_404(StudentProfile.objects.select_related('user'), pk=pk)
    password = new_password()
    student.user.set_password(password)
    student.user.save(update_fields=['password'])
    return _student_page(request, pk, new_password_value=password)


# ---------------------------------------------------------------- billing
@crm_view
def payments(request):
    period = crm.parse_month(request.GET.get('month'))
    start, end = crm.month_range(period)
    method = request.GET.get('method') or ''
    qs = StudentPayment.objects.filter(paid_at__range=(start, end)).select_related(
        'student__user', 'received_by', 'teacher__user',
    )
    if method:
        qs = qs.filter(method=method)
    month_qs = StudentPayment.objects.filter(paid_at__range=(start, end))
    by_method = {row['method']: row['s'] for row in month_qs.values('method').annotate(s=Sum('amount'))}
    money = crm._money_totals(month_qs)
    total = money['revenue']
    billed = StudentCharge.objects.filter(is_cancelled=False, period=period).aggregate(s=Sum('amount'))['s'] or crm.ZERO
    online = crm.online_payments_by_month(period).get(period, crm.ZERO)
    methods = [
        {'value': v, 'label': l, 'sum': by_method.get(v, crm.ZERO),
         'pct': float(by_method.get(v, 0) / total * 100) if total else 0}
        for v, l in StudentPayment.Method.choices
    ]
    no_fee = Enrollment.objects.filter(status=Enrollment.Status.ACTIVE, monthly_fee=0).select_related('student__user')[:12]
    return render(request, 'crm/payments.html', _ctx(
        request, 'payments', period=period, period_label=crm.month_label(period),
        prev=crm.add_months(period, -1), next=crm.add_months(period, 1),
        payments=qs[:400], total=total, money=money, billed=billed, online=online, methods=methods, method=method,
        method_choices=StudentPayment.Method.choices, revenue=crm.revenue_series(6), no_fee=no_fee,
        upcoming=crm.upcoming_dues(7),
    ))


def _payment_form_page(request, form, title, pay=None):
    return render(request, 'crm/payment_form.html', _ctx(
        request, 'payments', form=form, title=title, pay=pay,
        enrollment_options=form.enrollment_options() if hasattr(form, 'enrollment_options') else [],
    ))


@crm_view
def payment_new(request):
    student_id = request.GET.get('student')
    initial = {'student': student_id}
    if student_id:
        e = Enrollment.objects.filter(student_id=student_id, status=Enrollment.Status.ACTIVE).first()
        if e:
            initial.update(enrollment=e, amount=e.monthly_fee or None, teacher=e.teacher_id,
                           teacher_percent=e.teacher_percent)
        initial['is_new_customer'] = not StudentPayment.objects.filter(student_id=student_id).exists()
    form = PaymentForm(request.POST or None, initial=initial)
    if request.method == 'POST' and form.is_valid():
        pay = form.save(commit=False)
        pay.received_by = request.user
        pay.save()
        messages.success(request, f'{pay.amount} AZN ödəniş qeydə alındı (qəbz {pay.receipt_number}).')
        if request.POST.get('next'):
            return _next_or(request, 'crm:payments')
        return redirect('crm:payment_receipt', pk=pay.pk)
    return _payment_form_page(request, form, 'Ödəniş qəbul et')


@crm_view
def payment_edit(request, pk):
    pay = get_object_or_404(StudentPayment, pk=pk)
    form = PaymentForm(request.POST or None, instance=pay)
    if request.method == 'POST':
        if 'delete' in request.POST:
            student_id = pay.student_id
            pay.delete()
            messages.info(request, 'Ödəniş silindi.')
            return redirect('crm:student', pk=student_id)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ödəniş yeniləndi.')
            return redirect('crm:student', pk=pay.student_id)
    return _payment_form_page(request, form, f'Ödəniş {pay.receipt_number}', pay=pay)


@crm_view
def charge_new(request):
    form = ChargeForm(request.POST or None, initial={'student': request.GET.get('student')})
    if request.method == 'POST' and form.is_valid():
        ch = form.save(commit=False)
        ch.created_by = request.user
        ch.group = ch.enrollment.group if ch.enrollment_id else None
        ch.save()
        messages.success(request, f'{ch.amount} AZN hesab yazıldı.')
        if request.POST.get('next'):
            return _next_or(request, 'crm:payments')
        return redirect('crm:student', pk=ch.student_id)
    return render(request, 'crm/payment_form.html', _ctx(request, 'payments', form=form, title='Hesab yaz'))


@crm_view
@require_POST
def charge_cancel(request, pk):
    ch = get_object_or_404(StudentCharge, pk=pk)
    ch.is_cancelled = True
    ch.save(update_fields=['is_cancelled'])
    messages.info(request, 'Hesab ləğv edildi. Bu ay üçün yenidən yazılmayacaq.')
    return redirect('crm:student', pk=ch.student_id)


@crm_view
def payment_receipt(request, pk):
    pay = get_object_or_404(StudentPayment.objects.select_related('student__user', 'received_by', 'teacher__user'), pk=pk)
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
    return render(request, 'crm/debts.html', _ctx(
        request, 'debts', rows=rows, total=total, overdue=overdue, upcoming=crm.upcoming_dues(7),
    ))


# ---------------------------------------------------------------- teachers & reports
@crm_view
def teachers(request):
    period = crm.parse_month(request.GET.get('month'))
    if request.method == 'POST':
        teacher = get_object_or_404(TeacherProfile, pk=request.POST.get('teacher'))
        start, end = crm.month_range(crm.parse_month(request.POST.get('month')))
        qs = StudentPayment.objects.filter(teacher=teacher, teacher_status=StudentPayment.TeacherStatus.PENDING)
        if request.POST.get('scope') != 'all':
            qs = qs.filter(paid_at__range=(start, end))
        else:
            qs = qs.filter(paid_at__lte=end)
        total = qs.aggregate(s=Sum('teacher_amount'))['s'] or crm.ZERO
        n = qs.update(teacher_status=StudentPayment.TeacherStatus.PAID, teacher_paid_at=timezone.localdate())
        messages.success(request, f'{teacher.full_name}: {n} ödəniş üzrə {total} AZN ödənildi kimi qeyd olundu.')
        return redirect(f"{reverse('crm:teachers')}?month={start:%Y-%m}")
    rows = crm.teacher_payouts(period)
    open_id = request.GET.get('t')
    start, end = crm.month_range(period)
    details = {}
    for p in StudentPayment.objects.filter(paid_at__range=(start, end), teacher__isnull=False).select_related('student__user').order_by('paid_at'):
        details.setdefault(p.teacher_id, []).append(p)
    for r in rows:
        r['payments'] = details.get(r['teacher'].pk, [])
    known = {r['teacher'].pk for r in rows}
    idle = TeacherProfile.objects.exclude(pk__in=known).select_related('user').annotate(
        n=Count('crm_enrollments', filter=Q(crm_enrollments__status=Enrollment.Status.ACTIVE)),
    ).order_by('user__username')
    totals = {
        k: sum((r[k] for r in rows), crm.ZERO) for k in ('revenue', 'tcost', 'paid', 'pending', 'older_pending')
    }
    return render(request, 'crm/teachers.html', _ctx(
        request, 'teachers', rows=rows, idle=idle, totals=totals, period=period,
        period_label=crm.month_label(period), prev=crm.add_months(period, -1), next=crm.add_months(period, 1),
        open_id=open_id, form=TeacherForm(),
    ))


@crm_view
@require_POST
def teacher_new(request):
    form = TeacherForm(request.POST)
    if form.is_valid():
        t = form.save()
        messages.success(request, f'{t.full_name} müəllim kimi əlavə olundu.')
    else:
        messages.error(request, 'Müəllim əlavə olunmadı: ' + '; '.join(e for errs in form.errors.values() for e in errs))
    return _next_or(request, 'crm:teachers')


@crm_view
@require_POST
def payment_teacher_status(request, pk):
    pay = get_object_or_404(StudentPayment, pk=pk)
    status = request.POST.get('status')
    if status in StudentPayment.TeacherStatus.values:
        pay.teacher_status = status
        pay.teacher_paid_at = timezone.localdate() if status == StudentPayment.TeacherStatus.PAID else None
        if status == StudentPayment.TeacherStatus.NONE:
            pay.teacher_amount = crm.ZERO
        elif not pay.teacher_amount and pay.teacher_percent:
            pay.apply_teacher_share()
            pay.teacher_status = status
        pay.save(update_fields=['teacher_status', 'teacher_paid_at', 'teacher_amount'])
    return _next_or(request, 'crm:teachers')


@crm_view
def reports(request):
    period_raw = request.GET.get('month') or ''
    if period_raw == 'all' or not period_raw:
        start, end, period, label = date(2000, 1, 1), date(2100, 1, 1), None, 'Bütün dövr'
    else:
        period = crm.parse_month(period_raw)
        (start, end), label = crm.month_range(period), crm.month_label(period)
    months = crm.monthly_report(12)
    return render(request, 'crm/reports.html', _ctx(
        request, 'reports', months=months, courses=crm.breakdown(start, end, 'course'),
        teachers_rows=crm.breakdown(start, end, 'teacher'), period=period, label=label,
        totals=crm._money_totals(StudentPayment.objects.filter(paid_at__range=(start, end))),
        month_options=[m['month'] for m in reversed(months)],
    ))


# ---------------------------------------------------------------- groups & attendance
@crm_view
def groups(request):
    start, end = crm.month_range(timezone.localdate())
    rate_rows = (
        Attendance.objects.filter(session_date__range=(start, end), student__isnull=False)
        .values('group_id', 'status').annotate(n=Count('id'))
    )
    by_group = {}
    for row in rate_rows:
        by_group.setdefault(row['group_id'], {'present': 0, 'late': 0, 'absent': 0})[row['status']] = row['n']
    fees = {
        r['group_id']: r['s'] for r in Enrollment.objects.filter(status=Enrollment.Status.ACTIVE, group__isnull=False)
        .values('group_id').annotate(s=Sum('monthly_fee'))
    }
    rows = []
    qs = crm.billable_groups().select_related('teacher__user').prefetch_related('schedules').annotate(
        n=Count('students', distinct=True)).order_by('name')
    for g in qs:
        c = by_group.get(g.pk, {'present': 0, 'late': 0, 'absent': 0})
        rows.append({
            'group': g, 'students': g.n, 'rate': crm._rate(c['present'], c['late'], c['absent']),
            'expected': fees.get(g.pk) or crm.ZERO, 'fill': round(g.n * 100 / g.max_students) if g.max_students else 0,
            'slots': list(g.schedules.all()),
        })
    expected = sum((r['expected'] for r in rows), crm.ZERO)
    return render(request, 'crm/groups.html', _ctx(request, 'groups', rows=rows, expected=expected))


@crm_view
def group_form(request, pk=None):
    group = get_object_or_404(StudyGroup, pk=pk) if pk else None
    form = GroupForm(request.POST or None, instance=group, initial={} if group else {'max_students': 4})
    if request.method == 'POST':
        if 'drop_slot' in request.POST and group:
            slot = group.schedules.filter(pk=request.POST.get('drop_slot')).first()
            if slot and slot.attendances.exists():
                messages.error(request, 'Bu dərs saatında davamiyyət qeydləri var — silinə bilməz.')
            elif slot:
                slot.delete()
                messages.info(request, 'Dərs saatı silindi.')
            return redirect('crm:group_edit', pk=group.pk)
        if form.is_valid():
            group = form.save()
            messages.success(request, f'{group.name} yadda saxlanıldı.')
            return redirect('crm:groups')
    members = []
    if group:
        es = {e.student_id: e for e in Enrollment.objects.filter(group=group).select_related('student__user')}
        for st in group.students.select_related('user').order_by('user__username'):
            members.append({'student': st, 'enrollment': es.get(st.pk)})
    return render(request, 'crm/group_form.html', _ctx(
        request, 'groups', form=form, group=group, members=members,
        slots=list(group.schedules.all()) if group else [],
        title=group.name if group else 'Yeni qrup',
    ))


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
