"""Custom Django admin views for attendance control."""

from datetime import date

from django.contrib import admin, messages
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.translation import gettext as _

from portals.models import Attendance, Schedule, StudentProfile, StudyGroup
from portals.teacher_forms import build_session_attendance_form
from portals.utils.admin_attendance import (
    build_admin_attendance_hub_context,
    get_student_attendance_overview,
    save_admin_group_attendance,
)


def _parse_int(value):
    if value in (None, ''):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _parse_date(value):
    if not value:
        return None
    try:
        return date.fromisoformat(str(value).strip())
    except ValueError:
        return None


def attendance_hub_view(admin_site, request):
    teacher_id = _parse_int(request.GET.get('teacher') or request.POST.get('teacher'))
    group_id = _parse_int(request.GET.get('group') or request.POST.get('group'))
    schedule_id = _parse_int(request.GET.get('schedule') or request.POST.get('schedule'))
    session_date = _parse_date(request.GET.get('date') or request.POST.get('date'))

    if request.method == 'POST' and request.POST.get('action') == 'mark':
        schedule = get_object_or_404(Schedule.objects.select_related('group'), pk=schedule_id)
        session_date = _parse_date(request.POST.get('date'))
        if not session_date:
            messages.error(request, _('Pick a valid session date.'))
            return HttpResponseRedirect(request.path + f'?teacher={teacher_id}&group={group_id}')

        student_status_map = {}
        for student in schedule.group.students.all():
            field = f'status_{student.pk}'
            if field in request.POST:
                student_status_map[student.pk] = request.POST[field]

        if not student_status_map:
            messages.error(request, _('No students to mark.'))
        else:
            saved = save_admin_group_attendance(schedule, session_date, student_status_map)
            messages.success(
                request,
                _('Saved attendance for %(count)s student(s).') % {'count': saved},
            )
        redirect_url = reverse('admin:portals_attendance_hub')
        return HttpResponseRedirect(
            f'{redirect_url}?teacher={schedule.group.teacher_id}&group={schedule.group_id}'
            f'&schedule={schedule.pk}&date={session_date.isoformat()}'
        )

    context = build_admin_attendance_hub_context(
        teacher_id=teacher_id,
        group_id=group_id,
        session_date=session_date,
        schedule_id=schedule_id,
    )
    context.update({
        **admin_site.each_context(request),
        'title': _('Attendance control'),
        'opts': Attendance._meta,
        'has_view_permission': True,
    })

    if context['schedule'] and context['students']:
        context['form'] = build_session_attendance_form(
            context['students'],
            existing=context['existing'],
        )

    return render(request, 'admin/portals/attendance/hub.html', context)


def student_attendance_detail_view(admin_site, request, student_id):
    student = get_object_or_404(
        StudentProfile.objects.select_related('user'),
        pk=student_id,
    )
    overview = get_student_attendance_overview(student)
    hub_url = reverse('admin:portals_attendance_hub')
    default_group = overview['groups'][0] if overview['groups'] else None
    mark_url = hub_url
    if default_group:
        mark_url = (
            f'{hub_url}?teacher={default_group.teacher_id}'
            f'&group={default_group.pk}'
        )

    context = {
        **admin_site.each_context(request),
        'title': _('Attendance history — %(name)s') % {'name': student.full_name},
        'opts': StudentProfile._meta,
        'student': student,
        'overview': overview,
        'mark_url': mark_url,
        'student_change_url': reverse('admin:portals_studentprofile_change', args=[student.pk]),
        'has_view_permission': True,
    }
    return render(request, 'admin/portals/attendance/student_detail.html', context)
