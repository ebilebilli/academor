"""Test fixtures for groups, services and quiz categories.

Groups carry no services any more: a student's access comes from their own
enrollments. ``link_study_group_courses`` is kept as a fixture shorthand for the many
tests that say "this is the IELTS group": it enrols the group's students (present and
added later) in those services *themselves*, the way a teacher or admin would. It
does not touch ``group.courses`` and nothing like it exists in production code.
"""

from django.db.models.signals import m2m_changed

from portals.utils.portal_services import services_for_portal_codes

_FIXTURE_GROUP_CODES = {}  # (group pk, group name) -> service codes for its students


def _enroll(student_id, codes):
    from portals.utils.student_courses import set_student_course_enrollment

    for code in codes:
        set_student_course_enrollment(student_id, code, is_active=True)


def _enroll_fixture_group_students(sender, instance, action, pk_set, reverse=False, **kwargs):
    if action != 'post_add' or not pk_set:
        return
    if reverse:
        # student.groups.add(group): instance is the student, pk_set the groups
        from portals.models import StudyGroup

        for group in StudyGroup.objects.filter(pk__in=pk_set):
            codes = _FIXTURE_GROUP_CODES.get((group.pk, group.name))
            if codes:
                _enroll(instance.pk, codes)
        return
    codes = _FIXTURE_GROUP_CODES.get((instance.pk, instance.name))
    if codes:
        for student_id in pk_set:
            _enroll(student_id, codes)


def _connect_fixture_receiver():
    from portals.models import StudyGroup

    m2m_changed.connect(
        _enroll_fixture_group_students,
        sender=StudyGroup.students.through,
        dispatch_uid='portals_tests_fixture_group_enrollments',
    )


def link_study_group_courses(group, *codes):
    """Fixture: the students of ``group`` are enrolled in ``codes`` themselves."""
    _connect_fixture_receiver()
    _FIXTURE_GROUP_CODES[(group.pk, group.name)] = tuple(codes)
    for student_id in group.students.values_list('pk', flat=True):
        _enroll(student_id, codes)


link_study_group_services = link_study_group_courses


def create_quiz_category(name, *service_codes):
    from portals.models import QuizCategory

    category = QuizCategory.objects.create(name=name)
    category.services.set(services_for_portal_codes(service_codes))
    return category


def link_quiz_category_services(category, *codes):
    category.services.set(services_for_portal_codes(codes))
