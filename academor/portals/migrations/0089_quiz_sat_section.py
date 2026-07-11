from django.db import migrations, models


def backfill_sat_section(apps, schema_editor):
    Quiz = apps.get_model('portals', 'Quiz')
    for quiz in Quiz.objects.filter(is_sat=True, sat_section='').select_related('category'):
        category_name = (getattr(quiz.category, 'name', '') or '').strip().lower()
        if 'math' in category_name:
            quiz.sat_section = 'algebra'
        elif 'writing' in quiz.topic.lower():
            quiz.sat_section = 'writing'
        else:
            quiz.sat_section = 'reading'
        quiz.save(update_fields=['sat_section'])


class Migration(migrations.Migration):
    dependencies = [
        ('portals', '0088_activate_quiz_ielts_flag'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='sat_section',
            field=models.CharField(
                blank=True,
                choices=[
                    ('reading', 'Reading'),
                    ('writing', 'Writing'),
                    ('algebra', 'Algebra'),
                    ('geometry_data', 'Geometry & Data'),
                ],
                help_text=(
                    'Required for SAT quizzes. Pick exactly one: Reading, Writing, Algebra, or Geometry & Data. '
                    'Reading uses IELTS-style passages; the others use multiple-choice questions.'
                ),
                max_length=32,
                verbose_name='SAT section',
            ),
        ),
        migrations.RunPython(backfill_sat_section, migrations.RunPython.noop),
    ]
