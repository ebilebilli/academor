from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views import View

from portals.models import IeltsMockTestAttempt
from portals.utils.customer_mock import (
    abandon_customer_mock_test_attempt,
    consume_customer_mock_credit_on_quiz_start,
    get_active_customer_mock_attempt,
    resolve_customer_mock_start_request,
    resolve_customer_mock_take_request,
)
from portals.utils.ielts_mock_test import parse_mock_attempt_id
from portals.utils.portal_session import clear_quiz_attempt_start, get_quiz_attempt_start, set_quiz_attempt_start
from portals.utils.queries import get_customer_mock_quiz_take_data, get_customer_profile
from portals.utils.safe_redirect import safe_portal_next_url
from portals.utils.quiz_submit import (
    submit_listening_quiz_attempt,
    submit_manual_quiz_attempt,
    submit_reading_quiz_attempt,
    submit_speaking_quiz_attempt,
)
from portals.views.mixins import CustomerQuizTakeRequiredMixin
from portals.views.quiz_views import (
    _mock_submit_kwargs,
    _parse_duration_sec,
    _parse_json_submit_payload,
)
from portals.views.views_v1 import _portal_context


class CustomerReadingQuizTakeView(CustomerQuizTakeRequiredMixin, View):
    template_name = 'portals/student/quiz_take_reading.html'

    def get(self, request, pk):
        profile = get_customer_profile(request.portal_user)
        mock_id = parse_mock_attempt_id(request.GET.get('mock'))
        if not mock_id:
            raise Http404
        quiz = get_customer_mock_quiz_take_data(profile.pk, pk, mock_attempt_id=mock_id)
        if not quiz:
            raise Http404

        mock_ctx = resolve_customer_mock_take_request(profile.pk, mock_id, pk)
        if mock_ctx.get('mock_redirect'):
            return redirect(mock_ctx['mock_redirect'])

        start_url = f"{reverse('portals:customer-quiz-start', kwargs={'pk': pk})}?mock={mock_id}"
        cancel_url = (
            f"{reverse('portals:customer-quiz-cancel', kwargs={'pk': pk})}"
            f"?mock={mock_id}&next={mock_ctx.get('back_url', reverse('portals:customer-ielts-mock'))}"
        )
        return render(
            request,
            self.template_name,
            _portal_context(
                request,
                quiz=quiz,
                submit_url=reverse('portals:customer-reading-quiz-submit', kwargs={'pk': pk}),
                start_url=start_url,
                back_url=mock_ctx.get('back_url') or reverse('portals:customer-ielts-mock'),
                quiz_cancel_url=cancel_url,
                **{k: v for k, v in mock_ctx.items() if k != 'back_url'},
            ),
        )


class CustomerSpeakingQuizTakeView(CustomerQuizTakeRequiredMixin, View):
    template_name = 'portals/student/quiz_take_speaking.html'

    def get(self, request, pk):
        profile = get_customer_profile(request.portal_user)
        mock_id = parse_mock_attempt_id(request.GET.get('mock'))
        if not mock_id:
            raise Http404
        quiz = get_customer_mock_quiz_take_data(profile.pk, pk, mock_attempt_id=mock_id)
        if not quiz:
            raise Http404

        mock_ctx = resolve_customer_mock_take_request(profile.pk, mock_id, pk)
        if mock_ctx.get('mock_redirect'):
            return redirect(mock_ctx['mock_redirect'])

        start_url = f"{reverse('portals:customer-quiz-start', kwargs={'pk': pk})}?mock={mock_id}"
        cancel_url = (
            f"{reverse('portals:customer-quiz-cancel', kwargs={'pk': pk})}"
            f"?mock={mock_id}&next={mock_ctx.get('back_url', reverse('portals:customer-ielts-mock'))}"
        )
        return render(
            request,
            self.template_name,
            _portal_context(
                request,
                quiz=quiz,
                submit_url=reverse('portals:customer-speaking-quiz-submit', kwargs={'pk': pk}),
                start_url=start_url,
                back_url=mock_ctx.get('back_url') or reverse('portals:customer-ielts-mock'),
                quiz_cancel_url=cancel_url,
                **{k: v for k, v in mock_ctx.items() if k != 'back_url'},
            ),
        )


class CustomerManualQuizTakeView(CustomerQuizTakeRequiredMixin, View):
    template_name = 'portals/student/quiz_take_manual.html'

    def get(self, request, pk):
        profile = get_customer_profile(request.portal_user)
        mock_id = parse_mock_attempt_id(request.GET.get('mock'))
        if not mock_id:
            raise Http404
        quiz = get_customer_mock_quiz_take_data(profile.pk, pk, mock_attempt_id=mock_id)
        if not quiz:
            raise Http404

        mock_ctx = resolve_customer_mock_take_request(profile.pk, mock_id, pk)
        if mock_ctx.get('mock_redirect'):
            return redirect(mock_ctx['mock_redirect'])

        start_url = f"{reverse('portals:customer-quiz-start', kwargs={'pk': pk})}?mock={mock_id}"
        cancel_url = (
            f"{reverse('portals:customer-quiz-cancel', kwargs={'pk': pk})}"
            f"?mock={mock_id}&next={mock_ctx.get('back_url', reverse('portals:customer-ielts-mock'))}"
        )
        return render(
            request,
            self.template_name,
            _portal_context(
                request,
                quiz=quiz,
                submit_url=reverse('portals:customer-manual-quiz-submit', kwargs={'pk': pk}),
                start_url=start_url,
                back_url=mock_ctx.get('back_url') or reverse('portals:customer-ielts-mock'),
                quiz_cancel_url=cancel_url,
                **{k: v for k, v in mock_ctx.items() if k != 'back_url'},
            ),
        )


class CustomerQuizStartView(CustomerQuizTakeRequiredMixin, View):
    def post(self, request, pk):
        profile = get_customer_profile(request.portal_user)
        mock_id = parse_mock_attempt_id(request.GET.get('mock') or request.POST.get('mock'))
        if not mock_id:
            return JsonResponse({'success': False, 'error': _('Mock test session required.')}, status=400)

        quiz = get_customer_mock_quiz_take_data(profile.pk, pk, mock_attempt_id=mock_id)
        if not quiz:
            return JsonResponse({'success': False, 'error': _('Quiz not found.')}, status=404)

        start_override = resolve_customer_mock_start_request(profile.pk, mock_id, pk)
        if start_override is not None:
            status = 400 if start_override.get('success') is False else 200
            return JsonResponse(start_override, status=status)

        attempt = get_active_customer_mock_attempt(profile.pk, mock_id)
        if attempt:
            from portals.utils.ielts_mock_test import section_for_quiz_in_attempt

            section = section_for_quiz_in_attempt(attempt, pk)
            if section == IeltsMockTestAttempt.Section.LISTENING and not attempt.credit_consumed:
                ok, error = consume_customer_mock_credit_on_quiz_start(profile.pk, mock_id, pk)
                if not ok:
                    return JsonResponse({'success': False, 'error': error}, status=400)

        set_quiz_attempt_start(request, pk)
        return JsonResponse({'success': True})


class CustomerQuizCancelView(CustomerQuizTakeRequiredMixin, View):
    """Leave the quiz page; mock abandon only on POST (CSRF-safe). GET redirects back."""

    def _redirect_after_cancel(self, request):
        next_url = safe_portal_next_url(request, request.GET.get('next'))
        if next_url:
            return redirect(next_url)
        return redirect('portals:customer-ielts-mock')

    def get(self, request, pk):
        profile = get_customer_profile(request.portal_user)
        mock_id = parse_mock_attempt_id(request.GET.get('mock') or request.POST.get('mock'))
        if mock_id:
            quiz = get_customer_mock_quiz_take_data(profile.pk, pk, mock_attempt_id=mock_id)
            if not quiz:
                next_url = safe_portal_next_url(request, request.GET.get('next'))
                if next_url:
                    return redirect(next_url)
                raise Http404
        return self._redirect_after_cancel(request)

    def post(self, request, pk):
        profile = get_customer_profile(request.portal_user)
        mock_id = parse_mock_attempt_id(request.GET.get('mock') or request.POST.get('mock'))
        if mock_id:
            abandon_customer_mock_test_attempt(profile.pk, mock_id)
        clear_quiz_attempt_start(request, pk)
        return self._redirect_after_cancel(request)


class CustomerReadingQuizSubmitView(CustomerQuizTakeRequiredMixin, View):
    def post(self, request, pk):
        profile = get_customer_profile(request.portal_user)
        payload = _parse_json_submit_payload(request)
        if payload is None:
            return JsonResponse({'success': False, 'error': _('Invalid request.')}, status=400)

        session_started_at = get_quiz_attempt_start(request, pk)
        if not session_started_at:
            return JsonResponse(
                {'success': False, 'error': _('Quiz not started.')},
                status=400,
            )

        result = submit_reading_quiz_attempt(
            customer_id=profile.pk,
            quiz_id=pk,
            given_answers=payload.get('answers') or {},
            duration_sec=_parse_duration_sec(payload.get('duration_sec')),
            session_started_at=session_started_at,
            completion_trigger=payload.get('completion_trigger'),
            **_mock_submit_kwargs(request, payload),
        )
        if result.get('success'):
            clear_quiz_attempt_start(request, pk)
        return JsonResponse(result, status=200 if result.get('success') else 400)


class CustomerSpeakingQuizSubmitView(CustomerQuizTakeRequiredMixin, View):
    def post(self, request, pk):
        profile = get_customer_profile(request.portal_user)
        mock_kwargs = _mock_submit_kwargs(request, {'mock': request.POST.get('mock')})
        session_started_at = get_quiz_attempt_start(request, pk)
        if not session_started_at:
            return JsonResponse(
                {'success': False, 'error': _('Quiz not started.')},
                status=400,
            )

        recording_files = {}
        for key, upload in request.FILES.items():
            if key.startswith('recording_'):
                question_id = key[len('recording_'):]
                if question_id:
                    recording_files[question_id] = upload

        recording_durations = {}
        for key, value in request.POST.items():
            if key.startswith('duration_'):
                question_id = key[len('duration_'):]
                if question_id:
                    try:
                        recording_durations[question_id] = int(value)
                    except (TypeError, ValueError):
                        recording_durations[question_id] = 0

        result = submit_speaking_quiz_attempt(
            customer_id=profile.pk,
            quiz_id=pk,
            recording_files=recording_files or None,
            recording_durations=recording_durations or None,
            duration_sec=_parse_duration_sec(request.POST.get('duration_sec')),
            session_started_at=session_started_at,
            allow_empty_submission=request.POST.get('allow_empty') in ('1', 'true', 'True'),
            completion_trigger=request.POST.get('completion_trigger'),
            **mock_kwargs,
        )
        if result.get('success'):
            clear_quiz_attempt_start(request, pk)
        return JsonResponse(result, status=200 if result.get('success') else 400)


class CustomerManualQuizSubmitView(CustomerQuizTakeRequiredMixin, View):
    def post(self, request, pk):
        profile = get_customer_profile(request.portal_user)
        payload = _parse_json_submit_payload(request)
        if payload is None:
            return JsonResponse({'success': False, 'error': _('Invalid request.')}, status=400)

        mock_kwargs = _mock_submit_kwargs(request, payload)
        mock_attempt_id = mock_kwargs.get('mock_attempt_id')
        session_started_at = get_quiz_attempt_start(request, pk)
        if not session_started_at:
            return JsonResponse(
                {'success': False, 'error': _('Quiz not started.')},
                status=400,
            )

        if mock_attempt_id:
            quiz = get_customer_mock_quiz_take_data(profile.pk, pk, mock_attempt_id=mock_attempt_id)
            if quiz and quiz.get('is_listening'):
                result = submit_listening_quiz_attempt(
                    customer_id=profile.pk,
                    quiz_id=pk,
                    given_answers=payload.get('answers') or {},
                    ordered_answers=payload.get('ordered_answers'),
                    duration_sec=_parse_duration_sec(payload.get('duration_sec')),
                    session_started_at=session_started_at,
                    allow_empty_submission=bool(payload.get('allow_empty') or payload.get('allow_empty_submission')),
                    completion_trigger=payload.get('completion_trigger'),
                    **mock_kwargs,
                )
                if result.get('success'):
                    clear_quiz_attempt_start(request, pk)
                return JsonResponse(result, status=200 if result.get('success') else 400)

        result = submit_manual_quiz_attempt(
            customer_id=profile.pk,
            quiz_id=pk,
            student_submission=payload.get('submission') or payload.get('student_submission') or '',
            given_answers=payload.get('answers'),
            ordered_answers=payload.get('ordered_answers'),
            duration_sec=_parse_duration_sec(payload.get('duration_sec')),
            session_started_at=session_started_at,
            allow_empty_submission=bool(payload.get('allow_empty') or payload.get('allow_empty_submission')),
            completion_trigger=payload.get('completion_trigger'),
            **mock_kwargs,
        )
        if result.get('success'):
            clear_quiz_attempt_start(request, pk)
        return JsonResponse(result, status=200 if result.get('success') else 400)
