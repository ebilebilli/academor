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
        constraints = [
            models.UniqueConstraint(
                fields=('group', 'weekday', 'start_time', 'effective_from'),
                name='portals_schedule_unique_slot',
            ),
        ]

    def __str__(self):
        weekday = self.get_weekday_display()
        return f'{self.group} — {weekday} {self.start_time:%H:%M}'


class AttendanceRegisterGuest(models.Model):
    """Manual name on a group's monthly register — not a portal StudentProfile."""

    group = models.ForeignKey(
        'StudyGroup',
        on_delete=models.CASCADE,
        related_name='register_guests',
        verbose_name=_('Group'),
    )
    name = models.CharField(
        max_length=200,
        verbose_name=_('Full name'),
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Active'),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at'),
    )

    class Meta:
        verbose_name = _('Register guest student')
        verbose_name_plural = _('Register guest students')
        ordering = ('name', 'id')

    def __str__(self):
        return self.name


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
        null=True,
        blank=True,
        help_text=_('Optional class slot. Monthly register marks may have no slot.'),
    )
    group = models.ForeignKey(
        'StudyGroup',
        on_delete=models.CASCADE,
        related_name='group_attendances',
        verbose_name=_('Group'),
        null=True,
        blank=True,
    )
    student = models.ForeignKey(
        'StudentProfile',
        on_delete=models.CASCADE,
        related_name='attendances',
        verbose_name=_('Student'),
        null=True,
        blank=True,
    )
    guest = models.ForeignKey(
        AttendanceRegisterGuest,
        on_delete=models.CASCADE,
        related_name='attendances',
        verbose_name=_('Guest student'),
        null=True,
        blank=True,
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
            models.UniqueConstraint(
                fields=('group', 'student', 'session_date'),
                condition=models.Q(schedule__isnull=True, student__isnull=False),
                name='portals_attendance_unique_register_day',
            ),
            models.UniqueConstraint(
                fields=('group', 'guest', 'session_date'),
                condition=models.Q(guest__isnull=False, schedule__isnull=True),
                name='portals_attendance_unique_guest_day',
            ),
            models.CheckConstraint(
                condition=models.Q(schedule__isnull=False) | models.Q(group__isnull=False),
                name='portals_attendance_schedule_or_group',
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(student__isnull=False, guest__isnull=True)
                    | models.Q(student__isnull=True, guest__isnull=False)
                ),
                name='portals_attendance_student_xor_guest',
            ),
        ]

    def save(self, *args, **kwargs):
        if self.schedule_id:
            schedule_group_id = getattr(self.schedule, 'group_id', None)
            if schedule_group_id and self.group_id != schedule_group_id:
                self.group_id = schedule_group_id
        if self.guest_id and not self.group_id:
            guest_group_id = getattr(self.guest, 'group_id', None)
            if guest_group_id:
                self.group_id = guest_group_id
        super().save(*args, **kwargs)

    def __str__(self):
        who = self.student if self.student_id else self.guest
        return f'{who} — {self.session_date} ({self.get_status_display()})'
