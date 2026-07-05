from django.contrib import messages
from datetime import timedelta

from django.http import Http404, JsonResponse
from django.template.loader import render_to_string
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views import View

from portals.models import Attendance, Schedule
from portals.teacher_forms import (
    TeacherLessonForm,
    TeacherScheduleForm,
    TeacherTextbookForm,
    build_session_attendance_form,
)
from portals.utils.queries import (
    get_teacher_attendance_students,
    get_teacher_profile,
    serialize_teacher,
)
from portals.utils.teacher_access import (
    get_teacher_group,
    get_teacher_lesson,
    get_teacher_schedule,
    get_teacher_textbook,
)
from portals.utils.teacher_attendance import (
    parse_student_ids,
    save_session_attendance,
    selected_student_ids_from_post,
)
from portals.utils.teacher_courses import course_type_choices_for_teacher
from portals.utils.teacher_schedule import build_teacher_week_calendar, parse_week_start
from portals.utils.weekly_scores import (
    build_teacher_weekly_score_view,
    parse_weekly_score_post,
    save_teacher_weekly_scores,
    student_ids_open_for_scoring,
)
from portals.views.mixins import TeacherRequiredMixin, TeacherScheduleMutationForbiddenMixin


def _teacher_ctx(request, **extra):
    profile = get_teacher_profile(request.portal_user)
    ctx = {'teacher': serialize_teacher(profile), 'portal_role': 'teacher'}
    ctx.update(extra)
    return ctx


def _form_response(request, template, form, *, title, subtitle='', cancel_href, extra=None):
    ctx = _teacher_ctx(
        request,
        form=form,
        form_title=title,
        form_subtitle=subtitle,
        cancel_href=cancel_href,
        **(extra or {}),
    )
    return render(request, template, ctx)


def _schedule_calendar_url(week=None):
    url = reverse('portals:teacher-schedule')
    if week:
        return f'{url}?week={week}'
    return url


def _schedule_form_cancel_href(request, *, group_pk=None):
    if request.GET.get('return_to') == 'schedule' or request.POST.get('return_to') == 'schedule':
        week = request.GET.get('week') or request.POST.get('return_week')
        return _schedule_calendar_url(week)
    if group_pk:
        return reverse('portals:teacher-group-detail', kwargs={'pk': group_pk})
    return reverse('portals:teacher-schedule')


def _schedule_form_redirect(request, *, group_pk=None):
    from django.shortcuts import redirect

    return redirect(_schedule_form_cancel_href(request, group_pk=group_pk))


def _schedule_form_extra(request):
    extra = {}
    if request.GET.get('return_to') == 'schedule':
        extra['return_to'] = 'schedule'
        week = request.GET.get('week')
        if week:
            extra['return_week'] = week
    return extra


def _attendance_picker_context(request, teacher, *, entry_mode='calendar'):
    week_start = parse_week_start(request.GET.get('week'))
    student_ids = parse_student_ids(request.GET.getlist('students') or request.GET.get('students'))
    calendar = build_teacher_week_calendar(
        teacher.pk,
        week_start=week_start,
        student_ids=student_ids or None,
    )
    picker_students = None
    if entry_mode == 'students':
        picker_students = get_teacher_attendance_students(teacher.pk)
    return {
        'mode': 'picker',
        'entry_mode': entry_mode,
        'calendar': calendar,
        'selected_student_ids': student_ids,
        'picker_students': picker_students,
        'students_no_common_group': bool(student_ids) and not calendar['has_sessions'],
    }


def _attendance_picker_url(entry_mode, week=None, student_ids=None):
    if entry_mode == 'students':
        base = reverse('portals:teacher-attendance-create')
    else:
        base = reverse('portals:teacher-attendance-session')
    params = []
    if week:
        params.append(f'week={week}')
    if student_ids:
        params.append('students=' + ','.join(str(sid) for sid in student_ids))
    if not params:
        return base
    return f'{base}?{"&".join(params)}'


class TeacherScheduleCreateView(TeacherScheduleMutationForbiddenMixin, TeacherRequiredMixin, View):
    template_name = 'portals/teacher/schedule_form.html'

    def get(self, request, group_pk):
        teacher = get_teacher_profile(request.portal_user)
        group = get_teacher_group(teacher.pk, group_pk)
        if not group:
            raise Http404
        return _form_response(
            request,
            self.template_name,
            TeacherScheduleForm(teacher.pk, group_fixed=True),
            title=_('Add schedule slot'),
            subtitle=group.name,
            cancel_href=_schedule_form_cancel_href(request, group_pk=group_pk),
            extra={'group': group, **_schedule_form_extra(request)},
        )

    def post(self, request, group_pk):
        teacher = get_teacher_profile(request.portal_user)
        group = get_teacher_group(teacher.pk, group_pk)
        if not group:
            raise Http404
        form = TeacherScheduleForm(teacher.pk, group_fixed=True, data=request.POST)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.group = group
            schedule.save()
            messages.success(request, _('Schedule slot added.'))
            return _schedule_form_redirect(request, group_pk=group_pk)
        return _form_response(
            request,
            self.template_name,
            form,
            title=_('Add schedule slot'),
            subtitle=group.name,
            cancel_href=_schedule_form_cancel_href(request, group_pk=group_pk),
            extra={'group': group, **_schedule_form_extra(request)},
        )


class TeacherScheduleSlotCreateView(TeacherScheduleMutationForbiddenMixin, TeacherRequiredMixin, View):
    template_name = 'portals/teacher/schedule_form.html'

    def get(self, request):
        teacher = get_teacher_profile(request.portal_user)
        initial = {}
        weekday = request.GET.get('weekday')
        if weekday is not None:
            try:
                initial['weekday'] = int(weekday)
            except (TypeError, ValueError):
                pass
        group_pk = request.GET.get('group')
        if group_pk:
            try:
                initial['group'] = int(group_pk)
            except (TypeError, ValueError):
                pass
        form = TeacherScheduleForm(teacher.pk, initial=initial)
        return _form_response(
            request,
            self.template_name,
            form,
            title=_('Add schedule slot'),
            subtitle=_('Pick a group, day, and time for this weekly slot.'),
            cancel_href=_schedule_form_cancel_href(request),
            extra={
                'return_to': 'schedule',
                'return_week': request.GET.get('week', ''),
            },
        )

    def post(self, request):
        teacher = get_teacher_profile(request.portal_user)
        form = TeacherScheduleForm(teacher.pk, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _('Schedule slot added.'))
            return _schedule_form_redirect(request)
        return _form_response(
            request,
            self.template_name,
            form,
            title=_('Add schedule slot'),
            subtitle=_('Pick a group, day, and time for this weekly slot.'),
            cancel_href=_schedule_form_cancel_href(request),
            extra={
                'return_to': request.POST.get('return_to', 'schedule'),
                'return_week': request.POST.get('return_week', ''),
            },
        )


class TeacherScheduleDeleteView(TeacherScheduleMutationForbiddenMixin, TeacherRequiredMixin, View):
    def post(self, request, schedule_pk):
        teacher = get_teacher_profile(request.portal_user)
        schedule = get_teacher_schedule(teacher.pk, schedule_pk)
        if not schedule:
            raise Http404
        week = request.POST.get('week', '').strip()
        schedule.delete()
        messages.success(request, _('Schedule slot deleted.'))
        return redirect(_schedule_calendar_url(week or None))


class TeacherScheduleEditView(TeacherScheduleMutationForbiddenMixin, TeacherRequiredMixin, View):
    template_name = 'portals/teacher/schedule_form.html'

    def get(self, request, schedule_pk):
        teacher = get_teacher_profile(request.portal_user)
        schedule = get_teacher_schedule(teacher.pk, schedule_pk)
        if not schedule:
            raise Http404
        group = schedule.group
        extra = {'group': group, **_schedule_form_extra(request)}
        if request.GET.get('return_to') == 'schedule':
            extra.setdefault('return_to', 'schedule')
            extra.setdefault('return_week', request.GET.get('week', ''))
        return _form_response(
            request,
            self.template_name,
            TeacherScheduleForm(teacher.pk, instance=schedule),
            title=_('Edit schedule slot'),
            subtitle=group.name,
            cancel_href=_schedule_form_cancel_href(request, group_pk=group.pk),
            extra=extra,
        )

    def post(self, request, schedule_pk):
        teacher = get_teacher_profile(request.portal_user)
        schedule = get_teacher_schedule(teacher.pk, schedule_pk)
        if not schedule:
            raise Http404
        group = schedule.group
        form = TeacherScheduleForm(teacher.pk, request.POST, instance=schedule)
        if form.is_valid():
            form.save()
            messages.success(request, _('Schedule slot updated.'))
            return _schedule_form_redirect(request, group_pk=group.pk)
        return _form_response(
            request,
            self.template_name,
            form,
            title=_('Edit schedule slot'),
            subtitle=group.name,
            cancel_href=_schedule_form_cancel_href(request, group_pk=group.pk),
            extra={
                'group': group,
                'return_to': request.POST.get('return_to', ''),
                'return_week': request.POST.get('return_week', ''),
            },
        )


class TeacherLessonCreateView(TeacherRequiredMixin, View):
    template_name = 'portals/teacher/lesson_form.html'

    def get(self, request):
        teacher = get_teacher_profile(request.portal_user)
        return _form_response(
            request,
            self.template_name,
            TeacherLessonForm(teacher.pk),
            title=_('Upload lesson'),
            subtitle=_('Name your lesson, pick groups, and attach materials in a few steps.'),
            cancel_href=reverse('portals:teacher-lessons'),
        )

    def post(self, request):
        teacher = get_teacher_profile(request.portal_user)
        form = TeacherLessonForm(teacher.pk, request.POST, request.FILES)
        if form.is_valid():
            lessons = form.save_for_groups(teacher)
            count = len(lessons)
            if count == 1:
                messages.success(request, _('Lesson uploaded successfully.'))
            else:
                messages.success(
                    request,
                    _('Lesson uploaded to %(count)s groups.') % {'count': count},
                )
            return redirect('portals:teacher-lessons')
        return _form_response(
            request,
            self.template_name,
            form,
            title=_('Upload lesson'),
            subtitle=_('Name your lesson, pick groups, and attach materials in a few steps.'),
            cancel_href=reverse('portals:teacher-lessons'),
        )


class TeacherLessonEditView(TeacherRequiredMixin, View):
    template_name = 'portals/teacher/lesson_form.html'

    def get(self, request, pk):
        teacher = get_teacher_profile(request.portal_user)
        lesson = get_teacher_lesson(teacher.pk, pk)
        if not lesson:
            raise Http404
        return _form_response(
            request,
            self.template_name,
            TeacherLessonForm(teacher.pk, instance=lesson),
            title=_('Edit lesson'),
            subtitle=lesson.display_name,
            cancel_href=reverse('portals:teacher-lessons'),
        )

    def post(self, request, pk):
        teacher = get_teacher_profile(request.portal_user)
        lesson = get_teacher_lesson(teacher.pk, pk)
        if not lesson:
            raise Http404
        form = TeacherLessonForm(teacher.pk, request.POST, request.FILES, instance=lesson)
        if form.is_valid():
            form.save()
            messages.success(request, _('Lesson updated successfully.'))
            return redirect('portals:teacher-lessons')
        return _form_response(
            request,
            self.template_name,
            form,
            title=_('Edit lesson'),
            subtitle=lesson.display_name,
            cancel_href=reverse('portals:teacher-lessons'),
        )


class TeacherAttendanceCreateView(TeacherRequiredMixin, View):
    """Student-first entry: pick students, then a session from the visual calendar."""
    template_name = 'portals/teacher/attendance_session.html'

    def get(self, request):
        schedule_id = request.GET.get('schedule')
        session_date = request.GET.get('date')
        if schedule_id and session_date:
            url = reverse('portals:teacher-attendance-session')
            query = f'schedule={schedule_id}&date={session_date}'
            students = request.GET.get('students')
            if students:
                query += f'&students={students}'
            return redirect(f'{url}?{query}')

        teacher = get_teacher_profile(request.portal_user)
        ctx = _attendance_picker_context(request, teacher, entry_mode='students')
        ctx['picker_url'] = reverse('portals:teacher-attendance-create')
        return render(
            request,
            self.template_name,
            _teacher_ctx(request, **ctx),
        )


class TeacherSessionAttendanceView(TeacherRequiredMixin, View):
    template_name = 'portals/teacher/attendance_session.html'

    def _load_session(self, request, teacher_id):
        schedule_id = request.GET.get('schedule') or request.POST.get('schedule')
        session_date_raw = request.GET.get('date') or request.POST.get('date')
        if not schedule_id or not session_date_raw:
            return None, None, None
        schedule = get_teacher_schedule(teacher_id, schedule_id)
        if not schedule:
            return None, None, None
        try:
            from datetime import date
            session_date = date.fromisoformat(str(session_date_raw).strip())
        except ValueError:
            return None, None, None
        from portals.utils.teacher_schedule import schedule_visible_on_date
        if not schedule_visible_on_date(schedule, session_date):
            return None, None, None
        students = list(
            schedule.group.students.select_related('user').order_by('user__username', 'id'),
        )
        existing = {
            row.student_id: row.status
            for row in Attendance.objects.filter(
                schedule=schedule,
                session_date=session_date,
            )
        }
        return schedule, session_date, (students, existing)

    def get(self, request):
        teacher = get_teacher_profile(request.portal_user)
        schedule, session_date, payload = self._load_session(request, teacher.pk)
        if not schedule:
            ctx = _attendance_picker_context(request, teacher, entry_mode='calendar')
            ctx['picker_url'] = reverse('portals:teacher-attendance-session')
            return render(
                request,
                self.template_name,
                _teacher_ctx(request, **ctx),
            )
        students, existing = payload
        if not students:
            messages.warning(request, _('This group has no students yet.'))
            return redirect('portals:teacher-group-detail', pk=schedule.group_id)
        preselected = parse_student_ids(
            request.GET.getlist('students') or request.GET.get('students')
        )
        preselected_set = {str(sid) for sid in preselected} if preselected else None
        form = build_session_attendance_form(students, existing=existing)
        return render(
            request,
            self.template_name,
            _teacher_ctx(
                request,
                mode='mark',
                form=form,
                schedule=schedule,
                session_date=session_date,
                students=students,
                preselected_set=preselected_set,
                selected_student_ids_param=request.GET.get('students', ''),
            ),
        )

    def post(self, request):
        teacher = get_teacher_profile(request.portal_user)
        schedule, session_date, payload = self._load_session(request, teacher.pk)
        if not schedule:
            raise Http404
        students, existing = payload
        selected_ids = selected_student_ids_from_post(request.POST)
        if not selected_ids:
            messages.error(request, _('Select at least one student.'))
            form = build_session_attendance_form(students, existing=existing)
            return render(
                request,
                self.template_name,
                _teacher_ctx(
                    request,
                    mode='mark',
                    form=form,
                    schedule=schedule,
                    session_date=session_date,
                    students=students,
                    preselected_set=set(),
                    selected_student_ids_param=request.POST.get('students', ''),
                ),
            )

        group_student_ids = {student.pk for student in students}
        if not set(selected_ids).issubset(group_student_ids):
            raise Http404

        selected_students = [student for student in students if student.pk in selected_ids]
        form = build_session_attendance_form(selected_students, existing=existing)(request.POST)
        if form.is_valid():
            status_map = {
                student.pk: form.cleaned_data[f'status_{student.pk}']
                for student in selected_students
            }
            count = save_session_attendance(schedule, session_date, status_map)
            messages.success(
                request,
                _('Attendance saved for %(count)s student(s).') % {'count': count},
            )
            week_start = session_date - timedelta(days=session_date.weekday())
            week = request.POST.get('week') or week_start.isoformat()
            return redirect(f'{reverse("portals:teacher-schedule")}?week={week}')
        return render(
            request,
            self.template_name,
            _teacher_ctx(
                request,
                mode='mark',
                form=form,
                schedule=schedule,
                session_date=session_date,
                students=students,
                preselected_set={str(sid) for sid in selected_ids},
                selected_student_ids_param=','.join(str(sid) for sid in selected_ids),
            ),
        )


class TeacherTextbookCreateView(TeacherRequiredMixin, View):
    template_name = 'portals/teacher/textbook_form.html'

    def get(self, request):
        teacher = get_teacher_profile(request.portal_user)
        return _form_response(
            request,
            self.template_name,
            TeacherTextbookForm(teacher.pk),
            title=_('Add textbook'),
            subtitle=_('Upload a PDF textbook for students in one of your groups.'),
            cancel_href=reverse('portals:teacher-classrooms'),
        )

    def post(self, request):
        teacher = get_teacher_profile(request.portal_user)
        form = TeacherTextbookForm(teacher.pk, request.POST, request.FILES)
        if form.is_valid():
            form.save(teacher=teacher)
            messages.success(request, _('Textbook added successfully.'))
            return redirect('portals:teacher-classrooms')
        return _form_response(
            request,
            self.template_name,
            form,
            title=_('Add textbook'),
            subtitle=_('Upload a PDF textbook for students in one of your groups.'),
            cancel_href=reverse('portals:teacher-classrooms'),
        )


class TeacherTextbookEditView(TeacherRequiredMixin, View):
    template_name = 'portals/teacher/textbook_form.html'

    def get(self, request, pk):
        teacher = get_teacher_profile(request.portal_user)
        textbook = get_teacher_textbook(teacher.pk, pk)
        if not textbook:
            raise Http404
        return _form_response(
            request,
            self.template_name,
            TeacherTextbookForm(teacher.pk, instance=textbook),
            title=_('Edit textbook'),
            subtitle=_('Update the name, description, or PDF for this group.'),
            cancel_href=reverse('portals:teacher-classroom-detail', kwargs={'pk': pk}),
        )

    def post(self, request, pk):
        teacher = get_teacher_profile(request.portal_user)
        textbook = get_teacher_textbook(teacher.pk, pk)
        if not textbook:
            raise Http404
        form = TeacherTextbookForm(teacher.pk, request.POST, request.FILES, instance=textbook)
        if form.is_valid():
            form.save(teacher=teacher)
            messages.success(request, _('Textbook updated successfully.'))
            return redirect('portals:teacher-classroom-detail', pk=pk)
        return _form_response(
            request,
            self.template_name,
            form,
            title=_('Edit textbook'),
            subtitle=_('Update the name, description, or PDF for this group.'),
            cancel_href=reverse('portals:teacher-classroom-detail', kwargs={'pk': pk}),
        )


class TeacherWeeklyScoresView(TeacherRequiredMixin, View):
    template_name = 'portals/teacher/weekly_scores.html'
    panel_template_name = 'portals/includes/teacher_weekly_scores_panel.html'

    def _resolve_group(self, request):
        group = request.GET.get('group') or request.POST.get('group') or 'all'
        return str(group)

    def _board_context(self, request, teacher):
        group = self._resolve_group(request)
        return build_teacher_weekly_score_view(
            teacher.pk,
            group_id=group,
        )

    def _render_panel(self, request, teacher, *, flash_message='', flash_level=''):
        ctx = self._board_context(request, teacher)
        ctx['flash_message'] = flash_message
        ctx['flash_level'] = flash_level
        return render_to_string(
            self.panel_template_name,
            _teacher_ctx(request, **ctx),
            request=request,
        )

    def get(self, request):
        teacher = get_teacher_profile(request.portal_user)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render(
                request,
                self.panel_template_name,
                _teacher_ctx(request, **self._board_context(request, teacher)),
            )
        return render(
            request,
            self.template_name,
            _teacher_ctx(request, **self._board_context(request, teacher)),
        )

    def post(self, request):
        from django.core.exceptions import ValidationError

        teacher = get_teacher_profile(request.portal_user)
        ctx = self._board_context(request, teacher)
        week_start = ctx['week_value']
        student_ids = student_ids_open_for_scoring(
            ctx['rows'],
            teacher_id=teacher.pk,
            week_start=week_start,
        )
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        if not ctx.get('has_any_editable_rows'):
            message = _('All weekly scores for this week are already saved.')
            if is_ajax:
                return JsonResponse({'ok': False, 'message': message}, status=400)
            messages.info(request, message)
            return render(request, self.template_name, _teacher_ctx(request, **ctx))

        if not student_ids:
            if ctx.get('has_any_editable_rows'):
                message = _('No unscored students in this group. Switch to All to continue.')
            else:
                message = _('No students to score yet.')
            if is_ajax:
                return JsonResponse({'ok': False, 'message': message}, status=400)
            messages.warning(request, message)
            return render(request, self.template_name, _teacher_ctx(request, **ctx))

        entries = parse_weekly_score_post(request.POST, student_ids)
        try:
            result = save_teacher_weekly_scores(
                teacher_id=teacher.pk,
                week_start=ctx['week_value'],
                entries=entries,
            )
        except ValidationError as exc:
            message = exc.messages[0] if exc.messages else str(exc)
            if is_ajax:
                return JsonResponse({'ok': False, 'message': message}, status=400)
            messages.error(request, message)
            return render(request, self.template_name, _teacher_ctx(request, **ctx))

        saved = result['saved']
        if saved:
            message = _('Weekly scores saved.')
            level = 'success'
        elif result.get('skipped'):
            message = _('All entered scores were already saved.')
            level = 'info'
        else:
            message = _('Enter a score for at least one student.')
            level = 'info'

        if is_ajax:
            html = self._render_panel(request, teacher, flash_message=message, flash_level=level)
            return JsonResponse({'ok': True, 'message': message, 'level': level, 'html': html})

        messages.success(request, message) if saved else messages.info(request, message)
        group = request.POST.get('group') or ctx.get('active_group', 'all')
        url = reverse('portals:teacher-weekly-scores')
        if group != 'all':
            url = f'{url}?group={group}'
        return redirect(url)
