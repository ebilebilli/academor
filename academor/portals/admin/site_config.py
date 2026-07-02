from django.contrib import admin
from django.contrib.admin.forms import AdminAuthenticationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from portals.utils.admin_access import can_access_django_admin


class StaffOnlyAdminAuthenticationForm(AdminAuthenticationForm):
    """Reject portal-only accounts at the admin login screen."""

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not can_access_django_admin(user):
            raise ValidationError(
                _(
                    'This account uses the student portal only. '
                    'Log in from the main website with "Log in".',
                ),
                code='invalid_login',
            )


def configure_admin_site():
    """
    Configure admin site with staff-only access.
    Note: With separate cookies (portal_sessionid vs sessionid),
    admin logout does NOT affect portal session anymore.
    """
    admin.site.login_form = StaffOnlyAdminAuthenticationForm

    def has_permission(request):
        return (
            request.user.is_active
            and can_access_django_admin(request.user)
        )

    admin.site.has_permission = has_permission
