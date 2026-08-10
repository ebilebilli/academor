import json

from django.http import Http404, JsonResponse
from django.views import View

from portals.utils.queries import get_teacher_profile
from portals.utils.quiz_assignments import (
    set_student_mock_access,
    set_student_quiz_assignment,
    set_student_quiz_assignments,
)
from portals.utils.teacher_access import get_teacher_student
from portals.views.mixins import TeacherRequiredMixin

BULK_QUIZ_LIMIT = 2000


def _parse_is_active(payload, fallback=None):
    raw_active = payload.get('is_active', fallback)
    if isinstance(raw_active, bool):
        return raw_active
    return str(raw_active).lower() in ('1', 'true', 'yes', 'on')


def _parse_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _read_payload(request):
    try:
        return json.loads(request.body.decode('utf-8') or '{}')
    except (json.JSONDecodeError, UnicodeDecodeError):
        return request.POST


class TeacherQuizAssignmentToggleView(TeacherRequiredMixin, View):
    """Activate or deactivate a quiz for one student (teacher portal)."""

    def post(self, request, student_pk, quiz_pk):
        profile = get_teacher_profile(request.portal_user)
        student = get_teacher_student(profile.pk, student_pk)
        if not student:
            raise Http404

        payload = _read_payload(request)
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


class TeacherQuizAssignmentBulkView(TeacherRequiredMixin, View):
    """Activate or deactivate a whole quiz category for one student in one call."""

    def post(self, request, student_pk):
        profile = get_teacher_profile(request.portal_user)
        if not get_teacher_student(profile.pk, student_pk):
            raise Http404

        payload = _read_payload(request)
        category_id = _parse_int(payload.get('category_id'))
        raw_quiz_ids = payload.get('quiz_ids')
        quiz_ids = None
        if raw_quiz_ids is not None:
            if isinstance(raw_quiz_ids, str):
                raw_quiz_ids = [part for part in raw_quiz_ids.split(',') if part.strip()]
            quiz_ids = [
                parsed
                for parsed in (_parse_int(value) for value in raw_quiz_ids)
                if parsed is not None
            ][:BULK_QUIZ_LIMIT]
        if category_id is None and quiz_ids is None:
            return JsonResponse({'ok': False, 'error': 'nothing_selected'}, status=400)

        is_active = _parse_is_active(payload, request.POST.get('is_active'))
        raw_general = payload.get('general_only', request.POST.get('general_only'))
        raw_program = payload.get('program_flagged_only', request.POST.get('program_flagged_only'))
        general_only = False if raw_general is None else _parse_is_active({'is_active': raw_general}, False)
        program_flagged_only = (
            False if raw_program is None else _parse_is_active({'is_active': raw_program}, False)
        )
        updated_ids = set_student_quiz_assignments(
            profile.pk,
            student_pk,
            is_active=is_active,
            category_id=category_id,
            quiz_ids=quiz_ids,
            general_only=general_only,
            program_flagged_only=program_flagged_only,
        )
        if updated_ids is None:
            return JsonResponse({'ok': False, 'error': 'forbidden'}, status=403)

        return JsonResponse({
            'ok': True,
            'is_active': is_active,
            'quiz_ids': updated_ids,
            'updated': len(updated_ids),
        })


class TeacherMockAccessToggleView(TeacherRequiredMixin, View):
    """Activate or deactivate mock access for one student and exam program."""

    def post(self, request, student_pk, program):
        profile = get_teacher_profile(request.portal_user)
        student = get_teacher_student(profile.pk, student_pk)
        if not student:
            raise Http404

        payload = _read_payload(request)
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
