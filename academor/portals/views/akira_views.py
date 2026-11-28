"""AKIRA endpoints for the portal: the page asks for the comment after it has rendered."""

import json

from django.http import Http404, JsonResponse
from django.views import View

from portals.akira import service
from portals.models import AkiraReport, QuizResult
from portals.utils.notifications import (
    customer_can_view_quiz_result,
    is_quiz_result_published,
    parent_can_view_quiz_result,
    student_can_view_quiz_result,
)
from portals.utils.queries import get_portal_role
from portals.utils.student_courses import teacher_can_review_quiz_result
from portals.views.mixins import PortalLoginRequiredMixin, _portal_profile_for_role


def can_view_result(role: str, profile, result: QuizResult) -> bool:
    if profile is None:
        return False
    if role == 'student':
        return student_can_view_quiz_result(profile.pk, result)
    if role == 'teacher':
        return is_quiz_result_published(result) and teacher_can_review_quiz_result(profile.pk, result)
    if role == 'parent':
        return parent_can_view_quiz_result(profile.pk, result)
    if role == 'customer':
        return customer_can_view_quiz_result(profile.pk, result)
    return False


def _body(request) -> dict:
    try:
        data = json.loads(request.body or b'{}')
    except ValueError:
        return {}
    return data if isinstance(data, dict) else {}


class AkiraQuizResultView(PortalLoginRequiredMixin, View):
    """POST {} writes (or returns) the comment; POST {"helpful": true|false} stores the reader's vote."""

    def post(self, request, result_pk):
        result = QuizResult.objects.select_related('quiz__category').filter(pk=result_pk).first()
        role = get_portal_role(request.portal_user)
        profile = _portal_profile_for_role(request.portal_user, role)
        if result is None or not can_view_result(role, profile, result):
            raise Http404
        report = service.report_for_quiz_result(result)
        if report is None:
            return JsonResponse(service.report_payload(None))
        data = _body(request)
        if 'helpful' in data and role in ('student', 'customer'):
            AkiraReport.objects.filter(pk=report.pk).update(helpful=bool(data['helpful']))
            report.refresh_from_db()
            return JsonResponse(service.report_payload(report))
        report = service.write_comment(report.pk)
        return JsonResponse(service.report_payload(report))
