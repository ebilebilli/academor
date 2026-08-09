"""One-shot: re-score an existing QuizResult from stored given_answers.

Use when admin correct answers were fixed after a student already submitted.
Does not change answers — only recalculates total_score from current keys.

Examples (dry-run first, then apply):

    python manage.py regrade_quiz_result --result-id 123
    python manage.py regrade_quiz_result --result-id 123 --apply

    python manage.py regrade_quiz_result --mock-attempt-id 45 --section math
    python manage.py regrade_quiz_result --mock-attempt-id 45 --section math --apply

Delete this command after use.
"""

from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from portals.models import IeltsMockTestAttempt, QuizResult
from portals.utils.quiz_submit import score_variant_quiz


class Command(BaseCommand):
    help = (
        'Re-score QuizResult(s) using stored given_answers and current correct answers. '
        'Dry-run by default; pass --apply to save.'
    )

    def add_arguments(self, parser):
        parser.add_argument('--result-id', type=int, help='QuizResult primary key.')
        parser.add_argument(
            '--mock-attempt-id',
            type=int,
            help='Mock attempt id (regrades one section result).',
        )
        parser.add_argument(
            '--section',
            default='math',
            help='Section on the mock attempt (default: math). Ignored with --result-id.',
        )
        parser.add_argument(
            '--apply',
            action='store_true',
            help='Persist the new total_score. Without this flag, only prints the diff.',
        )

    def handle(self, *args, **options):
        result_id = options.get('result_id')
        mock_attempt_id = options.get('mock_attempt_id')
        apply = options['apply']

        if bool(result_id) == bool(mock_attempt_id):
            raise CommandError('Provide exactly one of --result-id or --mock-attempt-id.')

        if result_id:
            result = (
                QuizResult.objects.select_related('quiz', 'student', 'customer')
                .filter(pk=result_id)
                .first()
            )
            if not result:
                raise CommandError(f'QuizResult {result_id} not found.')
            results = [result]
        else:
            attempt = IeltsMockTestAttempt.objects.filter(pk=mock_attempt_id).first()
            if not attempt:
                raise CommandError(f'Mock attempt {mock_attempt_id} not found.')
            section = (options.get('section') or 'math').strip()
            result = attempt.result_for_section(section)
            if not result:
                raise CommandError(
                    f'Mock attempt {mock_attempt_id} has no result for section "{section}".',
                )
            # Refresh with relations used for logging.
            result = QuizResult.objects.select_related('quiz', 'student', 'customer').get(pk=result.pk)
            results = [result]

        changed = 0
        for result in results:
            old_score, new_score, max_score = self._regrade_one(result, apply=apply)
            owner = result.student or result.customer
            label = 'UPDATED' if apply and old_score != new_score else (
                'WOULD UPDATE' if old_score != new_score else 'UNCHANGED'
            )
            if old_score != new_score:
                changed += 1
            self.stdout.write(
                f'[{label}] result={result.pk} quiz={result.quiz_id} ({result.quiz.topic}) '
                f'owner={owner} score {old_score} -> {new_score} / {max_score}',
            )

        if not apply:
            self.stdout.write(self.style.WARNING(
                f'Dry-run only ({changed} would change). Re-run with --apply to save.',
            ))
        else:
            self.stdout.write(self.style.SUCCESS(f'Done. Updated {changed} result(s).'))

    def _regrade_one(self, result: QuizResult, *, apply: bool) -> tuple[float | None, float, int]:
        quiz = result.quiz
        if quiz.is_variant_quiz:
            new_score, max_score, _breakdown = score_variant_quiz(quiz, result.given_answers or {})
        elif quiz.is_reading_quiz:
            from portals.utils.quiz_reading import get_reading_questions_for_quiz
            from portals.utils.quiz_reading_score import (
                normalize_reading_answers,
                score_reading_quiz,
            )

            questions = get_reading_questions_for_quiz(quiz)
            normalized = normalize_reading_answers(
                quiz,
                result.given_answers or {},
                questions=questions,
            )
            new_score, max_score, _breakdown = score_reading_quiz(
                quiz,
                normalized,
                questions=questions,
            )
        else:
            raise CommandError(
                f'Result {result.pk}: quiz {quiz.pk} is not auto-scored '
                f'(grading_mode={quiz.grading_mode}).',
            )

        old_score = result.total_score
        if apply and old_score != new_score:
            with transaction.atomic():
                QuizResult.objects.filter(pk=result.pk).update(total_score=new_score)
            try:
                from portals.utils.cache_utils import invalidate_model_cache

                invalidate_model_cache('QuizResult')
            except Exception:
                pass
            result.total_score = new_score

        return old_score, float(new_score), int(max_score)
