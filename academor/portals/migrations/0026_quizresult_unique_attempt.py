from django.db import migrations, models


def dedupe_quiz_results(apps, schema_editor):
    QuizResult = apps.get_model('portals', 'QuizResult')
    seen = set()
    for row in QuizResult.objects.order_by('student_id', 'quiz_id', '-completed_at', '-id').iterator():
        key = (row.student_id, row.quiz_id)
        if key in seen:
            row.delete()
        else:
            seen.add(key)


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0025_classroom_service_m2m'),
    ]

    operations = [
        migrations.RunPython(dedupe_quiz_results, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name='quizresult',
            constraint=models.UniqueConstraint(
                fields=('student', 'quiz'),
                name='portals_quiz_result_one_per_student',
            ),
        ),
    ]
