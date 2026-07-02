"""Parent portal access — linked children only, no course filtering."""

from portals.models import StudentProfile


def get_parent_students(profile):
    if not profile:
        return []
    return list(
        profile.students.select_related('user').order_by('user__username', 'id'),
    )


def resolve_parent_student(profile, request):
    students = get_parent_students(profile)
    if not students:
        return None
    raw = request.GET.get('student')
    if raw not in (None, ''):
        try:
            student_pk = int(raw)
        except (TypeError, ValueError):
            return None
        for student in students:
            if student.pk == student_pk:
                return student
        return None
    return students[0]


def parent_can_access_student(profile, student_id):
    if profile is None or not student_id:
        return False
    from portals.models import ParentProfile

    if isinstance(profile, int):
        return ParentProfile.objects.filter(pk=profile, students__pk=student_id).exists()
    return profile.students.filter(pk=student_id).exists()


def parent_has_students(profile):
    if not profile:
        return False
    return profile.students.exists()
