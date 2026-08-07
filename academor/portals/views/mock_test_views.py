import logging

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views import View

from portals.models import IeltsMockTestAttempt, PortalNotification
from portals.utils.ielts_mock_test import (
    get_mock_attempt_for_student,
    get_mock_complete_url,
    get_mock_landing_url,
    get_mock_take_url,
    get_missing_mock_sections,
    get_student_completed_mock_attempts,
    get_student_mock_exam_programs,
    is_valid_mock_program,
    resolve_student_mock_exam_program,
    serialize_mock_attempt_summaries,
    serialize_mock_attempt_summary,
    start_mock_test_attempt,
    student_can_access_mock,
    student_can_access_mock_program,
)
from portals.utils.mock_programs import (
    get_program_first_section,
    get_program_label,
    get_section_label,
)
from portals.utils.queries import get_parent_profile, get_student_profile, get_teacher_profile, serialize_parent
from portals.utils.student_courses import teacher_can_see_quiz_result
from portals.views.mixins import ParentRequiredMixin, StudentRequiredMixin, TeacherRequiredMixin
from portals.views.views_v1 import _parent_student_page, _portal_context

logger = logging.getLogger('portals.mock_test')


def _require_student_program(profile, program: str) -> None:
    if not is_valid_mock_program(program):
        raise Http404
    if program not in get_student_mock_exam_programs(profile.pk):
        raise Http404


class StudentMockPickerView(StudentRequiredMixin, View):
    template_name = 'portals/student/mock_picker.html'

    def get(self, request):
        profile = get_student_profile(request.portal_user)
        programs = get_student_mock_exam_programs(profile.pk)
        if not programs:
            raise Http404
        if len(programs) == 1:
            return redirect('portals:student-mock-landing', program=programs[0])
        return render(
            request,
            self.template_name,
            _portal_context(
                request,
                mock_programs=[
                    {
                        'code': program,
                        'label': get_program_label(program),
                        'landing_url': get_mock_landing_url(program),
                    }
                    for program in programs
                ],
            ),
        )


class StudentMockLandingView(StudentRequiredMixin, View):
    template_name = 'portals/student/mock_landing.html'

    def get(self, request, program: str):
        profile = get_student_profile(request.portal_user)
        _require_student_program(profile, program)

        mock_unlocked = student_can_access_mock_program(profile.pk, program)
        missing_sections = get_missing_mock_sections(profile.pk, program) if mock_unlocked else []
        missing_labels = [
            get_section_label(program, section_key)
            for section_key in missing_sections
        ]
        return render(
            request,
            self.template_name,
            _portal_context(
                request,
                exam_program=program,
                exam_program_label=get_program_label(program),
                mock_unlocked=mock_unlocked,
                can_start=mock_unlocked and not missing_sections,
                missing_sections=missing_labels,
                completed_attempts=serialize_mock_attempt_summaries(
                    get_student_completed_mock_attempts(profile.pk, exam_program=program)
                ),
            ),
        )


class StudentMockStartView(StudentRequiredMixin, View):
    def post(self, request, program: str):
        profile = get_student_profile(request.portal_user)
        _require_student_program(profile, program)
        if not student_can_access_mock_program(profile.pk, program):
            raise Http404

        attempt, error = start_mock_test_attempt(profile.pk, program)
        if error:
            messages.error(request, error)
            logger.warning(
                'Mock test start blocked student_id=%s program=%s error=%s',
                profile.pk,
                program,
                error,
            )
            return redirect('portals:student-mock-landing', program=program)

        first_section = get_program_first_section(program)
        return redirect(get_mock_take_url(attempt, first_section))


class StudentMockCompleteView(StudentRequiredMixin, View):
    template_name = 'portals/student/mock_complete.html'

    def get(self, request, program: str, pk: int):
        profile = get_student_profile(request.portal_user)
        _require_student_program(profile, program)
        attempt = get_mock_attempt_for_student(profile.pk, pk)
        if (
            not attempt
            or attempt.exam_program != program
            or attempt.status != IeltsMockTestAttempt.Status.COMPLETED
        ):
            logger.warning(
                'Mock test complete page denied student_id=%s attempt_id=%s status=%s',
                profile.pk,
                pk,
                getattr(attempt, 'status', None),
            )
            raise Http404

        logger.info('Mock test complete page viewed student_id=%s attempt_id=%s', profile.pk, pk)

        return render(
            request,
            self.template_name,
            _portal_context(
                request,
                exam_program=program,
                exam_program_label=get_program_label(program),
                mock_attempt=serialize_mock_attempt_summary(attempt),
            ),
        )


class StudentIeltsMockLegacyRedirectView(StudentRequiredMixin, View):
    def get(self, request):
        profile = get_student_profile(request.portal_user)
        program = resolve_student_mock_exam_program(profile.pk)
        if program:
            return redirect('portals:student-mock-landing', program=program)
        programs = get_student_mock_exam_programs(profile.pk)
        if programs:
            return redirect('portals:student-mock-picker')
        raise Http404


class ParentMockDetailView(ParentRequiredMixin, View):
    template_name = 'portals/student/mock_complete.html'

    def get(self, request, pk: int):
        profile = get_parent_profile(request.portal_user)
        student, child_ctx = _parent_student_page(request, profile)
        if not get_student_mock_exam_programs(student.pk):
            raise Http404

        attempt = get_mock_attempt_for_student(student.pk, pk)
        if not attempt or attempt.status != IeltsMockTestAttempt.Status.COMPLETED:
            raise Http404

        PortalNotification.objects.filter(
            parent_id=profile.pk,
            ielts_mock_test_id=attempt.pk,
            is_read=False,
        ).update(is_read=True)

        back_url = reverse('portals:parent-scores') + child_ctx.get('student_query', '')
        return render(
            request,
            self.template_name,
            _portal_context(
                request,
                page_eyebrow='Parent',
                page_subtitle=_('Mock test results for your linked student.'),
                parent=serialize_parent(profile),
                student=child_ctx['selected_student'],
                exam_program=attempt.exam_program,
                exam_program_label=get_program_label(attempt.exam_program),
                mock_attempt=serialize_mock_attempt_summary(attempt),
                mock_back_url=back_url,
                score_detail_url_name='portals:parent-score-detail',
                score_detail_url_suffix=child_ctx.get('student_query', ''),
                **child_ctx,
            ),
        )


class TeacherMockDetailView(TeacherRequiredMixin, View):
    template_name = 'portals/teacher/mock_detail.html'

    def get(self, request, pk: int):
        profile = get_teacher_profile(request.portal_user)
        attempt = (
            IeltsMockTestAttempt.objects.filter(pk=pk)
            .select_related(
                'student__user',
                'customer__user',
                'customer__teacher',
                'listening_quiz__category',
                'reading_quiz__category',
                'writing_quiz__category',
                'speaking_quiz__category',
                'math_quiz__category',
                'listening_result',
                'reading_result',
                'writing_result',
                'speaking_result',
                'math_result',
            )
            .first()
        )
        if not attempt or attempt.status != IeltsMockTestAttempt.Status.COMPLETED:
            raise Http404

        if attempt.customer_id:
            visible = attempt.customer.teacher_id == profile.pk
        else:
            visible = any(
                teacher_can_see_quiz_result(profile.pk, attempt.student_id, attempt.quiz_for_section(section))
                for section in attempt.program_section_order()
                if attempt.quiz_for_section(section)
            )
        if not visible:
            raise Http404

        return render(
            request,
            self.template_name,
            _portal_context(
                request,
                exam_program=attempt.exam_program,
                exam_program_label=get_program_label(attempt.exam_program),
                mock_attempt=serialize_mock_attempt_summary(attempt),
                back_url=reverse('portals:teacher-notifications'),
            ),
        )


# Backward-compatible view aliases.
StudentIeltsMockLandingView = StudentIeltsMockLegacyRedirectView


class StudentIeltsMockStartView(StudentRequiredMixin, View):
    def post(self, request):
        profile = get_student_profile(request.portal_user)
        program = resolve_student_mock_exam_program(profile.pk)
        if not program:
            return redirect('portals:student-mock-picker')
        return StudentMockStartView().post(request, program=program)


class StudentIeltsMockCompleteView(StudentRequiredMixin, View):
    def get(self, request, pk: int):
        profile = get_student_profile(request.portal_user)
        attempt = get_mock_attempt_for_student(profile.pk, pk)
        if not attempt:
            raise Http404
        return StudentMockCompleteView().get(request, program=attempt.exam_program, pk=pk)


ParentIeltsMockDetailView = ParentMockDetailView
TeacherIeltsMockDetailView = TeacherMockDetailView
