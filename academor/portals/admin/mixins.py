from django.contrib import admin
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from portals.utils.portal_services import get_active_course_type_choices

from .help_texts import get_admin_help


class CourseTypeTabFilterMixin:
    """Changelist tabs filtered by active site service codes."""

    course_type_query_param = 'course_type'
    course_type_field = 'course_type'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        course_type = request.GET.get(self.course_type_query_param)
        if course_type:
            qs = qs.filter(**{self.course_type_field: course_type})
        return qs

    def _course_type_tab_url(self, request, course_type):
        params = request.GET.copy()
        if course_type:
            params[self.course_type_query_param] = course_type
        else:
            params.pop(self.course_type_query_param, None)
        changelist_url = reverse(
            f'admin:{self.model._meta.app_label}_{self.model._meta.model_name}_changelist',
        )
        query = params.urlencode()
        return f'{changelist_url}?{query}' if query else changelist_url

    def get_course_type_tabs(self, request):
        current = request.GET.get(self.course_type_query_param, '')
        tabs = [{
            'label': _('All'),
            'url': self._course_type_tab_url(request, ''),
            'active': not current,
        }]
        for code, label in get_active_course_type_choices():
            tabs.append({
                'label': label,
                'url': self._course_type_tab_url(request, code),
                'active': current == code,
            })
        return tabs

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['course_type_tabs'] = self.get_course_type_tabs(request)
        return super().changelist_view(request, extra_context=extra_context)


class PortalModelAdmin(admin.ModelAdmin):
    """ModelAdmin with portal-themed help, stats, and styling."""

    change_list_template = 'admin/portals/portals_change_list.html'
    change_form_template = 'admin/portals/portals_change_form.html'

    class Media:
        css = {
            'all': ('portals/css/portal-admin.css',),
        }
        js = ('assets/js/admin_image_compress.js',)

    def get_portal_stats(self, request):
        return []

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['admin_page_help'] = get_admin_help(self.model)
        extra_context['portal_stats'] = self.get_portal_stats(request)
        return super().changelist_view(request, extra_context=extra_context)

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['admin_page_help'] = get_admin_help(self.model)
        return super().changeform_view(
            request,
            object_id,
            form_url,
            extra_context=extra_context,
        )
