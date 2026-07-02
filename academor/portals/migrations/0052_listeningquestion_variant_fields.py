from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0051_alter_listeningquestion_question_richtext'),
    ]

    operations = [
        migrations.AddField(
            model_name='listeningquestion',
            name='answer_options',
            field=models.JSONField(
                blank=True,
                default=list,
                help_text='Optional JSON list of choices, e.g. ["Option A", "Option B"]. Leave empty for a text answer.',
                verbose_name='Answer options',
            ),
        ),
        migrations.AddField(
            model_name='listeningquestion',
            name='correct_answer',
            field=models.CharField(
                blank=True,
                help_text='Must exactly match one option when answer options are set.',
                max_length=500,
                verbose_name='Correct answer',
            ),
        ),
        migrations.AddField(
            model_name='listeningquestion',
            name='correct_option_index',
            field=models.PositiveIntegerField(default=0, verbose_name='Correct option index'),
        ),
    ]
