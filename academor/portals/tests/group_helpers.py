from portals.utils.portal_services import services_for_portal_codes


def link_study_group_courses(group, *codes):
    group.courses.set(services_for_portal_codes(codes))


link_study_group_services = link_study_group_courses


def create_quiz_category(name, *service_codes):
    from portals.models import QuizCategory

    category = QuizCategory.objects.create(name=name)
    category.services.set(services_for_portal_codes(service_codes))
    return category


def link_quiz_category_services(category, *codes):
    category.services.set(services_for_portal_codes(codes))
