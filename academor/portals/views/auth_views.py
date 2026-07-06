from urllib.parse import urlencode, urlparse, urlunparse

from django.contrib import messages
from django.contrib.auth import authenticate
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views import View
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST

from portals.forms import PortalLoginForm
from portals.utils.portal_session import is_portal_authenticated, portal_login, portal_logout
from portals.utils.queries import get_portal_role
from portals.utils.safe_redirect import safe_portal_next_url


def _append_query(url: str, params: dict) -> str:
    parsed = urlparse(url)
    existing = {}
    if parsed.query:
        for part in parsed.query.split('&'):
            if '=' in part:
                key, value = part.split('=', 1)
                existing[key] = value
    existing.update({k: v for k, v in params.items() if v is not None})
    return urlunparse(parsed._replace(query=urlencode(existing)))


def _login_page_url(next_url=''):
    url = reverse('portals:login')
    if next_url:
        return _append_query(url, {'next': next_url})
    return url


def _redirect_after_login(request, next_url=''):
    safe_next = safe_portal_next_url(request, next_url)
    if safe_next:
        return redirect(safe_next)
    return redirect('portals:dashboard')


@method_decorator(ensure_csrf_cookie, name='dispatch')
class PortalLoginView(View):
    """Portal login page and POST handler (portal session only)."""

    template_name = 'portals/login.html'

    def get(self, request):
        next_url = (request.GET.get('next') or '').strip()
        if is_portal_authenticated(request):
            return _redirect_after_login(request, next_url)
        response = render(
            request,
            self.template_name,
            {
                'next': next_url or reverse('portals:dashboard'),
            },
        )
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Vary'] = 'Cookie'
        return response

    def post(self, request):
        form = PortalLoginForm(request.POST)
        next_url = (request.POST.get('next') or '').strip()
        fallback = _login_page_url(next_url)

        if not form.is_valid():
            messages.error(request, _('Please enter your username and password.'))
            return redirect(fallback)

        user = authenticate(
            request,
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password'],
        )
        if user is None:
            messages.error(request, _('Invalid username or password.'))
            request.session['portal_login_username'] = form.cleaned_data['username']
            return redirect(fallback)

        if not get_portal_role(user):
            messages.error(
                request,
                _('This account cannot access the portal. Staff and admin users must use the admin panel.'),
            )
            return redirect(fallback)

        portal_login(request, user)
        request.session.pop('portal_login_username', None)
        return _redirect_after_login(request, next_url)


class PortalLogoutView(View):
    """Sign out from the portal only — Django admin session stays untouched."""

    def get(self, request):
        return redirect('portals:dashboard')

    @method_decorator(require_POST)
    def post(self, request):
        portal_logout(request)
        return redirect('projects:home-page')
