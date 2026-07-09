import logging

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import get_language, gettext as _
from django.views import View

from portals.models import IeltsMockTestAttempt
from portals.utils.customer_mock import (
    customer_can_start_mock,
    customer_has_in_progress_mock,
    get_active_mock_packages,
    get_customer_completed_mock_attempts,
    get_customer_mock_take_url,
    get_missing_customer_mock_sections,
    get_mock_attempt_for_customer,
    serialize_customer_mock_attempt_summary,
    start_customer_mock_test_attempt,
)
from portals.utils.queries import get_customer_profile, serialize_customer
from portals.utils.quiz_stats import compute_mock_average_stats
from portals.views.mixins import CustomerRequiredMixin
from portals.views.views_v1 import _portal_context

logger = logging.getLogger('portals.customer')


class CustomerDashboardView(CustomerRequiredMixin, View):
    template_name = 'portals/customer/dashboard.html'

    def get(self, request):
        profile = get_customer_profile(request.portal_user)
        in_progress = customer_has_in_progress_mock(profile.pk)
        completed_attempts = get_customer_completed_mock_attempts(profile.pk)
        latest = completed_attempts[0] if completed_attempts else None
        mock_attempts = [
            serialize_customer_mock_attempt_summary(attempt)
            for attempt in completed_attempts
        ]
        mock_stats = compute_mock_average_stats(mock_attempts)
        return render(
            request,
            self.template_name,
            _portal_context(
                request,
                customer=serialize_customer(profile),
                in_progress_mock=in_progress,
                mock_stats=mock_stats,
                latest_attempt=(
                    serialize_customer_mock_attempt_summary(latest) if latest else None
                ),
            ),
        )


class CustomerIeltsMockLandingView(CustomerRequiredMixin, View):
    template_name = 'portals/customer/ielts_mock_landing.html'

    def get(self, request):
        profile = get_customer_profile(request.portal_user)
        can_start = customer_can_start_mock(profile.pk)
        missing_sections = get_missing_customer_mock_sections() if can_start else []
        missing_labels = [
            dict(IeltsMockTestAttempt.Section.choices).get(section, section)
            for section in missing_sections
        ]
        return render(
            request,
            self.template_name,
            _portal_context(
                request,
                customer=serialize_customer(profile),
                mock_credits=profile.mock_credits,
                can_start=can_start and not missing_sections,
                has_credits=profile.mock_credits > 0 or customer_has_in_progress_mock(profile.pk),
                missing_sections=missing_labels,
                completed_attempts=[
                    serialize_customer_mock_attempt_summary(attempt)
                    for attempt in get_customer_completed_mock_attempts(profile.pk)
                ],
            ),
        )


class CustomerIeltsMockStartView(CustomerRequiredMixin, View):
    def post(self, request):
        profile = get_customer_profile(request.portal_user)
        if not customer_can_start_mock(profile.pk):
            messages.error(request, _('You have no mock test credits. Purchase a package to continue.'))
            return redirect('portals:customer-mock-packages')

        attempt, error = start_customer_mock_test_attempt(profile.pk)
        if error:
            messages.error(request, error)
            logger.warning('Customer mock start blocked customer_id=%s error=%s', profile.pk, error)
            return redirect('portals:customer-ielts-mock')

        return redirect(get_customer_mock_take_url(attempt, IeltsMockTestAttempt.Section.LISTENING))


class CustomerIeltsMockCompleteView(CustomerRequiredMixin, View):
    template_name = 'portals/student/ielts_mock_complete.html'

    def get(self, request, pk):
        profile = get_customer_profile(request.portal_user)
        attempt = get_mock_attempt_for_customer(profile.pk, pk)
        if not attempt or attempt.status != IeltsMockTestAttempt.Status.COMPLETED:
            raise Http404

        return render(
            request,
            self.template_name,
            _portal_context(
                request,
                mock_attempt=serialize_customer_mock_attempt_summary(attempt),
                mock_back_url=reverse('portals:customer-ielts-mock'),
            ),
        )


class CustomerMockPackagesView(CustomerRequiredMixin, View):
    template_name = 'portals/customer/mock_packages.html'

    def get(self, request):
        profile = get_customer_profile(request.portal_user)
        lang = (get_language() or 'az')[:2]
        packages = [
            {
                'id': pkg.pk,
                'name': pkg.localized_name(lang),
                'credits': pkg.credits,
                'price': pkg.price,
            }
            for pkg in get_active_mock_packages()
        ]
        return render(
            request,
            self.template_name,
            _portal_context(
                request,
                customer=serialize_customer(profile),
                packages=packages,
            ),
        )
