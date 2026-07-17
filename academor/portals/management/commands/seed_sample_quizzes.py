"""Create 10 sample quizzes with categories and questions for portal demo/testing."""

from django.core.management.base import BaseCommand
from django.db import transaction

from portals.models import (
    Quiz,
    QuizQuestion,
)
from portals.utils.portal_services import get_active_course_type_codes
from projects.models.service_models import Service

SAMPLE_SERVICES = (
    ('ielts', 'IELTS', 'ielts'),
    ('only-speaking', 'Speaking', 'speaking'),
    ('general-english', 'General English', 'general_english'),
)

QUIZ_SPECS = (
    ('ielts', 'Reading practice', 'IELTS Reading — Set 1'),
    ('ielts', 'Listening practice', 'IELTS Listening — Set 1'),
    ('ielts', 'Grammar review', 'IELTS Grammar — Mixed'),
    ('speaking', 'Fluency drills', 'Speaking — Fluency Set 1'),
    ('speaking', 'Pronunciation', 'Speaking — Pronunciation'),
    ('general_english', 'Vocabulary', 'General English — Vocabulary A'),
    ('general_english', 'Tenses', 'General English — Tenses'),
    ('ielts', 'Writing task 2', 'IELTS Writing — Task 2'),
    ('speaking', 'Part 2 topics', 'Speaking — Part 2 Cards'),
    ('general_english', 'Reading comprehension', 'General English — Reading'),
)

SAMPLE_QUESTIONS = (
    (
        'Choose the correct synonym for "rapid".',
        ['quick', 'slow', 'heavy', 'quiet'],
        'quick',
    ),
    (
        'Which sentence is grammatically correct?',
        [
            'She have been studying all day.',
            'She has been studying all day.',
            'She has been study all day.',
            'She having studied all day.',
        ],
        'She has been studying all day.',
    ),
    (
        'What is the past participle of "write"?',
        ['wrote', 'written', 'writed', 'writing'],
        'written',
    ),
)


def _ensure_site_services():
    for slug, name, _code in SAMPLE_SERVICES:
        Service.objects.get_or_create(
            slug=slug,
            defaults={
                'name_az': name,
                'name_en': name,
                'is_active': True,
            },
        )


class Command(BaseCommand):
    help = 'Create 10 sample quizzes (categories + questions). Safe to re-run — skips existing topics.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Create even when a quiz with the same topic already exists.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        force = options['force']
        _ensure_site_services()

        active_codes = set(get_active_course_type_codes())
        if not active_codes:
            self.stderr.write(
                'No active portal services found. Add active projects.Service rows first.',
            )
            raise SystemExit(1)

        created_quizzes = 0
        skipped = 0

        for service_code, category_name, topic in QUIZ_SPECS:
            if service_code not in active_codes:
                self.stdout.write(
                    self.style.WARNING(f'Skip "{topic}": service {service_code!r} not active on site'),
                )
                skipped += 1
                continue

            if not force and Quiz.objects.filter(topic=topic).exists():
                self.stdout.write(f'Skip existing quiz: {topic}')
                skipped += 1
                continue

            from portals.utils.quiz_category_services import ensure_quiz_category

            category, _ = ensure_quiz_category(service_code, category_name)
            quiz = Quiz.objects.create(
                category=category,
                topic=topic,
            )
            for order, (text, options_list, correct) in enumerate(SAMPLE_QUESTIONS, start=1):
                QuizQuestion.objects.create(
                    quiz=quiz,
                    order=order,
                    prompt_type=QuizQuestion.PromptType.TEXT,
                    question=text,
                    answer_options=options_list,
                    correct_answer=correct,
                    correct_option_index=options_list.index(correct),
                )
            created_quizzes += 1
            self.stdout.write(self.style.SUCCESS(f'Created: {topic} ({service_code})'))

        self.stdout.write(
            self.style.SUCCESS(
                f'Done — {created_quizzes} quiz(zes) created, {skipped} skipped.',
            ),
        )
