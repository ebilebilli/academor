import logging

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views import View

from portals.utils.customer_mock import (
    build_customer_mock_picker_programs,
    customer_can_start_mock,
    customer_can_view_mock_program,
    customer_has_in_progress_mock,
    get_customer_mock_history_attempts,
    get_customer_mock_take_url,
    get_customer_selectable_mock_programs,
    get_missing_customer_mock_sections,
    get_mock_attempt_for_customer,
    resolve_customer_mock_exam_program,
    serialize_customer_mock_attempt_summary,
    start_customer_mock_test_attempt,
)
from portals.utils.ielts_mock_test import get_program_first_section
from portals.utils.mock_programs import get_program_label, get_section_label, is_valid_mock_program
from portals.utils.queries import get_customer_profile, serialize_customer
from portals.views.mixins import CustomerRequiredMixin
from portals.views.views_v1 import _portal_context

logger = logging.getLogger('portals.customer_mock')


def _require_customer_program(profile, program: str) -> None:
    if not is_valid_mock_program(program):
        logger.warning(
            'Customer mock program 404 customer_id=%s program=%s reason=invalid_program',
            getattr(profile, 'pk', None),
            program,
        )
        raise Http404
    if not customer_can_view_mock_program(profile.pk, program):
        logger.warning(
            'Customer mock program 404 customer_id=%s program=%s reason=not_viewable',
            getattr(profile, 'pk', None),
            program,
        )
        raise Http404


class CustomerMockPickerView(CustomerRequiredMixin, View):
    template_name = 'portals/customer/mock_picker.html'

    def get(self, request):
        profile = get_customer_profile(request.portal_user)
        mock_programs = build_customer_mock_picker_programs(profile.pk)
        logger.info(
            'Customer mock picker customer_id=%s programs=%s',
            profile.pk,
            [row['code'] for row in mock_programs],
        )
        if len(mock_programs) == 1:
            return redirect('portals:customer-mock-landing', program=mock_programs[0]['code'])
        return render(
            request,
            self.template_name,
            _portal_context(
                request,
                customer=serialize_customer(profile),
                mock_programs=mock_programs,
            ),
        )


class CustomerMockHistoryView(CustomerRequiredMixin, View):
    template_name = 'portals/customer/mock_history.html'

    def get(self, request):
        profile = get_customer_profile(request.portal_user)
        history_attempts = [
            serialize_customer_mock_attempt_summary(attempt)
            for attempt in get_customer_mock_history_attempts(profile.pk, limit=50)
        ]
        return render(
            request,
            self.template_name,
            _portal_context(
                request,
                customer=serialize_customer(profile),
                completed_attempts=history_attempts,
            ),
        )


class CustomerMockLandingView(CustomerRequiredMixin, View):
    template_name = 'portals/customer/mock_landing.html'

    def get(self, request, program: str):
        profile = get_customer_profile(request.portal_user)
        _require_customer_program(profile, program)

        can_start = customer_can_start_mock(profile.pk, program)
        missing_sections = get_missing_customer_mock_sections(exam_program=program) if can_start else []
        missing_labels = [
            get_section_label(program, section, translate=False)
            for section in missing_sections
        ]
        program_credits = profile.mock_credits_for_program(program)
        logger.info(
            'Customer mock landing customer_id=%s program=%s credits=%s can_start=%s '
            'missing_sections=%s',
            profile.pk,
            program,
            program_credits,
            can_start and not missing_sections,
            missing_sections,
        )
        return render(
            request,
            self.template_name,
            _portal_context(
                request,
                customer=serialize_customer(profile),
                exam_program=program,
                exam_program_label=get_program_label(program),
                program_credits=program_credits,
                can_start=can_start and not missing_sections,
                has_credits=program_credits > 0 or customer_has_in_progress_mock(profile.pk, exam_program=program),
                missing_sections=missing_labels,
                completed_attempts=[
                    serialize_customer_mock_attempt_summary(attempt)
                    for attempt in get_customer_mock_history_attempts(
                        profile.pk,
                        exam_program=program,
                    )
                ],
            ),
        )


class CustomerMockStartView(CustomerRequiredMixin, View):
    def post(self, request, program: str):
        profile = get_customer_profile(request.portal_user)
        _require_customer_program(profile, program)
        if not customer_can_start_mock(profile.pk, program):
            logger.warning(
                'Customer mock start blocked customer_id=%s program=%s reason=no_credits '
                'ielts_credits=%s sat_credits=%s',
                profile.pk,
                program,
                profile.ielts_mock_credits,
                profile.sat_mock_credits,
            )
            messages.error(request, _('You have no mock test credits. Purchase a package to continue.'))
            return redirect('portals:customer-mock-packages')

        missing_sections = get_missing_customer_mock_sections(exam_program=program)
        if missing_sections:
            logger.warning(
                'Customer mock start missing section quizzes customer_id=%s program=%s '
                'missing_sections=%s',
                profile.pk,
                program,
                missing_sections,
            )

        attempt, error = start_customer_mock_test_attempt(profile.pk, program)
        if error:
            messages.error(request, error)
            logger.warning(
                'Customer mock start blocked customer_id=%s program=%s error=%s',
                profile.pk,
                program,
                error,
            )
            return redirect('portals:customer-mock-landing', program=program)

        first_section = get_program_first_section(program)
        take_url = get_customer_mock_take_url(attempt, first_section)
        logger.info(
            'Customer mock start ok customer_id=%s program=%s attempt_id=%s '
            'first_section=%s take_url=%s section_quizzes=%s',
            profile.pk,
            program,
            attempt.pk,
            first_section,
            take_url,
            {
                section: getattr(attempt.quiz_for_section(section), 'pk', None)
                for section in attempt.program_section_order()
            },
        )
        return redirect(take_url)


class CustomerMockCompleteView(CustomerRequiredMixin, View):
    template_name = 'portals/student/mock_complete.html'

    def get(self, request, program: str, pk: int):
        profile = get_customer_profile(request.portal_user)
        _require_customer_program(profile, program)
        attempt = get_mock_attempt_for_customer(profile.pk, pk)
        if not attempt or attempt.exam_program != program:
            raise Http404

        return render(
            request,
            self.template_name,
            _portal_context(
                request,
                exam_program=program,
                exam_program_label=get_program_label(program),
                mock_attempt=serialize_customer_mock_attempt_summary(attempt),
                mock_back_url=reverse('portals:customer-mock-history'),
                score_detail_url_name='portals:customer-score-detail',
            ),
        )


class CustomerIeltsMockLegacyRedirectView(CustomerRequiredMixin, View):
    def get(self, request):
        profile = get_customer_profile(request.portal_user)
        program = resolve_customer_mock_exam_program(profile.pk)
        if program:
            return redirect('portals:customer-mock-landing', program=program)
        programs = get_customer_selectable_mock_programs(profile.pk)
        if programs:
            return redirect('portals:customer-mock-picker')
        raise Http404


class CustomerIeltsMockStartLegacyView(CustomerRequiredMixin, View):
    def post(self, request):
        profile = get_customer_profile(request.portal_user)
        if not customer_can_start_mock(profile.pk):
            messages.error(request, _('You have no mock test credits. Purchase a package to continue.'))
            return redirect('portals:customer-mock-packages')
        program = resolve_customer_mock_exam_program(profile.pk)
        if not program:
            return redirect('portals:customer-mock-picker')
        return CustomerMockStartView().post(request, program=program)


class CustomerIeltsMockCompleteLegacyView(CustomerRequiredMixin, View):
    def get(self, request, pk: int):
        profile = get_customer_profile(request.portal_user)
        attempt = get_mock_attempt_for_customer(profile.pk, pk)
        if not attempt:
            raise Http404
        return CustomerMockCompleteView().get(
            request,
            program=attempt.exam_program,
            pk=pk,
        )
