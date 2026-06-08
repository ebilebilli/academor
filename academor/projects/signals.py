"""
ORM signals: ordering helpers + cache invalidation.

All @cached_query / @cached_page_data in projects.utils.queries use a global
cache_version key. invalidate_model_cache() bumps that version, so every
persisted model that feeds those queries must call _invalidate_on_commit here.

Keep in sync with queries.py (add a receiver when a new cached query reads a model):
  Service (incl. card_icon → serialize_project_category `icon` on home + /courses/),
  CoursePricePackage (→ Service: packages in course list/detail + payments catalog),
  AbroadModel, StudyAbroadSection, StudyAbroadAdvantage, University,
  Team, Review, BlogPost, BlogPostImage, About, AboutWhyItem, Contact, Media, Tagline, SiteFaqEntry,
  Test, Question, Option

  Course detail (`course-detail.html`): `get_active_project_category_by_slug` + trainers M2M — invalidate
  `Service` on save/delete and on `instructors` M2M changes; `CoursePricePackage` save/delete
  (admin inline does not save the parent course); `Team` save/delete bumps all caches
  (including stale category detail with embedded trainer rows).
  (University: pre_save fills unique slug from name — university_slug_from_name.)
  Homepage blog hero + section preview rows use `_fresh_home_blog_context()` merged into `get_home_page_data()`
  (fresh on every GET; not stored inside the page blob).
  Homepage About block uses `get_home_about_context()` (`@cached_query`, per lang; not stored inside the page blob).

  Blog index (`projects:blog-page`, blog.html): `get_blog_page_data()` uses `@cached_page_data(CACHE_TIMEOUT_MEDIUM)`
  and calls cached `get_blog_posts(is_active=True)` (featured = `on_top`[:2], rest = listing). Invalidate via
  `invalidate_blog_post_cache` / `invalidate_blog_post_image_cache` so `cache_version` bumps and blog list + detail caches miss.

Not cached (no invalidation needed for public query cache): ContactInquiry, UserResult.
"""
from django.db.models.signals import post_save, post_delete, pre_save, m2m_changed
from django.dispatch import receiver
from django.db import transaction
from django.db.models import F
from django.utils.text import slugify

# from projects.utils import send_mail_func
from projects.utils.cache_utils import invalidate_model_cache
from projects.utils.image_resize import resize_image_field
from projects.models import (
    Service,
    CoursePricePackage,
    AbroadModel,
    StudyAbroadSection,
    StudyAbroadAdvantage,
    University,
    Team,
    Review,
    BlogPost,
    BlogPostImage,
    About,
    AboutWhyItem,
    Contact,
    Media,
    Tagline,
    SiteFaqEntry,
    Test,
    Question,
    Option,
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


@receiver(pre_save, sender=Service)
def auto_shift_service_order(sender, instance, **kwargs):
    _shift_order(Service, instance)


@receiver(pre_save, sender=Team)
def auto_shift_team_order(sender, instance, **kwargs):
    _shift_order(Team, instance)


# ── Cache invalidation signals ────────────────────────────────────────────────

# Cache invalidation signals for models

def _invalidate_on_commit(model_name):
    transaction.on_commit(lambda: invalidate_model_cache(model_name))


@receiver(post_save, sender=Service)
@receiver(post_delete, sender=Service)
def invalidate_service_cache(sender, instance, **kwargs):
    """
    Home / courses list / nav: cached `get_project_categories` and page blobs
    (`_get_home_page_data_cached`, `get_project_list_data`, …) embed serialized
    categories including `icon` from `card_icon` + slug hints.
    """
    _invalidate_on_commit('Service')


@receiver(m2m_changed, sender=Service.instructors.through)
def invalidate_service_instructors_m2m(sender, instance, **kwargs):
    """Admin filter_horizontal / M2M-only trainer links — no post_save on Service."""
    if kwargs.get('action') not in ('post_add', 'post_remove', 'post_clear'):
        return
    _invalidate_on_commit('Service')


@receiver(post_save, sender=CoursePricePackage)
@receiver(post_delete, sender=CoursePricePackage)
def invalidate_course_price_package_cache(sender, instance, **kwargs):
    """
    Price packages are prefetched on cached `get_project_categories` /
    `get_active_project_category_by_slug` and serialized into course cards/detail.
    Inline admin edits packages without touching Service.post_save.
    """
    _invalidate_on_commit('Service')


@receiver(post_save, sender=AbroadModel)
@receiver(post_delete, sender=AbroadModel)
def invalidate_abroad_cache(sender, instance, **kwargs):
    """Clears query + page cache (incl. Study Abroad list/detail, home abroad grid, nav dropdown)."""
    _invalidate_on_commit('AbroadModel')


@receiver(post_save, sender=University)
@receiver(post_delete, sender=University)
def invalidate_university_cache(sender, instance, **kwargs):
    """Bumps global cache version — clears university flags marquee (home/abroad listing),
    abroad-detail partner sidebar, university-detail profile, and any page that embeds
    university data (get_abroad_detail_view_context, get_university_detail_view_context, etc.)."""
    _invalidate_on_commit('University')


# University logos display at 80–192 px; 384 px covers 2× retina for the largest slot.
UNIVERSITY_FLAG_MAX_PX = 384


@receiver(pre_save, sender=University)
def resize_university_flag_on_upload(sender, instance, **kwargs):
    """Downscale oversized flag uploads before they hit storage / the public site."""
    if not instance.flag:
        return
    if instance.pk:
        try:
            old = University.objects.only('flag').get(pk=instance.pk)
            if old.flag.name == instance.flag.name:
                return
        except University.DoesNotExist:
            pass
    resize_image_field(
        instance.flag,
        max_width=UNIVERSITY_FLAG_MAX_PX,
        max_height=UNIVERSITY_FLAG_MAX_PX,
    )


@receiver(pre_save, sender=University)
def university_slug_from_name(sender, instance, **kwargs):
    """Unique slug from name (mirrors Team); skipped when name is empty — slug may stay null."""
    name = (instance.name or '').strip()
    if not name:
        return
    base = slugify(name) or 'university'
    if len(base) > 140:
        base = base[:140]
    slug = base
    n = 2
    qs = University.objects.exclude(pk=instance.pk) if instance.pk else University.objects.all()
    while qs.filter(slug=slug).exists():
        suffix = f'-{n}'
        slug = (base[: max(1, 150 - len(suffix))] + suffix)[:150]
        n += 1
    instance.slug = slug


@receiver(post_save, sender=StudyAbroadSection)
@receiver(post_delete, sender=StudyAbroadSection)
def invalidate_study_abroad_section_cache(sender, instance, **kwargs):
    """Clears cache for Study Abroad intro text on the Study Abroad page."""
    _invalidate_on_commit('StudyAbroadSection')


@receiver(post_save, sender=StudyAbroadAdvantage)
@receiver(post_delete, sender=StudyAbroadAdvantage)
def invalidate_study_abroad_advantage_cache(sender, instance, **kwargs):
    _invalidate_on_commit('StudyAbroadAdvantage')


@receiver(post_save, sender=About)
@receiver(post_delete, sender=About)
def invalidate_about_cache(sender, instance, **kwargs):
    """Invalidate cache when About is saved or deleted."""
    _invalidate_on_commit('About')


@receiver(post_save, sender=AboutWhyItem)
@receiver(post_delete, sender=AboutWhyItem)
def invalidate_about_why_cache(sender, instance, **kwargs):
    _invalidate_on_commit('AboutWhyItem')


@receiver(pre_save, sender=SiteFaqEntry)
def auto_shift_site_faq_entry_order(sender, instance, **kwargs):
    _shift_order(SiteFaqEntry, instance)


@receiver(post_save, sender=SiteFaqEntry)
@receiver(post_delete, sender=SiteFaqEntry)
def invalidate_site_faq_cache(sender, instance, **kwargs):
    _invalidate_on_commit('SiteFaqEntry')


@receiver(post_save, sender=Contact)
@receiver(post_delete, sender=Contact)
def invalidate_contact_cache(sender, instance, **kwargs):
    """Invalidate cache when Contact is saved or deleted."""
    _invalidate_on_commit('Contact')


@receiver(post_save, sender=Team)
@receiver(post_delete, sender=Team)
def invalidate_team_cache(sender, instance, **kwargs):
    """Home/team pages + course detail Trainers tab (via cached category-by-slug)."""
    _invalidate_on_commit('Team')


@receiver(post_save, sender=Review)
@receiver(post_delete, sender=Review)
def invalidate_review_cache(sender, instance, **kwargs):
    _invalidate_on_commit('Review')


@receiver(post_save, sender=BlogPost)
@receiver(post_delete, sender=BlogPost)
def invalidate_blog_post_cache(sender, instance, **kwargs):
    """
    Blog index (`get_blog_page_data`), post detail sidebar lists (`get_blog_detail_view_context`),
    and any other `@cached_*` helpers that pull `BlogPost` / `get_blog_posts`.
    """
    _invalidate_on_commit('BlogPost')


@receiver(post_save, sender=BlogPostImage)
@receiver(post_delete, sender=BlogPostImage)
def invalidate_blog_post_image_cache(sender, instance, **kwargs):
    """Cover/order changes affect serialized posts on blog listing and home fresh query reads same DB."""
    _invalidate_on_commit('BlogPost')


@receiver(post_save, sender=Media)
@receiver(post_delete, sender=Media)
def invalidate_media_cache(sender, instance, **kwargs):
    """Invalidate cache when Media is saved or deleted (hero bg, service imgs, etc.)."""
    # Single bump: invalidate_model_cache only raises global cache_version — one call is enough.
    _invalidate_on_commit('Media')



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

