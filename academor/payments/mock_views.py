from decimal import Decimal

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import get_language, gettext as _
from django.views.decorators.http import require_http_methods

from portals.utils.customer_mock import get_active_mock_packages
from portals.utils.portal_session import is_portal_authenticated
from portals.utils.queries import get_customer_profile, get_portal_role

from .models import Payment
from .views import _is_ajax, _start_payment


def _portal_mock_packages_url():
    return reverse('portals:customer-mock-packages')


@require_http_methods(['POST'])
def payment_start_mock(request, package_id: int):
    if not is_portal_authenticated(request):
        messages.error(request, _('Please log in to purchase a mock test package.'))
        return redirect(reverse('portals:login') + '?next=' + _portal_mock_packages_url())

    if get_portal_role(request.portal_user) != 'customer':
        messages.error(request, _('Only customer accounts can purchase mock test packages here.'))
        return redirect('portals:dashboard')

    profile = get_customer_profile(request.portal_user)
    if not profile:
        messages.error(request, _('Customer profile not found.'))
        return redirect('portals:login')

    package = get_active_mock_packages().filter(pk=package_id).first()
    if not package:
        message = _('This package is not available.')
        if _is_ajax(request):
            return JsonResponse({'success': False, 'message': message}, status=400)
        messages.error(request, message)
        return redirect(_portal_mock_packages_url())

    lang = (get_language() or 'az')[:2]
    description = _('Academor — %(name)s (%(credits)s mock tests)') % {
        'name': package.localized_name(lang),
        'credits': package.credits,
    }
    user = request.portal_user
    payment, result = _start_payment(
        amount=Decimal(package.price),
        description=description,
        mock_package=package,
        customer=profile,
        buyer_name=user.get_username(),
        buyer_email=getattr(user, 'email', '') or '',
        buyer_phone=profile.phone or '',
        contract_language=lang,
        product_type=Payment.ProductType.MOCK_TEST,
    )
    if payment is None:
        message = result.get('error') or _('Order could not be created.')
        if _is_ajax(request):
            return JsonResponse({'success': False, 'message': message}, status=502)
        messages.error(request, message)
        return redirect(_portal_mock_packages_url())

    redirect_url = result['payment_url']
    if _is_ajax(request):
        return JsonResponse({'success': True, 'redirect_url': redirect_url})
    return redirect(redirect_url)
