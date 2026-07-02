from portals.utils.portal_services import services_for_portal_codes


def link_study_group_courses(group, *codes):
    group.courses.set(services_for_portal_codes(codes))


link_study_group_services = link_study_group_courses
