from django.contrib import admin
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
            ),
        }
        js = (
            'https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js',
            'payments/admin/enrollment-contract-pdf.js',
        )

    list_display = (
        'id',
        'course',
        'price_package',
        'buyer_email',
        'buyer_name',
        'buyer_phone',
        'contract_number',
        'status',
        'payment',
        'created_at',
    )
    list_filter = ('status', *_CREATED_AT_FILTERS)
    search_fields = (
        'buyer_email',
        'buyer_name',
        'buyer_phone',
        'contract_number',
        'payment__transaction_id',
    )
    readonly_fields = (
        'payment',
        'course',
        'price_package',
        'buyer_email',
        'buyer_name',
        'buyer_phone',
        'contract_number',
        'contract_document',
        'status',
        'created_at',
    )
    fields = readonly_fields

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @admin.display(description=_('Training agreement'))
    def contract_document(self, obj):
        return _render_enrollment_contract_document(obj)
