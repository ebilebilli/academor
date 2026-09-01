from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from portals.utils.normalize_phone_number import phone_number_validator


class SocialLinksMixin(models.Model):
    instagram = models.URLField(blank=True, verbose_name=_('Instagram URL'))
    facebook = models.URLField(blank=True, verbose_name=_('Facebook URL'))
    linkedin = models.URLField(blank=True, verbose_name=_('LinkedIn URL'))
    youtube = models.URLField(blank=True, verbose_name=_('YouTube URL'))

    class Meta:
        abstract = True


class StudentProfile(SocialLinksMixin, models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_profile',
        verbose_name=_('User'),
    )
    profile_image = models.ImageField(
        upload_to='portals/profiles/students/',
        null=True,
        blank=True,
        verbose_name=_('Profile photo'),
    )
    bio = models.TextField(
        blank=True,
        verbose_name=_('Bio'),
    )
    enrollment_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Enrollment date'),
    )
    lessons_per_month = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Lessons per month'),
        help_text=_('Expected number of lessons per month (e.g. 8 or 12).'),
    )
    program_month = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Program month'),
        help_text=_('Which month of the program the student is in (1, 2, 3…).'),
    )
    phone = models.CharField(
        max_length=30,
        blank=True,
        validators=[phone_number_validator],
        verbose_name=_('Phone'),
    )

    class Meta:
        verbose_name = _('Student profile')
        verbose_name_plural = _('Student profiles')
        ordering = ('user__username', 'id')

    @property
    def full_name(self) -> str:
        return self.user.get_username() if self.user_id else ''

    def get_course_type_codes(self):
        from portals.utils.student_courses import get_student_course_type_codes

        return get_student_course_type_codes(self.pk) if self.pk else []

    def get_active_course_specializations(self):
        if not self.pk:
            return self.course_specializations.none()
        return self.course_specializations.filter(is_active=True)

    def get_course_type_labels(self):
        from portals.utils.portal_services import get_course_type_label_map

        labels = get_course_type_label_map()
        return [labels.get(code, code) for code in self.get_course_type_codes()]

    def __str__(self):
        name = self.full_name or '—'
        return str(_('Student: %(name)s') % {'name': name})


class CustomerProfile(models.Model):
    """Paid mock-test portal user (not a full student)."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='customer_profile',
        verbose_name=_('User'),
    )
    phone = models.CharField(
        max_length=30,
        blank=True,
        validators=[phone_number_validator],
        verbose_name=_('Phone'),
    )
    ielts_mock_credits = models.PositiveIntegerField(
        default=0,
        verbose_name=_('IELTS mock credits'),
        help_text=_('One credit is consumed when the customer starts an IELTS mock test.'),
    )
    sat_mock_credits = models.PositiveIntegerField(
        default=0,
        verbose_name=_('SAT mock credits'),
        help_text=_('One credit is consumed when the customer starts a SAT mock test.'),
    )
    teacher = models.ForeignKey(
        'TeacherProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='customers',
        verbose_name=_('Reviewing teacher'),
        help_text=_('Teacher who reviews this customer\'s mock Writing and Speaking submissions.'),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))

    class Meta:
        verbose_name = _('Customer profile')
        verbose_name_plural = _('Customer profiles')
        ordering = ('user__username', 'id')

    @property
    def full_name(self) -> str:
        return self.user.get_username() if self.user_id else ''

    @property
    def mock_credits(self) -> int:
        return int(self.ielts_mock_credits or 0) + int(self.sat_mock_credits or 0)

    def mock_credits_for_program(self, exam_program: str) -> int:
        from portals.utils.mock_programs import IELTS_SERVICE, SAT_SERVICE

        if exam_program == IELTS_SERVICE:
            return int(self.ielts_mock_credits or 0)
        if exam_program == SAT_SERVICE:
            return int(self.sat_mock_credits or 0)
        return 0

    def __str__(self):
        name = self.full_name or '—'
        return str(_('Customer: %(name)s') % {'name': name})


class ParentProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='parent_profile',
        verbose_name=_('User'),
    )
    students = models.ManyToManyField(
        StudentProfile,
        related_name='parent_profiles',
        verbose_name=_('Linked students'),
        blank=True,
    )
    phone = models.CharField(
        max_length=30,
        blank=True,
        validators=[phone_number_validator],
        verbose_name=_('Phone'),
    )

    class Meta:
        verbose_name = _('Parent profile')
        verbose_name_plural = _('Parent profiles')
        ordering = ('user__username', 'id')

    @property
    def full_name(self) -> str:
        return self.user.get_username() if self.user_id else ''

    def __str__(self):
        name = self.full_name or '—'
        return str(_('Parent: %(name)s') % {'name': name})


class TeacherProfile(SocialLinksMixin, models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='teacher_profile',
        verbose_name=_('User'),
    )
    profile_image = models.ImageField(
        upload_to='portals/profiles/teachers/',
        null=True,
        blank=True,
        verbose_name=_('Profile photo'),
    )
    specialization = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Specialization'),
    )
    bio = models.TextField(
        blank=True,
        verbose_name=_('Bio'),
    )
    phone = models.CharField(
        max_length=30,
        blank=True,
        validators=[phone_number_validator],
        verbose_name=_('Phone'),
    )

    class Meta:
        verbose_name = _('Teacher profile')
        verbose_name_plural = _('Teacher profiles')
        ordering = ('user__username', 'id')

    @property
    def full_name(self) -> str:
        return self.user.get_username() if self.user_id else ''

    def __str__(self):
        name = self.full_name or '—'
        return str(_('Teacher: %(name)s') % {'name': name})

    def get_course_type_codes(self):
        return list(self.course_specializations.values_list('course_type', flat=True))

    def get_course_type_labels(self):
        from portals.utils.portal_services import get_course_type_label_map

        labels = get_course_type_label_map()
        return [labels.get(code, code) for code in self.get_course_type_codes()]


class StudentCourseSpecialization(models.Model):
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='course_specializations',
        verbose_name=_('Student'),
    )
    course_type = models.CharField(
        max_length=255,
        verbose_name=_('Service'),
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Active'),
        help_text=_('Only active enrollments grant quiz and classroom access for this service.'),
    )

    class Meta:
        verbose_name = _('Student service')
        verbose_name_plural = _('Student services')
        constraints = [
            models.UniqueConstraint(
                fields=('student', 'course_type'),
                name='portals_student_course_type_uniq',
            ),
        ]
        ordering = ('course_type', 'id')

    def __str__(self):
        from portals.utils.portal_services import resolve_course_type_label

        label = resolve_course_type_label(self.course_type)
        if not self.is_active:
            return f'{label} ({_("inactive")})'
        return label

    def _course_type_is_allowed(self) -> bool:
        from portals.utils.portal_services import is_active_portal_course_type

        if not self.course_type or is_active_portal_course_type(self.course_type):
            return True
        if self.pk:
            previous = (
                StudentCourseSpecialization.objects.filter(pk=self.pk)
                .values_list('course_type', flat=True)
                .first()
            )
            if previous == self.course_type:
                return True
        return False

    def clean(self):
        super().clean()
        if not self._course_type_is_allowed():
            raise ValidationError({
                'course_type': _('Course type "%(code)s" is not linked to an active site service.') % {
                    'code': self.course_type,
                },
            })

    def save(self, *args, **kwargs):
        if not self._course_type_is_allowed():
            # ValidationError (not ValueError) so admin/forms show a field
            # error instead of a 500.
            raise ValidationError(
                f'Course type "{self.course_type}" is not linked to an active site service.',
            )
        super().save(*args, **kwargs)


class TeacherCourseSpecialization(models.Model):
    teacher = models.ForeignKey(
        TeacherProfile,
        on_delete=models.CASCADE,
        related_name='course_specializations',
        verbose_name=_('Teacher'),
    )
    course_type = models.CharField(
        max_length=255,
        verbose_name=_('Course type'),
    )

    class Meta:
        verbose_name = _('Course specialization')
        verbose_name_plural = _('Course specializations')
        constraints = [
            models.UniqueConstraint(
                fields=('teacher', 'course_type'),
                name='portals_teacher_course_type_uniq',
            ),
        ]
        ordering = ('course_type', 'id')

    def __str__(self):
        from portals.utils.portal_services import resolve_course_type_label

        return resolve_course_type_label(self.course_type)

    def _course_type_is_allowed(self) -> bool:
        from portals.utils.portal_services import is_active_portal_course_type

        if not self.course_type or is_active_portal_course_type(self.course_type):
            return True
        if self.pk:
            previous = (
                TeacherCourseSpecialization.objects.filter(pk=self.pk)
                .values_list('course_type', flat=True)
                .first()
            )
            if previous == self.course_type:
                return True
        return False

    def clean(self):
        super().clean()
        if not self._course_type_is_allowed():
            raise ValidationError({
                'course_type': _('Course type "%(code)s" is not linked to an active site service.') % {
                    'code': self.course_type,
                },
            })

    def save(self, *args, **kwargs):
        if not self._course_type_is_allowed():
            raise ValidationError(
                f'Course type "{self.course_type}" is not linked to an active site service.',
            )
        super().save(*args, **kwargs)
