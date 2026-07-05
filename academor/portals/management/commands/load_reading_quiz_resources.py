"""Load IELTS-style reading quizzes from JSON files in portals/resources/reading_questions/."""

from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from portals.utils.quiz_reading_resource_loader import (
    RESOURCES_DIR,
    load_all_reading_resources,
    load_reading_resource_file,
)


class Command(BaseCommand):
    help = (
        'Load reading quizzes (passages, groups, questions) from JSON files '
        'in portals/resources/reading_questions/.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            help='Load a single JSON file (name under resources/reading_questions/ or full path).',
        )
        parser.add_argument(
            '--keep-old',
            action='store_true',
            help='Do not replace existing passages/questions on the quiz.',
        )

    def handle(self, *args, **options):
        replace_existing = not options['keep_old']

        if options['file']:
            file_arg = options['file']
            path = Path(file_arg)
            if not path.is_file():
                path = RESOURCES_DIR / file_arg
            if not path.is_file():
                raise CommandError(f'Resource file not found: {options["file"]}')
            results = [load_reading_resource_file(path, replace_existing=replace_existing)]
        else:
            results = load_all_reading_resources(replace_existing=replace_existing)
            if not results:
                raise CommandError(
                    f'No JSON files found in {RESOURCES_DIR}. '
                    'Add a reading resource file first.',
                )

        for row in results:
            self.stdout.write(
                self.style.SUCCESS(
                    f'{row["file"]} → {row["category"]}: '
                    f'Quiz {row["quiz_topic"]} '
                    f'({"created" if row["quiz_created"] else "updated"}, id={row["quiz_id"]}); '
                    f'{row["passages"]} passage(s), {row["groups"]} group(s), '
                    f'{row["questions"]} question(s).',
                ),
            )
