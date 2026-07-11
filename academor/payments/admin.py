from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from projects.admin.mixins import AcademorModelAdmin
from projects.admin.filters import (
    CreatedAtMonthFilter,
    CreatedAtPeriodFilter,
    CreatedAtYearFilter,
)

from .models import CourseEnrollment, Payment
from .admin_filters import EnrollmentCourseFilter, EnrollmentProductTypeFilter

_CREATED_AT_FILTERS = (
    CreatedAtPeriodFilter,
    CreatedAtYearFilter,
    CreatedAtMonthFilter,
)


def _render_enrollment_contract_document(obj):
    if not obj or not obj.contract_html:
        return mark_safe('<span class="quiet">—</span>')

    return format_html(
        '<div class="enrollment-contract-admin">'
        '<p class="enrollment-contract-admin__actions">'
        '<button type="button" class="button" id="enrollment-contract-pdf-download"'
        ' data-busy-label="{}" data-error-label="{}">'
        '{}</button>'
        '</p>'
        '<div class="enrollment-contract-admin__scroll">'
        '<div id="enrollment-contract-pdf-source" data-contract-number="{}">{}</div>'
        '</div>'
        '</div>',
        _('Generating PDF…'),
        _('PDF could not be generated.'),
        _('Download PDF'),
        obj.contract_number,
        mark_safe(obj.contract_html),
    )


class CourseEnrollmentInline(admin.StackedInline):
    model = CourseEnrollment
    extra = 0
    max_num = 1
    can_delete = False
    readonly_fields = (
        'course',
        'price_package',
        'customer',
        'buyer_email',
        'buyer_name',
        'buyer_phone',
        'contract_number',
        'status',
        'created_at',
    )
    fields = readonly_fields

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Payment)
class PaymentAdmin(AcademorModelAdmin):
    list_display = (
        'transaction_id',
        'amount',
        'currency',
        'status',
        'product_type',
        'course',
        'price_package',
        'buyer_email',
        'buyer_phone',
        'contract_number',
        'created_at',
    )
    list_filter = ('status', 'product_type', 'currency', *_CREATED_AT_FILTERS)
    search_fields = (
        'transaction_id',
        'client_order_id',
        'description',
        'buyer_email',
        'buyer_name',
        'buyer_phone',
        'contract_number',
    )
    readonly_fields = (
        'transaction_id',
        'client_order_id',
        'amount',
        'currency',
        'status',
        'product_type',
        'course',
        'price_package',
        'buyer_email',
        'buyer_name',
        'buyer_phone',
        'contract_number',
        'description',
        'enrollment_completed_at',
        'callback_up',
        'callback_payload',
        'callback_received_at',
        'created_at',
        'updated_at',
    )
    fields = readonly_fields
    inlines = [CourseEnrollmentInline]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(AcademorModelAdmin):
    change_form_template = 'admin/payments/courseenrollment/change_form.html'

    class Media:
        css = {
            'all': (
                'payments/admin/enrollment-contract-admin.css',
                'payments/admin/enrollment-contract-pdf.css',
                'payments/admin/enrollment-list.css',
            ),
        }
        js = (
            'https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js',
            'payments/admin/enrollment-contract-pdf.js',
        )

    list_display = (
        'id',
        'product_type_badge',
        'product_label',
        'buyer_name',
        'buyer_phone',
        'buyer_email',
        'contract_number',
        'status',
        'created_at',
    )
    list_display_links = ('id', 'buyer_name', 'buyer_phone')
    list_filter = (
        EnrollmentProductTypeFilter,
        EnrollmentCourseFilter,
        'status',
        *_CREATED_AT_FILTERS,
    )
    list_per_page = 50
    search_fields = (
        'buyer_email',
        'buyer_name',
        'buyer_phone',
        'contract_number',
        'payment__transaction_id',
        'course__name_az',
        'course__name_en',
        'price_package__name_az',
        'price_package__name_en',
    )
    readonly_fields = (
        'payment',
        'product_type_badge',
        'course',
        'price_package',
        'customer',
        'buyer_email',
        'buyer_name',
        'buyer_phone',
        'contract_number',
        'contract_document',
        'status',
        'created_at',
    )
    fields = readonly_fields

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                'payment',
                'course',
                'price_package',
                'customer',
                'customer__user',
            )
        )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        # Allow opening the detail page (read-only); saving is still blocked.
        return request.method in ('GET', 'HEAD', 'OPTIONS')

    def has_view_permission(self, request, obj=None):
        return True

    def save_model(self, request, obj, form, change):
        return

    def save_related(self, request, form, formsets, change):
        return

    @admin.display(description=_('Product type'), ordering='payment__product_type')
    def product_type_badge(self, obj):
        if not obj or not obj.payment_id:
            return '—'
        product_type = obj.payment.product_type
        label = obj.payment.get_product_type_display()
        css = 'enrollment-type-badge'
        if product_type == Payment.ProductType.MOCK_TEST:
            css += ' enrollment-type-badge--mock'
            filter_value = Payment.ProductType.MOCK_TEST
        elif product_type == Payment.ProductType.COURSE:
            css += ' enrollment-type-badge--course'
            filter_value = Payment.ProductType.COURSE
        else:
            filter_value = product_type
        url = (
            reverse('admin:payments_courseenrollment_changelist')
            + f'?product_type={filter_value}'
        )
        return format_html(
            '<a class="{}" href="{}">{}</a>',
            css,
            url,
            label,
        )

    @admin.display(description=_('Package / service'))
    def product_label(self, obj):
        if not obj:
            return '—'
        if obj.course_id and obj.course:
            if obj.price_package_id and obj.price_package:
                prefix = 'Mock — ' if obj.is_mock_enrollment else ''
                return f'{prefix}{obj.course} — {obj.price_package}'
            return str(obj.course)
        return '—'

    @admin.display(description=_('Agreement'))
    def contract_document(self, obj):
        return _render_enrollment_contract_document(obj)
