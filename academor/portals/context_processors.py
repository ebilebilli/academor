from portals.utils.portal_session import is_portal_authenticated


def portal_auth_context(request):
    user = getattr(request, 'portal_user', None)
    if user is None:
        from portals.utils.portal_session import get_portal_user
        user = get_portal_user(request)
    return {
        'portal_user': user,
        'portal_is_authenticated': is_portal_authenticated(request),
    }


def portal_notification_context(request):
    empty = {
        'portal_unread_notifications': 0,
        'portal_notifications_url': '',
        'portal_pending_reviews_count': 0,
        'portal_pending_reviews_url': '',
    }
    if not request.path.startswith('/portal/'):
        return empty
    if not is_portal_authenticated(request):
        return empty

    from django.urls import reverse

    from portals.utils.notifications import (
        get_teacher_pending_review_count,
        get_teacher_portal_bell_count,
        get_unread_notification_count,
    )
    from portals.utils.queries import get_parent_profile, get_portal_role, get_student_profile, get_teacher_profile

    role = get_portal_role(request.portal_user)
    if role == 'teacher':
        profile = get_teacher_profile(request.portal_user)
        if not profile:
            return empty
        return {
            'portal_unread_notifications': get_teacher_portal_bell_count(profile.pk),
            'portal_notifications_url': reverse('portals:teacher-notifications'),
            'portal_pending_reviews_count': get_teacher_pending_review_count(profile.pk),
            'portal_pending_reviews_url': reverse('portals:teacher-quiz-results'),
        }
    if role == 'parent':
        profile = get_parent_profile(request.portal_user)
        if not profile:
            return empty
        return {
            **empty,
            'portal_unread_notifications': get_unread_notification_count(parent_id=profile.pk),
            'portal_notifications_url': reverse('portals:parent-notifications'),
        }
    if role == 'student':
        profile = get_student_profile(request.portal_user)
        if not profile:
            return empty
        return {
            **empty,
            'portal_unread_notifications': get_unread_notification_count(student_id=profile.pk),
            'portal_notifications_url': reverse('portals:student-notifications'),
        }
    return empty
