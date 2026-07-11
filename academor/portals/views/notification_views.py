from django.contrib import messages
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views import View

from portals.models import PortalNotification
from portals.utils.notifications import (
    delete_notification,
    get_notifications,
    get_score_detail_for_customer,
    get_score_detail_for_parent,
    get_score_detail_for_student,
    get_score_detail_for_teacher,
    get_teacher_portal_bell_count,
    get_unread_notification_count,
    mark_all_notifications_read,
    mark_notification_read,
)
from portals.utils.queries import (
    get_customer_profile,
    get_parent_profile,
    get_portal_role,
    get_student_profile,
    get_teacher_profile,
    serialize_customer,
    serialize_parent,
    serialize_student,
    serialize_teacher,
)
from portals.utils.safe_redirect import safe_portal_next_url
from portals.views.mixins import (
    CustomerRequiredMixin,
    ParentRequiredMixin,
    PortalLoginRequiredMixin,
    StudentRequiredMixin,
    TeacherRequiredMixin,
)
from portals.views.views_v1 import _portal_context


PERIOD_CHOICES = ('all', 'day', 'week', 'month', 'year')

PERIOD_TAB_LABELS = {
    'all': _('Hamısı'),
    'day': _('Bu gün'),
    'week': _('Bu həftə'),
    'month': _('Bu ay'),
    'year': _('Bu il'),
}

PERIOD_TAB_SHORT_LABELS = {
    'all': _('Hamısı'),
    'day': _('Gün'),
    'week': _('Həftə'),
    'month': _('Ay'),
    'year': _('İl'),
}


def _notification_period_queryset(*, teacher_id=None, parent_id=None, student_id=None, customer_id=None):
    if teacher_id:
        return PortalNotification.objects.filter(
            teacher_id=teacher_id,
            kind=PortalNotification.Kind.RESULT_PUBLISHED,
        )
    from portals.utils.notifications import _notification_queryset

    return _notification_queryset(
        teacher_id=teacher_id,
        parent_id=parent_id,
        student_id=student_id,
        customer_id=customer_id,
    )


def _build_notification_period_tabs(*, teacher_id=None, parent_id=None, student_id=None, customer_id=None):
    from portals.utils.notifications import _apply_period_filter

    base_qs = _notification_period_queryset(
        teacher_id=teacher_id,
        parent_id=parent_id,
        student_id=student_id,
        customer_id=customer_id,
    )
    return [
        {
            'code': code,
            'label': PERIOD_TAB_LABELS[code],
            'short_label': PERIOD_TAB_SHORT_LABELS[code],
            'count': _apply_period_filter(base_qs, code).count(),
        }
        for code in PERIOD_CHOICES
    ]


def _notification_recipient(request):
    role = get_portal_role(request.portal_user)
    if role == 'teacher':
        profile = get_teacher_profile(request.portal_user)
        return role, profile, {'teacher_id': profile.pk}, reverse('portals:teacher-notifications')
    if role == 'parent':
        profile = get_parent_profile(request.portal_user)
        return role, profile, {'parent_id': profile.pk}, reverse('portals:parent-notifications')
    if role == 'student':
        profile = get_student_profile(request.portal_user)
        return role, profile, {'student_id': profile.pk}, reverse('portals:student-notifications')
    if role == 'customer':
        profile = get_customer_profile(request.portal_user)
        return role, profile, {'customer_id': profile.pk}, reverse('portals:customer-notifications')
    return None, None, {}, reverse('portals:dashboard')


def _wants_json(request) -> bool:
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return True
    accept = request.headers.get('Accept') or ''
    return 'application/json' in accept


def _respond_notification_action(request, *, success, message, back_url, recipient_kwargs):
    unread_count = get_unread_notification_count(**recipient_kwargs)
    if _wants_json(request):
        status = 200 if success else 404
        return JsonResponse(
            {
                'success': success,
                'message': message,
                'unread_count': unread_count,
            },
            status=status,
        )
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)
    next_url = safe_portal_next_url(request, request.POST.get('next')) or back_url
    return redirect(next_url)


class TeacherNotificationsView(TeacherRequiredMixin, View):
    template_name = 'portals/notifications.html'

    def get(self, request):
        profile = get_teacher_profile(request.portal_user)
        period = request.GET.get('period', 'day')
        if period not in PERIOD_CHOICES:
            period = 'day'
        return render(
            request,
            self.template_name,
            _portal_context(
                request,
                teacher=serialize_teacher(profile),
                notifications=get_notifications(teacher_id=profile.pk, period=period),
                unread_count=get_teacher_portal_bell_count(profile.pk),
                period=period,
                period_choices=PERIOD_CHOICES,
                period_tabs=_build_notification_period_tabs(teacher_id=profile.pk),
                notifications_url_name='portals:teacher-notifications',
                notifications_subtitle=_('Published quiz results from your students.'),
            ),
        )


class ParentNotificationsView(ParentRequiredMixin, View):
    template_name = 'portals/notifications.html'

    def get(self, request):
        profile = get_parent_profile(request.portal_user)
        period = request.GET.get('period', 'day')
        if period not in PERIOD_CHOICES:
            period = 'day'
        return render(
            request,
            self.template_name,
            _portal_context(
                request,
                parent=serialize_parent(profile),
                notifications=get_notifications(parent_id=profile.pk, period=period),
                unread_count=get_unread_notification_count(parent_id=profile.pk),
                period=period,
                period_choices=PERIOD_CHOICES,
                period_tabs=_build_notification_period_tabs(parent_id=profile.pk),
                notifications_url_name='portals:parent-notifications',
            ),
        )


class StudentNotificationsView(StudentRequiredMixin, View):
    template_name = 'portals/notifications.html'

    def get(self, request):
        profile = get_student_profile(request.portal_user)
        period = request.GET.get('period', 'day')
        if period not in PERIOD_CHOICES:
            period = 'day'
        return render(
            request,
            self.template_name,
            _portal_context(
                request,
                student=serialize_student(profile),
                notifications=get_notifications(student_id=profile.pk, period=period),
                unread_count=get_unread_notification_count(student_id=profile.pk),
                period=period,
                period_choices=PERIOD_CHOICES,
                period_tabs=_build_notification_period_tabs(student_id=profile.pk),
                notifications_url_name='portals:student-notifications',
            ),
        )


class CustomerNotificationsView(CustomerRequiredMixin, View):
    template_name = 'portals/notifications.html'

    def get(self, request):
        profile = get_customer_profile(request.portal_user)
        period = request.GET.get('period', 'day')
        if period not in PERIOD_CHOICES:
            period = 'day'
        return render(
            request,
            self.template_name,
            _portal_context(
                request,
                customer=serialize_customer(profile),
                notifications=get_notifications(customer_id=profile.pk, period=period),
                unread_count=get_unread_notification_count(customer_id=profile.pk),
                period=period,
                period_choices=PERIOD_CHOICES,
                period_tabs=_build_notification_period_tabs(customer_id=profile.pk),
                notifications_url_name='portals:customer-notifications',
                notifications_subtitle=_('Dərc olunmuş IELTS mock test nəticələri.'),
            ),
        )


class CustomerScoreDetailView(CustomerRequiredMixin, View):
    template_name = 'portals/score_detail.html'

    def get(self, request, result_pk):
        profile = get_customer_profile(request.portal_user)
        detail = get_score_detail_for_customer(profile.pk, result_pk)
        if not detail:
            raise Http404
        PortalNotification.objects.filter(
            customer_id=profile.pk,
            quiz_result_id=result_pk,
            is_read=False,
        ).update(is_read=True)
        return render(
            request,
            self.template_name,
            _portal_context(
                request,
                customer=serialize_customer(profile),
                detail=detail,
            ),
        )


class StudentScoreDetailView(StudentRequiredMixin, View):
    template_name = 'portals/score_detail.html'

    def get(self, request, result_pk):
        profile = get_student_profile(request.portal_user)
        detail = get_score_detail_for_student(profile.pk, result_pk)
        if not detail:
            raise Http404
        PortalNotification.objects.filter(
            student_id=profile.pk,
            quiz_result_id=result_pk,
            is_read=False,
        ).update(is_read=True)
        return render(
            request,
            self.template_name,
            _portal_context(
                request,
                student=serialize_student(profile),
                detail=detail,
            ),
        )


class TeacherScoreDetailView(TeacherRequiredMixin, View):
    template_name = 'portals/score_detail.html'

    def get(self, request, result_pk):
        profile = get_teacher_profile(request.portal_user)
        detail = get_score_detail_for_teacher(profile.pk, result_pk)
        if not detail:
            raise Http404
        PortalNotification.objects.filter(
            teacher_id=profile.pk,
            quiz_result_id=result_pk,
            is_read=False,
        ).update(is_read=True)
        return render(
            request,
            self.template_name,
            _portal_context(
                request,
                teacher=serialize_teacher(profile),
                detail=detail,
            ),
        )


def _parent_score_detail_back(request):
    source = request.GET.get('from', '')
    student_id = request.GET.get('student')
    if source == 'quiz-results':
        url = reverse('portals:parent-scores')
        if student_id:
            url = f'{url}?student={student_id}&view=quiz'
        else:
            url = f'{url}?view=quiz'
        return url, _('Back to results and assessments')
    if source == 'dashboard':
        return reverse('portals:parent-dashboard'), _('Back to dashboard')
    return reverse('portals:parent-notifications'), _('Back to notifications')


class ParentScoreDetailView(ParentRequiredMixin, View):
    template_name = 'portals/score_detail.html'

    def get(self, request, result_pk):
        profile = get_parent_profile(request.portal_user)
        detail = get_score_detail_for_parent(profile.pk, result_pk)
        if not detail:
            raise Http404
        back_url, back_label = _parent_score_detail_back(request)
        detail['back_url'] = back_url
        detail['back_label'] = back_label
        PortalNotification.objects.filter(
            parent_id=profile.pk,
            quiz_result_id=result_pk,
            is_read=False,
        ).update(is_read=True)
        return render(
            request,
            self.template_name,
            _portal_context(
                request,
                parent=serialize_parent(profile),
                detail=detail,
            ),
        )


class NotificationMarkReadView(PortalLoginRequiredMixin, View):
    def post(self, request, pk):
        _role, profile, recipient_kwargs, back = _notification_recipient(request)
        if not profile:
            return redirect('portals:dashboard')
        marked = mark_notification_read(notification_id=pk, **recipient_kwargs)
        return _respond_notification_action(
            request,
            success=marked,
            message=_('Notification marked as read.') if marked else _('Notification not found.'),
            back_url=back,
            recipient_kwargs=recipient_kwargs,
        )


class NotificationDeleteView(PortalLoginRequiredMixin, View):
    def post(self, request, pk):
        _role, profile, recipient_kwargs, back = _notification_recipient(request)
        if not profile:
            return redirect('portals:dashboard')
        deleted = delete_notification(notification_id=pk, **recipient_kwargs)
        return _respond_notification_action(
            request,
            success=deleted,
            message=_('Notification deleted.') if deleted else _('Notification not found.'),
            back_url=back,
            recipient_kwargs=recipient_kwargs,
        )


class NotificationMarkAllReadView(PortalLoginRequiredMixin, View):
    def post(self, request):
        _role, profile, recipient_kwargs, back = _notification_recipient(request)
        if not profile:
            return redirect('portals:dashboard')
        mark_all_notifications_read(**recipient_kwargs)
        return _respond_notification_action(
            request,
            success=True,
            message=_('All notifications marked as read.'),
            back_url=back,
            recipient_kwargs=recipient_kwargs,
        )
