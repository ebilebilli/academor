from urllib.parse import quote

from django.shortcuts import redirect
from django.urls import reverse

from portals.utils.portal_session import is_portal_authenticated, portal_logout
from portals.utils.queries import (
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


class TeacherOrStudentRequiredMixin(PortalLoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not is_portal_authenticated(request):
            return _portal_login_redirect(request)
        role = get_portal_role(request.portal_user)
        if role not in ('teacher', 'student'):
            return redirect('portals:dashboard')
        return super(PortalLoginRequiredMixin, self).dispatch(request, *args, **kwargs)
