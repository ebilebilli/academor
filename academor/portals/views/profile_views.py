from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _
from django.views import View

from portals.forms import ParentProfileEditForm, StudentProfileEditForm, TeacherProfileEditForm
from portals.utils.attendance_stats import compute_attendance_stats
from portals.utils.quiz_stats import compute_quiz_average_stats
from portals.utils.queries import (
    get_parent_profile,
    get_portal_role,
    get_student_attendance_detail,
    get_student_profile,
    get_student_quiz_results,
    get_teacher_profile,
    serialize_parent,
    serialize_student,
    serialize_teacher,
)
from portals.views.mixins import PortalLoginRequiredMixin


class PortalProfileView(PortalLoginRequiredMixin, View):
    template_name = 'portals/profile.html'

    def _get_profile_and_form(self, request, data=None, files=None):
        role = get_portal_role(request.portal_user)
        if role == 'teacher':
            profile = get_teacher_profile(request.portal_user)
            form_class = TeacherProfileEditForm
            serialized = serialize_teacher
        elif role == 'parent':
            profile = get_parent_profile(request.portal_user)
            form_class = ParentProfileEditForm
            serialized = serialize_parent
        else:
            profile = get_student_profile(request.portal_user)
            form_class = StudentProfileEditForm
            serialized = serialize_student

        if data is not None:
            form = form_class(data, files, instance=profile)
        else:
            form = form_class(instance=profile)
        return role, profile, form, serialized

    def _render_profile(self, request, role, profile, form, serialized):
        context = {
            'portal_role': role,
            'profile': serialized(profile),
            'form': form,
            'is_teacher': role == 'teacher',
            'is_parent': role == 'parent',
            'is_student': role == 'student',
        }
        if role == 'student':
            quiz_results = get_student_quiz_results(profile.pk)
            attendance_detail = get_student_attendance_detail(profile.pk)
            context['quiz_average'] = compute_quiz_average_stats(quiz_results)
            context['attendance_stats'] = compute_attendance_stats(attendance_detail)
        return render(request, self.template_name, context)

    def get(self, request):
        role = get_portal_role(request.portal_user)
        if role not in ('teacher', 'student', 'parent'):
            return redirect('portals:dashboard')
        role, profile, form, serialized = self._get_profile_and_form(request)
        return self._render_profile(request, role, profile, form, serialized)

    def post(self, request):
        role = get_portal_role(request.portal_user)
        if role not in ('teacher', 'student', 'parent'):
            return redirect('portals:dashboard')
        role, profile, form, serialized = self._get_profile_and_form(
            request,
            data=request.POST,
            files=request.FILES,
        )

        if role in ('teacher', 'student') and request.POST.get('profile_image-clear') == 'on' and not request.FILES.get('profile_image'):
            if profile.profile_image:
                profile.profile_image.delete(save=False)
            profile.profile_image = None
            profile.save(update_fields=['profile_image'])
            messages.success(request, _('Your profile photo has been removed.'))
            return redirect('portals:profile')

        if form.is_valid():
            form.save()
            messages.success(request, _('Your profile has been updated.'))
            return redirect('portals:profile')

        messages.error(request, _('Please fix the errors below and try again.'))
        return self._render_profile(request, role, profile, form, serialized)
