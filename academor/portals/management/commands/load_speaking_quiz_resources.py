"""Load IELTS-style speaking quizzes from JSON files in portals/resources/speaking_questions/."""

from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from portals.utils.quiz_speaking_resource_loader import (
    RESOURCES_DIR,
    load_all_speaking_resources,
    load_speaking_resource_file,
)


class Command(BaseCommand):
    help = (
        'Load speaking quizzes (parts and questions) from JSON files '
        'in portals/resources/speaking_questions/.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            help='Load a single JSON file (name under resources/speaking_questions/ or full path).',
        )
        parser.add_argument(
            '--keep-old',
            action='store_true',
            help='Do not replace existing parts/questions on the quiz.',
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
            results = [load_speaking_resource_file(path, replace_existing=replace_existing)]
        else:
            results = load_all_speaking_resources(replace_existing=replace_existing)
            if not results:
                raise CommandError(
                    f'No JSON files found in {RESOURCES_DIR}. '
                    'Add a speaking resource file first.',
                )

        for row in results:
            self.stdout.write(
                self.style.SUCCESS(
                    f'{row["file"]} → {row["category"]} '
                    f'(category id={row["category_id"]}): '
                    f'Quiz «{row["quiz_topic"]}» '
                    f'({"created" if row["quiz_created"] else "updated"}, quiz id={row["quiz_id"]}); '
                    f'{row["parts"]} part(s), {row["questions"]} speaking question(s). '
                    f'Admin: Portals → Quizzes → filter category «{row["category_name"]}».',
                ),
            )
