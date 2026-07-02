from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Schedule(models.Model):
    class Weekday(models.IntegerChoices):
        MONDAY = 0, _('Monday')
        TUESDAY = 1, _('Tuesday')
        WEDNESDAY = 2, _('Wednesday')
        THURSDAY = 3, _('Thursday')
        FRIDAY = 4, _('Friday')
        SATURDAY = 5, _('Saturday')
        SUNDAY = 6, _('Sunday')

    group = models.ForeignKey(
        'StudyGroup',
        on_delete=models.CASCADE,
        related_name='schedules',
        verbose_name=_('Group'),
    )
    weekday = models.IntegerField(
        choices=Weekday.choices,
        verbose_name=_('Weekday'),
    )
    start_time = models.TimeField(
        verbose_name=_('Start time'),
    )
    duration_min = models.PositiveIntegerField(
        verbose_name=_('Duration (minutes)'),
    )
    room_or_link = models.CharField(
        max_length=500,
        blank=True,
        verbose_name=_('Room or link'),
    )
    effective_from = models.DateField(
        default=timezone.localdate,
        verbose_name=_('Active from'),
        help_text=_(
            'First calendar date when this weekly slot appears. '
            'Past weeks and months before this date will not show the slot.'
        ),
    )

    class Meta:
        verbose_name = _('Schedule')
        verbose_name_plural = _('Schedules')
        ordering = ('weekday', 'start_time', 'id')

    def __str__(self):
        weekday = self.get_weekday_display()
        return f'{self.group} — {weekday} {self.start_time:%H:%M}'


class Attendance(models.Model):
    class Status(models.TextChoices):
        PRESENT = 'present', _('Present')
        ABSENT = 'absent', _('Absent')
        LATE = 'late', _('Late')

    schedule = models.ForeignKey(
        Schedule,
        on_delete=models.CASCADE,
        related_name='attendances',
        verbose_name=_('Schedule'),
    )
    student = models.ForeignKey(
        'StudentProfile',
        on_delete=models.CASCADE,
        related_name='attendances',
        verbose_name=_('Student'),
    )
    session_date = models.DateField(
        verbose_name=_('Session date'),
        help_text=_('Concrete date of the class session (schedule defines the recurring slot).'),
    )
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        verbose_name=_('Status'),
    )
    marked_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Marked at'),
    )
    note = models.TextField(
        blank=True,
        verbose_name=_('Note'),
    )

    class Meta:
        verbose_name = _('Attendance')
        verbose_name_plural = _('Attendance records')
        ordering = ('-session_date', '-marked_at', 'id')
        constraints = [
            models.UniqueConstraint(
                fields=('schedule', 'student', 'session_date'),
                name='portals_attendance_unique_session',
            ),
        ]

    def __str__(self):
        return f'{self.student} — {self.session_date} ({self.get_status_display()})'
