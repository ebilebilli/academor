"""Convert legacy IELTS listening gap-fill answers (single correct_answer) to SPR."""

from django.core.management.base import BaseCommand, CommandError

from portals.models import ListeningAudio, ListeningQuestion, Quiz
from portals.utils.quiz_listening import convert_listening_queryset_gapfill_to_spr


class Command(BaseCommand):
    help = (
        'Convert listening gap-fill questions (no answer_options, single correct_answer) '
        'to spr_correct_answers for admin/UI SPR scoring.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--quiz-id',
            type=int,
            help='Only convert questions belonging to this listening quiz id.',
        )
        parser.add_argument(
            '--audio-id',
            type=int,
            help='Only convert questions under this ListeningAudio id.',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Report how many would convert without saving.',
        )

    def handle(self, *args, **options):
        qs = ListeningQuestion.objects.all().order_by('id')

        quiz_id = options.get('quiz_id')
        audio_id = options.get('audio_id')
        if quiz_id is not None:
            if not Quiz.objects.filter(pk=quiz_id, is_listening=True).exists():
                raise CommandError(f'Listening quiz not found: {quiz_id}')
            qs = qs.filter(audio__quiz_id=quiz_id)
        if audio_id is not None:
            if not ListeningAudio.objects.filter(pk=audio_id).exists():
                raise CommandError(f'ListeningAudio not found: {audio_id}')
            qs = qs.filter(audio_id=audio_id)

        if options['dry_run']:
            would_convert = 0
            skipped_mcq = 0
            skipped_unchanged_or_empty = 0
            from portals.utils.quiz_listening import build_listening_spr_answers

            for question in qs.iterator():
                if len(question.variant_options) >= 2:
                    skipped_mcq += 1
                    continue
                answers = build_listening_spr_answers(question)
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
                    f'skipped_mcq={skipped_mcq}, '
                    f'skipped_unchanged_or_empty={skipped_unchanged_or_empty}',
                ),
            )
            return

        stats = convert_listening_queryset_gapfill_to_spr(qs)
        self.stdout.write(
            self.style.SUCCESS(
                f'Converted={stats["converted"]}, '
                f'skipped_mcq={stats["skipped_mcq"]}, '
                f'skipped_unchanged_or_empty={stats["skipped_empty"]}',
            ),
        )
