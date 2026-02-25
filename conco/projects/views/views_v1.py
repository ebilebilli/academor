from django.views import View
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import IntegrityError
from django.http import Http404
from django.utils.translation import gettext as _

from projects.models import AppealVacancy
from projects.forms.forms_v1 import AppealForm
from projects.utils.queries import (
    get_language_from_request, get_home_page_data, get_project_list_data,
    get_project_by_slug, serialize_project, get_background_image,
    get_about, serialize_about, get_partners, serialize_partner,
    get_contact, serialize_contact, get_vacancy_list_data,
    get_vacancy_by_slug, serialize_vacancy, get_statistics,
    get_project_categories, serialize_project_category,
    get_services, serialize_service,
)


class HomePageView(View):
    template_name = 'index.html'
    
    def get(self, request):
        lang = get_language_from_request(request)
        context = get_home_page_data(request, lang)
        context['footer_image'] = get_background_image('footer')
        context['language'] = lang
        return render(request, self.template_name, context)


class ProjectPageView(View):
    template_name = 'projects.html'
    
    def get(self, request, category_slug=None):
        lang = get_language_from_request(request)
        if category_slug:
            request.GET = request.GET.copy()
            request.GET['slug'] = category_slug
        context = get_project_list_data(request, lang)
        context['background_image'] = get_background_image('project')
        context['footer_image'] = get_background_image('footer')
        context['language'] = lang
        return render(request, self.template_name, context)


class ProjectDetailPageView(View):
    template_name = 'project-details.html'
    
    def get(self, request, slug):
        lang = get_language_from_request(request)
        
        # Əvvəlcə layihə kimi yoxla
        project = get_project_by_slug(slug, lang)
        if project:
            # Bu layihədir, detalları göstər
            categories = get_project_categories(lang)
            serialized_categories = [
                serialize_project_category(category, lang)
                for category in categories
            ]
            contact = get_contact(lang)
            
            context = {
                'project': serialize_project(project, lang),
                'categories': serialized_categories,
                'contact': serialize_contact(contact, lang) if contact else None,
                'language': lang,
                'background_image': get_background_image('project'),
                'footer_image': get_background_image('footer'),
            }
            return render(request, self.template_name, context)
        
        # Əgər layihə deyilsə, kateqoriya kimi yoxla
        from projects.models import ProjectCategory
        try:
            category = ProjectCategory.objects.get(slug=slug)
            # Bu kateqoriyadır, kateqoriya səhifəsini göstər
            request.GET = request.GET.copy()
            request.GET['slug'] = slug
            context = get_project_list_data(request, lang)
            context['background_image'] = get_background_image('project')
            context['footer_image'] = get_background_image('footer')
            context['language'] = lang
            return render(request, 'projects.html', context)
        except ProjectCategory.DoesNotExist:
            raise Http404(_("Project not found"))


class AboutPageView(View):
    template_name = 'about.html'
    
    def get(self, request):
        lang = get_language_from_request(request)
        is_active = request.GET.get('is_active', 'true').lower() == 'true'
        about = get_about(lang)
        partners = get_partners(lang=lang, is_active=is_active)
        contact = get_contact(lang)
        statistics = get_statistics()
        categories = get_project_categories(lang)
        serialized_categories = [
            serialize_project_category(category, lang)
            for category in categories
        ]
        context = {
            'about': serialize_about(about, lang) if about else None,
            'partners': [serialize_partner(p, lang) for p in partners],
            'contact': serialize_contact(contact, lang) if contact else None,
            'categories': serialized_categories,
            'statistics': statistics,
            'language': lang,
            'background_image': get_background_image('about'),
            'footer_image': get_background_image('footer'),
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
        services = get_services(lang=lang, is_active=True)
        serialized_services = [serialize_service(s, lang) for s in services]
        context = {
            'contact': serialize_contact(contact, lang) if contact else None,
            'categories': serialized_categories,
            'services': serialized_services,
            'language': lang,
            'background_image': get_background_image('service'),
            'footer_image': get_background_image('footer'),
        }
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
            'footer_image': get_background_image('footer'),
            'form': form,
        }

        return render(request, self.template_name, context)
    
    def post(self, request):
        lang = get_language_from_request(request)
        from projects.forms.forms_v1 import AppealContactForm
        form = AppealContactForm(request.POST)
        
        if form.is_valid():
            try:
                appeal_contact = form.save()
                messages.success(request, _('Mesajınız uğurla göndərildi.'))
                return redirect('projects:contact-page')
            except Exception as e:
                messages.error(request, _('Xəta baş verdi. Zəhmət olmasa yenidən cəhd edin.'))
        else:
            messages.error(request, _('Formda xəta var. Zəhmət olmasa düzəldin.'))
        
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
            'footer_image': get_background_image('footer'),
            'form': form,
        }
        
        return render(request, self.template_name, context)


class VacancyPageView(View):
    template_name = 'vacancy.html'
    
    def get(self, request):
        lang = get_language_from_request(request)
        context = get_vacancy_list_data(request, lang)
        categories = get_project_categories(lang)
        context['categories'] = [
            serialize_project_category(category, lang)
            for category in categories
        ]
        context['background_image'] = get_background_image('vacancy')
        context['footer_image'] = get_background_image('footer')
        context['language'] = lang
        return render(request, self.template_name, context)


class VacancyDetailPageView(View):
    template_name = 'vacancy-details.html'
    
    def get(self, request, slug):
        lang = get_language_from_request(request)
        vacancy = get_vacancy_by_slug(slug, lang)
        if not vacancy:
            from django.http import Http404
            raise Http404(_("Vacancy not found"))
        
        form = AppealForm()
        contact = get_contact(lang)
        categories = get_project_categories(lang)
        serialized_categories = [
            serialize_project_category(category, lang)
            for category in categories
        ]
        context = {
            'vacancy': serialize_vacancy(vacancy, lang),
            'contact': serialize_contact(contact, lang) if contact else None,
            'categories': serialized_categories,
            'language': lang,
            'background_image': get_background_image('vacancy'),
            'footer_image': get_background_image('footer'),
            'form': form,
        }
        return render(request, self.template_name, context)
    
    def post(self, request, slug):
        lang = get_language_from_request(request)
        vacancy = get_vacancy_by_slug(slug, lang)
        if not vacancy:
            raise Http404(_("Vacancy not found"))
        
        form = AppealForm(request.POST, request.FILES)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            phone_number = form.cleaned_data.get('phone_number')
            situation_one = AppealVacancy.objects.filter(vacancy=vacancy, email=email).exists()
            situation_two = AppealVacancy.objects.filter(vacancy=vacancy, phone_number=phone_number).exists()
            
            if situation_one or situation_two :
                messages.error(request, _('Bu vakansiyaya müraciət artıq göndərilmişdir.'))
            else:
                try:
                    appeal = form.save(commit=False)
                    appeal.vacancy = vacancy
                    appeal.save()
                    messages.success(request, _('Müraciətiniz uğurla göndərildi.'))
                    return redirect('projects:vacancy-detail', slug=slug)
                except IntegrityError:
                    messages.error(request, _('Bu e-poçt ünvanı ilə bu vakansiyaya müraciət artıq göndərilmişdir.'))
        else:
            messages.error(request, _('Xəta baş verdi. Zəhmət olmasa yenidən cəhd edin.'))
        
        contact = get_contact(lang)
        categories = get_project_categories(lang)
        serialized_categories = [
            serialize_project_category(category, lang)
            for category in categories
        ]
        context = {
            'vacancy': serialize_vacancy(vacancy, lang),
            'contact': serialize_contact(contact, lang) if contact else None,
            'categories': serialized_categories,
            'language': lang,
            'background_image': get_background_image('vacancy'),
            'footer_image': get_background_image('footer'),
            'form': form,
        }
        return render(request, self.template_name, context)


