"""
Re-process existing university flag images that were uploaded before server-side resize.

Usage:
    python manage.py resize_university_flags
    python manage.py resize_university_flags --dry-run
"""
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from PIL import Image

from projects.models import University
from projects.signals import UNIVERSITY_FLAG_MAX_PX
from projects.utils.image_resize import resize_image_field


class Command(BaseCommand):
    help = 'Downscale university flag images larger than the public display size.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='List oversized flags without writing changes.',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        resized = 0
        skipped = 0
        errors = 0

        for university in University.objects.exclude(flag='').iterator():
            name = university.flag.name
            if not name or not default_storage.exists(name):
                skipped += 1
                continue
            try:
                with default_storage.open(name, 'rb') as fh:
                    width, height = Image.open(fh).size
            except Exception as exc:
                errors += 1
                self.stderr.write(f'#{university.pk} {name}: read failed ({exc})')
                continue

            if width <= UNIVERSITY_FLAG_MAX_PX and height <= UNIVERSITY_FLAG_MAX_PX:
                skipped += 1
                continue

            label = f'#{university.pk} {(university.name or name).strip()[:60]}'
            self.stdout.write(f'{label}: {width}×{height} → max {UNIVERSITY_FLAG_MAX_PX}px')
            if dry_run:
                resized += 1
                continue

            old_name = name
            try:
                if resize_image_field(
                    university.flag,
                    max_width=UNIVERSITY_FLAG_MAX_PX,
                    max_height=UNIVERSITY_FLAG_MAX_PX,
                    force=True,
                ):
                    university.save(update_fields=['flag'])
                    if old_name != university.flag.name and default_storage.exists(old_name):
                        default_storage.delete(old_name)
                    resized += 1
                else:
                    skipped += 1
            except Exception as exc:
                errors += 1
                self.stderr.write(f'{label}: resize failed ({exc})')

        verb = 'would resize' if dry_run else 'resized'
        self.stdout.write(
            self.style.SUCCESS(f'Done — {verb} {resized}, skipped {skipped}, errors {errors}.')
        )
