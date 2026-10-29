"""Find reading / listening quizzes whose choice answers all point at the first option.

Until the correct-option sync preferred the answer text, questions created in code (the JSON
resource loaders) kept the default correct_option_index=0, and saving them replaced the real
answer with option 1. In a genuine test about 1 in 4 answers is the first option, so a quiz
where nearly every choice answer is option 1 was most likely hit. Read-only: it only reports.
Re-run the resource loader on the original JSON to restore such a quiz.
"""

from collections import defaultdict

from django.core.management.base import BaseCommand

from portals.models import ListeningQuestion, ReadingQuestion
from portals.models.reading_models import CHOICE_QUESTION_TYPES


class Command(BaseCommand):
    help = 'List reading/listening quizzes where almost every choice answer is the first option.'

    def add_arguments(self, parser):
        parser.add_argument('--min-questions', type=int, default=4, help='Skip quizzes with fewer choice questions.')
        parser.add_argument('--threshold', type=float, default=0.75, help='Share of first-option answers to flag.')

    def handle(self, *args, **options):
        stats = defaultdict(lambda: {'kind': '', 'topic': '', 'slug': '', 'total': 0, 'first': 0})

        reading = ReadingQuestion.objects.filter(question_type__in=CHOICE_QUESTION_TYPES).select_related(
            'passage__quiz', 'group',
        )
        for question in reading.iterator():
            if len(question.variant_options) < 2:
                continue
            self._count(stats, 'reading', question.passage.quiz, question.correct_option_index)

        listening = ListeningQuestion.objects.select_related('audio__quiz', 'group')
        for question in listening.iterator():
            if len(question.variant_options) < 2:
                continue
            self._count(stats, 'listening', question.audio.quiz, question.correct_option_index)

        flagged = [
            (quiz_id, row) for quiz_id, row in sorted(stats.items())
            if row['total'] >= options['min_questions'] and row['first'] / row['total'] >= options['threshold']
        ]
        for quiz_id, row in flagged:
            self.stdout.write(
                f"{row['kind']:<9} quiz={quiz_id} slug={row['slug'] or '-'} "
                f"first-option answers {row['first']}/{row['total']}  {row['topic']}"
            )
        self.stdout.write(self.style.SUCCESS(
            f'{len(flagged)} suspicious quiz(zes) out of {len(stats)} with choice questions.'
        ))

    @staticmethod
    def _count(stats, kind, quiz, index):
        row = stats[quiz.pk]
        row.update(kind=kind, topic=quiz.topic, slug=getattr(quiz, 'resource_slug', '') or '')
        row['total'] += 1
        if index == 0:
            row['first'] += 1
