from django.db.models import Q, Prefetch
from django.utils import translation
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# from django.conf import settings

from projects.models import *
from projects.utils.cache_utils import cached_query, get_query_cache_key, cached_page_data
from django.core.cache import cache


def get_language_from_request(request):
    lang = request.GET.get('lang', '').lower() or request.GET.get('language', '').lower()
    if lang in ['az', 'en', 'ru']:
        request.session['django_language'] = lang
        request.session['language'] = lang 
        request.session.modified = True
        translation.activate(lang)
        return lang
    
    lang = request.session.get('django_language', '').lower()
    if lang in ['az', 'en', 'ru']:
        translation.activate(lang)
        return lang
    
    lang = request.session.get('language', '').lower()
    if lang in ['az', 'en', 'ru']:
        request.session['django_language'] = lang
        request.session.modified = True
        translation.activate(lang)
        return lang
    
    lang = getattr(request, 'LANGUAGE_CODE', 'az')
    if lang in ['az', 'en', 'ru']:
        request.session['django_language'] = lang
        request.session['language'] = lang
        request.session.modified = True
        translation.activate(lang)
        return lang
    
    # Default olaraq az
    request.session['django_language'] = 'az'
    request.session['language'] = 'az'
    request.session.modified = True
    translation.activate('az')
    return 'az'


def get_localized_field_name(field_base, lang):
    if lang == 'en':
        return f'{field_base}_en'
    elif lang == 'ru':
        return f'{field_base}_ru'
    else:
        return f'{field_base}_az'


@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_project_categories(lang='az'):
    """Layihə kateqoriyalarını qaytarır"""
    name_field = get_localized_field_name('name', lang)
    return ProjectCategory.objects.all().order_by('id')


def get_projects(lang='az', category_slug=None, is_active=True, is_completed=None, on_main_page=None, speacial_project=None):
    queryset = Project.objects.select_related('category').prefetch_related(
        Prefetch('medias', queryset=Media.objects.filter(image__isnull=False))
    )
    
    if is_active is not None:
        queryset = queryset.filter(is_active=is_active)
    
    if is_completed is not None:
        queryset = queryset.filter(is_completed=is_completed)
    
    if category_slug:
        queryset = queryset.filter(category__slug=category_slug)
    
    if on_main_page is not None:
        queryset = queryset.filter(on_main_page=on_main_page)
    
    if speacial_project is not None:
        queryset = queryset.filter(speacial_project=speacial_project)
    
    return queryset.order_by('-created_at')


@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_project_by_slug(slug, lang='az'):
    try:
        project = Project.objects.select_related('category').prefetch_related(
            Prefetch('medias', queryset=Media.objects.filter(image__isnull=False))
        ).get(slug=slug, is_active=True)
        return project
    except Project.DoesNotExist:
        return None


@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_about(lang='az'):
    about = About.objects.prefetch_related(
        Prefetch('medias', queryset=Media.objects.filter(
            Q(image__isnull=False) | Q(video__isnull=False)
        ))
    ).first()
    return about


def get_partners(lang='az', is_active=True):
    queryset = Partner.objects.prefetch_related(
        Prefetch('medias', queryset=Media.objects.filter(image__isnull=False))
    )
    
    if is_active is not None:
        queryset = queryset.filter(is_active=is_active)
    
    return queryset.order_by('-created_at')


@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_contact(lang='az'):
    return Contact.objects.first()


@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_services(lang='az', is_active=True):
    queryset = Service.objects.prefetch_related(
        Prefetch('medias', queryset=Media.objects.filter(image__isnull=False))
    )
    if is_active is not None:
        queryset = queryset.filter(is_active=is_active)
    return list(queryset.order_by('-created_at'))


def get_vacancies(lang='az', is_active=True):
    queryset = Vacancy.objects.prefetch_related(
        Prefetch('medias', queryset=Media.objects.filter(image__isnull=False))
    )
    
    if is_active is not None:
        queryset = queryset.filter(is_active=is_active)
    
    return queryset.order_by('-created_at')


@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_vacancy_by_slug(slug, lang='az'):
    try:
        vacancy = Vacancy.objects.prefetch_related(
            Prefetch('medias', queryset=Media.objects.filter(image__isnull=False))
        ).get(slug=slug, is_active=True)
        return vacancy
    except Vacancy.DoesNotExist:
        return None


@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_background_image(page_type):
    image_map = {
        'home': 'is_home_page_background_image',
        'about': 'is_about_page_background_image',
        'contact': 'is_contact_page_background_image',
        'partner': 'is_partner_background_image',
        'project': 'is_project_page_background_image',
        'vacancy': 'is_vacany_page_background_image',
        'service': 'is_service_page_background_image',
        'footer': 'is_footer_background_image',
    }
    
    if page_type not in image_map:
        return None
    
    media = Media.objects.filter(**{image_map[page_type]: True}).first()
    if media and media.image:
        return media.image.url
    return None


@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_home_background_images(limit=6):
    """Ana səhifə hero karuseli üçün background image-ləri qaytarır (maksimum 6 ədəd)"""
    media_list = Media.objects.filter(
        is_home_page_background_image=True,
        image__isnull=False
    ).order_by('-created_at')[:limit]
    
    return [media.image.url for media in media_list if media.image]


@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_motto(lang='az'):
    motto = Motto.objects.first()
    if not motto:
        return None
    
    text_field = get_localized_field_name('text', lang)
    text = getattr(motto, text_field, motto.text_az)
    return text


@cached_query(timeout='CACHE_TIMEOUT_LONG')
@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_statistics():

    statistic = Statistic.objects.first()
    
    if statistic:
        return {
            'client_count': statistic.value_one,
            'project_count': statistic.value_two,
            'partner_count': statistic.value_three,
        }
    
    from projects.models import AppealVacancy
    
    client_count = AppealVacancy.objects.values('email', 'phone_number').distinct().count()
    project_count = Project.objects.filter(is_active=True).count()
    partner_count = Partner.objects.filter(is_active=True).count()
    
    return {
        # 'client_count': client_count,
        'project_count': project_count,
        'partner_count': partner_count,
    }


def serialize_project(project, lang='az'):
    if project is None:
        return None
    
    name_field = get_localized_field_name('name', lang)
    desc_field = get_localized_field_name('description', lang)
    cat_name_field = get_localized_field_name('name', lang)
    
    return {
        'id': project.id,
        'slug': project.slug,
        'name': getattr(project, name_field, project.name_az),
        'description': getattr(project, desc_field, project.description_az),
        'url': project.url,
        'is_completed': project.is_completed,
        'is_active': project.is_active,
        'speacial_project': project.speacial_project,
        'on_main_page': project.on_main_page,
        'project_date': project.project_date,
        'created_at': project.created_at,
        'category': {
            'id': project.category.id,
            'slug': project.category.slug,
            'name': getattr(project.category, cat_name_field, project.category.name_az),
        },
        'medias': [
            {
                'id': media.id,
                'image': media.image.url if media.image else None,
                'video': media.video.url if media.video else None,
            }
            for media in project.medias.all()
        ]
    }


def serialize_project_category(category, lang='az'):
    name_field = get_localized_field_name('name', lang)
    
    return {
        'id': category.id,
        'slug': category.slug,
        'name': getattr(category, name_field, category.name_az),
    }


def serialize_about(about, lang='az'):
    if about is None:
        return None
    
    main_title_field = get_localized_field_name('main_title', lang)
    second_title_field = get_localized_field_name('second_title', lang)
    desc_field = get_localized_field_name('description', lang)
    
    return {
        'id': about.id,
        'main_title': getattr(about, main_title_field, about.main_title_az),
        'second_title': getattr(about, second_title_field, about.second_title_az),
        'description': getattr(about, desc_field, about.description_az),
        'medias': [
            {
                'id': media.id,
                'image': media.image.url if media.image else None,
                'video': media.video.url if media.video else None,
            }
            for media in about.medias.all()
        ]
    }


def serialize_service(service, lang='az'):
    if service is None:
        return None
    title_field = get_localized_field_name('title', lang)
    desc_field = get_localized_field_name('description', lang)
    first_media = service.medias.filter(image__isnull=False).first()
    return {
        'id': service.id,
        'title': getattr(service, title_field, service.title_az),
        'description': getattr(service, desc_field, service.description_az),
        'image': first_media.image.url if first_media and first_media.image else None,
        'url': service.url if getattr(service, 'url', None) else None,
    }


def serialize_partner(partner, lang='az'):
    if partner is None:
        return None
    
    name_field = get_localized_field_name('name', lang)
    
    media = partner.medias.first()
    
    return {
        'id': partner.id,
        'name': getattr(partner, name_field, partner.name_az),
        'instagram': partner.instagram,
        'facebook': partner.facebook,
        'linkedn': partner.linkedn,
        'is_active': partner.is_active,
        'created_at': partner.created_at,
        'logo': media.image.url if media and media.image else None,
    }


def serialize_contact(contact, lang='az'):
    if contact is None:
        return None
    
    address_field = get_localized_field_name('address', lang)
    
    return {
        'id': contact.id,
        'address': getattr(contact, address_field, contact.address_az),
        'phone': contact.phone,
        'whatsapp_number': contact.whatsapp_number,
        'whatsapp_number_2': contact.whatsapp_number_2,
        'phone_three': contact.phone_three,
        'email': contact.email,
        'instagram': contact.instagram,
        'facebook': contact.facebook,
        'youtube': contact.youtube,
        'linkedn': contact.linkedn,
        'tiktok': contact.tiktok,
    }


def serialize_vacancy(vacancy, lang='az'):
    if vacancy is None:
        return None
    
    title_field = get_localized_field_name('title', lang)
    desc_field = get_localized_field_name('description', lang)
    
    media = vacancy.medias.first()
    
    return {
        'id': vacancy.id,
        'slug': vacancy.slug,
        'title': getattr(vacancy, title_field, vacancy.title_az),
        'description': getattr(vacancy, desc_field, vacancy.description_az),
        'is_active': vacancy.is_active,
        'created_at': vacancy.created_at,
        'image': media.image.url if media and media.image else None,
    }


def paginate_queryset(queryset, page, per_page):
    paginator = Paginator(queryset, per_page)
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    return page_obj, paginator


def get_pagination_data(page_obj, paginator):
    return {
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages,
        'total_count': paginator.count,
        'per_page': paginator.per_page,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
    }


@cached_page_data(timeout='CACHE_TIMEOUT_MEDIUM')
def get_home_page_data(request, lang):
    category_slug = request.GET.get('slug')  # category_slug -> slug
    is_completed = request.GET.get('is_completed')
    is_active = request.GET.get('is_active', 'true').lower() == 'true'
    special_filter = request.GET.get('special')  # "Seçilmiş" filteri üçün
    
    if is_completed is not None:
        is_completed = is_completed.lower() == 'true'
    else:
        is_completed = None
    
    projects_page = request.GET.get('page', 1)
    projects_per_page = int(request.GET.get('per_page', 9))
    
    if special_filter == 'true':
        # "Seçilmiş" filterində: həm speacial_project=True, həm də on_main_page=True olanlar
        projects = get_projects(
            lang=lang,
            category_slug=None,
            is_active=is_active,
            is_completed=is_completed,
            on_main_page=True,         # on_main_page=True olmalıdır
            speacial_project=True
        )[:9]  # Ümumi maksimum 9 layihə
    else:
        all_main_page_projects = get_projects(
            lang=lang,
            category_slug=None,         # bütün kateqoriyalar
            is_active=is_active,
            is_completed=is_completed,
            on_main_page=True,
            speacial_project=None
        )

        from collections import defaultdict

        projects_by_category = defaultdict(list)
        for project in all_main_page_projects:
            cat_id = project.category_id
            if len(projects_by_category[cat_id]) < 9:
                projects_by_category[cat_id].append(project)

        projects = []
        for cat_id in sorted(projects_by_category.keys()):
            projects.extend(projects_by_category[cat_id])

    serialized_projects = [serialize_project(project, lang) for project in projects]
    projects_paginator = None
    projects_page_obj = None
    
    categories = get_project_categories(lang)
    serialized_categories = [
        serialize_project_category(category, lang)
        for category in categories
    ]
    
    partners_page = request.GET.get('partners_page', 1)
    partners_per_page = int(request.GET.get('partners_per_page', 10))
    
    all_partners = get_partners(lang=lang, is_active=True)
    partners_page_obj, partners_paginator = paginate_queryset(all_partners, partners_page, partners_per_page)
    serialized_partners = [
        serialize_partner(partner, lang)
        for partner in partners_page_obj
    ]
    
    vacancies_page = request.GET.get('vacancies_page', 1)
    vacancies_per_page = int(request.GET.get('vacancies_per_page', 9))
    
    all_vacancies = get_vacancies(lang=lang, is_active=True)
    vacancies_page_obj, vacancies_paginator = paginate_queryset(all_vacancies, vacancies_page, vacancies_per_page)
    serialized_vacancies = [
        serialize_vacancy(vacancy, lang)
        for vacancy in vacancies_page_obj
    ]
    
    about = get_about(lang)
    serialized_about = serialize_about(about, lang) if about else None
    
    contact = get_contact(lang)
    serialized_contact = serialize_contact(contact, lang) if contact else None
    
    # Hero carousel üçün 6 ədəd background image
    hero_background_images = get_home_background_images(limit=6)
    
    # Motto modelindən deviz
    motto = get_motto(lang)
    
    return {
        'projects': serialized_projects,
        'categories': serialized_categories,
        'partners': serialized_partners,
        'vacancies': serialized_vacancies,
        'about': serialized_about,
        'contact': serialized_contact,
        'projects_pagination': get_pagination_data(projects_page_obj, projects_paginator) if projects_paginator else None,
        'partners_pagination': get_pagination_data(partners_page_obj, partners_paginator),
        'vacancies_pagination': get_pagination_data(vacancies_page_obj, vacancies_paginator),
        'filters': {
            'slug': category_slug,  # category_slug -> slug
            'is_completed': is_completed,
            'is_active': is_active,
        },
        'background_image': get_background_image('home'),
        'hero_background_images': hero_background_images,
        'motto': motto,
        'statistics': get_statistics(),
        'footer_image': get_background_image('footer'),
    }


@cached_page_data(timeout='CACHE_TIMEOUT_MEDIUM')
def get_project_list_data(request, lang):
    category_slug = request.GET.get('slug')  # category_slug -> slug
    is_completed = request.GET.get('is_completed')
    is_active = request.GET.get('is_active', 'true').lower() == 'true'
    
    if is_completed is not None:
        is_completed = is_completed.lower() == 'true'
    else:
        is_completed = None
    
    page = request.GET.get('page', 1)
    per_page = int(request.GET.get('per_page', 10))
    
    projects = get_projects(
        lang=lang,
        category_slug=category_slug,
        is_active=is_active,
        is_completed=is_completed
    )
    
    projects_page_obj, projects_paginator = paginate_queryset(projects, page, per_page)
    serialized_projects = [
        serialize_project(project, lang)
        for project in projects_page_obj
    ]
    
    categories = get_project_categories(lang)
    serialized_categories = [
        serialize_project_category(category, lang)
        for category in categories
    ]
    
    selected_category = None
    if category_slug:
        try:
            category_obj = next((cat for cat in categories if cat.slug == category_slug), None)
            if category_obj:
                selected_category = serialize_project_category(category_obj, lang)
        except (ValueError, TypeError):
            pass
    
    contact = get_contact(lang)
    serialized_contact = serialize_contact(contact, lang) if contact else None
    
    return {
        'projects': serialized_projects,
        'categories': serialized_categories,
        'selected_category': selected_category,
        'contact': serialized_contact,
        'pagination': get_pagination_data(projects_page_obj, projects_paginator),
        'filters': {
            'slug': category_slug,  # category_slug -> slug
            'is_completed': is_completed,
            'is_active': is_active,
        },
        'background_image': get_background_image('project'),
        'footer_image': get_background_image('footer'),
    }


@cached_page_data(timeout='CACHE_TIMEOUT_MEDIUM')
def get_vacancy_list_data(request, lang):
    is_active = request.GET.get('is_active', 'true').lower() == 'true'
    page = request.GET.get('page', 1)
    per_page = int(request.GET.get('per_page', 10))
    
    vacancies = get_vacancies(lang=lang, is_active=is_active)
    vacancies_page_obj, vacancies_paginator = paginate_queryset(vacancies, page, per_page)
    
    serialized_vacancies = [
        serialize_vacancy(vacancy, lang)
        for vacancy in vacancies_page_obj
    ]
    
    contact = get_contact(lang)
    serialized_contact = serialize_contact(contact, lang) if contact else None
    
    return {
        'vacancies': serialized_vacancies,
        'contact': serialized_contact,
        'pagination': get_pagination_data(vacancies_page_obj, vacancies_paginator),
        'background_image': get_background_image('vacancy'),
        'footer_image': get_background_image('footer'),
    }
