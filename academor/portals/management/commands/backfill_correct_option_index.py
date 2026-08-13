"""Backfill correct_option_index for MCQ / choice questions from legacy correct_answer text."""

from django.core.management.base import BaseCommand

from portals.models import ListeningQuestion, QuizQuestion
from portals.models.reading_models import CHOICE_QUESTION_TYPES, ReadingQuestion, matching_option_index
from portals.utils.quiz_correct_option_backfill import (
    backfill_listening_question,
    backfill_quiz_question_mcq,
    backfill_reading_question,
)


class Command(BaseCommand):
    help = (
        'Set correct_option_index (and sync correct_answer) for variant, listening, '
        'and IELTS reading choice questions that still rely on pasted option text.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Report counts without saving.',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        stats = {
            'variant_updated': 0,
            'variant_skipped': 0,
            'listening_updated': 0,
            'listening_skipped': 0,
            'reading_updated': 0,
            'reading_skipped': 0,
        }

        for question in QuizQuestion.objects.exclude(
            question_type=QuizQuestion.QuestionType.SPR,
        ).iterator():
            if dry_run:
                options_list = [
                    str(item).strip()
                    for item in (question.answer_options or [])
                    if str(item).strip()
                ]
                if len(options_list) < 2:
                    stats['variant_skipped'] += 1
                    continue
                from portals.utils.quiz_correct_option import sync_correct_option_fields

                resolved = sync_correct_option_fields(
                    options_list,
                    existing_index=question.correct_option_index,
                    existing_answer=(question.correct_answer or '').strip(),
                    match_answer=lambda opts, value: opts.index(value) if value in opts else None,
                )
                if resolved is None:
                    stats['variant_skipped'] += 1
                elif (
                    question.correct_option_index != resolved[0]
                    or (question.correct_answer or '').strip() != resolved[1]
                ):
                    stats['variant_updated'] += 1
                else:
                    stats['variant_skipped'] += 1
                continue

            if backfill_quiz_question_mcq(question):
                stats['variant_updated'] += 1
            else:
                stats['variant_skipped'] += 1

        for question in ListeningQuestion.objects.iterator():
            if dry_run:
                options = question.variant_options
                if len(options) < 2:
                    stats['listening_skipped'] += 1
                    continue
                from portals.utils.quiz_correct_option import sync_correct_option_fields

                resolved = sync_correct_option_fields(
                    options,
                    existing_index=question.correct_option_index,
                    existing_answer=(question.correct_answer or '').strip(),
                    match_answer=lambda opts, value: opts.index(value) if value in opts else None,
                )
                if resolved is None:
                    stats['listening_skipped'] += 1
                elif (
                    question.correct_option_index != resolved[0]
                    or (question.correct_answer or '').strip() != resolved[1]
                ):
                    stats['listening_updated'] += 1
                else:
                    stats['listening_skipped'] += 1
                continue

            if backfill_listening_question(question):
                stats['listening_updated'] += 1
            else:
                stats['listening_skipped'] += 1

        for question in ReadingQuestion.objects.filter(
            question_type__in=CHOICE_QUESTION_TYPES,
        ).select_related('group').iterator():
            if dry_run:
                from portals.models.reading_models import resolve_reading_question_options
                from portals.utils.quiz_correct_option import sync_correct_option_fields

                options = resolve_reading_question_options(question)
                if len(options) < 2:
                    stats['reading_skipped'] += 1
                    continue
                resolved = sync_correct_option_fields(
                    options,
                    existing_index=question.correct_option_index,
                    existing_answer=(question.correct_answer or '').strip(),
                    match_answer=matching_option_index,
                )
                if resolved is None:
                    stats['reading_skipped'] += 1
                elif (
                    question.correct_option_index != resolved[0]
                    or (question.correct_answer or '').strip() != resolved[1]
                ):
                    stats['reading_updated'] += 1
                else:
                    stats['reading_skipped'] += 1
                continue

            if backfill_reading_question(question):
                stats['reading_updated'] += 1
            else:
                stats['reading_skipped'] += 1

        prefix = 'Dry run: ' if dry_run else ''
        self.stdout.write(
            self.style.SUCCESS(
                f'{prefix}variant updated={stats["variant_updated"]}, '
                f'skipped={stats["variant_skipped"]}; '
                f'listening updated={stats["listening_updated"]}, '
                f'skipped={stats["listening_skipped"]}; '
                f'reading updated={stats["reading_updated"]}, '
                f'skipped={stats["reading_skipped"]}',
            ),
        )
