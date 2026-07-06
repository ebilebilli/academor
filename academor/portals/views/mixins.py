from urllib.parse import quote

from django.shortcuts import redirect
from django.urls import reverse

from portals.utils.portal_session import is_portal_authenticated
from portals.utils.queries import get_portal_role


def _portal_login_redirect(request):
    next_path = quote(request.get_full_path(), safe='')
    login = reverse('portals:login')
    return redirect(f'{login}?next={next_path}')


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
        if get_portal_role(request.portal_user) != self.required_role:
            return redirect('portals:dashboard')
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
