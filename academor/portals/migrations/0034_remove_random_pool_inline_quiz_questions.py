from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0033_quiz_resource_slug_pool_filter'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='quiz',
            name='pool_resource_name',
        ),
        migrations.RemoveField(
            model_name='quiz',
            name='use_random_questions_20',
        ),
        migrations.RemoveField(
            model_name='quiz',
            name='use_random_questions_30',
        ),
        migrations.RemoveField(
            model_name='quiz',
            name='use_random_questions_50',
        ),
        migrations.AddField(
            model_name='quizquestion',
            name='source_key',
            field=models.CharField(
                blank=True,
                help_text='Stable key for upsert when reloading JSON resources.',
                max_length=64,
                verbose_name='Source key',
            ),
        ),
        migrations.AddConstraint(
            model_name='quizquestion',
            constraint=models.UniqueConstraint(
                condition=models.Q(('source_key', ''), _negated=True),
                fields=('quiz', 'source_key'),
                name='portals_quiz_question_source_key_uniq',
            ),
        ),
        migrations.DeleteModel(
            name='QuizCategoryQuestion',
        ),
    ]
