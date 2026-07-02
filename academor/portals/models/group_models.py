from django.db import models
from django.utils.translation import gettext_lazy as _


class StudyGroup(models.Model):
    """
    Portal study group (named StudyGroup to avoid clashing with django.contrib.auth.Group).
    """

    teacher = models.ForeignKey(
        'TeacherProfile',
        on_delete=models.PROTECT,
        related_name='groups',
        verbose_name=_('Teacher'),
    )
    name = models.CharField(
        max_length=200,
        verbose_name=_('Name'),
    )
    courses = models.ManyToManyField(
        'projects.Service',
        related_name='study_groups',
        blank=True,
        verbose_name=_('Courses'),
        help_text=_('Site courses linked to this group.'),
    )
    start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Start date'),
    )
    max_students = models.PositiveIntegerField(
        default=12,
        verbose_name=_('Max students'),
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Active'),
    )
    students = models.ManyToManyField(
        'StudentProfile',
        related_name='groups',
        blank=True,
        verbose_name=_('Students'),
        help_text=_('Students in this group. One student may belong to several groups.'),
    )

    class Meta:
        verbose_name = _('Study group')
        verbose_name_plural = _('Study groups')
        ordering = ('-is_active', 'name', 'id')

    def __str__(self):
        return self.name

    def get_course_slugs(self):
        if hasattr(self, '_prefetched_objects_cache') and 'courses' in self._prefetched_objects_cache:
            return [course.slug for course in self.courses.all() if course.slug]
        return list(self.courses.values_list('slug', flat=True))

    def get_course_labels(self):
        from portals.utils.portal_services import localized_service_name

        if hasattr(self, '_prefetched_objects_cache') and 'courses' in self._prefetched_objects_cache:
            return [localized_service_name(course) for course in self.courses.all()]
        return [localized_service_name(course) for course in self.courses.all()]

    def get_portal_course_codes(self):
        from portals.utils.group_services import study_group_portal_codes

        return study_group_portal_codes(self)

    # Backward-compatible aliases (Classroom-style naming).
    get_service_slugs = get_course_slugs
    get_service_labels = get_course_labels
