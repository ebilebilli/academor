from django.shortcuts import redirect
from django.views import View

from portals.utils.queries import get_portal_role
from portals.views.mixins import PortalLoginRequiredMixin


class PortalProfileView(PortalLoginRequiredMixin, View):
    def _redirect_for_role(self, role):
        if role == 'teacher':
            return redirect('portals:teacher-dashboard')
        if role == 'student':
            return redirect('portals:student-dashboard')
        if role == 'parent':
            return redirect('portals:parent-dashboard')
        return redirect('portals:dashboard')

    def get(self, request):
        return self._redirect_for_role(get_portal_role(request.portal_user))

    def post(self, request):
        return self._redirect_for_role(get_portal_role(request.portal_user))
