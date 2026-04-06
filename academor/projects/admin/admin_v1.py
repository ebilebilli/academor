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


class MediaInlineCategory(MediaInlineBase):
    fk_name = 'category'
    max_num = 30
    fields = ('image', 'thumbnail_preview', 'created_at')
    extra = 1

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('category')


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
class ServiceCategoryAdmin(admin.ModelAdmin):
    form = ServiceCategoryAdminForm
    list_display = ('id', 'category_thumb', 'name_link', 'name_en', 'name_ru', 'is_active', 'created_at')
    list_display_links = ('id',)
    list_filter = ('is_active', 'created_at')
    search_fields = (
        'name_az', 'name_en', 'name_ru',
        'description_az', 'description_en', 'description_ru',
    )
    list_per_page = 25
    exclude = ('slug',)
    readonly_fields = ('created_at',)
    inlines = [MediaInlineCategory]

    fieldsets = (
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
            'fields': ('is_active', 'created_at')
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


@admin.register(ServiceHighlight)
class ServiceHighlightAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title_link',
        'title_en',
        'title_ru',
        'order',
        'is_active',
        'created_at',
    )
    list_display_links = ('id',)
    list_filter = ('is_active', 'created_at')
    search_fields = (
        'title_az', 'title_en', 'title_ru',
        'description_az', 'description_en', 'description_ru',
    )
    list_editable = ('order', 'is_active')
    readonly_fields = ('created_at',)
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
            'fields': ('order', 'is_active', 'created_at')
        }),
    )

    def title_link(self, obj):
        url = reverse('admin:projects_servicehighlight_change', args=[obj.pk])
        name = obj.title_az or obj.title_en or obj.title_ru or 'Service highlight'
        return format_html(
            '<a href="{}" style="color: #417690; text-decoration: none; font-weight: 600; font-size: 14px;">🔗 {}</a>',
            url,
            name,
        )
    title_link.short_description = "Title (AZ)"
    title_link.admin_order_field = 'title_az'

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
    list_display = ('id', 'title_link', 'media_count', 'updated_info')
    list_display_links = ('id',)
    search_fields = ('description_az', 'description_en', 'description_ru')
    inlines = [MediaInlineAbout]
    list_per_page = 25

    fieldsets = (
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
    
    def updated_info(self, obj):
        if hasattr(obj, 'updated_at'):
            return obj.updated_at.strftime('%d.%m.%Y %H:%M') if obj.updated_at else "-"
        return "-"
    updated_info.short_description = "Last updated"


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
        "Tagline": 50,

        # Team / reviews
        "Team": 100,
        "Review": 110,

        # Service categories
        "ServiceCategory": 200,
        "ServiceHighlight": 210,
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
