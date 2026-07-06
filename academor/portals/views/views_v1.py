from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views import View

from portals.utils.quiz_stats import compute_quiz_average_stats, compute_weekly_average_stats
from portals.utils.parent_access import parent_has_students, resolve_parent_student
from portals.utils.student_courses import QUIZ_HISTORY_INITIAL_SIZE, QUIZ_HISTORY_PAGE_SIZE
from portals.utils.queries import (
    build_lesson_category_tabs,
    build_lesson_period_tabs,
    build_lesson_subject_tabs,
    build_score_period_tabs,
    prepare_teacher_scores_with_groups,
    resolve_score_group_param,
    get_parent_child_attendance,
    get_parent_child_attendance_detail,
    get_parent_child_quiz_results,
    get_parent_dashboard_data,
    get_parent_profile,
    get_portal_role,
    get_student_dashboard_data,
    get_student_lessons,
    get_student_profile,
    get_student_lesson,
    get_lesson_detail,
    get_student_schedules,
    get_student_scores,
    get_student_quiz_results,
    get_student_video_records,
    get_teacher_dashboard_data,
    get_teacher_group_detail,
    get_teacher_lessons,
    get_teacher_profile,
    get_teacher_quiz_detail,
    get_teacher_quiz_categories,
    get_teacher_quiz_category,
    get_teacher_quizzes_for_category,
    get_student_quiz_categories,
    get_student_quiz_category,
    get_student_quizzes_for_category,
    build_quiz_service_tabs,
    get_teacher_scores,
    get_teacher_student_attendance_detail,
    get_teacher_student_group_names,
    get_teacher_student_quiz_results,
    get_teacher_student_scores,
    group_scores_by_day,
    resolve_scores_view_param,
    split_score_rows_by_source,
    split_student_quiz_results,
    split_teacher_score_rows,
    get_teacher_classrooms,
    get_student_classrooms,
    get_parent_classrooms,
    build_classroom_group_tabs,
    get_classroom_detail,
    serialize_group,
    serialize_parent,
    serialize_student,
    serialize_teacher,
)
from portals.utils.teacher_attendance_hub import build_teacher_attendance_hub
from portals.utils.weekly_scores import (
    get_student_weekly_scores,
    get_teacher_student_weekly_scores,
    get_teacher_weekly_scores_list,
)
from portals.utils.teacher_access import get_teacher_lesson, get_teacher_student, teacher_groups_qs
from portals.utils.teacher_schedule import (
    build_student_week_calendar,
    build_teacher_week_calendar,
    parse_week_start,
)
from portals.views.mixins import (
    ParentRequiredMixin,
    PortalLoginRequiredMixin,
    StudentRequiredMixin,
    TeacherRequiredMixin,
)


def _portal_context(request, **extra):
    user = request.portal_user
    ctx = {'portal_role': get_portal_role(user)}
    ctx.update(extra)
    return ctx


class PortalDashboardView(PortalLoginRequiredMixin, View):
    """Send user to the dashboard for their portal role."""

    def get(self, request):
        role = get_portal_role(request.portal_user)
        if role == 'teacher':
            return redirect('portals:teacher-dashboard')
        if role == 'student':
            return redirect('portals:student-dashboard')
        if role == 'parent':
            return redirect('portals:parent-dashboard')
        return render(
            request,
            'portals/dashboard.html',
            _portal_context(request, role=None),
        )


# ---------------------------------------------------------------------------
# Teacher
# ---------------------------------------------------------------------------

class TeacherDashboardView(TeacherRequiredMixin, View):
    template_name = 'portals/teacher/dashboard.html'

    def get(self, request):
        profile = get_teacher_profile(request.portal_user)
        data = get_teacher_dashboard_data(request, profile.pk)
        return render(
            request,
            self.template_name,
            _portal_context(
                request,
                teacher=serialize_teacher(profile),
                **data,
            ),
        )


class TeacherGroupsListView(TeacherRequiredMixin, View):
    template_name = 'portals/teacher/groups.html'

    def get(self, request):
        profile = get_teacher_profile(request.portal_user)
        from django.db.models import Count

        groups = [
            serialize_group(g)
            for g in teacher_groups_qs(profile.pk)
            .select_related('teacher')
            .annotate(student_count=Count('students', distinct=True))
            .prefetch_related('students')
            .order_by('-is_active', 'name')
        ]
        return render(
            request,
            self.template_name,
            _portal_context(
                request,
                teacher=serialize_teacher(profile),
                groups=groups,
            ),
        )


class TeacherGroupDetailView(TeacherRequiredMixin, View):
    template_name = 'portals/teacher/group_detail.html'

    def get(self, request, pk):
        profile = get_teacher_profile(request.portal_user)
        group = get_teacher_group_detail(profile.pk, pk)
        if not group:
            raise Http404
        return render(
            request,
            self.template_name,
            _portal_context(request, teacher=serialize_teacher(profile), group=group),
        )


class TeacherLessonsListView(TeacherRequiredMixin, View):
    template_name = 'portals/teacher/lessons.html'

    def get(self, request):
        profile = get_teacher_profile(request.portal_user)
        lessons = get_teacher_lessons(profile.pk)
        return render(
            request,
            self.template_name,
            _portal_context(
                request,
                teacher=serialize_teacher(profile),
                lessons=lessons,
                subject_tabs=build_lesson_subject_tabs(lessons),
                category_tabs=build_lesson_category_tabs(lessons),
                period_tabs=build_lesson_period_tabs(lessons),
            ),
        )


class TeacherLessonDetailView(TeacherRequiredMixin, View):
    template_name = 'portals/lesson_detail.html'

    def get(self, request, pk):
        profile = get_teacher_profile(request.portal_user)
        lesson = get_teacher_lesson(profile.pk, pk)
        if not lesson:
            raise Http404
        return render(
            request,
            self.template_name,
            _portal_context(
                request,
                teacher=serialize_teacher(profile),
                lesson=get_lesson_detail(lesson),
                page_eyebrow='Teacher',
                back_url=reverse('portals:teacher-lessons'),
                edit_url=reverse('portals:teacher-lesson-edit', kwargs={'pk': pk}),
                group_detail_url=reverse('portals:teacher-group-detail', kwargs={'pk': lesson.group_id}),
            ),
        )


class TeacherAttendanceListView(TeacherRequiredMixin, View):
    template_name = 'portals/teacher/attendance.html'

    def get(self, request):
        profile = get_teacher_profile(request.portal_user)
        hub = build_teacher_attendance_hub(profile.pk)
        return render(
            request,
            self.template_name,
            _portal_context(
                request,
                teacher=serialize_teacher(profile),
                students=hub['students'],
                attendance_groups=hub['groups'],
                hub_stats=hub['stats']['all'],
                hub_stats_map=hub['stats'],
            ),
        )


class TeacherStudentAttendanceDetailView(TeacherRequiredMixin, View):
    template_name = 'portals/teacher/attendance_student.html'

    def get(self, request, student_pk):
        profile = get_teacher_profile(request.portal_user)
        detail = get_teacher_student_attendance_detail(profile.pk, student_pk)
        if not detail:
            raise Http404
        return render(
            request,
            self.template_name,
            _portal_context(
                request,
                teacher=serialize_teacher(profile),
                **detail,
            ),
        )


_TEACHER_STUDENT_PROFILE_TABS = frozenset({'quiz-results', 'duration', 'daily-scores', 'weekly-scores'})


def _teacher_student_profile_stats(quiz_results, scores, daily_score_history):
    quiz_average = compute_quiz_average_stats(quiz_results)
    durations = [int(row.get('duration_sec') or 0) for row in quiz_results]
    duration_count = len([d for d in durations if d > 0])
    avg_duration_sec = round(sum(durations) / duration_count) if duration_count else 0
    return {
        'quiz_count': len(quiz_results),
        'pending_count': quiz_average['pending_count'],
        'avg_score_pct': quiz_average['avg_score_pct'],
        'graded_count': quiz_average['graded_count'],
        'score_tier': quiz_average['tier'],
        'quiz_average': quiz_average,
        'total_duration_sec': sum(durations),
        'max_duration_sec': max(durations) if durations else 0,
        'min_duration_sec': min(d for d in durations if d > 0) if duration_count else 0,
        'avg_duration_sec': avg_duration_sec,
        'duration_attempt_count': duration_count,
        'score_count': len(scores),
        'active_days': len(daily_score_history),
    }


class TeacherStudentProfileView(TeacherRequiredMixin, View):
    template_name = 'portals/teacher/student_profile.html'
    tab_panel_template_name = 'portals/includes/teacher_student_profile_tab_panel.html'

    def _build_context(self, request, profile, student, tab):
        student_pk = student.pk
        quiz_results = get_teacher_student_quiz_results(profile.pk, student_pk)
        manual_quiz_results, auto_quiz_results = split_student_quiz_results(quiz_results)
        scores = get_teacher_student_scores(profile.pk, student_pk)
        daily_score_history = group_scores_by_day(scores)
        attendance_detail = get_teacher_student_attendance_detail(profile.pk, student_pk)
        quiz_average = compute_quiz_average_stats(quiz_results)
        weekly_scores = get_teacher_student_weekly_scores(profile.pk, student_pk)
        return _portal_context(
            request,
            teacher=serialize_teacher(profile),
            student=serialize_student(student),
            groups=get_teacher_student_group_names(profile.pk, student_pk),
            active_tab=tab,
            quiz_results=quiz_results,
            manual_quiz_results=manual_quiz_results,
            auto_quiz_results=auto_quiz_results,
            duration_history=quiz_results,
            daily_score_history=daily_score_history,
            stats=_teacher_student_profile_stats(quiz_results, scores, daily_score_history),
            quiz_average=quiz_average,
            attendance_summary=attendance_detail['summary'] if attendance_detail else None,
            attendance_records=attendance_detail['records'] if attendance_detail else [],
            weekly_scores=weekly_scores,
        )

    def get(self, request, student_pk):
        profile = get_teacher_profile(request.portal_user)
        student = get_teacher_student(profile.pk, student_pk)
        if not student:
            raise Http404
        tab = request.GET.get('tab', 'quiz-results')
        if tab not in _TEACHER_STUDENT_PROFILE_TABS:
            tab = 'quiz-results'
        context = self._build_context(request, profile, student, tab)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render(request, self.tab_panel_template_name, context)
        return render(request, self.template_name, context)


class TeacherScheduleView(TeacherRequiredMixin, View):
    template_name = 'portals/teacher/schedule.html'

    def get(self, request):
        profile = get_teacher_profile(request.portal_user)
        week_start = parse_week_start(request.GET.get('week'))
        calendar = build_teacher_week_calendar(profile.pk, week_start=week_start)
        groups = [
            serialize_group(g)
            for g in teacher_groups_qs(profile.pk).order_by('-is_active', 'name')
        ]
        return render(
            request,
            self.template_name,
            _portal_context(
                request,
                teacher=serialize_teacher(profile),
                calendar=calendar,
                groups=groups,
            ),
        )


class TeacherScoresListView(TeacherRequiredMixin, View):
    template_name = 'portals/teacher/scores.html'

    def get(self, request):
        profile = get_teacher_profile(request.portal_user)
        quiz_scores = get_teacher_scores(profile.pk)
        weekly_scores = get_teacher_weekly_scores_list(profile.pk)
        grouped = prepare_teacher_scores_with_groups(profile.pk, quiz_scores, weekly_scores)
        quiz_scores = grouped['quiz_scores']
        weekly_scores = grouped['weekly_scores']
        score_group_tabs = grouped['score_groups']
        return render(
            request,
            self.template_name,
            _portal_context(
                request,
                teacher=serialize_teacher(profile),
                quiz_scores=quiz_scores,
                weekly_scores=weekly_scores,
                scores_view=resolve_scores_view_param(request, quiz_scores, weekly_scores),
                score_detail_url_name='portals:teacher-score-detail',
                show_teacher_column=False,
                show_comment_column=True,
                period_tabs=build_score_period_tabs(quiz_scores, weekly_scores),
                score_groups=score_group_tabs,
                active_score_group=resolve_score_group_param(request, score_group_tabs),
                total_score_count=grouped['total_score_count'],
            ),
        )


class TeacherQuizzesListView(TeacherRequiredMixin, View):
    template_name = 'portals/teacher/quiz_categories.html'

    def get(self, request):
        profile = get_teacher_profile(request.portal_user)
        categories = get_teacher_quiz_categories(profile.pk)
        return render(
            request,
            self.template_name,
            _portal_context(
                request,
                teacher=serialize_teacher(profile),
                categories=categories,
                service_tabs=build_quiz_service_tabs(categories),
            ),
        )


class TeacherQuizCategoryDetailView(TeacherRequiredMixin, View):
    template_name = 'portals/teacher/quiz_category_detail.html'

    def get(self, request, category_pk):
        profile = get_teacher_profile(request.portal_user)
        category = get_teacher_quiz_category(profile.pk, category_pk)
        if not category:
            raise Http404
        return render(
            request,
            self.template_name,
            _portal_context(
                request,
                teacher=serialize_teacher(profile),
                category=category,
                quizzes=get_teacher_quizzes_for_category(profile.pk, category_pk),
            ),
        )


class TeacherQuizDetailView(TeacherRequiredMixin, View):
    template_name = 'portals/teacher/quiz_detail.html'

    def get(self, request, pk):
        profile = get_teacher_profile(request.portal_user)
        quiz = get_teacher_quiz_detail(profile.pk, pk)
        if not quiz:
            raise Http404
        return render(
            request,
            self.template_name,
            _portal_context(request, teacher=serialize_teacher(profile), quiz=quiz),
        )


# ---------------------------------------------------------------------------
# Student
# ---------------------------------------------------------------------------

class StudentDashboardView(StudentRequiredMixin, View):
    template_name = 'portals/student/dashboard.html'

    def get(self, request):
        profile = get_student_profile(request.portal_user)
        data = get_student_dashboard_data(request, profile.pk)
        return render(
            request,
            self.template_name,
            _portal_context(
                request,
                student=serialize_student(profile),
                **data,
            ),
        )


class StudentScheduleView(StudentRequiredMixin, View):
    template_name = 'portals/student/schedule.html'

    def get(self, request):
        profile = get_student_profile(request.portal_user)
        week_start = parse_week_start(request.GET.get('week'))
        return render(
            request,
            self.template_name,
            _portal_context(
                request,
                student=serialize_student(profile),
                calendar=build_student_week_calendar(profile.pk, week_start=week_start),
                week_nav_prefix='',
            ),
        )


class StudentLessonsView(StudentRequiredMixin, View):
    template_name = 'portals/student/lessons.html'

    def get(self, request):
        profile = get_student_profile(request.portal_user)
        lessons = get_student_lessons(profile.pk)
        return render(
            request,
            self.template_name,
            _portal_context(
                request,
                student=serialize_student(profile),
                lessons=lessons,
                subject_tabs=build_lesson_subject_tabs(lessons),
                category_tabs=build_lesson_category_tabs(lessons),
                period_tabs=build_lesson_period_tabs(lessons),
                video_records=get_student_video_records(profile.pk),
            ),
        )


class StudentLessonDetailView(StudentRequiredMixin, View):
    template_name = 'portals/lesson_detail.html'

    def get(self, request, pk):
        profile = get_student_profile(request.portal_user)
        lesson = get_student_lesson(profile.pk, pk)
        if not lesson:
            raise Http404
        return render(
            request,
            self.template_name,
            _portal_context(
                request,
                student=serialize_student(profile),
                lesson=get_lesson_detail(lesson),
                page_eyebrow='Student',
                back_url=reverse('portals:student-lessons'),
            ),
        )


class StudentScoresView(StudentRequiredMixin, View):
    template_name = 'portals/student/scores.html'

    def get(self, request):
        profile = get_student_profile(request.portal_user)
        all_quiz_scores = get_student_scores(profile.pk)
        weekly_scores = get_student_weekly_scores(profile.pk)
        quiz_results = get_student_quiz_results(profile.pk)
        quiz_scores = all_quiz_scores[:QUIZ_HISTORY_INITIAL_SIZE]
        total_quiz_scores = len(all_quiz_scores)
        mock_attempts = None
        from portals.utils.ielts_mock_test import (
            get_student_completed_mock_attempts,
            serialize_mock_attempt_summary,
            student_can_access_ielts_mock,
        )
        if student_can_access_ielts_mock(profile.pk):
            mock_attempts = [
                serialize_mock_attempt_summary(attempt)
                for attempt in get_student_completed_mock_attempts(profile.pk)
            ]
        return render(
            request,
            self.template_name,
            _portal_context(
                request,
                student=serialize_student(profile),
                quiz_scores=quiz_scores,
                quiz_scores_total_count=total_quiz_scores,
                quiz_scores_lazy_load=total_quiz_scores > QUIZ_HISTORY_INITIAL_SIZE,
                quiz_scores_load_url=reverse('portals:student-quiz-history-load'),
                quiz_average=compute_quiz_average_stats(quiz_results),
                weekly_scores=weekly_scores,
                mock_attempts=mock_attempts,
                mock_detail_url_name='portals:student-ielts-mock-complete',
                scores_view=resolve_scores_view_param(
                    request, all_quiz_scores, weekly_scores, mock_attempts=mock_attempts
                ),
                score_detail_url_name='portals:student-score-detail',
                show_comment_column=False,
                show_teacher_column=True,
                period_tabs=build_score_period_tabs(all_quiz_scores, weekly_scores),
                weekly_average=compute_weekly_average_stats(weekly_scores),
            ),
        )


class StudentQuizHistoryLoadView(StudentRequiredMixin, View):
    def get(self, request):
        try:
            offset = max(0, int(request.GET.get('offset', 0)))
        except (TypeError, ValueError):
            offset = 0

        profile = get_student_profile(request.portal_user)
        all_quiz_scores = get_student_scores(profile.pk)
        page = all_quiz_scores[offset:offset + QUIZ_HISTORY_PAGE_SIZE]
        html = render_to_string(
            'portals/includes/quiz_score_history_rows.html',
            {
                'quiz_scores': page,
                'score_detail_url_name': 'portals:student-score-detail',
                'show_student_column': False,
                'show_quiz_history_empty': False,
            },
            request=request,
        )
        next_offset = offset + len(page)
        return JsonResponse(
            {
                'html': html,
                'has_more': next_offset < len(all_quiz_scores),
                'next_offset': next_offset,
            }
        )


class StudentQuizzesView(StudentRequiredMixin, View):
    template_name = 'portals/student/quiz_categories.html'

    def get(self, request):
        profile = get_student_profile(request.portal_user)
        categories = get_student_quiz_categories(profile.pk)
        return render(
            request,
            self.template_name,
            _portal_context(
                request,
                student=serialize_student(profile),
                categories=categories,
                service_tabs=build_quiz_service_tabs(categories),
                can_take_quiz=True,
                category_detail_url_name='portals:student-quiz-category',
                category_url_suffix='',
            ),
        )


class StudentQuizCategoryDetailView(StudentRequiredMixin, View):
    template_name = 'portals/student/quiz_category_detail.html'

    def get(self, request, category_pk):
        profile = get_student_profile(request.portal_user)
        category = get_student_quiz_category(profile.pk, category_pk)
        if not category:
            raise Http404
        return render(
            request,
            self.template_name,
            _portal_context(
                request,
                student=serialize_student(profile),
                category=category,
                quizzes=get_student_quizzes_for_category(profile.pk, category_pk),
                can_take_quiz=True,
                categories_back_url='portals:student-quizzes',
                category_url_suffix='',
            ),
        )


# ---------------------------------------------------------------------------
# Parent
# ---------------------------------------------------------------------------

def _parent_child_context(request, profile):
    student = resolve_parent_student(profile, request)
    children = [
        serialize_student(row)
        for row in profile.students.select_related('user').order_by('user__username', 'id')
    ]
    selected = serialize_student(student) if student else None
    return {
        'children': children,
        'selected_student': selected,
        'student_query': f'?student={student.pk}' if student and len(children) > 1 else '',
        'week_nav_prefix': f'student={student.pk}&' if student and len(children) > 1 else '',
    }


def _parent_student_page(request, profile):
    if not parent_has_students(profile):
        raise Http404
    student = resolve_parent_student(profile, request)
    if not student:
        raise Http404
    return student, _parent_child_context(request, profile)


def _render_parent_child_page(request, profile, template_name, *, page_subtitle, **extra):
    student, child_ctx = _parent_student_page(request, profile)
    return render(
        request,
        template_name,
        _portal_context(
            request,
            page_eyebrow='Parent',
            page_subtitle=page_subtitle,
            parent=serialize_parent(profile),
            student=child_ctx['selected_student'],
            **child_ctx,
            **extra,
        ),
    )


class ParentDashboardView(ParentRequiredMixin, View):
    template_name = 'portals/parent/dashboard.html'

    def get(self, request):
        profile = get_parent_profile(request.portal_user)
        data = get_parent_dashboard_data(request, profile.pk)
        return render(
            request,
            self.template_name,
            _portal_context(
                request,
                parent=serialize_parent(profile),
                **data,
            ),
        )


class ParentAttendanceView(ParentRequiredMixin, View):
    template_name = 'portals/parent/attendance.html'

    def get(self, request):
        profile = get_parent_profile(request.portal_user)
        student, child_ctx = _parent_student_page(request, profile)
        detail = get_parent_child_attendance_detail(student.pk)
        if not detail:
            raise Http404
        return render(
            request,
            self.template_name,
            _portal_context(
                request,
                page_eyebrow='Parent',
                page_subtitle=_("Student attendance history."),
                parent=serialize_parent(profile),
                **detail,
                **child_ctx,
            ),
        )


class ParentScheduleView(ParentRequiredMixin, View):
    template_name = 'portals/student/schedule.html'

    def get(self, request):
        profile = get_parent_profile(request.portal_user)
        student, _child_ctx = _parent_student_page(request, profile)
        week_start = parse_week_start(request.GET.get('week'))
        return _render_parent_child_page(
            request,
            profile,
            self.template_name,
            page_subtitle=_("Student weekly class timetable."),
            calendar=build_student_week_calendar(student.pk, week_start=week_start),
        )


class ParentLessonsView(ParentRequiredMixin, View):
    template_name = 'portals/student/lessons.html'

    def get(self, request):
        profile = get_parent_profile(request.portal_user)
        student, child_ctx = _parent_student_page(request, profile)
        lessons = get_student_lessons(student.pk)
        return _render_parent_child_page(
            request,
            profile,
            self.template_name,
            page_subtitle=_("Student lesson materials and video recordings."),
            lessons=lessons,
            subject_tabs=build_lesson_subject_tabs(lessons),
            category_tabs=build_lesson_category_tabs(lessons),
            period_tabs=build_lesson_period_tabs(lessons),
            video_records=get_student_video_records(student.pk),
        )


class ParentLessonDetailView(ParentRequiredMixin, View):
    template_name = 'portals/lesson_detail.html'

    def get(self, request, pk):
        profile = get_parent_profile(request.portal_user)
        student, child_ctx = _parent_student_page(request, profile)
        lesson = get_student_lesson(student.pk, pk)
        if not lesson:
            raise Http404
        back_url = reverse('portals:parent-lessons') + child_ctx.get('student_query', '')
        return render(
            request,
            self.template_name,
            _portal_context(
                request,
                page_eyebrow='Parent',
                page_subtitle=_("Student lesson materials and video recordings."),
                parent=serialize_parent(profile),
                student=child_ctx['selected_student'],
                lesson=get_lesson_detail(lesson),
                back_url=back_url,
                **child_ctx,
            ),
        )


class ParentScoresView(ParentRequiredMixin, View):
    template_name = 'portals/parent/scores.html'

    def get(self, request):
        from portals.utils.ielts_mock_test import (
            get_student_completed_mock_attempts,
            serialize_mock_attempt_summary,
            student_can_access_ielts_mock,
        )

        profile = get_parent_profile(request.portal_user)
        student, child_ctx = _parent_student_page(request, profile)
        quiz_scores = get_student_scores(student.pk)
        weekly_scores = get_student_weekly_scores(student.pk)
        quiz_results = get_parent_child_quiz_results(student.pk, parent_id=profile.pk)
        mock_attempts = None
        if student_can_access_ielts_mock(student.pk):
            mock_attempts = [
                serialize_mock_attempt_summary(attempt)
                for attempt in get_student_completed_mock_attempts(student.pk)
            ]
        return _render_parent_child_page(
            request,
            profile,
            self.template_name,
            page_subtitle=_('Quiz history, weekly grades, and mock test results for your linked student.'),
            quiz_scores=quiz_scores,
            weekly_scores=weekly_scores,
            quiz_average=compute_quiz_average_stats(quiz_results),
            scores_view=resolve_scores_view_param(
                request, quiz_scores, weekly_scores, mock_attempts=mock_attempts
            ),
            score_detail_url_name='portals:parent-score-detail',
            mock_detail_url_name='portals:parent-ielts-mock-detail',
            mock_detail_url_suffix=child_ctx.get('student_query', ''),
            show_comment_column=False,
            show_teacher_column=True,
            period_tabs=build_score_period_tabs(quiz_scores, weekly_scores),
            weekly_average=compute_weekly_average_stats(weekly_scores),
            mock_attempts=mock_attempts,
        )


def _classrooms_back_url(request):
    role = get_portal_role(request.portal_user)
    if role == 'teacher':
        return reverse('portals:teacher-dashboard')
    if role == 'parent':
        return reverse('portals:parent-dashboard')
    return reverse('portals:student-dashboard')


def _classrooms_list_url(request):
    role = get_portal_role(request.portal_user)
    if role == 'teacher':
        return reverse('portals:teacher-classrooms')
    if role == 'parent':
        return reverse('portals:parent-classrooms')
    return reverse('portals:student-classrooms')


class ClassroomsListView(PortalLoginRequiredMixin, View):
    template_name = 'portals/classrooms.html'

    def get(self, request):
        role = get_portal_role(request.portal_user)
        if role not in ('teacher', 'student', 'parent'):
            return redirect('portals:dashboard')

        child_ctx = {}
        if role == 'teacher':
            profile = get_teacher_profile(request.portal_user)
            classrooms = get_teacher_classrooms(profile.pk) if profile else []
        elif role == 'student':
            profile = get_student_profile(request.portal_user)
            classrooms = get_student_classrooms(profile.pk) if profile else []
        else:
            profile = get_parent_profile(request.portal_user)
            if parent_has_students(profile):
                child_ctx = _parent_child_context(request, profile)
                student = resolve_parent_student(profile, request)
                if not student:
                    # Invalid ?student= param: match _parent_student_page
                    # instead of silently showing all children's classrooms.
                    raise Http404
                classrooms = get_parent_classrooms(profile.pk, student_id=student.pk)
            else:
                classrooms = get_parent_classrooms(profile.pk) if profile else []

        ctx = _portal_context(
            request,
            classrooms=classrooms,
            group_tabs=build_classroom_group_tabs(classrooms),
            back_url=_classrooms_back_url(request),
        )
        if child_ctx:
            ctx.update(child_ctx)
        return render(request, self.template_name, ctx)


class ClassroomDetailView(PortalLoginRequiredMixin, View):
    template_name = 'portals/classroom_detail.html'

    def get(self, request, pk):
        role = get_portal_role(request.portal_user)
        if role not in ('teacher', 'student', 'parent'):
            return redirect('portals:dashboard')

        classroom = None
        if role == 'teacher':
            profile = get_teacher_profile(request.portal_user)
            if profile:
                classroom = get_classroom_detail(pk, role='teacher', profile_id=profile.pk)
        elif role == 'student':
            profile = get_student_profile(request.portal_user)
            if profile:
                classroom = get_classroom_detail(pk, role='student', profile_id=profile.pk)
        else:
            profile = get_parent_profile(request.portal_user)
            if not profile:
                raise Http404
            if parent_has_students(profile):
                student = resolve_parent_student(profile, request)
                if not student:
                    raise Http404
                classroom = get_classroom_detail(pk, role='student', profile_id=student.pk)
            else:
                classroom = get_classroom_detail(pk, role='parent', profile_id=profile.pk)

        if not classroom:
            raise Http404
        edit_url = None
        if role == 'teacher':
            edit_url = reverse('portals:teacher-classroom-edit', kwargs={'pk': pk})
        return render(
            request,
            self.template_name,
            _portal_context(
                request,
                classroom=classroom,
                back_url=_classrooms_list_url(request),
                edit_url=edit_url,
            ),
        )
