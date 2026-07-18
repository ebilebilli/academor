from django.db import models
from django.utils.translation import gettext_lazy as _


class LessonCategory(models.Model):
    service = models.CharField(
        max_length=255,
        db_index=True,
        verbose_name=_('Service'),
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_('Name'),
    )

    class Meta:
        verbose_name = _('Lesson category')
        verbose_name_plural = _('Lesson categories')
        constraints = [
            models.UniqueConstraint(
                fields=('service', 'name'),
                name='portals_lesson_category_uniq',
            ),
        ]
        ordering = ('service', 'name', 'id')

    def __str__(self):
        from portals.utils.portal_services import resolve_course_type_label

        return f'{resolve_course_type_label(self.service)} — {self.name}'


class Lesson(models.Model):
    group = models.ForeignKey(
        'StudyGroup',
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name=_('Group'),
    )
    teacher = models.ForeignKey(
        'TeacherProfile',
        on_delete=models.PROTECT,
        related_name='lessons',
        verbose_name=_('Teacher'),
    )
    subject = models.CharField(
        max_length=255,
        db_index=True,
        verbose_name=_('Service'),
    )
    category = models.ForeignKey(
        LessonCategory,
        on_delete=models.PROTECT,
        related_name='lessons',
        null=True,
        blank=True,
        verbose_name=_('Category'),
    )
    name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('Name'),
    )
    lesson_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Lesson date'),
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Description'),
    )
    pdf_file = models.FileField(
        upload_to='portals/lessons/pdf/',
        null=True,
        blank=True,
        verbose_name=_('PDF file'),
    )
    video_url = models.URLField(
        blank=True,
        verbose_name=_('Video URL'),
    )
    image = models.ImageField(
        upload_to='portals/lessons/images/',
        null=True,
        blank=True,
        verbose_name=_('Image'),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at'),
    )

    class Meta:
        verbose_name = _('Lesson')
        verbose_name_plural = _('Lessons')
        ordering = ('-lesson_date', '-created_at', 'id')

    def __str__(self):
        from portals.utils.portal_services import resolve_course_type_label

        label = (self.name or '').strip() or resolve_course_type_label(self.subject)
        return f'{label} — {self.group.name}'

    @property
    def display_name(self):
        from portals.utils.portal_services import resolve_course_type_label

        return (self.name or '').strip() or resolve_course_type_label(self.subject)


class LessonAttachment(models.Model):
    class Kind(models.TextChoices):
        PDF = 'pdf', _('PDF')
        IMAGE = 'image', _('Image')
        VIDEO = 'video', _('Video')

    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name=_('Lesson'),
    )
    kind = models.CharField(
        max_length=16,
        choices=Kind.choices,
        verbose_name=_('Type'),
    )
    file = models.FileField(
        upload_to='portals/lessons/attachments/',
        null=True,
        blank=True,
        verbose_name=_('File'),
    )
    video_url = models.URLField(
        blank=True,
        verbose_name=_('Video URL'),
    )

    class Meta:
        verbose_name = _('Lesson attachment')
        verbose_name_plural = _('Lesson attachments')
        ordering = ('id',)

    def __str__(self):
        return f'{self.get_kind_display()} — {self.lesson_id}'


class LessonHomework(models.Model):
    class FileKind(models.TextChoices):
        PDF = 'pdf', _('PDF')
        WORD = 'word', _('Word')
        TXT = 'txt', _('Text')

    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='homeworks',
        verbose_name=_('Lesson'),
    )
    student = models.ForeignKey(
        'StudentProfile',
        on_delete=models.CASCADE,
        related_name='lesson_homeworks',
        verbose_name=_('Student'),
    )
    text = models.TextField(
        blank=True,
        verbose_name=_('Text'),
    )
    file = models.FileField(
        upload_to='portals/lessons/homework/',
        null=True,
        blank=True,
        verbose_name=_('File'),
    )
    original_filename = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Original filename'),
    )
    file_kind = models.CharField(
        max_length=16,
        choices=FileKind.choices,
        blank=True,
        verbose_name=_('File type'),
    )
    submitted_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Submitted at'),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at'),
    )

    class Meta:
        verbose_name = _('Lesson homework')
        verbose_name_plural = _('Lesson homeworks')
        ordering = ('-submitted_at', 'id')
        constraints = [
            models.UniqueConstraint(
                fields=('lesson', 'student'),
                name='portals_lesson_homework_lesson_student_uniq',
            ),
        ]

    def __str__(self):
        return f'{self.student_id} → lesson {self.lesson_id}'


class Classroom(models.Model):
    group = models.ForeignKey(
        'StudyGroup',
        on_delete=models.CASCADE,
        related_name='textbooks',
        null=True,
        blank=True,
        verbose_name=_('Group'),
    )
    teacher = models.ForeignKey(
        'TeacherProfile',
        on_delete=models.PROTECT,
        related_name='textbooks',
        null=True,
        blank=True,
        verbose_name=_('Teacher'),
    )
    name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('Name'),
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Description'),
    )
    pdf_file = models.FileField(
        upload_to='portals/classrooms/pdf/',
        null=True,
        blank=True,
        verbose_name=_('PDF file'),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at'),
    )
    services = models.ManyToManyField(
        'projects.Service',
        related_name='classrooms',
        blank=True,
        verbose_name=_('Services'),
        help_text=_('Legacy admin field — portal textbooks use group access instead.'),
    )

    class Meta:
        verbose_name = _('Textbook')
        verbose_name_plural = _('Textbooks')
        ordering = ('name', 'id')

    def __str__(self):
        return (self.name or '').strip() or str(_('Textbook %(pk)s') % {'pk': self.pk or '—'})

    @property
    def display_name(self):
        return (self.name or '').strip() or str(_('Textbook'))

    def get_service_slugs(self):
        if hasattr(self, '_prefetched_objects_cache') and 'services' in self._prefetched_objects_cache:
            return [service.slug for service in self.services.all() if service.slug]
        return list(self.services.values_list('slug', flat=True))

    def get_service_codes(self):
        return self.get_service_slugs()

    def get_service_labels(self):
        from portals.utils.portal_services import localized_service_name

        if hasattr(self, '_prefetched_objects_cache') and 'services' in self._prefetched_objects_cache:
            return [localized_service_name(service) for service in self.services.all()]
        return [
            localized_service_name(service)
            for service in self.services.all()
        ]

    def get_portal_course_codes(self):
        from portals.utils.portal_services import classroom_service_portal_codes

        return classroom_service_portal_codes(self.services.all())


class VideoRecord(models.Model):
    group = models.ForeignKey(
        'StudyGroup',
        on_delete=models.CASCADE,
        related_name='video_records',
        verbose_name=_('Group'),
    )
    title = models.CharField(
        max_length=255,
        verbose_name=_('Title'),
    )
    youtube_url = models.URLField(
        verbose_name=_('YouTube URL'),
    )
    lesson_date = models.DateField(
        verbose_name=_('Lesson date'),
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Description'),
    )

    class Meta:
        verbose_name = _('Video record')
        verbose_name_plural = _('Video records')
        ordering = ('-lesson_date', '-id')

    def __str__(self):
        return f'{self.title} ({self.lesson_date})'
