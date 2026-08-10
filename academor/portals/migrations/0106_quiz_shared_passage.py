import ckeditor.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0105_alter_quizquestion_spr_correct_answers_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='has_shared_passage',
            field=models.BooleanField(
                default=False,
                help_text=(
                    'For standard multiple-choice quizzes only. When enabled, a fixed passage stays at the top '
                    'and questions appear below (Reading-style layout). Leave off for plain question lists. '
                    'Not used with Listening, Writing, Speaking, Reading, or Math formats.'
                ),
                verbose_name='Shared passage layout',
            ),
        ),
        migrations.AddField(
            model_name='quiz',
            name='shared_passage',
            field=ckeditor.fields.RichTextField(
                blank=True,
                help_text='Fixed text shown above all questions when shared passage layout is enabled.',
                verbose_name='Shared passage text',
            ),
        ),
    ]
