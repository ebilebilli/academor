"""Admin for AKIRA: reports, spend, explanations to approve, and teaching materials."""

from django.contrib import admin
from django.db.models import Sum
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from portals.models import AkiraExplanation, AkiraMaterial, AkiraReport, AkiraUsage


@admin.register(AkiraReport)
class AkiraReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'kind', 'course_code', 'status', 'helpful', 'attempts', 'created_at')
    list_filter = ('kind', 'status', 'course_code', 'helpful')
    search_fields = ('comment', 'error')
    readonly_fields = (
        'kind', 'course_code', 'quiz_result', 'user_result', 'student', 'customer', 'facts',
        'model_name', 'attempts', 'helpful', 'created_at', 'updated_at',
    )
    fields = readonly_fields[:6] + ('status', 'comment', 'error') + readonly_fields[6:]
    actions = ('write_again',)

    @admin.action(description=_('Let AKIRA write these comments again'))
    def write_again(self, request, queryset):
        queryset.update(status=AkiraReport.Status.PENDING, comment='', error='', attempts=0)


@admin.register(AkiraUsage)
class AkiraUsageAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'purpose', 'model_name', 'input_tokens', 'output_tokens', 'cost_usd', 'ok')
    list_filter = ('purpose', 'ok', 'model_name')
    date_hierarchy = 'created_at'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        from portals.akira import client

        start = timezone.localdate().replace(day=1)
        spent = AkiraUsage.objects.filter(created_at__date__gte=start).aggregate(total=Sum('cost_usd'))['total'] or 0
        extra_context = {
            **(extra_context or {}),
            'title': _('AKIRA usage — this month: $%(spent)s of $%(budget)s') % {
                'spent': f'{spent:.2f}',
                'budget': f'{client.monthly_budget_usd():.2f}',
            },
        }
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(AkiraExplanation)
class AkiraExplanationAdmin(admin.ModelAdmin):
    list_display = ('question', 'answer_key', 'status', 'reviewed_by', 'reviewed_at')
    list_filter = ('status',)
    search_fields = ('text',)
    raw_id_fields = ('question',)
    readonly_fields = ('reviewed_by', 'reviewed_at', 'created_at')
    actions = ('approve', 'reject')

    @admin.action(description=_('Approve the selected explanations'))
    def approve(self, request, queryset):
        queryset.update(status=AkiraExplanation.Status.APPROVED, reviewed_by=request.user, reviewed_at=timezone.now())

    @admin.action(description=_('Reject the selected explanations'))
    def reject(self, request, queryset):
        queryset.update(status=AkiraExplanation.Status.REJECTED, reviewed_by=request.user, reviewed_at=timezone.now())


@admin.register(AkiraMaterial)
class AkiraMaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'course_code', 'domain', 'is_active', 'updated_at')
    list_filter = ('course_code', 'is_active')
    search_fields = ('title', 'content', 'domain')
