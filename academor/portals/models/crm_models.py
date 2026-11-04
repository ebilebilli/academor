"""CRM: leads (müraciətlər) and tuition billing (hesablar / ödənişlər).

Leads gather every way someone reaches Academor (contact form, study-abroad form, level
test, phone, Instagram...) into one pipeline.

Billing follows how the office works: the fee belongs to the student's course registration
(Enrollment), not to the group. Every enrollment is billed monthly on its own day (counted
from its first payment date); payments record the course, the teacher and the teacher's share.
"""

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Lead(models.Model):
    class Source(models.TextChoices):
        CONTACT_FORM = 'contact_form', _('Saytın əlaqə formu')
        STUDY_ABROAD = 'study_abroad', _('Xaricdə təhsil formu')
        LEVEL_TEST = 'level_test', _('Səviyyə testi')
        ONLINE_PAYMENT = 'online_payment', _('Online ödəniş')
        PHONE = 'phone', _('Zəng')
        WHATSAPP = 'whatsapp', _('WhatsApp')
        INSTAGRAM = 'instagram', _('Instagram')
        WALK_IN = 'walk_in', _('Ofisə gəlib')
        REFERRAL = 'referral', _('Tövsiyə')
        CORPORATE = 'corporate', _('Korporativ')
        OTHER = 'other', _('Digər')

    class Status(models.TextChoices):
        NEW = 'new', _('Yeni')
        CONTACTED = 'contacted', _('Əlaqə saxlanıldı')
        TRIAL = 'trial', _('Sınaq dərsi')
        ENROLLED = 'enrolled', _('Qeydiyyatdan keçdi')
        LOST = 'lost', _('İtirildi')

    full_name = models.CharField(max_length=200, verbose_name=_('Ad, soyad'))
    phone = models.CharField(max_length=40, blank=True, verbose_name=_('Telefon'))
    email = models.EmailField(blank=True, verbose_name=_('E-poçt'))
    source = models.CharField(
        max_length=30, choices=Source.choices, default=Source.OTHER, verbose_name=_('Mənbə'),
    )
    interest = models.CharField(
        max_length=200, blank=True, verbose_name=_('Maraqlandığı kurs / xidmət'),
    )
    level = models.CharField(max_length=20, blank=True, verbose_name=_('Səviyyə'))
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.NEW, db_index=True,
        verbose_name=_('Status'),
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='crm_leads', verbose_name=_('Məsul şəxs'),
    )
    next_action_at = models.DateField(null=True, blank=True, verbose_name=_('Növbəti addım tarixi'))
    trial_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Sınaq dərsi vaxtı'))
    message = models.TextField(blank=True, verbose_name=_('Müraciət mətni'))
    lost_reason = models.CharField(max_length=200, blank=True, verbose_name=_('İtirilmə səbəbi'))
    student = models.ForeignKey(
        'StudentProfile', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='crm_leads', verbose_name=_('Tələbə'),
    )
    # where the lead came from, when it was created automatically
    contact_inquiry = models.OneToOneField(
        'projects.ContactInquiry', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='crm_lead',
    )
    study_abroad_application = models.OneToOneField(
        'projects.StudyAbroadApplication', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='crm_lead',
    )
    level_test_result = models.OneToOneField(
        'projects.UserResult', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='crm_lead',
    )
    created_at = models.DateTimeField(default=timezone.now, db_index=True, verbose_name=_('Yaradılıb'))
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at', '-id')
        verbose_name = _('Müraciət')
        verbose_name_plural = _('Müraciətlər')

    def __str__(self):
        return self.full_name

    @property
    def is_open(self):
        return self.status not in (self.Status.ENROLLED, self.Status.LOST)


class LeadActivity(models.Model):
    class Kind(models.TextChoices):
        NOTE = 'note', _('Qeyd')
        CALL = 'call', _('Zəng')
        MESSAGE = 'message', _('Mesaj')
        STATUS = 'status', _('Status dəyişdi')
        CREATED = 'created', _('Yaradıldı')

    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='activities')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='crm_activities',
    )
    kind = models.CharField(max_length=20, choices=Kind.choices, default=Kind.NOTE)
    text = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ('-created_at', '-id')


class Enrollment(models.Model):
    """A student's registration on a course: the fee, the teacher's share and the billing day."""

    class Status(models.TextChoices):
        ACTIVE = 'active', _('Aktiv')
        WAITING = 'waiting', _('Gözləyir')
        LEFT = 'left', _('Ayrıldı')
        FINISHED = 'finished', _('Bitirdi')

    student = models.ForeignKey(
        'StudentProfile', on_delete=models.CASCADE, related_name='crm_enrollments', verbose_name=_('Tələbə'),
    )
    course = models.CharField(max_length=120, verbose_name=_('Kurs'))
    group = models.ForeignKey(
        'StudyGroup', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='crm_enrollments', verbose_name=_('Qrup'),
    )
    teacher = models.ForeignKey(
        'TeacherProfile', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='crm_enrollments', verbose_name=_('Müəllim'),
    )
    monthly_fee = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('0'), verbose_name=_('Aylıq haqq (AZN)'),
    )
    teacher_percent = models.DecimalField(
        max_digits=6, decimal_places=3, default=Decimal('0'), verbose_name=_('Müəllim faizi (%)'),
    )
    start_date = models.DateField(default=timezone.localdate, verbose_name=_('Başlama tarixi'))
    # monthly charges fall on this day of every month, starting with this date
    first_due_date = models.DateField(
        null=True, blank=True, verbose_name=_('İlk ödəniş tarixi'),
        help_text=_('Hər ay bu günə hesab yazılır. Boş qalsa, başlama tarixi götürülür.'),
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.ACTIVE, db_index=True, verbose_name=_('Status'),
    )
    ended_at = models.DateField(null=True, blank=True, verbose_name=_('Ayrılma / bitmə tarixi'))
    leave_reason = models.CharField(max_length=255, blank=True, verbose_name=_('Ayrılma səbəbi'))
    note = models.CharField(max_length=255, blank=True, verbose_name=_('Qeyd'))
    lead = models.ForeignKey(
        Lead, null=True, blank=True, on_delete=models.SET_NULL, related_name='enrollments',
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='+',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('status', '-start_date', '-id')
        verbose_name = _('Kurs qeydiyyatı')
        verbose_name_plural = _('Kurs qeydiyyatları')

    def __str__(self):
        return f'{self.course} — {self.monthly_fee.normalize():f} AZN'

    @property
    def billing_anchor(self):
        return self.first_due_date or self.start_date

    @property
    def is_billable(self):
        return self.status == self.Status.ACTIVE and self.monthly_fee > 0 and self.billing_anchor is not None

    def due_date_for(self, n):
        """The n-th monthly due date (0 = the first one)."""
        import calendar

        anchor = self.billing_anchor
        y, m = divmod(anchor.month - 1 + n, 12)
        year, month = anchor.year + y, m + 1
        return anchor.replace(year=year, month=month, day=min(anchor.day, calendar.monthrange(year, month)[1]))

    def due_dates(self, until):
        n = 0
        while True:
            d = self.due_date_for(n)
            if d > until or (self.ended_at and d > self.ended_at):
                return
            yield d
            n += 1

    @property
    def next_due_date(self):
        if not self.is_billable:
            return None
        today = timezone.localdate()
        n = 0
        while True:
            d = self.due_date_for(n)
            if d > today:
                return d
            n += 1


class StudentCharge(models.Model):
    """What a student owes: a monthly fee, a package, an exam fee..."""

    class Kind(models.TextChoices):
        MONTHLY = 'monthly', _('Aylıq haqq')
        PACKAGE = 'package', _('Paket / kurs')
        EXAM = 'exam', _('İmtahan')
        OTHER = 'other', _('Digər')

    student = models.ForeignKey(
        'StudentProfile', on_delete=models.CASCADE, related_name='crm_charges', verbose_name=_('Tələbə'),
    )
    enrollment = models.ForeignKey(
        Enrollment, null=True, blank=True, on_delete=models.CASCADE,
        related_name='charges', verbose_name=_('Kurs'),
    )
    group = models.ForeignKey(
        'StudyGroup', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='crm_charges', verbose_name=_('Qrup'),
    )
    kind = models.CharField(max_length=20, choices=Kind.choices, default=Kind.MONTHLY, verbose_name=_('Növ'))
    # first day of the month the charge is for (monthly fees); free for other kinds
    period = models.DateField(null=True, blank=True, verbose_name=_('Ay'))
    description = models.CharField(max_length=200, blank=True, verbose_name=_('Açıqlama'))
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Məbləğ (AZN)'))
    due_date = models.DateField(verbose_name=_('Son ödəniş tarixi'))
    is_cancelled = models.BooleanField(default=False, verbose_name=_('Ləğv edilib'))
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='+',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-due_date', '-id')
        verbose_name = _('Hesab')
        verbose_name_plural = _('Hesablar')
        constraints = [
            models.UniqueConstraint(
                fields=('enrollment', 'period'),
                condition=models.Q(kind='monthly', is_cancelled=False, enrollment__isnull=False),
                name='crm_one_monthly_charge_per_enrollment_month',
            ),
        ]

    def __str__(self):
        return f'{self.student} — {self.amount} AZN'


class StudentPayment(models.Model):
    """Money received from (or on behalf of) a student."""

    class Method(models.TextChoices):
        CASH = 'cash', _('Nağd')
        CARD = 'card', _('Kart')
        CARD_UP = 'card_up', _('Kart - up')
        TRANSFER = 'transfer', _('Köçürmə')
        ONLINE = 'online', _('Online')

    class TeacherStatus(models.TextChoices):
        PENDING = 'pending', _('Ödənilməyib')
        PAID = 'paid', _('Ödənilib')
        NONE = 'none', _('Verilməyəcək')

    student = models.ForeignKey(
        'StudentProfile', on_delete=models.CASCADE, related_name='crm_payments', verbose_name=_('Tələbə'),
    )
    enrollment = models.ForeignKey(
        Enrollment, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='payments', verbose_name=_('Kurs qeydiyyatı'),
    )
    course = models.CharField(max_length=120, blank=True, verbose_name=_('Kurs'))
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Məbləğ (AZN)'))
    method = models.CharField(max_length=20, choices=Method.choices, default=Method.CASH, verbose_name=_('Üsul'))
    is_new_customer = models.BooleanField(default=False, verbose_name=_('Yeni müştəri'))
    teacher = models.ForeignKey(
        'TeacherProfile', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='crm_payments', verbose_name=_('Müəllim'),
    )
    teacher_percent = models.DecimalField(
        max_digits=6, decimal_places=3, default=Decimal('0'), verbose_name=_('Müəllim faizi (%)'),
    )
    teacher_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('0'), verbose_name=_('Müəllimə düşən (AZN)'),
    )
    teacher_status = models.CharField(
        max_length=20, choices=TeacherStatus.choices, default=TeacherStatus.PENDING, db_index=True,
        verbose_name=_('Müəllimə ödəniş'),
    )
    teacher_paid_at = models.DateField(null=True, blank=True, verbose_name=_('Müəllimə ödənildi'))
    paid_at = models.DateField(default=timezone.localdate, verbose_name=_('Ödəniş tarixi'))
    # corporate / parent payer, e.g. "LANDAU School" paying for an employee
    payer = models.CharField(max_length=200, blank=True, verbose_name=_('Ödəyən (şirkət / valideyn)'))
    note = models.CharField(max_length=255, blank=True, verbose_name=_('Qeyd'))
    receipt_number = models.CharField(max_length=30, blank=True, unique=True, null=True, verbose_name=_('Qəbz №'))
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='+',
        verbose_name=_('Qəbul edən'),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-paid_at', '-id')
        verbose_name = _('Ödəniş')
        verbose_name_plural = _('Ödənişlər')

    def __str__(self):
        return f'{self.student} — {self.amount} AZN'

    @property
    def school_amount(self):
        return self.amount - self.teacher_amount

    def apply_teacher_share(self):
        """Teacher's money from the percent; nothing to pay without a teacher or a percent."""
        if self.teacher_id and self.teacher_percent and self.teacher_percent > 0:
            self.teacher_amount = (self.amount * self.teacher_percent / 100).quantize(Decimal('0.01'))
            if self.teacher_status == self.TeacherStatus.NONE:
                self.teacher_status = self.TeacherStatus.PENDING
        else:
            self.teacher_amount = Decimal('0')
            self.teacher_status = self.TeacherStatus.NONE

    def save(self, *args, **kwargs):
        if self.enrollment_id and not self.course:
            self.course = self.enrollment.course
        super().save(*args, **kwargs)
        if not self.receipt_number:
            self.receipt_number = f'Q-{self.paid_at:%y%m}-{self.pk:05d}'
            super().save(update_fields=['receipt_number'])

