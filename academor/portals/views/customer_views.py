import logging

from django.shortcuts import redirect, render
from django.utils.translation import get_language
from django.views import View

from portals.utils.customer_mock import (
    build_customer_mock_dashboard_sections,
    get_active_mock_packages_services,
    get_customer_completed_mock_attempts,
    serialize_customer_mock_attempt_summary,
)
from portals.utils.queries import get_customer_profile, serialize_customer
from projects.utils.queries import serialize_project_category_detail
from portals.utils.quiz_stats import build_mock_stats_list
from portals.views.mixins import CustomerRequiredMixin
from portals.views.views_v1 import _portal_context

logger = logging.getLogger('portals.customer')


class CustomerDashboardView(CustomerRequiredMixin, View):
    template_name = 'portals/customer/dashboard.html'

    def get(self, request):
        profile = get_customer_profile(request.portal_user)
        completed_attempts = get_customer_completed_mock_attempts(profile.pk)
        mock_attempts = [
            serialize_customer_mock_attempt_summary(attempt)
            for attempt in completed_attempts
        ]
        return render(
            request,
            self.template_name,
            _portal_context(
                request,
                customer=serialize_customer(profile),
                mock_stats_list=build_mock_stats_list(mock_attempts),
                mock_program_sections=build_customer_mock_dashboard_sections(profile.pk),
            ),
        )


class CustomerMockPackagesView(CustomerRequiredMixin, View):
    template_name = 'portals/customer/mock_packages.html'

    def get(self, request):
        profile = get_customer_profile(request.portal_user)
        lang = (get_language() or 'az')[:2]
        mock_services = []
        for service in get_active_mock_packages_services():
            course = serialize_project_category_detail(service, lang)
            packages = course.get('price_packages') or []
            if not packages:
                continue
            mock_services.append({
                'course': course,
                'packages': packages,
                'exam': (
                    'ielts' if service.ielts_mock_test
                    else 'sat' if service.sat_mock_test
                    else 'mock'
                ),
            })
        return render(
            request,
            self.template_name,
            _portal_context(
                request,
                customer=serialize_customer(profile),
                mock_services=mock_services,
            ),
        )


class CustomerMockPaymentStartView(CustomerRequiredMixin, View):
    """Portal-only mock checkout — skips public contract form."""

    def get(self, request, slug):
        return redirect('portals:customer-mock-packages')

    def post(self, request, slug):
        from payments.views import start_portal_customer_mock_payment

        return start_portal_customer_mock_payment(request, slug)
