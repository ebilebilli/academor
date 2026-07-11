"""Shared helpers for portal HTTP and quiz test setup."""

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import Client, RequestFactory

from portals.middleware import PortalSessionMiddleware
from portals.models import QuizAssignment
from portals.utils.portal_session import PORTAL_COOKIE_NAME, portal_login
from projects.models.service_models import Service

User = get_user_model()


def ensure_active_portal_services(*slugs):
    defaults = {
        'ielts': {'name_az': 'IELTS', 'name_en': 'IELTS'},
        'sat': {'name_az': 'SAT', 'name_en': 'SAT'},
        'speaking': {'name_az': 'Speaking', 'name_en': 'Speaking'},
    }
    for slug in slugs or ('ielts', 'sat', 'speaking'):
        meta = defaults.get(slug, {'name_az': slug.upper(), 'name_en': slug.upper()})
        Service.objects.get_or_create(
            slug=slug,
            defaults={**meta, 'is_active': True},
        )


def portal_client_login(client: Client, user) -> None:
    factory = RequestFactory()
    request = factory.get('/portal/')
    request.COOKIES = {}
    portal_login(request, user)
    middleware = PortalSessionMiddleware(lambda r: HttpResponse())
    response = middleware(request)
    client.cookies[PORTAL_COOKIE_NAME] = response.cookies[PORTAL_COOKIE_NAME].value


def assign_quiz_to_student(student, quiz, *, is_active=True):
    QuizAssignment.objects.update_or_create(
        student=student,
        quiz=quiz,
        defaults={'is_active': is_active},
    )


def assign_quizzes_to_student(student, *quizzes, is_active=True):
    for quiz in quizzes:
        assign_quiz_to_student(student, quiz, is_active=is_active)
