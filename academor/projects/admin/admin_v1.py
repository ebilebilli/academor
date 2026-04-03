from django.contrib import admin
from django.db.models import Q
from django.db import models
from django.utils.html import format_html
from django.urls import reverse
from django import forms
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet
from ckeditor.widgets import CKEditorWidget

from projects.models import *


# Media
@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
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
        'is_vacany_page_background_image',
        'is_service_page_background_image',
        'created_at',
    )
    readonly_fields = ('created_at', 'media_preview_detailed')

    fieldsets = (
        ('Media file', {
            'fields': ('image', 'media_preview_detailed')
        }),
        ('Background assignments', {
            'fields': (
                'is_home_page_background_image',
                'is_about_page_background_image',
                'is_contact_page_background_image',
                'is_project_page_background_image',
                'is_courses_page_background_image',
                'is_tests_page_background_image',
                'is_vacany_page_background_image',
                'is_service_page_background_image',
            ),
        }),
    )

    ordering = ('-created_at',)
    list_per_page = 25

    class Media:
        js = ('assets/js/admin_image_compress.js',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(
            Q(is_home_page_background_image=True)
            | Q(is_about_page_background_image=True)
            | Q(is_contact_page_background_image=True)
            | Q(is_project_page_background_image=True)
            | Q(is_courses_page_background_image=True)
            | Q(is_tests_page_background_image=True)
            | Q(is_vacany_page_background_image=True)
            | Q(is_service_page_background_image=True)
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
        if obj.is_vacany_page_background_image:
            flags.append("💼 Vacancies page")
        if obj.is_service_page_background_image:
            flags.append("🛠️ Services page")
        return " | ".join(flags) if flags else "-"
    background_flags.short_description = "Background"



class MediaInlineBase(admin.TabularInline):
    model = Media
    extra = 1
    readonly_fields = ('created_at', 'thumbnail_preview')
    fields = ('image', 'video', 'thumbnail_preview', 'created_at')
    verbose_name = "Media"
    verbose_name_plural = "Media"
    
    class Media:
        js = ('assets/js/admin_image_compress.js',)
    
    def thumbnail_preview(self, obj):
        if obj and obj.image:
            return format_html(
                '<img src="{}" style="max-width: 60px; max-height: 60px; border-radius: 4px;" />',
                obj.image.url
            )
        return "-"
    thumbnail_preview.short_description = "Preview"


class MediaInlineProject(MediaInlineBase):
    fk_name = 'project'
    fields = ('image', 'thumbnail_preview', 'created_at')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('project')


class MediaInlinePartner(MediaInlineBase):
    fields = ('image', 'thumbnail_preview', 'created_at')


class MediaInlineAbout(MediaInlineBase):
    fields = ('image', 'video', 'thumbnail_preview', 'created_at')
    max_num = 12
    extra = 1
    
    def get_formset(self, request, obj=None, **kwargs):
        from django.forms import BaseInlineFormSet
        from django.core.exceptions import ValidationError
        
        class MediaAboutFormSet(BaseInlineFormSet):
            def clean(self):
                super().clean()
                video_count = 0
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
                            if form.cleaned_data.get('video'):
                                video_count += 1
                            if form.cleaned_data.get('image'):
                                if not form.instance.pk or (form.instance.pk and form.cleaned_data.get('image') != form.instance.image):
                                    image_count += 1
                
                if video_count > 1:
                    raise ValidationError('Only one video may be uploaded. Please add a video to a single media row only.')
                
                total_images = existing_images - deleted_images + image_count
                
                if total_images > 12:
                    raise ValidationError(
                        'About page allows at most 12 images. Currently: {} existing, {} removed, {} new — total would be {}.'
                        .format(existing_images, deleted_images, image_count, total_images)
                    )
        
        kwargs['formset'] = MediaAboutFormSet
        return super().get_formset(request, obj, **kwargs)


class MediaInlineVacancy(MediaInlineBase):
    max_num = 1
    fields = ('image', 'thumbnail_preview', 'created_at')


class MediaInlineService(MediaInlineBase):
    fk_name = 'service'
    max_num = 1
    fields = ('image', 'thumbnail_preview', 'created_at')
    extra = 0

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('service')


class MediaInlineCategory(MediaInlineBase):
    fk_name = 'category'
    max_num = 1
    fields = ('image', 'thumbnail_preview', 'created_at')
    extra = 0

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('category')


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'category_thumb', 'name_link', 'name_en', 'name_ru', 'projects_count')
    list_display_links = ('id',)
    search_fields = ('name_az', 'name_en', 'name_ru')
    list_per_page = 25
    inlines = [MediaInlineCategory]

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

    def name_link(self, obj):
        url = reverse('admin:projects_servicecategory_change', args=[obj.pk])
        name = obj.name_az or 'Category'
        return format_html('<a href="{}" style="color: #417690; text-decoration: none; font-weight: 600; font-size: 14px;">🔗 {}</a>', url, name)
    name_link.short_description = "Name (AZ)"
    name_link.admin_order_field = 'name_az'
    
    def projects_count(self, obj):
        count = obj.services.count()
        if count > 0:
            url = reverse('admin:projects_service_changelist') + f'?category__id__exact={obj.id}'
            return format_html('<a href="{}" style="color: #28a745; text-decoration: none;">📁 {} projects</a>', url, count)
        return "0 projects"
    projects_count.short_description = "Projects"

# Project 
class ServiceAdminForm(forms.ModelForm):
    """Service (project) admin form."""

    class Meta:
        model = Service
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()

        category = cleaned_data.get('category')
        on_main_page = cleaned_data.get('on_main_page')
        speacial_project = cleaned_data.get('speacial_project')

        errors = {}

        if speacial_project:
            if not on_main_page:
                errors['on_main_page'] = (
                    '⚠️ When “Featured project” is enabled, “Show on home page” must also be checked. '
                    'Featured projects are shown on the home page.'
                )

            qs = Service.objects.filter(speacial_project=True, on_main_page=True)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.count() >= 9:
                errors['speacial_project'] = (
                    '⚠️ At most 9 featured projects are allowed. '
                    'Uncheck “Featured project” on an existing project before adding another.'
                )

        if on_main_page:
            if category is None:
                errors['category'] = 'Select a category to show this project on the home page.'
            else:
                qs = Service.objects.filter(on_main_page=True, category=category)
                if self.instance and self.instance.pk:
                    qs = qs.exclude(pk=self.instance.pk)

                if qs.count() >= 9:
                    errors['on_main_page'] = (
                        f'⚠️ At most 9 home-page projects are allowed in category “{category}”. '
                        'Uncheck “Show on home page” on an existing project in this category first.'
                    )

        if errors:
            raise ValidationError(errors)

        return cleaned_data


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    form = ServiceAdminForm
    list_display = (
        'id',
        'name_link',
        'category_display',
        'status_badges',
        'project_date',
    )
    list_display_links = ('id',)
    list_filter = (
        'category',
        'is_completed',
        'is_active',
        'on_main_page',
        'speacial_project',
        'project_date',
    )
    search_fields = ('name_az', 'name_en', 'name_ru', 'description_az', 'description_en', 'description_ru')
    exclude = ('slug',)
    inlines = [MediaInlineProject]
    readonly_fields = ('created_at',)
    ordering = ('-project_date', '-created_at')
    list_per_page = 25
    
    fieldsets = (
        ('Main details', {
            'fields': ('category', 'url')
        }),
        ('Azerbaijani', {
            'fields': ('name_az', 'description_az')
        }),
        ('English', {
            'fields': ('name_en', 'description_en')
        }),
        ('Русский', {
            'fields': ('name_ru', 'description_ru')
        }),
        ('Status', {
            'fields': ('is_completed', 'is_active', 'on_main_page', 'speacial_project')
        }),
        ('Date', {
            'fields': ('project_date', 'created_at')
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('category')
    
    def response_delete(self, request, obj_display, obj_id):
        try:
            return super().response_delete(request, obj_display, obj_id)
        except Exception as e:
            from django.contrib import messages
            from django.http import HttpResponseRedirect
            from django.urls import reverse
            
            try:
                from projects.models import Media
                Media.objects.filter(project_id=obj_id).delete()
            except Exception:
                pass
            
            messages.success(request, f'"{obj_display}" was deleted successfully.')
            return HttpResponseRedirect(reverse('admin:projects_service_changelist'))
    
    def name_link(self, obj):
        url = reverse('admin:projects_service_change', args=[obj.pk])
        return format_html('<a href="{}" style="color: #417690; text-decoration: none; font-weight: 600; font-size: 14px;">🔗 {}</a>', url, obj.name_az)
    name_link.short_description = "Project name"
    name_link.admin_order_field = 'name_az'
    
    def category_display(self, obj):
        if obj.category:
            return obj.category.name_az or '-'
        return '-'
    category_display.short_description = "Category"
    category_display.admin_order_field = 'category'
    
    def status_badges(self, obj):
        badges = []
        if obj.is_active:
            badges.append('<span style="background: #28a745; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">✓ Active</span>')
        else:
            badges.append('<span style="background: #dc3545; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">✗ Inactive</span>')
        
        if obj.is_completed:
            badges.append('<span style="background: #17a2b8; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">✓ Completed</span>')
        else:
            badges.append('<span style="background: #ffc107; color: #333; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">🔄 In progress</span>')
        
        if obj.on_main_page:
            badges.append('<span style="background: #6f42c1; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">🏠 On home page</span>')
        
        if obj.speacial_project:
            badges.append('<span style="background: #e83e8c; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">⭐ Featured</span>')
        
        return format_html(' '.join(badges))
    status_badges.short_description = "Status"

@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
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
class AboutAdmin(admin.ModelAdmin):
    list_display = ('id', 'title_link', 'second_title_az', 'media_count', 'updated_info')
    list_display_links = ('id',)
    search_fields = ('main_title_az', 'main_title_en', 'main_title_ru', 'second_title_az', 'second_title_en', 'second_title_ru', 'description_az', 'description_en', 'description_ru')
    inlines = [MediaInlineAbout]
    list_per_page = 25
    
    fieldsets = (
        ('Main heading', {
            'fields': ('main_title_az', 'main_title_en', 'main_title_ru')
        }),
        ('Subtitle', {
            'fields': ('second_title_az', 'second_title_en', 'second_title_ru')
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
    )
    
    def title_link(self, obj):
        url = reverse('admin:projects_about_change', args=[obj.pk])
        title = obj.main_title_az or 'About'
        return format_html('<a href="{}" style="color: #417690; text-decoration: none; font-weight: 600; font-size: 14px;">🔗 {}</a>', url, title)
    title_link.short_description = "Main heading"
    title_link.admin_order_field = 'main_title_az'
    
    def media_count(self, obj):
        count = obj.medias.count()
        if count > 0:
            return format_html('<span style="background: #007bff; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px;">📷 {} images</span>', count)
        return "📷 0 images"
    media_count.short_description = "Media"
    
    def updated_info(self, obj):
        if hasattr(obj, 'updated_at'):
            return obj.updated_at.strftime('%d.%m.%Y %H:%M') if obj.updated_at else "-"
        return "-"
    updated_info.short_description = "Last updated"


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('id', 'title_link', 'media_count', 'active_status', 'created_at')
    list_display_links = ('id',)
    list_filter = ('is_active', 'created_at')
    search_fields = ('title_az', 'title_en', 'title_ru', 'description_az', 'description_en', 'description_ru')
    inlines = [MediaInlineService]
    list_per_page = 25

    fieldsets = (
        ('Azerbaijani', {
            'fields': ('title_az', 'description_az')
        }),
        ('English', {
            'fields': ('title_en', 'description_en')
        }),
        ('Русский', {
            'fields': ('title_ru', 'description_ru')
        }),
        ('Link', {
            'fields': ('url',),
            'description': 'The “Learn more” button links to this URL. Leave blank to hide the button.'
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )

    def title_link(self, obj):
        url = reverse('admin:projects_program_change', args=[obj.pk])
        title = obj.title_az or 'Service'
        return format_html('<a href="{}" style="color: #417690; text-decoration: none; font-weight: 600; font-size: 14px;">🔗 {}</a>', url, title)
    title_link.short_description = "Name (AZ)"
    title_link.admin_order_field = 'title_az'

    def media_count(self, obj):
        count = obj.medias.count()
        if count > 0:
            return format_html('<span style="background: #007bff; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px;">📷 {} images</span>', count)
        return "📷 0 images"
    media_count.short_description = "Media"

    def active_status(self, obj):
        if obj.is_active:
            return format_html('<span style="background: #28a745; color: white; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: bold;">✓ Active</span>')
        return format_html('<span style="background: #dc3545; color: white; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: bold;">✗ Inactive</span>')
    active_status.short_description = "Status"


# Contact 
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
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
        'email',
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
            'fields': ('email',)
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
        if obj.email:
            return format_html('<a href="mailto:{}" style="color: #417690; text-decoration: none;">✉️ {}</a>', obj.email, obj.email)
        return "-"
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
            'description': CKEditorWidget(),
        }


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    form = TeamAdminForm
    list_display = ('id', 'name', 'role')
    search_fields = ('name', 'role', 'description', 'instagram', 'facebook', 'linkedin', 'tiktok', 'youtube')
    list_per_page = 25


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'message')
    list_editable = ('is_active',)
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    list_per_page = 25


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


class OptionInline(admin.TabularInline):
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
class TestAdmin(admin.ModelAdmin):
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
class QuestionAdmin(admin.ModelAdmin):
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
class UserResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'test', 'first_name', 'last_name', 'number', 'email', 'score', 'level', 'created_at')
    list_filter = ('test', 'level', 'created_at')
    search_fields = ('first_name', 'last_name', 'number', 'email', 'level')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    list_per_page = 25

@admin.register(CareerOpening)
class CareerOpeningAdmin(admin.ModelAdmin):
    inlines = [MediaInlineVacancy]
    list_display = (
        'id',
        'title_link',
        'vacancy_status',
        'appeals_count',
        'created_at',
    )
    list_display_links = ('id',)
    list_filter = ('is_active', 'created_at')
    search_fields = ('title_az', 'title_en', 'title_ru', 'description_az', 'description_en', 'description_ru')
    exclude = ('slug',)
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    list_per_page = 25
    
    fieldsets = (
        ('Azerbaijani', {
            'fields': ('title_az', 'description_az')
        }),
        ('English', {
            'fields': ('title_en', 'description_en')
        }),
        ('Русский', {
            'fields': ('title_ru', 'description_ru')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Date', {
            'fields': ('created_at',)
        }),
    )
    
    def title_link(self, obj):
        url = reverse('admin:projects_careeropening_change', args=[obj.pk])
        return format_html('<a href="{}" style="color: #417690; text-decoration: none; font-weight: 600; font-size: 14px;">🔗 {}</a>', url, obj.title_az)
    title_link.short_description = "Vacancy title"
    title_link.admin_order_field = 'title_az'
    
    def vacancy_status(self, obj):
        if obj.is_active:
            return format_html('<span style="background: #28a745; color: white; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: bold;">✓ Active</span>')
        return format_html('<span style="background: #dc3545; color: white; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: bold;">✗ Inactive</span>')
    vacancy_status.short_description = "Status"
    
    def appeals_count(self, obj):
        count = obj.appeal_set.count()
        read_count = obj.appeal_set.filter(is_read=True).count()
        unread_count = count - read_count
        
        if count > 0:
            url = reverse('admin:projects_jobapplication_changelist') + f'?vacancy__id__exact={obj.id}'
            badge_html = f'<a href="{url}" style="text-decoration: none;">'
            if unread_count > 0:
                badge_html += f'<span style="background: #dc3545; color: white; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: bold;">📄 {count} CV ({unread_count} unread)</span>'
            else:
                badge_html += f'<span style="background: #28a745; color: white; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: bold;">📄 {count} CV (all read)</span>'
            badge_html += '</a>'
            return format_html(badge_html)
        return format_html('<span style="color: #6c757d;">📄 0 CV</span>')
    appeals_count.short_description = "Applications"

@admin.register(Tagline)
class TaglineAdmin(admin.ModelAdmin):
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

    def has_add_permission(self, request):
        if Tagline.objects.exists():
            return False
        return super().has_add_permission(request)

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = (
        'candidate_info',
        'vacancy_info',
        'contact_info',
        'cv_download',
        'is_read',
        'read_status_badge',
        'created_at_formatted',
    )

    list_display_links = None
    list_editable = ('is_read',)
    list_filter = ('is_read', 'created_at', 'vacancy')
    readonly_fields = ('created_at', 'cv_preview')
    search_fields = (
        'full_name',
        'email',
        'phone_number',
        'vacancy__title_az',
        'vacancy__title_en',
        'vacancy__title_ru',
    )
    ordering = ('-created_at',)
    list_per_page = 25
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Vacancy', {
            'fields': ('vacancy',)
        }),
        ('Candidate', {
            'fields': ('full_name', 'email', 'phone_number', 'info')
        }),
        ('CV file', {
            'fields': ('cv', 'cv_preview')
        }),
        ('Status', {
            'fields': ('is_read',)
        }),
        ('Date', {
            'fields': ('created_at',)
        }),
    )

    def candidate_info(self, obj):
        detail_url = reverse('admin:projects_jobapplication_change', args=[obj.pk])
        name = obj.full_name or "No name"
        
        return format_html(
            '<div style="padding: 8px 0;">'
            '<a href="{}" style="color: #417690; text-decoration: none; font-weight: 600; '
            'font-size: 15px; display: block; line-height: 1.4;">'
            '👤 {}</a>'
            '</div>',
            detail_url,
            name
        )
    candidate_info.short_description = "Candidate"
    candidate_info.admin_order_field = 'full_name'

    def vacancy_info(self, obj):
        if obj.vacancy:
            vacancy_url = reverse('admin:projects_careeropening_change', args=[obj.vacancy.pk])
            detail_url = reverse('admin:projects_jobapplication_change', args=[obj.pk])
            
            return format_html(
                '<div style="padding: 8px 0;">'
                '<a href="{}" style="color: #417690; text-decoration: none; font-weight: 500; '
                'font-size: 14px; display: block; margin-bottom: 4px; line-height: 1.4;">'
                '💼 {}</a>'
                '<a href="{}" style="color: #6c757d; text-decoration: none; font-size: 11px; '
                'opacity: 0.8;">→ View vacancy</a>'
                '</div>',
                detail_url,
                obj.vacancy.title_az[:50] + ('...' if len(obj.vacancy.title_az) > 50 else ''),
                vacancy_url
            )
        return format_html('<span style="color: #999; font-size: 13px;">No vacancy</span>')
    vacancy_info.short_description = "Vacancy"
    vacancy_info.admin_order_field = 'vacancy__title_az'

    def contact_info(self, obj):
        contact_items = []
        
        if obj.email:
            contact_items.append(
                format_html(
                    '<div style="margin-bottom: 4px;">'
                    '<span style="color: #666; font-size: 12px;">✉️</span> '
                    '<a href="mailto:{}" style="color: #417690; text-decoration: none; '
                    'font-size: 13px;">{}</a>'
                    '</div>',
                    obj.email,
                    obj.email[:30] + ('...' if len(obj.email) > 30 else '')
                )
            )
        
        if obj.phone_number:
            contact_items.append(
                format_html(
                    '<div>'
                    '<span style="color: #666; font-size: 12px;">📞</span> '
                    '<span style="color: #333; font-size: 13px;">{}</span>'
                    '</div>',
                    obj.phone_number
                )
            )
        
        if not contact_items:
            return format_html('<span style="color: #999; font-size: 12px;">No contact info</span>')
        
        return format_html(
            '<div style="padding: 8px 0; line-height: 1.6;">{}</div>',
            format_html(''.join(contact_items))
        )
    contact_info.short_description = "Contact"

    def cv_download(self, obj):
        detail_url = reverse('admin:projects_jobapplication_change', args=[obj.pk])
        
        if obj.cv:
            file_name = obj.cv.name.split('/')[-1]
            file_size = obj.cv.size if hasattr(obj.cv, 'size') else None
            size_text = f"{round(file_size / 1024, 1)} KB" if isinstance(file_size, (int, float)) else "N/A"
            
            return format_html(
                '<div style="padding: 8px 0;">'
                '<a href="{}" target="_blank" '
                'style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); '
                'color: white; padding: 8px 14px; border-radius: 6px; text-decoration: none; '
                'font-size: 12px; font-weight: 600; display: inline-block; margin-bottom: 4px; '
                'box-shadow: 0 2px 4px rgba(0,0,0,0.1); transition: all 0.2s;">'
                '📎 Download CV</a>'
                '<div style="color: #666; font-size: 11px; margin-top: 4px;">'
                '📄 {} <span style="opacity: 0.7;">({})</span>'
                '</div>'
                '</div>',
                obj.cv.url,
                file_name[:25] + ('...' if len(file_name) > 25 else ''),
                size_text
            )
        
        return format_html(
            '<div style="padding: 8px 0;">'
            '<a href="{}" style="color: #999; text-decoration: none; font-size: 12px;">'
            'No CV file</a>'
            '</div>',
            detail_url
        )
    cv_download.short_description = "CV"

    def read_status_badge(self, obj):
        if obj.is_read:
            return format_html(
                '<div style="padding: 8px 0;">'
                '<span style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); '
                'color: white; padding: 6px 12px; border-radius: 8px; font-size: 11px; '
                'font-weight: 600; display: inline-block; box-shadow: 0 2px 4px rgba(40,167,69,0.3);">'
                '✓ Read</span>'
                '</div>'
            )
        return format_html(
            '<div style="padding: 8px 0;">'
            '<span style="background: linear-gradient(135deg, #dc3545 0%, #c82333 100%); '
            'color: white; padding: 6px 12px; border-radius: 8px; font-size: 11px; '
            'font-weight: 600; display: inline-block; box-shadow: 0 2px 4px rgba(220,53,69,0.3);">'
            '🔴 Unread</span>'
            '</div>'
        )
    read_status_badge.short_description = "Status"
    read_status_badge.admin_order_field = 'is_read'

    def created_at_formatted(self, obj):
        if obj.created_at:
            date_str = obj.created_at.strftime('%d.%m.%Y')
            time_str = obj.created_at.strftime('%H:%M')
            return format_html(
                '<div style="padding: 8px 0;">'
                '<div style="color: #333; font-size: 13px; font-weight: 500; margin-bottom: 2px;">{}</div>'
                '<div style="color: #999; font-size: 11px;">{}</div>'
                '</div>',
                date_str,
                time_str
            )
        return "-"
    created_at_formatted.short_description = "Date"
    created_at_formatted.admin_order_field = 'created_at'

    def cv_preview(self, obj):
        if obj.cv:
            file_name = obj.cv.name.split('/')[-1]
            file_size = obj.cv.size if hasattr(obj.cv, 'size') else None

            return format_html(
                '<div style="padding:12px;background:#e3f2fd;border-radius:4px;'
                'border-left:3px solid #2196f3;">'
                '<span style="color:#1976d2;font-weight:500;">📄 {}</span> '
                '<span style="color:#666;font-size:12px;">({} KB)</span>'
                '<a href="{}" target="_blank" '
                'style="color:#2196f3;text-decoration:none;margin-left:8px;font-weight:500;">'
                '📥 Download</a>'
                '</div>',
                file_name,
                round(file_size / 1024, 2) if isinstance(file_size, (int, float)) else 'N/A',
                obj.cv.url
            )
        return "-"

    cv_preview.short_description = "CV preview"


@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
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
        'subject',
        'info',
    )
    ordering = ('-created_at',)
    list_per_page = 25
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Sender', {
            'fields': ('full_name', 'email')
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
        
        return format_html(
            '<div style="padding: 8px 0;">'
            '<a href="{}" style="color: #417690; text-decoration: none; font-weight: 600; '
            'font-size: 15px; display: block; line-height: 1.4; margin-bottom: 4px;">'
            '👤 {}</a>'
            '<a href="mailto:{}" style="color: #666; text-decoration: none; font-size: 13px;">'
            '✉️ {}</a>'
            '</div>',
            detail_url,
            name,
            email,
            email[:30] + ('...' if len(email) > 30 else '')
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

@admin.register(AcademyStatistic)
class AcademyStatisticAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'value_one',
        'value_two',
        'value_three',
    )
    list_display_links = ('id',)
    fieldsets = (
        ('Statistics', {
            'fields': (
                'value_one',
                'value_two',
                'value_three',
            ),
        }),
    )


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
        "Contact": 30,
        "AcademyStatistic": 40,
        "Tagline": 50,

        # Team / reviews
        "Team": 100,
        "Review": 110,

        # Services / programs
        "ServiceCategory": 200,
        "Service": 210,
        "Program": 220,
        "Instructor": 230,

        # Careers / inbound
        "CareerOpening": 300,
        "JobApplication": 310,
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
