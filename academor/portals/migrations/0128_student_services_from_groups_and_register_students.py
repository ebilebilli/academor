"""Students own their services; register names become real students.

Until now a student's quiz / mock-test / notification access followed the services of the
group they were in. From here on it follows the student's own services, and a group is only
a name. This migration carries the existing data over once:

1. every student keeps the services their groups gave them (as their own enrollments);
2. a student with no service at all gets the default: IELTS + General English;
3. every IELTS student gets General English switched on;
4. names typed into the attendance register ("guest" rows) become real students of that
   teacher (same defaults), and their attendance marks move with them;
5. register-only groups created by teachers become ordinary groups.

Nothing is deleted: old guest rows are only switched off.
"""

import re

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db import migrations

IELTS = 'ielts'
GENERAL_ENGLISH = 'general_english'
USERNAME_MAX = 150
_NOT_USERNAME_CHARS = re.compile(r'[^\w.@+\- ]', re.UNICODE)


def _service_code(service):
    from portals.utils.portal_services import infer_course_type_for_service

    return infer_course_type_for_service(service) or (service.slug or '').strip()


def _active_code_slugs(Service):
    """code -> every key (the code itself + service slugs) that means that code."""
    mapping = {}
    for service in Service.objects.filter(is_active=True):
        code = _service_code(service)
        if not code:
            continue
        bucket = mapping.setdefault(code, {code})
        slug = (service.slug or '').strip()
        if slug:
            bucket.add(slug)
    return mapping


def _clean_username(raw):
    name = ' '.join(_NOT_USERNAME_CHARS.sub(' ', str(raw or '')).split())
    return name[:USERNAME_MAX].strip()


def _free_username(User, base):
    candidate = base
    number = 2
    while User.objects.filter(username__iexact=candidate).exists():
        suffix = f' {number}'
        candidate = base[: USERNAME_MAX - len(suffix)].rstrip() + suffix
        number += 1
    return candidate


def _ensure_default_services(Spec, student_id, defaults):
    for code in defaults:
        Spec.objects.get_or_create(
            student_id=student_id,
            course_type=code,
            defaults={'is_active': True},
        )


def forwards(apps, schema_editor):
    Student = apps.get_model('portals', 'StudentProfile')
    Spec = apps.get_model('portals', 'StudentCourseSpecialization')
    Group = apps.get_model('portals', 'StudyGroup')
    Guest = apps.get_model('portals', 'AttendanceRegisterGuest')
    Attendance = apps.get_model('portals', 'Attendance')
    Service = apps.get_model('projects', 'Service')
    app_label, model_name = settings.AUTH_USER_MODEL.split('.')
    User = apps.get_model(app_label, model_name)

    if not Student.objects.exists() and not Guest.objects.exists():
        return  # fresh database: nothing to carry over

    code_slugs = _active_code_slugs(Service)
    defaults = [code for code in (IELTS, GENERAL_ENGLISH) if code in code_slugs]

    # 1. services the groups gave their students become the students' own
    for group in Group.objects.prefetch_related('courses', 'students'):
        codes = {_service_code(service) for service in group.courses.all() if service.is_active}
        codes.discard('')
        if not codes:
            continue
        for student in group.students.all():
            for code in codes:
                Spec.objects.get_or_create(
                    student_id=student.pk,
                    course_type=code,
                    defaults={'is_active': True},
                )

    # 2. no service at all -> the default pair
    if defaults:
        with_service = set(Spec.objects.values_list('student_id', flat=True))
        for student_id in Student.objects.values_list('pk', flat=True):
            if student_id not in with_service:
                _ensure_default_services(Spec, student_id, defaults)

    # 3. IELTS students have General English on
    if GENERAL_ENGLISH in code_slugs and IELTS in code_slugs:
        ielts_keys = code_slugs[IELTS]
        general_keys = code_slugs[GENERAL_ENGLISH]
        ielts_students = set(
            Spec.objects.filter(course_type__in=ielts_keys, is_active=True)
            .values_list('student_id', flat=True)
        )
        for student_id in ielts_students:
            rows = Spec.objects.filter(student_id=student_id, course_type__in=general_keys)
            if rows.exists():
                rows.filter(is_active=False).update(is_active=True)
            else:
                Spec.objects.create(
                    student_id=student_id,
                    course_type=GENERAL_ENGLISH,
                    is_active=True,
                )

    # 4. register names -> real students of that teacher
    for guest in Guest.objects.filter(is_active=True).select_related('group').order_by('id'):
        group = guest.group
        username = _clean_username(guest.name)
        if not username or group is None:
            continue

        student = None
        user = User.objects.filter(username__iexact=username).order_by('id').first()
        if user is not None:
            # the same name already signs in as a student: it is that student
            student = Student.objects.filter(user_id=user.pk).first()
        if student is None:
            if user is not None:
                username = _free_username(User, username)  # the name belongs to another role
            user = User.objects.create(
                username=username,
                password=make_password(None),  # no password yet: set one before they sign in
                is_active=True,
            )
            student = Student.objects.create(user_id=user.pk)

        student.teachers.add(group.teacher_id)
        if not group.is_main_register:
            if not group.students.filter(pk=student.pk).exists():
                if group.max_students and group.students.count() >= group.max_students:
                    Group.objects.filter(pk=group.pk).update(max_students=group.students.count() + 1)
                group.students.add(student.pk)
        if defaults and not Spec.objects.filter(student_id=student.pk).exists():
            _ensure_default_services(Spec, student.pk, defaults)

        for mark in Attendance.objects.filter(guest_id=guest.pk):
            clash = Attendance.objects.filter(
                group_id=mark.group_id,
                student_id=student.pk,
                session_date=mark.session_date,
                schedule__isnull=True,
            ).exists()
            if clash:
                mark.delete()  # the student already has a mark for that day
                continue
            Attendance.objects.filter(pk=mark.pk).update(student_id=student.pk, guest_id=None)

        Guest.objects.filter(pk=guest.pk).update(is_active=False)

    # 5. groups teachers made in the register are ordinary groups now
    Group.objects.filter(is_register_only=True, is_main_register=False).update(is_register_only=False)


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0127_student_active_teachers_lesson_targets'),
        ('projects', '0044_service_is_training'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
