"""AKIRA reports: build the facts, keep to the budget, ask the AI, store the answer."""

from __future__ import annotations

import logging
from datetime import datetime, time

from django.db import transaction
from django.db.models import Q, Sum
from django.utils import timezone

from portals.akira import analytics, client, prompts
from portals.akira.courses import active_course, course_for_quiz
from portals.akira.skills import question_skill
from portals.models import AkiraMaterial, AkiraReport, AkiraUsage

logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 2
MATERIAL_CHARS = 2000
PUBLIC_COURSE_CODE = 'sat'


# --- facts ------------------------------------------------------------------------


def quiz_result_facts(result) -> dict | None:
    """Facts for a portal quiz attempt, or None when AKIRA does not cover this quiz."""
    quiz = result.quiz
    course = active_course(getattr(course_for_quiz(quiz), 'code', ''))
    if course is None or not quiz.is_variant_quiz or quiz.is_manual_grading:
        return None
    from portals.utils.notifications import _build_variant_breakdown

    questions = {q.pk: q for q in quiz.questions.all()}
    items = []
    for number, row in enumerate(_build_variant_breakdown(result), start=1):
        answered = row.get('selected_index') is not None or bool(row.get('student_answer'))
        status = analytics.CORRECT if row.get('is_correct') else (analytics.WRONG if answered else analytics.BLANK)
        domain, skill = question_skill(questions.get(row['id']))
        items.append(analytics.build_item(number, status, domain, skill))
    if not items:
        return None
    facts = analytics.analyse_section(items, course, duration_sec=result.duration_sec or None, label=quiz.topic)
    facts['time_pressure'] = analytics.time_pressure(facts)
    return {'course_code': course.code, 'facts': facts}


def public_test_facts(rows: list[dict], quizzes: dict, total_scaled: str = '') -> dict | None:
    """Facts for a finished public test. ``rows`` are the result page rows (with ``review``)."""
    sections = []
    for row in rows:
        quiz = quizzes.get(row.get('quiz_id'))
        course = active_course(getattr(course_for_quiz(quiz), 'code', '')) if quiz else None
        review = row.get('review') or []
        if course is None or not review:
            continue
        answerable = [q for q in quiz.questions.all() if q.is_answerable]
        by_position = answerable if len(answerable) == len(review) else []
        items = []
        for position, item in enumerate(review):
            domain, skill = question_skill(by_position[position]) if by_position else ('', '')
            items.append(analytics.build_item(item['number'], item['status'], domain, skill))
        facts = analytics.analyse_section(
            items,
            course,
            duration_sec=row.get('duration_sec') or None,
            scaled=row.get('scaled') or '',
            label=row.get('label') or course.label,
        )
        facts['time_pressure'] = analytics.time_pressure(facts)
        sections.append(facts)
    if not sections:
        return None
    facts = {'sections': sections, 'summary': analytics.headline(sections)}
    if total_scaled:
        facts['total_scaled'] = total_scaled
        facts['total_scale_max'] = 1600
    return {'course_code': PUBLIC_COURSE_CODE, 'facts': facts}


# --- reports ----------------------------------------------------------------------


def report_for_quiz_result(result) -> AkiraReport | None:
    existing = AkiraReport.objects.filter(quiz_result=result).first()
    if existing:
        return existing
    built = quiz_result_facts(result)
    if not built:
        return None
    report, _created = AkiraReport.objects.get_or_create(
        quiz_result=result,
        defaults={
            'kind': AkiraReport.Kind.QUIZ,
            'course_code': built['course_code'],
            'student_id': result.student_id,
            'customer_id': result.customer_id,
            'facts': built['facts'],
        },
    )
    return report


def report_for_public_result(user_result, rows: list[dict], quizzes: dict, total_scaled: str = '') -> AkiraReport | None:
    existing = AkiraReport.objects.filter(user_result=user_result).first()
    if existing:
        return existing
    built = public_test_facts(rows, quizzes, total_scaled)
    if not built:
        return None
    report, _created = AkiraReport.objects.get_or_create(
        user_result=user_result,
        defaults={
            'kind': AkiraReport.Kind.PUBLIC_TEST,
            'course_code': built['course_code'],
            'facts': built['facts'],
        },
    )
    return report


# --- budget -----------------------------------------------------------------------


def _month_start():
    today = timezone.localdate()
    return timezone.make_aware(datetime.combine(today.replace(day=1), time.min))


def month_spend_usd():
    total = AkiraUsage.objects.filter(created_at__gte=_month_start()).aggregate(total=Sum('cost_usd'))['total']
    return total or 0


def _person_reports_this_month(report: AkiraReport) -> int:
    if not report.student_id and not report.customer_id:
        return 0
    person = Q(student_id=report.student_id) if report.student_id else Q(customer_id=report.customer_id)
    return (
        AkiraReport.objects.filter(person, status=AkiraReport.Status.READY, created_at__gte=_month_start())
        .exclude(pk=report.pk)
        .count()
    )


def skip_reason(report: AkiraReport) -> str:
    """Why AKIRA should not write this report now ('' = go ahead)."""
    if not client.is_configured():
        return 'not configured'
    if month_spend_usd() >= client.monthly_budget_usd():
        return 'monthly budget reached'
    if _person_reports_this_month(report) >= client.student_monthly_limit():
        return 'personal monthly limit reached'
    return ''


# --- writing ----------------------------------------------------------------------


def _materials(report: AkiraReport) -> list[dict]:
    facts = report.facts or {}
    sections = facts.get('sections') or [facts]
    codes = {report.course_code}
    weak = set()
    for section in sections:
        weak.update(section.get('weak_domains') or [])
    if report.course_code == PUBLIC_COURSE_CODE:
        codes |= {'sat-math', 'sat-verbal'}
    rows = (
        AkiraMaterial.objects.filter(is_active=True, course_code__in=codes)
        .filter(Q(domain='') | Q(domain__in=weak))
        .order_by('-domain', 'title')[:2]
    )
    return [{'title': m.title, 'content': m.content[:MATERIAL_CHARS]} for m in rows]


def _log_usage(report, completion, ok: bool):
    if completion is None:
        return
    AkiraUsage.objects.create(
        purpose=f'report:{report.kind}',
        model_name=completion.model,
        input_tokens=completion.input_tokens,
        output_tokens=completion.output_tokens,
        cache_read_tokens=completion.cache_read_tokens,
        cache_write_tokens=completion.cache_write_tokens,
        cost_usd=completion.cost_usd,
        ok=ok,
        report=report,
    )


def write_comment(report_id: int) -> AkiraReport:
    """Write the AKIRA comment for a report once; later calls return what is stored."""
    with transaction.atomic():
        report = AkiraReport.objects.select_for_update().get(pk=report_id)
        if report.status in (AkiraReport.Status.READY, AkiraReport.Status.SKIPPED):
            return report
        if report.status == AkiraReport.Status.FAILED and report.attempts >= MAX_ATTEMPTS:
            return report
        reason = skip_reason(report)
        if reason:
            report.status = AkiraReport.Status.SKIPPED
            report.error = reason
            report.save(update_fields=['status', 'error', 'updated_at'])
            return report

        audience = 'visitor' if report.kind == AkiraReport.Kind.PUBLIC_TEST else 'student'
        message = prompts.build_user_message(report.facts, audience=audience, materials=_materials(report))
        report.attempts += 1
        report.model_name = client.model_name()
        try:
            completion = client.complete(prompts.SYSTEM_PROMPT, message)
        except client.AkiraError as exc:
            _log_usage(report, exc.completion, ok=False)
            report.status = AkiraReport.Status.FAILED
            report.error = str(exc)[:255]
            report.save(update_fields=['status', 'error', 'attempts', 'model_name', 'updated_at'])
            return report

        unknown = prompts.unknown_numbers(completion.text, report.facts)
        if unknown:
            _log_usage(report, completion, ok=False)
            report.status = AkiraReport.Status.FAILED
            report.error = f'numbers not in facts: {sorted(unknown)[:5]}'
            report.save(update_fields=['status', 'error', 'attempts', 'model_name', 'updated_at'])
            return report

        _log_usage(report, completion, ok=True)
        report.comment = completion.text
        report.status = AkiraReport.Status.READY
        report.error = ''
        report.save(update_fields=['status', 'comment', 'error', 'attempts', 'model_name', 'updated_at'])
        return report


def report_payload(report: AkiraReport | None) -> dict:
    """What the page script gets back."""
    if report is None:
        return {'status': 'none'}
    data = {'status': report.status, 'id': report.pk}
    if report.status == AkiraReport.Status.READY:
        data['comment'] = report.comment
        data['helpful'] = report.helpful
    elif report.status == AkiraReport.Status.FAILED and report.attempts < MAX_ATTEMPTS:
        data['status'] = AkiraReport.Status.PENDING  # the page may try once more
    return data
