from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from payments.models import Payment


class EnrollmentProductTypeFilter(admin.SimpleListFilter):
    title = _('Product type')
    parameter_name = 'product_type'
    template = 'admin/filter.html'

    def lookups(self, request, model_admin):
        return (
            (Payment.ProductType.COURSE, _('Course / service')),
            (Payment.ProductType.MOCK_TEST, _('Mock test')),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if not value:
            return queryset
        return queryset.filter(payment__product_type=value)

    def choices(self, changelist):
        yield {
            'selected': self.value() is None,
            'query_string': changelist.get_query_string(remove=[self.parameter_name]),
            'display': _('All'),
        }
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == str(lookup),
                'query_string': changelist.get_query_string(
                    {self.parameter_name: lookup}
                ),
                'display': title,
            }


class EnrollmentCourseFilter(admin.SimpleListFilter):
    title = _('Service')
    parameter_name = 'course'

    def lookups(self, request, model_admin):
        from payments.models import CourseEnrollment
        from projects.models import Service

        course_ids = (
            CourseEnrollment.objects.filter(course_id__isnull=False)
            .values_list('course_id', flat=True)
            .distinct()
        )
        services = Service.objects.filter(pk__in=course_ids).order_by('order', 'id')
        return [(service.pk, str(service)) for service in services]

    def queryset(self, request, queryset):
        value = self.value()
        if not value:
            return queryset
        return queryset.filter(course_id=value)
