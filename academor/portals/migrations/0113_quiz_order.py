from django.db import migrations, models


def forwards_quiz_order(apps, schema_editor):
    Quiz = apps.get_model('portals', 'Quiz')
    category_ids = (
        Quiz.objects.order_by('category_id')
        .values_list('category_id', flat=True)
        .distinct()
    )
    for category_id in category_ids:
        quizzes = list(
            Quiz.objects.filter(category_id=category_id).order_by('-created_at', 'id'),
        )
        for index, quiz in enumerate(quizzes):
            if quiz.order != index:
                quiz.order = index
                quiz.save(update_fields=['order'])


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0112_quizquestion_is_dropdown'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='quiz',
            options={
                'ordering': ('order', 'topic', 'id'),
                'verbose_name': 'Quiz',
                'verbose_name_plural': 'Quizzes',
            },
        ),
        migrations.AddField(
            model_name='quiz',
            name='order',
            field=models.PositiveIntegerField(
                default=0,
                help_text='Lower numbers appear first within the category on the portal quiz list.',
                verbose_name='Order',
            ),
        ),
        migrations.RunPython(forwards_quiz_order, migrations.RunPython.noop),
    ]
