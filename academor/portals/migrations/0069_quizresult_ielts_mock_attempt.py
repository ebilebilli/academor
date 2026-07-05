from django.db import migrations, models
import django.db.models.deletion


def link_existing_mock_results(apps, schema_editor):
    IeltsMockTestAttempt = apps.get_model('portals', 'IeltsMockTestAttempt')
    QuizResult = apps.get_model('portals', 'QuizResult')

    result_fields = (
        'listening_result_id',
        'reading_result_id',
        'writing_result_id',
        'speaking_result_id',
    )
    for attempt in IeltsMockTestAttempt.objects.exclude(status='abandoned').iterator():
        for field in result_fields:
            result_id = getattr(attempt, field)
            if not result_id:
                continue
            QuizResult.objects.filter(
                pk=result_id,
                ielts_mock_attempt__isnull=True,
            ).update(ielts_mock_attempt_id=attempt.pk)


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0068_portal_notification_weekly_score'),
    ]

    operations = [
        migrations.AddField(
            model_name='quizresult',
            name='ielts_mock_attempt',
            field=models.ForeignKey(
                blank=True,
                help_text='Set when this result belongs to a mock test section (not a standalone quiz).',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='section_results',
                to='portals.ieltsmocktestattempt',
                verbose_name='IELTS mock test attempt',
            ),
        ),
        migrations.RunPython(link_existing_mock_results, migrations.RunPython.noop),
    ]
