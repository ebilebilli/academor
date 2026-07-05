"""Generate IELTS reading quiz JSON resource files from the topic bank."""

from django.core.management.base import BaseCommand

from portals.utils.reading_bank_data import TOPICS
from portals.utils.reading_bank_generator import build_quiz_json, generate_all, validate_quiz


class Command(BaseCommand):
    help = 'Write ielts_reading_test_*.json files from the built-in topic bank (tests 2–51).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Validate topics without writing JSON files.',
        )

    def handle(self, *args, **options):
        errors = []
        for topic in TOPICS:
            data = build_quiz_json(topic)
            errors.extend(validate_quiz(data, quiz_number=topic['quiz_number']))

        if errors:
            for message in errors:
                self.stderr.write(self.style.ERROR(message))
            raise SystemExit(1)

        self.stdout.write(
            self.style.SUCCESS(f'Validated {len(TOPICS)} quizzes (40 questions each).'),
        )

        if options['dry_run']:
            return

        paths = generate_all(TOPICS)
        for path in paths:
            self.stdout.write(self.style.SUCCESS(f'Wrote {path.name}'))
