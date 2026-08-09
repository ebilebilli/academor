"""One-shot: re-score an existing QuizResult from stored given_answers.

Use when admin correct answers were fixed after a student already submitted.
Does not change answers — only recalculates total_score from current keys.

Examples (dry-run first, then apply):

    python manage.py regrade_quiz_result --result-id 123
    python manage.py regrade_quiz_result --result-id 123 --verbose
    python manage.py regrade_quiz_result --result-id 123 --apply

    python manage.py regrade_quiz_result --mock-attempt-id 45 --section math --verbose

Delete this command after use.
"""

from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from portals.models import IeltsMockTestAttempt, QuizQuestion, QuizResult
from portals.utils.quiz_submit import (
    _normalize_given_answers,
    _question_correct_index,
    score_variant_quiz,
)
from portals.utils.sat_spr_validation import plain_spr_text, validate_spr_answer


def _short(value, limit: int = 60) -> str:
    text = plain_spr_text(value) if value is not None else ''
    text = ' '.join(text.split())
    if len(text) > limit:
        return text[: limit - 1] + '…'
    return text or '—'


class Command(BaseCommand):
    help = (
        'Re-score QuizResult(s) using stored given_answers and current correct answers. '
        'Dry-run by default; pass --apply to save. Use --verbose for per-question detail.'
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
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Print every question: student answer vs current key, plus key drift warnings.',
        )

    def handle(self, *args, **options):
        result_id = options.get('result_id')
        mock_attempt_id = options.get('mock_attempt_id')
        apply = options['apply']
        verbose = options['verbose']

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
            result = QuizResult.objects.select_related('quiz', 'student', 'customer').get(pk=result.pk)
            results = [result]

        changed = 0
        for result in results:
            if verbose and result.quiz.is_variant_quiz:
                self._print_variant_diagnostics(result)

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

    def _print_variant_diagnostics(self, result: QuizResult) -> None:
        quiz = result.quiz
        answers = _normalize_given_answers(result.given_answers or {})
        questions = list(
            quiz.questions.order_by('order', 'id').only(
                'id', 'order', 'question_type', 'answer_options', 'correct_answer',
                'correct_option_index', 'spr_correct_answers',
            ),
        )

        answered = 0
        correct_count = 0
        drift = 0
        blank = 0

        self.stdout.write(self.style.NOTICE(
            f'--- Diagnostics for result={result.pk} quiz={quiz.pk} '
            f'({len(questions)} questions, {len(answers)} stored answers) ---',
        ))

        for q in questions:
            qtype = q.question_type
            prefix = f'Q{q.order or "?"} id={q.pk}'

            if qtype == QuizQuestion.QuestionType.SPR:
                student = answers.get(q.pk)
                if student in (None, ''):
                    blank += 1
                    self.stdout.write(f'{prefix} SPR  student=BLANK  key={_short(q.spr_correct_answers)}  WRONG')
                    continue
                answered += 1
                ok = False
                if q.spr_correct_answers:
                    ok = validate_spr_answer(str(student), q.spr_correct_answers)['is_correct']
                if ok:
                    correct_count += 1
                mark = 'OK' if ok else 'WRONG'
                self.stdout.write(
                    f'{prefix} SPR  student={_short(student)}  '
                    f'key={_short(q.spr_correct_answers)}  {mark}',
                )
                continue

            options = q.answer_options or []
            selected = answers.get(q.pk)
            correct_idx = _question_correct_index(q)
            stored_idx = q.correct_option_index
            correct_text = (q.correct_answer or '').strip()
            text_in_options = bool(correct_text and correct_text in options)
            index_from_text = options.index(correct_text) if text_in_options else None

            if text_in_options and index_from_text != stored_idx:
                drift += 1
                self.stdout.write(self.style.WARNING(
                    f'{prefix} KEY-DRIFT: correct_answer→index {index_from_text}, '
                    f'stored correct_option_index={stored_idx}',
                ))
            elif correct_text and not text_in_options:
                drift += 1
                self.stdout.write(self.style.WARNING(
                    f'{prefix} KEY-DRIFT: correct_answer HTML not in options; '
                    f'scoring falls back to correct_option_index={stored_idx} '
                    f'(answer={_short(correct_text)})',
                ))

            if selected is None:
                blank += 1
                sel_label = 'BLANK'
                is_ok = False
            else:
                answered += 1
                sel_label = f'idx={selected}'
                if isinstance(selected, int) and 0 <= selected < len(options):
                    sel_label += f'({_short(options[selected], 40)})'
                is_ok = (
                    correct_idx is not None
                    and selected is not None
                    and selected == correct_idx
                )

            if is_ok:
                correct_count += 1
            mark = 'OK' if is_ok else 'WRONG'
            key_label = f'idx={correct_idx}'
            if correct_idx is not None and 0 <= correct_idx < len(options):
                key_label += f'({_short(options[correct_idx], 40)})'
            self.stdout.write(f'{prefix} MCQ  student={sel_label}  key={key_label}  {mark}')

        self.stdout.write(
            f'--- Summary: answered={answered}/{len(questions)} blank={blank} '
            f'correct_now={correct_count} key_drift_warnings={drift} ---',
        )
        if drift:
            self.stdout.write(self.style.ERROR(
                'KEY-DRIFT means admin "correct answer" text often does NOT update the '
                'scored index (CKEditor HTML mismatch). Fix the option radio/index in admin, '
                'or make correct_answer exactly match one option string.',
            ))

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
