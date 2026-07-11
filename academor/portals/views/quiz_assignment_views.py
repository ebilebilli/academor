import json

from django.http import Http404, JsonResponse
from django.views import View

from portals.utils.queries import get_teacher_profile
from portals.utils.quiz_assignments import (
    set_student_mock_access,
    set_student_quiz_assignment,
)
from portals.utils.teacher_access import get_teacher_student
from portals.views.mixins import TeacherRequiredMixin


def _parse_is_active(payload, fallback=None):
    raw_active = payload.get('is_active', fallback)
    if isinstance(raw_active, bool):
        return raw_active
    return str(raw_active).lower() in ('1', 'true', 'yes', 'on')


class TeacherQuizAssignmentToggleView(TeacherRequiredMixin, View):
    """Activate or deactivate a quiz for one student (teacher portal)."""

    def post(self, request, student_pk, quiz_pk):
        profile = get_teacher_profile(request.portal_user)
        student = get_teacher_student(profile.pk, student_pk)
        if not student:
            raise Http404

        try:
            payload = json.loads(request.body.decode('utf-8') or '{}')
        except json.JSONDecodeError:
            payload = request.POST

        assignment = set_student_quiz_assignment(
            profile.pk,
            student_pk,
            quiz_pk,
            is_active=_parse_is_active(payload, request.POST.get('is_active')),
        )
        if assignment is None:
            return JsonResponse({'ok': False, 'error': 'forbidden'}, status=403)

        return JsonResponse({
            'ok': True,
            'quiz_id': quiz_pk,
            'is_active': assignment.is_active,
        })


class TeacherMockAccessToggleView(TeacherRequiredMixin, View):
    """Activate or deactivate mock access for one student and exam program."""

    def post(self, request, student_pk, program):
        profile = get_teacher_profile(request.portal_user)
        student = get_teacher_student(profile.pk, student_pk)
        if not student:
            raise Http404

        try:
            payload = json.loads(request.body.decode('utf-8') or '{}')
        except json.JSONDecodeError:
            payload = request.POST

        access = set_student_mock_access(
            profile.pk,
            student_pk,
            program,
            is_active=_parse_is_active(payload, request.POST.get('is_active')),
        )
        if access is None:
            return JsonResponse({'ok': False, 'error': 'forbidden'}, status=403)

        return JsonResponse({
            'ok': True,
            'program': program,
            'is_active': access.is_active,
        })
