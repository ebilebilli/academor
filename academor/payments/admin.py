from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'transaction_id',
        'amount',
        'currency',
        'status',
        'user',
        'created_at',
    )
    list_filter = ('status', 'currency', 'created_at')
    search_fields = ('transaction_id', 'client_order_id', 'description')
    readonly_fields = ('created_at', 'updated_at')
