from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'transaction_id',
        'amount',
        'currency',
        'status',
        'created_at',
    )
    list_filter = ('status', 'currency', 'created_at')
    search_fields = ('transaction_id', 'client_order_id', 'description')
    fields = (
        'transaction_id',
        'client_order_id',
        'amount',
        'currency',
        'status',
        'description',
        'created_at',
        'updated_at',
    )
    readonly_fields = fields

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
