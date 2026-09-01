"""Import teachers, students, and study groups from qrup_import.json."""

import json
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from portals.forms import (
    PORTAL_ROLE_STUDENT,
    PORTAL_ROLE_TEACHER,
    create_portal_profile,
    set_teacher_course_specializations,
)
from portals.models import Schedule, StudentCourseSpecialization, StudentProfile, StudyGroup, TeacherProfile
from portals.utils.qrup_import_helpers import (
    ENGLISH_LANGUAGE_COURSE_NAMES,
    ENGLISH_LANGUAGE_COURSE_SLUGS,
    IELTS_COURSE_NAMES,
    IELTS_COURSE_SLUGS,
    group_course_slugs,
    is_ielts_track,
    normalize_course_slug,
    student_course_enrollment_slugs,
    sync_student_participation,
)
from portals.utils.student_courses import ensure_student_group_course_enrollments
from projects.models.service_models import Service

User = get_user_model()

DEFAULT_JSON = Path(__file__).resolve().parents[2] / 'data' / 'qrup_import.json'

SUBJECT_FALLBACKS = {
    'general-english': ['general english', 'general-english', 'english language course', 'english language'],
    'foundation-ielts': ['foundation ielts', 'foundation-ielts', 'ielts'],
    'english-for-kids': ['english for kids', 'kids english', 'english-for-kids'],
    'ap-economics': ['ap economics', 'ap-economics'],
    'gre-math': ['gre math', 'gre-math'],
    'gre-verbal': ['gre verbal', 'gre-verbal'],
    'ielts': ['ielts', 'ielts course'],
    'ielts-course': ['ielts course', 'ielts'],
    'english-language-course': ['english language course', 'english language'],
    'sat-verbal': ['sat verbal', 'sat-verbal'],
    'cfa-1': ['cfa 1', 'cfa-1', 'cfa'],
}


def load_payload(path):
    with open(path, encoding='utf-8') as fh:
        return json.load(fh)


def resolve_service(slug, cache):
    slug = normalize_course_slug(slug)
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


def resolve_service_candidates(slugs, names, cache):
    for slug in slugs:
        service = resolve_service(slug, cache)
        if service:
            return service
    for name in names:
        for field in ('name_en', 'name_az', 'name_ru'):
            service = Service.objects.filter(is_active=True, **{f'{field}__iexact': name}).first()
            if not service:
                service = Service.objects.filter(is_active=True, **{f'{field}__icontains': name}).first()
            if service:
                cache[service.slug] = service
                return service
    return None


def resolve_ielts_bundle(cache):
    services = []
    for slugs, names in (
        (IELTS_COURSE_SLUGS, IELTS_COURSE_NAMES),
        (ENGLISH_LANGUAGE_COURSE_SLUGS, ENGLISH_LANGUAGE_COURSE_NAMES),
    ):
        service = resolve_service_candidates(slugs, names, cache)
        if service and service not in services:
            services.append(service)
    return services


def resolve_course_type(service, slug):
    if service and service.slug:
        return service.slug
    return normalize_course_slug(slug)


def get_or_create_user(username, password, *, update_password=False):
    user = User.objects.filter(username=username).first()
    if user:
        if update_password and password:
            user.set_password(password)
            user.save(update_fields=['password'])
        return user, False
    user = User.objects.create_user(username=username, password=password)
    return user, True


def ensure_student_course_enrollments(profile, item, cache, stdout, style):
    slugs = item.get('course_enrollments') or student_course_enrollment_slugs(
        item.get('subject', ''),
        item.get('course_slug', ''),
    )
    services = []
    if is_ielts_track(item.get('subject', ''), item.get('course_slug', '')):
        services = resolve_ielts_bundle(cache)
    else:
        for slug in slugs:
            service = resolve_service(slug, cache)
            if service and service not in services:
                services.append(service)

    seen = set()
    for service in services:
        code = service.slug
        if code in seen:
            continue
        seen.add(code)
        StudentCourseSpecialization.objects.update_or_create(
            student=profile,
            course_type=code,
            defaults={'is_active': True},
        )
    if is_ielts_track(item.get('subject', ''), item.get('course_slug', '')) and len(services) < 2:
        stdout.write(style.WARNING(
            f'    IELTS bundle incomplete for {profile.user.username} '
            f'({len(services)}/2 courses resolved)',
        ))


def sync_group_schedules(group, schedule_items, *, effective_from=None):
    from datetime import time as dt_time

    effective_from = effective_from or timezone.localdate()
    desired_keys = set()
    for slot in schedule_items or []:
        start_raw = slot.get('start_time', '')
        parts = str(start_raw).split(':')
        if len(parts) < 2:
            continue
        start_time = dt_time(int(parts[0]), int(parts[1]))
        weekday = int(slot['weekday'])
        duration = int(slot.get('duration_min') or 90)
        room = slot.get('room_or_link', '')
        Schedule.objects.update_or_create(
            group=group,
            weekday=weekday,
            start_time=start_time,
            effective_from=effective_from,
            defaults={
                'duration_min': duration,
                'room_or_link': room,
            },
        )
        desired_keys.add((weekday, start_time, effective_from))

    if not desired_keys:
        return

    keep_ids = []
    for row in group.schedules.filter(effective_from=effective_from):
        if (row.weekday, row.start_time, row.effective_from) in desired_keys:
            keep_ids.append(row.pk)
    group.schedules.filter(effective_from=effective_from).exclude(pk__in=keep_ids).delete()


class Command(BaseCommand):
    help = 'Import or update portal teachers, students, and study groups from qrup_import.json.'

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
            help='Skip users that already exist instead of updating profiles.',
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
        student_payload_by_name = {
            item['full_name']: item for item in payload.get('students', [])
        }

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
                service_cache,
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
                student_payload_by_name,
                dry_run=dry_run,
            )
            self._import_participation(
                payload.get('students', []),
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

            action = 'UPDATE' if existing else 'CREATE'
            self.stdout.write(f'  {"[dry]" if dry_run else action} Teacher: {username}')
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
            elif item.get('phone') and profile.phone != item['phone']:
                profile.phone = item['phone']
                profile.save(update_fields=['phone'])

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
        service_cache,
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

            action = 'UPDATE' if existing else 'CREATE'
            self.stdout.write(f'  {"[dry]" if dry_run else action} Student: {username}')
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
            else:
                update_fields = []
                phone = item.get('phone', '')
                if phone and profile.phone != phone:
                    profile.phone = phone
                    update_fields.append('phone')
                if item.get('start_date'):
                    parsed_start = self._parse_start_date(item, profile)
                    if parsed_start:
                        profile.enrollment_date = parsed_start
                        update_fields.append('enrollment_date')
                if update_fields:
                    profile.save(update_fields=update_fields)

            ensure_student_course_enrollments(
                profile,
                item,
                service_cache,
                self.stdout,
                self.style,
            )

            student_profiles[item['full_name']] = profile

    def _import_groups(
        self,
        groups,
        service_cache,
        teacher_profiles,
        student_profiles,
        student_payload_by_name,
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

            self.stdout.write(f'  {"[dry]" if dry_run else "UPSERT"} Group: {item["name"]}')
            if dry_run:
                continue

            group, _created = StudyGroup.objects.get_or_create(
                name=item['name'],
                defaults={
                    'teacher': teacher,
                    'max_students': item.get('max_students') or 12,
                    'is_active': True,
                },
            )
            group.teacher = teacher
            group.max_students = item.get('max_students') or group.max_students
            group.is_active = True
            group.save(update_fields=['teacher', 'max_students', 'is_active'])

            slugs = item.get('course_slugs') or group_course_slugs(
                item.get('subject', ''),
                normalize_course_slug(item.get('course_slug', '')),
            )
            services = []
            for slug in slugs:
                service = resolve_service(slug, service_cache)
                if service and service not in services:
                    services.append(service)
                elif not service:
                    self.stdout.write(self.style.WARNING(f'    Unknown course for group: {slug}'))
            if services:
                group.courses.set(services)

            sync_group_schedules(
                group,
                item.get('schedule') or [],
                effective_from=self._group_schedule_start(
                    student_names,
                    student_payload_by_name,
                ),
            )

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

            group.students.set(profiles)
            for name in student_names:
                profile = student_profiles.get(name)
                if not profile:
                    profile = StudentProfile.objects.filter(user__username=name).first()
                if not profile:
                    continue
                ensure_student_group_course_enrollments(profile.pk, group)
                payload_item = student_payload_by_name.get(name)
                if payload_item:
                    ensure_student_course_enrollments(
                        profile,
                        payload_item,
                        service_cache,
                        self.stdout,
                        self.style,
                    )

    def _group_schedule_start(self, student_names, student_payload_by_name):
        from datetime import date

        candidates = []
        for name in student_names:
            payload = student_payload_by_name.get(name) or {}
            raw = payload.get('start_date')
            if not raw:
                continue
            if isinstance(raw, date):
                candidates.append(raw)
            else:
                try:
                    candidates.append(date.fromisoformat(str(raw)[:10]))
                except ValueError:
                    continue
        if candidates:
            return min(candidates)
        return timezone.localdate()

    def _parse_start_date(self, item, profile):
        from datetime import date

        raw = item.get('start_date') or getattr(profile, 'enrollment_date', None)
        if not raw:
            return None
        if isinstance(raw, date):
            return raw
        try:
            return date.fromisoformat(str(raw)[:10])
        except ValueError:
            return None

    def _import_participation(self, students, student_profiles, *, dry_run):
        with_participation = [s for s in students if s.get('participation')]
        if not with_participation:
            return
        self.stdout.write(f'Syncing participation for {len(with_participation)} students...')
        for item in with_participation:
            group_name = item.get('matched_group') or item.get('group_name')
            if not group_name:
                self.stdout.write(self.style.WARNING(
                    f'  SKIP participation (no group): {item.get("full_name")}',
                ))
                continue
            participation = item['participation']
            attended = participation.get('lessons_attended', 0)
            if not attended:
                continue
            self.stdout.write(
                f'  {"[dry]" if dry_run else "SYNC"} Participation: {item["full_name"]} '
                f'({attended}/{participation.get("total_sessions")})',
            )
            if dry_run:
                continue
            profile = student_profiles.get(item['full_name'])
            if not profile:
                profile = StudentProfile.objects.filter(user__username=item['full_name']).first()
            if not profile:
                self.stdout.write(self.style.WARNING(
                    f'    Student not found: {item["full_name"]}',
                ))
                continue
            group = StudyGroup.objects.filter(name=group_name, is_active=True).first()
            if not group:
                self.stdout.write(self.style.WARNING(f'    Group not found: {group_name}'))
                continue
            start_date = self._parse_start_date(item, profile)
            if not start_date:
                self.stdout.write(self.style.WARNING(
                    f'    No start date for: {item["full_name"]}',
                ))
                continue
            saved = sync_student_participation(
                profile,
                group,
                participation,
                start_date=start_date,
            )
            if not saved:
                self.stdout.write(self.style.WARNING(
                    f'    No sessions generated for: {item["full_name"]}',
                ))
