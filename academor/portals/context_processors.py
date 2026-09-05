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
    from portals.utils.queries import get_customer_profile, get_parent_profile, get_portal_role, get_student_profile, get_teacher_profile

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
    if role == 'customer':
        profile = get_customer_profile(request.portal_user)
        if not profile:
            return empty
        return {
            **empty,
            'portal_unread_notifications': get_unread_notification_count(customer_id=profile.pk),
            'portal_notifications_url': reverse('portals:customer-notifications'),
        }
    return empty


def portal_student_service_context(request):
    if not request.path.startswith('/portal/'):
        return {'portal_student_has_ielts': False, 'portal_student_has_mock_exam': False}
    if not is_portal_authenticated(request):
        return {'portal_student_has_ielts': False, 'portal_student_has_mock_exam': False}

    from portals.utils.queries import get_portal_role, get_student_profile
    from portals.utils.ielts_mock_test import get_student_mock_exam_programs, student_can_access_mock
    from portals.utils.student_courses import student_has_course_access

    role = get_portal_role(request.portal_user)
    if role != 'student':
        return {
            'portal_student_has_ielts': False,
            'portal_student_has_mock_exam': False,
            'portal_student_mock_unlocked': False,
            'portal_student_mock_url': None,
        }
    profile = get_student_profile(request.portal_user)
    if not profile:
        return {
            'portal_student_has_ielts': False,
            'portal_student_has_mock_exam': False,
            'portal_student_mock_unlocked': False,
            'portal_student_mock_url': None,
        }
    programs = get_student_mock_exam_programs(profile.pk)
    has_mock_exam = bool(programs)
    if len(programs) == 1:
        from django.urls import reverse

        mock_url = reverse('portals:student-mock-landing', kwargs={'program': programs[0]})
    elif programs:
        from django.urls import reverse

        mock_url = reverse('portals:student-mock-picker')
    else:
        mock_url = None
    return {
        'portal_student_has_ielts': student_has_course_access(profile.pk, 'ielts'),
        'portal_student_has_mock_exam': has_mock_exam,
        'portal_student_mock_unlocked': student_can_access_mock(profile.pk),
        'portal_student_mock_url': mock_url,
    }


def portal_customer_service_context(request):
    if not request.path.startswith('/portal/'):
        return {'portal_customer_has_mock_exam': False, 'portal_customer_mock_url': None}
    if not is_portal_authenticated(request):
        return {'portal_customer_has_mock_exam': False, 'portal_customer_mock_url': None}

    from django.urls import reverse

    from portals.utils.customer_mock import get_customer_selectable_mock_programs
    from portals.utils.queries import get_portal_role, get_customer_profile

    role = get_portal_role(request.portal_user)
    if role != 'customer':
        return {'portal_customer_has_mock_exam': False, 'portal_customer_mock_url': None}

    profile = get_customer_profile(request.portal_user)
    if not profile:
        return {'portal_customer_has_mock_exam': False, 'portal_customer_mock_url': None}

    programs = get_customer_selectable_mock_programs(profile.pk)
    # Always link Mock Test to the mock flow — never to Paket al.
    if len(programs) == 1:
        mock_url = reverse('portals:customer-mock-landing', kwargs={'program': programs[0]})
    else:
        mock_url = reverse('portals:customer-mock-picker')
    return {
        'portal_customer_has_mock_exam': True,
        'portal_customer_mock_url': mock_url,
    }
