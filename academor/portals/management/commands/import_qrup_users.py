"""Import teachers, students, and study groups from qrup_import.json."""

import json
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from portals.forms import (
    PORTAL_ROLE_STUDENT,
    PORTAL_ROLE_TEACHER,
    create_portal_profile,
    set_teacher_course_specializations,
)
from portals.models import StudentProfile, StudyGroup, TeacherProfile
from portals.utils.student_courses import ensure_student_group_course_enrollments
from projects.models.service_models import Service

User = get_user_model()

DEFAULT_JSON = Path(__file__).resolve().parents[2] / 'data' / 'qrup_import.json'

SUBJECT_FALLBACKS = {
    'general-english': ['general english', 'general-english'],
    'foundation-ielts': ['foundation ielts', 'foundation-ielts'],
    'english-for-kids': ['english for kids', 'kids english', 'english-for-kids'],
    'ap-economics': ['ap economics', 'ap-economics'],
    'gre-math': ['gre math', 'gre-math'],
    'gre-verbal': ['gre verbal', 'gre-verbal'],
    'ielts': ['ielts'],
    'sat-verbal': ['sat verbal', 'sat-verbal'],
    'cfa-1': ['cfa 1', 'cfa-1', 'cfa'],
}


def load_payload(path):
    with open(path, encoding='utf-8') as fh:
        return json.load(fh)


def resolve_service(slug, cache):
    slug = (slug or '').strip().lower()
    if not slug:
        return None
    if slug in cache:
        return cache[slug]

    service = Service.objects.filter(slug=slug, is_active=True).first()
    if service:
        cache[slug] = service
        return service

    for candidate in SUBJECT_FALLBACKS.get(slug, [slug.replace('-', ' ')]):
        service = Service.objects.filter(is_active=True).filter(
            slug__icontains=candidate.replace(' ', '-'),
        ).first()
        if service:
            cache[slug] = service
            return service
        for field in ('name_az', 'name_en', 'name_ru'):
            service = Service.objects.filter(is_active=True, **{f'{field}__icontains': candidate}).first()
            if service:
                cache[slug] = service
                return service

    cache[slug] = None
    return None


def resolve_course_type(service, slug):
    if service and service.slug:
        return service.slug
    return slug


def get_or_create_user(username, password, *, update_password=False):
    user = User.objects.filter(username=username).first()
    if user:
        if update_password and password:
            user.set_password(password)
            user.save(update_fields=['password'])
        return user, False
    user = User.objects.create_user(username=username, password=password)
    return user, True


class Command(BaseCommand):
    help = 'Import portal teachers, students, and study groups from qrup_import.json.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--json',
            default=str(DEFAULT_JSON),
            help='Path to import JSON (default: portals/data/qrup_import.json).',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Print actions without writing to the database.',
        )
        parser.add_argument(
            '--update-passwords',
            action='store_true',
            help='Reset passwords for existing users to values from JSON.',
        )
        parser.add_argument(
            '--skip-existing',
            action='store_true',
            help='Skip users that already exist instead of updating.',
        )

    def handle(self, *args, **options):
        json_path = Path(options['json'])
        if not json_path.exists():
            raise CommandError(f'JSON file not found: {json_path}')

        payload = load_payload(json_path)
        dry_run = options['dry_run']
        update_passwords = options['update_passwords']
        skip_existing = options['skip_existing']

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN — no database changes.'))

        service_cache = {}
        teacher_profiles = {}
        student_profiles = {}

        with transaction.atomic():
            self._import_teachers(
                payload.get('teachers', []),
                service_cache,
                teacher_profiles,
                dry_run=dry_run,
                update_passwords=update_passwords,
                skip_existing=skip_existing,
            )
            self._import_students(
                payload.get('students', []),
                student_profiles,
                dry_run=dry_run,
                update_passwords=update_passwords,
                skip_existing=skip_existing,
            )
            self._import_groups(
                payload.get('groups', []),
                service_cache,
                teacher_profiles,
                student_profiles,
                dry_run=dry_run,
            )

            if dry_run:
                transaction.set_rollback(True)

        self.stdout.write(self.style.SUCCESS('Import finished.'))

    def _import_teachers(
        self,
        teachers,
        service_cache,
        teacher_profiles,
        *,
        dry_run,
        update_passwords,
        skip_existing,
    ):
        self.stdout.write(f'Importing {len(teachers)} teachers...')
        for item in teachers:
            username = item['username']
            existing = User.objects.filter(username=username).exists()
            if existing and skip_existing:
                profile = TeacherProfile.objects.filter(user__username=username).first()
                if profile:
                    teacher_profiles[item['full_name']] = profile
                self.stdout.write(f'  SKIP teacher (exists): {username}')
                continue

            self.stdout.write(f'  {"[dry]" if dry_run else "+"} Teacher: {username}')
            if dry_run:
                teacher_profiles[item['full_name']] = None
                continue

            user, created = get_or_create_user(
                username,
                item['password'],
                update_password=update_passwords and not created,
            )
            profile = TeacherProfile.objects.filter(user=user).first()
            if not profile:
                create_portal_profile(user, PORTAL_ROLE_TEACHER, phone=item.get('phone', ''))
                profile = TeacherProfile.objects.get(user=user)

            course_codes = []
            for slug in item.get('courses', []):
                service = resolve_service(slug, service_cache)
                if service:
                    course_codes.append(resolve_course_type(service, slug))
                else:
                    self.stdout.write(self.style.WARNING(f'    Unknown course slug: {slug}'))

            if course_codes:
                set_teacher_course_specializations(profile, course_codes)

            teacher_profiles[item['full_name']] = profile

    def _import_students(
        self,
        students,
        student_profiles,
        *,
        dry_run,
        update_passwords,
        skip_existing,
    ):
        self.stdout.write(f'Importing {len(students)} students...')
        for item in students:
            username = item['username']
            existing = User.objects.filter(username=username).exists()
            if existing and skip_existing:
                profile = StudentProfile.objects.filter(user__username=username).first()
                if profile:
                    student_profiles[item['full_name']] = profile
                self.stdout.write(f'  SKIP student (exists): {username}')
                continue

            self.stdout.write(f'  {"[dry]" if dry_run else "+"} Student: {username}')
            if dry_run:
                student_profiles[item['full_name']] = None
                continue

            user, created = get_or_create_user(
                username,
                item['password'],
                update_password=update_passwords and not created,
            )
            profile = StudentProfile.objects.filter(user=user).first()
            if not profile:
                create_portal_profile(
                    user,
                    PORTAL_ROLE_STUDENT,
                    phone=item.get('phone', ''),
                )
                profile = StudentProfile.objects.get(user=user)

            if item.get('start_date') and not profile.enrollment_date:
                profile.enrollment_date = item['start_date']
                profile.save(update_fields=['enrollment_date'])

            student_profiles[item['full_name']] = profile

    def _import_groups(
        self,
        groups,
        service_cache,
        teacher_profiles,
        student_profiles,
        *,
        dry_run,
    ):
        self.stdout.write(f'Importing {len(groups)} study groups...')
        for item in groups:
            teacher_name = item.get('teacher', '')
            teacher = teacher_profiles.get(teacher_name)
            if not teacher and not dry_run:
                teacher = TeacherProfile.objects.filter(user__username=teacher_name).first()

            if not teacher and not dry_run:
                self.stdout.write(self.style.ERROR(f'  SKIP group (no teacher): {item["name"]}'))
                continue

            self.stdout.write(f'  {"[dry]" if dry_run else "+"} Group: {item["name"]}')
            if dry_run:
                continue

            group, created = StudyGroup.objects.get_or_create(
                name=item['name'],
                defaults={
                    'teacher': teacher,
                    'max_students': item.get('max_students') or 12,
                    'is_active': True,
                },
            )
            if not created:
                group.teacher = teacher
                group.max_students = item.get('max_students') or group.max_students
                group.is_active = True
                group.save(update_fields=['teacher', 'max_students', 'is_active'])

            service = resolve_service(item.get('course_slug', ''), service_cache)
            if service:
                group.courses.set([service])
            else:
                self.stdout.write(self.style.WARNING(
                    f'    Unknown course for group: {item.get("course_slug")}',
                ))

            student_names = item.get('student_names') or []
            profiles = []
            for name in student_names:
                profile = student_profiles.get(name)
                if not profile:
                    profile = StudentProfile.objects.filter(user__username=name).first()
                if profile:
                    profiles.append(profile)
                else:
                    self.stdout.write(self.style.WARNING(f'    Student not found for group: {name}'))

            if profiles:
                group.students.add(*profiles)
                for profile in profiles:
                    ensure_student_group_course_enrollments(profile.pk, group)
