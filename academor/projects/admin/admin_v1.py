from django.contrib import admin
from django.db.models import Q
from django.db import models
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import reverse
from django import forms
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet
from ckeditor.widgets import CKEditorWidget

from projects.models import *


class AdminImageCompressMixin:
    class Media:
        js = ('assets/js/admin_image_compress.js',)


# Media
@admin.register(Media)
class MediaAdmin(AdminImageCompressMixin, admin.ModelAdmin):
    list_display = (
        'id',
        'media_preview',
        'background_flags',
        'created_at',
    )
    list_display_links = ('media_preview',)
    list_filter = (
        'is_home_page_background_image',
        'is_about_page_background_image',
        'is_contact_page_background_image',
        'is_project_page_background_image',
        'is_courses_page_background_image',
        'is_tests_page_background_image',
        'is_service_page_background_image',
        'is_footer_background_image',
        'is_abroad_page_background_image',
        'created_at',
    )
    readonly_fields = ('created_at', 'media_preview_detailed')

    fieldsets = (
        ('Media file', {
            'fields': ('image', 'media_preview_detailed')
        }),
        ('Background assignments', {
            'description': (
                'Tick exactly one role per image where possible. '
                'Study abroad page background image: header on /abroad/ and abroad detail pages '
                '(if unset, the About page background image is used).'
            ),
            'fields': (
                'is_home_page_background_image',
                'is_about_page_background_image',
                'is_contact_page_background_image',
                'is_project_page_background_image',
                'is_courses_page_background_image',
                'is_tests_page_background_image',
                'is_service_page_background_image',
                'is_footer_background_image',
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
            Q(is_home_page_background_image=True)
            | Q(is_about_page_background_image=True)
            | Q(is_contact_page_background_image=True)
            | Q(is_project_page_background_image=True)
            | Q(is_courses_page_background_image=True)
            | Q(is_tests_page_background_image=True)
            | Q(is_service_page_background_image=True)
            | Q(is_footer_background_image=True)
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
        flags = []
        if obj.is_home_page_background_image:
            flags.append("🏠 Home page")
        if obj.is_about_page_background_image:
            flags.append("ℹ️ About page")
        if obj.is_contact_page_background_image:
            flags.append("🤝 Contact page")
        if obj.is_project_page_background_image:
            flags.append("📁 Projects page")
        if obj.is_courses_page_background_image:
            flags.append("📚 Courses page")
        if obj.is_tests_page_background_image:
            flags.append("📝 Tests pages")
        if obj.is_service_page_background_image:
            flags.append("🛠️ Services page")
        if obj.is_footer_background_image:
            flags.append("🔻 Footer")
        if obj.is_abroad_page_background_image:
            flags.append("🌍 Study abroad page")
        return " | ".join(flags) if flags else "-"
    background_flags.short_description = "Background"



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


class MediaInlinePartner(MediaInlineBase):
    fields = ('image', 'thumbnail_preview', 'created_at')


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
                        'About page allows at most 12 images. Currently: {} existing, {} removed, {} new — total would be {}.'
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
    verbose_name_plural = 'Image'

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


class CoursePricePackageInline(admin.TabularInline):
    model = CoursePricePackage
    extra = 0
    classes = ('collapse',)
    fields = (
        'name_az',
        'name_en',
        'name_ru',
        'duration',
        'lesson_count',
        'lesson_minutes',
        'price',
        'order',
        'is_active',
    )
    ordering = ('order', 'id')


@admin.register(CoursePricePackage)
class CoursePricePackageAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'course',
        'name_az',
        'duration',
        'lesson_count',
        'lesson_minutes',
        'price',
        'order',
        'is_active',
    )
    list_filter = ('is_active', 'course')
    search_fields = ('name_az', 'name_en', 'name_ru', 'course__name_az', 'course__slug')
    list_editable = ('order', 'is_active')
    ordering = ('course', 'order', 'id')
    autocomplete_fields = ('course',)
    fieldsets = (
        (None, {
            'fields': ('course', 'order', 'is_active'),
        }),
        ('Names', {
            'fields': ('name_az', 'name_en', 'name_ru'),
        }),
        ('Package details', {
            'fields': ('duration', 'lesson_count', 'lesson_minutes', 'price'),
        }),
    )


class ServiceCategoryAdminForm(forms.ModelForm):
    class Meta:
        model = ServiceCategory
        fields = '__all__'
        widgets = {
            'description_az': CKEditorWidget(),
            'description_en': CKEditorWidget(),
            'description_ru': CKEditorWidget(),
        }


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(AdminImageCompressMixin, admin.ModelAdmin):
    form = ServiceCategoryAdminForm
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
    filter_horizontal = ('instructors',)
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
        ('Русский', {
            'fields': ('name_ru', 'description_ru', 'duration_months_ru', 'lesson_count_ru')
        }),
        ('Course details', {
            'fields': ('instructors', 'has_certificate', 'is_online', 'is_offline'),
            'description': (
                'Add one or more price packages below. '
                'Legacy “Price (AZN)” on the model is deprecated; use packages instead.'
            ),
        }),
        ('Service card (home & courses list)', {
            'fields': ('card_icon',),
            'description': (
                'Icon shown on service cards. Presets match Academor programs from SEO: '
                'General English, Speaking, IELTS, GMAT, GRE, YÖS, ALES, study abroad, etc. '
                'Leave “Default” to auto-detect from the URL slug when possible.'
            ),
        }),
        ('Status', {
            'fields': ('order', 'is_active', 'show_on_main_page', 'created_at')
        }),
    )

    def category_thumb(self, obj):
        media = obj.medias.filter(image__isnull=False).exclude(image='').first()
        if media and media.image:
            return format_html(
                '<img src="{}" style="max-width: 48px; max-height: 48px; border-radius: 4px; object-fit: cover;" />',
                media.image.url,
            )
        return '—'

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
        url = reverse('admin:projects_servicecategory_change', args=[obj.pk])
        name = obj.name_az or 'Category'
        return format_html('<a href="{}" style="color: #417690; text-decoration: none; font-weight: 600; font-size: 14px;">🔗 {}</a>', url, name)
    name_link.short_description = "Name (AZ)"
    name_link.admin_order_field = 'name_az'

    def instructors_display(self, obj):
        names = list(obj.instructors.values_list('name', flat=True)[:3])
        if not names:
            return '—'
        extra = obj.instructors.count() - len(names)
        text = ', '.join(names)
        if extra > 0:
            text += f' (+{extra})'
        return text

    instructors_display.short_description = 'Trainers'


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
class AbroadModelAdmin(AdminImageCompressMixin, admin.ModelAdmin):
    form = AbroadModelAdminForm
    list_display = ('id', 'name_az', 'slug', 'name_en', 'name_ru', 'preview_image', 'is_active', 'show_on_main_page', 'created_at')
    list_filter = ('is_active', 'show_on_main_page', 'created_at')
    search_fields = ('name_az', 'name_en', 'name_ru', 'slug', 'description_az', 'description_en', 'description_ru')
    list_editable = ('is_active', 'show_on_main_page')
    readonly_fields = ('created_at', 'preview_image_large')
    list_per_page = 25
    fieldsets = (
        ('Content', {
            'fields': ('img', 'detail_page_img')
        }),
        ('Azerbaijani', {
            'fields': ('name_az', 'slug', 'description_az')
        }),
        ('English', {
            'fields': ('name_en', 'description_en')
        }),
        ('Русский', {
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
        return "—"
    preview_image.short_description = "Image"

    def preview_image_large(self, obj):
        if obj.img:
            return format_html(
                '<img src="{}" style="max-width: 280px; max-height: 220px; border-radius: 8px; object-fit: cover;" />',
                obj.img.url,
            )
        return "—"
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
class UniversityAdmin(AdminImageCompressMixin, admin.ModelAdmin):
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
        ('Русский', {
            'fields': ('description_ru',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )

    def website_link(self, obj):
        if obj.website:
            return format_html(
                '<a href="{}" target="_blank" rel="noopener noreferrer" '
                'style="color: #417690; text-decoration: none; font-size: 13px;">🌐 {}</a>',
                obj.website,
                (obj.website.replace('https://', '').replace('http://', '').rstrip('/'))[:40],
            )
        return '—'
    website_link.short_description = 'Website'

    def flag_preview(self, obj):
        if obj.flag:
            return format_html(
                '<img src="{}" style="width: 48px; height: 48px; border-radius: 50%; object-fit: cover;" />',
                obj.flag.url,
            )
        return "—"
    flag_preview.short_description = "Flag"

    def flag_preview_large(self, obj):
        if obj.flag:
            return format_html(
                '<img src="{}" style="width: 96px; height: 96px; border-radius: 50%; object-fit: cover;" />',
                obj.flag.url,
            )
        return "—"
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
class StudyAbroadSectionAdmin(admin.ModelAdmin):
    form = StudyAbroadSectionAdminForm
    fieldsets = (
        ('Azerbaijani', {'fields': ('text_az',)}),
        ('English', {'fields': ('text_en',)}),
        ('Русский', {'fields': ('text_ru',)}),
    )

    def has_add_permission(self, request):
        return not StudyAbroadSection.objects.exists()


@admin.register(Instructor)
class InstructorAdmin(AdminImageCompressMixin, admin.ModelAdmin):
    list_display = (
        'id',
        'partner_logo',
        'name_link',
        'active_status',
        'created_at',
    )
    list_display_links = ('name_link',)
    list_filter = ('is_active', 'created_at')
    search_fields = ('name_az', 'name_en', 'name_ru')
    ordering = ('-created_at',)
    inlines = [MediaInlinePartner]
    readonly_fields = ('created_at', 'logo_preview')
    list_per_page = 25
    
    fieldsets = (
        ('Azerbaijani', {
            'fields': ('name_az',)
        }),
        ('English', {
            'fields': ('name_en',)
        }),
        ('Русский', {
            'fields': ('name_ru',)
        }),
        ('Social links', {
            'fields': ('instagram', 'facebook', 'linkedn')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Logo', {
            'fields': ('logo_preview',)
        }),
        ('Date', {
            'fields': ('created_at',)
        }),
    )
    
    def partner_logo(self, obj):
        media = obj.medias.first()
        if media and media.image:
            return format_html(
                '<img src="{}" style="max-width: 60px; max-height: 60px; border-radius: 4px; object-fit: contain;" />',
                media.image.url
            )
        return "❌"
    partner_logo.short_description = "Logo"
    
    def name_link(self, obj):
        url = reverse('admin:projects_instructor_change', args=[obj.pk])
        name = obj.name_az or 'Instructor'
        return format_html('<a href="{}" style="color: #417690; text-decoration: none; font-weight: 600; font-size: 14px;">🔗 {}</a>', url, name)
    name_link.short_description = "Name"
    name_link.admin_order_field = 'name_az'
    
    def logo_preview(self, obj):
        media = obj.medias.first()
        if media and media.image:
            return format_html(
                '<img src="{}" style="max-width: 250px; max-height: 250px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />',
                media.image.url
            )
        return "No logo"
    logo_preview.short_description = "Logo preview"
    
    def active_status(self, obj):
        if obj.is_active:
            return format_html('<span style="background: #28a745; color: white; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: bold;">✓ Active</span>')
        return format_html('<span style="background: #dc3545; color: white; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: bold;">✗ Inactive</span>')
    active_status.short_description = "Status"

# About 
@admin.register(About)
class AboutAdmin(AdminImageCompressMixin, admin.ModelAdmin):
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
        ('Description — Azerbaijani', {
            'fields': ('description_az',)
        }),
        ('Description — English', {
            'fields': ('description_en',)
        }),
        ('Description — Russian', {
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
            '<a href="{}" style="color: #417690; text-decoration: none; font-weight: 600; font-size: 14px;">🔗 About #{}</a>',
            url,
            obj.pk,
        )
    title_link.short_description = 'About'
    
    def media_count(self, obj):
        count = obj.medias.count()
        if count > 0:
            return format_html('<span style="background: #007bff; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px;">📷 {} images</span>', count)
        return "📷 0 images"
    media_count.short_description = "Media"

    def video_status(self, obj):
        has_video = bool(obj.video)
        has_cover = bool(obj.video_cover)
        if has_video and has_cover:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px;">🎬 Video + cover</span>'
            )
        if has_video:
            return format_html(
                '<span style="background: #ffc107; color: #212529; padding: 3px 8px; border-radius: 12px; font-size: 11px;">🎬 Video only</span>'
            )
        if has_cover:
            return format_html(
                '<span style="background: #6c757d; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px;">🖼 Cover only</span>'
            )
        return "—"
    video_status.short_description = "Video"

    def video_cover_preview(self, obj):
        if obj and obj.video_cover:
            return format_html(
                '<img src="{}" style="max-width: 320px; max-height: 180px; border-radius: 8px; object-fit: cover;" />',
                obj.video_cover.url,
            )
        return "—"
    video_cover_preview.short_description = "Cover preview"
    
    def updated_info(self, obj):
        if hasattr(obj, 'updated_at'):
            return obj.updated_at.strftime('%d.%m.%Y %H:%M') if obj.updated_at else "-"
        return "-"
    updated_info.short_description = "Last updated"


@admin.register(AboutWhyItem)
class AboutWhyItemAdmin(admin.ModelAdmin):
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
class SiteFaqEntryAdmin(admin.ModelAdmin):
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
            return q[:69] + '…'
        return q or '—'
    question_short.short_description = 'Question'


# Contact 
@admin.register(Contact)
class ContactAdmin(AdminImageCompressMixin, admin.ModelAdmin):
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
            'description': 'Google Maps → Share → Embed map → paste only the iframe src URL.',
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
        return format_html('<a href="{}" style="color: #417690; text-decoration: none; font-weight: 600; font-size: 14px;">🔗 {}</a>', url, address[:50] + '...' if len(address) > 50 else address)
    address_link.short_description = "Address"
    address_link.admin_order_field = 'address_az'
    
    def contact_phone(self, obj):
        phones = []
        if obj.phone:
            phones.append(format_html('<span style="color: #417690;">📞 {}</span>', obj.phone))
        if obj.whatsapp_number:
            phones.append(format_html('<span style="color: #25D366;">💬 {}</span>', obj.whatsapp_number))
        return format_html('<br>'.join(phones)) if phones else "-"
    contact_phone.short_description = "Phones"
    
    def contact_email(self, obj):
        lines = []
        for addr in (obj.email, obj.email_2, obj.email_3):
            if addr:
                lines.append(
                    format_html(
                        '<a href="mailto:{}" style="color: #417690; text-decoration: none;">✉️ {}</a>',
                        addr,
                        addr,
                    )
                )
        return format_html('<br>'.join(lines)) if lines else '-'
    contact_email.short_description = "Email"
    
    def social_links(self, obj):
        links = []
        if obj.instagram:
            links.append(format_html('<a href="{}" target="_blank" style="color: #E4405F; margin-right: 8px;">📷 Instagram</a>', obj.instagram))
        if obj.facebook:
            links.append(format_html('<a href="{}" target="_blank" style="color: #1877F2; margin-right: 8px;">👥 Facebook</a>', obj.facebook))
        if obj.youtube:
            links.append(format_html('<a href="{}" target="_blank" style="color: #FF0000; margin-right: 8px;">▶️ YouTube</a>', obj.youtube))
        if obj.linkedn:
            links.append(format_html('<a href="{}" target="_blank" style="color: #0A66C2; margin-right: 8px;">💼 LinkedIn</a>', obj.linkedn))
        if obj.tiktok:
            links.append(format_html('<a href="{}" target="_blank" style="color: #000000; margin-right: 8px;">🎵 TikTok</a>', obj.tiktok))
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
class TeamAdmin(AdminImageCompressMixin, admin.ModelAdmin):
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
class BlogPostAdmin(admin.ModelAdmin):
    form = BlogPostAdminForm
    inlines = [BlogPostImageInline]
    list_display = (
        'cover_preview', 'name_az', 'slug', 'date',
        'is_active', 'on_top', 'on_main_page', 'created_at',
    )
    list_display_links = ('cover_preview', 'name_az')
    list_editable = ('is_active', 'on_top', 'on_main_page')
    list_filter = ('is_active', 'on_top', 'on_main_page', 'date', 'created_at')
    search_fields = (
        'name_az', 'name_en', 'name_ru', 'slug',
        'description_az', 'description_en', 'description_ru',
    )
    readonly_fields = ('slug', 'created_at')
    ordering = ('-on_top', '-date', '-id')
    list_per_page = 25
    fieldsets = (
        (None, {
            'fields': ('slug', 'date', 'is_active', 'on_top', 'on_main_page'),
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
        first = obj.images.order_by('order', 'id').first()
        if first and first.image:
            return format_html(
                '<img src="{}" style="height:48px;width:72px;object-fit:cover;border-radius:4px;">',
                first.image.url,
            )
        return '-'


@admin.register(Review)
class ReviewAdmin(AdminImageCompressMixin, admin.ModelAdmin):
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
class TestAdmin(AdminImageCompressMixin, admin.ModelAdmin):
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
        ('Azərbaycan', {'fields': ('title_az', 'description_az')}),
        ('English', {'fields': ('title_en', 'description_en')}),
        ('Русский', {'fields': ('title_ru', 'description_ru')}),
        ('Other', {'fields': ('is_active', 'created_at')}),
    )

    @admin.display(description='Title')
    def list_title(self, obj):
        return obj.display_title() or '—'


@admin.register(Question)
class QuestionAdmin(AdminImageCompressMixin, admin.ModelAdmin):
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
class UserResultAdmin(AdminImageCompressMixin, admin.ModelAdmin):
    list_display = ('id', 'test', 'first_name', 'last_name', 'number', 'email', 'score', 'level', 'created_at')
    list_filter = ('test', 'level', 'created_at')
    search_fields = ('first_name', 'last_name', 'number', 'email', 'level')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    list_per_page = 25

@admin.register(Tagline)
class TaglineAdmin(AdminImageCompressMixin, admin.ModelAdmin):
    list_display = (
        'id',
        'text_preview_az',
        'text_preview_en',
        'text_preview_ru',
    )
    list_display_links = ('text_preview_az',)
    search_fields = (
        'heading_small_az', 'heading_main_az', 'body_az',
        'heading_small_en', 'heading_main_en', 'body_en',
        'heading_small_ru', 'heading_main_ru', 'body_ru',
    )
    list_per_page = 25
    
    fieldsets = (
        ('Azerbaijani', {
            'fields': ('heading_small_az', 'heading_main_az', 'body_az')
        }),
        ('English', {
            'fields': ('heading_small_en', 'heading_main_en', 'body_en')
        }),
        ('Русский', {
            'fields': ('heading_small_ru', 'heading_main_ru', 'body_ru')
        }),
    )
    
    def text_preview_az(self, obj):
        url = reverse('admin:projects_tagline_change', args=[obj.pk])
        base = obj.heading_main_az or obj.heading_small_az or obj.body_az or ''
        preview = base[:100] + '...' if len(base) > 100 else base
        return format_html(
            '<a href="{}" style="color: #417690; text-decoration: none; font-weight: 600; font-size: 14px;">🔗 {}</a>',
            url,
            preview or 'Tagline (AZ)',
        )
    text_preview_az.short_description = "Hero (AZ)"
    text_preview_az.admin_order_field = 'heading_main_az'
    
    def text_preview_en(self, obj):
        base = obj.heading_main_en or obj.heading_small_en or obj.body_en or ''
        preview = base[:100] + '...' if len(base) > 100 else base
        return preview or "-"
    text_preview_en.short_description = "Hero (EN)"
    text_preview_en.admin_order_field = 'heading_main_en'
    
    def text_preview_ru(self, obj):
        base = obj.heading_main_ru or obj.heading_small_ru or obj.body_ru or ''
        preview = base[:100] + '...' if len(base) > 100 else base
        return preview or "-"
    text_preview_ru.short_description = "Hero (RU)"
    text_preview_ru.admin_order_field = 'heading_main_ru'


@admin.register(ContactInquiry)
class ContactInquiryAdmin(AdminImageCompressMixin, admin.ModelAdmin):
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
                '<a href="tel:{}" style="color: #666; text-decoration: none; font-size: 13px;">📱 {}</a>',
                obj.mobile_number,
                obj.mobile_number[:30] + ('...' if len(obj.mobile_number) > 30 else '')
            )
        else:
            mobile_html = format_html(
                '<span style="color: #666; font-size: 13px;">📱 No mobile number</span>'
            )
        
        return format_html(
            '<div style="padding: 8px 0;">'
            '<a href="{}" style="color: #417690; text-decoration: none; font-weight: 600; '
            'font-size: 15px; display: block; line-height: 1.4; margin-bottom: 4px;">'
            '👤 {}</a>'
            '<a href="mailto:{}" style="color: #666; text-decoration: none; font-size: 13px;">'
            '✉️ {}</a><br>'
            '{}'
            '</div>',
            detail_url,
            name,
            email,
            email,
            email[:30] + ('...' if len(email) > 30 else ''),
            mobile_html
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
                '<span style="background: #28a745; color: white; padding: 4px 10px; '
                'border-radius: 12px; font-size: 11px; font-weight: bold;">✓ Read</span>'
            )
        return format_html(
            '<span style="background: #dc3545; color: white; padding: 4px 10px; '
            'border-radius: 12px; font-size: 11px; font-weight: bold;">✗ Unread</span>'
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
        "Contact": 30,
        "Tagline": 50,

        # Team / reviews / blog
        "Team": 100,
        "Review": 110,
        "BlogPost": 115,

        # Service categories
        "ServiceCategory": 200,
        "CoursePricePackage": 201,
        "AbroadModel": 220,
        "StudyAbroadSection": 222,
        "University": 225,
        "Instructor": 230,

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
