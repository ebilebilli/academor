from django.contrib import admin

from .models import CourseEnrollment, Payment


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
        'status',
        'created_at',
    )
    fields = readonly_fields

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
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
        'created_at',
    )
    list_filter = ('status', 'product_type', 'currency', 'created_at')
    search_fields = (
        'transaction_id',
        'client_order_id',
        'description',
        'buyer_email',
        'buyer_name',
        'buyer_phone',
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
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'course',
        'price_package',
        'buyer_email',
        'buyer_name',
        'buyer_phone',
        'status',
        'payment',
        'created_at',
    )
    list_filter = ('status', 'created_at')
    search_fields = (
        'buyer_email',
        'buyer_name',
        'buyer_phone',
        'payment__transaction_id',
    )
    readonly_fields = (
        'payment',
        'course',
        'price_package',
        'buyer_email',
        'buyer_name',
        'buyer_phone',
        'status',
        'created_at',
    )
    fields = readonly_fields

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
