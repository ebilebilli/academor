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
    get_mock_take_url,
    get_missing_mock_sections,
    get_student_completed_mock_attempts,
    serialize_mock_attempt_summary,
    start_mock_test_attempt,
    student_can_access_ielts_mock,
)
from portals.utils.queries import get_parent_profile, get_student_profile, get_teacher_profile, serialize_parent
from portals.utils.student_courses import teacher_can_see_quiz_result
from portals.views.mixins import ParentRequiredMixin, StudentRequiredMixin, TeacherRequiredMixin
from portals.views.views_v1 import _parent_student_page, _portal_context

logger = logging.getLogger('portals.ielts_mock')


class StudentIeltsMockLandingView(StudentRequiredMixin, View):
    template_name = 'portals/student/ielts_mock_landing.html'

    def get(self, request):
        from portals.utils.student_courses import student_has_course_access

        profile = get_student_profile(request.portal_user)
        if not student_has_course_access(profile.pk, 'ielts'):
            raise Http404

        mock_unlocked = student_can_access_ielts_mock(profile.pk)
        missing_sections = get_missing_mock_sections(profile.pk) if mock_unlocked else []
        missing_labels = [
            dict(IeltsMockTestAttempt.Section.choices).get(section, section)
            for section in missing_sections
        ]
        return render(
            request,
            self.template_name,
            _portal_context(
                request,
                mock_unlocked=mock_unlocked,
                can_start=mock_unlocked and not missing_sections,
                missing_sections=missing_labels,
                completed_attempts=[
                    serialize_mock_attempt_summary(attempt)
                    for attempt in get_student_completed_mock_attempts(profile.pk)
                ],
            ),
        )


class StudentIeltsMockStartView(StudentRequiredMixin, View):
    def post(self, request):
        profile = get_student_profile(request.portal_user)
        if not student_can_access_ielts_mock(profile.pk):
            raise Http404

        attempt, error = start_mock_test_attempt(profile.pk)
        if error:
            messages.error(request, error)
            logger.warning('Mock test start blocked student_id=%s error=%s', profile.pk, error)
            return redirect('portals:student-ielts-mock')

        return redirect(get_mock_take_url(attempt, IeltsMockTestAttempt.Section.LISTENING))


class StudentIeltsMockCompleteView(StudentRequiredMixin, View):
    template_name = 'portals/student/ielts_mock_complete.html'

    def get(self, request, pk):
        profile = get_student_profile(request.portal_user)
        attempt = get_mock_attempt_for_student(profile.pk, pk)
        if not attempt or attempt.status != IeltsMockTestAttempt.Status.COMPLETED:
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
                mock_attempt=serialize_mock_attempt_summary(attempt),
            ),
        )


class ParentIeltsMockDetailView(ParentRequiredMixin, View):
    template_name = 'portals/student/ielts_mock_complete.html'

    def get(self, request, pk):
        from portals.utils.student_courses import student_has_course_access

        profile = get_parent_profile(request.portal_user)
        student, child_ctx = _parent_student_page(request, profile)
        # Past mock results stay visible even when the teacher has locked new starts.
        if not student_has_course_access(student.pk, 'ielts'):
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
                mock_attempt=serialize_mock_attempt_summary(attempt),
                mock_back_url=back_url,
                score_detail_url_name='portals:parent-score-detail',
                score_detail_url_suffix=child_ctx.get('student_query', ''),
                **child_ctx,
            ),
        )


class TeacherIeltsMockDetailView(TeacherRequiredMixin, View):
    template_name = 'portals/teacher/ielts_mock_detail.html'

    def get(self, request, pk):
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
                'listening_result',
                'reading_result',
                'writing_result',
                'speaking_result',
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
                for section in IeltsMockTestAttempt.SECTION_ORDER
                if attempt.quiz_for_section(section)
            )
        if not visible:
            raise Http404

        return render(
            request,
            self.template_name,
            _portal_context(
                request,
                mock_attempt=serialize_mock_attempt_summary(attempt),
                back_url=reverse('portals:teacher-notifications'),
            ),
        )
