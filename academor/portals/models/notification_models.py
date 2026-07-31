from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from portals.models.quiz_models import Quiz
from projects.models.service_models import Service


class QuizResultReview(models.Model):
    """Teacher grading record for a manual-review quiz submission."""

    result = models.ForeignKey(
        'QuizResult',
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name=_('Quiz result'),
    )
    reviewer = models.ForeignKey(
        'TeacherProfile',
        on_delete=models.PROTECT,
        related_name='quiz_result_reviews',
        verbose_name=_('Reviewer'),
    )
    score = models.FloatField(
        verbose_name=_('Score'),
        validators=[
            MinValueValidator(0),
            MaxValueValidator(Quiz.MANUAL_REVIEW_MAX_SCORE),
        ],
    )
    feedback = models.TextField(
        blank=True,
        verbose_name=_('Feedback and corrections'),
    )
    reviewed_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Reviewed at'))

    class Meta:
        verbose_name = _('Quiz result review')
        verbose_name_plural = _('Quiz result reviews')
        ordering = ('-reviewed_at', 'id')

    def __str__(self):
        return f'{self.reviewer} → {self.result_id} ({self.score})'


class PortalNotification(models.Model):
    """Portal alerts for quiz submissions and published scores."""

    class Kind(models.TextChoices):
        SUBMISSION_PENDING = 'submission_pending', _('Submission awaiting review')
        RESULT_PUBLISHED = 'result_published', _('Result published')
        MOCK_TEST_COMPLETED = 'mock_test_completed', _('IELTS mock test completed')
        MOCK_TEST_SECTION_REVIEW = 'mock_test_section_review', _('IELTS mock test section review')
        MOCK_TEST_RESULTS_PUBLISHED = 'mock_test_results_published', _('IELTS mock test results published')
        WEEKLY_SCORE_PUBLISHED = 'weekly_score_published', _('Weekly score published')
        HOMEWORK_SUBMITTED = 'homework_submitted', _('Homework submitted')
        OFFER_NOTIFICATION = 'offer_notification', _('Offer notification')

    teacher = models.ForeignKey(
        'TeacherProfile',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications',
        verbose_name=_('Teacher'),
    )
    parent = models.ForeignKey(
        'ParentProfile',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications',
        verbose_name=_('Parent'),
    )
    student = models.ForeignKey(
        'StudentProfile',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications',
        verbose_name=_('Student'),
    )
    customer = models.ForeignKey(
        'CustomerProfile',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications',
        verbose_name=_('Customer'),
    )
    quiz_result = models.ForeignKey(
        'QuizResult',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications',
        verbose_name=_('Quiz result'),
    )
    ielts_mock_test = models.ForeignKey(
        'IeltsMockTestAttempt',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications',
        verbose_name=_('IELTS mock test'),
    )
    weekly_student_score = models.ForeignKey(
        'WeeklyStudentScore',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications',
        verbose_name=_('Weekly student score'),
    )
    lesson_homework = models.ForeignKey(
        'LessonHomework',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications',
        verbose_name=_('Lesson homework'),
    )
    offer_notification = models.ForeignKey(
        'OfferNotification',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications',
        verbose_name=_('Offer notification'),
    )
    kind = models.CharField(
        max_length=32,
        choices=Kind.choices,
        default=Kind.RESULT_PUBLISHED,
        verbose_name=_('Type'),
    )
    is_read = models.BooleanField(default=False, verbose_name=_('Read'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))

    class Meta:
        verbose_name = _('Portal notification')
        verbose_name_plural = _('Portal notifications')
        ordering = ('-created_at', '-id')
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(teacher__isnull=False, parent__isnull=True, student__isnull=True, customer__isnull=True)
                    | Q(teacher__isnull=True, parent__isnull=False, student__isnull=True, customer__isnull=True)
                    | Q(teacher__isnull=True, parent__isnull=True, student__isnull=False, customer__isnull=True)
                    | Q(teacher__isnull=True, parent__isnull=True, student__isnull=True, customer__isnull=False)
                ),
                name='portals_notification_single_recipient',
            ),
            models.CheckConstraint(
                condition=(
                    Q(quiz_result__isnull=False)
                    | Q(ielts_mock_test__isnull=False)
                    | Q(weekly_student_score__isnull=False)
                    | Q(lesson_homework__isnull=False)
                    | Q(offer_notification__isnull=False)
                ),
                name='portals_notification_has_target',
            ),
            models.UniqueConstraint(
                fields=('teacher', 'quiz_result', 'kind'),
                condition=Q(teacher__isnull=False, quiz_result__isnull=False),
                name='portals_notification_teacher_result_kind_unique',
            ),
            models.UniqueConstraint(
                fields=('teacher', 'ielts_mock_test', 'kind'),
                condition=Q(teacher__isnull=False, ielts_mock_test__isnull=False),
                name='portals_notification_teacher_mock_kind_unique',
            ),
            models.UniqueConstraint(
                fields=('teacher', 'lesson_homework', 'kind'),
                condition=Q(teacher__isnull=False, lesson_homework__isnull=False),
                name='portals_notification_teacher_homework_kind_unique',
            ),
            models.UniqueConstraint(
                fields=('parent', 'quiz_result'),
                condition=Q(parent__isnull=False, quiz_result__isnull=False),
                name='portals_notification_parent_result_unique',
            ),
            models.UniqueConstraint(
                fields=('student', 'quiz_result'),
                condition=Q(student__isnull=False, quiz_result__isnull=False),
                name='portals_notification_student_result_unique',
            ),
            models.UniqueConstraint(
                fields=('parent', 'weekly_student_score'),
                condition=Q(parent__isnull=False, weekly_student_score__isnull=False),
                name='portals_notification_parent_weekly_unique',
            ),
            models.UniqueConstraint(
                fields=('student', 'weekly_student_score'),
                condition=Q(student__isnull=False, weekly_student_score__isnull=False),
                name='portals_notification_student_weekly_unique',
            ),
            models.UniqueConstraint(
                fields=('customer', 'ielts_mock_test'),
                condition=Q(customer__isnull=False, ielts_mock_test__isnull=False),
                name='portals_notification_customer_mock_unique',
            ),
            models.UniqueConstraint(
                fields=('student', 'offer_notification'),
                condition=Q(student__isnull=False, offer_notification__isnull=False),
                name='portals_notification_student_offer_unique',
            ),
            models.UniqueConstraint(
                fields=('parent', 'offer_notification'),
                condition=Q(parent__isnull=False, offer_notification__isnull=False),
                name='portals_notification_parent_offer_unique',
            ),
        ]
        indexes = [
            models.Index(fields=['teacher', 'is_read', '-created_at']),
            models.Index(fields=['parent', 'is_read', '-created_at']),
            models.Index(fields=['student', 'is_read', '-created_at']),
            models.Index(fields=['customer', 'is_read', '-created_at']),
        ]

    def __str__(self):
        recipient = self.teacher or self.parent or self.student or self.customer
        target = (
            self.quiz_result_id
            or self.ielts_mock_test_id
            or self.weekly_student_score_id
            or self.lesson_homework_id
            or self.offer_notification_id
        )
        return f'{recipient} — {self.get_kind_display()} ({target})'


class OfferNotification(models.Model):
    """Admin-created offer notifications for students and parents."""

    class TargetRole(models.TextChoices):
        STUDENT = 'student', _('Student')
        PARENT = 'parent', _('Parent')
        ALL = 'all', _('All students and parents')

    name = models.CharField(
        max_length=200,
        verbose_name=_('Name'),
    )
    description = models.TextField(
        verbose_name=_('Description'),
    )
    target_role = models.CharField(
        max_length=16,
        choices=TargetRole.choices,
        default=TargetRole.ALL,
        verbose_name=_('Target role'),
    )
    services = models.ManyToManyField(
        'projects.Service',
        blank=True,
        related_name='offer_notifications',
        verbose_name=_('Services'),
        help_text=_('Leave empty to send to all services'),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))

    class Meta:
        verbose_name = _('Offer notification')
        verbose_name_plural = _('Offer notifications')
        ordering = ('-created_at', '-id')

    def __str__(self):
        return self.name


class OfferNotificationDelivery(models.Model):
    """Delivery record for offer notifications to specific users."""

    offer_notification = models.ForeignKey(
        'OfferNotification',
        on_delete=models.CASCADE,
        related_name='deliveries',
        verbose_name=_('Offer notification'),
    )
    student = models.ForeignKey(
        'StudentProfile',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='offer_notification_deliveries',
        verbose_name=_('Student'),
    )
    parent = models.ForeignKey(
        'ParentProfile',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='offer_notification_deliveries',
        verbose_name=_('Parent'),
    )
    portal_notification = models.ForeignKey(
        PortalNotification,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='offer_delivery',
        verbose_name=_('Portal notification'),
    )
    is_sent = models.BooleanField(default=False, verbose_name=_('Sent'))
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Sent at'))

    class Meta:
        verbose_name = _('Offer notification delivery')
        verbose_name_plural = _('Offer notification deliveries')
        ordering = ('-sent_at', '-id')
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(student__isnull=False, parent__isnull=True)
                    | Q(student__isnull=True, parent__isnull=False)
                ),
                name='portals_offer_notification_delivery_single_recipient',
            ),
        ]

    def __str__(self):
        recipient = self.student or self.parent
        return f'{self.offer_notification.name} → {recipient}'
