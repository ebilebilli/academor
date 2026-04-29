from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import Http404, HttpResponsePermanentRedirect, JsonResponse
from django.urls import reverse
from django.utils.translation import gettext as _

from projects.models import AbroadModel, Team
from projects.forms.forms_v1 import ReviewForm
from projects.utils.queries import (
    get_language_from_request, get_home_page_data,
    get_courses_list_data,
    get_background_image,
    get_about, serialize_about, get_serialized_partners,
    get_contact, serialize_contact,
    get_project_categories, serialize_project_category,
    serialize_project_category_detail,
    get_active_project_category_by_slug,
    get_team_members, serialize_team_member,
    get_reviews, serialize_review,
    get_serialized_service_highlights,
    get_abroad_page_data,
    get_abroad_detail_view_context,
    get_serialized_site_faq_entries,
)


class HomePageView(View):
    template_name = 'index.html'
    
    def get(self, request):
        lang = get_language_from_request(request)
        context = get_home_page_data(request, lang)
        context['language'] = lang
        return render(request, self.template_name, context)


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
        categories = get_project_categories(lang)
        context = {
            'course': course,
            'categories': [serialize_project_category(c, lang) for c in categories],
            'language': lang,
            'background_image': get_background_image('courses'),
            'page_title': f'{course["name"]} | Academor',
        }
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
            'partners': get_serialized_partners(lang=lang, is_active=is_active),
            'contact': serialize_contact(contact, lang) if contact else None,
            'categories': serialized_categories,
            'service_highlights': get_serialized_service_highlights(lang=lang, is_active=True),
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
        form = AppealContactForm()
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
        form = AppealContactForm(request.POST)
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
            'team': [serialize_team_member(m) for m in members],
            'categories': [serialize_project_category(c, lang) for c in categories],
            'language': lang,
            'background_image': get_background_image('about'),
        }
        return render(request, self.template_name, context)


class TeamDetailPageView(View):
    template_name = 'team-detail.html'

    def get(self, request, pk: int):
        lang = get_language_from_request(request)
        try:
            member = Team.objects.get(pk=pk)
        except Team.DoesNotExist:
            raise Http404(_("Team member not found"))

        categories = get_project_categories(lang)
        member_data = serialize_team_member(member)
        contact = get_contact(lang)
        context = {
            'member': member_data,
            'categories': [serialize_project_category(c, lang) for c in categories],
            'contact': serialize_contact(contact, lang) if contact else None,
            'language': lang,
            'background_image': get_background_image('about'),
            'page_title': f'{member_data["name"]} | Academor',
        }
        return render(request, self.template_name, context)


class ReviewsPageView(View):
    template_name = 'testimonial.html'

    def _build_context(self, request, form=None):
        lang = get_language_from_request(request)
        reviews = get_reviews()
        categories = get_project_categories(lang)
        return {
            'reviews': [serialize_review(r) for r in reviews],
            'form': form if form is not None else ReviewForm(),
            'categories': [serialize_project_category(c, lang) for c in categories],
            'language': lang,
            'background_image': get_background_image('about'),
        }

    def get(self, request):
        return render(request, self.template_name, self._build_context(request))

    def post(self, request):
        form = ReviewForm(request.POST)
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
                return redirect('projects:reviews-page')
            except Exception:
                messages.error(request, _('Something went wrong. Please try again.'))
                return redirect('projects:reviews-page')
        messages.error(request, _('Please correct the errors in the form.'))
        return render(request, self.template_name, self._build_context(request, form=form))


