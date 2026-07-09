from urllib.parse import quote
import json

from django.shortcuts import redirect
from django.urls import reverse

from portals.utils.portal_session import is_portal_authenticated, portal_logout
from portals.utils.queries import (
    get_customer_profile,
    get_parent_profile,
    get_portal_role,
    get_student_profile,
    get_teacher_profile,
)


def _portal_login_redirect(request):
    next_path = quote(request.get_full_path(), safe='')
    login = reverse('portals:login')
    return redirect(f'{login}?next={next_path}')


def _portal_profile_for_role(user, role):
    if role == 'teacher':
        return get_teacher_profile(user)
    if role == 'student':
        return get_student_profile(user)
    if role == 'parent':
        return get_parent_profile(user)
    if role == 'customer':
        return get_customer_profile(user)
    return None


def _clear_stale_portal_session(request):
    """Session user id present but profile row gone — drop session and send to login."""
    portal_logout(request)
    return _portal_login_redirect(request)


class PortalLoginRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not is_portal_authenticated(request):
            return _portal_login_redirect(request)
        return super().dispatch(request, *args, **kwargs)


class PortalRoleRequiredMixin(PortalLoginRequiredMixin):
    required_role = None

    def dispatch(self, request, *args, **kwargs):
        if not is_portal_authenticated(request):
            return _portal_login_redirect(request)
        role = get_portal_role(request.portal_user)
        if role != self.required_role:
            return redirect('portals:dashboard')
        if _portal_profile_for_role(request.portal_user, role) is None:
            return _clear_stale_portal_session(request)
        return super(PortalLoginRequiredMixin, self).dispatch(request, *args, **kwargs)


class TeacherRequiredMixin(PortalRoleRequiredMixin):
    required_role = 'teacher'


class TeacherScheduleMutationForbiddenMixin:
    """Schedule slots are managed in admin; teachers may view only."""

    def dispatch(self, request, *args, **kwargs):
        from django.contrib import messages
        from django.shortcuts import redirect
        from django.utils.translation import gettext as _

        messages.info(
            request,
            _('Schedule slots are managed by Academor administration. Contact admin to add or change slots.'),
        )
        return redirect('portals:teacher-schedule')


class StudentRequiredMixin(PortalRoleRequiredMixin):
    required_role = 'student'


class StudentQuizTakeRequiredMixin(StudentRequiredMixin):
    """Quiz attempts are student-only — parents may view results but never submit."""

    def dispatch(self, request, *args, **kwargs):
        role = get_portal_role(request.portal_user) if is_portal_authenticated(request) else None
        if role == 'parent':
            return redirect('portals:parent-scores')
        return super().dispatch(request, *args, **kwargs)


class ParentRequiredMixin(PortalRoleRequiredMixin):
    required_role = 'parent'


class CustomerRequiredMixin(PortalRoleRequiredMixin):
    required_role = 'customer'


def _customer_mock_id_from_request(request):
    mock_id = request.GET.get('mock') or request.POST.get('mock')
    if mock_id:
        return mock_id
    if request.method != 'POST':
        return None
    content_type = (request.content_type or '').split(';', 1)[0].strip().lower()
    if content_type != 'application/json':
        return None
    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except (json.JSONDecodeError, UnicodeDecodeError, AttributeError):
        return None
    mock_id = payload.get('mock') or payload.get('mock_attempt_id')
    return str(mock_id) if mock_id is not None else None


class CustomerQuizTakeRequiredMixin(CustomerRequiredMixin):
    """Customers may only take quizzes inside an active mock session."""

    def dispatch(self, request, *args, **kwargs):
        if not is_portal_authenticated(request):
            return _portal_login_redirect(request)
        role = get_portal_role(request.portal_user)
        if role != 'customer':
            return redirect('portals:dashboard')
        if get_customer_profile(request.portal_user) is None:
            return _clear_stale_portal_session(request)
        if not _customer_mock_id_from_request(request):
            return redirect('portals:customer-dashboard')
        return super(CustomerRequiredMixin, self).dispatch(request, *args, **kwargs)


class TeacherOrStudentRequiredMixin(PortalLoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not is_portal_authenticated(request):
            return _portal_login_redirect(request)
        role = get_portal_role(request.portal_user)
        if role not in ('teacher', 'student'):
            return redirect('portals:dashboard')
        return super(PortalLoginRequiredMixin, self).dispatch(request, *args, **kwargs)
