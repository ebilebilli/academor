from django.contrib import admin
from django.db.models import Q
from django.db import models, transaction
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import reverse
from django import forms
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet
from ckeditor.widgets import CKEditorWidget

from projects.models import *
from projects.admin.mixins import AcademorModelAdmin, install_admin_help
from projects.admin.order_fields import apply_order_choice_field
from projects.utils.cache_utils import invalidate_sale_cache, invalidate_model_cache


class AdminImageCompressMixin:
    class Media:
        js = ('assets/js/admin_image_compress.js',)


# Media
@admin.register(Media)
class MediaAdmin(AdminImageCompressMixin, AcademorModelAdmin):
    list_display = (
        'id',
        'media_preview',
        'background_flags',
        'created_at',
    )
    list_display_links = ('media_preview',)
    list_filter = (
        'is_about_page_background_image',
        'is_contact_page_background_image',
        'is_project_page_background_image',
        'is_courses_page_background_image',
        'is_tests_page_background_image',
        'is_service_page_background_image',
        'is_abroad_page_background_image',
        'created_at',
    )
    readonly_fields = ('created_at', 'media_preview_detailed')

    fieldsets = (
        (None, {
            'fields': ('image', 'media_preview_detailed'),
            'description': (
                'Upload a wide banner image. Then assign it to exactly one page below. '
                'This list only shows images already assigned to a page header.'
            ),
        }),
        ('Background assignments', {
            'description': (
                'Tick exactly one role per image where possible. '
                'Study abroad page background image: header on /abroad/ and abroad detail pages '
                '(if unset, the About page background image is used).'
            ),
            'fields': (
                'is_about_page_background_image',
                'is_contact_page_background_image',
                'is_project_page_background_image',
                'is_courses_page_background_image',
                'is_tests_page_background_image',
                'is_service_page_background_image',
                'is_abroad_page_background_image',
            ),
        }),
    )

    ordering = ('-created_at',)
    list_per_page = 25

    _NON_HOME_HEADER_BG_FIELDS = (
        'is_about_page_background_image',
        'is_contact_page_background_image',
        'is_project_page_background_image',
        'is_courses_page_background_image',
        'is_tests_page_background_image',
        'is_service_page_background_image',
        'is_footer_background_image',
        'is_abroad_page_background_image',
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj and any(getattr(obj, f, False) for f in self._NON_HOME_HEADER_BG_FIELDS):
            if 'image' in form.base_fields:
                form.base_fields['image'].widget.attrs['data-no-compress'] = '1'
        return form

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(
            Q(is_about_page_background_image=True)
            | Q(is_contact_page_background_image=True)
            | Q(is_project_page_background_image=True)
            | Q(is_courses_page_background_image=True)
            | Q(is_tests_page_background_image=True)
            | Q(is_service_page_background_image=True)
            | Q(is_abroad_page_background_image=True)
        )

    def media_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 80px; max-height: 80px; border-radius: 4px;" />',
                obj.image.url
            )
        return "-"
    media_preview.short_description = "Image"

    def media_preview_detailed(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 300px; border-radius: 8px;" />',
                obj.image.url
            )
        return "-"
    media_preview_detailed.short_description = "Image preview"

    def background_flags(self, obj):
        page_labels = (
            ('is_about_page_background_image', 'About page'),
            ('is_contact_page_background_image', 'Contact page'),
            ('is_project_page_background_image', 'Projects page'),
            ('is_courses_page_background_image', 'Courses page'),
            ('is_tests_page_background_image', 'Tests pages'),
            ('is_service_page_background_image', 'Services page'),
            ('is_abroad_page_background_image', 'Study abroad page'),
        )
        flags = [label for field, label in page_labels if getattr(obj, field, False)]
        return ' | '.join(flags) if flags else '-'
    background_flags.short_description = "Background"


@admin.register(Tagline)
class TaglineAdmin(AcademorModelAdmin):
    list_display = (
        'id',
        'page',
        'text_preview',
        'is_active',
    )
    list_filter = ('is_active',)
    list_editable = ('is_active',)
    search_fields = ('text',)
    ordering = ('page', 'id')
    fieldsets = (
        (None, {
            'fields': ('page', 'is_active', 'text'),
            'description': (
                'One tagline per inner page banner (About, Courses, Blog, etc.). '
                'Homepage is not included.'
            ),
        }),
    )

    @admin.display(description='Description (AZ)')
    def text_preview(self, obj):
        text = (obj.text or '').strip()
        if not text:
            return '-'
        return text[:80] + ('…' if len(text) > 80 else '')

    def changelist_view(self, request, extra_context=None):
        """
        list_editable (order, is_active) may batch-save without firing post_save on some setups.
        """
        response = super().changelist_view(request, extra_context=extra_context)
        if (
            request.method == 'POST'
            and '_save' in request.POST
            and response.status_code == 302
        ):
            transaction.on_commit(lambda: invalidate_model_cache('Tagline'))
        return response



class MediaInlineBase(AdminImageCompressMixin, admin.TabularInline):
    model = Media
    extra = 1
    readonly_fields = ('created_at', 'thumbnail_preview')
    fields = ('image', 'video', 'thumbnail_preview', 'created_at')
    verbose_name = "Media"
    verbose_name_plural = "Media"
    
    def thumbnail_preview(self, obj):
        if obj and obj.image:
            return format_html(
                '<img src="{}" style="max-width: 60px; max-height: 60px; border-radius: 4px;" />',
                obj.image.url
            )
        return "-"
    thumbnail_preview.short_description = "Preview"


class MediaInlineAbout(MediaInlineBase):
    fields = (
        'image',
        'thumbnail_preview',
        'gallery_order',
        'gallery_name_az',
        'gallery_role_az',
        'gallery_tag_az',
        'gallery_name_en',
        'gallery_role_en',
        'gallery_tag_en',
        'gallery_name_ru',
        'gallery_role_ru',
        'gallery_tag_ru',
        'created_at',
    )
    max_num = 8
    extra = 1
    
    def get_formset(self, request, obj=None, **kwargs):
        from django.forms import BaseInlineFormSet
        from django.core.exceptions import ValidationError
        
        class MediaAboutFormSet(BaseInlineFormSet):
            def clean(self):
                super().clean()
                image_count = 0
                deleted_images = 0
                
                # Count existing images on the About instance
                if obj:
                    existing_images = obj.medias.filter(image__isnull=False).exclude(image='').count()
                else:
                    existing_images = 0
                
                for form in self.forms:
                    if form.cleaned_data:
                        is_deleted = form.cleaned_data.get('DELETE', False)
                        
                        if is_deleted:
                            if form.instance and form.instance.pk and form.instance.image:
                                deleted_images += 1
                        else:
                            if form.cleaned_data.get('image'):
                                if not form.instance.pk or (form.instance.pk and form.cleaned_data.get('image') != form.instance.image):
                                    image_count += 1
                
                total_images = existing_images - deleted_images + image_count
                
                if total_images > 12:
                    raise ValidationError(
                        'About page allows at most 12 images. Currently: {} existing, {} removed, {} new - total would be {}.'
                        .format(existing_images, deleted_images, image_count, total_images)
                    )
        
        kwargs['formset'] = MediaAboutFormSet
        return super().get_formset(request, obj, **kwargs)


class MediaInlineCategory(MediaInlineBase):
    fk_name = 'category'
    max_num = 1
    extra = 0
    can_delete = True
    fields = ('image', 'thumbnail_preview', 'created_at')
    verbose_name = 'Image'


class MediaInlineSale(MediaInlineBase):
    fk_name = 'sale'
    max_num = 1
    extra = 0
    can_delete = True
    fields = ('image', 'thumbnail_preview', 'created_at')
    verbose_name = 'Card image'
    verbose_name_plural = 'Card images'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('category')

    def get_formset(self, request, obj=None, **kwargs):
        from django.forms import BaseInlineFormSet
        from django.core.exceptions import ValidationError

        class MediaCategoryFormSet(BaseInlineFormSet):
            def clean(self):
                super().clean()
                image_count = 0
                deleted_images = 0
                existing_images = 0
                if obj:
                    existing_images = obj.medias.filter(
                        image__isnull=False,
                    ).exclude(image='').count()

                for form in self.forms:
                    if not form.cleaned_data:
                        continue
                    if form.cleaned_data.get('DELETE', False):
                        if form.instance and form.instance.pk and form.instance.image:
                            deleted_images += 1
                        continue
                    if form.cleaned_data.get('image'):
                        is_new = not form.instance.pk
                        is_replaced = (
                            form.instance.pk
                            and form.cleaned_data.get('image') != form.instance.image
                        )
                        if is_new or is_replaced:
                            image_count += 1

                total_images = existing_images - deleted_images + image_count
                if total_images > 1:
                    raise ValidationError(
                        'Each service may have only one image. '
                        'Remove the extra image or replace the existing one.'
                    )

        kwargs['formset'] = MediaCategoryFormSet
        return super().get_formset(request, obj, **kwargs)


class CoursePricePackageInline(admin.StackedInline):
    model = CoursePricePackage
    extra = 0
    classes = ('wide', 'course-price-package-inline')
    fieldsets = (
        (None, {
            'fields': (
                'package_tab',
                'name_az',
                'name_en',
                'name_ru',
            ),
            'description': (
                'Pick the payment tab where this package appears on the course page.'
            ),
        }),
        ('Package details', {
            'fields': (
                'months',
                'lesson_count',
                'lesson_minutes',
                'price',
            ),
        }),
        ('Display & status', {
            'fields': (
                'order',
                'is_active',
                'is_premium',
                'show_on_homepage',
            ),
        }),
    )
    ordering = ('package_tab', 'order', 'id')


@admin.register(CoursePricePackage)
class CoursePricePackageAdmin(AcademorModelAdmin):
    list_display = (
        'id',
        'course',
        'package_tab_badge',
        'name_az',
        'months',
        'lesson_count',
        'lesson_minutes',
        'price',
        'order',
        'is_active',
        'is_premium',
        'show_on_homepage',
    )
    list_filter = ('package_tab', 'is_active', 'is_premium', 'show_on_homepage', 'course')
    search_fields = ('name_az', 'name_en', 'name_ru', 'course__name_az', 'course__slug')
    list_editable = ('order', 'is_active', 'show_on_homepage')
    ordering = ('course', 'package_tab', 'order', 'id')
    autocomplete_fields = ('course',)
    fieldsets = (
        (None, {
            'fields': (
                'course',
                'package_tab',
                'order',
                'is_active',
                'is_premium',
                'show_on_homepage',
            ),
            'description': (
                'Each package is one pricing option on the course page payment tabs '
                'and in the payment popup.'
            ),
        }),
        ('Names', {
            'fields': ('name_az', 'name_en', 'name_ru'),
        }),
        ('Package details', {
            'fields': ('months', 'lesson_count', 'lesson_minutes', 'price'),
        }),
    )

    def package_tab_badge(self, obj):
        colors = {
            CoursePricePackage.PackageTab.GROUP_STANDARD: '#417690',
            CoursePricePackage.PackageTab.GROUP_INTENSIVE: '#205067',
            CoursePricePackage.PackageTab.INDIVIDUAL_STANDARD: '#6a8caf',
            CoursePricePackage.PackageTab.INDIVIDUAL_INTENSIVE: '#4a6f8f',
            CoursePricePackage.PackageTab.FULL_PACKAGE_GROUP: '#0d9488',
            CoursePricePackage.PackageTab.FULL_PACKAGE_INDIVIDUAL: '#0891b2',
            CoursePricePackage.PackageTab.FULL_PACKAGE_INSTALLMENT: '#7c3aed',
        }
        color = colors.get(obj.package_tab, '#6c757d')
        label = obj.get_package_tab_display()
        return format_html(
            '<span class="admin-price-tab-badge" style="background:{};">{}</span>',
            color,
            label,
        )

    package_tab_badge.short_description = 'Payment tab'
    package_tab_badge.admin_order_field = 'package_tab'

    def changelist_view(self, request, extra_context=None):
        """
        list_editable (order, is_active) can bypass post_save — bump cache for course prices.
        """
        response = super().changelist_view(request, extra_context=extra_context)
        if (
            request.method == 'POST'
            and '_save' in request.POST
            and response.status_code == 302
        ):
            transaction.on_commit(lambda: invalidate_model_cache('Service'))
        return response


class ServiceAdminForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = '__all__'
        widgets = {
            'description_az': CKEditorWidget(),
            'description_en': CKEditorWidget(),
            'description_ru': CKEditorWidget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_order_choice_field(self, model=Service, instance=self.instance)


@admin.register(Service)
class ServiceAdmin(AdminImageCompressMixin, AcademorModelAdmin):
    form = ServiceAdminForm
    list_display = (
        'id',
        'category_thumb',
        'card_icon_preview',
        'name_link',
        'instructors_display',
        'name_en',
        'name_ru',
        'order',
        'is_active',
        'show_on_main_page',
        'created_at',
    )
    list_display_links = ('id',)
    list_editable = ('order', 'is_active', 'show_on_main_page')
    list_filter = ('is_active', 'show_on_main_page', 'instructors', 'created_at')
    search_fields = (
        'name_az', 'name_en', 'name_ru',
        'description_az', 'description_en', 'description_ru',
        'instructors__name',
    )
    filter_horizontal = ('instructors', 'tags')
    ordering = ('order', 'id')
    list_per_page = 25
    exclude = ('slug', 'price')
    readonly_fields = ('created_at',)
    inlines = [CoursePricePackageInline, MediaInlineCategory]

    fieldsets = (
        ('Azerbaijani', {
            'fields': ('name_az', 'description_az', 'duration_months_az', 'lesson_count_az')
        }),
        ('English', {
            'fields': ('name_en', 'description_en', 'duration_months_en', 'lesson_count_en')
        }),
        ('Russian', {
            'fields': ('name_ru', 'description_ru', 'duration_months_ru', 'lesson_count_ru')
        }),
        ('Course details', {
            'fields': ('instructors', 'tags', 'has_certificate', 'is_online', 'is_offline'),
            'description': (
                'Add price packages in the section below. Choose a payment tab for each '
                '(group/individual, standard/intensive, full package, installments). '
                'Legacy "Price (AZN)" on the model is deprecated; use packages instead.'
            ),
        }),
        ('Service card (home & courses list)', {
            'fields': ('card_icon',),
            'description': (
                'Icon shown on service cards. Presets match Academor programs from SEO: '
                'General English, Speaking, IELTS, GMAT, GRE, YOS, ALES, study abroad, etc. '
                'Leave "Default" to auto-detect from the URL slug when possible.'
            ),
        }),
        ('Status', {
            'fields': ('order', 'is_active', 'show_on_main_page', 'created_at'),
            'description': (
                'Order: 0 = first on the site, courses list, and header dropdown; '
                '1 = next, and so on. Duplicate positions shift automatically on save.'
            ),
        }),
    )

    def category_thumb(self, obj):
        media = obj.medias.filter(image__isnull=False).exclude(image='').first()
        if media and media.image:
            return format_html(
                '<img src="{}" style="max-width: 48px; max-height: 48px; border-radius: 4px; object-fit: cover;" />',
                media.image.url,
            )
        return '-'

    category_thumb.short_description = 'Thumbnail'

    def card_icon_preview(self, obj):
        from projects.service_category_icons import resolve_service_category_icon

        icon = resolve_service_category_icon(obj.card_icon or '', obj.slug or '')
        return format_html(
            '<span style="display:inline-flex;align-items:center;justify-content:center;'
            'width:2rem;height:2rem;border-radius:50%;background:rgba(255,84,20,.12);'
            'color:#ff5414;"><i class="fa {}" aria-hidden="true"></i></span>',
            icon,
        )

    card_icon_preview.short_description = 'Card icon'

    def name_link(self, obj):
        url = reverse('admin:projects_service_change', args=[obj.pk])
        name = obj.name_az or 'Service'
        return format_html('<a href="{}" class="admin-link">{}</a>', url, name)
    name_link.short_description = "Name (AZ)"
    name_link.admin_order_field = 'name_az'

    def instructors_display(self, obj):
        names = list(obj.instructors.values_list('name', flat=True)[:3])
        if not names:
            return '-'
        extra = obj.instructors.count() - len(names)
        text = ', '.join(names)
        if extra > 0:
            text += f' (+{extra})'
        return text

    instructors_display.short_description = 'Trainers'


@admin.register(ContentTag)
class ContentTagAdmin(AcademorModelAdmin):
    list_display = ('name_az', 'slug', 'name_en', 'name_ru', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    search_fields = ('name_az', 'name_en', 'name_ru', 'slug')
    ordering = ('order', 'name_az', 'id')
    exclude = ('slug',)


class SaleAdminForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = '__all__'
        widgets = {
            'description_az': CKEditorWidget(),
            'description_en': CKEditorWidget(),
            'description_ru': CKEditorWidget(),
        }

    def clean(self):
        cleaned_data = super().clean()
        apply_prices = cleaned_data.get('apply_to_service_prices')
        services = cleaned_data.get('services')
        percent = cleaned_data.get('percent')
        if apply_prices and not services:
            raise ValidationError(
                'Select at least one service when "Apply discount to service prices" is enabled.'
            )
        if apply_prices and percent is None:
            raise ValidationError(
                'Enter a discount percentage when "Apply discount to service prices" is enabled.'
            )
        return cleaned_data


@admin.register(Sale)
class SaleAdmin(AcademorModelAdmin):
    form = SaleAdminForm
    inlines = (MediaInlineSale,)
    list_display = (
        'id',
        'name_short',
        'percent_display',
        'end_date',
        'services_count',
        'created_at',
        'apply_to_service_prices',
        'is_active',
        'show_on_homepage',
    )
    list_display_links = ('name_short',)
    list_filter = ('is_active', 'show_on_homepage', 'apply_to_service_prices', 'end_date', 'created_at', 'services')
    list_editable = ('is_active', 'show_on_homepage', 'apply_to_service_prices')
    search_fields = (
        'name_az', 'name_en', 'name_ru',
        'description_az', 'description_en', 'description_ru',
    )
    filter_horizontal = ('services',)
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    list_per_page = 25

    fieldsets = (
        ('Promotion', {
            'fields': (
                'percent',
                'end_date',
                'apply_to_service_prices',
                'services',
                'is_active',
                'show_on_homepage',
                'created_at',
            ),
            'description': (
                'Leave "Discount (%)" empty for announcement-only promotions (event, campaign, etc.). '
                'Enable "Apply discount to service prices" to reduce the listed prices of '
                'selected courses by the discount percentage - a discount value is then required. '
                'Leave services empty for a general homepage promotion without price changes.'
            ),
        }),
        ('Azerbaijani', {
            'fields': ('name_az', 'description_az'),
        }),
        ('English', {
            'fields': ('name_en', 'description_en'),
        }),
        ('Russian', {
            'fields': ('name_ru', 'description_ru'),
        }),
    )

    @admin.display(description='Name')
    def name_short(self, obj):
        title = (obj.name_az or obj.name_en or obj.name_ru or '').strip()
        if len(title) > 72:
            return title[:69] + '...'
        return title or '-'

    @admin.display(description='Discount')
    def percent_display(self, obj):
        if obj.percent is None:
            return '-'
        return format_html(
            '<span style="font-weight:600;color:#ff5414;">{}%</span>',
            obj.percent,
        )

    @admin.display(description='Services')
    def services_count(self, obj):
        count = obj.services.count()
        if count == 0:
            return '-'
        return count

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        transaction.on_commit(invalidate_sale_cache)

    def changelist_view(self, request, extra_context=None):
        """
        list_editable saves use QuerySet.update() and bypass Sale post_save signals.
        """
        response = super().changelist_view(request, extra_context=extra_context)
        if request.method == 'POST' and '_save' in request.POST and response.status_code == 302:
            transaction.on_commit(invalidate_sale_cache)
        return response


class AbroadModelAdminForm(forms.ModelForm):
    class Meta:
        model = AbroadModel
        fields = '__all__'
        widgets = {
            'description_az': CKEditorWidget(),
            'description_en': CKEditorWidget(),
            'description_ru': CKEditorWidget(),
        }


@admin.register(AbroadModel)
class AbroadModelAdmin(AdminImageCompressMixin, AcademorModelAdmin):
    form = AbroadModelAdminForm
    list_display = ('id', 'name_az', 'slug', 'name_en', 'name_ru', 'preview_image', 'is_active', 'show_on_main_page', 'created_at')
    list_filter = ('is_active', 'show_on_main_page', 'created_at')
    search_fields = ('name_az', 'name_en', 'name_ru', 'slug', 'description_az', 'description_en', 'description_ru')
    list_editable = ('is_active', 'show_on_main_page')
    readonly_fields = ('created_at', 'preview_image_large')
    list_per_page = 25
    fieldsets = (
        ('Content', {
            'fields': ('img', 'detail_page_img'),
            'description': (
                'Card image appears on /abroad/ list and homepage. '
                'Detail page image is the header on the individual program page.'
            ),
        }),
        ('Azerbaijani', {
            'fields': ('name_az', 'slug', 'description_az')
        }),
        ('English', {
            'fields': ('name_en', 'description_en')
        }),
        ('Russian', {
            'fields': ('name_ru', 'description_ru')
        }),
        ('Status', {
            'fields': ('is_active', 'show_on_main_page', 'created_at', 'preview_image_large')
        }),
    )

    def preview_image(self, obj):
        if obj.img:
            return format_html(
                '<img src="{}" style="max-width: 52px; max-height: 52px; border-radius: 6px; object-fit: cover;" />',
                obj.img.url,
            )
        return "-"
    preview_image.short_description = "Image"

    def preview_image_large(self, obj):
        if obj.img:
            return format_html(
                '<img src="{}" style="max-width: 280px; max-height: 220px; border-radius: 8px; object-fit: cover;" />',
                obj.img.url,
            )
        return "-"
    preview_image_large.short_description = "Preview"


class UniversityAdminForm(forms.ModelForm):
    class Meta:
        model = University
        fields = '__all__'
        widgets = {
            'description_az': CKEditorWidget(),
            'description_en': CKEditorWidget(),
            'description_ru': CKEditorWidget(),
        }


@admin.register(University)
class UniversityAdmin(AdminImageCompressMixin, AcademorModelAdmin):
    form = UniversityAdminForm
    list_display = ('id', 'name', 'slug', 'study_abroad', 'website_link', 'flag_preview', 'is_active')
    list_filter = ('is_active', 'study_abroad')
    list_editable = ('is_active',)
    readonly_fields = ('slug', 'flag_preview_large')
    search_fields = ('name', 'slug', 'description_az', 'description_en', 'description_ru')
    autocomplete_fields = ('study_abroad',)
    list_per_page = 25
    fieldsets = (
        ('Content', {
            'fields': ('name', 'slug', 'study_abroad', 'website', 'flag', 'flag_preview_large')
        }),
        ('Azerbaijani', {
            'fields': ('description_az',)
        }),
        ('English', {
            'fields': ('description_en',)
        }),
        ('Russian', {
            'fields': ('description_ru',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )

    def website_link(self, obj):
        if obj.website:
            return format_html(
                '<a href="{}" target="_blank" rel="noopener noreferrer" class="admin-link">{}</a>',
                obj.website,
                (obj.website.replace('https://', '').replace('http://', '').rstrip('/'))[:40],
            )
        return '-'
    website_link.short_description = 'Website'

    def flag_preview(self, obj):
        if obj.flag:
            return format_html(
                '<img src="{}" style="width: 48px; height: 48px; border-radius: 50%; object-fit: cover;" />',
                obj.flag.url,
            )
        return "-"
    flag_preview.short_description = "Flag"

    def flag_preview_large(self, obj):
        if obj.flag:
            return format_html(
                '<img src="{}" style="width: 96px; height: 96px; border-radius: 50%; object-fit: cover;" />',
                obj.flag.url,
            )
        return "-"
    flag_preview_large.short_description = "Preview"


class StudyAbroadSectionAdminForm(forms.ModelForm):
    class Meta:
        model = StudyAbroadSection
        fields = '__all__'
        widgets = {
            'text_az': CKEditorWidget(),
            'text_en': CKEditorWidget(),
            'text_ru': CKEditorWidget(),
        }


@admin.register(StudyAbroadSection)
class StudyAbroadSectionAdmin(AcademorModelAdmin):
    form = StudyAbroadSectionAdminForm
    search_fields = ('text_az', 'text_en', 'text_ru')
    fieldsets = (
        ('Azerbaijani', {'fields': ('text_az',)}),
        ('English', {'fields': ('text_en',)}),
        ('Russian', {'fields': ('text_ru',)}),
    )

    def has_add_permission(self, request):
        return not StudyAbroadSection.objects.exists()


@admin.register(StudyAbroadAdvantage)
class StudyAbroadAdvantageAdmin(AcademorModelAdmin):
    list_display = ('order', 'title_az', 'icon', 'section', 'is_active')
    list_display_links = ('title_az',)
    list_editable = ('order', 'is_active')
    list_filter = ('is_active', 'section')
    ordering = ('order', 'id')
    search_fields = ('title_az', 'title_en', 'title_ru')
    autocomplete_fields = ('section',)
    fieldsets = (
        ('Display', {
            'fields': ('section', 'order', 'is_active', 'icon'),
            'description': (
                'Link to the Study Abroad Section. Icon = Font Awesome 5 class (e.g. fa-certificate). '
                'Shown as a small highlight under the study abroad hero on the homepage and /abroad/.'
            ),
        }),
        ('Azerbaijani', {'fields': ('title_az',)}),
        ('English', {'fields': ('title_en',)}),
        ('Russian', {'fields': ('title_ru',)}),
    )


# About 
@admin.register(About)
class AboutAdmin(AdminImageCompressMixin, AcademorModelAdmin):
    list_display = ('id', 'title_link', 'show_on_homepage', 'media_count', 'video_status', 'updated_info')
    list_display_links = ('id',)
    search_fields = ('description_az', 'description_en', 'description_ru')
    inlines = [MediaInlineAbout]
    list_per_page = 25
    readonly_fields = ('video_cover_preview',)

    fieldsets = (
        ('Homepage', {
            'fields': ('show_on_homepage',),
            'description': 'Control whether the About section appears on the home page.',
        }),
        ('Description - Azerbaijani', {
            'fields': ('description_az',)
        }),
        ('Description - English', {
            'fields': ('description_en',)
        }),
        ('Description - Russian', {
            'fields': ('description_ru',)
        }),
        ('About page video', {
            'fields': ('video', 'video_cover', 'video_cover_preview'),
            'description': (
                'Upload a cover image (poster) and video file for the About page. '
                'The cover is shown until the visitor presses play.'
            ),
        }),
    )

    def title_link(self, obj):
        url = reverse('admin:projects_about_change', args=[obj.pk])
        return format_html(
            '<a href="{}" class="admin-link">About #{}</a>',
            url,
            obj.pk,
        )
    title_link.short_description = 'About'

    def media_count(self, obj):
        count = obj.medias.count()
        if count > 0:
            return format_html(
                '<span class="admin-badge admin-badge--blue">{} images</span>', count,
            )
        return format_html('<span class="admin-muted">0 images</span>')
    media_count.short_description = "Media"

    def video_status(self, obj):
        has_video = bool(obj.video)
        has_cover = bool(obj.video_cover)
        if has_video and has_cover:
            return format_html(
                '<span class="admin-badge admin-badge--green">Video + cover</span>'
            )
        if has_video:
            return format_html(
                '<span class="admin-badge admin-badge--yellow">Video only</span>'
            )
        if has_cover:
            return format_html(
                '<span class="admin-badge admin-badge--gray">Cover only</span>'
            )
        return "-"
    video_status.short_description = "Video"

    def video_cover_preview(self, obj):
        if obj and obj.video_cover:
            return format_html(
                '<img src="{}" style="max-width: 320px; max-height: 180px; border-radius: 8px; object-fit: cover;" />',
                obj.video_cover.url,
            )
        return "-"
    video_cover_preview.short_description = "Cover preview"
    
    def updated_info(self, obj):
        if hasattr(obj, 'updated_at'):
            return obj.updated_at.strftime('%d.%m.%Y %H:%M') if obj.updated_at else "-"
        return "-"
    updated_info.short_description = "Last updated"


@admin.register(AboutWhyItem)
class AboutWhyItemAdmin(AcademorModelAdmin):
    list_display = ('order', 'title_az', 'icon', 'is_active')
    list_display_links = ('title_az',)
    list_editable = ('order', 'is_active')
    list_filter = ('is_active',)
    ordering = ('order', 'id')
    search_fields = ('title_az', 'title_en', 'title_ru', 'text_az', 'text_en', 'text_ru')

    fieldsets = (
        ('Display', {
            'fields': ('order', 'is_active', 'icon'),
            'description': 'Font Awesome 5 icon class (e.g. fa-graduation-cap). Shown under the About page image.',
        }),
        ('Azerbaijani', {'fields': ('title_az', 'text_az')}),
        ('English', {'fields': ('title_en', 'text_en')}),
        ('Russian', {'fields': ('title_ru', 'text_ru')}),
    )


@admin.register(SiteFaqEntry)
class SiteFaqEntryAdmin(AcademorModelAdmin):
    list_display = ('order', 'question_short', 'is_active')
    list_display_links = ('question_short',)
    list_filter = ('is_active',)
    list_editable = ('order', 'is_active')
    ordering = ('order', 'id')
    search_fields = (
        'question_az', 'question_en', 'question_ru',
        'answer_az', 'answer_en', 'answer_ru',
    )

    fieldsets = (
        ('Display', {
            'fields': ('order', 'is_active'),
            'description': 'Lower order numbers appear first on the About page. Duplicate orders are shifted automatically on save.',
        }),
        ('Azerbaijani', {
            'fields': ('question_az', 'answer_az'),
        }),
        ('English', {
            'fields': ('question_en', 'answer_en'),
        }),
        ('Russian', {
            'fields': ('question_ru', 'answer_ru'),
        }),
    )

    def question_short(self, obj):
        q = (obj.question_az or obj.question_en or obj.question_ru or '').strip()
        if len(q) > 72:
            return q[:69] + '...'
        return q or '-'
    question_short.short_description = 'Question'


# Contact 
@admin.register(Contact)
class ContactAdmin(AdminImageCompressMixin, AcademorModelAdmin):
    list_display = (
        'id',
        'address_link',
        'contact_phone',
        'contact_email',
        'social_links',
    )
    list_display_links = ('address_link',)
    search_fields = (
        'address_az', 'address_en', 'address_ru',
        'phone', 'whatsapp_number',
        'email', 'email_2', 'email_3',
    )
    list_per_page = 25
    
    fieldsets = (
        ('Address', {
            'fields': ('address_az', 'address_en', 'address_ru')
        }),
        ('Map', {
            'fields': ('map_embed_url',),
            'description': 'Google Maps -> Share -> Embed map -> paste only the iframe src URL.',
        }),
        ('Phone numbers', {
            'fields': ('phone', 'whatsapp_number', 'whatsapp_number_2', 'phone_three')
        }),
        ('Email', {
            'fields': ('email', 'email_2', 'email_3'),
        }),
        ('Social networks', {
            'fields': ('instagram', 'facebook', 'youtube', 'linkedn', 'tiktok')
        }),
    )
    
    def address_link(self, obj):
        url = reverse('admin:projects_contact_change', args=[obj.pk])
        address = obj.address_az or 'Contact'
        label = address[:50] + '...' if len(address) > 50 else address
        return format_html('<a href="{}" class="admin-link">{}</a>', url, label)
    address_link.short_description = "Address"
    address_link.admin_order_field = 'address_az'

    def contact_phone(self, obj):
        phones = []
        if obj.phone:
            phones.append(format_html('<span class="admin-phone">{}</span>', obj.phone))
        if obj.whatsapp_number:
            phones.append(format_html('<span class="admin-whatsapp">WA: {}</span>', obj.whatsapp_number))
        return format_html('<br>'.join(phones)) if phones else "-"
    contact_phone.short_description = "Phones"

    def contact_email(self, obj):
        lines = []
        for addr in (obj.email, obj.email_2, obj.email_3):
            if addr:
                lines.append(
                    format_html(
                        '<a href="mailto:{}" class="admin-sender-email">{}</a>',
                        addr,
                        addr,
                    )
                )
        return format_html('<br>'.join(lines)) if lines else '-'
    contact_email.short_description = "Email"

    def social_links(self, obj):
        links = []
        if obj.instagram:
            links.append(format_html(
                '<a href="{}" target="_blank" class="admin-social admin-social--instagram">Instagram</a>',
                obj.instagram,
            ))
        if obj.facebook:
            links.append(format_html(
                '<a href="{}" target="_blank" class="admin-social admin-social--facebook">Facebook</a>',
                obj.facebook,
            ))
        if obj.youtube:
            links.append(format_html(
                '<a href="{}" target="_blank" class="admin-social admin-social--youtube">YouTube</a>',
                obj.youtube,
            ))
        if obj.linkedn:
            links.append(format_html(
                '<a href="{}" target="_blank" class="admin-social admin-social--linkedin">LinkedIn</a>',
                obj.linkedn,
            ))
        if obj.tiktok:
            links.append(format_html(
                '<a href="{}" target="_blank" class="admin-social admin-social--tiktok">TikTok</a>',
                obj.tiktok,
            ))
        return format_html(' '.join(links)) if links else "-"
    social_links.short_description = "Social links"


class TeamAdminForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = '__all__'
        widgets = {
            'description_az': CKEditorWidget(),
            'description_en': CKEditorWidget(),
            'description_ru': CKEditorWidget(),
        }


@admin.register(Team)
class TeamAdmin(AdminImageCompressMixin, AcademorModelAdmin):
    form = TeamAdminForm
    list_display = ('id', 'name', 'slug', 'role', 'order')
    list_editable = ('order',)
    readonly_fields = ('slug',)
    ordering = ('order', 'id')
    search_fields = (
        'name', 'slug', 'role',
        'description_az', 'description_en', 'description_ru',
        'instagram', 'facebook', 'linkedin', 'tiktok', 'youtube',
    )
    fieldsets = (
        (None, {
            'fields': ('image', 'name', 'slug', 'role', 'order'),
        }),
        ('Azerbaijani', {
            'fields': ('description_az',),
        }),
        ('English', {
            'fields': ('description_en',),
        }),
        ('Russian', {
            'fields': ('description_ru',),
        }),
        ('Social & files', {
            'fields': (
                'instagram', 'facebook', 'linkedin', 'tiktok', 'youtube',
                'descriptor',
            ),
        }),
    )
    list_per_page = 25


class BlogPostAdminForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = '__all__'
        widgets = {
            'description_az': CKEditorWidget(),
            'description_en': CKEditorWidget(),
            'description_ru': CKEditorWidget(),
        }


class BlogPostImageInline(AdminImageCompressMixin, admin.TabularInline):
    model = BlogPostImage
    extra = 1
    max_num = 6
    fields = ('image', 'order', 'image_preview')
    readonly_fields = ('image_preview',)
    ordering = ('order', 'id')

    @admin.display(description='Preview')
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:56px;width:84px;object-fit:cover;border-radius:4px;">',
                obj.image.url,
            )
        return '-'


@admin.register(BlogPost)
class BlogPostAdmin(AdminImageCompressMixin, AcademorModelAdmin):
    form = BlogPostAdminForm
    inlines = [BlogPostImageInline]
    filter_horizontal = ('tags',)
    list_display = (
        'cover_preview', 'name_az', 'slug', 'date', 'video_status',
        'is_active', 'on_top', 'on_main_page', 'created_at',
    )
    list_display_links = ('cover_preview', 'name_az')
    list_editable = ('is_active', 'on_top', 'on_main_page')
    list_filter = ('is_active', 'on_top', 'on_main_page', 'date', 'created_at')
    search_fields = (
        'name_az', 'name_en', 'name_ru', 'slug',
        'description_az', 'description_en', 'description_ru',
    )
    readonly_fields = ('slug', 'created_at', 'cover_preview_detail')
    ordering = ('-on_top', '-date', '-id')
    list_per_page = 25
    fieldsets = (
        (None, {
            'fields': ('slug', 'date', 'is_active', 'on_top', 'on_main_page', 'tags'),
        }),
        ('Media', {
            'fields': ('cover', 'cover_preview_detail', 'video'),
            'description': (
                'Upload a cover image for list cards and video poster. '
                'If a video is set, it is shown large on the article page.'
            ),
        }),
        ('Azerbaijani', {
            'fields': ('name_az', 'description_az'),
        }),
        ('English', {
            'fields': ('name_en', 'description_en'),
        }),
        ('Russian', {
            'fields': ('name_ru', 'description_ru'),
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Cover')
    def cover_preview(self, obj):
        if obj.cover:
            return format_html(
                '<img src="{}" style="height:48px;width:72px;object-fit:cover;border-radius:4px;">',
                obj.cover.url,
            )
        first = obj.images.order_by('order', 'id').first()
        if first and first.image:
            return format_html(
                '<img src="{}" style="height:48px;width:72px;object-fit:cover;border-radius:4px;">',
                first.image.url,
            )
        return '-'

    @admin.display(description='Cover preview')
    def cover_preview_detail(self, obj):
        return self.cover_preview(obj)

    @admin.display(description='Video')
    def video_status(self, obj):
        has_video = bool(obj.video)
        has_cover = bool(obj.cover)
        if has_video and has_cover:
            return format_html('<span style="color:#198754;">●</span> Video + cover')
        if has_video:
            return format_html('<span style="color:#fd7e14;">●</span> Video only')
        if has_cover:
            return format_html('<span style="color:#0d6efd;">●</span> Cover only')
        return '-'


@admin.register(Review)
class ReviewAdmin(AdminImageCompressMixin, AcademorModelAdmin):
    list_display = ('id', 'name', 'rating_stars', 'is_active', 'created_at')
    list_filter = ('is_active', 'rating', 'created_at')
    search_fields = ('name', 'phone', 'message')
    list_editable = ('is_active',)
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    list_per_page = 25
    fields = ('name', 'phone', 'message', 'rating', 'is_active', 'created_at')

    @admin.display(description='Stars')
    def rating_stars(self, obj):
        n = int(obj.rating or 0)
        star_on = '<i class="fas fa-star" style="color:#ffb800;font-size:13px;"></i>'
        star_off = '<i class="far fa-star" style="color:#ccc;font-size:13px;"></i>'
        return mark_safe(
            '<span aria-label="{}/5">{}{}</span>'.format(
                n,
                star_on * n,
                star_off * (5 - n),
            )
        )


class OptionInlineFormSet(BaseInlineFormSet):
    """At most 5 options per question (admin + POST tampering)."""

    def clean(self):
        super().clean()
        if any(self.errors):
            return
        kept = 0
        for form in self.forms:
            data = getattr(form, 'cleaned_data', None)
            if not data or data.get('DELETE'):
                continue
            if form.instance.pk:
                kept += 1
            elif (data.get('text') or '').strip():
                kept += 1
        if kept > 5:
            raise ValidationError('Each question can have at most 5 options.')


class OptionInline(AdminImageCompressMixin, admin.TabularInline):
    model = Option
    formset = OptionInlineFormSet
    extra = 1
    max_num = 5
    fields = ('text', 'is_correct')
    can_delete = True
    verbose_name_plural = 'Options (max 5)'

    def get_max_num(self, request, obj=None, **kwargs):
        """Cap at 5 when new; if DB already has >5, show all so staff can delete down to 5."""
        if obj is None:
            return 5
        return max(5, obj.options.count())


@admin.register(Test)
class TestAdmin(AdminImageCompressMixin, AcademorModelAdmin):
    list_display = ('id', 'list_title', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = (
        'title_az',
        'title_en',
        'title_ru',
        'description_az',
        'description_en',
        'description_ru',
    )
    list_editable = ('is_active',)
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    list_per_page = 25
    fieldsets = (
        ('Azerbaijani', {'fields': ('title_az', 'description_az')}),
        ('English', {'fields': ('title_en', 'description_en')}),
        ('Russian', {'fields': ('title_ru', 'description_ru')}),
        ('Other', {'fields': ('is_active', 'created_at')}),
    )

    @admin.display(description='Title')
    def list_title(self, obj):
        return obj.display_title() or '-'


@admin.register(Question)
class QuestionAdmin(AdminImageCompressMixin, AcademorModelAdmin):
    list_display = ('id', 'test', 'order', 'text')
    list_filter = ('test',)
    search_fields = (
        'text',
        'test__title_az',
        'test__title_en',
        'test__title_ru',
    )
    ordering = ('test', 'order', 'id')
    inlines = [OptionInline]
    list_per_page = 25


@admin.register(UserResult)
class UserResultAdmin(AdminImageCompressMixin, AcademorModelAdmin):
    list_display = ('id', 'test', 'first_name', 'last_name', 'number', 'email', 'score', 'level', 'created_at')
    list_filter = ('test', 'level', 'created_at')
    search_fields = ('first_name', 'last_name', 'number', 'email', 'level')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    list_per_page = 25

@admin.register(ContactInquiry)
class ContactInquiryAdmin(AdminImageCompressMixin, AcademorModelAdmin):
    list_display = (
        'sender_info',
        'subject_preview',
        'message_preview',
        'is_read',
        'read_status_badge',
        'created_at_formatted',
    )

    list_display_links = None
    list_editable = ('is_read',)
    list_filter = ('is_read', 'created_at', 'created_date')
    readonly_fields = ('created_at', 'created_date')
    search_fields = (
        'full_name',
        'email',
        'mobile_number',
        'subject',
        'info',
    )
    ordering = ('-created_at',)
    list_per_page = 25
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Sender', {
            'fields': ('full_name', 'email', 'mobile_number')
        }),
        ('Message', {
            'fields': ('subject', 'info')
        }),
        ('Status', {
            'fields': ('is_read',)
        }),
        ('Date', {
            'fields': ('created_at', 'created_date')
        }),
    )

    def sender_info(self, obj):
        detail_url = reverse('admin:projects_contactinquiry_change', args=[obj.pk])
        name = obj.full_name or "No name"
        email = obj.email or "No email"
        if obj.mobile_number:
            mobile_html = format_html(
                '<a href="tel:{}" class="admin-muted">{}</a>',
                obj.mobile_number,
                obj.mobile_number[:30] + ('...' if len(obj.mobile_number) > 30 else ''),
            )
        else:
            mobile_html = format_html(
                '<span class="admin-muted">No mobile number</span>',
            )

        return format_html(
            '<div class="admin-sender-block">'
            '<a href="{}" class="admin-sender-name">{}</a>'
            '<a href="mailto:{}" class="admin-sender-email">{}</a><br>'
            '{}'
            '</div>',
            detail_url,
            name,
            email,
            email[:30] + ('...' if len(email) > 30 else ''),
            mobile_html,
        )
    sender_info.short_description = "Sender"
    sender_info.admin_order_field = 'full_name'

    def subject_preview(self, obj):
        detail_url = reverse('admin:projects_contactinquiry_change', args=[obj.pk])
        subject = obj.subject or "No subject"
        
        return format_html(
            '<a href="{}" style="color: #417690; text-decoration: none; font-weight: 500; '
            'font-size: 14px;">{}</a>',
            detail_url,
            subject[:50] + ('...' if len(subject) > 50 else '')
        )
    subject_preview.short_description = "Subject"
    subject_preview.admin_order_field = 'subject'

    def message_preview(self, obj):
        message = obj.info or "No message"
        return format_html(
            '<span style="color: #666; font-size: 13px;">{}</span>',
            message[:80] + ('...' if len(message) > 80 else '')
        )
    message_preview.short_description = "Message"
    message_preview.admin_order_field = 'info'

    def read_status_badge(self, obj):
        if obj.is_read:
            return format_html(
                '<span class="admin-badge admin-badge--green">Read</span>'
            )
        return format_html(
            '<span class="admin-badge admin-badge--red">Unread</span>'
        )
    read_status_badge.short_description = "Status"
    read_status_badge.admin_order_field = 'is_read'

    def created_at_formatted(self, obj):
        return obj.created_at.strftime('%d.%m.%Y %H:%M')
    created_at_formatted.short_description = "Date"
    created_at_formatted.admin_order_field = 'created_at'

# Admin Site Customization
admin.site.site_header = "Academor Admin Panel"
admin.site.site_title = "Academor Admin"
admin.site.index_title = "Administration"

# Make admin index model order less chaotic (per-app).
_original_get_app_list = admin.site.get_app_list


def _sorted_get_app_list(request, app_label=None):
    app_list = _original_get_app_list(request, app_label)

    projects_model_order = {
        # Content / landing
        "Media": 10,
        "About": 20,
        "AboutWhyItem": 21,
        "SiteFaqEntry": 25,
        "Tagline": 26,
        "Contact": 30,

        # Team / reviews / blog
        "Team": 100,
        "Review": 110,
        "BlogPost": 115,

        # Services / study abroad
        "Service": 200,
        "CoursePricePackage": 201,
        "AbroadModel": 220,
        "StudyAbroadSection": 222,
        "StudyAbroadAdvantage": 223,
        "University": 225,

        # Inbound
        "ContactInquiry": 320,

        # Tests
        "Test": 400,
        "Question": 410,
        "UserResult": 430,
    }

    for app in app_list:
        if app.get("app_label") == "projects":
            app["models"].sort(key=lambda m: projects_model_order.get(m.get("object_name"), 9999))

    return app_list


admin.site.get_app_list = _sorted_get_app_list

install_admin_help()
