from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.conf import settings
from django.db import transaction
from django.db.models import F

# from projects.utils import send_mail_func
from projects.utils.cache_utils import invalidate_model_cache
from projects.models import (
    ContactInquiry,
    ServiceCategory,
    ServiceHighlight,
    AbroadModel,
    StudyAbroadSection,
    University,
    Team,
    Review,
    Instructor,
    About,
    Contact,
    Media,
    Tagline,
    Test,
    Question,
    Option,
    UserResult,
)


# @receiver(post_save, sender=AppealVacancy)
# def send_mail_per_cv_appeal(sender, instance, created, **kwargs):
#     if not created:
#         return

#     subject = 'Website üzərindən CV göndərildi'

#     message = f"""
# Yeni CV daxil oldu 👇

# Vakansiya: {instance.vacancy}
# Ad Soyad: {instance.full_name}
# Email: {instance.email}
# Telefon: {instance.phone_number}
# Əlavə məlumat: {instance.info if instance.info else 'Yoxdur'}

# Tarix: {instance.created_at}
#     """

#     admin_email = settings.EMAIL_HOST_USER  

#     send_mail_func(
#         user_email=admin_email,
#         custom_subject=subject,
#         custom_message=message,
#         attachment_path=instance.cv.path,  
#         attachment_name=instance.cv.name 
#     )


# ── Order auto-shift signals ──────────────────────────────────────────────────

def _shift_order(model, instance, field='order'):
    """
    When saving `instance` with a given order value, push all OTHER records
    whose order >= new_order up by 1 so there are no duplicates.
    Only fires when a conflict actually exists (no unnecessary DB writes).
    """
    new_order = getattr(instance, field)
    exclude_pk = instance.pk or 0
    conflict_qs = model.objects.exclude(pk=exclude_pk).filter(**{field: new_order})
    if conflict_qs.exists():
        model.objects.exclude(pk=exclude_pk).filter(
            **{f'{field}__gte': new_order}
        ).update(**{field: F(field) + 1})


@receiver(pre_save, sender=ServiceCategory)
def auto_shift_service_category_order(sender, instance, **kwargs):
    _shift_order(ServiceCategory, instance)


@receiver(pre_save, sender=Team)
def auto_shift_team_order(sender, instance, **kwargs):
    _shift_order(Team, instance)


# ── Cache invalidation signals ────────────────────────────────────────────────

# Cache invalidation signals for models

def _invalidate_on_commit(model_name):
    transaction.on_commit(lambda: invalidate_model_cache(model_name))


@receiver(post_save, sender=ServiceCategory)
@receiver(post_delete, sender=ServiceCategory)
def invalidate_course_category_cache(sender, instance, **kwargs):
    """Invalidate cache when a course category (ServiceCategory) is saved or deleted."""
    _invalidate_on_commit('ServiceCategory')


@receiver(post_save, sender=ServiceHighlight)
@receiver(post_delete, sender=ServiceHighlight)
def invalidate_service_highlight_cache(sender, instance, **kwargs):
    _invalidate_on_commit('ServiceHighlight')


@receiver(post_save, sender=AbroadModel)
@receiver(post_delete, sender=AbroadModel)
def invalidate_abroad_cache(sender, instance, **kwargs):
    """Clears query + page cache (incl. Study Abroad list/detail, home abroad grid, nav dropdown)."""
    _invalidate_on_commit('AbroadModel')


@receiver(post_save, sender=University)
@receiver(post_delete, sender=University)
def invalidate_university_cache(sender, instance, **kwargs):
    """Clears cache for university flags marquee on home + Study Abroad page."""
    _invalidate_on_commit('University')


@receiver(post_save, sender=StudyAbroadSection)
@receiver(post_delete, sender=StudyAbroadSection)
def invalidate_study_abroad_section_cache(sender, instance, **kwargs):
    """Clears cache for Study Abroad intro text on the Study Abroad page."""
    _invalidate_on_commit('StudyAbroadSection')


@receiver(post_save, sender=Instructor)
@receiver(post_delete, sender=Instructor)
def invalidate_partner_cache(sender, instance, **kwargs):
    """Invalidate cache when Partner is saved or deleted."""
    _invalidate_on_commit('Instructor')


@receiver(post_save, sender=About)
@receiver(post_delete, sender=About)
def invalidate_about_cache(sender, instance, **kwargs):
    """Invalidate cache when About is saved or deleted."""
    _invalidate_on_commit('About')


@receiver(post_save, sender=Contact)
@receiver(post_delete, sender=Contact)
def invalidate_contact_cache(sender, instance, **kwargs):
    """Invalidate cache when Contact is saved or deleted."""
    _invalidate_on_commit('Contact')


@receiver(post_save, sender=Team)
@receiver(post_delete, sender=Team)
def invalidate_team_cache(sender, instance, **kwargs):
    _invalidate_on_commit('Team')


@receiver(post_save, sender=Review)
@receiver(post_delete, sender=Review)
def invalidate_review_cache(sender, instance, **kwargs):
    _invalidate_on_commit('Review')


@receiver(post_save, sender=Media)
@receiver(post_delete, sender=Media)
def invalidate_media_cache(sender, instance, **kwargs):
    """Invalidate cache when Media is saved or deleted."""
    # Media can affect multiple models, so invalidate all related caches
    _invalidate_on_commit('Media')
    
    # Also invalidate related model caches if media belongs to them
    # IMPORTANT: use *_id to avoid DoesNotExist during cascaded deletes
    if getattr(instance, 'category_id', None):
        _invalidate_on_commit('ServiceCategory')
    if getattr(instance, 'partner_id', None):
        _invalidate_on_commit('Instructor')
    if getattr(instance, 'about_id', None):
        _invalidate_on_commit('About')



@receiver(post_save, sender=Tagline)
@receiver(post_delete, sender=Tagline)
def invalidate_motto_cache(sender, instance, **kwargs):
    """Invalidate cache when Tagline is saved or deleted."""
    _invalidate_on_commit('Tagline')


@receiver(post_save, sender=Test)
@receiver(post_delete, sender=Test)
def invalidate_test_cache(sender, instance, **kwargs):
    _invalidate_on_commit('Test')


@receiver(post_save, sender=Question)
@receiver(post_delete, sender=Question)
def invalidate_question_cache(sender, instance, **kwargs):
    _invalidate_on_commit('Question')
    _invalidate_on_commit('Test')


@receiver(post_save, sender=Option)
@receiver(post_delete, sender=Option)
def invalidate_option_cache(sender, instance, **kwargs):
    _invalidate_on_commit('Option')
    _invalidate_on_commit('Question')
    _invalidate_on_commit('Test')

