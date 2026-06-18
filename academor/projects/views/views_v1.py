from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import Http404, HttpResponsePermanentRedirect, JsonResponse
from django.urls import reverse
from django.utils.translation import gettext as _

from projects.models import AbroadModel, Team, BlogPost
from projects.forms.forms_v1 import ReviewForm
from projects.utils.seo_text import meta_plain_excerpt
from projects.utils.canonical import canonical_url_for_request
from projects.utils.seo_meta import (
    blog_detail_seo,
    course_detail_seo,
    tag_archive_seo,
    dumps_structured_data,
    organization_json_ld,
    website_json_ld,
)
from projects.seo_page_defaults import get_page_seo_defaults
from projects.utils.queries import (
    get_language_from_request, get_home_page_data,
    get_courses_list_data,
    get_background_image,
    get_about, serialize_about, get_serialized_about_why_items, get_about_page_gallery_items,
    get_contact, serialize_contact,
    get_project_categories, serialize_project_category,
    serialize_project_category_detail,
    get_active_project_category_by_slug,
    get_team_members, serialize_team_member,
    get_blog_page_data,
    get_blog_detail_view_context,
    get_blog_tag_page_data,
    get_abroad_page_data,
    _fresh_abroad_advantages_context,
    get_abroad_detail_view_context,
    get_university_detail_view_context,
    apply_university_study_abroad_localized_name,
    get_serialized_site_faq_entries,
)


class HomePageView(View):
    template_name = 'index.html'

    def _home_context(self, request, lang, review_form=None, open_review_modal=False):
        context = get_home_page_data(request, lang)
        context['language'] = lang
        context['review_form'] = review_form if review_form is not None else ReviewForm(request=request)
        context['open_review_modal'] = open_review_modal
        canonical = canonical_url_for_request(request)
        context['structured_data_json'] = dumps_structured_data(
            organization_json_ld(canonical_url=canonical, lang=lang),
            website_json_ld(canonical_url=canonical),
        )
        return context

    def get(self, request):
        lang = get_language_from_request(request)
        return render(request, self.template_name, self._home_context(request, lang))

    def post(self, request):
        if not request.POST.get('review_submit'):
            return redirect('projects:home-page')
        lang = get_language_from_request(request)
        form = ReviewForm(request.POST, request=request)
        if form.is_valid():
            try:
                form.save()
                messages.success(
                    request,
                    _(
                        'Your review has been submitted successfully. '
                        'It will appear after moderation.'
                    ),
                )
            except Exception:
                messages.error(request, _('Something went wrong. Please try again.'))
            return redirect(reverse('projects:home-page') + '#reviews')
        messages.error(request, _('Please correct the errors in the form.'))
        return render(
            request,
            self.template_name,
            self._home_context(request, lang, review_form=form, open_review_modal=True),
        )


class CoursesPageView(View):
    template_name = 'courses.html'
    
    def get(self, request, category_slug=None):
        lang = get_language_from_request(request)
        if category_slug:
            request.GET = request.GET.copy()
            request.GET['slug'] = category_slug
        context = get_courses_list_data(request, lang)
        context['background_image'] = get_background_image('courses')
        context['language'] = lang
        return render(request, self.template_name, context)


class CourseDetailPageView(View):
    template_name = 'course-detail.html'

    def get(self, request, slug):
        lang = get_language_from_request(request)
        category = get_active_project_category_by_slug(slug)
        if not category:
            raise Http404(_("Category not found"))
        course = serialize_project_category_detail(category, lang)
        payment_form = None
        if course.get('has_payment'):
            from payments.catalog import default_price_package_index
            from payments.forms import CoursePaymentForm

            session_data = request.session.pop('course_payment_form_data', None)
            packages = course.get('price_packages') or []
            preferred_package_id = None
            if session_data is not None:
                data = dict(session_data)
                preferred_package_id = data.get('price_package_id')
                if not (data.get('buyer_name') or '').strip():
                    first = (data.get('buyer_first_name') or '').strip()
                    last = (data.get('buyer_last_name') or '').strip()
                    data['buyer_name'] = f'{first} {last}'.strip()
                payment_form = CoursePaymentForm(data, request=request)
                payment_form.is_valid()
            else:
                payment_form = CoursePaymentForm(request=request)

            default_package_index = default_price_package_index(
                packages,
                preferred_package_id,
            )
        else:
            default_package_index = 0

        seo_defaults = get_page_seo_defaults('course-detail', lang)
        context = {
            'course': course,
            'default_package_index': default_package_index,
            'language': lang,
            'background_image': get_background_image('courses'),
            'payment_form': payment_form,
        }
        context.update(
            course_detail_seo(
                canonical_url=canonical_url_for_request(request),
                course=course,
                default_keywords=seo_defaults.get('keywords'),
            )
        )
        return render(request, self.template_name, context)


class AboutPageView(View):
    template_name = 'about.html'
    
    def get(self, request):
        lang = get_language_from_request(request)
        is_active = request.GET.get('is_active', 'true').lower() == 'true'
        about = get_about(lang)
        contact = get_contact(lang)
        categories = get_project_categories(lang)
        serialized_categories = [
            serialize_project_category(category, lang)
            for category in categories
        ]
        context = {
            'about': serialize_about(about, lang) if about else None,
            'about_why_items': get_serialized_about_why_items(lang=lang, is_active=True),
            'about_gallery_items': get_about_page_gallery_items(lang=lang),
            'contact': serialize_contact(contact, lang) if contact else None,
            'categories': serialized_categories,
            'language': lang,
            'background_image': get_background_image('about'),
            'site_faqs': get_serialized_site_faq_entries(lang=lang, is_active=True),
        }

        return render(request, self.template_name, context)


class ServicesPageView(View):
    template_name = 'services.html'

    def get(self, request):
        lang = get_language_from_request(request)
        contact = get_contact(lang)
        categories = get_project_categories(lang)
        serialized_categories = [
            serialize_project_category(category, lang)
            for category in categories
        ]
        context = {
            'contact': serialize_contact(contact, lang) if contact else None,
            'categories': serialized_categories,
            'language': lang,
            'background_image': get_background_image('service'),
        }
        return render(request, self.template_name, context)


class AbroadPageView(View):
    template_name = 'abroad.html'

    def get(self, request):
        lang = get_language_from_request(request)
        context = get_abroad_page_data(request, lang)
        context.update(_fresh_abroad_advantages_context(lang))
        context['language'] = lang
        return render(request, self.template_name, context)


class AbroadDetailLegacyPkRedirectView(View):
    """301 from /abroad/<pk>/ (old URLs) to /abroad/<slug>/."""

    def get(self, request, pk: int):
        obj = AbroadModel.objects.filter(pk=pk, is_active=True).only('slug').first()
        if not obj or not obj.slug:
            raise Http404(_("Abroad item not found"))
        return HttpResponsePermanentRedirect(
            reverse('projects:abroad-detail', kwargs={'slug': obj.slug})
        )


class AbroadDetailPageView(View):
    template_name = 'abroad-detail.html'

    def get(self, request, slug: str):
        lang = get_language_from_request(request)
        context = get_abroad_detail_view_context(lang, slug)
        if not context:
            raise Http404(_("Abroad item not found"))
        item_data = context['abroad_item']
        excerpt = meta_plain_excerpt(item_data.get('description') or '')
        if not excerpt.strip():
            excerpt = _('Study abroad pathway: %(name)s — guidance from Academor, Baku.') % {
                'name': item_data['name'],
            }
        context['page_description'] = excerpt[:320]
        context['language'] = lang
        return render(request, self.template_name, context)


class AbroadUniversityDetailPageView(View):
    template_name = 'university-detail.html'

    def get(self, request, slug: str):
        lang = get_language_from_request(request)
        context = get_university_detail_view_context(lang, slug)
        if not context:
            raise Http404(_("University not found"))
        apply_university_study_abroad_localized_name(context['university'], lang)
        uni = context['university']
        excerpt = meta_plain_excerpt(uni.get('description') or '')
        if not excerpt.strip():
            excerpt = _('University profile: %(name)s — Academor study abroad support, Baku.') % {
                'name': uni['name'],
            }
        context['page_description'] = excerpt[:320]
        context['language'] = lang
        return render(request, self.template_name, context)


class ContactPageView(View):
    template_name = 'contact.html'
    
    def get(self, request):
        lang = get_language_from_request(request)
        contact = get_contact(lang)
        categories = get_project_categories(lang)
        serialized_categories = [
            serialize_project_category(category, lang)
            for category in categories
        ]
        from projects.forms.forms_v1 import AppealContactForm
        form = AppealContactForm(request=request)
        context = {
            'contact': serialize_contact(contact, lang) if contact else None,
            'categories': serialized_categories,
            'language': lang,
            'background_image': get_background_image('contact'),
            'form': form,
        }

        return render(request, self.template_name, context)
    
    def post(self, request):
        lang = get_language_from_request(request)
        from projects.forms.forms_v1 import AppealContactForm
        form = AppealContactForm(request.POST, request=request)
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        if form.is_valid():
            try:
                form.save()
                msg = _('Your message has been sent successfully.')
                if is_ajax:
                    return JsonResponse({'success': True, 'message': msg})
                messages.success(request, msg)
                return redirect('projects:contact-page')
            except Exception:
                err_msg = _('Something went wrong. Please try again.')
                if is_ajax:
                    return JsonResponse({'success': False, 'message': err_msg}, status=500)
                messages.error(request, err_msg)
        else:
            err_msg = _('Please correct the errors in the form.')
            if is_ajax:
                errors = {k: [str(e) for e in v] for k, v in form.errors.items()}
                return JsonResponse(
                    {'success': False, 'message': err_msg, 'errors': errors},
                    status=400,
                )
            messages.error(request, err_msg)

        contact = get_contact(lang)
        categories = get_project_categories(lang)
        serialized_categories = [
            serialize_project_category(category, lang)
            for category in categories
        ]
        context = {
            'contact': serialize_contact(contact, lang) if contact else None,
            'categories': serialized_categories,
            'language': lang,
            'background_image': get_background_image('contact'),
            'form': form,
        }
        
        return render(request, self.template_name, context)


class TeamPageView(View):
    template_name = 'team.html'

    def get(self, request):
        lang = get_language_from_request(request)
        members = get_team_members()
        categories = get_project_categories(lang)
        context = {
            'team': [serialize_team_member(m, lang=lang) for m in members],
            'categories': [serialize_project_category(c, lang) for c in categories],
            'language': lang,
            'background_image': get_background_image('about'),
        }
        return render(request, self.template_name, context)


class TeamDetailLegacyPkRedirectView(View):
    """301 from /team/<pk>/ (legacy) to /team/<slug>/."""

    def get(self, request, pk: int):
        obj = Team.objects.filter(pk=pk).only('slug').first()
        if not obj or not obj.slug:
            raise Http404(_("Team member not found"))
        return HttpResponsePermanentRedirect(
            reverse('projects:team-detail', kwargs={'slug': obj.slug})
        )


class TeamDetailPageView(View):
    template_name = 'team-detail.html'

    def get(self, request, slug: str):
        lang = get_language_from_request(request)
        member = Team.objects.filter(slug=slug).first()
        if not member:
            raise Http404(_("Team member not found"))

        categories = get_project_categories(lang)
        member_data = serialize_team_member(member, lang=lang)
        excerpt = meta_plain_excerpt(member_data.get('description') or '')
        if not excerpt.strip():
            role = (member_data.get('role') or '').strip()
            excerpt = _('%(name)s%(role_suffix)s — team profile at Academor, Baku.') % {
                'name': member_data['name'],
                'role_suffix': (f', {role}' if role else ''),
            }
        context = {
            'member': member_data,
            'categories': [serialize_project_category(c, lang) for c in categories],
            'language': lang,
            'background_image': get_background_image('about'),
            'page_title': f'{member_data["name"]} | Academor',
            'page_description': excerpt[:320],
        }
        return render(request, self.template_name, context)


class BlogPostsPartialView(View):
    """AJAX partial for blog list filtering (featured + grid HTML only)."""
    template_name = 'includes/blog_posts_partial.html'

    def get(self, request):
        lang = get_language_from_request(request)
        context = get_blog_page_data(request, lang)
        return render(request, self.template_name, context)


class BlogPageView(View):
    template_name = 'blog.html'

    def get(self, request):
        lang = get_language_from_request(request)
        context = get_blog_page_data(request, lang)
        return render(request, self.template_name, context)


class BlogTagPageView(View):
    template_name = 'blog.html'

    def get(self, request, slug: str):
        lang = get_language_from_request(request)
        context = get_blog_tag_page_data(request, lang, slug)
        if not context:
            raise Http404(_("Tag not found"))
        tag = context.get('active_tag')
        if not tag and context.get('active_tags'):
            tag = context['active_tags'][0]
        if not tag:
            raise Http404(_("Tag not found"))
        seo_defaults = get_page_seo_defaults('blog-tag-page', lang)
        section = {'az': 'Bloq', 'en': 'Blog', 'ru': 'Блог'}.get(lang, 'Bloq')
        description = seo_defaults.get('description', '')
        context.update(
            tag_archive_seo(
                canonical_url=canonical_url_for_request(request),
                tag_name=tag['name'],
                section_label=section,
                description=f'{tag["name"]}. {description}',
                default_keywords=seo_defaults.get('keywords'),
            )
        )
        return render(request, self.template_name, context)


class BlogDetailLegacyPkRedirectView(View):
    """301 from /blog/<pk>/ (legacy) to /blog/<slug>/."""

    def get(self, request, pk: int):
        obj = BlogPost.objects.filter(pk=pk).only('slug').first()
        if not obj or not obj.slug:
            raise Http404(_("Blog post not found"))
        return HttpResponsePermanentRedirect(
            reverse('projects:blog-detail', kwargs={'slug': obj.slug})
        )


class BlogDetailPageView(View):
    template_name = 'blog-detail.html'

    def get(self, request, slug: str):
        lang = get_language_from_request(request)
        context = get_blog_detail_view_context(lang, slug)
        if not context:
            raise Http404(_("Blog post not found"))

        post = context['post']
        seo_defaults = get_page_seo_defaults('blog-detail', lang)
        context.update(
            blog_detail_seo(
                canonical_url=canonical_url_for_request(request),
                post=post,
                lang=lang,
                default_keywords=seo_defaults.get('keywords'),
            )
        )
        return render(request, self.template_name, context)


