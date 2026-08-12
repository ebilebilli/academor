"""Convert legacy IELTS reading gap-fill answers (single correct_answer) to SPR."""

from django.core.management.base import BaseCommand, CommandError

from portals.models import ReadingPassage, ReadingQuestion, Quiz
from portals.models.reading_models import TEXT_QUESTION_TYPES
from portals.utils.quiz_reading import (
    build_reading_spr_answers,
    convert_reading_queryset_gapfill_to_spr,
)


class Command(BaseCommand):
    help = (
        'Convert reading gap-fill / completion questions '
        '(sentence/summary/note/table/flowchart/diagram/short answer) '
        'from single correct_answer (+ accept_alternatives) to spr_correct_answers.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--quiz-id',
            type=int,
            help='Only convert questions belonging to this reading quiz id.',
        )
        parser.add_argument(
            '--passage-id',
            type=int,
            help='Only convert questions under this ReadingPassage id.',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Report how many would convert without saving.',
        )

    def handle(self, *args, **options):
        qs = ReadingQuestion.objects.filter(
            question_type__in=TEXT_QUESTION_TYPES,
        ).order_by('id')

        quiz_id = options.get('quiz_id')
        passage_id = options.get('passage_id')
        if quiz_id is not None:
            if not Quiz.objects.filter(pk=quiz_id, is_reading=True).exists():
                raise CommandError(f'Reading quiz not found: {quiz_id}')
            qs = qs.filter(passage__quiz_id=quiz_id)
        if passage_id is not None:
            if not ReadingPassage.objects.filter(pk=passage_id).exists():
                raise CommandError(f'ReadingPassage not found: {passage_id}')
            qs = qs.filter(passage_id=passage_id)

        if options['dry_run']:
            would_convert = 0
            skipped_unchanged_or_empty = 0
            for question in qs.iterator():
                answers = build_reading_spr_answers(question)
                already = [
                    str(item).strip()
                    for item in (question.spr_correct_answers or [])
                    if str(item).strip()
                ]
                if answers and already != answers:
                    would_convert += 1
                else:
                    skipped_unchanged_or_empty += 1
            self.stdout.write(
                self.style.WARNING(
                    f'Dry run: would convert={would_convert}, '
                    f'skipped_unchanged_or_empty={skipped_unchanged_or_empty}',
                ),
            )
            return

        stats = convert_reading_queryset_gapfill_to_spr(qs)
        self.stdout.write(
            self.style.SUCCESS(
                f'Converted={stats["converted"]}, '
                f'skipped_choice={stats["skipped_choice"]}, '
                f'skipped_unchanged_or_empty={stats["skipped_empty"]}',
            ),
        )
