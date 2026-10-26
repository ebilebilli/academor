"""Fill the site with throwaway demo content so pages look full during local testing.

    python manage.py seed_fake_content            # 8 services, 8 countries, 20 universities, 8 team members
    python manage.py seed_fake_content --clear    # remove only what this command created

Everything it creates has a slug starting with "demo-" (Team and University slugs are
built from the name, so their names start with "Demo"), so --clear never touches real
data. Images are generated locally with Pillow (no network). Not for production.
"""
import io
import random

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from PIL import Image, ImageDraw

from projects.models import AbroadModel, Service, Team, University
from projects.service_category_icons import SERVICE_CATEGORY_ICON_CHOICES

PREFIX = 'demo-'
PALETTE = [(0, 49, 61), (255, 84, 20), (75, 60, 255), (14, 80, 96), (255, 138, 93), (31, 122, 140)]

SERVICES = [
    'IELTS Hazırlıq', 'General English', 'Speaking Club', 'SAT Hazırlıq',
    'GMAT Hazırlıq', 'Business English', 'Kids English', 'Online Fərdi Dərs',
]
COUNTRIES = [
    ('Almaniya', 'Germany', 'Германия'), ('Böyük Britaniya', 'United Kingdom', 'Великобритания'),
    ('Fransa', 'France', 'Франция'), ('ABŞ', 'USA', 'США'), ('Kanada', 'Canada', 'Канада'),
    ('İtaliya', 'Italy', 'Италия'), ('Türkiyə', 'Türkiye', 'Турция'), ('Niderland', 'Netherlands', 'Нидерланды'),
]
TEAM = [
    ('Aysel Məmmədova', 'IELTS müəllimi'), ('Rəşad Əliyev', 'SAT müəllimi'),
    ('Nigar Həsənova', 'General English müəllimi'), ('Elvin Quliyev', 'Speaking koçu'),
    ('Leyla İsmayılova', 'Xaricdə təhsil məsləhətçisi'), ('Murad Kərimov', 'GMAT müəllimi'),
    ('Günay Abbasova', 'Kids English müəllimi'), ('Tural Səfərov', 'Akademik koordinator'),
]
LOREM = (
    'Asfansfa nsfnasn lorem ipsum dolor sit amet, consectetur adipiscing elit. '
    'Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. '
    'Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.'
)


def _image(name, size=(1200, 800), seed=0, label=''):
    rnd = random.Random(seed)
    w, h = size
    img = Image.new('RGB', size, PALETTE[seed % len(PALETTE)])
    draw = ImageDraw.Draw(img)
    for _ in range(26):
        x, y, r = rnd.randint(0, w), rnd.randint(0, h), rnd.randint(w // 20, w // 4)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=rnd.choice(PALETTE))
    if label:
        draw.text((w * 0.06, h * 0.82), label, fill=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, 'WEBP', quality=80)
    return ContentFile(buf.getvalue(), name=name)


def _html(title):
    return f'<p><strong>{title}</strong></p><p>{LOREM}</p><p>{LOREM}</p>'


class Command(BaseCommand):
    help = 'Create demo services, study-abroad countries, universities and team members (local testing only).'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Delete only the demo-* records this command created.')

    @transaction.atomic
    def handle(self, *args, **options):
        if options['clear']:
            counts = {
                'universities': University.objects.filter(slug__startswith=PREFIX).delete()[0],
                'countries': AbroadModel.objects.filter(slug__startswith=PREFIX).delete()[0],
                'services': Service.objects.filter(slug__startswith=PREFIX).delete()[0],
                'team': Team.objects.filter(slug__startswith=PREFIX).delete()[0],
            }
            self.stdout.write(self.style.SUCCESS(f'Removed demo records: {counts}'))
            return

        icons = [value for value, _label in SERVICE_CATEGORY_ICON_CHOICES if value]
        team_members = []
        for i, (name, role) in enumerate(TEAM, 1):
            name = f'Demo {name}'
            member, created = Team.objects.get_or_create(
                name=name,
                defaults={
                    'role': role, 'order': 100 + i,
                    'description_az': _html(name), 'description_en': _html(name), 'description_ru': _html(name),
                    'instagram': 'https://instagram.com/', 'linkedin': 'https://linkedin.com/',
                },
            )
            if created:
                member.image.save(f'demo-team-{i}.webp', _image('t.webp', (800, 800), seed=i, label=name), save=True)
            team_members.append(member)

        for i, name in enumerate(SERVICES, 1):
            service, created = Service.objects.get_or_create(
                slug=f'{PREFIX}service-{i}',
                defaults={
                    'name_az': name, 'name_en': name, 'name_ru': name,
                    'description_az': _html(name), 'description_en': _html(name), 'description_ru': _html(name),
                    'duration_months_az': f'{i + 2} ay', 'duration_months_en': f'{i + 2} months', 'duration_months_ru': f'{i + 2} мес.',
                    'lesson_count_az': f'{i * 12} dərs', 'lesson_count_en': f'{i * 12} lessons', 'lesson_count_ru': f'{i * 12} уроков',
                    'bullet_list_az': 'Asfansfa nsfnasn\nLorem ipsum dolor\nSit amet consectetur',
                    'bullet_list_en': 'Lorem ipsum dolor\nSit amet consectetur',
                    'bullet_list_ru': 'Lorem ipsum dolor\nSit amet consectetur',
                    'card_icon': icons[(i - 1) % len(icons)],
                    'price': 150 + i * 25, 'order': 100 + i,
                    'is_active': True, 'show_on_main_page': True,
                },
            )
            if created:
                service.instructors.set(team_members[(i - 1) % 8:(i - 1) % 8 + 2])

        countries = []
        for i, (az, en, ru) in enumerate(COUNTRIES, 1):
            country, created = AbroadModel.objects.get_or_create(
                slug=f'{PREFIX}abroad-{i}',
                defaults={
                    'name_az': az, 'name_en': en, 'name_ru': ru,
                    'description_az': _html(az), 'description_en': _html(en), 'description_ru': _html(ru),
                    'is_active': True, 'show_on_main_page': True,
                    'img': _image(f'demo-abroad-{i}.webp', seed=20 + i, label=en),
                },
            )
            if created:
                country.detail_page_img.save(f'demo-abroad-detail-{i}.webp', _image('d.webp', (1600, 700), seed=40 + i, label=en), save=True)
            countries.append(country)

        for i in range(1, 21):
            country = countries[(i - 1) % len(countries)]
            University.objects.get_or_create(
                name=f'Demo University {i} ({country.name_en})',
                defaults={
                    'description_az': _html(f'Demo Universitet {i}'),
                    'description_en': _html(f'Demo University {i}'),
                    'description_ru': _html(f'Демо университет {i}'),
                    'study_abroad': country, 'website': 'https://example.com/', 'is_active': True,
                    'flag': _image(f'demo-flag-{i}.webp', (300, 200), seed=60 + i),
                },
            )

        self.stdout.write(self.style.SUCCESS(
            'Demo content ready: '
            f'{Service.objects.filter(slug__startswith=PREFIX).count()} services, '
            f'{AbroadModel.objects.filter(slug__startswith=PREFIX).count()} countries, '
            f'{University.objects.filter(slug__startswith=PREFIX).count()} universities, '
            f'{Team.objects.filter(slug__startswith=PREFIX).count()} team members.'
        ))
