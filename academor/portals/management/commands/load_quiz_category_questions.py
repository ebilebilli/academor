"""Load quizzes and questions from JSON files in portals/resources/quiz_questions/."""

from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from portals.utils.quiz_resource_loader import RESOURCES_DIR, load_all_resources, load_resource_file


class Command(BaseCommand):
    help = 'Load quizzes and inline questions from JSON files in portals/resources/quiz_questions/.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            help='Load a single JSON file (name under resources/quiz_questions/ or full path).',
        )
        parser.add_argument(
            '--keep-old',
            action='store_true',
            help='Do not deactivate questions missing from the resource file.',
        )

    def handle(self, *args, **options):
        deactivate_missing = not options['keep_old']

        if options['file']:
            file_arg = options['file']
            path = Path(file_arg)
            if not path.is_file():
                path = RESOURCES_DIR / file_arg
            if not path.is_file():
                raise CommandError(f'Resource file not found: {options["file"]}')
            results = [load_resource_file(path, deactivate_missing=deactivate_missing)]
        else:
            results = load_all_resources(deactivate_missing=deactivate_missing)
            if not results:
                raise CommandError(
                    f'No JSON files found in {RESOURCES_DIR}. '
                    'Add a resource file first.',
                )

        for row in results:
            self.stdout.write(
                self.style.SUCCESS(
                    f'{row["file"]} → {row["category"]}: '
                    f'Quiz {row["quiz_topic"]} '
                    f'({"created" if row["quiz_created"] else "updated"}, id={row["quiz_id"]}); '
                    f'questions {row["created"]} created, {row["updated"]} updated, '
                    f'{row["deleted"]} deleted ({row["total"]} total).',
                ),
            )
