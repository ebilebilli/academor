import json

from django.contrib import messages
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views import View

from portals.models import QuizResult
from portals.utils.portal_session import (
    clear_quiz_attempt_start,
    get_quiz_attempt_start,
    set_quiz_attempt_start,
)
from portals.utils.queries import (
    get_student_listening_quiz_take_data,
    get_student_manual_quiz_take_data,
    get_student_profile,
    get_student_quiz_take_data,
    get_student_reading_quiz_take_data,
    get_student_speaking_quiz_take_data,
    get_teacher_pending_quiz_results,
    get_teacher_profile,
    get_teacher_quiz_result_detail,
    serialize_teacher,
)
from portals.utils.quiz_submit import (
    submit_listening_quiz_attempt,
    submit_manual_quiz_attempt,
    submit_reading_quiz_attempt,
    submit_speaking_quiz_attempt,
    submit_teacher_quiz_review,
    submit_variant_quiz_attempt,
)
from portals.utils.ielts_mock_test import (
    abandon_mock_test_attempt,
    get_active_mock_attempt,
    parse_mock_attempt_id,
    resolve_mock_start_request,
    resolve_mock_take_request,
    serialize_mock_progress,
    validate_mock_section_submit,
)
from portals.utils.safe_redirect import safe_portal_next_url
from portals.views.mixins import StudentQuizTakeRequiredMixin, TeacherRequiredMixin
from portals.views.views_v1 import _portal_context


def _quiz_back_url(quiz: dict) -> str:
    category_pk = quiz.get('category_id')
    if category_pk is not None:
        return reverse('portals:student-quiz-category', kwargs={'category_pk': category_pk})
    return reverse('portals:student-quizzes')


def _mock_context_for_take(request, profile_id: int, quiz_id: int) -> dict:
    mock_id = parse_mock_attempt_id(request.GET.get('mock'))
    return resolve_mock_take_request(profile_id, mock_id, quiz_id)


def _mock_submit_kwargs(request, payload: dict | None = None) -> dict:
    mock_id = parse_mock_attempt_id(
        (payload or {}).get('mock')
        or (payload or {}).get('mock_attempt_id')
        or request.GET.get('mock')
    )
    if not mock_id:
        return {}
    return {
        'mock_attempt_id': mock_id,
        'defer_notifications': True,
    }


def _parse_reading_correct_answers(post_data) -> dict:
    answers = {}
    prefix = 'reading_correct_'
    for key in post_data:
        if not key.startswith(prefix):
            continue
        question_id = key[len(prefix):]
        if not question_id:
            continue
        value = (post_data.get(key) or '').strip()
        if value:
            answers[question_id] = value
    return answers


def _get_student_take_quiz(profile_id: int, quiz_id: int):
    quiz = get_student_quiz_take_data(profile_id, quiz_id)
    if quiz:
        return quiz, 'variant'
    quiz = get_student_reading_quiz_take_data(profile_id, quiz_id)
    if quiz:
        return quiz, 'reading'
    quiz = get_student_listening_quiz_take_data(profile_id, quiz_id)
    if quiz:
        return quiz, 'listening'
    quiz = get_student_speaking_quiz_take_data(profile_id, quiz_id)
    if quiz:
        return quiz, 'speaking'
    quiz = get_student_manual_quiz_take_data(profile_id, quiz_id)
    if quiz:
        return quiz, 'manual'
    return None, None


def _submit_leave_completion(
    *,
    profile_id: int,
    quiz_id: int,
    quiz_kind: str,
    session_started_at: str | None,
    mock_attempt_id: int | None = None,
):
    mock_kwargs = {
        'mock_attempt_id': mock_attempt_id,
        'defer_notifications': bool(mock_attempt_id),
    }
    if quiz_kind == 'variant':
        return submit_variant_quiz_attempt(
            student_id=profile_id,
            quiz_id=quiz_id,
            given_answers={},
            duration_sec=0,
            session_started_at=session_started_at,
            completion_trigger=QuizResult.CompletionTrigger.AUTO_LEAVE,
            **mock_kwargs,
        )
    if quiz_kind == 'reading':
        return submit_reading_quiz_attempt(
            student_id=profile_id,
            quiz_id=quiz_id,
            given_answers={},
            duration_sec=0,
            session_started_at=session_started_at,
            completion_trigger=QuizResult.CompletionTrigger.AUTO_LEAVE,
            **mock_kwargs,
        )
    if quiz_kind == 'listening':
        return submit_listening_quiz_attempt(
            student_id=profile_id,
            quiz_id=quiz_id,
            given_answers={},
            duration_sec=0,
            session_started_at=session_started_at,
            allow_empty_submission=True,
            completion_trigger=QuizResult.CompletionTrigger.AUTO_LEAVE,
            **mock_kwargs,
        )
    if quiz_kind == 'speaking':
        return submit_speaking_quiz_attempt(
            student_id=profile_id,
            quiz_id=quiz_id,
            recording_files={},
            duration_sec=0,
            session_started_at=session_started_at,
            allow_empty_submission=True,
            completion_trigger=QuizResult.CompletionTrigger.AUTO_LEAVE,
            **mock_kwargs,
        )
    if quiz_kind == 'manual':
        return submit_manual_quiz_attempt(
            student_id=profile_id,
            quiz_id=quiz_id,
            student_submission='',
            given_answers={},
            duration_sec=0,
            session_started_at=session_started_at,
            allow_empty_submission=True,
            completion_trigger=QuizResult.CompletionTrigger.AUTO_LEAVE,
            **mock_kwargs,
        )
    return {'success': False, 'error': _('Quiz not found.')}


class StudentQuizTakeView(StudentQuizTakeRequiredMixin, View):
    template_name = 'portals/student/quiz_take.html'

    def get(self, request, pk):
        profile = get_student_profile(request.portal_user)
        quiz = get_student_quiz_take_data(profile.pk, pk)
        if not quiz:
            raise Http404

        return render(
            request,
            self.template_name,
            _portal_context(
                request,
                quiz=quiz,
                submit_url=reverse('portals:student-quiz-submit', kwargs={'pk': pk}),
                start_url=reverse('portals:student-quiz-start', kwargs={'pk': pk}),
                back_url=_quiz_back_url(quiz),
            ),
        )


class StudentReadingQuizTakeView(StudentQuizTakeRequiredMixin, View):
    template_name = 'portals/student/quiz_take_reading.html'

    def get(self, request, pk):
        profile = get_student_profile(request.portal_user)
        mock_id = parse_mock_attempt_id(request.GET.get('mock'))
        quiz = get_student_reading_quiz_take_data(profile.pk, pk, mock_attempt_id=mock_id)
        if not quiz:
            raise Http404

        mock_ctx = _mock_context_for_take(request, profile.pk, pk)
        if mock_ctx.get('mock_redirect'):
            return redirect(mock_ctx['mock_redirect'])

        start_url = reverse('portals:student-quiz-start', kwargs={'pk': pk})
        if mock_ctx.get('mock_id'):
            start_url = f'{start_url}?mock={mock_ctx["mock_id"]}'

        ctx = _portal_context(
            request,
            quiz=quiz,
            submit_url=reverse('portals:student-reading-quiz-submit', kwargs={'pk': pk}),
            start_url=start_url,
            back_url=mock_ctx.get('back_url') or _quiz_back_url(quiz),
            **{k: v for k, v in mock_ctx.items() if k != 'back_url'},
        )
        return render(request, self.template_name, ctx)


class StudentSpeakingQuizTakeView(StudentQuizTakeRequiredMixin, View):
    template_name = 'portals/student/quiz_take_speaking.html'

    def get(self, request, pk):
        profile = get_student_profile(request.portal_user)
        mock_id = parse_mock_attempt_id(request.GET.get('mock'))
        quiz = get_student_speaking_quiz_take_data(profile.pk, pk, mock_attempt_id=mock_id)
        if not quiz:
            raise Http404

        mock_ctx = _mock_context_for_take(request, profile.pk, pk)
        if mock_ctx.get('mock_redirect'):
            return redirect(mock_ctx['mock_redirect'])

        start_url = reverse('portals:student-quiz-start', kwargs={'pk': pk})
        if mock_ctx.get('mock_id'):
            start_url = f'{start_url}?mock={mock_ctx["mock_id"]}'

        ctx = _portal_context(
            request,
            quiz=quiz,
            submit_url=reverse('portals:student-speaking-quiz-submit', kwargs={'pk': pk}),
            start_url=start_url,
            back_url=mock_ctx.get('back_url') or _quiz_back_url(quiz),
            **{k: v for k, v in mock_ctx.items() if k != 'back_url'},
        )
        return render(request, self.template_name, ctx)


class StudentManualQuizTakeView(StudentQuizTakeRequiredMixin, View):
    template_name = 'portals/student/quiz_take_manual.html'

    def get(self, request, pk):
        profile = get_student_profile(request.portal_user)
        mock_id = parse_mock_attempt_id(request.GET.get('mock'))
        quiz = get_student_listening_quiz_take_data(profile.pk, pk, mock_attempt_id=mock_id)
        if not quiz:
            quiz = get_student_manual_quiz_take_data(profile.pk, pk, mock_attempt_id=mock_id)
        if not quiz:
            raise Http404

        mock_ctx = _mock_context_for_take(request, profile.pk, pk)
        if mock_ctx.get('mock_redirect'):
            return redirect(mock_ctx['mock_redirect'])

        start_url = reverse('portals:student-quiz-start', kwargs={'pk': pk})
        if mock_ctx.get('mock_id'):
            start_url = f'{start_url}?mock={mock_ctx["mock_id"]}'

        ctx = _portal_context(
            request,
            quiz=quiz,
            submit_url=reverse('portals:student-manual-quiz-submit', kwargs={'pk': pk}),
            start_url=start_url,
            back_url=mock_ctx.get('back_url') or _quiz_back_url(quiz),
            **{k: v for k, v in mock_ctx.items() if k != 'back_url'},
        )
        return render(request, self.template_name, ctx)


class StudentQuizStartView(StudentQuizTakeRequiredMixin, View):
    def post(self, request, pk):
        profile = get_student_profile(request.portal_user)
        quiz, _quiz_kind = _get_student_take_quiz(profile.pk, pk)
        if not quiz:
            return JsonResponse({'success': False, 'error': _('Quiz not found.')}, status=404)

        mock_id = parse_mock_attempt_id(request.GET.get('mock') or request.POST.get('mock'))
        if mock_id:
            start_override = resolve_mock_start_request(profile.pk, mock_id, pk)
            if start_override is not None:
                status = 400 if start_override.get('success') is False else 200
                return JsonResponse(start_override, status=status)

        if quiz.get('view_only') and not mock_id:
            return JsonResponse(
                {'success': False, 'error': _('Your submission is awaiting teacher review.')},
                status=400,
            )

        existing_result = QuizResult.objects.filter(
            student_id=profile.pk,
            quiz_id=pk,
            ielts_mock_attempt__isnull=True,
        ).first()
        is_retest = bool(existing_result and existing_result.reviewed_at is not None and not mock_id)

        if is_retest:
            clear_quiz_attempt_start(request, pk)
            set_quiz_attempt_start(request, pk)
        elif not get_quiz_attempt_start(request, pk):
            set_quiz_attempt_start(request, pk)

        return JsonResponse({'success': True})


class StudentQuizCancelView(StudentQuizTakeRequiredMixin, View):
    """Leave the quiz page and auto-complete if an active attempt exists."""

    def get(self, request, pk):
        profile = get_student_profile(request.portal_user)
        quiz, quiz_kind = _get_student_take_quiz(profile.pk, pk)
        if not quiz:
            raise Http404

        session_started_at = get_quiz_attempt_start(request, pk)
        mock_id = parse_mock_attempt_id(request.GET.get('mock'))
        if session_started_at and not quiz.get('view_only') and not mock_id:
            _submit_leave_completion(
                profile_id=profile.pk,
                quiz_id=pk,
                quiz_kind=quiz_kind,
                session_started_at=session_started_at,
                mock_attempt_id=mock_id,
            )
        if mock_id:
            abandon_mock_test_attempt(profile.pk, mock_id)
        clear_quiz_attempt_start(request, pk)

        next_url = safe_portal_next_url(request, request.GET.get('next'))
        if next_url:
            return redirect(next_url)

        return redirect(_quiz_back_url(quiz))


class StudentQuizSubmitView(StudentQuizTakeRequiredMixin, View):
    def post(self, request, pk):
        profile = get_student_profile(request.portal_user)
        quiz = get_student_quiz_take_data(profile.pk, pk)
        if not quiz:
            return JsonResponse({'success': False, 'error': 'Quiz not found.'}, status=404)

        try:
            payload = json.loads(request.body.decode('utf-8') or '{}')
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid request.'}, status=400)

        session_started_at = get_quiz_attempt_start(request, pk)
        if not session_started_at:
            return JsonResponse(
                {'success': False, 'error': _('Quiz not started.')},
                status=400,
            )

        result = submit_variant_quiz_attempt(
            student_id=profile.pk,
            quiz_id=pk,
            given_answers=payload.get('answers') or {},
            duration_sec=int(payload.get('duration_sec') or 0),
            session_started_at=session_started_at,
            completion_trigger=payload.get('completion_trigger'),
        )
        if not result.get('success'):
            status = 400
            if result.get('error') == 'Quiz not found.':
                status = 404
            return JsonResponse(result, status=status)

        clear_quiz_attempt_start(request, pk)
        return JsonResponse(result)


class StudentReadingQuizSubmitView(StudentQuizTakeRequiredMixin, View):
    def post(self, request, pk):
        profile = get_student_profile(request.portal_user)
        quiz = get_student_reading_quiz_take_data(profile.pk, pk)
        if not quiz:
            return JsonResponse({'success': False, 'error': 'Quiz not found.'}, status=404)

        try:
            payload = json.loads(request.body.decode('utf-8') or '{}')
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid request.'}, status=400)

        session_started_at = get_quiz_attempt_start(request, pk)
        if not session_started_at:
            return JsonResponse(
                {'success': False, 'error': _('Quiz not started.')},
                status=400,
            )

        result = submit_reading_quiz_attempt(
            student_id=profile.pk,
            quiz_id=pk,
            given_answers=payload.get('answers') or {},
            duration_sec=int(payload.get('duration_sec') or 0),
            session_started_at=session_started_at,
            completion_trigger=payload.get('completion_trigger'),
            **_mock_submit_kwargs(request, payload),
        )
        if not result.get('success'):
            status = 400
            if result.get('error') == 'Quiz not found.':
                status = 404
            return JsonResponse(result, status=status)

        clear_quiz_attempt_start(request, pk)
        return JsonResponse(result)


class StudentManualQuizSubmitView(StudentQuizTakeRequiredMixin, View):
    def post(self, request, pk):
        profile = get_student_profile(request.portal_user)
        quiz = get_student_listening_quiz_take_data(profile.pk, pk)
        if quiz:
            try:
                payload = json.loads(request.body.decode('utf-8') or '{}')
            except json.JSONDecodeError:
                return JsonResponse({'success': False, 'error': 'Invalid request.'}, status=400)

            session_started_at = get_quiz_attempt_start(request, pk)
            if not session_started_at:
                return JsonResponse(
                    {'success': False, 'error': _('Quiz not started.')},
                    status=400,
                )

            result = submit_listening_quiz_attempt(
                student_id=profile.pk,
                quiz_id=pk,
                given_answers=payload.get('answers') or {},
                ordered_answers=payload.get('ordered_answers'),
                duration_sec=int(payload.get('duration_sec') or 0),
                session_started_at=session_started_at,
                allow_empty_submission=bool(payload.get('allow_empty')),
                completion_trigger=payload.get('completion_trigger'),
                **_mock_submit_kwargs(request, payload),
            )
            if not result.get('success'):
                status = 400
                if result.get('error') == 'Quiz not found.':
                    status = 404
                return JsonResponse(result, status=status)

            clear_quiz_attempt_start(request, pk)
            return JsonResponse(result)

        try:
            payload = json.loads(request.body.decode('utf-8') or '{}')
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid request.'}, status=400)

        mock_kwargs = _mock_submit_kwargs(request, payload)
        quiz = get_student_manual_quiz_take_data(
            profile.pk,
            pk,
            mock_attempt_id=mock_kwargs.get('mock_attempt_id'),
        )
        if not quiz:
            return JsonResponse({'success': False, 'error': 'Quiz not found.'}, status=404)

        if quiz.get('view_only') and not mock_kwargs.get('mock_attempt_id'):
            return JsonResponse(
                {'success': False, 'error': _('Your submission is awaiting teacher review.')},
                status=400,
            )

        session_started_at = get_quiz_attempt_start(request, pk)
        if not session_started_at:
            return JsonResponse(
                {'success': False, 'error': _('Quiz not started.')},
                status=400,
            )

        result = submit_manual_quiz_attempt(
            student_id=profile.pk,
            quiz_id=pk,
            student_submission=payload.get('submission') or '',
            given_answers=payload.get('answers') or {},
            ordered_answers=payload.get('ordered_answers'),
            duration_sec=int(payload.get('duration_sec') or 0),
            session_started_at=session_started_at,
            allow_empty_submission=bool(payload.get('allow_empty')),
            completion_trigger=payload.get('completion_trigger'),
            **_mock_submit_kwargs(request, payload),
        )
        if not result.get('success'):
            return JsonResponse(result, status=400)

        clear_quiz_attempt_start(request, pk)
        return JsonResponse(result)


class StudentSpeakingQuizSubmitView(StudentQuizTakeRequiredMixin, View):
    def post(self, request, pk):
        profile = get_student_profile(request.portal_user)
        mock_kwargs = _mock_submit_kwargs(request, {'mock': request.POST.get('mock')})
        quiz = get_student_speaking_quiz_take_data(
            profile.pk,
            pk,
            mock_attempt_id=mock_kwargs.get('mock_attempt_id'),
        )
        if not quiz:
            return JsonResponse({'success': False, 'error': 'Quiz not found.'}, status=404)
        if quiz.get('view_only') and not mock_kwargs.get('mock_attempt_id'):
            return JsonResponse(
                {'success': False, 'error': _('Your submission is awaiting teacher review.')},
                status=400,
            )

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

        try:
            duration_sec = int(request.POST.get('duration_sec') or 0)
        except (TypeError, ValueError):
            duration_sec = 0

        result = submit_speaking_quiz_attempt(
            student_id=profile.pk,
            quiz_id=pk,
            recording_files=recording_files,
            recording_durations=recording_durations,
            duration_sec=duration_sec,
            session_started_at=session_started_at,
            allow_empty_submission=request.POST.get('allow_empty') in ('1', 'true', 'True'),
            completion_trigger=request.POST.get('completion_trigger'),
            **_mock_submit_kwargs(request, {'mock': request.POST.get('mock')}),
        )
        if not result.get('success'):
            status = 400
            if result.get('error') == 'Quiz not found.':
                status = 404
            return JsonResponse(result, status=status)

        clear_quiz_attempt_start(request, pk)
        return JsonResponse(result)


class TeacherQuizResultsView(TeacherRequiredMixin, View):
    template_name = 'portals/teacher/quiz_results.html'

    def get(self, request):
        profile = get_teacher_profile(request.portal_user)
        return render(
            request,
            self.template_name,
            _portal_context(
                request,
                teacher=serialize_teacher(profile),
                pending_results=get_teacher_pending_quiz_results(profile.pk),
            ),
        )


class TeacherQuizResultReviewView(TeacherRequiredMixin, View):
    template_name = 'portals/teacher/quiz_result_review.html'

    def get(self, request, result_pk):
        profile = get_teacher_profile(request.portal_user)
        result = get_teacher_quiz_result_detail(profile.pk, result_pk)
        if not result:
            raise Http404
        return render(
            request,
            self.template_name,
            _portal_context(
                request,
                teacher=serialize_teacher(profile),
                result=result,
                back_url=reverse('portals:teacher-quiz-results'),
            ),
        )

    def post(self, request, result_pk):
        profile = get_teacher_profile(request.portal_user)
        result = get_teacher_quiz_result_detail(profile.pk, result_pk)
        if not result:
            raise Http404

        reading_correct_answers = None
        if result.get('is_reading'):
            reading_correct_answers = _parse_reading_correct_answers(request.POST)

        outcome = submit_teacher_quiz_review(
            teacher_id=profile.pk,
            result_id=result_pk,
            total_score=request.POST.get('total_score'),
            teacher_feedback=request.POST.get('teacher_feedback', ''),
            teacher_correct_answers=reading_correct_answers,
        )
        if outcome.get('success'):
            messages.success(request, _('Review saved.'))
            return redirect('portals:teacher-quiz-results')
        messages.error(request, outcome.get('error', _('Could not save review.')))
        return redirect('portals:teacher-quiz-result-review', result_pk=result_pk)
