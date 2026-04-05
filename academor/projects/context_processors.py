from projects.utils.queries import get_contact, get_language_from_request, serialize_contact


def site_footer_context(request):
    lang = get_language_from_request(request)
    contact = get_contact(lang)
    return {
        'footer_contact': serialize_contact(contact, lang) if contact else None,
    }
