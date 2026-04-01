from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.conf import settings

# from projects.utils import send_mail_func
from projects.utils.cache_utils import invalidate_model_cache
from projects.models import (
    JobApplication,
    ContactInquiry,
    Service,
    ServiceCategory,
    Team,
    Review,
    CareerOpening,
    Instructor,
    About, 
    Contact, 
    Media,
    Tagline,
    AcademyStatistic,
    Program,
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


# Cache invalidation signals for models

@receiver(post_save, sender=Service)
@receiver(post_delete, sender=Service)
def invalidate_project_cache(sender, instance, **kwargs):
    """Invalidate cache when Project is saved or deleted."""
    invalidate_model_cache('Service')


@receiver(post_save, sender=ServiceCategory)
@receiver(post_delete, sender=ServiceCategory)
def invalidate_project_category_cache(sender, instance, **kwargs):
    """Invalidate cache when ProjectCategory is saved or deleted."""
    invalidate_model_cache('ServiceCategory')


@receiver(post_save, sender=CareerOpening)
@receiver(post_delete, sender=CareerOpening)
def invalidate_vacancy_cache(sender, instance, **kwargs):
    """Invalidate cache when Vacancy is saved or deleted."""
    invalidate_model_cache('CareerOpening')


@receiver(post_save, sender=Instructor)
@receiver(post_delete, sender=Instructor)
def invalidate_partner_cache(sender, instance, **kwargs):
    """Invalidate cache when Partner is saved or deleted."""
    invalidate_model_cache('Instructor')


@receiver(post_save, sender=About)
@receiver(post_delete, sender=About)
def invalidate_about_cache(sender, instance, **kwargs):
    """Invalidate cache when About is saved or deleted."""
    invalidate_model_cache('About')


@receiver(post_save, sender=Contact)
@receiver(post_delete, sender=Contact)
def invalidate_contact_cache(sender, instance, **kwargs):
    """Invalidate cache when Contact is saved or deleted."""
    invalidate_model_cache('Contact')


@receiver(post_save, sender=Team)
@receiver(post_delete, sender=Team)
def invalidate_team_cache(sender, instance, **kwargs):
    invalidate_model_cache('Team')


@receiver(post_save, sender=Review)
@receiver(post_delete, sender=Review)
def invalidate_review_cache(sender, instance, **kwargs):
    invalidate_model_cache('Review')


@receiver(post_save, sender=Program)
@receiver(post_delete, sender=Program)
def invalidate_service_cache(sender, instance, **kwargs):
    """Invalidate cache when Service is saved or deleted."""
    invalidate_model_cache('Program')


@receiver(post_save, sender=Media)
@receiver(post_delete, sender=Media)
def invalidate_media_cache(sender, instance, **kwargs):
    """Invalidate cache when Media is saved or deleted."""
    # Media can affect multiple models, so invalidate all related caches
    invalidate_model_cache('Media')
    
    # Also invalidate related model caches if media belongs to them
    # IMPORTANT: use *_id to avoid DoesNotExist during cascaded deletes
    # (accessing instance.project may trigger a DB fetch and fail mid-delete)
    if getattr(instance, 'project_id', None):
        invalidate_model_cache('Service')
    if getattr(instance, 'partner_id', None):
        invalidate_model_cache('Instructor')
    if getattr(instance, 'about_id', None):
        invalidate_model_cache('About')
    if getattr(instance, 'vacancy_id', None):
        invalidate_model_cache('CareerOpening')
    if getattr(instance, 'service_id', None):
        invalidate_model_cache('Program')
    
    # If media is a background image for home page, invalidate home page cache
    if instance.is_home_page_background_image:
        invalidate_model_cache('Media')


@receiver(post_save, sender=Tagline)
@receiver(post_delete, sender=Tagline)
def invalidate_motto_cache(sender, instance, **kwargs):
    """Invalidate cache when Motto is saved or deleted."""
    invalidate_model_cache('Tagline')
    # Motto affects home page, so invalidate home page cache
    invalidate_model_cache('Media')


@receiver(post_save, sender=AcademyStatistic)
@receiver(post_delete, sender=AcademyStatistic)
def invalidate_statistic_cache(sender, instance, **kwargs):
    """Invalidate cache when Statistic is saved or deleted."""
    from projects.utils.cache_utils import invalidate_query_cache
    # Invalidate statistics cache
    invalidate_query_cache(['get_statistics'])
    invalidate_model_cache('AcademyStatistic')


@receiver(post_save, sender=ContactInquiry)
@receiver(post_delete, sender=ContactInquiry)
def invalidate_appeal_contact_cache(sender, instance, **kwargs):
    """Invalidate cache when AppealContact is saved or deleted."""
    invalidate_model_cache('ContactInquiry')


@receiver(post_save, sender=Test)
@receiver(post_delete, sender=Test)
def invalidate_test_cache(sender, instance, **kwargs):
    invalidate_model_cache('Test')


@receiver(post_save, sender=Question)
@receiver(post_delete, sender=Question)
def invalidate_question_cache(sender, instance, **kwargs):
    invalidate_model_cache('Question')
    invalidate_model_cache('Test')


@receiver(post_save, sender=Option)
@receiver(post_delete, sender=Option)
def invalidate_option_cache(sender, instance, **kwargs):
    invalidate_model_cache('Option')
    invalidate_model_cache('Question')
    invalidate_model_cache('Test')


@receiver(post_save, sender=UserResult)
@receiver(post_delete, sender=UserResult)
def invalidate_user_result_cache(sender, instance, **kwargs):
    invalidate_model_cache('UserResult')