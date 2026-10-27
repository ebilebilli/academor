from django.db import models
from django.utils.translation import gettext_lazy as _


class StudyAbroadApplication(models.Model):
    """Study-abroad consultation request sent from the abroad page or the homepage."""

    class ConsultationFormat(models.TextChoices):
        ONLINE = 'online', _('Online')
        IN_PERSON = 'in_person', _('Əyani')
        ANY = 'any', _('Fərq etmir')

    class StudyLevel(models.TextChoices):
        BACHELOR = 'bachelor', _('Bakalavr')
        MASTER = 'master', _('Magistratura')
        DOCTORATE = 'doctorate', _('Doktorantura')
        LANGUAGE_COURSE = 'language_course', _('Dil kursları')
        OTHER = 'other', _('Digər')

    class ScholarshipImportance(models.TextChoices):
        VERY_IMPORTANT = 'very_important', _('Çox önəmlidir')
        IMPORTANT = 'important', _('Önəmlidir')
        DOES_NOT_MATTER = 'does_not_matter', _('Fərq etmir')
        NO_SCHOLARSHIP = 'no_scholarship', _('Təqaüd istəmir')

    class TuitionBudget(models.TextChoices):
        UNDER_1000 = 'under_1000', _('$1,000-dən az')
        FROM_1000_TO_3000 = '1000_3000', _('$1,000–$3,000')
        FROM_3000_TO_5000 = '3000_5000', _('$3,000–$5,000')
        FROM_5000_TO_10000 = '5000_10000', _('$5,000–$10,000')
        OVER_10000 = 'over_10000', _('$10,000-dan çox')

    full_name = models.CharField(
        max_length=120,
        verbose_name=_('Ad və soyad'),
    )
    phone_number = models.CharField(
        max_length=30,
        verbose_name=_('Əlaqə nömrəsi'),
    )
    consultation_format = models.CharField(
        max_length=20,
        choices=ConsultationFormat.choices,
        verbose_name=_('İlkin konsultasiyanın formatı'),
    )
    study_level = models.CharField(
        max_length=20,
        choices=StudyLevel.choices,
        verbose_name=_('Təhsil səviyyəsi'),
    )
    desired_country = models.CharField(
        max_length=100,
        verbose_name=_('Təhsil almaq istədiyiniz ölkə'),
    )
    desired_major = models.CharField(
        max_length=150,
        verbose_name=_('Təhsil almaq istədiyiniz ixtisas'),
    )
    scholarship_importance = models.CharField(
        max_length=20,
        choices=ScholarshipImportance.choices,
        verbose_name=_('Təqaüdün əhəmiyyəti'),
    )
    tuition_budget = models.CharField(
        max_length=20,
        choices=TuitionBudget.choices,
        verbose_name=_('Təhsil haqqı üçün büdcə'),
    )
    international_certificates = models.TextField(
        max_length=1000,
        blank=True,
        verbose_name=_('Beynəlxalq sertifikatlar'),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Müraciət tarixi'),
    )

    class Meta:
        verbose_name = _('Xaricdə təhsil müraciəti')
        verbose_name_plural = _('Xaricdə təhsil müraciətləri')
        ordering = ('-created_at',)

    def __str__(self):
        return self.full_name
