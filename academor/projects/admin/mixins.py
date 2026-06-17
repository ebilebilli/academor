from django.contrib import admin

from .help_texts import ADMIN_INDEX_HELP, get_admin_help


class AdminHelpMixin:
    """Inject page-level English help text into changelist and change form views."""

    change_list_template = 'admin/academor_change_list.html'
    change_form_template = 'admin/academor_change_form.html'

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['admin_page_help'] = get_admin_help(self.model)
        return super().changelist_view(request, extra_context=extra_context)

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['admin_page_help'] = get_admin_help(self.model)
        return super().changeform_view(
            request, object_id, form_url, extra_context=extra_context,
        )


class AcademorModelAdmin(AdminHelpMixin, admin.ModelAdmin):
    """Base ModelAdmin with help panel on every page."""
    pass


_original_index = admin.site.index


def _index_with_help(request, extra_context=None):
    extra_context = extra_context or {}
    extra_context['admin_index_help'] = ADMIN_INDEX_HELP
    return _original_index(request, extra_context=extra_context)


def install_admin_help():
    """Hook help text into the admin index page."""
    admin.site.index_template = 'admin/academor_index.html'
    admin.site.index = _index_with_help
