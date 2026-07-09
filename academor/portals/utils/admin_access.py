from django.contrib.auth import get_user_model

from portals.models import CustomerProfile, ParentProfile, StudentProfile, TeacherProfile

User = get_user_model()


def has_portal_profile(user) -> bool:
    if not user or not user.pk:
        return False
    uid = user.pk
    return (
        TeacherProfile.objects.filter(user_id=uid).exists()
        or StudentProfile.objects.filter(user_id=uid).exists()
        or ParentProfile.objects.filter(user_id=uid).exists()
        or CustomerProfile.objects.filter(user_id=uid).exists()
    )


def can_access_django_admin(user) -> bool:
    """Only Staff / Admin accounts — not portal Teacher, Student, or Parent users."""
    if not user or not getattr(user, 'is_authenticated', False):
        return False
    if not user.is_active or not user.is_staff:
        return False
    if has_portal_profile(user):
        return False
    return True


def strip_admin_flags_for_portal_user(user):
    """Portal profiles must never retain Django admin permissions."""
    if not user or not user.pk:
        return
    if not has_portal_profile(user):
        return
    if user.is_staff or user.is_superuser:
        User.objects.filter(pk=user.pk).update(is_staff=False, is_superuser=False)
        user.is_staff = False
        user.is_superuser = False
