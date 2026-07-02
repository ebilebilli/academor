import json

from django.contrib import messages
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views import View

from portals.utils.portal_session import (
    clear_quiz_attempt_start,
    get_quiz_attempt_start,
    set_quiz_attempt_start,
)
from portals.utils.queries import (
    get_student_manual_quiz_take_data,
    get_student_profile,
    get_student_quiz_take_data,
    get_teacher_pending_quiz_results,
    get_teacher_profile,
    get_teacher_quiz_result_detail,
    serialize_teacher,
)
from portals.utils.quiz_submit import (
    student_has_quiz_attempt,
    submit_manual_quiz_attempt,
    submit_teacher_quiz_review,
    submit_variant_quiz_attempt,
)
from portals.views.mixins import StudentQuizTakeRequiredMixin, TeacherRequiredMixin
from portals.views.views_v1 import _portal_context


def _quiz_back_url(quiz: dict) -> str:
    category_pk = quiz.get('category_id')
    if category_pk is not None:
        return reverse('portals:student-quiz-category', kwargs={'category_pk': category_pk})
    return reverse('portals:student-quizzes')


class StudentQuizTakeView(StudentQuizTakeRequiredMixin, View):
    template_name = 'portals/student/quiz_take.html'

    def get(self, request, pk):
        profile = get_student_profile(request.portal_user)
        if student_has_quiz_attempt(profile.pk, pk):
            messages.info(request, _('You have already completed this quiz.'))
            return redirect('portals:student-scores')

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


class StudentManualQuizTakeView(StudentQuizTakeRequiredMixin, View):
    template_name = 'portals/student/quiz_take_manual.html'

    def get(self, request, pk):
        profile = get_student_profile(request.portal_user)
        quiz = get_student_manual_quiz_take_data(profile.pk, pk)
        if not quiz:
            raise Http404

        return render(
            request,
            self.template_name,
            _portal_context(
                request,
                quiz=quiz,
                submit_url=reverse('portals:student-manual-quiz-submit', kwargs={'pk': pk}),
                start_url=reverse('portals:student-quiz-start', kwargs={'pk': pk}),
                back_url=_quiz_back_url(quiz),
            ),
        )


class StudentQuizStartView(StudentQuizTakeRequiredMixin, View):
    def post(self, request, pk):
        profile = get_student_profile(request.portal_user)
        quiz = get_student_quiz_take_data(profile.pk, pk)
        if not quiz:
            quiz = get_student_manual_quiz_take_data(profile.pk, pk)
        if not quiz:
            return JsonResponse({'success': False, 'error': _('Quiz not found.')}, status=404)
        if quiz.get('view_only'):
            return JsonResponse(
                {'success': False, 'error': _('Your submission is awaiting teacher review.')},
                status=400,
            )

        set_quiz_attempt_start(request, pk)
        return JsonResponse({'success': True})


class StudentQuizCancelView(StudentQuizTakeRequiredMixin, View):
    """Leave the quiz intro without counting an attempt."""

    def get(self, request, pk):
        profile = get_student_profile(request.portal_user)
        quiz = get_student_quiz_take_data(profile.pk, pk)
        if not quiz:
            quiz = get_student_manual_quiz_take_data(profile.pk, pk)
        if not quiz:
            raise Http404

        clear_quiz_attempt_start(request, pk)

        next_url = (request.GET.get('next') or '').strip()
        if next_url and next_url.startswith('/portal/'):
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
        quiz = get_student_manual_quiz_take_data(profile.pk, pk)
        if not quiz:
            return JsonResponse({'success': False, 'error': 'Quiz not found.'}, status=404)
        if quiz.get('view_only'):
            return JsonResponse(
                {'success': False, 'error': _('Your submission is awaiting teacher review.')},
                status=400,
            )

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

        result = submit_manual_quiz_attempt(
            student_id=profile.pk,
            quiz_id=pk,
            student_submission=payload.get('submission') or '',
            given_answers=payload.get('answers') or {},
            ordered_answers=payload.get('ordered_answers'),
            duration_sec=int(payload.get('duration_sec') or 0),
            session_started_at=session_started_at,
            allow_empty_submission=bool(payload.get('allow_empty')),
        )
        if not result.get('success'):
            return JsonResponse(result, status=400)

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
        if not get_teacher_quiz_result_detail(profile.pk, result_pk):
            raise Http404

        outcome = submit_teacher_quiz_review(
            teacher_id=profile.pk,
            result_id=result_pk,
            total_score=request.POST.get('total_score'),
            teacher_feedback=request.POST.get('teacher_feedback', ''),
        )
        if outcome.get('success'):
            messages.success(request, _('Review saved.'))
            return redirect('portals:teacher-quiz-results')
        messages.error(request, outcome.get('error', _('Could not save review.')))
        return redirect('portals:teacher-quiz-result-review', result_pk=result_pk)
