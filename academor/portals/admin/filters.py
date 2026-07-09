from datetime import datetime, timedelta

from django.contrib import admin
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from portals.forms import (
    PORTAL_ROLE_ADMIN,
    PORTAL_ROLE_CHOICES,
    PORTAL_ROLE_CUSTOMER,
    PORTAL_ROLE_PARENT,
    PORTAL_ROLE_STAFF,
    PORTAL_ROLE_STUDENT,
    PORTAL_ROLE_TEACHER,
)

_EN_MONTHS = {
    1: 'January',
    2: 'February',
    3: 'March',
    4: 'April',
    5: 'May',
    6: 'June',
    7: 'July',
    8: 'August',
    9: 'September',
    10: 'October',
    11: 'November',
    12: 'December',
}


def _start_of_day(dt):
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def _start_of_month(dt):
    return _start_of_day(dt.replace(day=1))


def _start_of_year(dt):
    return _start_of_day(dt.replace(month=1, day=1))


def _portal_role_queryset(queryset, role):
    """Match ``get_user_portal_role`` priority for list filtering."""
    non_super = Q(is_superuser=False)

    if role == PORTAL_ROLE_ADMIN:
        return queryset.filter(is_superuser=True)

    if role == PORTAL_ROLE_TEACHER:
        return queryset.filter(non_super, teacher_profile__isnull=False)

    if role == PORTAL_ROLE_STUDENT:
        return queryset.filter(
            non_super,
            teacher_profile__isnull=True,
            student_profile__isnull=False,
        )

    if role == PORTAL_ROLE_PARENT:
        return queryset.filter(
            non_super,
            teacher_profile__isnull=True,
            student_profile__isnull=True,
            parent_profile__isnull=False,
        )

    if role == PORTAL_ROLE_CUSTOMER:
        return queryset.filter(
            non_super,
            teacher_profile__isnull=True,
            student_profile__isnull=True,
            parent_profile__isnull=True,
            customer_profile__isnull=False,
        )

    if role == PORTAL_ROLE_STAFF:
        return queryset.filter(
            non_super,
            is_staff=True,
            teacher_profile__isnull=True,
            student_profile__isnull=True,
            parent_profile__isnull=True,
            customer_profile__isnull=True,
        )

    if role == 'none':
        return queryset.filter(
            non_super,
            is_staff=False,
            teacher_profile__isnull=True,
            student_profile__isnull=True,
            parent_profile__isnull=True,
            customer_profile__isnull=True,
        )

    return queryset


class PortalRoleFilter(admin.SimpleListFilter):
    title = _('Role')
    parameter_name = 'portal_role'

    def lookups(self, request, model_admin):
        return list(PORTAL_ROLE_CHOICES) + [('none', _('No role'))]

    def queryset(self, request, queryset):
        value = self.value()
        if not value:
            return queryset
        return _portal_role_queryset(queryset, value)


class DateJoinedPeriodFilter(admin.SimpleListFilter):
    title = _('Date joined')
    parameter_name = 'joined_period'

    def lookups(self, request, model_admin):
        return (
            ('today', _('Today')),
            ('yesterday', _('Yesterday')),
            ('last_7', _('Last 7 days')),
            ('last_30', _('Last 30 days')),
            ('last_90', _('Last 90 days')),
            ('this_month', _('This month')),
            ('last_month', _('Last month')),
            ('this_year', _('This year')),
            ('last_year', _('Last year')),
            ('older', _('Older than 1 year')),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if not value:
            return queryset

        now = timezone.now()
        today = _start_of_day(now)

        if value == 'today':
            return queryset.filter(date_joined__gte=today)

        if value == 'yesterday':
            yesterday = today - timedelta(days=1)
            return queryset.filter(date_joined__gte=yesterday, date_joined__lt=today)

        if value == 'last_7':
            return queryset.filter(date_joined__gte=today - timedelta(days=7))

        if value == 'last_30':
            return queryset.filter(date_joined__gte=today - timedelta(days=30))

        if value == 'last_90':
            return queryset.filter(date_joined__gte=today - timedelta(days=90))

        if value == 'this_month':
            return queryset.filter(date_joined__gte=_start_of_month(now))

        if value == 'last_month':
            this_month_start = _start_of_month(now)
            prev_month_start = _start_of_month(this_month_start - timedelta(days=1))
            return queryset.filter(
                date_joined__gte=prev_month_start,
                date_joined__lt=this_month_start,
            )

        if value == 'this_year':
            return queryset.filter(date_joined__gte=_start_of_year(now))

        if value == 'last_year':
            this_year_start = _start_of_year(now)
            last_year_start = this_year_start.replace(year=this_year_start.year - 1)
            return queryset.filter(
                date_joined__gte=last_year_start,
                date_joined__lt=this_year_start,
            )

        if value == 'older':
            this_year_start = _start_of_year(now)
            last_year_start = this_year_start.replace(year=this_year_start.year - 1)
            return queryset.filter(date_joined__lt=last_year_start)

        return queryset


class DateJoinedYearFilter(admin.SimpleListFilter):
    title = _('Joined year')
    parameter_name = 'joined_year'

    def lookups(self, request, model_admin):
        years = model_admin.model.objects.dates('date_joined', 'year', order='DESC')
        return [(str(d.year), str(d.year)) for d in years]

    def queryset(self, request, queryset):
        value = self.value()
        if not value:
            return queryset
        return queryset.filter(date_joined__year=int(value))


class DateJoinedMonthFilter(admin.SimpleListFilter):
    title = _('Joined month')
    parameter_name = 'joined_month'

    def lookups(self, request, model_admin):
        year_param = request.GET.get('joined_year')
        qs = model_admin.model.objects.all()
        if year_param and year_param.isdigit():
            year = int(year_param)
            qs = qs.filter(date_joined__year=year)
            months = qs.dates('date_joined', 'month', order='DESC')
            return [
                (str(d.month), _EN_MONTHS.get(d.month, str(d.month)))
                for d in months
            ]

        year = timezone.now().year
        qs = qs.filter(date_joined__year=year)
        months = qs.dates('date_joined', 'month', order='DESC')
        if months:
            return [
                (str(d.month), f'{_EN_MONTHS.get(d.month, d.month)} {d.year}')
                for d in months
            ]

        return [
            (str(m), name)
            for m, name in sorted(_EN_MONTHS.items(), reverse=True)
        ]

    def queryset(self, request, queryset):
        value = self.value()
        if not value:
            return queryset

        month = int(value)
        year_param = request.GET.get('joined_year')
        if year_param and year_param.isdigit():
            year = int(year_param)
        else:
            year = timezone.now().year

        start = timezone.make_aware(datetime(year, month, 1))
        if month == 12:
            end_exclusive = timezone.make_aware(datetime(year + 1, 1, 1))
        else:
            end_exclusive = timezone.make_aware(datetime(year, month + 1, 1))
        return queryset.filter(date_joined__gte=start, date_joined__lt=end_exclusive)
